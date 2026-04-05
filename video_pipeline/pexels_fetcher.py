"""
Fetch portrait-orientation images from Pexels for video backgrounds.
Returns local file paths after downloading.
"""

import json
import logging
import urllib.request
from pathlib import Path
from typing import Optional

from .config import get_api_key

logger = logging.getLogger(__name__)


def fetch_portrait_images(
    queries: list[str],
    count: int = 4,
    output_dir: Optional[Path] = None,
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
            img_path = output_dir / f"img_{i:02d}.jpg"

            img_req = urllib.request.Request(
                img_url,
                headers={"User-Agent": "VideoPipeline/1.0"},
            )
            with urllib.request.urlopen(img_req, timeout=30) as img_resp:
                with open(img_path, "wb") as f:
                    f.write(img_resp.read())

            downloaded.append(img_path)
            logger.info(f"Downloaded [{len(downloaded)}/{count}]: {img_path.name} ← '{query}'")

        except Exception as e:
            logger.warning(f"Pexels fetch failed for '{query}': {e}")
            continue

    if not downloaded:
        raise RuntimeError(
            f"No images downloaded from Pexels. Check PEXELS_API_KEY and queries: {queries}"
        )

    logger.info(f"Pexels: {len(downloaded)} images saved to {output_dir}")
    return downloaded
