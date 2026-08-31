"""Platform adapter specific errors."""

from backend.app.core.errors import (
    PlatformError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    MediaUploadError,
    PublishingError,
    WebhookError,
    TokenExpiredError,
    InsufficientPermissionsError,
    PlatformUnavailableError,
    NotFoundError,
    UnsupportedCapabilityError,
)

__all__ = [
    "PlatformError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "MediaUploadError",
    "PublishingError",
    "WebhookError",
    "TokenExpiredError",
    "InsufficientPermissionsError",
    "PlatformUnavailableError",
    "NotFoundError",
    "UnsupportedCapabilityError",
]