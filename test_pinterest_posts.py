#!/usr/bin/env python3
"""
Test Pinterest video posting to all 3 brand accounts.

This script posts the test videos from Supabase to Pinterest using the Late API.
Run this after setting the LATE_API_KEY environment variables.

Usage:
    # Set the API keys first
    export LATE_API_KEY_2="sk_..."  # DailyDealDarling
    export LATE_API_KEY_3="sk_..."  # FitnessMadeEasy
    export LATE_API_KEY_4="sk_..."  # MenopausePlanner

    # Then run the script
    python test_pinterest_posts.py
"""

import os
import requests
import json

# Video URLs from Supabase storage
VIDEOS = {
    "daily_deal_darling": {
        "video_url": "https://bjacmhjtpkdcxngkasux.supabase.co/storage/v1/object/public/videos/daily-deal-darling.mp4",
        "api_key_env": "LATE_API_KEY_2",
        "account_id": "697ba20193a320156c4220b4",
        "board_id": "874683627569021288",
        "link": "https://dailydealdarling.com",
        "content": """Must-Have Kitchen Gadget!

This changed my morning routine forever... Saves 10 minutes every morning, under $25 on Amazon with over 50,000 5-star reviews!

Link in bio for the deal!

#amazonfinds #kitchengadgets #morningroutine #deals #dailydealdarling"""
    },
    "fitnessmadeasy": {
        "video_url": "https://bjacmhjtpkdcxngkasux.supabase.co/storage/v1/object/public/videos/fitness-made-easy.mp4",
        "api_key_env": "LATE_API_KEY_3",
        "account_id": "697bb4b893a320156c4221ab",
        "board_id": "756745612325868912",
        "link": "https://fitnessmadeasy.com",
        "content": """5-Minute Ab Workout

No equipment needed - burns belly fat fast! Perfect for beginners. Do it anywhere, anytime.

Save this for later!

#fitness #workout #abs #homeworkout #fitover35"""
    },
    "menopause_planner": {
        "video_url": "https://bjacmhjtpkdcxngkasux.supabase.co/storage/v1/object/public/videos/menopause-planner.mp4",
        "api_key_env": "LATE_API_KEY_4",
        "account_id": "697c329393a320156c422e6d",
        "board_id": "1076993767079887530",
        "link": "https://www.etsy.com/listing/4435219468/menopause-wellness-planner-bundle",
        "content": """Natural Hot Flash Relief

I wish I knew this sooner... Works in just 5 minutes, no medications needed. Doctor-approved method!

Get the full guide - link in bio!

#menopause #wellness #hotflashes #womenshealth #naturalremedy"""
    }
}


def post_to_pinterest(brand: str, config: dict) -> dict:
    """Post a video to Pinterest using Late API."""
    api_key = os.getenv(config["api_key_env"])

    if not api_key:
        return {"success": False, "error": f"Missing API key: {config['api_key_env']}"}

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
        "mediaItems": [{"type": "video", "url": config["video_url"]}]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://getlate.dev/api/v1/posts",
            headers=headers,
            json=payload,
            timeout=120
        )

        result = response.json()

        if response.status_code == 200 or response.status_code == 201:
            post = result.get('post', result)
            return {
                "success": True,
                "post_id": post.get('_id'),
                "status": post.get('status'),
                "response": result
            }
        else:
            return {
                "success": False,
                "error": result.get('message', str(result)),
                "status_code": response.status_code
            }

    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    print("=" * 60)
    print("Pinterest Video Posting Test")
    print("=" * 60)

    results = {}

    for brand, config in VIDEOS.items():
        print(f"\nPosting to {brand}...")
        print(f"  Video: {config['video_url']}")
        print(f"  Board: {config['board_id']}")

        result = post_to_pinterest(brand, config)
        results[brand] = result

        if result["success"]:
            print(f"  ✅ SUCCESS - Post ID: {result.get('post_id')}")
        else:
            print(f"  ❌ FAILED - {result.get('error')}")

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    success_count = sum(1 for r in results.values() if r["success"])
    print(f"\nSuccessful: {success_count}/{len(results)}")

    for brand, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"  {status} {brand}")

    return results


if __name__ == "__main__":
    main()
