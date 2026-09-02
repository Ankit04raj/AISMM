"""LinkedIn Adapter Configuration Schema."""

from typing import Optional, Dict, Any, List, ClassVar
from pydantic import BaseModel, Field, field_validator


class LinkedInAuthConfig(BaseModel):
    """LinkedIn OAuth 2.0 configuration."""
    client_id: str = Field(..., description="LinkedIn App Client ID")
    client_secret: str = Field(..., description="LinkedIn App Client Secret")
    redirect_uri: str = Field(..., description="OAuth redirect callback URI")
    organization_urn: Optional[str] = Field(default=None, description="URN of target organization (e.g. urn:li:organization:123456)")
    scopes: List[str] = Field(
        default=[
            "openid",
            "profile",
            "email",
            "w_member_social",
            "r_organization_social",
            "w_organization_social",
            "r_organization_admin",
            "rw_organization_admin",
        ],
        description="OAuth 2.0 scopes",
    )


class LinkedInRateLimitConfig(BaseModel):
    """LinkedIn API rate limit configuration."""
    shares_per_day: int = Field(default=250, ge=1, le=1000)
    calls_per_day: int = Field(default=10000, ge=100, le=100000)


class LinkedInMediaConfig(BaseModel):
    """Media upload limits for LinkedIn."""
    max_image_size_mb: int = Field(default=8, ge=1, le=20)
    max_video_size_mb: int = Field(default=500, ge=10, le=2000)
    max_document_size_mb: int = Field(default=100, ge=5, le=300)
    supported_image_formats: List[str] = Field(default=["jpg", "jpeg", "png", "gif"])
    supported_video_formats: List[str] = Field(default=["mp4", "mov"])


class LinkedInConfig(BaseModel):
    """Complete LinkedIn adapter configuration."""

    auth: LinkedInAuthConfig
    rate_limits: LinkedInRateLimitConfig = Field(default_factory=LinkedInRateLimitConfig)
    media: LinkedInMediaConfig = Field(default_factory=LinkedInMediaConfig)

    enable_insights: bool = Field(default=True)
    enable_webhooks: bool = Field(default=False)

    request_timeout_seconds: int = Field(default=30, ge=5, le=300)
    upload_timeout_seconds: int = Field(default=300, ge=30, le=3600)
    max_retries: int = Field(default=3, ge=0, le=10)

    presets: ClassVar = None

    @field_validator("auth")
    @classmethod
    def validate_auth(cls, v: LinkedInAuthConfig) -> LinkedInAuthConfig:
        if not v.client_id or not v.client_secret:
            raise ValueError("client_id and client_secret are required for LinkedIn")
        return v

    def to_adapter_config(self) -> Dict[str, Any]:
        return {
            "client_id": self.auth.client_id,
            "client_secret": self.auth.client_secret,
            "redirect_uri": self.auth.redirect_uri,
            "organization_urn": self.auth.organization_urn,
            "scopes": self.auth.scopes,
            "rate_limit_calls": self.rate_limits.shares_per_day,
            "rate_limit_window": 86400,
            "enable_insights": self.enable_insights,
            "enable_webhooks": self.enable_webhooks,
            "request_timeout": self.request_timeout_seconds,
            "upload_timeout": self.upload_timeout_seconds,
            "max_retries": self.max_retries,
        }


class LinkedInConfigPresets:
    """Pre-built configurations for LinkedIn environments."""

    @staticmethod
    def development() -> LinkedInConfig:
        return LinkedInConfig(
            auth=LinkedInAuthConfig(
                client_id="dev_li_client_id",
                client_secret="dev_li_client_secret",
                redirect_uri="http://localhost:8000/api/v1/auth/linkedin/callback",
            ),
            rate_limits=LinkedInRateLimitConfig(shares_per_day=50),
            request_timeout_seconds=60,
        )

    @staticmethod
    def production() -> LinkedInConfig:
        return LinkedInConfig(
            auth=LinkedInAuthConfig(
                client_id="prod_li_client_id",
                client_secret="prod_li_client_secret",
                redirect_uri="https://api.aismm.com/api/v1/auth/linkedin/callback",
            ),
            rate_limits=LinkedInRateLimitConfig(shares_per_day=250),
            request_timeout_seconds=30,
        )


LinkedInConfig.presets = LinkedInConfigPresets
