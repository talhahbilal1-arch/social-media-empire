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
    make_webhook_deals: str = ""
    make_webhook_menopause: str = ""

    # Late API keys (one per brand)
    late_api_key: str = ""      # Primary / fitness
    late_api_key_2: str = ""    # daily_deal_darling
    late_api_key_3: str = ""    # fitness (fallback)
    late_api_key_4: str = ""    # menopause_planner

    # Late API keys (alternate naming used by video-factory)
    late_api_key_ddd: str = ""   # daily_deal_darling (alias for late_api_key_2)
    late_api_key_meno: str = ""  # menopause_planner (alias for late_api_key_4)

    # Pinterest account/board IDs (per brand)
    pinterest_fitness_account_id: str = ""
    pinterest_fitness_board_id: str = ""
    pinterest_deals_account_id: str = ""
    pinterest_deals_board_id: str = ""
    pinterest_menopause_account_id: str = ""
    pinterest_menopause_board_id: str = ""
    # Alternate naming used by video-factory/test-pinterest-now
    pinterest_ddd_account_id: str = ""
    pinterest_ddd_board_id: str = ""
    pinterest_meno_account_id: str = ""
    pinterest_meno_board_id: str = ""

    # TikTok / Audio
    elevenlabs_api_key: str = ""
    supabase_tiktok_url: str = ""
    supabase_tiktok_key: str = ""

    # Deployment — Netlify
    netlify_api_token: str = ""
    netlify_site_id: str = ""

    # Deployment — Vercel (website hosting)
    vercel_brand_token: str = ""
    vercel_org_id: str = ""
    vercel_deals_project_id: str = ""
    vercel_fitover35_project_id: str = ""
    vercel_menopause_project_id: str = ""

    # YouTube Analytics
    youtube_api_key: str = ""

    # GitHub
    github_token: str = ""

    # Notifications
    alert_email: str = ""
    # Gmail SMTP (legacy fallback for core/notifications.py)
    alert_email_from: str = ""
    alert_email_password: str = ""
    alert_email_to: str = ""

    # Brands configuration (active Pinterest brands)
    # Note: per-brand video counts and posting slots are in cross_platform_poster.py
    brands: list = field(default_factory=lambda: [
        "daily_deal_darling",   # Women's beauty, fashion, home decor - 3 videos/day
        "fitness",       # Men's fitness/health 35+ - 6 videos/day
        "menopause_planner",    # Women's menopause wellness - 3 videos/day
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
            make_webhook_deals=os.getenv("MAKE_WEBHOOK_DEALS", ""),
            make_webhook_menopause=os.getenv("MAKE_WEBHOOK_MENOPAUSE", ""),
            late_api_key=os.getenv("LATE_API_KEY", "") or os.getenv("LATE_API_KEY_3", ""),
            late_api_key_2=os.getenv("LATE_API_KEY_2", ""),
            late_api_key_3=os.getenv("LATE_API_KEY_3", ""),
            late_api_key_4=os.getenv("LATE_API_KEY_4", ""),
            pinterest_fitness_account_id=os.getenv("PINTEREST_FITNESS_ACCOUNT_ID", ""),
            pinterest_fitness_board_id=os.getenv("PINTEREST_FITNESS_BOARD_ID", ""),
            pinterest_deals_account_id=os.getenv("PINTEREST_DEALS_ACCOUNT_ID", ""),
            pinterest_deals_board_id=os.getenv("PINTEREST_DEALS_BOARD_ID", ""),
            pinterest_menopause_account_id=os.getenv("PINTEREST_MENOPAUSE_ACCOUNT_ID", ""),
            pinterest_menopause_board_id=os.getenv("PINTEREST_MENOPAUSE_BOARD_ID", ""),
            # Alternate naming used by video-factory/test-pinterest-now
            late_api_key_ddd=os.getenv("LATE_API_KEY_DDD", "") or os.getenv("LATE_API_KEY_2", ""),
            late_api_key_meno=os.getenv("LATE_API_KEY_MENO", "") or os.getenv("LATE_API_KEY_4", ""),
            pinterest_ddd_account_id=os.getenv("PINTEREST_DDD_ACCOUNT_ID", "") or os.getenv("PINTEREST_DEALS_ACCOUNT_ID", ""),
            pinterest_ddd_board_id=os.getenv("PINTEREST_DDD_BOARD_ID", "") or os.getenv("PINTEREST_DEALS_BOARD_ID", ""),
            pinterest_meno_account_id=os.getenv("PINTEREST_MENO_ACCOUNT_ID", "") or os.getenv("PINTEREST_MENOPAUSE_ACCOUNT_ID", ""),
            pinterest_meno_board_id=os.getenv("PINTEREST_MENO_BOARD_ID", "") or os.getenv("PINTEREST_MENOPAUSE_BOARD_ID", ""),

            # TikTok / Audio
            elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY", ""),
            supabase_tiktok_url=os.getenv("SUPABASE_TIKTOK_URL", "") or os.getenv("SUPABASE_URL", ""),
            supabase_tiktok_key=os.getenv("SUPABASE_TIKTOK_KEY", "") or os.getenv("SUPABASE_KEY", ""),

            # Deployment — Netlify
            netlify_api_token=os.getenv("NETLIFY_API_TOKEN", ""),
            netlify_site_id=os.getenv("NETLIFY_SITE_ID", ""),

            # Deployment — Vercel
            vercel_brand_token=os.getenv("VERCEL_BRAND_TOKEN", ""),
            vercel_org_id=os.getenv("VERCEL_ORG_ID", ""),
            vercel_deals_project_id=os.getenv("VERCEL_DEALS_PROJECT_ID", ""),
            vercel_fitover35_project_id=os.getenv("VERCEL_FITOVER35_PROJECT_ID", ""),
            vercel_menopause_project_id=os.getenv("VERCEL_MENOPAUSE_PROJECT_ID", ""),

            # YouTube Analytics
            youtube_api_key=os.getenv("YOUTUBE_API_KEY", ""),

            # GitHub
            github_token=os.getenv("GITHUB_TOKEN", "") or os.getenv("GH_TOKEN", ""),

            # Notifications
            alert_email=os.getenv("ALERT_EMAIL", ""),
            alert_email_from=os.getenv("ALERT_EMAIL_FROM", ""),
            alert_email_password=os.getenv("ALERT_EMAIL_PASSWORD", ""),
            alert_email_to=os.getenv("ALERT_EMAIL_TO", ""),
        )

    def validate(self) -> list[str]:
        """Validate required configuration values. Returns list of missing keys."""
        required = {
            "anthropic_api_key": self.anthropic_api_key,
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
