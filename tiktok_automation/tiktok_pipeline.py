"""TikTok content pipeline: Claude script -> ElevenLabs TTS -> Pexels video -> Supabase.

Generates faceless TikTok video content targeting U.S. women 25-44.
Each run produces one script with audio and matched stock video.

Usage:
    python3 tiktok_automation/tiktok_pipeline.py [--count 3] [--category beauty_hack]
"""

import anthropic
import requests
import json
import os
import sys
import logging
import argparse
import random
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

CATEGORIES = [
    "quick_workout",
    "beauty_hack",
    "wellness_tip",
    "amazon_find",
    "lifestyle_hack",
]

PEXELS_SEARCH_MAP = {
    "quick_workout": "woman workout exercise home fitness",
    "beauty_hack": "woman skincare beauty routine face",
    "wellness_tip": "woman wellness meditation healthy lifestyle",
    "amazon_find": "woman unboxing product review kitchen",
    "lifestyle_hack": "woman home organization lifestyle hack",
}

ELEVENLABS_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Sarah - friendly female


def _supabase_creds() -> tuple:
    """Return (url, key) for the TikTok Supabase project."""
    url = os.environ.get("SUPABASE_TIKTOK_URL") or os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_TIKTOK_KEY") or os.environ.get("SUPABASE_KEY", "")
    return url, key


def generate_script(client: anthropic.Anthropic, category: Optional[str] = None) -> dict:
    """Generate a TikTok script via Claude API."""
    if category is None:
        category = random.choice(CATEGORIES)

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Create a viral TikTok short video script for the {category.replace('_', ' ')} niche. "
                    "TARGET AUDIENCE: U.S. women aged 25-44 interested in quick workouts, beauty hacks, and lifestyle tips. "
                    f"CATEGORY: {category}. "
                    "REQUIREMENTS: "
                    "1) Hook (first 3 seconds) that stops the scroll and creates curiosity. "
                    "2) Problem or Pain point that is relatable. "
                    "3) Solution or Tips with 2-3 actionable points. "
                    "4) CTA that is subtle and engagement-focused. "
                    "5) Duration 20-45 seconds when spoken. "
                    "Generate these fields: "
                    "topic (catchy max 100 chars), "
                    "script (natural conversational voiceover, no stage directions), "
                    "voice_prompt (ElevenLabs voice direction with tone pace emotion), "
                    "video_prompt (scene description for stock video search), "
                    "caption (TikTok caption with emoji hooks max 150 chars), "
                    "hashtags (array of 7 hashtags including #fyp), "
                    "affiliate_product (object with name, asin starting with B0, estimated_price as number). "
                    "Return ONLY valid JSON with these exact keys and no markdown formatting or code blocks."
                ),
            }
        ],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    data = json.loads(text)
    data["category"] = category
    logger.info(f"Generated script: {data['topic'][:60]}")
    return data


def generate_audio(script_text: str) -> Optional[bytes]:
    """Generate TTS audio via ElevenLabs API. Returns None if key not set."""
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        logger.warning("ELEVENLABS_API_KEY not set — skipping audio generation")
        return None

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
        json={
            "text": script_text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True,
            },
        },
    )
    response.raise_for_status()
    logger.info(f"Audio generated: {len(response.content)} bytes")
    return response.content


def upload_audio(audio_data: bytes, filename: str) -> str:
    """Upload audio to Supabase Storage and return public URL."""
    supabase_url, supabase_key = _supabase_creds()

    response = requests.post(
        f"{supabase_url}/storage/v1/object/tiktok-media/audio/{filename}",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "audio/mpeg",
        },
        data=audio_data,
    )
    response.raise_for_status()
    public_url = f"{supabase_url}/storage/v1/object/public/tiktok-media/audio/{filename}"
    logger.info(f"Audio uploaded: {public_url}")
    return public_url


def find_stock_video(category: str) -> Optional[str]:
    """Search Pexels for a portrait stock video matching the category."""
    pexels_key = os.environ.get("PEXELS_API_KEY", "")
    if not pexels_key:
        logger.warning("PEXELS_API_KEY not set, skipping video search")
        return None

    query = PEXELS_SEARCH_MAP.get(category, "woman lifestyle wellness")
    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": pexels_key},
        params={"query": query, "per_page": 5, "orientation": "portrait"},
    )
    response.raise_for_status()
    videos = response.json().get("videos", [])

    for video in videos:
        for vf in video.get("video_files", []):
            if vf.get("quality") == "hd" and vf.get("width", 0) < vf.get("height", 0):
                logger.info(f"Found video: {vf['link'][:60]}...")
                return vf["link"]

    if videos and videos[0].get("video_files"):
        return videos[0]["video_files"][0]["link"]

    return None


def save_to_supabase(script_data: dict, audio_url: str, video_url: Optional[str]) -> dict:
    """Insert the complete record into Supabase tiktok_queue."""
    supabase_url, supabase_key = _supabase_creds()

    status = "video_ready" if video_url else "audio_ready"

    payload = {
        "topic": script_data["topic"],
        "script": script_data["script"],
        "voice_prompt": script_data["voice_prompt"],
        "video_prompt": script_data["video_prompt"],
        "caption": script_data["caption"],
        "hashtags": script_data["hashtags"],
        "affiliate_products": [script_data["affiliate_product"]],
        "amazon_tag": "fitnessquick-20",
        "audio_url": audio_url,
        "video_url": video_url,
        "status": status,
        "script_generated_at": datetime.utcnow().isoformat() + "Z",
        "audio_generated_at": datetime.utcnow().isoformat() + "Z",
    }

    if video_url:
        payload["video_generated_at"] = datetime.utcnow().isoformat() + "Z"

    response = requests.post(
        f"{supabase_url}/rest/v1/tiktok_queue",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        },
        json=payload,
    )
    response.raise_for_status()
    record = response.json()[0]
    logger.info(f"Saved to Supabase: {record['id']} ({status})")
    return record


def run_pipeline(category: Optional[str] = None) -> dict:
    """Run the full TikTok content pipeline for one video."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set — cannot generate scripts")

    claude_client = anthropic.Anthropic(api_key=api_key)

    # Step 1: Generate script
    script = generate_script(claude_client, category)

    # Step 2: Generate audio (optional — skipped if ELEVENLABS_API_KEY not set)
    audio_url = None
    try:
        audio_data = generate_audio(script["script"])
        if audio_data:
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            filename = f"{timestamp}-{script['category']}.mp3"
            audio_url = upload_audio(audio_data, filename)
    except Exception as e:
        logger.warning(f"Audio generation/upload failed (non-fatal): {e}")

    # Step 3: Find stock video
    video_url = find_stock_video(script["category"])

    # Step 4: Save to Supabase
    try:
        record = save_to_supabase(script, audio_url, video_url)
        return {
            "id": record["id"],
            "topic": record["topic"],
            "status": record["status"],
            "audio_url": audio_url,
            "video_url": video_url,
        }
    except Exception as e:
        logger.warning(f"Supabase save failed: {e}")
        return {
            "id": "local",
            "topic": script["topic"],
            "status": "script_only",
            "audio_url": audio_url,
            "video_url": video_url,
        }


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    parser = argparse.ArgumentParser(description="TikTok content pipeline")
    parser.add_argument("--count", type=int, default=1, help="Number of scripts to generate")
    parser.add_argument("--category", type=str, default=None, help="Content category")
    parser.add_argument("--dry-run", action="store_true", help="Generate script only, no API calls")
    args = parser.parse_args()

    if args.dry_run:
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
        script = generate_script(client, args.category)
        print(json.dumps(script, indent=2))
        return

    results = []
    for i in range(args.count):
        logger.info(f"=== Generating video {i + 1}/{args.count} ===")
        result = run_pipeline(args.category)
        results.append(result)
        logger.info(f"Done: {result['topic'][:50]} -> {result['status']}")

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
