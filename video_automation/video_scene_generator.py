"""Generate 4 scene images for a video pin using Nano Banana (Gemini image generation).

Produces one image per narrative beat — wide establishing, close-up problem, action
solution, aspirational result — ready to feed the Remotion SlideshowVideo component.

All images are 1080x1920 JPEG bytes. Per-scene Pexels fallback keeps the pipeline
resilient: if Gemini fails on any scene, we fetch a brand-appropriate stock photo
instead. Returns exactly 4 images, always.
"""

import logging
import os
import time
from io import BytesIO

logger = logging.getLogger(__name__)

IMAGE_MODEL = "gemini-2.0-flash-exp"
TARGET_SIZE = (1080, 1920)

# Per-brand scene-specific Pexels search queries (last-resort fallback).
# Keyed by (brand, scene_index) — scene 1 = wide, 2 = close-up, 3 = action, 4 = result.
_PEXELS_SCENE_QUERIES = {
    "fitness": [
        "man gym interior wide",
        "muscle close up sweat effort",
        "man lifting weights action",
        "man confident fit physique",
    ],
    "deals": [
        "modern home living room cozy",
        "hands unboxing product close",
        "shopping online laptop lifestyle",
        "organized kitchen clean aesthetic",
    ],
    "menopause": [
        "calm bedroom natural light wellness",
        "woman thoughtful close portrait",
        "woman yoga meditation peaceful",
        "woman smiling confident midlife",
    ],
}

# Brand visual DNA — fed into every Gemini scene prompt so all 4 images feel cohesive.
_BRAND_VISUAL = {
    "fitness": (
        "Professional fitness photography. Subject: muscular man over 35. "
        "Dramatic contrast lighting, gym or athletic setting, dark moody palette "
        "with warm orange and charcoal tones. Magazine-cover quality."
    ),
    "deals": (
        "Professional product lifestyle photography. Warm golden-hour lighting, "
        "clean minimalist styling, aspirational home aesthetic. "
        "Cream, gold, and burgundy tones. Editorial quality."
    ),
    "menopause": (
        "Soft wellness photography of a woman in her 40s-50s. Natural light, "
        "botanical elements, calming pastel palette — lavender, sage, blush pink. "
        "Serene, empowering, premium wellness-retreat aesthetic."
    ),
}


def _get_client():
    """Lazy Gemini client — reuses shared helper when available."""
    try:
        from video_automation.gemini_client import get_client
        return get_client()
    except Exception:
        from google import genai
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        return genai.Client(api_key=api_key)


def _scene_prompts(brand: str, topic: str, hook: str, points: list) -> list:
    """Build 4 scene prompts — wide, close-up, action, result — for one video."""
    visual = _BRAND_VISUAL.get(brand, _BRAND_VISUAL["fitness"])
    topic_hint = topic or hook or ""
    problem = (points[0] if points else topic_hint)[:120]
    solution = (points[1] if len(points) > 1 else topic_hint)[:120]
    outcome = (points[-1] if points else topic_hint)[:120]

    return [
        # Scene 1 — wide establishing
        f"{visual} Wide establishing shot that sets the scene. Topic: {topic_hint}. "
        f"Capture the full environment. Portrait 9:16 composition. "
        f"No text, no watermarks, no logos.",
        # Scene 2 — close-up problem
        f"{visual} Close-up detail shot illustrating the problem: {problem}. "
        f"Shallow depth of field, emotional focus. Portrait 9:16 composition. "
        f"No text, no watermarks, no logos.",
        # Scene 3 — action/solution
        f"{visual} Action shot showing the solution in progress: {solution}. "
        f"Dynamic movement, clear subject. Portrait 9:16 composition. "
        f"No text, no watermarks, no logos.",
        # Scene 4 — aspirational result
        f"{visual} Aspirational result shot: {outcome}. Confident, transformed, "
        f"content subject. Triumphant mood. Portrait 9:16 composition. "
        f"No text, no watermarks, no logos.",
    ]


def _normalize_to_jpeg(raw_bytes: bytes) -> bytes:
    """Re-encode any image bytes as 1080x1920 JPEG (center-crop cover fit)."""
    from PIL import Image

    img = Image.open(BytesIO(raw_bytes)).convert("RGB")
    target_w, target_h = TARGET_SIZE
    src_w, src_h = img.size

    # Scale to cover, then center-crop
    scale = max(target_w / src_w, target_h / src_h)
    new_w, new_h = int(src_w * scale), int(src_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    img = img.crop((left, top, left + target_w, top + target_h))

    out = BytesIO()
    img.save(out, "JPEG", quality=90, optimize=True)
    return out.getvalue()


def _gemini_scene(prompt: str, brand: str, scene_idx: int) -> bytes:
    """Generate one scene via Gemini with 2 retries. Raises on total failure."""
    from google.genai import types

    client = _get_client()
    last_error = None

    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model=IMAGE_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
            )
            for candidate in response.candidates or []:
                for part in candidate.content.parts or []:
                    if hasattr(part, "inline_data") and part.inline_data:
                        data = part.inline_data.data
                        if isinstance(data, str):
                            import base64
                            data = base64.b64decode(data)
                        if data:
                            logger.info(f"[{brand}] scene {scene_idx + 1} Gemini: {len(data)} bytes")
                            return _normalize_to_jpeg(data)
            raise RuntimeError("Gemini returned no image data")
        except Exception as e:
            last_error = e
            if attempt == 0:
                time.sleep(2)
                logger.warning(f"[{brand}] scene {scene_idx + 1} retry after: {e}")

    raise RuntimeError(f"Gemini failed for scene {scene_idx + 1}: {last_error}")


def _pexels_scene(brand: str, scene_idx: int) -> bytes:
    """Fetch a scene-appropriate Pexels portrait JPEG. Raises on failure."""
    import requests

    api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY not set")

    queries = _PEXELS_SCENE_QUERIES.get(brand, _PEXELS_SCENE_QUERIES["fitness"])
    query = queries[scene_idx % len(queries)]

    resp = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": api_key},
        params={"query": query, "per_page": 15, "orientation": "portrait"},
        timeout=15,
    )
    resp.raise_for_status()
    photos = resp.json().get("photos", [])
    if not photos:
        raise RuntimeError(f"Pexels returned 0 photos for '{query}'")

    # Pick a different photo per scene to keep variety
    photo = photos[scene_idx % len(photos)]
    img_resp = requests.get(photo["src"]["large2x"], timeout=30)
    img_resp.raise_for_status()
    return _normalize_to_jpeg(img_resp.content)


def _placeholder_scene(brand: str, scene_idx: int) -> bytes:
    """Last-resort solid color JPEG so we never return fewer than 4 images."""
    from PIL import Image

    colors = {
        "fitness":   [(26, 26, 36), (46, 26, 20), (36, 32, 28), (40, 28, 22)],
        "deals":     [(48, 32, 24), (60, 42, 28), (52, 38, 32), (40, 30, 22)],
        "menopause": [(48, 36, 58), (56, 44, 64), (62, 52, 70), (70, 58, 76)],
    }
    palette = colors.get(brand, colors["fitness"])
    color = palette[scene_idx % len(palette)]
    img = Image.new("RGB", TARGET_SIZE, color)
    out = BytesIO()
    img.save(out, "JPEG", quality=85)
    return out.getvalue()


def generate_scene_images(brand: str, video_content: dict) -> list:
    """Generate 4 scene images for a video pin.

    Args:
        brand: Content-engine brand key: 'fitness', 'deals', or 'menopause'
        video_content: Dict from generate_video_pin_content() with keys like
            'topic', 'hook', 'title', 'tips'

    Returns:
        List of exactly 4 JPEG byte arrays at 1080x1920. Never raises — falls
        through Gemini → Pexels → solid-color placeholder per scene.
    """
    topic = video_content.get("topic") or video_content.get("hook", "")
    hook = video_content.get("hook", "")
    points = video_content.get("tips", []) or []

    prompts = _scene_prompts(brand, topic, hook, points)
    scenes = []

    for i, prompt in enumerate(prompts):
        try:
            scenes.append(_gemini_scene(prompt, brand, i))
            continue
        except Exception as gem_err:
            logger.warning(f"[{brand}] scene {i + 1} Gemini failed: {gem_err}")

        try:
            scenes.append(_pexels_scene(brand, i))
            logger.info(f"[{brand}] scene {i + 1} Pexels fallback used")
            continue
        except Exception as pex_err:
            logger.warning(f"[{brand}] scene {i + 1} Pexels failed: {pex_err}")

        scenes.append(_placeholder_scene(brand, i))
        logger.warning(f"[{brand}] scene {i + 1} using solid-color placeholder")

    return scenes
