"""
Platform Capabilities System

Defines the capability-based platform system where each platform
declares what it supports dynamically.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


class Capability(str, Enum):
    """All possible platform capabilities."""
    PUBLISHING = "publishing"
    SCHEDULING = "scheduling"
    TEXT_POST = "text_post"
    IMAGE_POST = "image_post"
    VIDEO_POST = "video_post"
    CAROUSEL_POST = "carousel_post"
    STORIES = "stories"
    SHORT_VIDEO = "short_video"
    COMMENTS = "comments"
    REPLIES = "replies"
    ANALYTICS = "analytics"
    AUDIENCE_METRICS = "audience_metrics"
    WEBHOOKS = "webhooks"
    DIRECT_MESSAGES = "direct_messages"
    HASHTAGS = "hashtags"
    MENTIONS = "mentions"


@dataclass
class PlatformLimits:
    """Platform-specific content limits."""
    text_length: int = 280
    hashtag_count: int = 30
    media_count: int = 4
    video_duration_seconds: int = 140
    carousel_cards: int = 10


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_window: int = 100
    window_seconds: int = 60
    burst: int = 10
    backoff_base: float = 1.0
    backoff_max: float = 60.0
    max_retries: int = 5


@dataclass
class PlatformCapabilities:
    """
    Immutable capability set for a platform.
    Loaded from configuration, not hardcoded.
    """
    platform_id: str
    capabilities: Dict[Capability, bool] = field(default_factory=dict)
    limits: PlatformLimits = field(default_factory=PlatformLimits)
    rate_limits: RateLimitConfig = field(default_factory=RateLimitConfig)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def supports(self, capability: str) -> bool:
        """Check if platform supports a capability."""
        try:
            cap = Capability(capability)
            return self.capabilities.get(cap, False)
        except ValueError:
            return False
    
    def get_supported(self) -> List[str]:
        """Get list of supported capability names."""
        return [cap.value for cap, enabled in self.capabilities.items() if enabled]
    
    def get_limit(self, limit_name: str) -> Optional[int]:
        """Get a platform limit."""
        return getattr(self.limits, limit_name, None)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "platform_id": self.platform_id,
            "capabilities": {cap.value: enabled for cap, enabled in self.capabilities.items()},
            "limits": {
                "text_length": self.limits.text_length,
                "hashtag_count": self.limits.hashtag_count,
                "media_count": self.limits.media_count,
                "video_duration_seconds": self.limits.video_duration_seconds,
                "carousel_cards": self.limits.carousel_cards,
            },
            "rate_limits": {
                "requests_per_window": self.rate_limits.requests_per_window,
                "window_seconds": self.rate_limits.window_seconds,
                "burst": self.rate_limits.burst,
            },
        }
