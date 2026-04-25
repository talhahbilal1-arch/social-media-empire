"""Generate videos via Short Video Maker Docker container (localhost:3123).

Short Video Maker produces TikTok-quality portrait shorts with AI
voiceover, auto-generated captions, Pexels B-roll, and background music.
It exposes a REST API; the container must be running on the Mac for
this module to work.

Public functions:
  is_short_video_maker_available() -> bool
  generate_video(brand, scenes, config=None) -> dict | None
  scenes_from_pin_content(brand, video_content) -> list[dict]
  get_brand_config(brand) -> dict
"""

import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

BASE_URL = os.environ.get("SHORT_VIDEO_MAKER_URL", "http://localhost:3123")

# Per-brand voice + music mood. Voice `am_adam` is the male option;
# `af_heart` is the female option. Music moods match the container's
# built-in library (see README: sad/melancholic/happy/euphoric/excited/
# chill/uneasy/angry/dark/hopeful/contemplative/funny).
BRAND_CONFIGS = {
    "fitness":    {"voice": "am_adam",  "music": "excited"},
    "deals":      {"voice": "af_heart", "music": "happy"},
    "homedecor":  {"voice": "af_heart", "music": "chill"},
    "beauty":     {"voice": "af_heart", "music": "chill"},
    "menopause":  {"voice": "af_heart", "music": "hopeful"},
    "pilottools": {"voice": "af_heart", "music": "contemplative"},
}

# Brand-specific visual keywords mixed into every scene's Pexels search.
# The primary keyword is always included; the fallback set gives Pexels
# enough variety to return distinct B-roll across 6 scenes.
BRAND_KEYWORDS = {
    "fitness":    ["man", "gym", "workout", "strength", "muscle"],
    "deals":      ["home", "kitchen", "cozy", "shopping", "lifestyle"],
    "homedecor":  ["home", "cozy", "interior", "living room", "bedroom"],
    "beauty":     ["woman", "skincare", "beauty", "makeup", "glow"],
    "menopause":  ["woman", "wellness", "calm", "self care", "mature"],
    "pilottools": ["laptop", "technology", "working", "office", "startup"],
}

# Render ceiling — the container takes 2-5 minutes per video; we leave
# headroom for slow Pexels responses or TTS quirks but bail after 10 min.
POLL_INTERVAL_SEC = 5
MAX_WAIT_SEC = 600
HEALTH_TIMEOUT_SEC = 3


def is_short_video_maker_available() -> bool:
    """Return True if the container responds to /health within 3 seconds."""
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=HEALTH_TIMEOUT_SEC)
        return resp.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False
    except Exception as e:
        logger.warning(f"short_video_maker health check errored: {e}")
        return False


def get_brand_config(brand: str) -> dict:
    """Return the Short Video Maker config dict for `brand`.

    Always produces portrait 9:16 with captions at bottom on a black
    background — the format that performs on Pinterest/TikTok/Shorts.
    """
    per_brand = BRAND_CONFIGS.get(brand, BRAND_CONFIGS["fitness"])
    return {
        "voice": per_brand["voice"],
        "music": per_brand["music"],
        "orientation": "portrait",
        "captionPosition": "bottom",
        "captionBackgroundColor": "black",
        "paddingBack": 1500,
        "musicVolume": "medium",
    }


_TIP_NOUN_RE = re.compile(r"\b[a-zA-Z]{4,}\b")
_STOPWORDS = {
    "with", "your", "that", "this", "have", "will", "from", "into",
    "when", "what", "they", "them", "than", "then", "just", "like",
    "make", "take", "keep", "best", "most", "some", "each", "week",
    "every", "after", "before", "about", "these", "those", "small",
    "daily", "today", "tips",
}


def _tip_to_search_terms(tip: str, brand_keywords: list[str]) -> list[str]:
    """Extract 1-2 visual nouns from a tip + append brand keyword.

    Pexels responds better to concrete nouns than to full sentences.
    We grep 4+ letter words, drop obvious stopwords, take the first two,
    and always include one brand keyword as a safety net.
    """
    words = _TIP_NOUN_RE.findall(tip.lower())
    nouns = [w for w in words if w not in _STOPWORDS][:2]
    terms = list(nouns)
    if brand_keywords:
        terms.append(brand_keywords[0])
    return terms or [brand_keywords[0] if brand_keywords else "lifestyle"]


def scenes_from_pin_content(brand: str, video_content: dict) -> list[dict]:
    """Build a 6-scene payload from video_content.

    Scenes:
      1. hook        — search_query + primary brand keyword
      2-5. each tip  — noun hint from tip + primary brand keyword
      6. cta         — aspirational brand keywords

    If `tips` is missing or too short (shouldn't happen — content brain
    guarantees 5), falls back to a 3-scene hook/solution/cta layout so
    we still produce something renderable.
    """
    brand_keywords = BRAND_KEYWORDS.get(brand, BRAND_KEYWORDS["fitness"])
    primary = brand_keywords[0]
    search_query = (video_content.get("search_query") or primary).strip()

    hook = (video_content.get("hook") or "").strip()
    solution = (video_content.get("solution") or "").strip()
    cta = (video_content.get("cta") or "Save This For Later").strip()
    tips = [t for t in (video_content.get("tips") or []) if isinstance(t, str) and t.strip()]

    scenes: list[dict] = []

    if hook:
        scenes.append({"text": hook, "searchTerms": [search_query, primary]})

    if len(tips) >= 4:
        # Take up to 4 tips for the middle scenes.
        for tip in tips[:4]:
            scenes.append({
                "text": tip.strip(),
                "searchTerms": _tip_to_search_terms(tip, brand_keywords),
            })
    elif solution:
        scenes.append({"text": solution, "searchTerms": [search_query, brand_keywords[1] if len(brand_keywords) > 1 else primary]})

    scenes.append({
        "text": cta,
        "searchTerms": brand_keywords[1:3] if len(brand_keywords) >= 3 else [primary],
    })

    return scenes


def _extract_cover_frame(video_path: Path) -> bytes:
    """Extract a JPEG cover frame at 3 seconds via ffmpeg.

    Mirrors `remotion_renderer._extract_cover_frame` — same `-ss 3` target
    so covers across the two renderers look consistent on Pinterest.
    Returns empty bytes on any failure; callers treat empty covers as
    "no cover available" rather than crashing.
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        logger.warning("ffmpeg not on PATH — cover extraction skipped")
        return b""

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
        cover_path = Path(tf.name)
    try:
        subprocess.run(
            [
                ffmpeg, "-y", "-loglevel", "error",
                "-ss", "3",
                "-i", str(video_path),
                "-vframes", "1", "-q:v", "2",
                str(cover_path),
            ],
            check=True, timeout=30,
        )
        return cover_path.read_bytes() if cover_path.exists() else b""
    except Exception as e:
        logger.warning(f"cover extraction failed: {e}")
        return b""
    finally:
        cover_path.unlink(missing_ok=True)


def _poll_until_ready(video_id: str) -> bool:
    """Poll /status until `ready` or deadline. Returns True on ready."""
    deadline = time.monotonic() + MAX_WAIT_SEC
    while time.monotonic() < deadline:
        try:
            resp = requests.get(
                f"{BASE_URL}/api/short-video/{video_id}/status",
                timeout=10,
            )
            if resp.status_code == 200:
                status = (resp.json() or {}).get("status", "")
                if status == "ready":
                    return True
                if status in ("failed", "error"):
                    logger.error(f"short_video_maker reported {status} for {video_id}")
                    return False
        except Exception as e:
            logger.warning(f"poll error for {video_id}: {e}")
        time.sleep(POLL_INTERVAL_SEC)
    logger.error(f"short_video_maker timed out after {MAX_WAIT_SEC}s for {video_id}")
    return False


def generate_video(brand: str, scenes: list[dict], config: Optional[dict] = None) -> Optional[dict]:
    """Submit a render job and return bytes + metadata.

    Returns `{'video_bytes', 'cover_bytes', 'duration', 'video_id'}` on
    success, or None on any failure (container down, render timeout,
    download error, etc). Callers should not raise — they should mark
    the pin `video_failed` and move on.

    `duration` is approximate (scene count × 4 seconds) because the
    container does not report actual duration in the status response.
    """
    cfg = config or get_brand_config(brand)

    try:
        resp = requests.post(
            f"{BASE_URL}/api/short-video",
            json={"scenes": scenes, "config": cfg},
            timeout=30,
        )
    except Exception as e:
        logger.error(f"short_video_maker create errored: {e}")
        return None

    if resp.status_code not in (200, 201):
        logger.error(f"short_video_maker create HTTP {resp.status_code}: {resp.text[:200]}")
        return None

    try:
        video_id = (resp.json() or {}).get("videoId", "")
    except Exception:
        logger.error(f"short_video_maker create returned non-JSON: {resp.text[:200]}")
        return None

    if not video_id:
        logger.error(f"short_video_maker create returned no videoId: {resp.text[:200]}")
        return None

    logger.info(f"short_video_maker job {video_id} submitted ({len(scenes)} scenes)")

    if not _poll_until_ready(video_id):
        return None

    try:
        dl = requests.get(f"{BASE_URL}/api/short-video/{video_id}", timeout=120)
    except Exception as e:
        logger.error(f"short_video_maker download errored for {video_id}: {e}")
        return None

    if dl.status_code != 200 or not dl.content:
        logger.error(f"short_video_maker download HTTP {dl.status_code} for {video_id}")
        return None

    video_bytes = dl.content
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
        tf.write(video_bytes)
        tmp_path = Path(tf.name)
    try:
        cover_bytes = _extract_cover_frame(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    return {
        "video_bytes": video_bytes,
        "cover_bytes": cover_bytes,
        "duration": len(scenes) * 4,  # approximate
        "video_id": video_id,
    }
