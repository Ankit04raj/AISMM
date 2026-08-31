"""Platform-specific error hierarchy."""


class PlatformError(Exception):
    """Base exception for all platform-related errors."""

    def __init__(self, message: str, platform: str = "", details: dict = None):
        self.message = message
        self.platform = platform
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.platform:
            return f"[{self.platform}] {self.message}"
        return self.message


class AuthenticationError(PlatformError):
    """Authentication/authorization failed."""

    def __init__(self, message: str, platform: str = "", details: dict = None):
        super().__init__(message, platform, details)
        self.error_code = "AUTH_FAILED"


class TokenExpiredError(AuthenticationError):
    """Access token has expired."""

    def __init__(self, platform: str = "", details: dict = None):
        super().__init__("Access token has expired", platform, details)
        self.error_code = "TOKEN_EXPIRED"


class RateLimitError(PlatformError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str,
        platform: str = "",
        details: dict = None,
        retry_after: int = None,
    ):
        super().__init__(message, platform, details)
        self.error_code = "RATE_LIMITED"
        self.retry_after = retry_after


class ValidationError(PlatformError):
    """Request validation failed."""

    def __init__(self, message: str, platform: str = "", details: dict = None):
        super().__init__(message, platform, details)
        self.error_code = "VALIDATION_FAILED"


class PublishingError(PlatformError):
    """Content publishing failed."""

    def __init__(self, message: str, platform: str = "", details: dict = None):
        super().__init__(message, platform, details)
        self.error_code = "PUBLISH_FAILED"


class MediaUploadError(PlatformError):
    """Media upload failed."""

    def __init__(self, message: str, platform: str = "", details: dict = None):
        super().__init__(message, platform, details)
        self.error_code = "MEDIA_UPLOAD_FAILED"


class AnalyticsError(PlatformError):
    """Analytics fetch failed."""

    def __init__(self, message: str, platform: str = "", details: dict = None):
        super().__init__(message, platform, details)
        self.error_code = "ANALYTICS_FAILED"


class UnsupportedCapabilityError(PlatformError):
    """Requested capability not supported by platform."""

    def __init__(self, capability: str, platform: str = "", details: dict = None):
        super().__init__(
            f"Capability '{capability}' not supported", platform, details
        )
        self.error_code = "UNSUPPORTED_CAPABILITY"
        self.capability = capability


class PlatformUnavailableError(PlatformError):
    """Platform API unavailable."""

    def __init__(self, platform: str = "", details: dict = None):
        super().__init__("Platform API temporarily unavailable", platform, details)
        self.error_code = "PLATFORM_UNAVAILABLE"


class NotFoundError(PlatformError):
    """Resource not found."""

    def __init__(self, resource: str, platform: str = "", details: dict = None):
        super().__init__(f"Resource not found: {resource}", platform, details)
        self.error_code = "NOT_FOUND"
        self.resource = resource


class WebhookError(PlatformError):
    """Webhook processing failed."""

    def __init__(self, message: str, platform: str = "", details: dict = None):
        super().__init__(message, platform, details)
        self.error_code = "WEBHOOK_FAILED"


class InsufficientPermissionsError(PlatformError):
    """Insufficient permissions for requested operation."""

    def __init__(self, message: str, platform: str = "", details: dict = None):
        super().__init__(message, platform, details)
        self.error_code = "INSUFFICIENT_PERMISSIONS"