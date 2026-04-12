"""Nano Banana — AI-generated Pinterest pin images via Gemini 2.5 Flash Image.

Replaces generic Pexels stock photos with brand-tailored AI-generated images.
Free tier: 500 images/day (we need ~15). Falls back to Pexels on failure.

Usage:
    from video_automation.nano_banana_generator import generate_pin_image, generate_pin_batch
    img_bytes = generate_pin_image('fitness', 'Best strength exercises for men over 35')
    pins = generate_pin_batch('deals', ['topic1', 'topic2'], count=5)
"""

import io
import logging
import os
import textwrap
import time

logger = logging.getLogger(__name__)

# Current Gemini image generation model — portrait 2:3 ratio recommended for Pinterest
IMAGE_MODEL = "gemini-2.5-flash-preview-image-generation"

# Brand-specific visual identity for prompt engineering
BRAND_CONFIGS = {
    "fitness": {
        "name": "FitOver35",
        "colors": "warm orange, coral red, charcoal black, and athletic white",
        "style": "bold condensed sans-serif, sports editorial, high-impact gym aesthetic",
        "audience": "men over 35 who train seriously",
        "aesthetic": "athletic, energetic, masculine — like a fitness magazine cover for men",
        "content_frame": "strength training, muscle building, fat loss, healthy lifestyle for men",
        "mood": "powerful and motivational",
    },
    "deals": {
        "name": "DailyDealDarling",
        "colors": "warm gold, forest green, cream white, and rich burgundy",
        "style": "bold sale-tag energy, large numbers, clean sans-serif, price-badge design",
        "audience": "savvy home shoppers looking for Amazon deals",
        "aesthetic": "organised home flat-lay, modern clean lifestyle aesthetic",
        "content_frame": "Amazon finds, home organisation, budget lifestyle, product savings",
        "mood": "exciting deal discovery, aspirational and inviting",
    },
    "menopause": {
        "name": "MenopausePlanner",
        "colors": "soft purple, teal, blush pink, warm cream, and sage green",
        "style": "elegant serif headings, calming wellness brand typography",
        "audience": "women navigating perimenopause and menopause",
        "aesthetic": "calming wellness retreat, natural light, botanical elements",
        "content_frame": "menopause wellness, hormone balance, midlife health tips",
        "mood": "empowering, serene, and supportive — a knowledgeable friend",
    },
}

# Brand URLs shown in small text at pin bottom
BRAND_URLS = {
    "fitness": "fitover35.com",
    "deals": "dailydealdarling.com",
    "menopause": "menopauseplanner.com",
}

# Brand overlay bar colors (RGBA) for PIL text overlay
BRAND_OVERLAY_COLORS = {
    "fitness": (20, 20, 20, 210),      # near-black, energetic
    "deals": (30, 60, 30, 200),        # dark forest green
    "menopause": (55, 30, 65, 200),    # deep purple
}

# Pexels brand-safe fallback queries
_PEXELS_FALLBACK = {
    "fitness": "man fitness workout gym strength",
    "deals": "home organisation modern minimal products",
    "menopause": "wellness calm nature woman relaxed",
}


def _get_client():
    """Lazy-init Gemini client — reuses shared module when available."""
    try:
        from video_automation.gemini_client import get_client
        return get_client()
    except Exception:
        from google import genai
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        return genai.Client(api_key=api_key)


def _build_prompt(brand: str, topic: str) -> str:
    """Construct a brand-specific image generation prompt."""
    cfg = BRAND_CONFIGS.get(brand, BRAND_CONFIGS["fitness"])
    return (
        f"Create a professional Pinterest pin image at portrait 2:3 ratio (1000x1500px). "
        f"Topic: {topic}. "
        f"Brand: {cfg['name']}. Aesthetic: {cfg['aesthetic']}. "
        f"Color palette: {cfg['colors']}. Typography: {cfg['style']}. "
        f"Mood: {cfg['mood']}. Content: {cfg['content_frame']}. "
        f"Include bold, readable headline text overlay on the image about: {topic}. "
        f"The text must be high-contrast and legible on a small mobile screen. "
        f"Requirements: professional Pinterest quality, clean composition, not cluttered. "
        f"No watermarks, no borders, no Instagram filters."
    )


def generate_pin_image(brand: str, topic: str, style: str = "default") -> bytes:
    """Generate a Pinterest pin image using Gemini image generation.

    Args:
        brand: Brand key — 'fitness', 'deals', or 'menopause'
        topic: Pin topic used to craft the visual and text overlay prompt
        style: Visual style hint (reserved for future sub-styles)

    Returns:
        PNG image bytes ready for upload to Supabase Storage

    Raises:
        RuntimeError: If Gemini fails after 3 retries AND Pexels fallback also fails
    """
    from google.genai import types

    client = _get_client()
    prompt = _build_prompt(brand, topic)
    last_error = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=IMAGE_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"]
                ),
            )
            for candidate in response.candidates or []:
                for part in candidate.content.parts or []:
                    if hasattr(part, "inline_data") and part.inline_data:
                        img_bytes = part.inline_data.data
                        if isinstance(img_bytes, str):
                            import base64
                            img_bytes = base64.b64decode(img_bytes)
                        if img_bytes:
                            logger.info(f"[{brand}] Gemini image generated ({len(img_bytes)} bytes)")
                            return img_bytes
            raise RuntimeError("Gemini returned no image data")
        except Exception as e:
            last_error = e
            wait = 2 ** attempt
            logger.warning(f"[{brand}] Gemini image attempt {attempt + 1}/3 failed: {e} — retry in {wait}s")
            if attempt < 2:
                time.sleep(wait)

    # Fallback: fetch from Pexels and return raw bytes
    logger.warning(f"[{brand}] Gemini failed after 3 attempts ({last_error}), falling back to Pexels")
    return _pexels_fallback(brand, topic)


def _pexels_fallback(brand: str, topic: str) -> bytes:
    """Fetch a Pexels image and return raw bytes as last-resort fallback."""
    import requests

    api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        raise RuntimeError(f"[{brand}] Gemini and Pexels both unavailable (no PEXELS_API_KEY)")

    query = _PEXELS_FALLBACK.get(brand, topic)
    resp = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": api_key},
        params={"query": query, "per_page": 5, "orientation": "portrait"},
        timeout=15,
    )
    resp.raise_for_status()
    photos = resp.json().get("photos", [])
    if not photos:
        raise RuntimeError(f"[{brand}] Pexels returned no photos for '{query}'")
    img_resp = requests.get(photos[0]["src"]["large2x"], timeout=30)
    img_resp.raise_for_status()
    return img_resp.content


def _generate_metadata(brand: str, topic: str) -> dict:
    """Generate Pinterest-optimized title and description via Gemini text."""
    try:
        from video_automation.gemini_client import generate_json
        import json

        cfg = BRAND_CONFIGS.get(brand, BRAND_CONFIGS["fitness"])
        prompt = (
            f"Generate a Pinterest pin title and description.\n"
            f"Topic: {topic}\nBrand: {cfg['name']} ({cfg['audience']})\n"
            f"- Title: 50-80 chars, keyword-rich, compelling, no clickbait\n"
            f"- Description: 150-250 chars, 3-5 relevant hashtags at the end\n"
            f'Return ONLY valid JSON: {{"title": "...", "description": "..."}}'
        )
        data = json.loads(generate_json(prompt, max_tokens=300))
        return {"title": data.get("title", topic[:80]), "description": data.get("description", topic)}
    except Exception as e:
        logger.warning(f"[{brand}] Metadata generation failed: {e}")
        return {"title": topic[:80], "description": topic}


def generate_pin_batch(brand: str, topics: list, count: int = 5) -> list:
    """Generate a batch of Pinterest pins with AI images and metadata.

    Args:
        brand: Brand key — 'fitness', 'deals', or 'menopause'
        topics: List of topic strings (cycled if fewer than count)
        count: Number of pins to generate

    Returns:
        List of dicts: image_bytes, topic, title, description, filename
    """
    import datetime

    if not topics:
        topics = [brand]
    selected = [topics[i % len(topics)] for i in range(count)]
    results = []

    for i, topic in enumerate(selected):
        try:
            image_bytes = generate_pin_image(brand, topic)
            metadata = _generate_metadata(brand, topic)
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            results.append({
                "image_bytes": image_bytes,
                "topic": topic,
                "title": metadata["title"],
                "description": metadata["description"],
                "filename": f"{brand}_ai_{i}_{timestamp}.png",
            })
            logger.info(f"[{brand}] Pin {i + 1}/{count} done: {metadata['title'][:50]}")
        except Exception as e:
            logger.error(f"[{brand}] Pin {i + 1} failed for '{topic}': {e}")

    return results
