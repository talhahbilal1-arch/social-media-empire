"""
Fetch portrait-orientation images for video backgrounds.
Primary: Nano Banana (Gemini AI) — on-brand, no stock photo feel.
Fallback: Pexels stock photos.
Returns local file paths after downloading/generating.
"""

import json
import logging
import urllib.request
from pathlib import Path
from typing import Optional

from .config import get_api_key

logger = logging.getLogger(__name__)


def _try_nano_banana(query: str, brand: str, output_path: Path) -> bool:
    """Try generating a video background image via Nano Banana (Gemini).

    Uses a landscape/scenery prompt override so images suit video backgrounds
    rather than the portrait pin style.

    Returns True and writes to output_path on success, False on any failure.
    """
    try:
        import sys
        import os
        # Locate project root (two levels up from video_pipeline/)
        project_root = Path(__file__).resolve().parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from video_automation.nano_banana_generator import _get_client
        from google.genai import types as genai_types

        # Landscape prompt suited for video scene backgrounds
        prompt = (
            f"Wide landscape photography, cinematic quality, no people in foreground. "
            f"Scene: {query}. "
            f"Style: wide establishing shot, natural light, rich colors, photorealistic. "
            f"No text, no watermarks, no UI elements. Suitable as a full-screen video background."
        )

        client = _get_client()
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                output_path.write_bytes(part.inline_data.data)
                logger.info(f"Nano Banana: generated video background for '{query[:40]}' → {output_path.name}")
                return True

        return False
    except Exception as e:
        logger.debug(f"Nano Banana video background failed for '{query}': {e}")
        return False


def fetch_portrait_images(
    queries: list[str],
    count: int = 4,
    output_dir: Optional[Path] = None,
    brand: str = "fitness",
) -> list[Path]:
    """
    Download portrait-orientation images from Pexels API.

    Args:
        queries: List of search queries from the script generator
        count: Max number of images to download (default 4)
        output_dir: Directory to save images (default /tmp)

    Returns:
        List of Path objects to downloaded JPEG files
    """
    api_key = get_api_key("PEXELS_API_KEY")

    if output_dir is None:
        output_dir = Path("/tmp")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    downloaded: list[Path] = []

    for i, query in enumerate(queries):
        if len(downloaded) >= count:
            break

        img_path = output_dir / f"img_{i:02d}.jpg"

        # Primary: Nano Banana AI generation (on-brand, wide landscape for video)
        if _try_nano_banana(query, brand, img_path):
            downloaded.append(img_path)
            logger.info(f"NanoBanana [{len(downloaded)}/{count}]: {img_path.name} ← '{query}'")
            continue

        # Fallback: Pexels stock photos
        try:
            url = (
                "https://api.pexels.com/v1/search"
                f"?query={urllib.request.quote(query)}"
                "&orientation=portrait&per_page=1&size=large"
            )
            req = urllib.request.Request(
                url,
                headers={"Authorization": api_key, "User-Agent": "VideoPipeline/1.0"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())

            photos = data.get("photos", [])
            if not photos:
                logger.warning(f"No Pexels results for query: '{query}'")
                continue

            photo = photos[0]
            # portrait is ~1080x1620, original can be huge — portrait is ideal
            img_url = photo["src"].get("portrait") or photo["src"].get("original")

            img_req = urllib.request.Request(
                img_url,
                headers={"User-Agent": "VideoPipeline/1.0"},
            )
            with urllib.request.urlopen(img_req, timeout=30) as img_resp:
                with open(img_path, "wb") as f:
                    f.write(img_resp.read())

            downloaded.append(img_path)
            logger.info(f"Pexels [{len(downloaded)}/{count}]: {img_path.name} ← '{query}'")

        except Exception as e:
            logger.warning(f"Pexels fetch failed for '{query}': {e}")
            continue

    if not downloaded:
        raise RuntimeError(
            f"No images downloaded from Pexels. Check PEXELS_API_KEY and queries: {queries}"
        )

    logger.info(f"Pexels: {len(downloaded)} images saved to {output_dir}")
    return downloaded
