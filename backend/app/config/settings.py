"""AISMM Configuration Settings using Pydantic Settings."""

from functools import lru_cache
from typing import List, Optional, Set
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Known insecure/placeholder secrets that must NEVER be used in production/staging
DENYLISTED_SECRETS: Set[str] = {
    "dev-secret-key-change-in-production",
    "your-secret-key-change-in-production",
    "aismm_production_master_secret_key_2026",
    "aismm_production_master_secret_key_2026_docker",
    "webhook-secret-change-in-production",
    "replace_with_a_secure_random_secret_key_at_least_32_chars",
    "replace_with_jwt_secret_key",
    "secret",
    "changeme",
    "password",
    "your-secret-key",
    "dev-secret",
    "admin",
    "123456",
}


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "AISMM"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Database
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/aismm")
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = 50

    # Core Security Keys — NO DEFAULT VALUES ALLOWED
    SECRET_KEY: str = Field(description="Master application secret key for encryption and signing")
    JWT_SECRET_KEY: str = Field(description="JWT signing secret key")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])

    # Security
    BCRYPT_ROUNDS: int = 12
    API_RATE_LIMIT_PER_MINUTE: int = 100

    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")

    # MLflow
    MLFLOW_TRACKING_URI: str = Field(default="http://localhost:5000")
    MLFLOW_EXPERIMENT_NAME: str = "aismm"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json, text

    # File Storage
    UPLOAD_DIR: str = "/tmp/aismm/uploads"
    MAX_UPLOAD_SIZE_MB: int = 100
    MEDIA_ALLOWED_HOSTS: List[str] = Field(default_factory=list)

    # Webhooks
    WEBHOOK_SECRET: Optional[str] = Field(default=None, description="Webhook signature verification secret")
    WEBHOOK_TIMEOUT_SECONDS: int = 30

    # Email & Notifications
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: Optional[str] = Field(default="noreply@aismm.app", description="From email address for outbound emails")
    FROM_NAME: str = Field(default="AISMM", description="From name for outbound emails")

    # SMS/Phone Verification
    ENABLE_PHONE_VERIFICATION: bool = False
    SMS_PROVIDER: Optional[str] = None  # msg91, fast2sms, twilio
    SMS_API_KEY: Optional[str] = None
    SMS_API_SECRET: Optional[str] = None
    SMS_SENDER_ID: Optional[str] = None
    SMS_FROM_NUMBER: Optional[str] = None

    # Frontend URL (for links in emails and verification)
    FRONTEND_URL: str = "http://localhost:3000"

    # Platform OAuth (configured per platform in platform_config.yaml)
    INSTAGRAM_CLIENT_ID: Optional[str] = None
    INSTAGRAM_CLIENT_SECRET: Optional[str] = None
    FACEBOOK_CLIENT_ID: Optional[str] = None
    FACEBOOK_CLIENT_SECRET: Optional[str] = None
    X_CLIENT_ID: Optional[str] = None
    X_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_CLIENT_ID: Optional[str] = None
    YOUTUBE_CLIENT_SECRET: Optional[str] = None

    # Credential Encryption
    ENCRYPTION_KEY: Optional[str] = None  # 32-byte base64 encoded key

    # Monitoring
    ENABLE_PROMETHEUS: bool = True
    PROMETHEUS_PORT: int = 9090

    # Feature Flags
    ENABLE_MOCK_PLATFORM: bool = True
    ENABLE_AUTO_REPLY: bool = True
    ENABLE_GROWTH_PREDICTION: bool = True
    ENABLE_SENTIMENT_ANALYSIS: bool = True
    ENABLE_SCHEDULING: bool = True

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Startup check: refuse to boot if in non-development environment with insecure/denylisted secrets."""
        env_lower = self.ENVIRONMENT.strip().lower()
        if env_lower != "development":
            # 1. Check SECRET_KEY
            if not self.SECRET_KEY or self.SECRET_KEY.strip().lower() in DENYLISTED_SECRETS:
                raise ValueError(
                    f"FATAL SECURITY ERROR: In environment '{self.ENVIRONMENT}', "
                    f"SECRET_KEY cannot be a known placeholder value . "
                    f"A cryptographically secure secret key is required for boot."
                )
            if len(self.SECRET_KEY.strip()) < 16:
                raise ValueError(
                    f"FATAL SECURITY ERROR: In environment '{self.ENVIRONMENT}', "
                    f"SECRET_KEY must be at least 16 characters long."
                )

            # 2. Check JWT_SECRET_KEY
            if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY.strip().lower() in DENYLISTED_SECRETS:
                raise ValueError(
                    f"FATAL SECURITY ERROR: In environment '{self.ENVIRONMENT}', "
                    f"JWT_SECRET_KEY cannot be a known placeholder value . "
                    f"A cryptographically secure JWT secret key is required for boot."
                )
            if len(self.JWT_SECRET_KEY.strip()) < 16:
                raise ValueError(
                    f"FATAL SECURITY ERROR: In environment '{self.ENVIRONMENT}', "
                    f"JWT_SECRET_KEY must be at least 16 characters long."
                )

            # 3. Check WEBHOOK_SECRET if configured
            if self.WEBHOOK_SECRET and self.WEBHOOK_SECRET.strip().lower() in DENYLISTED_SECRETS:
                raise ValueError(
                    f"FATAL SECURITY ERROR: In environment '{self.ENVIRONMENT}', "
                    f"WEBHOOK_SECRET cannot be a known placeholder value."
                )

            # 4. Email verification must be enabled in production
            if not self.ENABLE_EMAIL_NOTIFICATIONS:
                raise ValueError(
                    f"FATAL SECURITY ERROR: In environment '{self.ENVIRONMENT}', "
                    f"ENABLE_EMAIL_NOTIFICATIONS must be true. Email verification is required for production."
                )
            if not self.SMTP_HOST:
                raise ValueError(
                    f"FATAL SECURITY ERROR: In environment '{self.ENVIRONMENT}', "
                    f"SMTP_HOST must be configured for email verification in production."
                )

            if "*" in self.CORS_ORIGINS or not self.CORS_ORIGINS:
                raise ValueError("Production CORS requires explicit allowed origins")
            if not self.FRONTEND_URL.startswith("https://"):
                raise ValueError("Production FRONTEND_URL must use HTTPS")
            if not self.SMTP_USER or not self.SMTP_PASSWORD:
                raise ValueError("Production SMTP credentials are required")
            if self.DEBUG:
                raise ValueError("DEBUG must be disabled in production")
        return self


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export for easy imports
try:
    settings = get_settings()
except Exception:
    # If environment variables are missing at raw import time without .env,
    # settings will be instantiated when get_settings() is called with proper env.
    settings = None  # type: ignore
