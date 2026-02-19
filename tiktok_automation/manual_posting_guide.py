"""Manual TikTok Posting Helper - formats videos for manual posting when API unavailable.

When TIKTOK_ACCESS_TOKEN is not set, this script formats video_ready items
for manual posting and provides instructions.

Usage:
    python3 tiktok_automation/manual_posting_guide.py [--output posting_batch.json]
"""

import os
import sys
import json
import logging
import argparse
import requests
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════


def _supabase_creds() -> tuple:
    """Return (url, key) for the TikTok Supabase project."""
    url = os.environ.get("SUPABASE_TIKTOK_URL") or os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_TIKTOK_KEY") or os.environ.get("SUPABASE_KEY", "")
    return url, key


def fetch_video_ready_items(limit: int = 10) -> list:
    """Fetch items with status='video_ready' from tiktok_queue."""
    supabase_url, supabase_key = _supabase_creds()

    response = requests.get(
        f"{supabase_url}/rest/v1/tiktok_queue",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
        },
        params={
            "status": "eq.video_ready",
            "order": "created_at.asc",
            "limit": limit,
        },
    )
    response.raise_for_status()
    items = response.json()
    logger.info(f"Fetched {len(items)} video_ready items")
    return items


def format_for_manual_posting(items: list) -> list:
    """Format items for manual TikTok posting."""
    formatted = []

    for item in items:
        # Build the caption with hashtags
        full_caption = f"{item.get('caption', '')}\n\n{' '.join(item.get('hashtags', []))}"

        # Build affiliate link if product available
        affiliate_link = None
        products = item.get("affiliate_products", [])
        if products and len(products) > 0:
            product = products[0]
            asin = product.get("asin", "")
            amazon_tag = item.get("amazon_tag", "fitnessquick-20")
            if asin:
                affiliate_link = f"https://www.amazon.com/dp/{asin}?tag={amazon_tag}"

        formatted_item = {
            "id": item.get("id"),
            "topic": item.get("topic"),
            "video_url": item.get("video_url"),
            "audio_url": item.get("audio_url"),
            "caption": full_caption[:2200],  # TikTok caption limit
            "hashtags": item.get("hashtags", []),
            "affiliate_products": item.get("affiliate_products", []),
            "affiliate_link": affiliate_link,
            "created_at": item.get("created_at"),
            "posting_instructions": [
                "1. Open TikTok app and create a new post",
                "2. Upload the video from video_url or download it first",
                "3. Copy and paste the caption text",
                "4. Set privacy to 'Public'",
                "5. Click post",
                f"6. After posting, copy the TikTok URL and update status in Supabase"
            ]
        }

        formatted.append(formatted_item)

    return formatted


def update_queue_item_scheduled(item_id: str) -> bool:
    """Update item to status='scheduled' to mark as queued for manual posting."""
    supabase_url, supabase_key = _supabase_creds()

    payload = {
        "status": "scheduled",
        "updated_at": datetime.utcnow().isoformat(),
    }

    try:
        response = requests.patch(
            f"{supabase_url}/rest/v1/tiktok_queue?id=eq.{item_id}",
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        logger.info(f"Marked item {item_id} as scheduled")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to update Supabase: {e}")
        return False


def generate_posting_batch(output_file: str, limit: int = 10) -> bool:
    """Generate a batch file with formatted videos for manual posting."""
    logger.info(f"Generating manual posting batch (max {limit} videos)...")

    try:
        items = fetch_video_ready_items(limit=limit)
    except Exception as e:
        logger.error(f"Failed to fetch items: {e}")
        return False

    if not items:
        logger.info("No video_ready items to format")
        return True

    formatted_items = format_for_manual_posting(items)

    # Generate batch file
    batch_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "total_items": len(formatted_items),
        "instructions": [
            "This file contains TikTok videos ready for manual posting.",
            "1. Review each video's caption and hashtags",
            "2. Upload video to TikTok using the video_url or audio_url",
            "3. Set caption and privacy settings as specified",
            "4. After posting, update the item status in Supabase to 'posted'",
            "5. Store TikTok post URL for reference"
        ],
        "videos": formatted_items,
    }

    try:
        with open(output_file, "w") as f:
            json.dump(batch_data, f, indent=2)
        logger.info(f"Batch file saved to {output_file}")

        # Mark items as scheduled
        for item in formatted_items:
            update_queue_item_scheduled(item["id"])

        return True

    except IOError as e:
        logger.error(f"Failed to write batch file: {e}")
        return False


def print_posting_summary(items: list) -> None:
    """Print summary of videos ready for posting."""
    print("\n" + "=" * 70)
    print("TikTok Manual Posting Summary")
    print("=" * 70)
    print(f"Total videos ready: {len(items)}\n")

    for i, item in enumerate(items, 1):
        print(f"Video {i}: {item['topic'][:50]}")
        print(f"  Video URL: {item['video_url'][:60]}...")
        print(f"  Caption: {item['caption'][:80]}...")
        print(f"  Hashtags: {' '.join(item['hashtags'][:3])} ...")
        if item.get("affiliate_link"):
            print(f"  Affiliate Link: {item['affiliate_link'][:60]}...")
        print()

    print("=" * 70)
    print("To post these videos manually:")
    print("  1. Use the generated posting_batch.json file")
    print("  2. Or check Supabase tiktok_queue table directly")
    print("  3. After posting, update status to 'posted' in Supabase")
    print("=" * 70 + "\n")


def main():
    """Generate manual posting batch and display summary."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Format TikTok videos for manual posting"
    )
    parser.add_argument(
        "--output",
        default="tiktok_posting_batch.json",
        help="Output file for batch data",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=10,
        help="Max videos to include",
    )
    parser.add_argument(
        "--skip-file",
        action="store_true",
        help="Don't generate file, just display summary",
    )
    args = parser.parse_args()

    # Validate Supabase
    supabase_url, supabase_key = _supabase_creds()
    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_TIKTOK_URL and SUPABASE_TIKTOK_KEY must be set")
        sys.exit(1)

    # Fetch and format items
    try:
        items = fetch_video_ready_items(limit=args.max)
    except Exception as e:
        logger.error(f"Failed to fetch items: {e}")
        sys.exit(1)

    if not items:
        logger.info("No video_ready items found")
        return

    # Display summary
    formatted_items = format_for_manual_posting(items)
    print_posting_summary(formatted_items)

    # Generate batch file
    if not args.skip_file:
        if generate_posting_batch(args.output, limit=args.max):
            logger.info(f"✓ Batch file generated: {args.output}")
        else:
            logger.error("Failed to generate batch file")
            sys.exit(1)


if __name__ == "__main__":
    main()
