"""AISMM Error hierarchy."""

from typing import Optional, Dict, Any


class AISMMError(Exception):
    """Base exception for all AISMM errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "AISMM_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class NotFoundError(AISMMError):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", platform: str = "", details: Optional[Dict[str, Any]] = None):
        msg = f"Resource not found: {resource}" if not resource.startswith("Resource not found") else resource
        d = dict(details or {})
        if platform:
            d["platform"] = platform
        super().__init__(
            message=msg,
            error_code="NOT_FOUND",
            status_code=404,
            details=d,
        )
        self.resource = resource
        self.platform = platform


class ValidationError(AISMMError):
    """Validation failed."""

    def __init__(self, message: str, platform: str = "", details: Optional[Dict[str, Any]] = None):
        d = dict(details or {})
        if platform:
            d["platform"] = platform
        super().__init__(
            message=message,
            error_code="VALIDATION_FAILED",
            status_code=422,
            details=d,
        )
        self.platform = platform


class AuthenticationError(AISMMError):
    """Authentication/authorization failed."""

    def __init__(self, message: str = "Authentication failed", platform: str = "", status_code: int = 401, details: Optional[Dict[str, Any]] = None):
        d = dict(details or {})
        if platform:
            d["platform"] = platform
        super().__init__(
            message=message,
            error_code="AUTH_FAILED",
            status_code=status_code,
            details=d,
        )
        self.platform = platform


class AuthorizationError(AISMMError):
    """Authorization failed."""

    def __init__(self, message: str = "Permission denied", platform: str = "", details: Optional[Dict[str, Any]] = None):
        d = dict(details or {})
        if platform:
            d["platform"] = platform
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=d,
        )
        self.platform = platform


class PlatformError(AISMMError):
    """Base exception for platform-specific errors."""

    def __init__(
        self,
        message: str,
        platform: str = "",
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None,
    ):
        d = dict(details or {})
        if platform:
            d["platform"] = platform
        super().__init__(
            message=message,
            error_code="PLATFORM_ERROR",
            status_code=status_code,
            details=d,
        )
        self.platform = platform

    def __str__(self) -> str:
        if self.platform:
            return f"[{self.platform}] {self.message}"
        return self.message


class TokenExpiredError(AuthenticationError):
    """Access token has expired."""

    def __init__(self, message: str = "Access token has expired", platform: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, platform=platform, status_code=401, details=details)
        self.error_code = "TOKEN_EXPIRED"


class RateLimitError(PlatformError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str,
        platform: str = "",
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None,
    ):
        d = dict(details or {})
        if retry_after is not None:
            d["retry_after"] = retry_after
        super().__init__(message=message, platform=platform, status_code=429, details=d)
        self.error_code = "RATE_LIMITED"
        self.retry_after = retry_after


class PublishingError(PlatformError):
    """Content publishing failed."""

    def __init__(self, message: str, platform: str = "", status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, platform=platform, status_code=status_code, details=details)
        self.error_code = "PUBLISH_FAILED"


class MediaUploadError(PlatformError):
    """Media upload failed."""

    def __init__(self, message: str, platform: str = "", status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, platform=platform, status_code=status_code, details=details)
        self.error_code = "MEDIA_UPLOAD_FAILED"


class SchedulingError(PlatformError):
    """Post scheduling failed."""

    def __init__(self, message: str, platform: str = "", status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, platform=platform, status_code=status_code, details=details)
        self.error_code = "SCHEDULING_FAILED"


class AnalyticsError(PlatformError):
    """Analytics fetch failed."""

    def __init__(self, message: str, platform: str = "", status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, platform=platform, status_code=status_code, details=details)
        self.error_code = "ANALYTICS_FAILED"


class UnsupportedCapabilityError(PlatformError):
    """Requested capability not supported by platform."""

    def __init__(self, capability: str, platform: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Capability '{capability}' not supported",
            platform=platform,
            status_code=400,
            details=details,
        )
        self.error_code = "UNSUPPORTED_CAPABILITY"
        self.capability = capability


class PlatformUnavailableError(PlatformError):
    """Platform API unavailable."""

    def __init__(self, platform: str = "", message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message or f"Platform {platform} is currently unavailable",
            platform=platform,
            status_code=503,
            details=details,
        )
        self.error_code = "PLATFORM_UNAVAILABLE"


class WebhookError(PlatformError):
    """Webhook processing failed."""

    def __init__(self, message: str, platform: str = "", status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, platform=platform, status_code=status_code, details=details)
        self.error_code = "WEBHOOK_FAILED"


class InsufficientPermissionsError(PlatformError):
    """Insufficient permissions for requested operation."""

    def __init__(
        self,
        message: str,
        platform: str = "",
        required_permissions: Optional[list] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        d = dict(details or {})
        if required_permissions:
            d["required_permissions"] = required_permissions
        super().__init__(message=message, platform=platform, status_code=403, details=d)
        self.error_code = "INSUFFICIENT_PERMISSIONS"


class ConfigurationError(AISMMError):
    """Configuration error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=500,
            details=details,
        )


class DatabaseError(AISMMError):
    """Database error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details,
        )
