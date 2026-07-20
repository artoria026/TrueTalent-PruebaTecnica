"""Settings for the RPA module, loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class RpaSettings(BaseSettings):
    """Configuration for Playwright-based scrapers."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    headless: bool = True
    default_search_term: str = "Python (programming language)"
    log_level: str = "INFO"

    rpa_results_api_url: str = "http://localhost:8000/api/v1/rpa/extractions"
    assistant_api_url: str = "http://localhost:8000/api/v1/assistant/summarize"
    assistant_user_id: str = "rpa-wikipedia-scraper"
