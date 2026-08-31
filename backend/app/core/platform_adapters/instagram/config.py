"""Instagram Adapter Configuration Schema."""

from typing import Optional, Dict, Any, List, ClassVar
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator


class InstagramAuthConfig(BaseModel):
    """Instagram OAuth configuration."""
    client_id: str = Field(..., description="Instagram App Client ID")
    client_secret: str = Field(..., description="Instagram App Client Secret")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    scopes: List[str] = Field(
        default=[
            "instagram_graph_user_profile",
            "instagram_graph_user_media",
            "instagram_manage_comments",
            "instagram_manage_insights",
            "pages_show_list",
            "pages_read_engagement",
        ],
        description="OAuth scopes"
    )


class InstagramRateLimitConfig(BaseModel):
    """Rate limit configuration."""
    calls_per_hour: int = Field(default=200, ge=1, le=1000)
    calls_per_day: int = Field(default=4800, ge=1, le=50000)
    burst_limit: int = Field(default=50, ge=1, le=200)


class InstagramMediaConfig(BaseModel):
    """Media upload configuration."""
    max_image_size_mb: int = Field(default=8, ge=1, le=100)
    max_video_size_mb: int = Field(default=100, ge=1, le=4000)
    max_carousel_items: int = Field(default=10, ge=2, le=10)
    supported_image_formats: List[str] = Field(default=["jpg", "jpeg", "png", "gif", "webp"])
    supported_video_formats: List[str] = Field(default=["mp4", "mov", "avi", "mkv"])
    chunk_size_mb: int = Field(default=4, ge=1, le=100)
    resumable_threshold_mb: int = Field(default=100, ge=10, le=1000)


class InstagramWebhookConfig(BaseModel):
    """Webhook configuration."""
    verify_token: str = Field(..., description="Webhook verification token")
    callback_url: str = Field(..., description="Webhook callback URL")
    fields: List[str] = Field(
        default=[
            "comments",
            "mentions",
            "story_replies",
        ],
        description="Subscribed webhook fields"
    )
    app_secret: str = Field(..., description="Instagram App Secret for signature verification")


class InstagramConfig(BaseModel):
    """Complete Instagram adapter configuration."""

    # Auth
    auth: InstagramAuthConfig

    # Rate limits
    rate_limits: InstagramRateLimitConfig = Field(default_factory=InstagramRateLimitConfig)

    # Media
    media: InstagramMediaConfig = Field(default_factory=InstagramMediaConfig)

    # Feature flags
    enable_scheduling: bool = Field(default=True)
    enable_insights: bool = Field(default=True)
    enable_webhooks: bool = Field(default=False)

    # Webhooks
    webhook: Optional[InstagramWebhookConfig] = None
    enable_carousel: bool = Field(default=True)
    enable_reels: bool = Field(default=True)
    enable_stories: bool = Field(default=True)

    # Timeouts
    request_timeout_seconds: int = Field(default=30, ge=5, le=300)
    upload_timeout_seconds: int = Field(default=300, ge=30, le=3600)

    # Retry
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_backoff_factor: float = Field(default=1.5, ge=0.5, le=5.0)

    # Cache
    cache_ttl_seconds: int = Field(default=300, ge=60, le=3600)


    presets: ClassVar = None  # Set after InstagramConfigPresets is defined

    @validator("auth")
    def validate_auth(cls, v):
        if not v.client_id or not v.client_secret:
            raise ValueError("client_id and client_secret are required")
        return v

    @validator("webhook")
    def validate_webhook(cls, v, values):
        if values.get("enable_webhooks", False):
            if v is None or not v.verify_token or not v.callback_url or not v.app_secret:
                raise ValueError("Webhook config requires verify_token, callback_url, and app_secret")
        return v

    def to_adapter_config(self) -> Dict[str, Any]:
        """Convert to adapter config dict."""
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
            "retry_backoff_factor": self.retry_backoff_factor,
            "cache_ttl": self.cache_ttl_seconds,
        }



# Default configuration for development/testing
def get_default_config() -> InstagramConfig:
    """Get default configuration (for development)."""
    import os

    return InstagramConfig(
        auth=InstagramAuthConfig(
            client_id=os.getenv("INSTAGRAM_CLIENT_ID", "dev_client_id"),
            client_secret=os.getenv("INSTAGRAM_CLIENT_SECRET", "dev_client_secret"),
            redirect_uri=os.getenv("INSTAGRAM_REDIRECT_URI", "http://localhost:8000/callback/instagram"),
        ),
        rate_limits=InstagramRateLimitConfig(
            calls_per_hour=200,
            calls_per_day=4800,
        ),
        media=InstagramMediaConfig(),
        webhook=InstagramWebhookConfig(
            verify_token=os.getenv("INSTAGRAM_WEBHOOK_VERIFY_TOKEN", "dev_verify_token"),
            callback_url=os.getenv("INSTAGRAM_WEBHOOK_URL", "http://localhost:8000/webhook/instagram"),
            app_secret=os.getenv("INSTAGRAM_APP_SECRET", "dev_app_secret"),
        ) if os.getenv("INSTAGRAM_WEBHOOK_URL") else None,
        enable_webhooks=bool(os.getenv("INSTAGRAM_WEBHOOK_URL")),
    )


# Configuration for different environments
class InstagramConfigPresets:
    """Pre-built configurations for different environments."""

    @staticmethod
    def development() -> InstagramConfig:
        """Development configuration with relaxed limits."""
        config = get_default_config()
        config.rate_limits.calls_per_hour = 50
        config.rate_limits.calls_per_day = 1000
        config.request_timeout_seconds = 60
        config.upload_timeout_seconds = 600
        config.max_retries = 1
        return config

    @staticmethod
    def staging() -> InstagramConfig:
        """Staging configuration."""
        config = get_default_config()
        config.rate_limits.calls_per_hour = 100
        config.rate_limits.calls_per_day = 2400
        return config

    @staticmethod
    def production() -> InstagramConfig:
        """Production configuration with full limits."""
        config = get_default_config()
        config.rate_limits.calls_per_hour = 200
        config.rate_limits.calls_per_day = 4800
        config.request_timeout_seconds = 30
        config.upload_timeout_seconds = 300
        config.max_retries = 3
        return config

    @staticmethod
    def high_volume() -> InstagramConfig:
        """High-volume configuration (requires special approval)."""
        config = InstagramConfig.presets.production()
        config.rate_limits.calls_per_hour = 1000
        config.rate_limits.calls_per_day = 24000
        config.rate_limits.burst_limit = 200
        return config


# Environment variable mapping
ENV_VAR_MAPPING = {
    "client_id": "INSTAGRAM_CLIENT_ID",
    "client_secret": "INSTAGRAM_CLIENT_SECRET",
    "redirect_uri": "INSTAGRAM_REDIRECT_URI",
    "verify_token": "INSTAGRAM_WEBHOOK_VERIFY_TOKEN",
    "callback_url": "INSTAGRAM_WEBHOOK_URL",
    "app_secret": "INSTAGRAM_APP_SECRET",
}


def load_config_from_env() -> InstagramConfig:
    """Load configuration from environment variables."""
    import os

    auth = InstagramAuthConfig(
        client_id=os.getenv("INSTAGRAM_CLIENT_ID", ""),
        client_secret=os.getenv("INSTAGRAM_CLIENT_SECRET", ""),
        redirect_uri=os.getenv("INSTAGRAM_REDIRECT_URI", ""),
    )

    webhook = None
    if os.getenv("INSTAGRAM_WEBHOOK_URL"):
        webhook = InstagramWebhookConfig(
            verify_token=os.getenv("INSTAGRAM_WEBHOOK_VERIFY_TOKEN", ""),
            callback_url=os.getenv("INSTAGRAM_WEBHOOK_URL", ""),
            app_secret=os.getenv("INSTAGRAM_APP_SECRET", ""),
        )

    return InstagramConfig(
        auth=auth,
        webhook=webhook,
        enable_webhooks=bool(webhook),
    )
InstagramConfig.presets = InstagramConfigPresets
