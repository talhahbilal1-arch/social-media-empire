#!/usr/bin/env python3
"""Test script to verify Pinterest posting to enabled accounts.

This script posts a test video to each Pinterest account to verify:
1. The correct account receives the post
2. The content is appropriate for each brand
3. The multi-API-key setup works correctly

Current setup:
- fitnessmadeasy: 1uy77rvyo4c0mmr Pinterest -> "Fitness Goods" board (LATE_API_KEY_3)
- menopause_planner: TheMenopausePlanner Pinterest -> "Menopause Wellness Tips" board (LATE_API_KEY_4)
- daily_deal_darling: DISABLED (Pinterest not connected)

Usage:
    export LATE_API_KEY_3="sk_xxx..."      # Fitness Late account
    export LATE_API_KEY_4="sk_xxx..."      # Menopause Late account
    python test_pinterest_accounts.py
"""

import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from video_automation.cross_platform_poster import BRAND_PLATFORM_CONFIG
from video_automation.pinterest_idea_pins import PinterestIdeaPinCreator

# Test video URL (a public sample video)
TEST_VIDEO_URL = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"

# Brand-specific test content
TEST_CONTENT = {
    "menopause_planner": {
        "title": "5 Natural Menopause Relief Tips",
        "description": "Discover natural ways to manage menopause symptoms. These science-backed tips can help you feel better every day.",
        "hashtags": ["#menopause", "#wellness", "#womenshealth", "#naturalremedies", "#selfcare"]
    },
    "fitnessmadeasy": {
        "title": "Quick 10-Minute Morning Workout",
        "description": "Start your day right with this energizing workout routine. No equipment needed - perfect for busy mornings!",
        "hashtags": ["#fitness", "#workout", "#morningroutine", "#exercise", "#healthylifestyle"]
    },
    "daily_deal_darling": {
        "title": "Amazing Kitchen Gadget Find!",
        "description": "This affordable kitchen tool is a game-changer! Perfect for meal prep and saves so much time.",
        "hashtags": ["#amazonfinds", "#kitchengadgets", "#deals", "#homehacks", "#budgetfriendly"]
    }
}


def test_pinterest_account(brand: str, poster: PinterestIdeaPinCreator) -> dict:
    """Test posting to a specific brand's Pinterest account."""
    config = BRAND_PLATFORM_CONFIG.get(brand)
    if not config:
        return {"success": False, "error": f"Brand {brand} not found in config"}

    if not config.get("enabled", False):
        return {"success": False, "error": f"Brand {brand} is disabled"}

    content = TEST_CONTENT.get(brand)
    if not content:
        return {"success": False, "error": f"No test content for brand {brand}"}

    account_id = config.get("pinterest_account_id")
    api_key_env = config.get("late_api_key_env", "LATE_API_KEY")
    board_id = config.get("pinterest_board_id", "default")
    link_url = config.get("link_url")

    print(f"\n{'='*60}")
    print(f"Testing: {brand}")
    print(f"  Account ID: {account_id}")
    print(f"  API Key Env: {api_key_env}")
    print(f"  Board: {board_id}")
    print(f"  Title: {content['title']}")
    print(f"{'='*60}")

    # Check if API key is available
    if not os.getenv(api_key_env):
        return {"success": False, "error": f"API key not set: {api_key_env}"}

    try:
        result = poster.create_video_idea_pin(
            board_id=board_id,
            title=content["title"],
            description=f"{content['description']}\n\n{' '.join(content['hashtags'])}",
            video_url=TEST_VIDEO_URL,
            link=link_url,
            pinterest_account_id=account_id,
            api_key_env=api_key_env
        )

        return result

    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    print("="*60)
    print("Pinterest Multi-Account Test")
    print("="*60)

    # Check for API keys
    api_key_3 = os.getenv("LATE_API_KEY_3")
    api_key_4 = os.getenv("LATE_API_KEY_4")

    print(f"\nAPI Key Status:")
    print(f"  LATE_API_KEY_3 (fitness):   {'✓ Set' if api_key_3 else '✗ NOT SET'}")
    print(f"  LATE_API_KEY_4 (menopause): {'✓ Set' if api_key_4 else '✗ NOT SET'}")

    if not api_key_3 and not api_key_4:
        print("\nERROR: No API keys set. Please set LATE_API_KEY_3 and/or LATE_API_KEY_4")
        sys.exit(1)

    # Create Pinterest poster
    poster = PinterestIdeaPinCreator()

    # Test each enabled brand
    results = {}
    brands_to_test = ["menopause_planner", "fitnessmadeasy", "daily_deal_darling"]

    for brand in brands_to_test:
        result = test_pinterest_account(brand, poster)
        results[brand] = result

        if result.get("success"):
            print(f"  ✓ SUCCESS - Post ID: {result.get('id', 'N/A')}")
            if result.get("url"):
                print(f"    URL: {result.get('url')}")
        else:
            print(f"  ✗ FAILED - {result.get('error', 'Unknown error')}")

        # Wait between posts to avoid rate limiting
        if brand != brands_to_test[-1]:
            print("  Waiting 5 seconds before next test...")
            time.sleep(5)

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    success_count = sum(1 for r in results.values() if r.get("success"))
    total_count = len(results)

    for brand, result in results.items():
        status = "✓ SUCCESS" if result.get("success") else f"✗ FAILED: {result.get('error', 'Unknown')}"
        print(f"  {brand}: {status}")

    print(f"\nTotal: {success_count}/{total_count} successful")

    # Return exit code based on results
    sys.exit(0 if success_count == total_count else 1)


if __name__ == "__main__":
    main()
