"""Instagram Graph API Adapter Implementation."""

import httpx
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union


from ..base import (
    BasePlatformAdapter,
    PlatformCapability,
    PostContent,
    PostResult,
    AnalyticsData,
    CommentData,
    MediaItem,
)
from ...errors import (
    AuthenticationError,

    ValidationError,
    MediaUploadError,
    PublishingError,
    PlatformError,
)
from ...normalization import (
    UniversalContent,
    UniversalMedia,
    ContentType,
    MetricNormalizer,
)
from ...normalization.content import MediaType


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
        PlatformCapability.GET_INSIGHTS,
        PlatformCapability.MANAGE_WEBHOOKS,
        PlatformCapability.REPLY_COMMENT,
        PlatformCapability.DELETE_COMMENT,
        PlatformCapability.HIDE_COMMENT,
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
        self.ig_user_id = config.get("ig_user_id")
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

    # =========================================================================
    # BasePlatformAdapter required property
    # =========================================================================

    @property
    def platform_name(self) -> str:
        """Return platform name."""
        return self.PLATFORM_NAME

    # =========================================================================
    # Authentication
    # =========================================================================

    async def authenticate(self, credentials: Dict[str, Any]) -> Union[bool, Dict[str, Any]]:
        """Authenticate with platform."""
        if "code" in credentials:
            return await self._authenticate_oauth(credentials)
        try:
            self.access_token = credentials.get("access_token")
            self.ig_user_id = credentials.get("ig_user_id")
            if credentials.get("client_id"):
                self.client_id = credentials["client_id"]
            if credentials.get("client_secret"):
                self.client_secret = credentials["client_secret"]
            return await self.validate_connection()
        except Exception:
            return False

    async def _authenticate_oauth(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Full OAuth code exchange flow. Returns token info dict."""
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
        self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        # Get long-lived token (60 days)
        long_lived = await self._exchange_long_lived_token(self.access_token)
        self.access_token = long_lived["access_token"]
        self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=long_lived["expires_in"])

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

    async def refresh_token(self) -> bool:
        """Refresh access token using long-lived token exchange."""
        if not self.client_id or not self.client_secret or not self.access_token:
            return False

        client = await self._get_client()
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "fb_exchange_token": self.access_token,
        }
        response = await client.get(self.REFRESH_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token", self.access_token)
            expires_in = data.get("expires_in", 5184000)
            self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            if self._http_client:
                self._http_client.headers["Authorization"] = f"Bearer {self.access_token}"
            return True
        return False

    async def validate_connection(self) -> bool:
        """Validate connection is active by fetching user profile."""
        try:
            if not self.ig_user_id:
                return False
            client = await self._get_client()
            response = await client.get(f"/{self.ig_user_id}", params={"fields": "id,username"})
            return response.status_code == 200
        except Exception:
            return False

    # =========================================================================
    # Internal Instagram publish helpers
    # =========================================================================

    def _determine_media_type(self, content: UniversalContent) -> str:
        """Determine Instagram media type from content."""
        if content.content_type in (ContentType.REEL, "reel"):
            return "REELS"
        if content.content_type in (ContentType.STORY, "story"):
            return "STORIES"
        if content.media and any((getattr(m, "type", None) or getattr(m, "media_type", None)) in (MediaType.VIDEO, "video") for m in content.media):
            return "REELS"
        if len(content.media) > 1:
            return "CAROUSEL"
        return "IMAGE"

    async def _upload_media(self, media: UniversalMedia, _media_type: str) -> str:
        """Upload media file and return media ID or URL."""
        if media.url:
            return media.url
        raise MediaUploadError(
            "Media URL required for Instagram publishing",
            platform=self.PLATFORM_NAME,
        )

    async def _create_media_container(
        self,
        content: UniversalContent,
        media_type: str,
        options: Dict,
    ) -> str:
        """Create media container (Step 1 of 2-phase publish)."""
        client = await self._get_client()

        media_ids = [await self._upload_media(m, media_type) for m in content.media]

        params: Dict[str, Any] = {
            "media_type": media_type,
            "caption": content.caption or content.text or "",
        }

        if media_type == "CAROUSEL":
            params["children"] = ",".join(media_ids)
        elif media_ids:
            params["media_url"] = media_ids[0]

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

    async def _publish_media_container(self, container_id: str) -> Dict[str, Any]:
        """Publish media container (Step 2 of 2-phase publish)."""
        client = await self._get_client()
        response = await client.post(
            f"/{self.ig_user_id}/media_publish",
            data={"creation_id": container_id},
        )
        if response.status_code != 200:
            raise PublishingError(
                f"Media publish failed: {response.text}",
                platform=self.PLATFORM_NAME,
                status_code=response.status_code,
            )
        return response.json()

    async def _publish_post_internal(
        self, content: UniversalContent, options: Dict
    ) -> Dict[str, Any]:
        """Internal publish using UniversalContent."""
        media_type = self._determine_media_type(content)
        container_id = await self._create_media_container(content, media_type, options)
        publish_result = await self._publish_media_container(container_id)
        return {
            "post_id": publish_result.get("id"),
            "permalink": publish_result.get("permalink"),
            "status": "published",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "media_type": media_type,
            "container_id": container_id,
            "platform_data": publish_result,
        }

    async def _schedule_post_internal(
        self, content: UniversalContent, options: Dict
    ) -> Dict[str, Any]:
        """Internal schedule using UniversalContent."""
        media_type = self._determine_media_type(content)
        container_id = await self._create_media_container(content, media_type, options)
        scheduled_at = options.get("scheduled_at")
        return {
            "post_id": container_id,
            "permalink": None,
            "status": "scheduled",
            "published_at": scheduled_at.isoformat() if scheduled_at else None,
            "media_type": media_type,
            "platform_data": {"container_id": container_id},
        }

    # =========================================================================
    # BasePlatformAdapter — Post operations
    # =========================================================================

    async def publish_post(self, content: Union[PostContent, UniversalContent]) -> PostResult:
        """Publish a post to Instagram via the base adapter contract."""
        if isinstance(content, UniversalContent):
            universal_content = content
        else:
            universal_content = UniversalContent(
            content_type=ContentType.POST,
            text=content.text,
            caption=content.text,
            hashtags=content.hashtags or [],
            mentions=content.mentions or [],
            media=[
                UniversalMedia(
                    type=MediaType(getattr(m, "type", None) or getattr(m, "media_type", None)) if isinstance(getattr(m, "type", None) or getattr(m, "media_type", None), str) else getattr(m, "type", None) or getattr(m, "media_type", None),
                    url=m.url,
                    alt_text=m.alt_text,
                    duration_seconds=getattr(m, "duration", None) or getattr(m, "duration_seconds", None),
                    thumbnail_url=m.thumbnail_url,
                )
                for m in (content.media or [])
            ],
            location_id=getattr(content, "location", None) or getattr(content, "location_id", None),
        )
        options = getattr(content, "platform_specific", None) or getattr(content, "platform_data", None) or {}
        result = await self._publish_post_internal(universal_content, options)
        platform_data = dict(result.get("platform_data") or {})
        platform_data.setdefault("container_id", result.get("container_id"))
        platform_data.setdefault("media_type", result.get("media_type"))
        return PostResult(
            platform_post_id=result.get("post_id", ""),
            url=result.get("permalink"),
            status=result.get("status", "published"),
            published_at=result.get("published_at"),
            platform_data=platform_data,
        )

    async def schedule_post(self, content: Union[PostContent, UniversalContent], scheduled_at: datetime) -> PostResult:
        """Schedule a post for later via the base adapter contract."""
        if isinstance(content, UniversalContent):
            universal_content = content
            if scheduled_at and not universal_content.scheduled_at:
                universal_content.scheduled_at = scheduled_at
        else:
            universal_content = UniversalContent(
            content_type=ContentType.POST,
            text=content.text,
            caption=content.text,
            hashtags=content.hashtags or [],
            mentions=content.mentions or [],
            media=[
                UniversalMedia(
                    type=MediaType(getattr(m, "type", None) or getattr(m, "media_type", None)) if isinstance(getattr(m, "type", None) or getattr(m, "media_type", None), str) else getattr(m, "type", None) or getattr(m, "media_type", None),
                    url=m.url,
                    alt_text=m.alt_text,
                    duration_seconds=getattr(m, "duration", None) or getattr(m, "duration_seconds", None),
                    thumbnail_url=m.thumbnail_url,
                )
                for m in (content.media or [])
            ],
            location_id=getattr(content, "location", None) or getattr(content, "location_id", None),
            scheduled_at=scheduled_at,
        )
        options = dict(content.platform_specific or {})
        options["scheduled_at"] = scheduled_at
        result = await self._schedule_post_internal(universal_content, options)
        return PostResult(
            platform_post_id=result.get("post_id", ""),
            url=result.get("permalink"),
            status=result.get("status", "scheduled"),
            published_at=result.get("published_at"),
            platform_data=result.get("platform_data", {}),
        )

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

    # =========================================================================
    # BasePlatformAdapter — Analytics
    # =========================================================================

    async def get_post_analytics(self, post_id: str) -> AnalyticsData:
        """Get analytics for a post."""
        insights = await self._fetch_insights(post_id)
        normalized = insights.get("normalized", {})
        return AnalyticsData(
            post_id=post_id,
            impressions=normalized.get("impressions", 0),
            reach=normalized.get("reach", 0),
            likes=normalized.get("likes", 0),
            comments=normalized.get("comments", 0),
            shares=normalized.get("shares", 0),
            saves=normalized.get("saves", 0),
            clicks=normalized.get("clicks", 0),
            video_views=normalized.get("video_views", 0),
            engagement=sum([
                normalized.get("likes", 0),
                normalized.get("comments", 0),
                normalized.get("shares", 0),
                normalized.get("saves", 0),
                normalized.get("clicks", 0),
            ]),
            platform_data=insights,
        )

    async def get_account_analytics(
        self, since: datetime, until: datetime
    ) -> Dict[str, Any]:
        """Get account-level analytics."""
        client = await self._get_client()
        response = await client.get(
            f"/{self.ig_user_id}/insights",
            params={
                "metric": "impressions,reach,profile_views,follower_count",
                "period": "day",
                "since": int(since.timestamp()),
                "until": int(until.timestamp()),
            },
        )
        if response.status_code != 200:
            raise PlatformError(
                f"Account insights fetch failed: {response.text}",
                platform=self.PLATFORM_NAME,
            )
        data = response.json()
        raw = {item["name"]: item["values"][0]["value"] for item in data.get("data", [])}
        return MetricNormalizer.normalize_metrics(raw, self.PLATFORM_NAME)

    # =========================================================================
    # BasePlatformAdapter — Comments
    # =========================================================================

    async def get_comments(self, post_id: str, limit: int = 50) -> List[CommentData]:
        """Get comments on a post."""
        client = await self._get_client()
        response = await client.get(
            f"/{post_id}/comments",
            params={"limit": limit, "fields": "id,text,timestamp,username,like_count"},
        )
        if response.status_code != 200:
            raise PlatformError(
                f"Get comments failed: {response.text}",
                platform=self.PLATFORM_NAME,
            )
        data = response.json().get("data", [])
        return [
            CommentData(
                id=c["id"],
                post_id=post_id,
                author_id="",
                author_name=c.get("username", ""),
                text=c.get("text", ""),
                created_at=datetime.fromisoformat(c["timestamp"].replace("Z", "+00:00"))
                if "timestamp" in c
                else datetime.now(timezone.utc),
                platform_data=c,
            )
            for c in data
        ]

    async def reply_to_comment(self, comment_id: str, text: str) -> CommentData:
        """Reply to a comment."""
        result = await self._reply_comment(comment_id, text)
        return CommentData(
            id=result.get("id", ""),
            post_id="",
            author_id=self.ig_user_id or "",
            author_name="",
            text=text,
            created_at=datetime.now(timezone.utc),
            platform_data=result,
        )

    async def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment."""
        client = await self._get_client()
        response = await client.delete(f"/{comment_id}")
        return response.status_code == 200

    async def hide_comment(self, comment_id: str) -> bool:
        """Hide a comment."""
        client = await self._get_client()
        response = await client.post(f"/{comment_id}", data={"hidden": "true"})
        return response.status_code == 200

    # =========================================================================
    # BasePlatformAdapter — Profile
    # =========================================================================

    async def get_profile(self) -> Dict[str, Any]:
        """Get profile info."""
        client = await self._get_client()
        response = await client.get(
            f"/{self.ig_user_id}",
            params={
                "fields": "id,username,account_type,media_count,biography,website,profile_picture_url"
            },
        )
        if response.status_code != 200:
            raise PlatformError(
                f"Get profile failed: {response.text}",
                platform=self.PLATFORM_NAME,
            )
        return response.json()

    async def update_profile(self, data: Dict[str, Any]) -> bool:
        """Update profile — limited to biography and website for Instagram."""
        client = await self._get_client()
        allowed_fields = {k: v for k, v in data.items() if k in ("biography", "website")}
        if not allowed_fields:
            return False
        response = await client.post(f"/{self.ig_user_id}", data=allowed_fields)
        return response.status_code == 200

    # =========================================================================
    # BasePlatformAdapter — Media
    # =========================================================================

    async def upload_media(self, media: MediaItem) -> str:
        """Upload media and return media ID."""
        universal_media = UniversalMedia(
            type=MediaType(media.media_type)
            if isinstance(media.media_type, str)
            else media.media_type,
            url=media.url,
            alt_text=media.alt_text,
            duration_seconds=media.duration,
            thumbnail_url=media.thumbnail_url,
        )
        return await self._upload_media(universal_media, media.media_type)

    # =========================================================================
    # Instagram-specific helpers (kept for internal / publisher use)
    # =========================================================================

    async def fetch_insights(
        self, post_id: str, metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Fetch insights/metrics for a post (Instagram-specific)."""
        return await self._fetch_insights(post_id, metrics)

    async def _fetch_insights(
        self, post_id: str, metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Fetch and normalize insights for a media item."""
        client = await self._get_client()
        default_metrics = [
            "impressions", "reach", "likes", "comments", "shares", "saves",
            "video_views", "profile_visits", "follows",
        ]
        metric_list = metrics or default_metrics

        response = await client.get(
            f"/{post_id}/insights",
            params={"metric": ",".join(metric_list), "period": "lifetime"},
        )
        if response.status_code != 200:
            raise PlatformError(
                f"Insights fetch failed: {response.text}",
                platform=self.PLATFORM_NAME, details={"status_code": response.status_code,
            })
        data = response.json()
        raw = {item["name"]: item["values"][0]["value"] for item in data.get("data", [])}
        return MetricNormalizer.normalize_metrics(raw, self.PLATFORM_NAME)

    async def fetch_account_insights(
        self, metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Fetch account-level insights (Instagram-specific)."""
        client = await self._get_client()
        default_metrics = [
            "followers_count", "impressions", "reach", "profile_views",
            "website_clicks", "email_contacts", "phone_call_clicks",
        ]
        metric_list = metrics or default_metrics

        response = await client.get(
            f"/{self.ig_user_id}/insights",
            params={"metric": ",".join(metric_list), "period": "day"},
        )
        if response.status_code != 200:
            raise PlatformError(
                f"Account insights failed: {response.text}",
                platform=self.PLATFORM_NAME,
            )
        data = response.json()
        raw = {item["name"]: item["values"][0]["value"] for item in data.get("data", [])}
        return MetricNormalizer.normalize_metrics(raw, self.PLATFORM_NAME)

    async def _reply_comment(self, comment_id: str, text: str) -> Dict[str, Any]:
        """Reply to a comment (returns raw API response)."""
        client = await self._get_client()
        response = await client.post(f"/{comment_id}/replies", data={"message": text})
        if response.status_code != 200:
            raise PlatformError(
                f"Reply comment failed: {response.text}",
                platform=self.PLATFORM_NAME,
            )
        return response.json()

    async def subscribe_webhook(
        self, callback_url: str, verify_token: str, fields: List[str]
    ) -> Dict[str, Any]:
        """Subscribe to Instagram webhooks."""
        client = await self._get_client()
        response = await client.post(
            f"/{self.ig_user_id}/subscribed_apps",
            data={
                "subscribed_fields": ",".join(fields),
                "callback_url": callback_url,
                "verify_token": verify_token,
            },
        )
        if response.status_code != 200:
            raise PlatformError(
                f"Webhook subscribe failed: {response.text}",
                platform=self.PLATFORM_NAME,
            )
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
        token_valid = await self.validate_connection()
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

    # =========================================================================
    # Lifecycle
    # =========================================================================

    async def close(self):
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()
