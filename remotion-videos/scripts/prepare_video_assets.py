#!/usr/bin/env python3
"""
Prepare video assets for Pinterest videos:
1. Download stock videos from Pexels (with proper API authentication)
2. Generate voiceover audio using ElevenLabs
"""

import os
import sys
import json
import requests
from pathlib import Path

# Asset directories
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
ASSETS_DIR = PROJECT_DIR / "public" / "assets"
VIDEOS_DIR = ASSETS_DIR / "videos"
AUDIO_DIR = ASSETS_DIR / "audio"

# Ensure directories exist
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Brand configurations with video scripts
BRANDS = {
    "daily_deal_darling": {
        "search_query": "kitchen cooking home lifestyle",
        "voiceover_text": "This changed everything. Must-Have Kitchen Gadget! Saves 10 minutes every morning. Under $25 on Amazon. Over 50,000 5-star reviews. Link in Bio!",
        "video_file": "daily-deal-darling-bg.mp4",
        "audio_file": "daily-deal-darling-voice.mp3"
    },
    "fitnessmadeasy": {
        "search_query": "fitness workout exercise gym",
        "voiceover_text": "No equipment needed. 5-Minute Ab Workout. Burns belly fat fast. Perfect for beginners. Do it anywhere. Save for Later!",
        "video_file": "fitness-made-easy-bg.mp4",
        "audio_file": "fitness-made-easy-voice.mp3"
    },
    "menopause_planner": {
        "search_query": "wellness relaxation nature calm",
        "voiceover_text": "I wish I knew this sooner. Natural Hot Flash Relief. Works in 5 minutes. No medications needed. Doctor-approved method. Get the Guide!",
        "video_file": "menopause-planner-bg.mp4",
        "audio_file": "menopause-planner-voice.mp3"
    }
}

# Alternative free stock video URLs (Pixabay - no API key required for direct downloads)
PIXABAY_VIDEOS = {
    "daily_deal_darling": "https://cdn.pixabay.com/video/2020/05/25/40302-424305562_large.mp4",  # Kitchen/cooking
    "fitnessmadeasy": "https://cdn.pixabay.com/video/2019/06/18/24584-343490337_large.mp4",  # Fitness/workout
    "menopause_planner": "https://cdn.pixabay.com/video/2020/07/30/46026-446001566_large.mp4"   # Nature/wellness
}


def download_video_pixabay(brand: str) -> bool:
    """Download stock video from Pixabay (no API key needed)."""
    config = BRANDS[brand]
    video_path = VIDEOS_DIR / config["video_file"]

    if video_path.exists():
        print(f"  Video already exists: {video_path}")
        return True

    url = PIXABAY_VIDEOS.get(brand)
    if not url:
        print(f"  No Pixabay URL configured for {brand}")
        return False

    print(f"  Downloading from Pixabay...")
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"  Downloaded: {video_path}")
        return True
    except Exception as e:
        print(f"  Download failed: {e}")
        return False


def download_video_pexels(brand: str, api_key: str) -> bool:
    """Download stock video from Pexels using API."""
    config = BRANDS[brand]
    video_path = VIDEOS_DIR / config["video_file"]

    if video_path.exists():
        print(f"  Video already exists: {video_path}")
        return True

    # Search for videos
    search_url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": api_key}
    params = {
        "query": config["search_query"],
        "orientation": "portrait",
        "size": "medium",
        "per_page": 5
    }

    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data.get("videos"):
            print(f"  No videos found for query: {config['search_query']}")
            return False

        # Get the first video's HD file
        video = data["videos"][0]
        video_files = video.get("video_files", [])

        # Find the best quality portrait video
        best_file = None
        for vf in video_files:
            if vf.get("height", 0) >= 1080 and vf.get("width", 0) <= vf.get("height", 0):
                if not best_file or vf.get("height", 0) > best_file.get("height", 0):
                    best_file = vf

        if not best_file:
            # Fallback to any HD file
            for vf in video_files:
                if vf.get("height", 0) >= 720:
                    best_file = vf
                    break

        if not best_file and video_files:
            best_file = video_files[0]

        if not best_file:
            print(f"  No suitable video file found")
            return False

        # Download the video
        download_url = best_file["link"]
        print(f"  Downloading: {download_url[:80]}...")

        dl_response = requests.get(download_url, stream=True, timeout=120)
        dl_response.raise_for_status()

        with open(video_path, 'wb') as f:
            for chunk in dl_response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"  Downloaded: {video_path}")
        return True

    except Exception as e:
        print(f"  Pexels download failed: {e}")
        return False


def generate_voiceover(brand: str, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bool:
    """Generate voiceover using ElevenLabs API."""
    config = BRANDS[brand]
    audio_path = AUDIO_DIR / config["audio_file"]

    if audio_path.exists():
        print(f"  Audio already exists: {audio_path}")
        return True

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": config["voiceover_text"],
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        print(f"  Generating voiceover for: {config['voiceover_text'][:50]}...")
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()

        with open(audio_path, 'wb') as f:
            f.write(response.content)

        print(f"  Generated: {audio_path}")
        return True

    except Exception as e:
        print(f"  Voiceover generation failed: {e}")
        return False


def main():
    print("=" * 60)
    print("Pinterest Video Asset Preparation")
    print("=" * 60)

    # Get API keys from environment
    pexels_key = os.getenv("PEXELS_API_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    elevenlabs_voice = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    print(f"\nAsset directories:")
    print(f"  Videos: {VIDEOS_DIR}")
    print(f"  Audio: {AUDIO_DIR}")

    print(f"\nAPI Keys:")
    print(f"  Pexels: {'Set' if pexels_key else 'NOT SET - will use Pixabay'}")
    print(f"  ElevenLabs: {'Set' if elevenlabs_key else 'NOT SET - skipping voiceover'}")

    results = {"videos": {}, "audio": {}}

    for brand in BRANDS:
        print(f"\n{'='*40}")
        print(f"Processing: {brand}")
        print("=" * 40)

        # Download video
        print("\n[Video Download]")
        if pexels_key:
            video_ok = download_video_pexels(brand, pexels_key)
        else:
            video_ok = download_video_pixabay(brand)
        results["videos"][brand] = video_ok

        # Generate voiceover
        print("\n[Voiceover Generation]")
        if elevenlabs_key:
            audio_ok = generate_voiceover(brand, elevenlabs_key, elevenlabs_voice)
        else:
            print("  Skipped - ELEVENLABS_API_KEY not set")
            audio_ok = False
        results["audio"][brand] = audio_ok

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    print("\nVideos:")
    for brand, ok in results["videos"].items():
        status = "OK" if ok else "FAILED"
        print(f"  {brand}: {status}")

    print("\nAudio:")
    for brand, ok in results["audio"].items():
        status = "OK" if ok else "FAILED/SKIPPED"
        print(f"  {brand}: {status}")

    # Write manifest
    manifest = {
        "videos": {brand: str(VIDEOS_DIR / BRANDS[brand]["video_file"]) for brand in BRANDS},
        "audio": {brand: str(AUDIO_DIR / BRANDS[brand]["audio_file"]) for brand in BRANDS}
    }
    manifest_path = ASSETS_DIR / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest written to: {manifest_path}")

    return 0 if all(results["videos"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
