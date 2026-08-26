"""
Platform Data Models

Universal data models used across all platform adapters.
Platform-agnostic representations that the AI core consumes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import uuid4


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    GIF = "gif"
    DOCUMENT = "document"
    AUDIO = "audio"


class ContentType(str, Enum):
    POST = "post"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    ARTICLE = "article"
    VIDEO = "video"
    CAROUSEL = "carousel"


class MetricType(str, Enum):
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    REACTION = "reaction"
    VIEW = "view"
    SAVE = "save"
    CLICK = "click"
    IMPRESSION = "impression"
    REACH = "reach"
    FOLLOWER = "follower"
    WATCH_TIME = "watch_time"


@dataclass
class MediaItem:
    """Media attachment for posts."""
    id: str = field(default_factory=lambda: str(uuid4()))
    media_type: MediaType = MediaType.IMAGE
    file_path: Optional[str] = None  # Local path
    url: Optional[str] = None  # Public URL
    thumbnail_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[int] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    alt_text: Optional[str] = None
    platform_media_ids: Dict[str, str] = field(default_factory=dict)  # platform -> media_id
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UniversalContent:
    """
    Platform-neutral content representation.
    This is what the AI core and content management work with.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    text: str = ""
    caption: str = ""
    title: Optional[str] = None
    media: List[MediaItem] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    location: Optional[str] = None
    language: str = "en"
    content_type: ContentType = ContentType.POST
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "caption": self.caption,
            "title": self.title,
            "media": [{"type": m.media_type.value, "url": m.url, "path": m.file_path} for m in self.media],
            "hashtags": self.hashtags,
            "mentions": self.mentions,
            "links": self.links,
            "location": self.location,
            "language": self.language,
            "content_type": self.content_type.value,
            "metadata": self.metadata,
        }


@dataclass
class PlatformSpecificPayload:
    """Platform-specific payload ready for API submission."""
    platform: str
    text: str
    media_ids: List[str] = field(default_factory=list)
    media_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "text": self.text,
            "media_ids": self.media_ids,
            "media_type": self.media_type,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "extra": self.extra,
        }


@dataclass
class NormalizedPost:
    """Platform-normalized post for analytics/AI."""
    platform_post_id: str
    platform_id: str
    content: str
    caption: str
    media_type: Optional[MediaType]
    posted_at: datetime
    engagement: Dict[str, int] = field(default_factory=dict)  # metric_type -> value
    engagement_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedComment:
    """Platform-normalized comment/reply."""
    platform_comment_id: str
    platform_id: str
    publication_id: str  # Our PostPublication ID
    author_username: str
    author_id: str
    author_avatar_url: Optional[str]
    text: str
    sentiment_score: Optional[float] = None  # -1 to 1
    sentiment_label: Optional[str] = None  # very_positive, positive, neutral, negative, very_negative
    like_count: int = 0
    reply_count: int = 0
    is_reply: bool = False
    parent_comment_id: Optional[str] = None
    platform_created_at: datetime = field(default_factory=datetime.utcnow)
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    our_reply: Optional[str] = None
    replied_at: Optional[datetime] = None


@dataclass
class NormalizedEngagement:
    """Platform-normalized engagement metrics."""
    metric_type: MetricType
    value: int
    source_platform: str
    original_metric: str  # e.g., "retweet_count", "reaction_count"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


@dataclass
class NormalizedAccountMetrics:
    """Platform-normalized account-level metrics."""
    platform_id: str
    platform_account_id: str
    followers: int = 0
    following: int = 0
    posts_count: int = 0
    total_engagement: int = 0
    avg_engagement_rate: float = 0.0
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedPostAnalytics:
    """Platform-normalized post analytics."""
    platform_post_id: str
    platform_id: str
    impressions: int = 0
    reach: int = 0
    engagement: Dict[str, int] = field(default_factory=dict)
    video_views: int = 0
    video_watch_time_seconds: int = 0
    clicks: int = 0
    saves: int = 0
    shares: int = 0
    fetched_at: datetime = field(default_factory=datetime.utcnow)


# Result types
@dataclass
class ValidationResult:
    """Content validation result."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    platform_adjustments: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PublishResult:
    """Post publishing result."""
    success: bool
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    error: Optional[str] = None
    platform_response: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScheduleResult:
    """Post scheduling result."""
    success: bool
    platform_schedule_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    error: Optional[str] = None
    platform_response: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MediaUploadResult:
    """Media upload result."""
    success: bool
    platform_media_id: Optional[str] = None
    media_url: Optional[str] = None
    error: Optional[str] = None
    platform_response: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplyResult:
    """Comment reply result."""
    success: bool
    platform_reply_id: Optional[str] = None
    error: Optional[str] = None
    platform_response: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WebhookRegistration:
    """Webhook registration result."""
    success: bool
    webhook_id: Optional[str] = None
    webhook_url: Optional[str] = None
    events: List[str] = field(default_factory=list)
    error: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class AuthResult:
    """Authentication result."""
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    scope: Optional[str] = None
    platform_account_id: Optional[str] = None
    account_username: Optional[str] = None
    account_name: Optional[str] = None
    error: Optional[str] = None
