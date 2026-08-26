"""AISMM Core Exceptions."""

from typing import Optional, Dict, Any


class AISMMError(Exception):
    """Base exception for AISMM errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "AISMM_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AISMMError):
    """Resource not found."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class ValidationError(AISMMError):
    """Validation error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class AuthenticationError(AISMMError):
    """Authentication error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details,
        )


class AuthorizationError(AISMMError):
    """Authorization error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details,
        )


class PlatformError(AISMMError):
    """Platform API error."""

    def __init__(
        self,
        message: str,
        platform: str,
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="PLATFORM_ERROR",
            status_code=status_code,
            details={**(details or {}), "platform": platform},
        )
        self.platform = platform


class RateLimitError(PlatformError):
    """Rate limit exceeded."""

    def __init__(self, message: str, platform: str, retry_after: Optional[int] = None):
        super().__init__(
            message=message,
            platform=platform,
            status_code=429,
            details={"retry_after": retry_after} if retry_after else {},
        )


class TokenExpiredError(AuthenticationError):
    """Access token expired."""

    def __init__(self, message: str = "Access token expired", platform: str = ""):
        super().__init__(
            message=message,
            details={"platform": platform} if platform else {},
        )


class InsufficientPermissionsError(PlatformError):
    """Insufficient permissions for operation."""

    def __init__(self, message: str, platform: str, required_permissions: Optional[list] = None):
        super().__init__(
            message=message,
            platform=platform,
            status_code=403,
            details={"required_permissions": required_permissions or []},
        )


class MediaUploadError(PlatformError):
    """Media upload failed."""

    def __init__(self, message: str, platform: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            platform=platform,
            status_code=400,
            details=details,
        )


class PublishingError(PlatformError):
    """Post publishing failed."""

    def __init__(self, message: str, platform: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            platform=platform,
            status_code=400,
            details=details,
        )


class SchedulingError(PlatformError):
    """Post scheduling failed."""

    def __init__(self, message: str, platform: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            platform=platform,
            status_code=400,
            details=details,
        )


class WebhookError(AISMMError):
    """Webhook processing error."""

    def __init__(self, message: str, platform: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="WEBHOOK_ERROR",
            status_code=400,
            details={**(details or {}), "platform": platform},
        )


class PlatformUnavailableError(PlatformError):
    """Platform API unavailable."""

    def __init__(self, platform: str, message: Optional[str] = None):
        super().__init__(
            message=message or f"Platform {platform} is currently unavailable",
            platform=platform,
            status_code=503,
        )


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