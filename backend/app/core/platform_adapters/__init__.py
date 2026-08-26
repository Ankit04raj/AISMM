"""Platform Adapters Package - Unified interface for social media platforms."""

from .base import BasePlatformAdapter, PlatformCapability
from .registry import PlatformRegistry
from ..errors import (
    PlatformError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    MediaUploadError,
    PublishingError,
    TokenExpiredError,
    PlatformUnavailableError,
    NotFoundError,
    UnsupportedCapabilityError,
)

# Import and register platform adapters
from .instagram import InstagramAdapter

# Register Instagram adapter
PlatformRegistry.register("instagram", InstagramAdapter)

__all__ = [
    # Base classes
    "BasePlatformAdapter",
    "PlatformCapability",
    "PlatformRegistry",
    # Errors
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
    # Adapters
    "InstagramAdapter",
]