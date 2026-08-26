"""AISMM Configuration Settings using Pydantic Settings."""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # JWT Authentication
    JWT_SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
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

    # Webhooks
    WEBHOOK_SECRET: str = Field(default="webhook-secret-change-in-production")
    WEBHOOK_TIMEOUT_SECONDS: int = 30

    # Notifications
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None

    # Frontend URL (for links in emails)
    FRONTEND_URL: str = "http://localhost:3000"

    # Platform OAuth (configured per platform in platform_config.yaml)
    # These are fallback defaults
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


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export for easy imports
settings = get_settings()