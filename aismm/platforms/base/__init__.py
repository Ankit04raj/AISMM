"""Base platform adapter package."""

from .adapter import BasePlatformAdapter
from .capabilities import Capability, PlatformCapabilities
from .models import (
    UniversalContent,
    PlatformSpecificPayload,
    NormalizedPost,
    NormalizedComment,
    NormalizedEngagement,
    NormalizedAccountMetrics,
    NormalizedPostAnalytics,
    MediaItem,
    ValidationResult,
    PublishResult,
    ScheduleResult,
    MediaUploadResult,
    ReplyResult,
    WebhookRegistration,
    AuthResult,
)
from .errors import (
    PlatformError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    PublishingError,
    AnalyticsError,
    UnsupportedCapabilityError,
)
from .registry import PlatformRegistry

__all__ = [
    "BasePlatformAdapter",
    "Capability",
    "PlatformCapabilities",
    "UniversalContent",
    "PlatformSpecificPayload",
    "NormalizedPost",
    "NormalizedComment",
    "NormalizedEngagement",
    "NormalizedAccountMetrics",
    "NormalizedPostAnalytics",
    "MediaItem",
    "ValidationResult",
    "PublishResult",
    "ScheduleResult",
    "MediaUploadResult",
    "ReplyResult",
    "WebhookRegistration",
    "AuthResult",
    "PlatformError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "PublishingError",
    "AnalyticsError",
    "UnsupportedCapabilityError",
    "PlatformRegistry",
]
