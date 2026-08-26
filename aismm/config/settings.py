"""
AISMM Settings - Central configuration management.
Uses Pydantic Settings for type-safe, environment-variable-driven configuration.
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "AISMM"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, validation_alias="DEBUG")
    ENVIRONMENT: str = Field(default="development", validation_alias="ENVIRONMENT")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    CONFIG_DIR: Path = BASE_DIR / "config"
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/aismm.db",
        validation_alias="DATABASE_URL"
    )
    DATABASE_ECHO: bool = Field(default=False, validation_alias="DATABASE_ECHO")
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="dev-secret-change-in-production",
        validation_alias="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        validation_alias="ALLOWED_ORIGINS"
    )
    
    # AI/ML
    MLFLOW_TRACKING_URI: str = Field(
        default="file:./mlruns",
        validation_alias="MLFLOW_TRACKING_URI"
    )
    MODEL_REGISTRY_PATH: Path = BASE_DIR / "models"
    
    # External APIs (base URLs, not secrets)
    INSTAGRAM_API_BASE: str = "https://graph.instagram.com"
    FACEBOOK_API_BASE: str = "https://graph.facebook.com"
    X_API_BASE: str = "https://api.twitter.com/2"
    LINKEDIN_API_BASE: str = "https://api.linkedin.com/v2"
    YOUTUBE_API_BASE: str = "https://www.googleapis.com/youtube/v3"
    
    # Webhook
    WEBHOOK_BASE_URL: str = Field(
        default="https://api.aismm.example.com",
        validation_alias="WEBHOOK_BASE_URL"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    LOG_FORMAT: str = "json"
    
    # Rate limiting
    DEFAULT_RATE_LIMIT: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


# Global settings instance
settings = Settings()

# Ensure data directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.MODEL_REGISTRY_PATH.mkdir(parents=True, exist_ok=True)
