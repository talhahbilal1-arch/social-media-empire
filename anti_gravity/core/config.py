"""
Centralized Pydantic-based configuration.

Reads all settings from environment variables / .env file.
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)


class Settings(BaseSettings):
    """All configuration for the Anti-Gravity engine."""

    # --- Gemini AI ---
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # --- WordPress ---
    WP_SITE_URL: str = ""  # e.g. https://futuretools.io
    WP_USERNAME: str = ""
    WP_APP_PASSWORD: str = ""
    WP_DEFAULT_STATUS: str = "draft"  # "draft" or "publish"

    # --- Pinterest ---
    PINTEREST_APP_ID: str = ""
    PINTEREST_APP_SECRET: str = ""
    PINTEREST_ACCESS_TOKEN: str = ""
    PINTEREST_BOARD_ID: str = ""

    # --- Database ---
    DATABASE_PATH: str = str(Path(__file__).parent.parent / "anti_gravity.db")

    # --- Content ---
    DEFAULT_NICHE: str = "affiliate marketing"
    MIN_WORD_COUNT: int = 1500
    AFFILIATE_LINK_PLACEHOLDER: str = "[AFFILIATE_LINK]"

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = str(Path(__file__).parent.parent / "logs" / "automation.log")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def wp_api_url(self) -> str:
        """Full WordPress REST API posts endpoint."""
        return f"{self.WP_SITE_URL.rstrip('/')}/wp-json/wp/v2"

    def require(self, *keys: str) -> None:
        """Raise ValueError if any listed keys are empty."""
        missing = [k for k in keys if not getattr(self, k, "")]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")


settings = Settings()
