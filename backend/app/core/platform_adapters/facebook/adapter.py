"""Facebook Graph API Adapter Implementation."""

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
from .auth import FacebookAuth, FacebookAuthConfig
from .publisher import FacebookPublisher
from .insights import FacebookInsights


class FacebookAdapter(BasePlatformAdapter):
    """Facebook Graph API adapter for Pages."""

    PLATFORM_NAME = "facebook"
    BASE_URL = "https://graph.facebook.com/v19.0"

    SUPPORTED_CAPABILITIES = {
        PlatformCapability.POST_TEXT,
        PlatformCapability.POST_IMAGE,
        PlatformCapability.POST_VIDEO,
        PlatformCapability.SCHEDULE_POST,
        PlatformCapability.DELETE_POST,
        PlatformCapability.GET_POST,
        PlatformCapability.GET_ANALYTICS,
        PlatformCapability.GET_INSIGHTS,
        PlatformCapability.REPLY_COMMENT,
        PlatformCapability.DELETE_COMMENT,
        PlatformCapability.HIDE_COMMENT,
        PlatformCapability.GET_PROFILE,
        PlatformCapability.UPDATE_PROFILE,
        PlatformCapability.MANAGE_WEBHOOKS,
    }

    RATE_LIMIT_CALLS = 200
    RATE_LIMIT_WINDOW = 3600

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.redirect_uri = config.get("redirect_uri")
        self.access_token = config.get("access_token")
        self.page_id = config.get("page_id")
        self._http_client: Optional[httpx.AsyncClient] = None

        self.auth = FacebookAuth(
            FacebookAuthConfig(
                client_id=self.client_id or "",
                client_secret=self.client_secret or "",
                redirect_uri=self.redirect_uri or "",
            )
        )
        self.publisher = FacebookPublisher(self)
        self.insights = FacebookInsights(self)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=30.0,
                headers={"Authorization": f"Bearer {self.access_token}"} if self.access_token else {},
            )
        return self._http_client

    @property
    def platform_name(self) -> str:
        return self.PLATFORM_NAME

    async def authenticate(self, credentials: Dict[str, Any]) -> Union[bool, Dict[str, Any]]:
        """Authenticate using code or direct access token."""
        if "code" in credentials:
            tokens = await self.auth.exchange_code(credentials["code"])
            self.access_token = tokens.get("access_token")
            # If user has a page, auto-resolve page access token
            try:
                page_info = await self.auth.get_page_access_token(self.access_token, credentials.get("page_id"))
                self.access_token = page_info["page_access_token"]
                self.page_id = page_info["page_id"]
                tokens["page_id"] = self.page_id
            except Exception:
                pass
            return tokens

        self.access_token = credentials.get("access_token")
        self.page_id = credentials.get("page_id")
        return await self.validate_connection()

    async def refresh_token(self) -> bool:
        return True  # Page access tokens do not expire if exchanged from 60-day token

    async def validate_connection(self) -> bool:
        try:
            client = await self._get_client()
            target = self.page_id or "me"
            resp = await client.get(f"/{target}", params={"fields": "id,name"})
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
                        type=MediaType(getattr(m, "type", None) or getattr(m, "media_type", None)),
                        url=m.url,
                        alt_text=m.alt_text,
                    )
                    for m in (content.media or [])
                ],
                location_id=getattr(content, "location", None),
            )

        res = await self.publisher.publish(universal_content)
        return PostResult(
            platform_post_id=res.post_id,
            url=res.permalink,
            status="published",
            published_at=datetime.now(timezone.utc),
            platform_data={"media_type": res.media_type},
        )

    async def schedule_post(self, content: Union[PostContent, UniversalContent], scheduled_at: datetime) -> PostResult:
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
                        type=MediaType(getattr(m, "type", None) or getattr(m, "media_type", None)),
                        url=m.url,
                        alt_text=m.alt_text,
                    )
                    for m in (content.media or [])
                ],
                scheduled_at=scheduled_at,
            )

        res = await self.publisher.publish(universal_content, options={"scheduled_at": scheduled_at})
        return PostResult(
            platform_post_id=res.post_id,
            url=res.permalink,
            status="scheduled",
            published_at=None,
            platform_data={"media_type": res.media_type},
        )

    async def delete_post(self, post_id: str) -> bool:
        client = await self._get_client()
        resp = await client.delete(f"/{post_id}")
        return resp.status_code == 200

    async def get_post(self, post_id: str) -> Dict[str, Any]:
        client = await self._get_client()
        resp = await client.get(f"/{post_id}", params={"fields": "id,message,created_time,permalink_url"})
        if resp.status_code != 200:
            raise PlatformError(f"Facebook get post failed: {resp.text}", platform="facebook")
        return resp.json()

    async def get_post_analytics(self, post_id: str) -> AnalyticsData:
        insights = await self.insights.get_post_insights(post_id)
        norm = insights.get("normalized", {})
        return AnalyticsData(
            post_id=post_id,
            impressions=norm.get("impressions", 0),
            reach=norm.get("reach", 0),
            likes=norm.get("likes", 0),
            comments=norm.get("comments", 0),
            shares=norm.get("shares", 0),
            video_views=norm.get("video_views", 0),
            engagement=sum([norm.get("likes", 0), norm.get("comments", 0), norm.get("shares", 0)]),
            platform_data=insights,
        )

    async def get_account_analytics(self, since: datetime, until: datetime) -> Dict[str, Any]:
        return await self.insights.get_page_insights()

    async def get_comments(self, post_id: str, limit: int = 50) -> List[CommentData]:
        client = await self._get_client()
        resp = await client.get(f"/{post_id}/comments", params={"limit": limit, "fields": "id,message,created_time,from,like_count"})
        if resp.status_code != 200:
            raise PlatformError(f"Facebook get comments failed: {resp.text}", platform="facebook")
        data = resp.json().get("data", [])
        return [
            CommentData(
                id=c["id"],
                post_id=post_id,
                author_id=c.get("from", {}).get("id", ""),
                author_name=c.get("from", {}).get("name", ""),
                text=c.get("message", ""),
                created_at=datetime.fromisoformat(c["created_time"].replace("Z", "+00:00")) if "created_time" in c else datetime.now(timezone.utc),
                platform_data=c,
            )
            for c in data
        ]

    async def reply_to_comment(self, comment_id: str, text: str) -> CommentData:
        client = await self._get_client()
        resp = await client.post(f"/{comment_id}/comments", data={"message": text})
        if resp.status_code != 200:
            raise PlatformError(f"Facebook reply comment failed: {resp.text}", platform="facebook")
        res_data = resp.json()
        return CommentData(
            id=res_data.get("id", ""),
            post_id="",
            author_id=self.page_id or "",
            author_name="",
            text=text,
            created_at=datetime.now(timezone.utc),
            platform_data=res_data,
        )

    async def delete_comment(self, comment_id: str) -> bool:
        client = await self._get_client()
        resp = await client.delete(f"/{comment_id}")
        return resp.status_code == 200

    async def hide_comment(self, comment_id: str) -> bool:
        client = await self._get_client()
        resp = await client.post(f"/{comment_id}", data={"is_hidden": "true"})
        return resp.status_code == 200

    async def get_profile(self) -> Dict[str, Any]:
        client = await self._get_client()
        target = self.page_id or "me"
        resp = await client.get(f"/{target}", params={"fields": "id,name,link,picture,fan_count,about,website"})
        if resp.status_code != 200:
            raise PlatformError(f"Facebook get profile failed: {resp.text}", platform="facebook")
        return resp.json()

    async def update_profile(self, data: Dict[str, Any]) -> bool:
        client = await self._get_client()
        target = self.page_id or "me"
        allowed = {k: v for k, v in data.items() if k in ("about", "website", "description")}
        if not allowed:
            return False
        resp = await client.post(f"/{target}", data=allowed)
        return resp.status_code == 200

    async def upload_media(self, media: MediaItem) -> str:
        return media.url

    async def get_capabilities(self) -> set:
        return self.SUPPORTED_CAPABILITIES

    async def fetch_insights(self, post_id: str, metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        return await self.insights.get_post_insights(post_id, metrics)

    async def fetch_account_insights(self, metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        return await self.insights.get_page_insights(metrics)

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.close()
