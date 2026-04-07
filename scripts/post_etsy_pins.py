#!/usr/bin/env python3
"""Post Etsy product pins (ADHD Planner + Night Shift Nurse Planner) to Pinterest.

Posts to DailyDealDarling Pinterest account (Make.com connection 6738173) on
the "Self Care Products Worth It" and "Gift Ideas" boards.

Usage:
  1. Update ETSY_URLS in video_automation/etsy_product_pins.py with real Etsy URLs
  2. Set env vars: SUPABASE_URL, SUPABASE_KEY, PEXELS_API_KEY, MAKE_WEBHOOK_DEALS
  3. Run: python3 scripts/post_etsy_pins.py
     Or with --limit N to post only N pins (default: 2 for daily scheduling)
     Or with --all to post all 10 pins at once

Requires: SUPABASE_URL, SUPABASE_KEY, PEXELS_API_KEY, MAKE_WEBHOOK_DEALS env vars.
"""

import os
import sys
import time
import hashlib
import argparse
import requests
from pathlib import Path

# Add repo root to path so video_automation imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from video_automation.etsy_product_pins import ETSY_PIN_TEMPLATES, ETSY_URLS
from video_automation.pinterest_boards import PINTEREST_BOARDS

# ─── ENV VARS ────────────────────────────────────────────────────────────────
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
MAKE_WEBHOOK_DEALS = os.getenv("MAKE_WEBHOOK_DEALS", "")

# Make.com brand name for DailyDealDarling routing
BRAND_NAME = "daily-deal-darling"


def get_pexels_image(query, used_ids=None):
    """Fetch a unique portrait Pexels image for the given query."""
    if not PEXELS_API_KEY:
        print("    ⚠ PEXELS_API_KEY not set")
        return None, None

    if used_ids is None:
        used_ids = set()

    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 20, "orientation": "portrait"}
    resp = requests.get(
        "https://api.pexels.com/v1/search", headers=headers, params=params, timeout=15
    )
    if resp.status_code != 200:
        print(f"    Pexels error: {resp.status_code}")
        return None, None

    for photo in resp.json().get("photos", []):
        if photo["id"] not in used_ids:
            used_ids.add(photo["id"])
            return photo["src"]["large2x"], photo["id"]

    return None, None


def render_pin_image(title, pexels_url):
    """Render PIL overlay on the Pexels image using the existing generator."""
    try:
        from video_automation.pin_image_generator import render_pin_image as _render
        return _render(title, pexels_url, style="gradient")
    except Exception as e:
        print(f"    PIL render failed: {e}")
        return None


def upload_to_supabase(img_bytes, filename):
    """Upload image bytes to Supabase Storage pin-images bucket."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("    ⚠ Supabase env vars not set")
        return None

    url = f"{SUPABASE_URL}/storage/v1/object/pin-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    resp = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if resp.status_code in (200, 201):
        return f"{SUPABASE_URL}/storage/v1/object/public/pin-images/{filename}"
    print(f"    Supabase upload failed: {resp.status_code} {resp.text[:100]}")
    return None


def get_board_id(board_name):
    """Resolve board name to DailyDealDarling board ID."""
    boards = PINTEREST_BOARDS.get("deals", {})
    # Exact match first
    if board_name in boards:
        return boards[board_name]
    # Fuzzy: find first board whose name contains the search term
    board_name_lower = board_name.lower()
    for name, board_id in boards.items():
        if board_name_lower in name.lower() or name.lower() in board_name_lower:
            return board_id
    # Fallback to default deals board
    from video_automation.pinterest_boards import DEFAULT_BOARDS
    return DEFAULT_BOARDS.get("deals", "")


def post_pin(pin, image_url, destination_url):
    """POST pin payload to Make.com deals webhook."""
    if not MAKE_WEBHOOK_DEALS:
        print("    ⚠ MAKE_WEBHOOK_DEALS not set — skipping post")
        return False

    board_id = get_board_id(pin["board"])
    payload = {
        "brand": BRAND_NAME,
        "title": pin["title"],
        "description": pin["description"],
        "image_url": image_url,
        "destination_url": destination_url,
        "board_id": board_id,
        "board": pin["board"],
    }

    resp = requests.post(MAKE_WEBHOOK_DEALS, json=payload, timeout=15)
    if resp.status_code in (200, 202):
        print(f"    ✓ Posted to Pinterest")
        return True
    print(f"    ✗ Webhook failed ({resp.status_code}): {resp.text[:100]}")
    return False


def select_pins(limit):
    """Select up to `limit` pins using hour-based rotation so each run is different."""
    from datetime import datetime, timezone
    hour = datetime.now(timezone.utc).hour
    total = len(ETSY_PIN_TEMPLATES)
    # Pick starting index based on current hour, wrap around
    start = (hour * limit) % total
    selected = []
    for i in range(limit):
        selected.append(ETSY_PIN_TEMPLATES[(start + i) % total])
    return selected


def main():
    parser = argparse.ArgumentParser(description="Post Etsy product pins to Pinterest")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--limit", type=int, default=2, help="Pins to post this run (default: 2)")
    group.add_argument("--all", action="store_true", help="Post all 10 pins")
    args = parser.parse_args()

    pins_to_post = ETSY_PIN_TEMPLATES if args.all else select_pins(args.limit)
    total = len(pins_to_post)

    # Warn if Etsy URLs are still placeholders
    placeholder_count = sum(1 for u in ETSY_URLS.values() if "YOUR-" in u)
    if placeholder_count:
        print(f"⚠  {placeholder_count} Etsy URL(s) are still placeholders.")
        print("   Update ETSY_URLS in video_automation/etsy_product_pins.py with real URLs.\n")

    used_pexels_ids = set()
    posted = 0
    failed = 0

    for i, pin in enumerate(pins_to_post, 1):
        product_key = pin["product"]
        destination_url = ETSY_URLS.get(product_key, "#")
        print(f"\n[{i}/{total}] {pin['title'][:70]}")
        print(f"    Product: {product_key} | Board: {pin['board']}")

        # 1. Fetch Pexels image
        pexels_url, pexels_id = get_pexels_image(pin["image_query"], used_pexels_ids)
        if not pexels_url:
            print("    No Pexels image found — skipping")
            failed += 1
            continue
        print(f"    Pexels: {pexels_url[:60]}...")

        # 2. Render PIL overlay
        img_bytes = render_pin_image(pin["title"], pexels_url)
        if not img_bytes:
            print("    PIL failed — using raw Pexels image")
            raw = requests.get(pexels_url, timeout=15)
            img_bytes = raw.content if raw.status_code == 200 else None
        if not img_bytes:
            failed += 1
            continue

        # 3. Upload to Supabase
        slug = hashlib.md5(pin["title"].encode()).hexdigest()[:8]
        filename = f"etsy-pin-{product_key}-{slug}.jpg"
        image_url = upload_to_supabase(img_bytes, filename)
        if not image_url:
            print("    Supabase upload failed — skipping")
            failed += 1
            continue
        print(f"    Uploaded: {filename}")

        # 4. Post via Make.com
        if post_pin(pin, image_url, destination_url):
            posted += 1
        else:
            failed += 1

        # Rate limit between pins
        if i < total:
            time.sleep(3)

    print(f"\n{'='*50}")
    print(f"✅ Posted: {posted}/{total} pins")
    print(f"❌ Failed: {failed}/{total} pins")

    # Exit non-zero if all pins failed (for GitHub Actions to catch)
    if posted == 0 and total > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
