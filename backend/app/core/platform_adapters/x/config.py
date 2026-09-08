"""X (Twitter) Adapter Configuration Schema."""

from typing import Optional, Dict, Any, List, ClassVar
from pydantic import BaseModel, Field, field_validator


class XAuthConfig(BaseModel):
    """X OAuth 2.0 PKCE / User context configuration."""
    client_id: str = Field(..., description="X OAuth 2.0 Client ID")
    client_secret: Optional[str] = Field(default=None, description="X OAuth 2.0 Client Secret (confidential clients)")
    redirect_uri: str = Field(..., description="OAuth redirect callback URI")
    api_key: Optional[str] = Field(default=None, description="Twitter API Consumer Key (v1.1 media upload)")
    api_secret: Optional[str] = Field(default=None, description="Twitter API Consumer Secret")
    bearer_token: Optional[str] = Field(default=None, description="App-only Bearer Token")
    scopes: List[str] = Field(
        default=[
            "tweet.read",
            "tweet.write",
            "users.read",
            "offline.access",
            "like.read",
            "like.write",
        ],
        description="OAuth 2.0 scopes",
    )


class XRateLimitConfig(BaseModel):
    """X API v2 rate limit configuration."""
    tweets_per_15min: int = Field(default=50, ge=1, le=300)
    user_timeline_per_15min: int = Field(default=900, ge=10, le=1500)
    mentions_per_15min: int = Field(default=180, ge=5, le=500)


class XMediaConfig(BaseModel):
    """Media upload limits for X."""
    max_image_size_mb: int = Field(default=5, ge=1, le=15)
    max_video_size_mb: int = Field(default=512, ge=10, le=1024)
    max_video_duration_seconds: int = Field(default=140, ge=10, le=600)
    supported_image_formats: List[str] = Field(default=["jpg", "jpeg", "png", "gif", "webp"])
    supported_video_formats: List[str] = Field(default=["mp4", "mov"])


class XConfig(BaseModel):
    """Complete X (Twitter) adapter configuration."""

    auth: XAuthConfig
    rate_limits: XRateLimitConfig = Field(default_factory=XRateLimitConfig)
    media: XMediaConfig = Field(default_factory=XMediaConfig)

    enable_insights: bool = Field(default=True)
    enable_webhooks: bool = Field(default=False)

    request_timeout_seconds: int = Field(default=30, ge=5, le=300)
    upload_timeout_seconds: int = Field(default=180, ge=30, le=1800)
    max_retries: int = Field(default=3, ge=0, le=10)

    presets: ClassVar = None

    @field_validator("auth")
    @classmethod
    def validate_auth(cls, v: XAuthConfig) -> XAuthConfig:
        if not v.client_id:
            raise ValueError("client_id is required for X adapter")
        return v

    def to_adapter_config(self) -> Dict[str, Any]:
        return {
            "client_id": self.auth.client_id,
            "client_secret": self.auth.client_secret,
            "redirect_uri": self.auth.redirect_uri,
            "api_key": self.auth.api_key,
            "api_secret": self.auth.api_secret,
            "bearer_token": self.auth.bearer_token,
            "scopes": self.auth.scopes,
            "rate_limit_calls": self.rate_limits.tweets_per_15min,
            "rate_limit_window": 900,
            "enable_insights": self.enable_insights,
            "enable_webhooks": self.enable_webhooks,
            "request_timeout": self.request_timeout_seconds,
            "upload_timeout": self.upload_timeout_seconds,
            "max_retries": self.max_retries,
        }


class XConfigPresets:
    """Pre-built configurations for X environments."""

    @staticmethod
    def development() -> XConfig:
        return XConfig(
            auth=XAuthConfig(
                client_id="dev_x_client_id",
                client_secret="dev_x_client_secret",
                redirect_uri="http://localhost:8000/api/v1/auth/x/callback",
            ),
            rate_limits=XRateLimitConfig(tweets_per_15min=25),
            request_timeout_seconds=60,
        )

    @staticmethod
    def production() -> XConfig:
        return XConfig(
            auth=XAuthConfig(
                client_id="prod_x_client_id",
                client_secret="prod_x_client_secret",
                redirect_uri="https://api.aismm.com/api/v1/auth/x/callback",
            ),
            rate_limits=XRateLimitConfig(tweets_per_15min=50),
            request_timeout_seconds=30,
        )


XConfig.presets = XConfigPresets
