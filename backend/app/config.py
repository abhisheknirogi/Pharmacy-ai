import os
from datetime import timedelta
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API
    APP_NAME: str = "PharmaRec AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ["true", "1"]

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pharmacy.db")

    # JWT
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "your-secret-key-change-this-in-production-pharmarec-2024"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
    ]

    # ML Models
    ML_MODEL_PATH: str = os.path.join(os.path.dirname(__file__), "../../ml-engine/models")
    USE_ML_FALLBACK: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
