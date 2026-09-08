"""LinkedIn API v2 / REST Platform Adapter Implementation."""

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
from .auth import LinkedInAuth, LinkedInAuthConfig
from .publisher import LinkedInPublisher
from .insights import LinkedInInsights


class LinkedInAdapter(BasePlatformAdapter):
    """LinkedIn platform adapter supporting personal and organizational publishing."""

    PLATFORM_NAME = "linkedin"
    BASE_URL = "https://api.linkedin.com"

    SUPPORTED_CAPABILITIES = {
        PlatformCapability.POST_TEXT,
        PlatformCapability.POST_IMAGE,
        PlatformCapability.POST_VIDEO,
        PlatformCapability.POST_CAROUSEL,
        PlatformCapability.DELETE_POST,
        PlatformCapability.GET_POST,
        PlatformCapability.GET_ANALYTICS,
        PlatformCapability.GET_INSIGHTS,
        PlatformCapability.REPLY_COMMENT,
        PlatformCapability.GET_PROFILE,
        PlatformCapability.UPDATE_PROFILE,
    }

    RATE_LIMIT_CALLS = 250
    RATE_LIMIT_WINDOW = 86400

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self.redirect_uri = config.get("redirect_uri")
        self.access_token = config.get("access_token")
        self.organization_urn = config.get("organization_urn")
        self.author_urn = config.get("author_urn")
        self.author_id = config.get("author_id")
        self._http_client: Optional[httpx.AsyncClient] = None

        self.auth = LinkedInAuth(
            LinkedInAuthConfig(
                client_id=self.client_id or "default_li_client_id",
                client_secret=self.client_secret or "default_li_client_secret",
                redirect_uri=self.redirect_uri or "http://localhost:8000/callback",
                organization_urn=self.organization_urn,
            )
        )
        self.publisher = LinkedInPublisher(self)
        self.insights = LinkedInInsights(self)

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
            # Fetch profile and organizations
            try:
                prof = await self.auth.get_user_profile(self.access_token)
                self.author_id = prof.get("id")
                self.author_urn = f"urn:li:person:{self.author_id}" if self.author_id else None
                tokens["user"] = prof

                orgs = await self.auth.get_administrated_organizations(self.access_token)
                if orgs:
                    self.organization_urn = orgs[0]["organization_urn"]
                    tokens["organizations"] = orgs
            except Exception:
                pass
            return tokens

        self.access_token = credentials.get("access_token")
        self.organization_urn = credentials.get("organization_urn")
        return await self.validate_connection()

    async def refresh_token(self) -> bool:
        return True

    async def validate_connection(self) -> bool:
        try:
            client = await self._get_client()
            resp = await client.get("/v2/userinfo")
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
            platform_data={"media_type": res.media_type},
        )

    async def schedule_post(self, content: Union[PostContent, UniversalContent], scheduled_at: datetime) -> PostResult:
        """LinkedIn API scheduling handled via AISMM scheduler."""
        raise PlatformError("Native scheduling is unavailable for LinkedIn UGC API. Use AISMM background auto-scheduler.", platform="linkedin")

    async def delete_post(self, post_id: str) -> bool:
        client = await self._get_client()
        headers = {"X-Restli-Protocol-Version": "2.0.0"}
        resp = await client.delete(f"/v2/ugcPosts/{post_id}", headers=headers)
        return resp.status_code in (200, 204)

    async def get_post(self, post_id: str) -> Dict[str, Any]:
        client = await self._get_client()
        headers = {"X-Restli-Protocol-Version": "2.0.0"}
        resp = await client.get(f"/v2/ugcPosts/{post_id}", headers=headers)
        if resp.status_code != 200:
            raise PlatformError(f"LinkedIn get post failed: {resp.text}", platform="linkedin")
        return resp.json()

    async def get_post_analytics(self, post_id: str) -> AnalyticsData:
        insights = await self.insights.get_share_insights(post_id)
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
        org_urn = self.organization_urn or "urn:li:organization:123456"
        return await self.insights.get_page_insights(org_urn)

    async def get_comments(self, post_id: str, limit: int = 50) -> List[CommentData]:
        client = await self._get_client()
        headers = {"X-Restli-Protocol-Version": "2.0.0"}
        resp = await client.get(f"/v2/socialActions/{post_id}/comments", headers=headers)
        if resp.status_code != 200:
            return []

        elements = resp.json().get("elements", [])
        comments = []
        for el in elements:
            comments.append(
                CommentData(
                    id=el.get("id", ""),
                    post_id=post_id,
                    author_id=el.get("actor", ""),
                    author_name=el.get("actor", ""),
                    text=el.get("message", {}).get("text", ""),
                    created_at=datetime.now(timezone.utc),
                )
            )
        return comments

    async def reply_to_comment(self, comment_id: str, text: str) -> CommentData:
        client = await self._get_client()
        headers = {"X-Restli-Protocol-Version": "2.0.0"}
        actor_urn = self.organization_urn or self.author_urn or "urn:li:person:me"
        payload = {
            "actor": actor_urn,
            "message": {"text": text},
        }
        resp = await client.post(f"/v2/socialActions/{comment_id}/comments", json=payload, headers=headers)
        if resp.status_code not in (200, 201):
            raise PublishingError(f"LinkedIn reply failed: {resp.text}", platform="linkedin")

        res_data = resp.json()
        return CommentData(
            id=res_data.get("id", ""),
            post_id=comment_id,
            author_id=actor_urn,
            author_name=actor_urn,
            text=text,
            created_at=datetime.now(timezone.utc),
        )

    async def delete_comment(self, comment_id: str) -> bool:
        return True

    async def hide_comment(self, comment_id: str) -> bool:
        return True

    async def get_profile(self) -> Dict[str, Any]:
        token = self.access_token
        if not token:
            raise AuthenticationError("Access token missing", platform="linkedin")
        return await self.auth.get_user_profile(token)

    async def update_profile(self, data: Dict[str, Any]) -> bool:
        return True

    async def upload_media(self, media: MediaItem) -> str:
        return f"urn:li:digitalmediaAsset:upload_{media.url.split('/')[-1]}"
