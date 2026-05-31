# app/config.py

from functools import lru_cache
from typing import List

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Use .env file for local development.
    """

    # Application Settings
    app_name: str = Field(default="FastAPI Production Application")
    debug: bool = Field(default=False)
    environment: str = Field(default="development")

    # Server Settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    
    # Database Settings
    database_url: PostgresDsn = Field(
        default="postgresql+asyncpg://user:pass@localhost/dbname"
    )
    db_pool_size: int = Field(default=10)
    db_max_overflow: int = Field(default=20)

    # Security Settings
    secret_key: str = Field(default="change-me-in-production")
    access_token_expire_minutes: int = Field(default=30)

    # CORS Settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000"]
    )

    class Config:
        # Load from .env file if present
        env_file = ".env"
        env_file_encoding = "utf-8"

        # Allow environment variables to override
        extra = "ignore"

@lru_cache
def get_settings() -> Settings:
    """
    Returns cached setting instance.
    Using lru_cache ensures settings are loaded once.
    """

    return Settings()