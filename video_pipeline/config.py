"""Brand configs and environment variable loading for the video pipeline."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# ── Load .env files ────────────────────────────────────────────────────────────
# Load project .env first, then toolkit .env for ElevenLabs key fallback

_PROJECT_ENV = Path(__file__).parent.parent / ".env"
_TOOLKIT_ENV = Path.home() / "claude-video-toolkit" / ".env"

load_dotenv(_PROJECT_ENV)  # project env — higher priority
if not os.getenv("ELEVENLABS_API_KEY"):
    load_dotenv(_TOOLKIT_ENV)  # fallback for ElevenLabs key

# ── Output directories ─────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "videos"
ASSETS_DIR = Path(__file__).parent / "assets"
BGMUSIC_DIR = ASSETS_DIR / "bgmusic"
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "/opt/homebrew/bin/ffmpeg")
FFPROBE_BIN = os.getenv("FFPROBE_BIN", "/opt/homebrew/bin/ffprobe")

# ── ElevenLabs voice IDs (public library defaults, override via env) ───────────
# Find IDs at: https://elevenlabs.io/app/voice-library
_VOICE_IDS = {
    "warm_female":       os.getenv("VOICE_ID_WARM_FEMALE",     "21m00Tcm4TlvDq8ikWAM"),  # Rachel
    "authoritative_male": os.getenv("VOICE_ID_AUTH_MALE",      "pNInz6obpgDQGcFmaJgB"),  # Adam
    "empathetic_female": os.getenv("VOICE_ID_EMPATHETIC_FEMALE","EXAVITQu4vr4xnSDxMaL"),  # Bella
    "professional":      os.getenv("VOICE_ID_PROFESSIONAL",    "ErXwobaYiN019PkySvjV"),  # Antoni
}

# ── Brand configs ──────────────────────────────────────────────────────────────
BRANDS: dict[str, dict] = {
    "fitover35": {
        "name": "Fitness Made Easy",
        "niche": "Men's fitness over 35 — muscle building, nutrition, testosterone, recovery",
        "audience": "men aged 35-60 who want to build muscle, stay lean, and feel strong",
        "tone": "authoritative, motivational, no-nonsense, practical, results-focused",
        "colors": {
            "primary": "#1A1A1A",
            "accent":  "#C9A96E",
            "text":    "#FFFFFF",
        },
        "voice_style": "authoritative_male",
        "topics": [
            "muscle building over 35", "testosterone optimization", "protein and nutrition",
            "workout plans for older men", "recovery and sleep", "body recomposition",
            "strength training fundamentals", "fat loss for men over 35",
        ],
        "hook_styles": [
            "If you're over 35 and struggling with {topic}, this changes everything...",
            "Most men over 35 make this {topic} mistake. Here's the fix...",
            "I wish I knew this about {topic} when I was 35...",
            "The #1 {topic} tip most trainers won't tell you...",
        ],
        "hashtags": ["#fitover35", "#menshealth", "#musclebuilding", "#fitover40", "#strengthtraining", "#over35fitness"],
        "cta": "Follow for daily fitness tips. Free 30-day plan in bio.",
        "webhook_env": "MAKE_WEBHOOK_FITNESS",
        "site_url": "https://fitover35.com",
        "amazon_tag": "fitover3509-20",
    },
    "deals": {
        "name": "Daily Deal Darling",
        "niche": "Budget home, beauty, and lifestyle finds for women",
        "audience": "women aged 25-45 who love Amazon deals, home decor, and beauty finds",
        "tone": "warm, excited, friendly, relatable, conversational",
        "colors": {
            "primary": "#2D5A3D",
            "accent":  "#D4A574",
            "text":    "#FFFFFF",
        },
        "voice_style": "warm_female",
        "topics": [
            "Amazon must-haves under $25", "viral TikTok products", "home organization finds",
            "beauty dupes", "kitchen gadgets", "cozy home items", "hidden Amazon gems",
            "budget home decor", "self-care products",
        ],
        "hook_styles": [
            "This $__ Amazon find is going viral and here's why...",
            "STOP scrolling — this {topic} deal ends TODAY...",
            "I almost didn't share this {topic} because it keeps selling out...",
            "POV: You discover this cult-favorite {topic} is under $25...",
        ],
        "hashtags": ["#amazonfind", "#dealsoftheday", "#amazonmusthaves", "#homefinds", "#budgetbeauty", "#tiktokmademebuyit"],
        "cta": "Follow for daily deals. Free finds guide in bio link.",
        "webhook_env": "MAKE_WEBHOOK_DEALS",
        "site_url": "https://dailydealdarling.com",
        "amazon_tag": "dailydealdarl-20",
    },
    "menopause": {
        "name": "Menopause Planner",
        "niche": "Menopause wellness, symptom management, and hormone health",
        "audience": "women aged 45-60 navigating perimenopause and menopause",
        "tone": "warm, empathetic, supportive, informative, reassuring",
        "colors": {
            "primary": "#9CAF88",
            "accent":  "#D4A5A5",
            "text":    "#FFFFFF",
        },
        "voice_style": "empathetic_female",
        "topics": [
            "hot flash relief", "menopause sleep tips", "hormone balance naturally",
            "weight gain during menopause", "brain fog and mood swings",
            "menopause diet and nutrition", "HRT options explained",
            "perimenopause signs", "self-care rituals for menopause",
        ],
        "hook_styles": [
            "If you're struggling with {topic}, you're not alone — and this helps...",
            "Nobody talks about this {topic} menopause tip...",
            "The {topic} trick that changed everything for women in menopause...",
            "This is why you're experiencing {topic} during menopause...",
        ],
        "hashtags": ["#menopause", "#perimenopause", "#hormonehealth", "#menopausewellness", "#womenover45", "#menopauserelief"],
        "cta": "Follow for daily menopause tips. Free symptom guide in bio.",
        "webhook_env": "MAKE_WEBHOOK_MENOPAUSE",
        "site_url": "https://menopause-planner-website.vercel.app",
        "amazon_tag": "dailydealdarl-20",
    },
    "pilottools": {
        "name": "PilotTools",
        "niche": "AI tool reviews, productivity tips, and automation for professionals",
        "audience": "professionals, entrepreneurs, and creators who use AI tools",
        "tone": "professional, tech-savvy, insightful, practical, enthusiastic",
        "colors": {
            "primary": "#1E3A5F",
            "accent":  "#4ECDC4",
            "text":    "#FFFFFF",
        },
        "voice_style": "professional",
        "topics": [
            "best AI tools for productivity", "ChatGPT alternatives", "AI writing tools",
            "AI video tools", "automation workflows", "SaaS tool reviews",
            "no-code AI tools", "AI for content creators", "free vs paid AI tools",
        ],
        "hook_styles": [
            "This AI tool just replaced {topic} for me and it's free...",
            "The {topic} AI tool nobody's talking about in {year}...",
            "I tested every {topic} AI tool so you don't have to...",
            "Stop paying for {topic} — this free AI tool does it better...",
        ],
        "hashtags": ["#aitools", "#productivity", "#artificialintelligence", "#chatgpt", "#automation", "#techreview"],
        "cta": "Follow for weekly AI tool reviews. Top 50 tools list at pilottools.ai",
        "webhook_env": None,  # No Pinterest webhook for pilottools
        "site_url": "https://pilottools.ai",
        "amazon_tag": None,
    },
}


def get_brand(brand_key: str) -> dict:
    """Return brand config, raising ValueError if unknown."""
    if brand_key not in BRANDS:
        raise ValueError(f"Unknown brand '{brand_key}'. Valid brands: {list(BRANDS)}")
    return BRANDS[brand_key]


def get_env(key: str, required: bool = False) -> Optional[str]:
    """Return env var value, optionally raising if missing."""
    value = os.getenv(key)
    if required and not value:
        raise EnvironmentError(f"Required env var '{key}' is not set.")
    return value


def get_voice_id(brand_key: str) -> str:
    """Return ElevenLabs voice ID for the brand, checking env override first."""
    brand = get_brand(brand_key)
    env_override = os.getenv(f"VOICE_ID_{brand_key.upper()}")
    if env_override:
        return env_override
    style = brand["voice_style"]
    return _VOICE_IDS[style]


def get_pinterest_webhook(brand_key: str) -> Optional[str]:
    """Return Make.com webhook URL for the brand's Pinterest poster."""
    brand = get_brand(brand_key)
    env_key = brand.get("webhook_env")
    if not env_key:
        return None
    return os.getenv(env_key)
