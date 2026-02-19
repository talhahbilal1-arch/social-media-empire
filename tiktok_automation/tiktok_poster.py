"""TikTok Content Posting API implementation.

Posts video_ready items from tiktok_queue to TikTok via Content Posting API.
Handles TikTok API polling for async video processing.

Usage:
    python3 tiktok_automation/tiktok_poster.py [--max 5] [--dry-run]
"""

import os
import sys
import json
import logging
import requests
import time
import argparse
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

TIKTOK_API_BASE = "https://open.tiktokapis.com/v2"


def _supabase_creds() -> tuple:
    """Return (url, key) for the TikTok Supabase project."""
    url = os.environ.get("SUPABASE_TIKTOK_URL") or os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_TIKTOK_KEY") or os.environ.get("SUPABASE_KEY", "")
    return url, key


def get_tiktok_access_token() -> Optional[str]:
    """Get TikTok access token from environment."""
    return os.environ.get("TIKTOK_ACCESS_TOKEN", "")


def fetch_video_ready_items(limit: int = 5) -> list:
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
    logger.info(f"Fetched {len(items)} video_ready items from tiktok_queue")
    return items


def post_to_tiktok_api(
    access_token: str,
    video_url: str,
    caption: str,
    hashtags: list,
) -> Optional[dict]:
    """Post video to TikTok via Content Posting API (async init).

    Returns publish_id for polling, or None if failed.

    TikTok Content Posting API flow:
    1. POST /post/publish/video/init/ with video URL
    2. Poll /post/publish/status/fetch/ with publish_id
    """
    # Step 1: Initialize upload with video URL
    init_url = f"{TIKTOK_API_BASE}/post/publish/video/init/"

    # Combine caption and hashtags
    full_caption = f"{caption}\n\n{' '.join(hashtags)}"[:2200]  # TikTok limit

    payload = {
        "source_info": {
            "source": "PULL_FROM_URL",
            "video_url": video_url,
        },
        "post_info": {
            "title": full_caption,
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_comment": False,
            "disable_duet": False,
            "disable_stitch": False,
            "video_cover_timestamp_ms": 1000,
        },
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        logger.info(f"Initializing TikTok upload for video: {video_url[:60]}...")
        response = requests.post(init_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()
        if data.get("data", {}).get("publish_id"):
            publish_id = data["data"]["publish_id"]
            logger.info(f"TikTok upload initialized: publish_id={publish_id}")
            return {"publish_id": publish_id, "init_response": data}
        else:
            logger.error(f"TikTok init response missing publish_id: {data}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"TikTok API init failed: {e}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        return None


def poll_tiktok_status(access_token: str, publish_id: str, max_polls: int = 60) -> Optional[dict]:
    """Poll TikTok for upload status (up to 5 minutes with 5s intervals)."""
    status_url = f"{TIKTOK_API_BASE}/post/publish/status/fetch/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    for attempt in range(max_polls):
        try:
            logger.info(f"Polling TikTok status (attempt {attempt + 1}/{max_polls})...")
            response = requests.post(
                status_url,
                json={"publish_id": publish_id},
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            status = data.get("data", {}).get("status")

            if status == "PUBLISHED":
                logger.info(f"Video published! TikTok post ID: {data['data'].get('video_id')}")
                return data["data"]

            elif status == "PROCESSING" or status == "UPLOAD_IN_PROGRESS":
                logger.info(f"Status: {status}, waiting...")
                time.sleep(5)

            elif status == "FAILED":
                logger.error(f"TikTok upload failed: {data}")
                return None

            else:
                logger.warning(f"Unknown status: {status}")
                time.sleep(5)

        except requests.exceptions.RequestException as e:
            logger.error(f"TikTok status polling failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            if attempt < max_polls - 1:
                time.sleep(5)

    logger.error(f"Polling timeout after {max_polls} attempts (5 minutes)")
    return None


def update_queue_item_posted(item_id: str, tiktok_data: dict) -> bool:
    """Update tiktok_queue item to status='posted' with TikTok metadata."""
    supabase_url, supabase_key = _supabase_creds()

    # Extract post ID from TikTok response
    tiktok_post_id = tiktok_data.get("video_id", "")

    payload = {
        "status": "posted",
        "tiktok_post_id": tiktok_post_id,
        "posted_at": datetime.now(timezone.utc).isoformat(),
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
        logger.info(f"Updated tiktok_queue item {item_id} to posted")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to update Supabase: {e}")
        return False


def update_queue_item_failed(item_id: str, error_message: str, retry_count: int) -> bool:
    """Update tiktok_queue item to status='failed' with error details."""
    supabase_url, supabase_key = _supabase_creds()

    payload = {
        "status": "failed",
        "error_message": error_message,
        "retry_count": retry_count + 1,
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
        logger.error(f"Updated tiktok_queue item {item_id} to failed: {error_message}")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to update Supabase (failed status): {e}")
        return False


def log_posting_event(item_id: str, status: str, tiktok_post_id: Optional[str] = None) -> bool:
    """Log posting event to analytics/events table for tracking."""
    supabase_url, supabase_key = _supabase_creds()

    # Try to log to tiktok_analytics if post succeeded
    if status == "posted" and tiktok_post_id:
        payload = {
            "tiktok_queue_id": item_id,
            "tiktok_post_id": tiktok_post_id,
            "views": 0,
            "snapshot_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            response = requests.post(
                f"{supabase_url}/rest/v1/tiktok_analytics",
                headers={
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            logger.info(f"Logged posting event to tiktok_analytics for {item_id}")
            return True
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to log analytics event (non-fatal): {e}")
            return False

    return True


def process_video_ready_item(item: dict, dry_run: bool = False) -> bool:
    """Process a single video_ready item through posting."""
    item_id = item.get("id")
    topic = item.get("topic", "Unknown")
    video_url = item.get("video_url")
    caption = item.get("caption", "")
    hashtags = item.get("hashtags", [])
    retry_count = item.get("retry_count", 0)

    logger.info(f"Processing item {item_id}: {topic[:50]}...")

    if not video_url:
        logger.error(f"Item {item_id} missing video_url, marking as failed")
        update_queue_item_failed(item_id, "Missing video_url", retry_count)
        return False

    if dry_run:
        logger.info(f"DRY RUN: Would post to TikTok:")
        logger.info(f"  Video: {video_url}")
        logger.info(f"  Caption: {caption[:100]}...")
        logger.info(f"  Hashtags: {' '.join(hashtags)}")
        return True

    # Get TikTok access token
    access_token = get_tiktok_access_token()

    if not access_token:
        logger.warning(
            "TIKTOK_ACCESS_TOKEN not set. Marking item as pending for manual posting. "
            "To enable auto-posting, set TIKTOK_ACCESS_TOKEN in GitHub secrets."
        )
        logger.info(f"Item {item_id} queued for manual posting:")
        logger.info(f"  Video: {video_url}")
        logger.info(f"  Caption: {caption[:100]}...")
        return True

    # Step 1: Initialize upload
    init_result = post_to_tiktok_api(access_token, video_url, caption, hashtags)

    if not init_result:
        logger.error(f"Failed to initialize TikTok upload for {item_id}")
        update_queue_item_failed(item_id, "TikTok API init failed", retry_count)
        return False

    publish_id = init_result.get("publish_id")

    # Step 2: Poll for completion (up to 5 minutes)
    tiktok_data = poll_tiktok_status(access_token, publish_id)

    if not tiktok_data:
        logger.error(f"TikTok polling timeout or failed for {item_id}")
        update_queue_item_failed(item_id, "TikTok polling timeout", retry_count)
        return False

    # Step 3: Update Supabase to posted
    tiktok_post_id = tiktok_data.get("video_id", "")
    if update_queue_item_posted(item_id, tiktok_data):
        log_posting_event(item_id, "posted", tiktok_post_id)
        logger.info(f"Successfully posted item {item_id} to TikTok: {tiktok_post_id}")
        return True
    else:
        logger.error(f"Failed to update Supabase for posted item {item_id}")
        return False


def main():
    """Main entry point: fetch and post all video_ready items."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    parser = argparse.ArgumentParser(description="TikTok Video Poster")
    parser.add_argument("--max", type=int, default=5, help="Max videos to post per run")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually post, just log")
    args = parser.parse_args()

    logger.info("TikTok Poster starting...")

    # Validate Supabase
    supabase_url, supabase_key = _supabase_creds()
    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_TIKTOK_URL and SUPABASE_TIKTOK_KEY must be set")
        sys.exit(1)

    # Fetch ready items
    try:
        items = fetch_video_ready_items(limit=args.max)
    except Exception as e:
        logger.error(f"Failed to fetch video_ready items: {e}")
        sys.exit(1)

    if not items:
        logger.info("No video_ready items to post")
        return

    # Process each item
    success_count = 0
    failed_count = 0

    for item in items:
        try:
            if process_video_ready_item(item, dry_run=args.dry_run):
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            logger.error(f"Unexpected error processing item: {e}")
            failed_count += 1

    logger.info(f"Posting complete: {success_count} success, {failed_count} failed")

    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
