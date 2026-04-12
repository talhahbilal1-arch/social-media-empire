#!/usr/bin/env python3
"""
Post the 13 product promotion pins to Pinterest via the existing Make.com pipeline.

Usage:
  1. Update GUMROAD_URLS at the top once your Gumroad listings are live
  2. Run: python3 post-product-pins.py
  3. Each pin will be rendered, uploaded to Supabase, and posted via Make.com webhook

Requirements: SUPABASE_URL, SUPABASE_KEY, PEXELS_API_KEY env vars set
"""

import os
import sys
import json
import time
import requests
import hashlib
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from video_automation.brand_slugs import BRAND_SLUG

# ─── CONFIGURE THESE ONCE GUMROAD IS LIVE ──────────────────────────────────────
GUMROAD_URLS = {
    "product_1": "https://talhahbilal.gumroad.com/l/lupkl",        # $27 AI Fitness Coach Vault
    "product_2": "https://talhahbilal.gumroad.com/l/epjybe",       # $47 Pinterest Automation Blueprint
    "product_3": "https://talhahbilal.gumroad.com/l/weaaa",        # $17 Online Coach AI Client Machine
    "lead_magnet": "https://talhahbilal.gumroad.com/l/dkschg",     # FREE 5 Prompts Lead Magnet
}

# ─── MAKE.COM WEBHOOK URLS ──────────────────────────────────────────────────────
MAKE_WEBHOOKS = {
    "fitness": os.getenv("MAKE_WEBHOOK_FITNESS", ""),
    "deals": os.getenv("MAKE_WEBHOOK_DEALS", ""),
    "menopause": os.getenv("MAKE_WEBHOOK_MENOPAUSE", ""),
}

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# ─── 13 PRODUCT PINS ──────────────────────────────────────────────────────────
PRODUCT_PINS = [
    # PRODUCT 1 PINS
    {
        "brand": "fitness",
        "title": "5 Fitness Prompts Men Over 35 Actually Need (Most Miss #3)",
        "description": "Men over 35 fitness isn't the same game as it was at 22. The training, nutrition, and recovery rules change — and most AI fitness advice doesn't account for it. These 5 prompts were written by an ISSA CPT specifically for this age group. Copy, paste, and get a real program in minutes. Save this for your next training reset. #fitover35 #menshealth #aicoach #fitnesscoach #chatgptprompts #workoutover35",
        "image_query": "athletic man over 40 strength training gym barbell focused",
        "destination_url": "product_1",
        "board": "Men's Fitness Over 35",
    },
    {
        "brand": "fitness",
        "title": "Stop Writing Programs From Scratch — Use These 5 AI Prompts",
        "description": "Fitness coaches: writing a new training program shouldn't take 2 hours. These prompts generate a complete 4-8 week program with sets, reps, progression, and deload week built in — in minutes. Written specifically for the men over 35 market. Grab the free version below. Save this for when your next client program is due. #personaltrainer #fitnesscoach #aitools #chatgpt #coachingbusiness #fitnessbusiness",
        "image_query": "personal trainer man reviewing training plan clipboard gym",
        "destination_url": "lead_magnet",
        "board": "Fitness Coach Business",
    },
    {
        "brand": "fitness",
        "title": "The Testosterone Protocol Men Over 35 Should Know (AI Prompts)",
        "description": "Testosterone peaks in your 20s. By 35, natural decline has started — and most 'fitness advice' still assumes you're 25. These AI prompts are built around the real hormonal environment of men over 35: recovery time, cortisol, sleep, and natural optimization strategies. 8 hormone health prompts in the full vault. #testosterone #fitover35 #menshealth #hormonehealth #naturaltest #fitnessafter35",
        "image_query": "man over 35 healthy lifestyle morning routine fitness",
        "destination_url": "product_1",
        "board": "Men's Fitness Over 35",
    },
    {
        "brand": "fitness",
        "title": "I Used to Spend 3 Hours on Client Programs. Now It Takes 20 Min",
        "description": "Not exaggerating. Writing a complete training program used to take me most of my Sunday. With these AI prompts, I input the client's details and get back a full program with periodization, exercise selection, and deload schedule in minutes. Still review it. Still customize it. But the starting point is done. 75 prompts for fitness coaches who work with men over 35. Link in bio. #fitnesscoach #onlinecoach #personaltrainer #aitools #coachingbusiness",
        "image_query": "fitness coach man laptop notebook planning workout programs",
        "destination_url": "product_1",
        "board": "Fitness Coach Business",
    },
    {
        "brand": "fitness",
        "title": "Why Generic AI Fitness Prompts Don't Work After 35 (Here's What Does)",
        "description": "Tried asking ChatGPT for a workout program and got back something that looks like it was written for a 22-year-old? That's because most fitness prompts ignore the specific considerations of men over 35: joint health, recovery capacity, hormone levels, and the training modifications that actually matter. These 75 prompts are written for this specific context. No generic advice. #fitover35 #menshealth #chatgptfitness #aicoach #workoutover35 #fitnessafter35",
        "image_query": "athletic middle-aged man gym determined expression weights",
        "destination_url": "product_1",
        "board": "Men's Fitness Over 35",
    },
    # PRODUCT 2 PINS
    {
        "brand": "fitness",
        "title": "How This Pinterest System Posts 15 Pins/Day Without Touching It",
        "description": "GitHub Actions + Claude AI + Make.com + Pexels. This is the actual stack running a live Pinterest automation system that posts 15 pins daily across 3 brands, generates SEO articles, and deploys them to websites automatically. Total cost: ~$20-40/month in Claude API. Everything else is free. The full blueprint is documented and available. Link in profile. #pinterestmarketing #contentautomation #aimarketing #makecom #pinterestgrowth",
        "image_query": "person at computer multiple browser tabs social media dashboard",
        "destination_url": "product_2",
        "board": "Pinterest Marketing Tips",
    },
    {
        "brand": "fitness",
        "title": "5 Reasons Your Pinterest Isn't Growing (And the Automation Fix)",
        "description": "Most people post inconsistently, use weak titles, ignore SEO, never test what works, and give up after 30 days. This automation system fixes all five: posts daily, uses curiosity-gap titles, front-loads keywords, tracks what performs, and runs forever. Built on GitHub Actions, Claude API, and Make.com — all free except the API. Full blueprint below. #pinterestautomation #pinterestmarketing #contentcreator #digitalmarketing #aitools",
        "image_query": "pinterest app phone screen analytics marketing data",
        "destination_url": "product_2",
        "board": "Pinterest Marketing Tips",
    },
    {
        "brand": "fitness",
        "title": "45 Pinterest Title Formulas That Actually Get Clicks (Documented)",
        "description": "After running a Pinterest automation system across 3 brands, here are the hook frameworks that consistently outperform: curiosity gap, specific listicle, personal story, and data-backed claims. Generic titles kill your reach. These 45 formulas are organized by goal — max clicks vs. max saves vs. trust building. Part of the full Pinterest Automation Blueprint. Save this. #pinteresttips #pinterestmarketing #contentmarketing #pinterestgrowth #socialmediatips",
        "image_query": "content creator woman laptop notebook writing social media strategy",
        "destination_url": "product_2",
        "board": "Pinterest Marketing Tips",
    },
    {
        "brand": "fitness",
        "title": "The Free Pinterest Automation Stack Nobody Talks About",
        "description": "GitHub Actions (free) + Claude API ($20/mo) + Pexels API (free) + Make.com (free) + Supabase (free) + Vercel (free) = a system that posts 15 pins/day, writes SEO articles, and deploys them to your website — automatically. Most automation courses sell you on expensive tools. This uses the free tier of everything. Blueprint linked in profile. Includes all prompts, code, and setup guides. #pinterestautomation #makecom #claudeai #githubactions #contentautomation",
        "image_query": "developer programmer laptop code terminal screen night",
        "destination_url": "product_2",
        "board": "AI Tools & Automation",
    },
    # PRODUCT 3 PINS
    {
        "brand": "fitness",
        "title": "5 Scripts Every Online Coach Needs (Stop Writing From Scratch)",
        "description": "The DM inquiry reply you didn't know how to start. The proposal email you rewrote 3 times. The 'I need to think about it' response that made you panic. All of these have scripts. 50 AI prompts and word-for-word conversation scripts for every stage of coaching: discovery, sales, onboarding, retention, testimonials. Coaches — save this. #onlinecoach #coachingbusiness #fitnessbusiness #clientacquisition #businesscoach",
        "image_query": "woman business owner laptop coffee professional workspace",
        "destination_url": "product_3",
        "board": "Fitness Coach Business",
    },
    {
        "brand": "fitness",
        "title": "Online Coaches: Save 10 Hours a Week Using These AI Prompts",
        "description": "Writing every caption, email, follow-up, and proposal from scratch is why coaches burn out. These 50 prompts handle the writing side of running a coaching business. You still do the real work — showing up for clients, delivering results. AI handles the inbox. Save this if you're tired of staring at blank screens. #coachingbusiness #onlinecoach #aitools #businesstools #chatgptforcoaches",
        "image_query": "productive woman entrepreneur working home office focused",
        "destination_url": "product_3",
        "board": "Fitness Coach Business",
    },
    {
        "brand": "fitness",
        "title": "The Exact Discovery Call Script That Converts Without Pressure",
        "description": "Most coaches either pitch too hard (creepy) or not hard enough (nothing happens). This discovery call script does one thing: helps you understand the prospect's situation so deeply that the right decision becomes obvious to both of you. Word-for-word opening, diagnostic questions, price presentation, 5 objection scripts. Part of the Online Coach AI Client Machine. Link in profile. #discoverycall #coachingsales #clientacquisition #onlinecoach #salestips",
        "image_query": "professional woman coaching video call laptop home office",
        "destination_url": "product_3",
        "board": "Fitness Coach Business",
    },
    # LEAD MAGNET
    {
        "brand": "fitness",
        "title": "FREE: 5 AI Prompts That Save Fitness Coaches 5 Hours a Week",
        "description": "Grab 5 free copy-paste prompts from the AI Fitness Coach Vault. Includes: Instagram DM reply template · Week of content in 10 min · 4-week client program builder · Check-in email generator · Pinterest pin titles. No email required. Instant download. Link in bio. These are taken from the full 75-prompt vault — giving you the best ones first. #fitnesscoach #freetools #aitools #personaltrainer #chatgptprompts",
        "image_query": "fitness coach woman smiling laptop free download digital product",
        "destination_url": "lead_magnet",
        "board": "Fitness Coach Business",
    },
]


def get_pexels_image(query, used_ids=None):
    """Fetch a unique Pexels image for the given query."""
    if not PEXELS_API_KEY:
        return None, None

    if used_ids is None:
        used_ids = set()

    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/v1/search"
    params = {"query": query, "per_page": 20, "orientation": "portrait"}

    resp = requests.get(url, headers=headers, params=params, timeout=15)
    if resp.status_code != 200:
        return None, None

    data = resp.json()
    photos = data.get("photos", [])
    for photo in photos:
        if photo["id"] not in used_ids:
            used_ids.add(photo["id"])
            return photo["src"]["large2x"], photo["id"]

    return None, None


def render_pin_image(title, pexels_url):
    """Download Pexels image and render PIL overlay."""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "video_automation"))
        from pin_image_generator import render_pin_image as _render
        return _render(title, pexels_url, style="gradient")
    except Exception as e:
        print(f"    PIL render failed: {e}")
        return None


def upload_to_supabase(img_bytes, filename):
    """Upload image bytes to Supabase Storage."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    bucket_url = f"{SUPABASE_URL}/storage/v1/object/pin-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    resp = requests.post(bucket_url, headers=headers, data=img_bytes, timeout=30)
    if resp.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/pin-images/{filename}"
        return public_url
    else:
        print(f"    Upload failed: {resp.status_code} {resp.text[:200]}")
        return None


def post_pin(pin_data, image_url, destination_url):
    """Post pin via Make.com webhook."""
    brand = pin_data["brand"]
    webhook_url = MAKE_WEBHOOKS.get(brand)
    if not webhook_url:
        print(f"    No webhook for brand: {brand}")
        return False

    payload = {
        "brand": BRAND_SLUG.get(brand, brand),
        "title": pin_data["title"],
        "description": pin_data["description"],
        "image_url": image_url,
        "destination_url": destination_url,
        "board_id": "",  # Make.com scenario uses board name
        "board": pin_data["board"],
    }

    resp = requests.post(webhook_url, json=payload, timeout=15)
    if resp.status_code in (200, 202):
        print(f"    ✓ Posted: {pin_data['title'][:60]}...")
        return True
    else:
        print(f"    ✗ Failed ({resp.status_code}): {resp.text[:100]}")
        return False


def main():
    # Validate URLs
    placeholder_count = sum(1 for u in GUMROAD_URLS.values() if "YOUR-GUMROAD-SLUG" in u)
    if placeholder_count > 0:
        print(f"⚠️  {placeholder_count} Gumroad URL(s) are still placeholders.")
        print("   Update the GUMROAD_URLS dict at the top of this file before posting.")
        print("   Continuing with placeholder URLs for testing...\n")

    used_pexels_ids = set()
    posted = 0
    failed = 0

    for i, pin in enumerate(PRODUCT_PINS, 1):
        print(f"\n[{i}/13] {pin['title'][:65]}...")

        dest_url = GUMROAD_URLS.get(pin["destination_url"], "#")

        # 1. Get Pexels image
        pexels_url, pexels_id = get_pexels_image(pin["image_query"], used_pexels_ids)
        if not pexels_url:
            print(f"    No Pexels image found — skipping")
            failed += 1
            continue

        print(f"    Pexels image: {pexels_url[:60]}...")

        # 2. Render PIL overlay
        img_bytes = render_pin_image(pin["title"], pexels_url)
        if not img_bytes:
            print(f"    PIL render failed — posting without overlay")
            # Download raw image as fallback
            img_resp = requests.get(pexels_url, timeout=15)
            img_bytes = img_resp.content if img_resp.status_code == 200 else None

        if not img_bytes:
            failed += 1
            continue

        # 3. Upload to Supabase
        filename = f"product-pin-{hashlib.md5(pin['title'].encode()).hexdigest()[:8]}.jpg"
        image_url = upload_to_supabase(img_bytes, filename)
        if not image_url:
            print(f"    Supabase upload failed — skipping")
            failed += 1
            continue

        print(f"    Uploaded: {filename}")

        # 4. Post via Make.com
        success = post_pin(pin, image_url, dest_url)
        if success:
            posted += 1
        else:
            failed += 1

        # Rate limit between pins
        time.sleep(2)

    print(f"\n{'='*50}")
    print(f"✅ Posted: {posted}/13 pins")
    print(f"❌ Failed: {failed}/13 pins")


if __name__ == "__main__":
    main()
