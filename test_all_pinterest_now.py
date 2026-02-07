#!/usr/bin/env python3
"""Quick test to post a video to all 3 Pinterest accounts."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.clients.late_api import LateAPIClient

# Sample video URL (Google sample video - reliable and public)
VIDEO_URL = "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4"

# All 3 accounts to test
ACCOUNTS = [
    {
        "brand": "daily_deal_darling",
        "api_key": "sk_191f58baa59a897d5836822d023958b4b08dc50b942c42608f54f35db5e51f26",
        "account_id": "697ba20193a320156c4220b4",
        "board_id": "874683627569021288",
        "title": "Must-Have Kitchen Gadget for 2026!",
        "description": "This genius kitchen find is a total game-changer! Makes cooking so much easier. Link in bio for details!\n\n#amazonfinds #kitchenhacks #deals #homegadgets #cooking",
        "link": "https://dailydealdarling.com"
    },
    {
        "brand": "fitnessmadeasy", 
        "api_key": "sk_8e65dd394bf9de906f3a72ba04c608dd0ca6c3ff49f6b3490a035dfcd268f4bd",
        "account_id": "697bb4b893a320156c4221ab",
        "board_id": "756745612325868912",
        "title": "5-Minute Ab Workout - No Equipment Needed!",
        "description": "Quick and effective core workout you can do anywhere! Perfect for busy days. Save this for later!\n\n#fitness #abworkout #homeworkout #fitover35 #exercise",
        "link": "https://fitnessmadeasy.com"
    },
    {
        "brand": "menopause_planner",
        "api_key": "sk_37d9439119d55bdaab7316707b2dda03ad616752ae9b4ee720764c944dac39cb",
        "account_id": "697c329393a320156c422e6d",
        "board_id": "1076993767079887530",
        "title": "3 Natural Ways to Beat Hot Flashes",
        "description": "Struggling with hot flashes? These natural remedies can help! Save this for when you need relief.\n\n#menopause #hotflashes #wellness #womenover50 #naturalremedies",
        "link": "https://www.etsy.com/listing/4435219468/menopause-wellness-planner-bundle"
    }
]

def post_to_account(account):
    """Post a video to a single Pinterest account."""
    print(f"\n{'='*60}")
    print(f"Posting to: {account['brand']}")
    print(f"  Title: {account['title']}")
    print(f"  Board: {account['board_id']}")
    print(f"{'='*60}")
    
    try:
        client = LateAPIClient(api_key=account['api_key'])
        
        result = client.create_pinterest_video_pin(
            video_url=VIDEO_URL,
            title=account['title'],
            description=account['description'],
            link=account['link'],
            board_id=account['board_id'],
            publish_now=True,
            account_id=account['account_id']
        )
        
        if result.success:
            print(f"  ✅ SUCCESS!")
            print(f"  Post ID: {result.post_id}")
            print(f"  URL: {result.platform_post_url}")
            return {"success": True, "url": result.platform_post_url, "brand": account['brand']}
        else:
            print(f"  ❌ FAILED: {result.error}")
            return {"success": False, "error": result.error, "brand": account['brand']}
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return {"success": False, "error": str(e), "brand": account['brand']}

def main():
    print("="*60)
    print("PINTEREST LIVE TEST - Posting to ALL 3 accounts")
    print("="*60)
    print(f"Video: {VIDEO_URL}")
    
    results = []
    
    for account in ACCOUNTS:
        result = post_to_account(account)
        results.append(result)
        
        # Small delay between posts
        if account != ACCOUNTS[-1]:
            print("\n  Waiting 3 seconds...")
            time.sleep(3)
    
    # Summary
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    success_count = 0
    for r in results:
        if r['success']:
            print(f"  ✅ {r['brand']}: {r['url']}")
            success_count += 1
        else:
            print(f"  ❌ {r['brand']}: {r['error']}")
    
    print(f"\n  Total: {success_count}/3 successful")
    print("="*60)
    
    return 0 if success_count == 3 else 1

if __name__ == "__main__":
    sys.exit(main())
