#!/usr/bin/env python3
"""
Download stock videos from free sources for Pinterest videos.
Using direct CDN links that work without API keys.
"""

import os
import requests
from pathlib import Path

# Output directory
VIDEOS_DIR = Path(__file__).parent.parent / "public" / "assets" / "videos"
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# Working stock video URLs from Pexels official CDN
# These are vertical/portrait format videos suitable for Pinterest/TikTok
STOCK_VIDEOS = {
    "daily_deal_darling": {
        # Kitchen/cooking related from Pexels
        "url": "https://videos.pexels.com/video-files/4252599/4252599-hd_1080_1920_25fps.mp4",
        "fallback": "https://videos.pexels.com/video-files/5750737/5750737-uhd_1440_2560_24fps.mp4",
        "file": "daily-deal-darling-bg.mp4"
    },
    "fitnessmadeasy": {
        # Fitness/workout from Pexels
        "url": "https://videos.pexels.com/video-files/4761440/4761440-hd_1080_1920_25fps.mp4",
        "fallback": "https://videos.pexels.com/video-files/4761671/4761671-hd_1080_1920_25fps.mp4",
        "file": "fitness-made-easy-bg.mp4"
    },
    "menopause_planner": {
        # Wellness/relaxation from Pexels
        "url": "https://videos.pexels.com/video-files/3327309/3327309-hd_1080_1920_30fps.mp4",
        "fallback": "https://videos.pexels.com/video-files/4057411/4057411-hd_1080_1920_25fps.mp4",
        "file": "menopause-planner-bg.mp4"
    }
}


def download_video(url: str, output_path: Path, timeout: int = 60) -> bool:
    """Download a video from URL."""
    try:
        print(f"  Downloading from: {url[:80]}...")
        response = requests.get(url, stream=True, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Verify file size
        size = output_path.stat().st_size
        if size < 100000:  # Less than 100KB is probably an error
            print(f"  Warning: File too small ({size} bytes)")
            return False

        print(f"  Downloaded: {output_path.name} ({size / 1024 / 1024:.1f} MB)")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 60)
    print("Stock Video Download")
    print("=" * 60)
    print(f"\nOutput directory: {VIDEOS_DIR}")

    results = {}

    for brand, config in STOCK_VIDEOS.items():
        print(f"\n[{brand}]")
        output_path = VIDEOS_DIR / config["file"]

        if output_path.exists() and output_path.stat().st_size > 100000:
            print(f"  Already exists: {output_path}")
            results[brand] = True
            continue

        # Try primary URL
        success = download_video(config["url"], output_path)

        # Try fallback if primary fails
        if not success and config.get("fallback"):
            print("  Trying fallback URL...")
            success = download_video(config["fallback"], output_path)

        results[brand] = success

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for brand, success in results.items():
        status = "OK" if success else "FAILED"
        print(f"  {brand}: {status}")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    exit(main())
