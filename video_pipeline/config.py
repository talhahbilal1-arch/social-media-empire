"""
Brand configs and API key loading for the video pipeline.
Loads from .env (project root) and ~/claude-video-toolkit/.env (for ElevenLabs).
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


def _load_env_file(path: Path) -> None:
    """Load a .env file into os.environ (skip if missing)."""
    if not path.exists():
        logger.debug(f".env not found at {path}, skipping")
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def load_env() -> None:
    """Load env vars from project .env and ~/claude-video-toolkit/.env."""
    # Project root .env
    project_root = Path(__file__).parent.parent
    _load_env_file(project_root / ".env")

    # ElevenLabs toolkit env
    toolkit_env = Path.home() / "claude-video-toolkit" / ".env"
    _load_env_file(toolkit_env)


@dataclass
class BrandColors:
    primary: str
    accent: str
    text: str


@dataclass
class BrandConfig:
    key: str
    name: str
    colors: BrandColors
    voice_style: str
    topics: list[str]
    pinterest_webhook_env: str
    affiliate_tag: str
    pexels_orientation: str = "portrait"

    @property
    def pinterest_webhook_url(self) -> Optional[str]:
        return os.environ.get(self.pinterest_webhook_env)


BRANDS: dict[str, BrandConfig] = {
    "daily_deal_darling": BrandConfig(
        key="daily_deal_darling",
        name="Daily Deal Darling",
        colors=BrandColors(primary="#D4AF37", accent="#FAF9F6", text="#1A1A1A"),
        voice_style="friendly, enthusiastic, deal-savvy",
        topics=[
            "Amazon deals under $20",
            "home organization hacks",
            "budget kitchen gadgets",
            "cleaning products that work",
            "smart home deals",
            "back-to-school savings",
            "holiday gift ideas under $25",
            "bathroom upgrades on a budget",
            "desk organization products",
            "laundry room essentials",
        ],
        pinterest_webhook_env="MAKE_WEBHOOK_DEALS",
        affiliate_tag="dailydealdarl-20",
    ),
    "fitover35": BrandConfig(
        key="fitover35",
        name="Fit Over 35",
        colors=BrandColors(primary="#CCFF00", accent="#0A0A0A", text="#FFFFFF"),
        voice_style="motivational, knowledgeable, direct",
        topics=[
            "progressive overload for men over 35",
            "testosterone-boosting foods",
            "recovery and sleep optimization",
            "home gym essentials",
            "compound lifts for beginners",
            "fat loss after 35",
            "joint-friendly workouts",
            "protein intake for muscle building",
            "mobility and flexibility",
            "5-minute morning routines",
        ],
        pinterest_webhook_env="MAKE_WEBHOOK_FITNESS",
        affiliate_tag="fitover3509-20",
        pexels_orientation="portrait",
    ),
    "menopause_planner": BrandConfig(
        key="menopause_planner",
        name="Menopause Planner",
        colors=BrandColors(primary="#3D6B4F", accent="#FDFBF7", text="#1A1A1A"),
        voice_style="calm, empathetic, informative",
        topics=[
            "hot flash relief tips",
            "menopause-friendly nutrition",
            "sleep during menopause",
            "hormone balance naturally",
            "weight management after 40",
            "mood and brain fog solutions",
            "best supplements for menopause",
            "exercise for hormonal balance",
            "self-care routines",
            "stress reduction techniques",
        ],
        pinterest_webhook_env="MAKE_WEBHOOK_MENOPAUSE",
        affiliate_tag="dailydealdarl-20",
    ),
    "pilottools": BrandConfig(
        key="pilottools",
        name="PilotTools",
        colors=BrandColors(primary="#6366F1", accent="#F8FAFC", text="#0F172A"),
        voice_style="professional, tech-savvy, concise",
        topics=[
            "best AI writing tools 2025",
            "AI tools for entrepreneurs",
            "ChatGPT alternatives",
            "AI image generators compared",
            "productivity tools for creators",
            "AI video editors",
            "no-code AI tools",
            "AI for social media",
            "best free AI tools",
            "AI tools under $20/month",
        ],
        pinterest_webhook_env="MAKE_WEBHOOK_PILOTTOOLS",
        affiliate_tag="pilottools-20",
    ),
}


def get_brand(brand_key: str) -> BrandConfig:
    """Return BrandConfig for the given key. Raises ValueError if unknown."""
    if brand_key not in BRANDS:
        raise ValueError(
            f"Unknown brand '{brand_key}'. Valid options: {list(BRANDS.keys())}"
        )
    return BRANDS[brand_key]


def get_api_key(name: str, required: bool = True) -> Optional[str]:
    """Fetch an API key from env. Raises RuntimeError if required and missing."""
    value = os.environ.get(name)
    if not value and required:
        raise RuntimeError(
            f"Missing required env var: {name}. "
            f"Add it to .env or ~/claude-video-toolkit/.env"
        )
    return value
