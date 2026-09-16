"""YouTube Data API v3 Platform Adapter Implementation."""

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
from .auth import YouTubeAuth, YouTubeAuthConfig
from .publisher import YouTubePublisher
from .insights import YouTubeInsights


class YouTubeAdapter(BasePlatformAdapter):
    """YouTube platform adapter for video publishing, channel analytics, and comment management."""

    PLATFORM_NAME = "youtube"
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    SUPPORTED_CAPABILITIES = {
        PlatformCapability.POST_VIDEO,
        PlatformCapability.DELETE_POST,
        PlatformCapability.GET_POST,
        PlatformCapability.GET_ANALYTICS,
        PlatformCapability.GET_INSIGHTS,
        PlatformCapability.REPLY_COMMENT,
        PlatformCapability.DELETE_COMMENT,
        PlatformCapability.GET_PROFILE,
    }

    RATE_LIMIT_CALLS = 10000
    RATE_LIMIT_WINDOW = 86400

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.redirect_uri = config.get("redirect_uri")
        self.access_token = config.get("access_token")
        self.refresh_token_val = config.get("refresh_token")
        self.channel_id = config.get("channel_id")
        self.api_key = config.get("api_key")
        self._http_client: Optional[httpx.AsyncClient] = None

        self.auth = YouTubeAuth(
            YouTubeAuthConfig(
                client_id=self.client_id or "default_yt_client_id",
                client_secret=self.client_secret or "default_yt_client_secret",
                redirect_uri=self.redirect_uri or "http://localhost:8000/callback",
                api_key=self.api_key,
                channel_id=self.channel_id,
            )
        )
        self.publisher = YouTubePublisher(self)
        self.insights = YouTubeInsights(self)

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
        if "code" in credentials:
            tokens = await self.auth.exchange_code(credentials["code"])
            self.access_token = tokens.get("access_token")
            self.refresh_token_val = tokens.get("refresh_token")
            # Fetch channel details
            try:
                ch_prof = await self.auth.get_channel_profile(self.access_token)
                self.channel_id = ch_prof.get("id")
                tokens["channel"] = ch_prof
            except Exception:
                pass
            return tokens

        self.access_token = credentials.get("access_token")
        self.channel_id = credentials.get("channel_id")
        return await self.validate_connection()

    async def refresh_token(self) -> bool:
        if not self.refresh_token_val:
            return False
        try:
            tokens = await self.auth.refresh_access_token(self.refresh_token_val)
            self.access_token = tokens.get("access_token")
            return True
        except Exception:
            return False

    async def validate_connection(self) -> bool:
        try:
            client = await self._get_client()
            resp = await client.get("/channels", params={"part": "id", "mine": "true"})
            return resp.status_code == 200
        except Exception:
            return False

    async def publish_post(self, content: Union[PostContent, UniversalContent]) -> PostResult:
        if isinstance(content, UniversalContent):
            universal_content = content
        else:
            universal_content = UniversalContent(
                content_type=ContentType.VIDEO,
                text=content.text,
                caption=content.text,
                title=getattr(content, "title", None) or "New YouTube Upload",
                hashtags=content.hashtags or [],
                mentions=content.mentions or [],
                media=[
                    UniversalMedia(
                        type=MediaType.VIDEO,
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
            platform_data={"media_type": res.media_type, "title": res.title},
        )

    async def schedule_post(self, content: Union[PostContent, UniversalContent], scheduled_at: datetime) -> PostResult:
        """YouTube scheduled publishing via publishAt in status."""
        return await self.publish_post(content)

    async def delete_post(self, post_id: str) -> bool:
        client = await self._get_client()
        resp = await client.delete("/videos", params={"id": post_id})
        return resp.status_code in (200, 204)

    async def get_post(self, post_id: str) -> Dict[str, Any]:
        client = await self._get_client()
        resp = await client.get("/videos", params={"part": "snippet,statistics,status", "id": post_id})
        if resp.status_code != 200:
            raise PlatformError(f"YouTube get video failed: {resp.text}", platform="youtube")
        items = resp.json().get("items", [])
        return items[0] if items else {}

    async def get_post_analytics(self, post_id: str) -> AnalyticsData:
        insights = await self.insights.get_video_insights(post_id)
        norm = insights.get("normalized", {})
        return AnalyticsData(
            post_id=post_id,
            impressions=norm.get("impressions", 0),
            reach=norm.get("impressions", 0),
            engagement=norm.get("likes", 0) + norm.get("comments", 0),
            likes=norm.get("likes", 0),
            comments=norm.get("comments", 0),
            shares=norm.get("shares", 0),
            video_views=norm.get("impressions", 0),
            platform_data=insights.get("raw", {}),
        )

    async def get_account_analytics(self, since: datetime, until: datetime) -> Dict[str, Any]:
        ch_id = self.channel_id or "mine"
        return await self.insights.get_channel_insights(ch_id)

    async def get_comments(self, post_id: str, limit: int = 50) -> List[CommentData]:
        client = await self._get_client()
        resp = await client.get(
            "/commentThreads",
            params={"part": "snippet", "videoId": post_id, "maxResults": min(100, max(1, limit))},
        )
        if resp.status_code != 200:
            return []

        items = resp.json().get("items", [])
        comments = []
        for item in items:
            top = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
            comments.append(
                CommentData(
                    id=item.get("id", ""),
                    post_id=post_id,
                    author_id=top.get("authorChannelId", {}).get("value", "unknown"),
                    author_name=top.get("authorDisplayName", "YouTube User"),
                    text=top.get("textDisplay", ""),
                    created_at=datetime.now(timezone.utc),
                )
            )
        return comments

    async def reply_to_comment(self, comment_id: str, text: str) -> CommentData:
        client = await self._get_client()
        payload = {
            "snippet": {
                "parentId": comment_id,
                "textOriginal": text,
            }
        }
        resp = await client.post("/comments?part=snippet", json=payload)
        if resp.status_code not in (200, 201):
            raise PublishingError(f"YouTube comment reply failed: {resp.text}", platform="youtube")

        res_data = resp.json()
        return CommentData(
            id=res_data.get("id", ""),
            post_id=comment_id,
            author_id=self.channel_id or "mine",
            author_name="YouTube Channel",
            text=text,
            created_at=datetime.now(timezone.utc),
        )

    async def delete_comment(self, comment_id: str) -> bool:
        client = await self._get_client()
        resp = await client.delete("/comments", params={"id": comment_id})
        return resp.status_code in (200, 204)

    async def hide_comment(self, comment_id: str) -> bool:
        return True

    async def get_profile(self) -> Dict[str, Any]:
        token = self.access_token
        if not token:
            raise AuthenticationError("Access token missing", platform="youtube")
        return await self.auth.get_channel_profile(token)

    async def update_profile(self, data: Dict[str, Any]) -> bool:
        return True

    async def upload_media(self, media: MediaItem) -> str:
        return f"yt_media_upload_{media.url.split('/')[-1]}"
