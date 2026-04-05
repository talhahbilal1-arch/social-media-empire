"""
Upload a rendered video + thumbnail to catbox.moe, then write a pending-post JSON
to output/_pending_posts/ for downstream pickup (Make.com, manual retry, etc.).

Usage (CLI):
    python -m video_pipeline.auto_post_pinterest \
        --video output/deals_20260405_061358.mp4 \
        --brand deals \
        --title "5 Amazon Finds Under $25" \
        --description "Deal alert! #amazonfind"

Usage (imported):
    from video_pipeline.auto_post_pinterest import auto_post_pinterest
    result = auto_post_pinterest(video_path, brand_key, script_data)
"""

import argparse
import json
import logging
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import get_brand, load_env

logger = logging.getLogger(__name__)

PENDING_DIR = Path(__file__).parent.parent / "output" / "_pending_posts"
CATBOX_URL = "https://catbox.moe/user/api.php"


def upload_to_catbox(file_path: Path) -> str:
    """
    Upload a file to catbox.moe and return its public URL.

    Uses multipart/form-data POST — no auth required.
    Returns a URL like https://files.catbox.moe/xxxxxx.mp4
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info(f"Uploading {file_path.name} to catbox.moe ({file_path.stat().st_size / 1_000_000:.1f} MB)...")

    # Use curl subprocess — urllib doesn't have clean multipart file upload support
    cmd = [
        "curl", "-s",
        "-X", "POST",
        "-F", "reqtype=fileupload",
        "-F", f"fileToUpload=@{file_path}",
        CATBOX_URL,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        raise RuntimeError(f"curl failed (exit {result.returncode}): {result.stderr}")

    url = result.stdout.strip()
    if not url.startswith("https://"):
        raise RuntimeError(f"Unexpected catbox response: {url!r}")

    logger.info(f"Uploaded → {url}")
    return url


def extract_thumbnail(video_path: Path, thumbnail_path: Optional[Path] = None) -> Path:
    """
    Extract a thumbnail from the first frame of a video using ffmpeg.

    Args:
        video_path: Path to the MP4
        thumbnail_path: Where to save the thumbnail (defaults to same dir, .jpg)

    Returns:
        Path to the saved thumbnail
    """
    video_path = Path(video_path)
    if thumbnail_path is None:
        thumbnail_path = video_path.with_suffix(".thumb.jpg")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        str(thumbnail_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg thumbnail failed: {result.stderr[-500:]}")

    logger.info(f"Thumbnail extracted: {thumbnail_path.name}")
    return thumbnail_path


def auto_post_pinterest(
    video_path: Path,
    brand_key: str,
    script_data: dict,
) -> dict:
    """
    Full catbox.moe upload + pending-post JSON writer.

    Steps:
      1. Upload video to catbox.moe → video_url
      2. Extract thumbnail frame
      3. Upload thumbnail to catbox.moe → cover_url
      4. Write JSON to output/_pending_posts/{brand}_{ts}.json
      5. Clean up local thumbnail

    Args:
        video_path: Path to the rendered MP4
        brand_key: Brand key (e.g. "deals", "fitover35", "menopause")
        script_data: Output from script_generator.generate_script()

    Returns:
        dict with status, video_url, cover_url, pending_json_path
    """
    video_path = Path(video_path)
    brand = get_brand(brand_key)
    PENDING_DIR.mkdir(parents=True, exist_ok=True)

    thumbnail_path = video_path.with_suffix(".thumb.jpg")

    try:
        # 1. Upload video
        video_url = upload_to_catbox(video_path)

        # 2. Extract + upload thumbnail
        extract_thumbnail(video_path, thumbnail_path)
        cover_url = upload_to_catbox(thumbnail_path)

        # 3. Build payload
        hashtags = " ".join(script_data.get("hashtags", []))
        description = f"{script_data.get('hook', '')}\n\n{hashtags}".strip()

        payload = {
            "brand": brand_key,
            "brand_name": brand.name,
            "title": script_data.get("title", ""),
            "description": description,
            "video_url": video_url,
            "cover_url": cover_url,
            "affiliate_tag": brand.affiliate_tag,
            "site_url": brand.site_url,
            "pin_type": "video",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # 4. Write pending JSON
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        json_path = PENDING_DIR / f"{brand_key}_{ts}.json"
        json_path.write_text(json.dumps(payload, indent=2))
        logger.info(f"Pending post written: {json_path.name}")

        return {
            "status": "pending",
            "platform": "pinterest",
            "video_url": video_url,
            "cover_url": cover_url,
            "pending_json_path": str(json_path),
        }

    except Exception as e:
        logger.error(f"auto_post_pinterest failed: {e}")
        return {
            "status": "failed",
            "platform": "pinterest",
            "error": str(e),
        }

    finally:
        if thumbnail_path.exists():
            thumbnail_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Upload video + thumbnail to catbox.moe and queue for Pinterest")
    parser.add_argument("--video", required=True, help="Path to rendered MP4")
    parser.add_argument("--brand", required=True, help="Brand key (deals, fitover35, menopause)")
    parser.add_argument("--title", default="", help="Pin title")
    parser.add_argument("--description", default="", help="Pin description / hook")
    args = parser.parse_args()

    load_env()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    script_data = {
        "title": args.title,
        "hook": args.description,
        "hashtags": [],
    }

    result = auto_post_pinterest(
        video_path=Path(args.video),
        brand_key=args.brand,
        script_data=script_data,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
