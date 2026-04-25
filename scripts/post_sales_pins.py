#!/usr/bin/env python3
"""Post sales pins for all 4 Gumroad/Etsy products directly to Pinterest.

Products (direct revenue generators):
  1. AI Fitness Coach Vault ($27)     → fitover35.com/products/fitness-vault
  2. AI Coach Machine ($17)           → fitover35.com/products/coach-machine
  3. Pinterest Blueprint ($47)        → dailydealdarling.com/articles/pinterest-automation-blueprint
  4. Menopause Wellness Planner $14.99 → menopause-planner-website.vercel.app/wellness-planner

Landing pages are deployed via Vercel from the outputs/ folder (cleanUrls: true).
Pins are routed via the per-brand Make.com webhooks — same pipeline as content pins.

Usage:
  python3 scripts/post_sales_pins.py               # post all 12 pins
  python3 scripts/post_sales_pins.py --brand fitness   # one brand only
  python3 scripts/post_sales_pins.py --dry-run     # validate without posting

Required env vars:
  SUPABASE_URL, SUPABASE_KEY, PEXELS_API_KEY,
  MAKE_WEBHOOK_FITNESS, MAKE_WEBHOOK_DEALS, MAKE_WEBHOOK_MENOPAUSE
"""

import os
import sys
import time
import hashlib
import argparse
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from video_automation.brand_slugs import BRAND_SLUG
from video_automation.pinterest_boards import PINTEREST_BOARDS, DEFAULT_BOARDS

# ─── ENV VARS ─────────────────────────────────────────────────────────────────
PEXELS_API_KEY   = os.getenv("PEXELS_API_KEY", "")
SUPABASE_URL     = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY     = os.getenv("SUPABASE_KEY", "")
MAKE_WEBHOOKS = {
    "fitness":   os.getenv("MAKE_WEBHOOK_FITNESS", ""),
    "deals":     os.getenv("MAKE_WEBHOOK_DEALS", ""),
    "menopause": os.getenv("MAKE_WEBHOOK_MENOPAUSE", ""),
}

# ─── PRODUCT LANDING PAGE URLS ────────────────────────────────────────────────
PRODUCT_URLS = {
    "fitness_vault":    "https://fitover35.com/products/fitness-vault",
    "coach_machine":    "https://fitover35.com/products/coach-machine",
    "blueprint":        "https://dailydealdarling.com/articles/pinterest-automation-blueprint",
    "menopause_planner": "https://menopause-planner-website.vercel.app/wellness-planner",
}

# ─── 12 SALES PINS (3 per product) ───────────────────────────────────────────
SALES_PINS = [
    # ── AI Fitness Coach Vault ($27) — fitness brand ──────────────────────────
    {
        "brand":       "fitness",
        "product":     "fitness_vault",
        "board":       "Fitness Motivation",
        "image_query": "fitness coach man laptop workout program planning professional",
        "style":       "big_stat",
        "title":       "75 AI Prompts Built for Men Over 35 (Not 22-Year-Old Advice)",
        "description": (
            "ChatGPT gives generic fitness advice. These 75 prompts are written for "
            "the specific reality of men over 35: joint health, hormone levels, recovery "
            "capacity, and training modifications that actually matter. Written by an ISSA CPT. "
            "$27 one-time. No subscription. Instant download. Save this for your next training reset. "
            "#fitover35 #menshealth #aicoach #fitnesscoach #workoutover35 #chatgptprompts"
        ),
    },
    {
        "brand":       "fitness",
        "product":     "fitness_vault",
        "board":       "Workouts for Men Over 35",
        "image_query": "athletic man over 40 gym weights determined focused training",
        "style":       "gradient",
        "title":       "I Spent 3 Hours Writing Client Programs. Now It Takes 20 Min.",
        "description": (
            "Not exaggerating. With these 75 AI prompts, I input client details and get back "
            "a complete 8-week program with periodization, exercise selection, and deload "
            "schedule — in minutes. Still review it. Still customize it. But the starting "
            "point is done. Built specifically for the men over 35 market. Link in profile. "
            "#personaltrainer #fitnesscoach #aitools #coachingbusiness #fitnessbusiness"
        ),
    },
    {
        "brand":       "fitness",
        "product":     "fitness_vault",
        "board":       "Supplement Honest Reviews",
        "image_query": "man over 35 healthy morning routine coffee workout fitness",
        "style":       "split_layout",
        "title":       "The $27 Tool Saving Fitness Coaches 10 Hours/Week",
        "description": (
            "The AI Fitness Coach Vault: 75 copy-paste prompts for client programs, "
            "nutrition plans, check-in messages, Instagram content, and more — all optimized "
            "for men over 35. Written by an ISSA CPT. $27 one-time download. "
            "Includes 8 hormone health prompts most coaches ignore. Save this. "
            "#aicoach #fitover35 #personaltrainer #fitnesscoach #chatgptfitness"
        ),
    },

    # ── AI Coach Machine ($17) — fitness brand ────────────────────────────────
    {
        "brand":       "fitness",
        "product":     "coach_machine",
        "board":       "Fitness Motivation",
        "image_query": "online fitness coach woman laptop professional home office confident",
        "style":       "gradient",
        "title":       "The DM Script That Converts Inquiries Without Being Salesy",
        "description": (
            "Stop losing potential clients at the DM stage. This word-for-word inquiry reply "
            "script, discovery call opener, proposal email, and 5 objection scripts are all "
            "inside the AI Coach Machine. 50 AI scripts for every awkward client conversation. "
            "$17 one-time. Coaches — save this. "
            "#onlinecoach #coachingbusiness #fitnessbusiness #clientacquisition #salesscript"
        ),
    },
    {
        "brand":       "fitness",
        "product":     "coach_machine",
        "board":       "Workouts for Men Over 35",
        "image_query": "fitness coach writing emails messaging client phone professional",
        "style":       "box_dark",
        "title":       "50 AI Scripts for Every Client Conversation You've Been Avoiding",
        "description": (
            "Pricing pushback. 'I need to think about it.' Onboarding emails. "
            "Check-ins that actually get responses. Testimonial requests that don't feel awkward. "
            "All 50 word-for-word scripts for online fitness coaches. $17 one-time. "
            "Stop writing from scratch. Link in profile. "
            "#onlinecoach #aitools #coachingbusiness #personaltrainer #businesstools"
        ),
    },
    {
        "brand":       "fitness",
        "product":     "coach_machine",
        "board":       "Fat Loss After 35",
        "image_query": "entrepreneur coach productivity laptop coffee focused morning",
        "style":       "big_stat",
        "title":       "Online Coaches: Save 10 Hours a Week With These 50 AI Scripts",
        "description": (
            "Writing every caption, DM reply, proposal, and check-in from scratch is why "
            "coaches burn out. These 50 prompts handle the writing side of your coaching business. "
            "Discovery calls, retention, testimonials, upsells — all scripted. "
            "$17 one-time. The AI Coach Machine. Save this if you're tired of the blank screen. "
            "#coachingbusiness #onlinecoach #aitools #chatgptforcoaches #businesscoach"
        ),
    },

    # ── Pinterest Automation Blueprint ($47) — deals brand ────────────────────
    {
        "brand":       "deals",
        "product":     "blueprint",
        "board":       "Gift Ideas",
        "image_query": "content creator person laptop multiple tabs social media dashboard analytics",
        "style":       "big_stat",
        "title":       "How This Pinterest System Posts 15 Pins/Day Without Touching It",
        "description": (
            "GitHub Actions + Claude AI + Make.com + Pexels + Supabase + Vercel. "
            "Real cost: $20-40/month in API fees. Everything else free. "
            "Runs 3x daily, generates SEO articles, deploys to websites, posts to Pinterest — "
            "automatically. Running live across 3 brands right now. Full blueprint linked. "
            "#pinterestmarketing #contentautomation #aimarketing #makecom #pinterestgrowth"
        ),
    },
    {
        "brand":       "deals",
        "product":     "blueprint",
        "board":       "Home Organization Finds",
        "image_query": "developer programmer laptop code terminal screen organized workspace",
        "style":       "gradient",
        "title":       "The Free Pinterest Automation Stack (Only $20/Month in AI Costs)",
        "description": (
            "GitHub Actions (free) + Pexels API (free) + Supabase (free) + Make.com (free) "
            "+ Vercel (free) + Claude API (~$20/month). Result: 15 pins/day, "
            "SEO articles auto-written, deployed to Vercel, Pinterest posting handled by Make.com. "
            "Full technical blueprint with code, prompts, and setup guide. $47 one-time. "
            "#pinterestautomation #claudeai #githubactions #contentautomation #digitalmarketing"
        ),
    },
    {
        "brand":       "deals",
        "product":     "blueprint",
        "board":       "Budget Home Decor",
        "image_query": "woman content creator laptop notebook social media strategy planning",
        "style":       "split_layout",
        "title":       "45 Pinterest Hook Formulas Tested on 3 Real Brands (Get Clicks)",
        "description": (
            "Curiosity gap, specific listicles, personal story, data-backed claims — "
            "these 45 title formulas consistently outperform generic titles across fitness, "
            "lifestyle, and wellness niches. Part of the full Pinterest Automation Blueprint: "
            "the complete GitHub Actions system that generates, renders, and posts pins daily. "
            "#pinteresttips #pinterestmarketing #contentmarketing #pinterestgrowth #socialmediatips"
        ),
    },

    # ── Menopause Wellness Planner ($14.99) — menopause brand ─────────────────
    {
        "brand":       "menopause",
        "product":     "menopause_planner",
        "board":       "Menopause Symptoms & Relief",
        "image_query": "woman journaling wellness planner morning routine calm peaceful",
        "style":       "split_layout",
        "title":       "The 34-Page Planner That Finally Organized My Menopause Journey",
        "description": (
            "Track hot flashes, sleep quality, mood, weight, and triggers in one structured place. "
            "The Menopause Wellness Planner Bundle: daily symptom log, trigger tracker, "
            "hormone diet guide, and 3-month review. $14.99 on Etsy. Instant digital download. "
            "Free symptom tracker included when you visit the link. "
            "#menopausesupport #perimenopause #menopauserelief #hormonebalance #womenover45"
        ),
    },
    {
        "brand":       "menopause",
        "product":     "menopause_planner",
        "board":       "Menopause Self Care",
        "image_query": "woman over 45 healthy happy self care morning journal routine",
        "style":       "gradient",
        "title":       "Stop Guessing What's Triggering Your Hot Flashes — Track It Here",
        "description": (
            "Food, stress, sleep, and alcohol all trigger hot flashes differently for each woman. "
            "This 34-page printable planner helps you identify your personal triggers in 30 days. "
            "Daily symptom log + trigger tracker + hormone diet guide + 3-month review. "
            "$14.99. Instant Etsy download. Free tracker inside the link. "
            "#hotflashrelief #menopausetips #perimenopause #hormonehealth #menopausewellness"
        ),
    },
    {
        "brand":       "menopause",
        "product":     "menopause_planner",
        "board":       "Hormone Balance Naturally",
        "image_query": "woman wellness planner writing notebook cozy herbal tea calm",
        "style":       "box_dark",
        "title":       "Perimenopause Symptom Tracker: 30 Days to Understanding Your Body",
        "description": (
            "The first step to managing menopause is knowing your patterns. "
            "This 34-page printable tracks 12 symptoms daily so you can identify trends, "
            "triggers, and what's actually working — before you spend money on supplements. "
            "$14.99 Etsy bundle. Free symptom tracker included. Instant download. "
            "#perimenopause #menopausesymptoms #menopauseself care #womenhealth #hormonebalance"
        ),
    },
]


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def get_pexels_image(query, used_ids=None):
    """Fetch a unique portrait Pexels image."""
    if not PEXELS_API_KEY:
        print("    ⚠ PEXELS_API_KEY not set")
        return None, None
    if used_ids is None:
        used_ids = set()
    resp = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_API_KEY},
        params={"query": query, "per_page": 20, "orientation": "portrait"},
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"    Pexels error: {resp.status_code}")
        return None, None
    for photo in resp.json().get("photos", []):
        if photo["id"] not in used_ids:
            used_ids.add(photo["id"])
            return photo["src"]["large2x"], photo["id"]
    return None, None


def render_pin_image(title, pexels_url, style="gradient"):
    """Render PIL overlay on the Pexels image."""
    try:
        from video_automation.pin_image_generator import render_pin_image as _render
        return _render(title, pexels_url, style=style)
    except Exception as e:
        print(f"    PIL render failed: {e}")
        return None


def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase Storage pin-images bucket."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("    ⚠ Supabase env vars not set")
        return None
    url = f"{SUPABASE_URL}/storage/v1/object/pin-images/{filename}"
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        },
        data=img_bytes,
        timeout=30,
    )
    if resp.status_code in (200, 201):
        return f"{SUPABASE_URL}/storage/v1/object/public/pin-images/{filename}"
    print(f"    Supabase upload failed: {resp.status_code} {resp.text[:100]}")
    return None


def get_board_id(brand, board_name):
    """Resolve board name to Pinterest board ID."""
    boards = PINTEREST_BOARDS.get(brand, {})
    if board_name in boards:
        return boards[board_name]
    board_lower = board_name.lower()
    for name, bid in boards.items():
        if board_lower in name.lower() or name.lower() in board_lower:
            return bid
    return DEFAULT_BOARDS.get(brand, "")


def post_pin(pin, image_url, destination_url, dry_run=False):
    """POST pin to Make.com webhook."""
    brand = pin["brand"]
    webhook_url = MAKE_WEBHOOKS.get(brand)
    if not webhook_url:
        print(f"    ⚠ MAKE_WEBHOOK_{brand.upper()} not set — skipping")
        return False

    board_id = get_board_id(brand, pin["board"])
    payload = {
        "brand":           BRAND_SLUG.get(brand, brand),
        "brand_key":       brand,
        "title":           pin["title"],
        "description":     pin["description"],
        "image_url":       image_url,
        "destination_url": destination_url,
        "board_id":        board_id,
        "board":           pin["board"],
        "pin_type":        "sales",
    }

    if dry_run:
        print(f"    [DRY RUN] Would POST to {webhook_url[:50]}...")
        print(f"    Payload: board={pin['board']} | dest={destination_url[:60]}")
        return True

    resp = requests.post(webhook_url, json=payload, timeout=15)
    if resp.status_code in (200, 202):
        print(f"    ✓ Posted to Pinterest ({brand})")
        return True
    print(f"    ✗ Webhook failed ({resp.status_code}): {resp.text[:100]}")
    return False


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Post sales pins for all 4 products")
    parser.add_argument(
        "--brand",
        choices=["fitness", "deals", "menopause"],
        help="Only post pins for this brand",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate without posting")
    args = parser.parse_args()

    pins_to_post = [p for p in SALES_PINS if not args.brand or p["brand"] == args.brand]
    total = len(pins_to_post)

    print(f"\nPosting {total} sales pins" + (" [DRY RUN]" if args.dry_run else ""))
    print("=" * 50)

    used_pexels_ids = set()
    posted = 0
    failed = 0

    for i, pin in enumerate(pins_to_post, 1):
        dest_url = PRODUCT_URLS[pin["product"]]
        print(f"\n[{i}/{total}] {pin['title'][:65]}")
        print(f"    Brand: {pin['brand']} | Board: {pin['board']}")
        print(f"    → {dest_url}")

        # 1. Fetch Pexels image
        pexels_url, _ = get_pexels_image(pin["image_query"], used_pexels_ids)
        if not pexels_url:
            print("    No Pexels image — skipping")
            failed += 1
            continue

        # 2. Render PIL overlay
        img_bytes = render_pin_image(pin["title"], pexels_url, pin.get("style", "gradient"))
        if not img_bytes:
            print("    PIL render failed — using raw Pexels image")
            raw = requests.get(pexels_url, timeout=15)
            img_bytes = raw.content if raw.status_code == 200 else None
        if not img_bytes:
            failed += 1
            continue

        # 3. Upload to Supabase
        slug = hashlib.md5(pin["title"].encode()).hexdigest()[:8]
        filename = f"sales-pin-{pin['product']}-{slug}.jpg"
        image_url = upload_to_supabase(img_bytes, filename)
        if not image_url:
            print("    Supabase upload failed — skipping")
            failed += 1
            continue
        print(f"    Uploaded: {filename}")

        # 4. Post via Make.com
        if post_pin(pin, image_url, dest_url, dry_run=args.dry_run):
            posted += 1
        else:
            failed += 1

        if i < total:
            time.sleep(3)

    print(f"\n{'=' * 50}")
    print(f"✅ Posted: {posted}/{total}")
    print(f"❌ Failed: {failed}/{total}")

    if posted == 0 and total > 0 and not args.dry_run:
        sys.exit(1)


if __name__ == "__main__":
    main()
