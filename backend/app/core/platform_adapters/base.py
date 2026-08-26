"""Base platform adapter interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from backend.app.core.errors import PlatformError, UnsupportedCapabilityError


class PlatformCapability(str, Enum):
    """Platform capabilities."""
    POST_TEXT = "post_text"
    POST_IMAGE = "post_image"
    POST_VIDEO = "post_video"
    POST_CAROUSEL = "post_carousel"
    POST_STORY = "post_story"
    POST_REEL = "post_reel"
    SCHEDULE_POST = "schedule_post"
    DELETE_POST = "delete_post"
    GET_POST = "get_post"
    GET_ANALYTICS = "get_analytics"
    GET_INSIGHTS = "get_insights"
    GET_AUDIENCE = "get_audience"
    REPLY_COMMENT = "reply_comment"
    DELETE_COMMENT = "delete_comment"
    HIDE_COMMENT = "hide_comment"
    LIKE_POST = "like_post"
    SHARE_POST = "share_post"
    GET_MENTIONS = "get_mentions"
    SEARCH_CONTENT = "search_content"
    GET_PROFILE = "get_profile"
    UPDATE_PROFILE = "update_profile"
    MANAGE_WEBHOOKS = "manage_webhooks"
    BULK_UPLOAD = "bulk_upload"
    MEDIA_LIBRARY = "media_library"


@dataclass
class MediaItem:
    """Media attachment for posts."""
    media_type: str  # image, video, gif
    url: str
    alt_text: Optional[str] = None
    duration: Optional[int] = None
    thumbnail_url: Optional[str] = None
    aspect_ratio: Optional[float] = None


@dataclass
class PostContent:
    """Content for a social media post."""
    text: str
    media: List[MediaItem] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    location: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    platform_specific: Dict[str, Any] = None

    def __post_init__(self):
        if self.media is None:
            self.media = []
        if self.hashtags is None:
            self.hashtags = []
        if self.mentions is None:
            self.mentions = []
        if self.platform_specific is None:
            self.platform_specific = {}


@dataclass
class PostResult:
    """Result of a post operation."""
    platform_post_id: str
    url: Optional[str] = None
    status: str = "published"
    published_at: Optional[datetime] = None
    platform_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.platform_data is None:
            self.platform_data = {}


@dataclass
class AnalyticsData:
    """Analytics data for a post."""
    post_id: str
    impressions: int = 0
    reach: int = 0
    engagement: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    clicks: int = 0
    video_views: int = 0
    video_watch_time: int = 0
    collected_at: Optional[datetime] = None
    platform_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.platform_data is None:
            self.platform_data = {}
        if self.collected_at is None:
            self.collected_at = datetime.utcnow()


@dataclass
class CommentData:
    """Comment data."""
    id: str
    post_id: str
    author_id: str
    author_name: str
    text: str
    created_at: datetime
    is_hidden: bool = False
    is_deleted: bool = False
    platform_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.platform_data is None:
            self.platform_data = {}


class BasePlatformAdapter(ABC):
    """Abstract base class for platform adapters."""

    PLATFORM_NAME: str = "base"
    SUPPORTED_CAPABILITIES: List[PlatformCapability] = []

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._session = None

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return platform name."""
        pass

    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with platform."""
        pass

    @abstractmethod
    async def refresh_token(self) -> bool:
        """Refresh access token."""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Validate connection is active."""
        pass

    # Post operations
    @abstractmethod
    async def publish_post(self, content: PostContent) -> PostResult:
        """Publish a post."""
        pass

    @abstractmethod
    async def schedule_post(self, content: PostContent, scheduled_at: datetime) -> PostResult:
        """Schedule a post for later."""
        pass

    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        """Delete a post."""
        pass

    @abstractmethod
    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """Get post details."""
        pass

    # Analytics
    @abstractmethod
    async def get_post_analytics(self, post_id: str) -> AnalyticsData:
        """Get analytics for a post."""
        pass

    @abstractmethod
    async def get_account_analytics(
        self,
        since: datetime,
        until: datetime,
    ) -> Dict[str, Any]:
        """Get account-level analytics."""
        pass

    # Comments
    @abstractmethod
    async def get_comments(self, post_id: str, limit: int = 50) -> List[CommentData]:
        """Get comments on a post."""
        pass

    @abstractmethod
    async def reply_to_comment(self, comment_id: str, text: str) -> CommentData:
        """Reply to a comment."""
        pass

    @abstractmethod
    async def delete_comment(self, comment_id: str) -> bool:
        """Delete a comment."""
        pass

    @abstractmethod
    async def hide_comment(self, comment_id: str) -> bool:
        """Hide a comment."""
        pass

    # Profile
    @abstractmethod
    async def get_profile(self) -> Dict[str, Any]:
        """Get profile info."""
        pass

    @abstractmethod
    async def update_profile(self, data: Dict[str, Any]) -> bool:
        """Update profile."""
        pass

    # Media
    @abstractmethod
    async def upload_media(self, media: MediaItem) -> str:
        """Upload media and return media ID."""
        pass

    def supports(self, capability: PlatformCapability) -> bool:
        """Check if platform supports a capability."""
        return capability in self.SUPPORTED_CAPABILITIES

    def require_capability(self, capability: PlatformCapability) -> None:
        """Raise error if capability not supported."""
        if not self.supports(capability):
            raise UnsupportedCapabilityError(capability.value, self.platform_name)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Clean up resources."""
        pass