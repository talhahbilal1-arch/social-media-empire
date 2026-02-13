#!/usr/bin/env python3
"""
Upload videos to Supabase and post to Pinterest via Late API.

This script uses the centralized brand configuration to ensure:
- Correct API key for each brand
- Correct Pinterest account for each brand
- Correct content/description for each brand
- No cross-contamination between brands

Usage:
    python upload_and_post.py [brand_id]

    If no brand_id is provided, processes all brands.
"""

import os
import sys
import json
import requests
from pathlib import Path

# Supabase Configuration (must be set via env vars)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_KEY environment variables are required")
    print("Set them before running this script")
BUCKET = "videos"


# ============================================================================
# CENTRALIZED BRAND CONFIGURATION
# Single source of truth - matches brands.ts in the Remotion project
# ============================================================================

BRAND_CONFIG = {
    "daily_deal_darling": {
        "id": "daily_deal_darling",
        "displayName": "DailyDealDarling",
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
        "pinterest": {
            "accountId": os.environ.get("PINTEREST_DDD_ACCOUNT_ID", ""),
            "boardId": os.environ.get("PINTEREST_DDD_BOARD_ID", ""),
            "apiKey": os.environ.get("LATE_API_KEY_DDD", ""),
            "link": "https://dailydealdarling.com",
        },
        "video": {
            "file": "daily-deal-darling.mp4",
            "storageName": "daily-deal-darling-slideshow.mp4",
        },
        "hashtags": "#beautyfinds #skincare #beautytips #womensfashion #homedecor #giftsforher",
    },
    "fitnessmadeasy": {
        "id": "fitnessmadeasy",
        "displayName": "FitOver35",
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
        "pinterest": {
            "accountId": os.environ.get("PINTEREST_FITNESS_ACCOUNT_ID", ""),
            "boardId": os.environ.get("PINTEREST_FITNESS_BOARD_ID", ""),
            "apiKey": os.environ.get("LATE_API_KEY", ""),
            "link": "https://fitnessmadeasy.com",
        },
        "video": {
            "file": "fitness-made-easy.mp4",
            "storageName": "fitness-made-easy-slideshow.mp4",
        },
        "hashtags": "#fitover35 #metabolismboost #womenshealth #homeworkout #fitnessover40",
    },
    "menopause_planner": {
        "id": "menopause_planner",
        "displayName": "MenopausePlanner",
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
        "pinterest": {
            "accountId": os.environ.get("PINTEREST_MENO_ACCOUNT_ID", ""),
            "boardId": os.environ.get("PINTEREST_MENO_BOARD_ID", ""),
            "apiKey": os.environ.get("LATE_API_KEY_MENO", ""),
            "link": "https://www.etsy.com/listing/4435219468/menopause-wellness-planner-bundle",
        },
        "video": {
            "file": "menopause-planner.mp4",
            "storageName": "menopause-planner-slideshow.mp4",
        },
        "hashtags": "#menopause #menopauserelief #sleeptips #nightsweats #perimenopause #menopausesupport",
    },
}


def build_pinterest_description(brand_id: str) -> str:
    """
    Build Pinterest description from brand content.

    Args:
        brand_id: The brand identifier

    Returns:
        Formatted Pinterest description with title, content, and hashtags
    """
    config = BRAND_CONFIG.get(brand_id)
    if not config:
        return ""

    content = config["content"]
    points_text = " ".join([f"{p}!" for p in content["points"]])

    return f"""{content['title']} - Watch with Sound!

{content['hook']} {points_text}

{content['cta']}

{config['hashtags']}"""


# Build legacy VIDEOS dict for backward compatibility
VIDEOS = {}
for brand_id, config in BRAND_CONFIG.items():
    VIDEOS[brand_id] = {
        "file": config["video"]["file"],
        "storage_name": config["video"]["storageName"],
        "account_id": config["pinterest"]["accountId"],
        "board_id": config["pinterest"]["boardId"],
        "link": config["pinterest"]["link"],
        "content": build_pinterest_description(brand_id),
    }

# Build LATE_API_KEYS for backward compatibility
LATE_API_KEYS = {
    brand_id: config["pinterest"]["apiKey"]
    for brand_id, config in BRAND_CONFIG.items()
}


def upload_to_supabase(file_path: Path, storage_name: str) -> str:
    """Upload video to Supabase Storage."""
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{storage_name}"

    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "video/mp4",
        "x-upsert": "true"
    }

    with open(file_path, 'rb') as f:
        response = requests.post(url, headers=headers, data=f)

    if response.status_code in [200, 201]:
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{storage_name}"
        return public_url
    else:
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")


def post_to_pinterest(brand: str, video_url: str, config: dict) -> dict:
    """Post video to Pinterest via Late API."""
    api_key = LATE_API_KEYS[brand]

    payload = {
        "content": config["content"],
        "platforms": [{
            "platform": "pinterest",
            "accountId": config["account_id"],
            "platformSpecificData": {
                "boardId": config["board_id"],
                "link": config["link"]
            }
        }],
        "mediaItems": [{"type": "video", "url": video_url}]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://getlate.dev/api/v1/posts",
        headers=headers,
        json=payload,
        timeout=120
    )

    result = response.json()

    if response.status_code in [200, 201]:
        post = result.get('post', result)
        return {
            "success": True,
            "post_id": post.get('_id'),
            "status": post.get('status'),
        }
    else:
        return {
            "success": False,
            "error": result.get('message', str(result)),
            "status_code": response.status_code
        }


def main():
    print("=" * 60)
    print("Pinterest Video Upload and Post")
    print("=" * 60)

    # Parse command line arguments
    target_brand = None
    if len(sys.argv) > 1:
        target_brand = sys.argv[1]
        if target_brand not in BRAND_CONFIG:
            print(f"ERROR: Unknown brand '{target_brand}'")
            print(f"Available brands: {', '.join(BRAND_CONFIG.keys())}")
            return 1

    videos_dir = Path(__file__).parent.parent / "out"
    results = {}

    # Filter brands if target specified
    brands_to_process = [target_brand] if target_brand else list(VIDEOS.keys())

    for brand in brands_to_process:
        config = VIDEOS[brand]
        brand_config = BRAND_CONFIG[brand]

        print(f"\n{'='*50}")
        print(f"Processing: {brand}")
        print(f"Display Name: {brand_config['displayName']}")
        print("=" * 50)

        # Show configuration for verification
        print(f"\n[Brand Configuration]")
        print(f"  Pinterest Account: {config['account_id']}")
        print(f"  Pinterest Board: {config['board_id']}")
        print(f"  API Key: {LATE_API_KEYS[brand][:20]}...")
        print(f"  Link: {config['link']}")

        video_path = videos_dir / config["file"]
        if not video_path.exists():
            print(f"\n  ERROR: Video not found: {video_path}")
            results[brand] = {"success": False, "error": "Video not found"}
            continue

        # Upload to Supabase
        print(f"\n[Uploading to Supabase]")
        print(f"  File: {video_path}")
        print(f"  Storage Name: {config['storage_name']}")
        try:
            video_url = upload_to_supabase(video_path, config["storage_name"])
            print(f"  Uploaded: {video_url}")
        except Exception as e:
            print(f"  ERROR: {e}")
            results[brand] = {"success": False, "error": str(e)}
            continue

        # Post to Pinterest
        print(f"\n[Posting to Pinterest]")
        print(f"  Using API Key for: {brand}")
        print(f"  Account ID: {config['account_id']}")
        print(f"  Board ID: {config['board_id']}")
        print(f"  Content Preview: {config['content'][:100]}...")

        result = post_to_pinterest(brand, video_url, config)
        results[brand] = result

        if result["success"]:
            print(f"  SUCCESS - Post ID: {result.get('post_id')}")
        else:
            print(f"  FAILED - {result.get('error')}")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    if not results:
        print("\nNo brands processed")
        return 0

    success_count = sum(1 for r in results.values() if r.get("success"))
    print(f"\nSuccessful: {success_count}/{len(results)}")

    for brand, result in results.items():
        status = "SUCCESS" if result.get("success") else "FAILED"
        display_name = BRAND_CONFIG[brand]["displayName"]
        print(f"  {brand} ({display_name}): {status}")

    return 0 if success_count == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
