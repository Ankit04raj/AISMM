"""
Platform Error Hierarchy

Normalized error types that all platform adapters translate to.
This ensures the core application never deals with platform-specific errors.
"""

from typing import Optional, Dict, Any


class PlatformError(Exception):
    """Base exception for all platform-related errors."""
    
    def __init__(self, message: str, platform: str = "", 
                 original_error: Optional[Exception] = None,
                 error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.platform = platform
        self.original_error = original_error
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        return f"[{self.platform}] {self.message}"


class AuthenticationError(PlatformError):
    """Authentication/authorization failures."""
    
    def __init__(self, message: str = "Authentication failed", platform: str = "",
                 original_error: Optional[Exception] = None, **kwargs):
        super().__init__(message, platform, original_error, error_code="AUTH_FAILED", **kwargs)


class TokenExpiredError(AuthenticationError):
    """Access token has expired."""
    
    def __init__(self, platform: str = "", original_error: Optional[Exception] = None):
        super().__init__("Access token expired", platform, original_error, error_code="TOKEN_EXPIRED")


class TokenInvalidError(AuthenticationError):
    """Access token is invalid or revoked."""
    
    def __init__(self, platform: str = "", original_error: Optional[Exception] = None):
        super().__init__("Access token invalid or revoked", platform, original_error, error_code="TOKEN_INVALID")


class InsufficientScopeError(AuthenticationError):
    """Token doesn't have required scopes."""
    
    def __init__(self, required_scopes: list, platform: str = "", 
                 original_error: Optional[Exception] = None):
        super().__init__(
            f"Insufficient scopes: {', '.join(required_scopes)}", 
            platform, original_error, error_code="INSUFFICIENT_SCOPE",
            details={"required_scopes": required_scopes}
        )


class RateLimitError(PlatformError):
    """Rate limit exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", platform: str = "",
                 original_error: Optional[Exception] = None,
                 retry_after: Optional[int] = None,
                 limit: Optional[int] = None,
                 window: Optional[int] = None):
        super().__init__(message, platform, original_error, error_code="RATE_LIMITED",
                        details={"retry_after": retry_after, "limit": limit, "window": window})
        self.retry_after = retry_after


class ValidationError(PlatformError):
    """Content validation failed."""
    
    def __init__(self, message: str = "Content validation failed", platform: str = "",
                 original_error: Optional[Exception] = None,
                 field_errors: Optional[Dict[str, str]] = None):
        super().__init__(message, platform, original_error, error_code="VALIDATION_ERROR",
                        details={"field_errors": field_errors or {}})
        self.field_errors = field_errors or {}


class PublishingError(PlatformError):
    """Post publishing failed."""
    
    def __init__(self, message: str = "Publishing failed", platform: str = "",
                 original_error: Optional[Exception] = None,
                 platform_response: Optional[Dict[str, Any]] = None):
        super().__init__(message, platform, original_error, error_code="PUBLISHING_FAILED",
                        details={"platform_response": platform_response or {}})


class SchedulingError(PlatformError):
    """Post scheduling failed."""
    
    def __init__(self, message: str = "Scheduling failed", platform: str = "",
                 original_error: Optional[Exception] = None,
                 platform_response: Optional[Dict[str, Any]] = None):
        super().__init__(message, platform, original_error, error_code="SCHEDULING_FAILED",
                        details={"platform_response": platform_response or {}})


class MediaUploadError(PlatformError):
    """Media upload failed."""
    
    def __init__(self, message: str = "Media upload failed", platform: str = "",
                 original_error: Optional[Exception] = None,
                 platform_response: Optional[Dict[str, Any]] = None,
                 media_type: Optional[str] = None):
        super().__init__(message, platform, original_error, error_code="MEDIA_UPLOAD_FAILED",
                        details={"platform_response": platform_response or {}, "media_type": media_type})


class AnalyticsError(PlatformError):
    """Analytics fetching failed."""
    
    def __init__(self, message: str = "Analytics fetch failed", platform: str = "",
                 original_error: Optional[Exception] = None):
        super().__init__(message, platform, original_error, error_code="ANALYTICS_FAILED")


class CommentsError(PlatformError):
    """Comment fetching/replying failed."""
    
    def __init__(self, message: str = "Comments operation failed", platform: str = "",
                 original_error: Optional[Exception] = None):
        super().__init__(message, platform, original_error, error_code="COMMENTS_FAILED")


class WebhookError(PlatformError):
    """Webhook registration/handling failed."""
    
    def __init__(self, message: str = "Webhook error", platform: str = "",
                 original_error: Optional[Exception] = None):
        super().__init__(message, platform, original_error, error_code="WEBHOOK_ERROR")


class UnsupportedCapabilityError(PlatformError):
    """Requested capability not supported by platform."""
    
    def __init__(self, capability: str, platform: str = "",
                 original_error: Optional[Exception] = None):
        super().__init__(
            f"Capability '{capability}' not supported by {platform or 'platform'}",
            platform, original_error, error_code="UNSUPPORTED_CAPABILITY",
            details={"capability": capability}
        )


class PlatformUnavailableError(PlatformError):
    """Platform API is unavailable."""
    
    def __init__(self, message: str = "Platform unavailable", platform: str = "",
                 original_error: Optional[Exception] = None,
                 status_code: Optional[int] = None):
        super().__init__(message, platform, original_error, error_code="PLATFORM_UNAVAILABLE",
                        details={"status_code": status_code})


class NetworkError(PlatformError):
    """Network connectivity issue."""
    
    def __init__(self, message: str = "Network error", platform: str = "",
                 original_error: Optional[Exception] = None):
        super().__init__(message, platform, original_error, error_code="NETWORK_ERROR")


class ConfigurationError(PlatformError):
    """Platform configuration issue."""
    
    def __init__(self, message: str = "Configuration error", platform: str = "",
                 original_error: Optional[Exception] = None):
        super().__init__(message, platform, original_error, error_code="CONFIG_ERROR")


# Error translation utilities
ERROR_CODE_MAP = {
    # Instagram/Facebook Graph API
    190: TokenExpiredError,
    102: TokenInvalidError,
    4: RateLimitError,
    100: ValidationError,
    200: PublishingError,
    32: PublishingError,  # Media upload error
    
    # X (Twitter) API v2
    32: TokenInvalidError,
    88: RateLimitError,
    187: PublishingError,  # Duplicate post
    327: ValidationError,  # Text too long
    403: AuthenticationError,
    
    # LinkedIn
    401: TokenInvalidError,
    429: RateLimitError,
    
    # YouTube
    401: TokenInvalidError,
    403: AuthenticationError,
    429: RateLimitError,
    400: ValidationError,
}


def translate_error(platform: str, error_data: Dict[str, Any], 
                    status_code: Optional[int] = None) -> PlatformError:
    """
    Translate platform-specific error to normalized AISMM error.
    
    Args:
        platform: Platform identifier
        error_data: Raw error response from platform
        status_code: HTTP status code if available
    
    Returns:
        Normalized PlatformError subclass
    """
    # Try to extract error code
    error_code = None
    message = "Unknown error"
    
    if isinstance(error_data, dict):
        # Instagram/Facebook format
        if "error" in error_data:
            err = error_data["error"]
            if isinstance(err, dict):
                error_code = err.get("code")
                message = err.get("message", message)
        # X format
        elif "errors" in error_data:
            errors = error_data["errors"]
            if errors and isinstance(errors[0], dict):
                error_code = errors[0].get("code")
                message = errors[0].get("message", message)
        # LinkedIn format
        elif "message" in error_data:
            message = error_data["message"]
            error_code = error_data.get("status")
        # YouTube format
        elif "error" in error_data:
            err = error_data["error"]
            if isinstance(err, dict):
                message = err.get("message", message)
                error_code = err.get("code")
    
    # Map known error codes
    if error_code and error_code in ERROR_CODE_MAP:
        error_class = ERROR_CODE_MAP[error_code]
        return error_class(message, platform=platform)
    
    # Map by HTTP status
    if status_code:
        if status_code == 401:
            return TokenInvalidError(message, platform=platform)
        elif status_code == 403:
            return AuthenticationError(message, platform=platform)
        elif status_code == 429:
            return RateLimitError(message, platform=platform)
        elif status_code >= 500:
            return PlatformUnavailableError(message, platform=platform, status_code=status_code)
        elif status_code == 400:
            return ValidationError(message, platform=platform)
    
    return PlatformError(message, platform=platform)
