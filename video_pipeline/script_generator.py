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


def _build_prompt(brand: BrandConfig, topic: Optional[str] = None) -> str:
    chosen_topic = topic or random.choice(brand.topics)

    return f"""You are a viral short-form video script writer for the brand "{brand.name}".

Brand voice: {brand.voice_style}
Topic: {chosen_topic}

Write a 30-60 second video script (roughly 75-150 words when spoken aloud at a normal pace).

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


def _build_pinterest_prompt(brand: BrandConfig, topic: Optional[str] = None) -> str:
    """Pinterest-optimized prompt: 10-12 sec spoken, open-loop curiosity hook, 1 body point."""
    chosen_topic = topic or random.choice(brand.topics)

    hook_examples = {
        "deals": [
            "This $12 Amazon gadget replaced 3 appliances in my kitchen...",
            "I almost returned this, then I saw what it actually does...",
            "The product every home needs but nobody's talking about...",
        ],
        "fitover35": [
            "Every trainer over 35 is doing this wrong — and it's killing your gains...",
            "This one habit added 10 pounds of muscle after 40...",
            "The muscle-building mistake men over 35 make every single day...",
        ],
        "menopause": [
            "This 30-second trick stopped my hot flashes for good...",
            "Doctors won't tell you this about menopause weight gain...",
            "The hormone hack that changed everything for women over 45...",
        ],
        "pilottools": [
            "This free AI tool just replaced $300/month of software...",
            "The AI tool that nobody's talking about in 2025...",
            "I tested every AI writing tool — this one shocked me...",
        ],
    }
    examples = hook_examples.get(brand.key, hook_examples["fitover35"])
    hook_example = random.choice(examples)

    return f"""You are a Pinterest video script writer for the brand "{brand.name}".

Brand voice: {brand.voice_style}
Topic: {chosen_topic}
Audience: {brand.audience}

Write a SHORT Pinterest video script — 10-12 seconds of spoken content (50-60 words MAX).

The hook MUST create an open loop — the viewer cannot mentally close it without clicking.
Hook example for inspiration (don't copy exactly): "{hook_example}"

Return ONLY valid JSON in this exact structure:
{{
  "title": "Compelling video title (under 55 chars)",
  "topic": "{chosen_topic}",
  "hook": "One sentence open-loop hook — creates curiosity the viewer MUST resolve by clicking",
  "body_points": [
    "One concrete teaser — reveals just enough to be intriguing, not enough to satisfy"
  ],
  "cta": "Link in bio",
  "full_script": "Complete narration: hook sentence + one body teaser + CTA. MAX 60 words. Read naturally at normal pace.",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "pexels_search_queries": [
    "specific portrait image query 1",
    "specific portrait image query 2",
    "specific portrait image query 3",
    "specific portrait image query 4"
  ],
  "estimated_duration_seconds": 12
}}

Rules:
- full_script must be 50-60 words MAXIMUM (counts as spoken — roughly 12 seconds)
- Hook must create an UNRESOLVED question or tease a secret/reveal
- body_points has exactly ONE item — a teaser, not a full answer
- cta is always "Link in bio" or "Tap to shop" — drives affiliate clicks
- Pexels queries must be portrait-oriented and visually relevant (e.g. "woman holding kitchen gadget smiling" not just "kitchen")
- No filler phrases like "in this video" or "today we're going to"
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
        format: "standard" (30-60s) or "pinterest" (10-12s open-loop)

    Returns:
        dict with keys: title, topic, hook, body_points, cta, full_script,
                        hashtags, pexels_search_queries, estimated_duration_seconds
    """
    import time as _time
    try:
        import google.genai as genai
    except ImportError:
        raise RuntimeError(
            "google-genai not installed. Run: pip install google-genai"
        )

    api_key = get_api_key("GEMINI_API_KEY")

    # Model fallback chain — if primary hits rate limit, try alternatives
    models_to_try = [model, "gemini-2.0-flash", "gemini-1.5-flash"]

    try:
        client = genai.Client(api_key=api_key)
        if format == "pinterest":
            prompt = _build_pinterest_prompt(brand, topic)
        else:
            prompt = _build_prompt(brand, topic)

        response = None
        last_error = None
        for attempt_model in models_to_try:
            for attempt in range(3):
                try:
                    logger.info(f"Generating script: brand={brand.key}, model={attempt_model}, attempt={attempt+1}")
                    response = client.models.generate_content(
                        model=attempt_model,
                        contents=prompt,
                        config=genai.types.GenerateContentConfig(
                            temperature=0.8,
                            response_mime_type="application/json",
                        ),
                    )
                    break  # Success
                except Exception as e:
                    last_error = e
                    err_str = str(e)
                    if any(code in err_str for code in ["429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE", "overloaded", "high demand"]):
                        wait = min(60, 10 * (attempt + 1))
                        logger.warning(f"Retryable error on {attempt_model}, waiting {wait}s (attempt {attempt+1}/3): {err_str[:100]}")
                        _time.sleep(wait)
                    else:
                        raise  # Non-retryable error
            if response is not None:
                break
            logger.warning(f"All retries exhausted for {attempt_model}, trying next model...")

        if response is None:
            raise RuntimeError(f"All models exhausted. Last error: {last_error}")

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
