"""Shared helper utilities for the video pipeline."""

import json
import logging
import os
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_audio_duration(path: str) -> Optional[float]:
    """Return audio/video duration in seconds using ffprobe."""
    from video_pipeline.config import FFPROBE_BIN
    try:
        result = subprocess.run(
            [
                FFPROBE_BIN, "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json", path,
            ],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception as e:
        logger.warning(f"ffprobe duration check failed: {e}")
        return None


def download_file(url: str, dest: str, timeout: int = 30) -> bool:
    """Download a file from URL to dest path. Returns True on success."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "social-media-empire/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            with open(dest, "wb") as f:
                f.write(response.read())
        return True
    except Exception as e:
        logger.warning(f"Download failed {url}: {e}")
        return False


def fetch_pexels_images(query: str, count: int, api_key: str, orientation: str = "portrait") -> list[str]:
    """
    Fetch image URLs from Pexels. Returns list of photo URLs (large2x).
    orientation: 'portrait' (1080x1920 friendly) or 'landscape'
    """
    import urllib.parse
    import urllib.request
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.pexels.com/v1/search?query={encoded_query}&per_page={count}&orientation={orientation}"
    req = urllib.request.Request(url, headers={"Authorization": api_key})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        photos = data.get("photos", [])
        return [p["src"]["large2x"] for p in photos[:count]]
    except Exception as e:
        logger.error(f"Pexels fetch failed for '{query}': {e}")
        return []


def download_pexels_images(queries: list[str], api_key: str, tmpdir: str) -> list[str]:
    """
    Download one image per query into tmpdir.
    Returns list of local file paths (may be shorter than queries if some fail).
    """
    paths = []
    seen_urls: set[str] = set()

    for i, query in enumerate(queries):
        urls = fetch_pexels_images(query, count=3, api_key=api_key)
        # Pick first URL not already downloaded
        chosen_url = next((u for u in urls if u not in seen_urls), urls[0] if urls else None)
        if not chosen_url:
            logger.warning(f"No Pexels result for query: {query}")
            continue
        seen_urls.add(chosen_url)
        dest = os.path.join(tmpdir, f"img_{i:02d}.jpg")
        if download_file(chosen_url, dest):
            paths.append(dest)
        else:
            logger.warning(f"Failed to download image for '{query}'")
        time.sleep(0.3)  # Rate limit respect

    return paths


def sanitize_filename(text: str, max_len: int = 50) -> str:
    """Convert text to a safe filename slug."""
    import re
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    return slug[:max_len]


def parse_json_from_response(text: str) -> Optional[dict]:
    """Extract JSON object from a possibly-wrapped LLM response."""
    import re
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("```").strip()
    # Find outermost { }
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
