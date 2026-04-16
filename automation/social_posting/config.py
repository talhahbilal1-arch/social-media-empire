"""Environment + brand configuration for the social posting suite.

All credentials are loaded from environment variables. Missing creds for a
platform should not crash the importer — callers can ask :func:`have_twitter`
or :func:`have_linkedin` and gracefully skip a platform when secrets are
absent (useful for dry-runs and CI without secrets).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:  # python-dotenv is optional in CI, only used for local dev
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - missing dotenv is fine in CI
    pass


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PACKAGE_DIR: Path = Path(__file__).resolve().parent
QUEUE_DIR: Path = PACKAGE_DIR / "queue"
POSTED_DIR: Path = PACKAGE_DIR / "posted"

QUEUE_DIR.mkdir(parents=True, exist_ok=True)
POSTED_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------
TWITTER_API_KEY: Optional[str] = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET: Optional[str] = os.environ.get("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN: Optional[str] = os.environ.get("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET: Optional[str] = os.environ.get("TWITTER_ACCESS_SECRET")

LINKEDIN_ACCESS_TOKEN: Optional[str] = os.environ.get("LINKEDIN_ACCESS_TOKEN")
LINKEDIN_PERSON_ID: Optional[str] = os.environ.get("LINKEDIN_PERSON_ID")

GEMINI_API_KEY: Optional[str] = os.environ.get("GEMINI_API_KEY")

SUPABASE_URL: Optional[str] = os.environ.get("SUPABASE_URL")
SUPABASE_KEY: Optional[str] = os.environ.get("SUPABASE_KEY")


def have_twitter() -> bool:
    """All four OAuth1.0a tokens present?"""
    return all(
        [
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_SECRET,
        ]
    )


def have_linkedin() -> bool:
    """LinkedIn OAuth2 access token + author URN present?"""
    return bool(LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_ID)


def have_supabase() -> bool:
    return bool(SUPABASE_URL and SUPABASE_KEY)


def have_gemini() -> bool:
    return bool(GEMINI_API_KEY)


def require(value: Optional[str], name: str) -> str:
    """Return ``value`` or raise a clear error mentioning the env var name."""
    if not value:
        raise RuntimeError(
            f"Required environment variable {name} is not set. "
            f"See automation/social_posting/README.md for setup."
        )
    return value


# ---------------------------------------------------------------------------
# Brands
# ---------------------------------------------------------------------------
@dataclass
class BrandConfig:
    """Per-brand metadata for downstream content generation + posting.

    LinkedIn currently posts from a single personal/company URN
    (``LINKEDIN_PERSON_ID``); per-brand overrides are supported here for
    when each brand gets its own LinkedIn page in the future.
    """

    name: str
    short_key: str
    site_url: str
    twitter_handle: Optional[str] = None
    linkedin_person_id: Optional[str] = None
    hashtags: list[str] = field(default_factory=list)


BRANDS: dict[str, BrandConfig] = {
    "fitness": BrandConfig(
        name="FitOver35",
        short_key="fitness",
        site_url="https://fitover35.com",
        twitter_handle="@fitover35",
        hashtags=["#FitOver35", "#MensFitness", "#StrengthTraining"],
    ),
    "deals": BrandConfig(
        name="Daily Deal Darling",
        short_key="deals",
        site_url="https://dailydealdarling.com",
        twitter_handle="@dailydealdarl",
        hashtags=["#Deals", "#HomeFinds", "#BudgetLifestyle"],
    ),
    "menopause": BrandConfig(
        name="Menopause Planner",
        short_key="menopause",
        site_url="https://menopause-planner-website.vercel.app",
        hashtags=["#MenopauseWellness", "#MidlifeHealth", "#WomensHealth"],
    ),
}


def get_brand(short_key: str) -> BrandConfig:
    if short_key not in BRANDS:
        raise KeyError(
            f"Unknown brand key {short_key!r}. Valid keys: {sorted(BRANDS)}"
        )
    return BRANDS[short_key]
