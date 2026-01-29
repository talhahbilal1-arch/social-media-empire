"""Configuration management for Social Media Empire."""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    # AI Services
    anthropic_api_key: str = ""
    gemini_api_key: str = ""

    # Media Services
    pexels_api_key: str = ""
    creatomate_api_key: str = ""

    # Database
    supabase_url: str = ""
    supabase_key: str = ""

    # Email Marketing
    resend_api_key: str = ""
    convertkit_api_key: str = ""
    convertkit_api_secret: str = ""
    convertkit_form_id: str = ""

    # Social Platforms
    youtube_client_id: str = ""
    youtube_client_secret: str = ""
    youtube_refresh_token: str = ""
    make_com_pinterest_webhook: str = ""

    # Notifications
    alert_email: str = ""

    # Brands configuration
    brands: list = field(default_factory=lambda: [
        "daily_deal_darling",
        "fitnessmadeasy",
        "menopause_planner",
        "nurse_planner",
        "adhd_planner"
    ])

    # Platforms configuration
    platforms: list = field(default_factory=lambda: [
        "youtube_shorts",
        "pinterest",
        "tiktok",
        "instagram_reels"
    ])

    # Schedule configuration (PST times)
    posting_times: list = field(default_factory=lambda: [
        "06:00",  # Morning
        "12:00",  # Noon
        "18:00"   # Evening
    ])

    videos_per_day: int = 3

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        load_dotenv()

        return cls(
            # AI Services
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),

            # Media Services
            pexels_api_key=os.getenv("PEXELS_API_KEY", ""),
            creatomate_api_key=os.getenv("CREATOMATE_API_KEY", ""),

            # Database
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_key=os.getenv("SUPABASE_KEY", ""),

            # Email Marketing
            resend_api_key=os.getenv("RESEND_API_KEY", ""),
            convertkit_api_key=os.getenv("CONVERTKIT_API_KEY", ""),
            convertkit_api_secret=os.getenv("CONVERTKIT_API_SECRET", ""),
            convertkit_form_id=os.getenv("CONVERTKIT_FORM_ID", ""),

            # Social Platforms
            youtube_client_id=os.getenv("YOUTUBE_CLIENT_ID", ""),
            youtube_client_secret=os.getenv("YOUTUBE_CLIENT_SECRET", ""),
            youtube_refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN", ""),
            make_com_pinterest_webhook=os.getenv("MAKE_COM_PINTEREST_WEBHOOK", ""),

            # Notifications
            alert_email=os.getenv("ALERT_EMAIL", ""),
        )

    def validate(self) -> list[str]:
        """Validate required configuration values. Returns list of missing keys."""
        required = {
            "gemini_api_key": self.gemini_api_key,
            "pexels_api_key": self.pexels_api_key,
            "supabase_url": self.supabase_url,
            "supabase_key": self.supabase_key,
        }

        missing = [key for key, value in required.items() if not value]
        return missing


_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config
