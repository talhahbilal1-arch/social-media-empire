"""
Generate 30-60 second video scripts using Google Gemini.
Returns structured script data: title, hook, body_points, cta, hashtags, pexels_search_queries.
"""

import json
import logging
import random
from typing import Optional

from .config import BrandConfig, get_api_key

logger = logging.getLogger(__name__)


def _build_prompt(
    brand: BrandConfig,
    topic: Optional[str] = None,
    format: str = "standard",
) -> str:
    chosen_topic = topic or random.choice(brand.topics)

    if format == "pinterest":
        return f"""You are a viral Pinterest video script writer for the brand "{brand.name}".

Brand voice: {brand.voice_style}
Topic: {chosen_topic}

Write a 10-12 second Pinterest video script (roughly 25-35 words spoken aloud).
Structure: Hook (1 sentence, 2-3s) → ONE key insight (1-2 sentences, 5-8s) → CTA (1 sentence, 2-3s).

Return ONLY valid JSON in this exact structure:
{{
  "title": "Compelling video title (under 60 chars)",
  "topic": "{chosen_topic}",
  "hook": "One punchy sentence that stops the scroll (2-3 seconds)",
  "body_points": [
    "ONE specific, actionable insight — 1-2 sentences max"
  ],
  "cta": "One clear action (save this, follow for more, link in bio)",
  "full_script": "Complete narration: hook + one insight + cta — 25-35 words total, ready for TTS",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "pexels_search_queries": [
    "specific video/image search query 1",
    "specific video/image search query 2",
    "specific video/image search query 3"
  ],
  "estimated_duration_seconds": 11
}}

Rules:
- full_script must be 25-35 words MAXIMUM — no exceptions
- body_points must have EXACTLY 1 item
- Hook creates instant curiosity or promises one specific result
- The one body point is a concrete fact or quick tip (not generic)
- Pexels queries must be specific (e.g. "woman doing home workout" not just "workout")
- Hashtags mix broad and niche tags for the brand
"""

    # Standard (30-60s) and youtube (same template) formats
    duration_hint = "30-60 second" if format != "youtube" else "30-60 second"
    return f"""You are a viral short-form video script writer for the brand "{brand.name}".

Brand voice: {brand.voice_style}
Topic: {chosen_topic}

Write a {duration_hint} video script (roughly 75-150 words when spoken aloud at a normal pace).

Return ONLY valid JSON in this exact structure:
{{
  "title": "Compelling video title (under 60 chars)",
  "topic": "{chosen_topic}",
  "hook": "First 3 seconds — one punchy sentence that stops the scroll",
  "body_points": [
    "Point 1 — specific, actionable, 1-2 sentences",
    "Point 2 — specific, actionable, 1-2 sentences",
    "Point 3 — specific, actionable, 1-2 sentences"
  ],
  "cta": "Clear call-to-action (follow, save, click link, etc.)",
  "full_script": "Complete narration text in order: hook + body + cta, ready for TTS",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "pexels_search_queries": [
    "specific image search query 1",
    "specific image search query 2",
    "specific image search query 3",
    "specific image search query 4",
    "specific image search query 5"
  ],
  "estimated_duration_seconds": 45
}}

Rules:
- Hook must create curiosity or promise a specific result
- Body points must be concrete facts or actionable tips (no filler)
- CTA must be one clear action
- Pexels queries must be specific enough to return relevant images (e.g. "woman doing yoga at home" not just "yoga")
- Hashtags should mix broad (#fitness) and niche (#fitover35) tags
- full_script should read naturally when spoken aloud
"""


def generate_script(
    brand: BrandConfig,
    topic: Optional[str] = None,
    model: str = "gemini-2.5-flash",
    format: str = "standard",
) -> dict:
    """
    Generate a video script for the given brand.

    Args:
        brand: BrandConfig instance
        topic: Optional specific topic; picks randomly from brand.topics if None
        model: Gemini model to use
        format: Video format — "pinterest" (10-12s, 1 body point),
                "youtube" or "standard" (30-60s, 3 body points)

    Returns:
        dict with keys: title, topic, hook, body_points, cta, full_script,
                        hashtags, pexels_search_queries, estimated_duration_seconds
    """
    try:
        import google.genai as genai
    except ImportError:
        raise RuntimeError(
            "google-genai not installed. Run: pip install google-genai"
        )

    api_key = get_api_key("GEMINI_API_KEY")

    try:
        client = genai.Client(api_key=api_key)
        prompt = _build_prompt(brand, topic, format=format)

        logger.info(f"Generating script for brand={brand.key}, model={model}, format={format}")

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0.8,
                response_mime_type="application/json",
            ),
        )

        raw = response.text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        script_data = json.loads(raw)

        # Validate required keys
        required_keys = [
            "title", "hook", "body_points", "cta", "full_script",
            "hashtags", "pexels_search_queries", "estimated_duration_seconds",
        ]
        missing = [k for k in required_keys if k not in script_data]
        if missing:
            raise ValueError(f"Gemini response missing keys: {missing}")

        logger.info(
            f"Script generated: '{script_data['title']}' "
            f"(~{script_data['estimated_duration_seconds']}s)"
        )
        return script_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini JSON response: {e}")
        raise
    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        raise
