"""Application configuration using pydantic-settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    app_name: str = "TestForge Store API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./testforge.db"

    # Auth — DEMO ONLY.  Never use these values in production.
    secret_key: str = "DEMO-ONLY-NOT-SECRET-change-before-any-real-use"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Pagination
    max_page_size: int = 100
    default_page_size: int = 20

    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()
