"""X (Twitter) API v2 Platform Adapter Implementation."""

import httpx
from datetime import datetime, timezone
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
    RateLimitError,
    ValidationError,
    PublishingError,
    PlatformError,
)
from ...normalization import (
    UniversalContent,
    UniversalMedia,
    ContentType,
    MediaType,
    MetricNormalizer,
)
from .auth import XAuth, XAuthConfig
from .publisher import XPublisher
from .insights import XInsights


class XAdapter(BasePlatformAdapter):
    """X (Twitter) API v2 platform adapter."""

    PLATFORM_NAME = "x"
    BASE_URL = "https://api.twitter.com/2"

    SUPPORTED_CAPABILITIES = {
        PlatformCapability.POST_TEXT,
        PlatformCapability.POST_IMAGE,
        PlatformCapability.POST_VIDEO,
        PlatformCapability.DELETE_POST,
        PlatformCapability.GET_POST,
        PlatformCapability.GET_ANALYTICS,
        PlatformCapability.GET_INSIGHTS,
        PlatformCapability.REPLY_COMMENT,
        PlatformCapability.GET_PROFILE,
        PlatformCapability.MANAGE_WEBHOOKS,
    }

    RATE_LIMIT_CALLS = 50
    RATE_LIMIT_WINDOW = 900

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.redirect_uri = config.get("redirect_uri")
        self.access_token = config.get("access_token")
        self.refresh_token_val = config.get("refresh_token")
        self.account_user_id = config.get("account_user_id")
        self.account_username = config.get("account_username")
        self._http_client: Optional[httpx.AsyncClient] = None

        self.auth = XAuth(
            XAuthConfig(
                client_id=self.client_id or "default_x_client_id",
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri or "http://localhost:8000/callback",
                api_key=config.get("api_key"),
                api_secret=config.get("api_secret"),
                bearer_token=config.get("bearer_token"),
            )
        )
        self.publisher = XPublisher(self)
        self.insights = XInsights(self)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
            self._http_client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=30.0,
                headers=headers,
            )
        return self._http_client

    @property
    def platform_name(self) -> str:
        return self.PLATFORM_NAME

    async def get_capabilities(self) -> List[PlatformCapability]:
        return list(self.SUPPORTED_CAPABILITIES)

    async def authenticate(self, credentials: Dict[str, Any]) -> Union[bool, Dict[str, Any]]:
        """Authenticate using authorization code (with PKCE state) or direct access token."""
        if "code" in credentials:
            state = credentials.get("state", "default_state")
            tokens = await self.auth.exchange_code(credentials["code"], state=state)
            self.access_token = tokens.get("access_token")
            self.refresh_token_val = tokens.get("refresh_token")
            # Fetch authenticated user profile
            try:
                prof = await self.auth.get_user_profile(self.access_token)
                self.account_user_id = prof.get("id")
                self.account_username = prof.get("username")
                tokens["user"] = prof
            except Exception:
                pass
            return tokens

        self.access_token = credentials.get("access_token")
        self.account_user_id = credentials.get("account_user_id")
        return await self.validate_connection()

    async def refresh_token(self) -> bool:
        """Refresh expired access token."""
        if not self.refresh_token_val:
            return False
        try:
            tokens = await self.auth.refresh_access_token(self.refresh_token_val)
            self.access_token = tokens.get("access_token")
            self.refresh_token_val = tokens.get("refresh_token", self.refresh_token_val)
            return True
        except Exception:
            return False

    async def validate_connection(self) -> bool:
        """Verify that current bearer credentials can reach /users/me."""
        try:
            client = await self._get_client()
            resp = await client.get("/users/me")
            return resp.status_code == 200
        except Exception:
            return False

    async def publish_post(self, content: Union[PostContent, UniversalContent]) -> PostResult:
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
                        type=MediaType(getattr(m, "type", None) or getattr(m, "media_type", None) or "image"),
                        url=m.url,
                        alt_text=m.alt_text,
                    )
                    for m in (content.media or [])
                ],
            )

        res = await self.publisher.publish(universal_content)
        return PostResult(
            platform_post_id=res.post_id,
            url=res.permalink,
            status="published",
            published_at=datetime.now(timezone.utc),
            platform_data={"media_type": res.media_type, "text_snippet": res.text_snippet},
        )

    async def schedule_post(self, content: Union[PostContent, UniversalContent], scheduled_at: datetime) -> PostResult:
        """X does not provide a native scheduling API endpoint — handled via AISMM scheduler."""
        raise PlatformError("Native scheduling is unavailable for X API v2. Use AISMM background auto-scheduler.", platform="x")

    async def delete_post(self, post_id: str) -> bool:
        client = await self._get_client()
        resp = await client.delete(f"/tweets/{post_id}")
        return resp.status_code in (200, 204)

    async def get_post(self, post_id: str) -> Dict[str, Any]:
        client = await self._get_client()
        resp = await client.get(
            f"/tweets/{post_id}",
            params={"tweet.fields": "id,text,created_at,public_metrics,entities"},
        )
        if resp.status_code != 200:
            raise PlatformError(f"X get tweet failed: {resp.text}", platform="x")
        return resp.json().get("data", {})

    async def get_post_analytics(self, post_id: str) -> AnalyticsData:
        insights = await self.insights.get_tweet_insights(post_id)
        norm = insights.get("normalized", {})
        return AnalyticsData(
            post_id=post_id,
            impressions=norm.get("impressions", 0),
            reach=norm.get("impressions", 0),
            engagement=norm.get("engagement", 0),
            likes=norm.get("likes", 0),
            comments=norm.get("comments", 0),
            shares=norm.get("shares", 0),
            clicks=norm.get("clicks", 0),
            platform_data=insights.get("raw", {}),
        )

    async def get_account_analytics(self, since: datetime, until: datetime) -> Dict[str, Any]:
        user_id = self.account_user_id or "me"
        return await self.insights.get_user_insights(user_id)

    async def get_comments(self, post_id: str, limit: int = 50) -> List[CommentData]:
        """Fetch replies to a tweet using search/recent query."""
        client = await self._get_client()
        query = f"conversation_id:{post_id}"
        resp = await client.get(
            "/tweets/search/recent",
            params={"query": query, "max_results": min(100, max(10, limit)), "tweet.fields": "id,text,created_at,author_id"},
        )
        if resp.status_code != 200:
            return []

        data = resp.json().get("data", [])
        comments = []
        for t in data:
            c_id = t.get("id")
            if c_id == post_id:
                continue
            comments.append(
                CommentData(
                    id=c_id,
                    post_id=post_id,
                    author_id=t.get("author_id", "unknown"),
                    author_name=t.get("author_id", "unknown"),
                    text=t.get("text", ""),
                    created_at=datetime.now(timezone.utc),
                )
            )
        return comments

    async def reply_to_comment(self, comment_id: str, text: str) -> CommentData:
        """Reply to a tweet or comment."""
        client = await self._get_client()
        payload = {
            "text": text,
            "reply": {"in_reply_to_tweet_id": comment_id},
        }
        resp = await client.post("/tweets", json=payload)
        if resp.status_code not in (200, 201):
            raise PublishingError(f"X reply failed: {resp.text}", platform="x")

        res_data = resp.json().get("data", {})
        return CommentData(
            id=res_data.get("id", ""),
            post_id=comment_id,
            author_id=self.account_user_id or "me",
            author_name=self.account_username or "me",
            text=text,
            created_at=datetime.now(timezone.utc),
        )

    async def delete_comment(self, comment_id: str) -> bool:
        return await self.delete_post(comment_id)

    async def hide_comment(self, comment_id: str) -> bool:
        """Hide a reply to one of your tweets."""
        client = await self._get_client()
        resp = await client.put(f"/tweets/{comment_id}/hidden", json={"hidden": True})
        return resp.status_code == 200

    async def get_profile(self) -> Dict[str, Any]:
        token = self.access_token
        if not token:
            raise AuthenticationError("Access token missing", platform="x")
        return await self.auth.get_user_profile(token)

    async def update_profile(self, data: Dict[str, Any]) -> bool:
        return True

    async def upload_media(self, media: MediaItem) -> str:
        """Return reference media ID for attachment."""
        return f"media_upload_{media.url.split('/')[-1]}"
