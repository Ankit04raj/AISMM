"""Universal content models for cross-platform normalization."""

import re
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class ContentType(str, Enum):
    """Universal content types."""
    POST = "post"
    REEL = "reel"
    STORY = "story"
    CAROUSEL = "carousel"
    IMAGE = "image"
    VIDEO = "video"


class MediaType(str, Enum):
    """Universal media types."""
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    AUDIO = "audio"
    DOCUMENT = "document"


@dataclass
class NormalizedContent:
    """Normalized platform-neutral content payload used by the AI layer."""
    text: str = ""
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    content_type: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_raw(cls, raw: Dict[str, Any]) -> "NormalizedContent":
        """Construct a normalized content object from raw platform data."""
        text = raw.get("text") or raw.get("caption") or ""
        hashtags = [h.lstrip("#") for h in re.findall(r"#([A-Za-z0-9_]+)", text)]
        mentions = [m.lstrip("@") for m in re.findall(r"@([A-Za-z0-9_]+)", text)]
        links = re.findall(r"https?://\S+", text)
        return cls(
            text=text,
            hashtags=hashtags,
            mentions=mentions,
            links=links,
            content_type=raw.get("content_type"),
            location=raw.get("location"),
            language=raw.get("language"),
            metadata={k: v for k, v in raw.items() if k not in {"text", "caption", "content_type", "location", "language"}},
        )


@dataclass
class UniversalMedia:
    """Universal media representation."""
    type: MediaType
    url: str
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    title: Optional[str] = None
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UniversalContent:
    """Universal content representation for cross-platform publishing."""
    content_type: ContentType
    text: Optional[str] = None
    caption: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    media: List[UniversalMedia] = field(default_factory=list)
    location_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    platform_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content_type": self.content_type.value,
            "text": self.text,
            "caption": self.caption,
            "hashtags": self.hashtags,
            "mentions": self.mentions,
            "media": [
                {
                    "type": m.type.value,
                    "url": m.url,
                    "thumbnail_url": m.thumbnail_url,
                    "duration_seconds": m.duration_seconds,
                    "width": m.width,
                    "height": m.height,
                    "title": m.title,
                    "caption": m.caption,
                    "alt_text": m.alt_text,
                    "file_size_bytes": m.file_size_bytes,
                    "mime_type": m.mime_type,
                    "metadata": m.metadata,
                }
                for m in self.media
            ],
            "location_id": self.location_id,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "platform_data": self.platform_data,
        }


@dataclass
class UniversalMetrics:
    """Universal metrics representation."""
    impressions: Optional[int] = None
    reach: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    video_views: Optional[int] = None
    engagement_rate: Optional[float] = None
    clicks: Optional[int] = None
    profile_visits: Optional[int] = None
    followers_gained: Optional[int] = None
    platform: Optional[str] = None
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    fetched_at: Optional[datetime] = None
    period: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "impressions": self.impressions,
            "reach": self.reach,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "saves": self.saves,
            "video_views": self.video_views,
            "engagement_rate": self.engagement_rate,
            "clicks": self.clicks,
            "profile_visits": self.profile_visits,
            "followers_gained": self.followers_gained,
            "platform": self.platform,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "period": self.period,
            "raw_data": self.raw_data,
        }


@dataclass
class UniversalAccount:
    """Universal account/profile representation."""
    platform: str
    platform_user_id: str
    username: str
    display_name: Optional[str] = None
    biography: Optional[str] = None
    website: Optional[str] = None
    profile_image_url: Optional[str] = None
    account_type: Optional[str] = None
    is_verified: Optional[bool] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    media_count: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "platform": self.platform,
            "platform_user_id": self.platform_user_id,
            "username": self.username,
            "display_name": self.display_name,
            "biography": self.biography,
            "website": self.website,
            "profile_image_url": self.profile_image_url,
            "account_type": self.account_type,
            "is_verified": self.is_verified,
            "followers_count": self.followers_count,
            "following_count": self.following_count,
            "media_count": self.media_count,
            "metadata": self.metadata,
        }