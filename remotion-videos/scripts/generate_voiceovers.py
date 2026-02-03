#!/usr/bin/env python3
"""
Generate voiceover audio files using ElevenLabs API.

This script generates voiceovers from the centralized brand configuration.
The voiceover text is built from the brand's hook, title, points, and CTA.

Usage:
    python generate_voiceovers.py [brand_id]

    If no brand_id is provided, generates voiceovers for all brands.
"""

import os
import sys
import requests
from pathlib import Path

# ElevenLabs API Key - can be overridden via environment variable
API_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_560ecaa78b2ab2234497d10b985f78037dc235d1acd9ec04")

# Default voice - Rachel (warm, friendly female voice)
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Asset directory
AUDIO_DIR = Path(__file__).parent.parent / "public" / "assets" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Centralized brand configuration (mirroring brands.ts)
# This ensures voiceover content matches exactly what's displayed in videos
BRAND_CONFIG = {
    "daily_deal_darling": {
        "content": {
            "hook": "Every woman needs this...",
            "title": "Life-Changing Beauty Find!",
            "points": [
                "Makes your skin glow",
                "Under $30 on sale now",
                "TikTok made me buy it",
            ],
            "cta": "Link in Bio!",
        },
        "voiceover_file": "daily-deal-darling-voice.mp3",
    },
    "fitnessmadeasy": {
        "content": {
            "hook": "Over 35? Try this...",
            "title": "Boost Your Metabolism!",
            "points": [
                "Works in just 10 minutes",
                "No gym required",
                "Feel stronger every day",
            ],
            "cta": "Save for Later!",
        },
        "voiceover_file": "fitness-made-easy-voice.mp3",
    },
    "menopause_planner": {
        "content": {
            "hook": "Struggling with menopause?",
            "title": "Sleep Better Tonight!",
            "points": [
                "Natural remedies that work",
                "No more night sweats",
                "Wake up refreshed",
            ],
            "cta": "Get the Guide!",
        },
        "voiceover_file": "menopause-planner-voice.mp3",
    },
}


def build_voiceover_script(brand_id: str) -> str:
    """
    Build voiceover script from brand content configuration.

    Args:
        brand_id: The brand identifier

    Returns:
        Complete voiceover script string
    """
    config = BRAND_CONFIG.get(brand_id)
    if not config:
        return ""

    content = config["content"]
    script = f"{content['hook']} {content['title']}. "

    for point in content["points"]:
        script += f"{point}. "

    script += content["cta"]
    return script


# Build VOICEOVERS dict from brand config for backward compatibility
VOICEOVERS = {}
for brand_id, config in BRAND_CONFIG.items():
    # Use hyphenated key for legacy compatibility
    legacy_key = brand_id.replace("_", "-")
    VOICEOVERS[legacy_key] = {
        "text": build_voiceover_script(brand_id),
        "file": config["voiceover_file"],
        "brand_id": brand_id,  # Keep reference to original brand ID
    }


def generate_voiceover(text: str, output_path: Path, voice_id: str = VOICE_ID) -> bool:
    """Generate voiceover audio using ElevenLabs API."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        print(f"  Generating: {text[:50]}...")
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        print(f"  Saved: {output_path}")
        return True

    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 60)
    print("ElevenLabs Voiceover Generation")
    print("=" * 60)
    print(f"\nOutput directory: {AUDIO_DIR}")

    # Parse command line arguments for specific brand
    target_brand = None
    if len(sys.argv) > 1:
        target_brand = sys.argv[1]
        # Convert underscore to hyphen for matching
        target_brand_hyphen = target_brand.replace("_", "-")
        if target_brand_hyphen not in VOICEOVERS and target_brand not in BRAND_CONFIG:
            print(f"ERROR: Unknown brand '{target_brand}'")
            print(f"Available brands: {', '.join(BRAND_CONFIG.keys())}")
            return 1
        target_brand = target_brand_hyphen

    results = {}

    for brand, config in VOICEOVERS.items():
        # Skip if targeting specific brand
        if target_brand and brand != target_brand:
            continue

        print(f"\n[{brand}]")
        print(f"  Brand ID: {config.get('brand_id', brand)}")
        print(f"  Script: {config['text'][:80]}...")

        output_path = AUDIO_DIR / config["file"]

        # Check for --force flag to regenerate existing files
        force_regenerate = "--force" in sys.argv

        if output_path.exists() and not force_regenerate:
            print(f"  Already exists: {output_path}")
            print(f"  (Use --force to regenerate)")
            results[brand] = True
            continue

        results[brand] = generate_voiceover(config["text"], output_path)

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for brand, success in results.items():
        status = "OK" if success else "FAILED"
        print(f"  {brand}: {status}")

    if not results:
        print("  No voiceovers processed")
        return 0

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
