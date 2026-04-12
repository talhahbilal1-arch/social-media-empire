"""
Generate Pinterest pin images using Gemini 2.0 Flash Exp (Nano Banana).
Free tier: 500 images/day. We need ~15/day (5 per brand).
"""
import os
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Brand-specific prompt configs
BRAND_CONFIGS = {
    "fitness": {
        "name": "FitOver35",
        "colors": "warm orange, coral, and white",
        "style": "energetic fitness, bold sporty typography",
        "audience": "women over 35",
        "aesthetic": "Clean, motivational, modern fitness aesthetic"
    },
    "deals": {
        "name": "DailyDealDarling",
        "colors": "emerald green, gold, and cream",
        "style": "exciting deal/savings energy, sale tag typography",
        "audience": "savvy shoppers looking for deals",
        "aesthetic": "Eye-catching, deal-focused, urgency-driven"
    },
    "menopause": {
        "name": "MenopausePlanner",
        "colors": "soft purple, teal, and lavender",
        "style": "calming wellness, elegant serif typography",
        "audience": "women navigating menopause",
        "aesthetic": "Calming, supportive, medical-wellness aesthetic"
    }
}


def generate_pin_image(brand: str, topic: str, headline: str = "") -> Optional[bytes]:
    """Generate a single Pinterest pin image with text overlay using Gemini."""
    try:
        from google import genai

        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        config = BRAND_CONFIGS.get(brand, BRAND_CONFIGS["fitness"])

        if not headline:
            headline = topic.upper()[:50]  # Use topic as headline, max 50 chars

        prompt = f"""Create a Pinterest pin image (1000x1500 pixels, portrait 2:3 ratio).

HEADLINE TEXT ON IMAGE: "{headline}"

Style: {config['aesthetic']}
Color palette: {config['colors']}
Typography: {config['style']}
Target audience: {config['audience']}
Topic: {topic}

Requirements:
- The headline text MUST be large, bold, and easily readable on mobile
- High contrast between text and background
- Professional Pinterest aesthetic - clean, not cluttered
- No watermarks or logos
- The image should stop someone scrolling and make them want to click
- Brand name "{config['name']}" in smaller text at bottom"""

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            )
        )

        # Extract image from response
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                return part.inline_data.data

        logger.warning(f"No image in Gemini response for {brand}/{topic}")
        return None

    except Exception as e:
        logger.error(f"Nano Banana generation failed for {brand}/{topic}: {e}")
        return None


def generate_pin_image_with_retry(brand: str, topic: str, headline: str = "", max_retries: int = 3) -> Optional[bytes]:
    """Generate with retry and exponential backoff."""
    for attempt in range(max_retries):
        result = generate_pin_image(brand, topic, headline)
        if result:
            return result
        if attempt < max_retries - 1:
            wait = 2 ** attempt * 5  # 5s, 10s, 20s
            logger.info(f"Retry {attempt+1}/{max_retries} in {wait}s...")
            time.sleep(wait)

    # Fallback to Pexels
    logger.warning(f"Falling back to Pexels for {brand}/{topic}")
    try:
        from video_automation.pexels_fetcher import fetch_pexels_image
        return fetch_pexels_image(topic)
    except Exception as e:
        logger.error(f"Pexels fallback also failed: {e}")
        return None


def generate_pin_batch(brand: str, topics: list, count: int = 5) -> list:
    """Generate a batch of pin images for a brand."""
    results = []
    for i, topic in enumerate(topics[:count]):
        logger.info(f"Generating pin {i+1}/{count} for {brand}: {topic}")

        image_bytes = generate_pin_image_with_retry(brand, topic)
        if image_bytes:
            config = BRAND_CONFIGS.get(brand, BRAND_CONFIGS["fitness"])
            results.append({
                "image_bytes": image_bytes,
                "topic": topic,
                "title": f"{topic} | {config['name']}",
                "description": f"{topic} - Tips and insights for {config['audience']}. Follow {config['name']} for more!",
                "filename": f"{brand}_{topic.lower().replace(' ', '_')[:40]}_{int(time.time())}.png"
            })
        else:
            logger.error(f"Failed to generate pin for {brand}/{topic}")

    return results
