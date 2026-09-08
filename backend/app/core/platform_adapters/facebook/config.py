"""Facebook Adapter Configuration Schema."""

from typing import Optional, Dict, Any, List, ClassVar
from pydantic import BaseModel, Field, field_validator


class FacebookAuthConfig(BaseModel):
    """Facebook OAuth configuration."""
    client_id: str = Field(..., description="Facebook App ID")
    client_secret: str = Field(..., description="Facebook App Secret")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    scopes: List[str] = Field(
        default=[
            "pages_show_list",
            "pages_read_engagement",
            "pages_manage_posts",
            "pages_manage_engagement",
            "read_insights",
        ],
        description="OAuth scopes",
    )


class FacebookRateLimitConfig(BaseModel):
    """Facebook rate limit configuration (Business use case)."""
    calls_per_hour: int = Field(default=200, ge=1, le=1000)
    calls_per_day: int = Field(default=4800, ge=1, le=50000)


class FacebookMediaConfig(BaseModel):
    """Media upload limits for Facebook."""
    max_image_size_mb: int = Field(default=10, ge=1, le=50)
    max_video_size_mb: int = Field(default=1000, ge=10, le=10000)
    supported_image_formats: List[str] = Field(default=["jpg", "jpeg", "png", "gif", "webp"])
    supported_video_formats: List[str] = Field(default=["mp4", "mov", "avi"])


class FacebookConfig(BaseModel):
    """Complete Facebook adapter configuration."""

    auth: FacebookAuthConfig
    rate_limits: FacebookRateLimitConfig = Field(default_factory=FacebookRateLimitConfig)
    media: FacebookMediaConfig = Field(default_factory=FacebookMediaConfig)

    enable_scheduling: bool = Field(default=True)
    enable_insights: bool = Field(default=True)
    enable_webhooks: bool = Field(default=False)

    request_timeout_seconds: int = Field(default=30, ge=5, le=300)
    upload_timeout_seconds: int = Field(default=300, ge=30, le=3600)
    max_retries: int = Field(default=3, ge=0, le=10)

    presets: ClassVar = None

    @field_validator("auth")
    @classmethod
    def validate_auth(cls, v: FacebookAuthConfig) -> FacebookAuthConfig:
        if not v.client_id or not v.client_secret:
            raise ValueError("client_id and client_secret are required")
        return v

    def to_adapter_config(self) -> Dict[str, Any]:
        return {
            "client_id": self.auth.client_id,
            "client_secret": self.auth.client_secret,
            "redirect_uri": self.auth.redirect_uri,
            "scopes": self.auth.scopes,
            "rate_limit_calls": self.rate_limits.calls_per_hour,
            "rate_limit_window": 3600,
            "enable_scheduling": self.enable_scheduling,
            "enable_insights": self.enable_insights,
            "enable_webhooks": self.enable_webhooks,
            "request_timeout": self.request_timeout_seconds,
            "upload_timeout": self.upload_timeout_seconds,
            "max_retries": self.max_retries,
        }


class FacebookConfigPresets:
    """Pre-built configurations for Facebook environments."""

    @staticmethod
    def development() -> FacebookConfig:
        return FacebookConfig(
            auth=FacebookAuthConfig(
                client_id="dev_fb_client_id",
                client_secret="dev_fb_client_secret",
                redirect_uri="http://localhost:8000/api/v1/auth/facebook/callback",
            ),
            rate_limits=FacebookRateLimitConfig(calls_per_hour=50),
            request_timeout_seconds=60,
        )

    @staticmethod
    def production() -> FacebookConfig:
        return FacebookConfig(
            auth=FacebookAuthConfig(
                client_id="prod_fb_client_id",
                client_secret="prod_fb_client_secret",
                redirect_uri="https://api.aismm.com/api/v1/auth/facebook/callback",
            ),
            rate_limits=FacebookRateLimitConfig(calls_per_hour=200),
            request_timeout_seconds=30,
        )


FacebookConfig.presets = FacebookConfigPresets
