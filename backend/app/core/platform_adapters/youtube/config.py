"""YouTube Adapter Configuration Schema."""

from typing import Optional, Dict, Any, List, ClassVar
from pydantic import BaseModel, Field, field_validator


class YouTubeAuthConfig(BaseModel):
    """YouTube / Google OAuth 2.0 configuration."""
    client_id: str = Field(..., description="Google OAuth 2.0 Client ID")
    client_secret: str = Field(..., description="Google OAuth 2.0 Client Secret")
    redirect_uri: str = Field(..., description="OAuth redirect callback URI")
    api_key: Optional[str] = Field(default=None, description="Google API Key")
    channel_id: Optional[str] = Field(default=None, description="YouTube Channel ID")
    scopes: List[str] = Field(
        default=[
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly",
            "https://www.googleapis.com/auth/youtube.force-ssl",
            "https://www.googleapis.com/auth/yt-analytics.readonly",
        ],
        description="OAuth 2.0 scopes",
    )


class YouTubeRateLimitConfig(BaseModel):
    """YouTube API quota configuration (default: 10,000 quota units/day)."""
    quota_units_per_day: int = Field(default=10000, ge=1000, le=1000000)
    video_uploads_per_day: int = Field(default=6, ge=1, le=50)


class YouTubeMediaConfig(BaseModel):
    """Media upload limits for YouTube."""
    max_video_size_mb: int = Field(default=256000, ge=100, le=512000)  # Up to 256 GB
    max_thumbnail_size_mb: int = Field(default=2, ge=1, le=10)
    supported_video_formats: List[str] = Field(default=["mp4", "mov", "avi", "wmv", "flv", "mkv", "webm"])


class YouTubeConfig(BaseModel):
    """Complete YouTube adapter configuration."""

    auth: YouTubeAuthConfig
    rate_limits: YouTubeRateLimitConfig = Field(default_factory=YouTubeRateLimitConfig)
    media: YouTubeMediaConfig = Field(default_factory=YouTubeMediaConfig)

    enable_insights: bool = Field(default=True)
    enable_webhooks: bool = Field(default=False)

    request_timeout_seconds: int = Field(default=30, ge=5, le=300)
    upload_timeout_seconds: int = Field(default=600, ge=60, le=7200)
    max_retries: int = Field(default=3, ge=0, le=10)

    presets: ClassVar = None

    @field_validator("auth")
    @classmethod
    def validate_auth(cls, v: YouTubeAuthConfig) -> YouTubeAuthConfig:
        if not v.client_id or not v.client_secret:
            raise ValueError("client_id and client_secret are required for YouTube")
        return v

    def to_adapter_config(self) -> Dict[str, Any]:
        return {
            "client_id": self.auth.client_id,
            "client_secret": self.auth.client_secret,
            "redirect_uri": self.auth.redirect_uri,
            "api_key": self.auth.api_key,
            "channel_id": self.auth.channel_id,
            "scopes": self.auth.scopes,
            "rate_limit_calls": self.rate_limits.quota_units_per_day,
            "rate_limit_window": 86400,
            "enable_insights": self.enable_insights,
            "enable_webhooks": self.enable_webhooks,
            "request_timeout": self.request_timeout_seconds,
            "upload_timeout": self.upload_timeout_seconds,
            "max_retries": self.max_retries,
        }


class YouTubeConfigPresets:
    """Pre-built configurations for YouTube environments."""

    @staticmethod
    def development() -> YouTubeConfig:
        return YouTubeConfig(
            auth=YouTubeAuthConfig(
                client_id="dev_yt_client_id",
                client_secret="dev_yt_client_secret",
                redirect_uri="http://localhost:8000/api/v1/auth/youtube/callback",
            ),
            request_timeout_seconds=60,
        )

    @staticmethod
    def production() -> YouTubeConfig:
        return YouTubeConfig(
            auth=YouTubeAuthConfig(
                client_id="prod_yt_client_id",
                client_secret="prod_yt_client_secret",
                redirect_uri="https://api.aismm.com/api/v1/auth/youtube/callback",
            ),
            request_timeout_seconds=30,
        )


YouTubeConfig.presets = YouTubeConfigPresets
