"""Application settings loaded from environment variables."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file if exists (development)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class Settings(BaseSettings):
    """Application settings with validation."""

    # API Keys (required for production, optional for testing)
    GEMINI_API_KEY: str = ""
    PEXELS_API_KEY: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Application settings
    DEFAULT_BRAND: str = "menopause"
    MAX_CACHE_SIZE_GB: int = 5
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def validate_api_keys(self, required: Optional[list[str]] = None) -> None:
        """Validate required API keys are present.

        Args:
            required: List of required keys, or None for all

        Raises:
            ValueError: If any required keys are missing
        """
        all_keys = ["GEMINI_API_KEY", "PEXELS_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
        check_keys = all_keys if required is None else required

        missing = [key for key in check_keys if not getattr(self, key)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Singleton instance
settings = Settings()
