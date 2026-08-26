"""Platform error hierarchy."""

from .platform_errors import (
    PlatformError,
    AuthenticationError,
    TokenExpiredError,
    RateLimitError,
    ValidationError,
    PublishingError,
    MediaUploadError,
    AnalyticsError,
    UnsupportedCapabilityError,
    PlatformUnavailableError,
    NotFoundError,
)

__all__ = [
    "PlatformError",
    "AuthenticationError",
    "TokenExpiredError",
    "RateLimitError",
    "ValidationError",
    "PublishingError",
    "MediaUploadError",
    "AnalyticsError",
    "UnsupportedCapabilityError",
    "PlatformUnavailableError",
    "NotFoundError",
]
