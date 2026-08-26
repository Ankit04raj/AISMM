"""
AISMM Platform Adapter Package

Platform-agnostic adapter architecture for social media integrations.
"""

from .base.adapter import BasePlatformAdapter
from .base.capabilities import Capability, PlatformCapabilities
from .base.models import (
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
from .base.errors import (
    PlatformError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    PublishingError,
    AnalyticsError,
    UnsupportedCapabilityError,
)
from .base.registry import PlatformRegistry

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
