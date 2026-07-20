"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_RATE_LIMIT_PER_MINUTE = 60


class Settings(BaseSettings):
    """Centralized application configuration, loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["local", "staging", "production"] = "local"
    app_debug: bool = True
    app_name: str = "transaction-api"
    log_level: str = "INFO"

    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173"
    rate_limit_per_minute: int = DEFAULT_RATE_LIMIT_PER_MINUTE

    postgres_user: str = "app"
    postgres_password: str = "change_me"  # noqa: S105 -- dev default, overridden via .env
    postgres_db: str = "transactions_db"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    database_url: str = (
        "postgresql+asyncpg://app:change_me@postgres:5432/transactions_db"
    )

    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_url: str = "redis://redis:6379/0"
    transactions_queue_name: str = "transactions"

    ai_provider: Literal["mock", "openai", "gemini"] = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Gemini reuses OpenAIService via its OpenAI-compatible endpoint.
    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"

    secret_key: str = Field(default="change_this_to_a_random_secret_in_production")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse the comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin]

    @property
    def is_production(self) -> bool:
        """Whether the app is running in the production environment."""
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
