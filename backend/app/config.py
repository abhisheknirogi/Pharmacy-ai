"""
Application configuration and settings.
Centralized configuration management with environment-based overrides.
"""

import os
from datetime import timedelta
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation and defaults."""

    # ==================== API Configuration ====================
    APP_NAME: str = Field("PharmaRec AI", description="Application name")
    APP_VERSION: str = Field("1.0.0", description="Application version")
    DEBUG: bool = Field(False, description="Enable debug mode")
    ENVIRONMENT: str = Field("development", description="Environment: development, staging, production")

    # ==================== Database Configuration ====================
    DATABASE_URL: str = Field(
        "sqlite:///./pharmacy.db",
        description="Database connection URL"
    )
    DATABASE_POOL_SIZE: int = Field(5, ge=1, le=20, description="Connection pool size")
    DATABASE_POOL_MAX_OVERFLOW: int = Field(10, ge=1, description="Max overflow connections")
    DATABASE_POOL_RECYCLE: int = Field(3600, ge=600, description="Connection recycle time in seconds")

    # ==================== Authentication & JWT ====================
    SECRET_KEY: str = Field(
        ...,
        description="Secret key for JWT signing (required in production)"
    )
    ALGORITHM: str = Field("HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        60 * 24,
        ge=15,
        le=10080,
        description="Access token expiration in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(30, ge=1, le=365, description="Refresh token expiration in days")

    # ==================== CORS Configuration ====================
    ALLOWED_ORIGINS: List[str] = Field(
        ["http://localhost:3000", "http://localhost:8000"],
        description="Allowed origins for CORS"
    )

    # ==================== API Rate Limiting ====================
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(
        100,
        ge=1,
        le=10000,
        description="Rate limit requests per minute"
    )

    # ==================== ML Models Configuration ====================
    ML_MODEL_PATH: str = Field(
        default_factory=lambda: os.path.join(os.path.dirname(__file__), "../../ml-engine/models"),
        description="Path to ML models directory"
    )
    USE_ML_FALLBACK: bool = Field(True, description="Use ML fallback when model unavailable")

    # ==================== Logging Configuration ====================
    LOG_LEVEL: str = Field("INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    LOG_FORMAT: str = Field("json", description="Log format: json or text")

    # ==================== Feature Flags ====================
    ENABLE_PDF_PARSING: bool = Field(True, description="Enable PDF parsing feature")
    ENABLE_ML_PREDICTIONS: bool = Field(True, description="Enable ML-based predictions")
    ENABLE_WHATSAPP_BOT: bool = Field(False, description="Enable WhatsApp bot feature")

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate secret key is sufficiently strong."""
        environment = info.data.get("ENVIRONMENT", "development")
        if environment == "production":
            if len(v) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
            if v == "your-secret-key-change-this-in-production-pharmarec-2024":
                raise ValueError("SECRET_KEY must not be the default value in production")
        return v

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of allowed values."""
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Initialize global settings
settings = Settings()
