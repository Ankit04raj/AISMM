"""Instagram Graph API Adapter Implementation."""

import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

from ..base import BasePlatformAdapter, PlatformCapability
from ...errors import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    MediaUploadError,
    PublishingError,
    PlatformError,
)
from ...normalization import UniversalContent, MetricNormalizer


class InstagramAdapter(BasePlatformAdapter):
    """Instagram Graph API adapter implementing BasePlatformAdapter contract."""

    PLATFORM_NAME = "instagram"
    BASE_URL = "https://graph.facebook.com/v19.0"
    AUTH_URL = "https://api.instagram.com/oauth/authorize"
    TOKEN_URL = "https://api.instagram.com/oauth/access_token"
    REFRESH_URL = "https://graph.facebook.com/v19.0/oauth/access_token"

    # Capability matrix for Instagram (ADR-003)
    SUPPORTED_CAPABILITIES = {
        PlatformCapability.POST_IMAGE,
        PlatformCapability.POST_CAROUSEL,
        PlatformCapability.POST_REEL,
        PlatformCapability.POST_STORY,
        PlatformCapability.SCHEDULE_POST,
        PlatformCapability.FETCH_INSIGHTS,
        PlatformCapability.WEBHOOK_SUBSCRIBE,
        PlatformCapability.MANAGE_COMMENTS,
        PlatformCapability.GET_PROFILE,
    }

    # Rate limits: 200 calls/hour/user
    RATE_LIMIT_CALLS = 200
    RATE_LIMIT_WINDOW = 3600  # seconds

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.redirect_uri = config.get("redirect_uri")
        self.access_token = config.get("access_token")
        self.ig_user_id = config.get("ig_user_id")  # Instagram Business Account ID
        self._token_expires_at: Optional[datetime] = None
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with auth headers."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=30.0,
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
        return self._http_client

    async def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        code = credentials.get("code")
        if not code:
            raise ValidationError("Authorization code required", platform=self.PLATFORM_NAME)

        client = await self._get_client()
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code": code,
        }

        response = await client.post(self.TOKEN_URL, data=data)
        if response.status_code != 200:
            raise AuthenticationError(
                f"Token exchange failed: {response.text}",
                platform=self.PLATFORM_NAME,
                status_code=response.status_code,
            )

        token_data = response.json()
        self.access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Get long-lived token (60 days)
        long_lived = await self._exchange_long_lived_token(self.access_token)
        self.access_token = long_lived["access_token"]
        self._token_expires_at = datetime.utcnow() + timedelta(seconds=long_lived["expires_in"])

        # Get Instagram Business Account ID
        self.ig_user_id = await self._get_ig_user_id()

        return {
            "access_token": self.access_token,
            "expires_at": self._token_expires_at.isoformat(),
            "ig_user_id": self.ig_user_id,
        }

    async def _exchange_long_lived_token(self, short_token: str) -> Dict[str, Any]:
        """Exchange short-lived token for long-lived (60 day) token."""
        client = await self._get_client()
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "fb_exchange_token": short_token,
        }
        response = await client.get(self.REFRESH_URL, params=params)
        if response.status_code != 200:
            raise AuthenticationError(
                f"Long-lived token exchange failed: {response.text}",
                platform=self.PLATFORM_NAME,
            )
        return response.json()

    async def _get_ig_user_id(self) -> str:
        """Get Instagram Business Account ID from Facebook Page."""
        client = await self._get_client()
        response = await client.get("/me/accounts", params={"fields": "instagram_business_account"})
        if response.status_code != 200:
            raise AuthenticationError(
                f"Failed to get Instagram account: {response.text}",
                platform=self.PLATFORM_NAME,
            )
        data = response.json()
        for account in data.get("data", []):
            if "instagram_business_account" in account:
                return account["instagram_business_account"]["id"]
        raise AuthenticationError("No Instagram Business Account linked", platform=self.PLATFORM_NAME)

    async def refresh_token(self) -> Dict[str, Any]:
        """Refresh long-lived access token (valid for 60 days, refreshable within 24h of expiry)."""
        if not self._token_expires_at or datetime.utcnow() >= self._token_expires_at - timedelta(hours=24):
            client = await self._get_client()
            params = {
                "grant_type": "fb_exchange_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "fb_exchange_token": self.access_token,
            }
            response = await client.get(self.REFRESH_URL, params=params)
            if response.status_code != 200:
                raise AuthenticationError(
                    f"Token refresh failed: {response.text}",
                    platform=self.PLATFORM_NAME,
                )
            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 5184000)  # 60 days default
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            # Update client headers
            self._http_client.headers["Authorization"] = f"Bearer {self.access_token}"

        return {
            "access_token": self.access_token,
            "expires_at": self._token_expires_at.isoformat() if self._token_expires_at else None,
        }

    async def validate_token(self) -> bool:
        """Validate current access token by making a test call."""
        try:
            client = await self._get_client()
            response = await client.get(f"/{self.ig_user_id}", params={"fields": "id"})
            return response.status_code == 200
        except Exception:
            return False

    async def publish_post(self, content: UniversalContent, options: Optional[Dict] = None) -> Dict[str, Any]:
        """Publish a post (image, carousel, or reel) to Instagram."""
        options = options or {}
        media_type = self._determine_media_type(content)

        # Step 1: Create media container
        container_id = await self._create_media_container(content, media_type, options)

        # Step 2: Publish container
        publish_result = await self._publish_media_container(container_id, options)

        return {
            "platform": self.PLATFORM_NAME,
            "post_id": publish_result.get("id"),
            "container_id": container_id,
            "permalink": publish_result.get("permalink"),
            "published_at": datetime.utcnow().isoformat(),
            "media_type": media_type,
        }

    def _determine_media_type(self, content: UniversalContent) -> str:
        """Determine Instagram media type from content."""
        if content.content_type == "reel" or (content.media and any(m.type == "video" for m in content.media)):
            return "REELS"
        elif content.content_type == "story":
            return "STORIES"
        elif len(content.media) > 1:
            return "CAROUSEL"
        return "IMAGE"

    async def _create_media_container(
        self,
        content: UniversalContent,
        media_type: str,
        options: Dict
    ) -> str:
        """Create media container (Step 1 of 2-phase publish)."""
        client = await self._get_client()

        # Upload media first
        media_ids = []
        for media in content.media:
            media_id = await self._upload_media(media, media_type)
            media_ids.append(media_id)

        # Build container params
        params = {
            "media_type": media_type,
            "caption": content.caption or content.text,
        }

        if media_type == "CAROUSEL":
            params["children"] = ",".join(media_ids)
        else:
            params["media_url"] = media_ids[0] if media_ids else ""

        if options.get("scheduled_at"):
            params["scheduled_publish_time"] = int(options["scheduled_at"].timestamp())

        if options.get("location_id"):
            params["location_id"] = options["location_id"]

        response = await client.post(f"/{self.ig_user_id}/media", data=params)
        if response.status_code != 200:
            raise MediaUploadError(
                f"Container creation failed: {response.text}",
                platform=self.PLATFORM_NAME,
                status_code=response.status_code,
            )

        return response.json()["id"]

    async def _upload_media(self, media: "UniversalMedia", media_type: str) -> str:
        """Upload media file and return media ID or URL."""
        # For production: implement resumable upload to Facebook's media upload endpoint
        # For now, assume media.url is a publicly accessible URL
        if media.url:
            return media.url

        # TODO: Implement chunked upload for large files
        raise MediaUploadError("Media URL required for Instagram publishing", platform=self.PLATFORM_NAME)

    async def _publish_media_container(self, container_id: str, options: Dict) -> Dict[str, Any]:
        """Publish media container (Step 2 of 2-phase publish)."""
        client = await self._get_client()
        response = await client.post(f"/{self.ig_user_id}/media_publish", data={"creation_id": container_id})
        if response.status_code != 200:
            raise PublishingError(
                f"Media publish failed: {response.text}",
                platform=self.PLATFORM_NAME,
                status_code=response.status_code,
            )
        return response.json()

    async def fetch_insights(self, post_id: str, metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch insights/metrics for a post."""
        client = await self._get_client()

        default_metrics = [
            "impressions", "reach", "likes", "comments", "shares", "saves",
            "video_views", "profile_visits", "follows"
        ]
        metric_list = metrics or default_metrics

        response = await client.get(
            f"/{post_id}/insights",
            params={"metric": ",".join(metric_list), "period": "lifetime"}
        )
        if response.status_code != 200:
            raise PlatformError(
                f"Insights fetch failed: {response.text}",
                platform=self.PLATFORM_NAME,
                status_code=response.status_code,
            )

        data = response.json()
        raw_metrics = {item["name"]: item["values"][0]["value"] for item in data.get("data", [])}
        return MetricNormalizer.normalize_metrics(raw_metrics, self.PLATFORM_NAME)

    async def fetch_account_insights(self, metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch account-level insights."""
        client = await self._get_client()
        default_metrics = [
            "followers_count", "impressions", "reach", "profile_views",
            "website_clicks", "email_contacts", "phone_call_clicks"
        ]
        metric_list = metrics or default_metrics

        response = await client.get(
            f"/{self.ig_user_id}/insights",
            params={"metric": ",".join(metric_list), "period": "day"}
        )
        if response.status_code != 200:
            raise PlatformError(
                f"Account insights failed: {response.text}",
                platform=self.PLATFORM_NAME,
            )

        data = response.json()
        raw_metrics = {item["name"]: item["values"][0]["value"] for item in data.get("data", [])}
        return MetricNormalizer.normalize_metrics(raw_metrics, self.PLATFORM_NAME)

    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """Get post details."""
        client = await self._get_client()
        fields = "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count"
        response = await client.get(f"/{post_id}", params={"fields": fields})
        if response.status_code != 200:
            raise PlatformError(
                f"Get post failed: {response.text}",
                platform=self.PLATFORM_NAME,
            )
        return response.json()

    async def delete_post(self, post_id: str) -> bool:
        """Delete a post."""
        client = await self._get_client()
        response = await client.delete(f"/{post_id}")
        return response.status_code == 200

    async def get_comments(self, post_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get comments on a post."""
        client = await self._get_client()
        response = await client.get(f"/{post_id}/comments", params={"limit": limit, "fields": "id,text,timestamp,username,like_count"})
        if response.status_code != 200:
            raise PlatformError(f"Get comments failed: {response.text}", platform=self.PLATFORM_NAME)
        return response.json().get("data", [])

    async def reply_comment(self, comment_id: str, text: str) -> Dict[str, Any]:
        """Reply to a comment."""
        client = await self._get_client()
        response = await client.post(f"/{comment_id}/replies", data={"message": text})
        if response.status_code != 200:
            raise PlatformError(f"Reply comment failed: {response.text}", platform=self.PLATFORM_NAME)
        return response.json()

    async def hide_comment(self, comment_id: str) -> bool:
        """Hide a comment."""
        client = await self._get_client()
        response = await client.post(f"/{comment_id}", data={"hidden": "true"})
        return response.status_code == 200

    async def subscribe_webhook(self, callback_url: str, verify_token: str, fields: List[str]) -> Dict[str, Any]:
        """Subscribe to Instagram webhooks."""
        client = await self._get_client()
        response = await client.post(
            f"/{self.ig_user_id}/subscribed_apps",
            data={
                "subscribed_fields": ",".join(fields),
                "callback_url": callback_url,
                "verify_token": verify_token,
            }
        )
        if response.status_code != 200:
            raise PlatformError(f"Webhook subscribe failed: {response.text}", platform=self.PLATFORM_NAME)
        return response.json()

    async def unsubscribe_webhook(self) -> bool:
        """Unsubscribe from webhooks."""
        client = await self._get_client()
        response = await client.delete(f"/{self.ig_user_id}/subscribed_apps")
        return response.status_code == 200

    async def get_capabilities(self) -> set:
        """Return supported capabilities."""
        return self.SUPPORTED_CAPABILITIES

    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        token_valid = await self.validate_token()
        return {
            "platform": self.PLATFORM_NAME,
            "status": "healthy" if token_valid else "degraded",
            "token_valid": token_valid,
            "ig_user_id": self.ig_user_id,
            "rate_limit_remaining": self._get_rate_limit_remaining(),
        }

    def _get_rate_limit_remaining(self) -> int:
        """Calculate remaining rate limit (simplified)."""
        # TODO: Implement proper rate limit tracking from response headers
        return self.RATE_LIMIT_CALLS

    async def close(self):
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()