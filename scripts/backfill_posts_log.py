#!/usr/bin/env python3
"""
Backfill posts_log table from content_bank and videos tables.

This script finds content that was marked as 'posted' but doesn't have
corresponding entries in posts_log, and creates those entries.

Usage:
    python scripts/backfill_posts_log.py

Requires:
    SUPABASE_URL and SUPABASE_KEY environment variables
"""
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient


def backfill_posts_log():
    """Backfill posts_log from content_bank items marked as posted."""

    db = SupabaseClient()

    print("=" * 60)
    print("POSTS_LOG BACKFILL SCRIPT")
    print("=" * 60)

    # Get current posts_log count
    current_posts = db.client.table('posts_log').select('id', count='exact').execute()
    print(f"\nCurrent posts_log entries: {current_posts.count}")

    # Get all brands
    brands = db.get_active_brands()
    print(f"Active brands: {len(brands)}")

    total_backfilled = 0

    for brand in brands:
        brand_id = brand['id']
        brand_name = brand['name']
        print(f"\n--- Processing: {brand_name} ---")

        # Find content marked as posted that's not in posts_log
        # We use content_bank.status = 'posted' as indicator
        posted_content = db.client.table('content_bank')\
            .select('id, title, content_type, updated_at')\
            .eq('brand_id', brand_id)\
            .eq('status', 'posted')\
            .execute()

        if not posted_content.data:
            print(f"  No posted content found for {brand_name}")
            continue

        print(f"  Found {len(posted_content.data)} posted content items")

        # Check which ones are already in posts_log
        for content in posted_content.data:
            content_id = content['id']

            # Check if already logged
            existing = db.client.table('posts_log')\
                .select('id')\
                .eq('content_id', content_id)\
                .execute()

            if existing.data:
                # Already logged, skip
                continue

            # Determine platform based on content type
            content_type = content.get('content_type', 'pin')
            if content_type in ['pin', 'carousel']:
                platform = 'pinterest'
            elif content_type in ['short']:
                platform = 'youtube'
            elif content_type in ['reel']:
                platform = 'instagram'
            elif content_type in ['video']:
                platform = 'tiktok'
            else:
                platform = 'pinterest'  # Default

            # Create posts_log entry
            post_record = {
                'content_id': content_id,
                'brand_id': brand_id,
                'platform': platform,
                'post_type': content_type,
                'status': 'posted',
                'posted_at': content.get('updated_at', datetime.utcnow().isoformat())
            }

            try:
                db.client.table('posts_log').insert(post_record).execute()
                total_backfilled += 1
                print(f"  + Backfilled: {content['title'][:40]}... ({platform})")
            except Exception as e:
                print(f"  ! Error backfilling {content_id}: {e}")

    # Final count
    final_posts = db.client.table('posts_log').select('id', count='exact').execute()

    print("\n" + "=" * 60)
    print("BACKFILL COMPLETE")
    print("=" * 60)
    print(f"Posts before: {current_posts.count}")
    print(f"Posts after:  {final_posts.count}")
    print(f"Backfilled:   {total_backfilled}")

    return total_backfilled


def show_posts_log_summary():
    """Show summary of posts_log table."""

    db = SupabaseClient()

    print("\n" + "=" * 60)
    print("POSTS_LOG SUMMARY")
    print("=" * 60)

    # Count by platform
    posts = db.client.table('posts_log')\
        .select('platform, status')\
        .execute()

    if not posts.data:
        print("posts_log is EMPTY")
        return

    # Group by platform
    by_platform = {}
    by_status = {}
    for post in posts.data:
        platform = post.get('platform', 'unknown')
        status = post.get('status', 'unknown')
        by_platform[platform] = by_platform.get(platform, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1

    print("\nBy Platform:")
    for platform, count in sorted(by_platform.items()):
        print(f"  {platform}: {count}")

    print("\nBy Status:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")

    # Recent posts
    recent = db.client.table('posts_log')\
        .select('platform, status, posted_at')\
        .order('posted_at', desc=True)\
        .limit(5)\
        .execute()

    if recent.data:
        print("\nMost Recent Posts:")
        for post in recent.data:
            print(f"  {post.get('posted_at', 'N/A')[:19]} | {post.get('platform')} | {post.get('status')}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Backfill posts_log table')
    parser.add_argument('--summary', action='store_true', help='Just show summary, no backfill')
    args = parser.parse_args()

    if args.summary:
        show_posts_log_summary()
    else:
        backfill_posts_log()
        show_posts_log_summary()
