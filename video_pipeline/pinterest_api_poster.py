"""
Pinterest video poster via catbox.moe + Make.com webhook.

Flow:
    1. Upload video MP4 to catbox.moe → get public video_url
    2. Extract thumbnail frame with FFmpeg → upload to catbox.moe → get cover_image_url
    3. POST {video_url, cover_image_url, title, description, board_id} to brand's Make.com webhook

The Make.com scenario (5-module) receives the webhook and handles the full Pinterest video upload.

Usage (as library):
    from video_pipeline.pinterest_api_poster import post_video_pin
    result = post_video_pin(brand_key="deals", video_path=Path("output/deals_xxx.mp4"), script_data={...})

Usage (direct):
    python -m video_pipeline.pinterest_api_poster --brand deals --video output/deals_xxx.mp4
"""

import json
import logging
import os
import subprocess
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

from .config import get_brand, BrandConfig, load_env, FFMPEG_BIN

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────

CATBOX_URL = "https://catbox.moe/user/api.php"

# Make.com webhook URLs — these NEW scenarios handle the full video upload flow
WEBHOOKS: dict[str, str] = {
    "deals":     os.getenv("MAKE_WEBHOOK_DEALS",     "https://hook.us2.make.com/cstwukwmwmnnfq1x82o4dlu2d5wzk43l"),
    "fitover35": os.getenv("MAKE_WEBHOOK_FITNESS",   "https://hook.us2.make.com/3j53k464d7hpaxy9o2fs5akprb8aj2nk"),
    "menopause": os.getenv("MAKE_WEBHOOK_MENOPAUSE", "https://hook.us2.make.com/7lrqz32lfrtdc0nkhv9z4whraxvuyo3x"),
}

# Pinterest board IDs per brand (these boards must exist on the Pinterest account)
BOARD_IDS: dict[str, str] = {
    "deals":     "874683627569021288",   # Amazon Finds
    "fitover35": "418834902785125486",   # Muscle building
    "menopause": "1076993767079887530",  # Wellness Tips
}


# ── catbox.moe upload ──────────────────────────────────────────────────────────

def _upload_to_catbox(file_path: Path) -> str:
    """
    Upload a file to catbox.moe and return the public direct URL.

    Uses multipart/form-data with reqtype=fileupload (no auth required).
    Raises RuntimeError if the upload fails or returns a non-URL response.
    """
    logger.info(f"Uploading to catbox.moe: {file_path.name} ({file_path.stat().st_size // 1024} KB)")

    boundary = "----CatboxBoundary7MA4YWxkTrZu0gW"
    file_bytes = file_path.read_bytes()
    mime_type = "video/mp4" if file_path.suffix.lower() == ".mp4" else "image/jpeg"

    # Build multipart body manually (no external deps)
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="reqtype"\r\n\r\n'
        f"fileupload\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="fileToUpload"; filename="{file_path.name}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        CATBOX_URL,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "social-media-empire/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = resp.read().decode("utf-8").strip()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"catbox.moe HTTP error {e.code}: {e.read().decode('utf-8', errors='replace')}")
    except Exception as e:
        raise RuntimeError(f"catbox.moe upload failed: {e}")

    if not result.startswith("https://"):
        raise RuntimeError(f"catbox.moe returned unexpected response: {result!r}")

    logger.info(f"catbox.moe upload complete: {result}")
    return result


# ── Thumbnail extraction ───────────────────────────────────────────────────────

def _extract_thumbnail(video_path: Path, timestamp: str = "00:00:01") -> Path:
    """
    Extract a single frame from the video using FFmpeg.

    Args:
        video_path: Path to the MP4 file
        timestamp: Time offset for the frame (default: 1 second in)

    Returns:
        Path to the extracted JPEG thumbnail (in a temp dir)

    Raises:
        RuntimeError if FFmpeg fails
    """
    thumb_path = video_path.parent / f"_thumb_{video_path.stem}.jpg"
    cmd = [
        FFMPEG_BIN, "-y",
        "-ss", timestamp,
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",          # JPEG quality (2 = high quality)
        str(thumb_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode != 0:
            stderr = result.stderr.decode("utf-8", errors="replace")
            raise RuntimeError(f"FFmpeg thumbnail extraction failed: {stderr[-300:]}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg thumbnail extraction timed out")

    if not thumb_path.exists() or thumb_path.stat().st_size == 0:
        raise RuntimeError(f"FFmpeg produced empty thumbnail at {thumb_path}")

    logger.info(f"Thumbnail extracted: {thumb_path.name} ({thumb_path.stat().st_size // 1024} KB)")
    return thumb_path


# ── Webhook POST ───────────────────────────────────────────────────────────────

def _post_to_webhook(
    webhook_url: str,
    brand: BrandConfig,
    video_url: str,
    cover_image_url: str,
    script_data: dict,
) -> dict:
    """
    POST the pin payload to the Make.com webhook URL.

    Returns a result dict with keys: status, status_code, response, error.
    """
    board_id = BOARD_IDS.get(brand.key, "")
    hashtags = " ".join(script_data.get("hashtags", brand.hashtags))
    description = f"{script_data.get('hook', '')}\n\n{hashtags}"[:500]

    # Build the pin creation body with MEDIA_ID_PLACEHOLDER
    # Make.com will replace this with the actual media_id from the /v5/media registration
    pin_body = json.dumps({
        "board_id": board_id,
        "title": script_data.get("title", brand.name)[:100],
        "description": description,
        "link": brand.site_url,
        "media_source": {
            "source_type": "video_id",
            "cover_image_url": cover_image_url,
            "media_id": "MEDIA_ID_PLACEHOLDER",
        },
    })

    payload = {
        "brand":           brand.key,
        "title":           script_data.get("title", brand.name)[:100],
        "description":     description,
        "video_url":       video_url,
        "cover_image_url": cover_image_url,
        "board_id":        board_id,
        "link":            brand.site_url,
        "pin_body":        pin_body,
    }

    payload_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload_bytes,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    logger.info(f"POSTing to Make.com webhook: brand={brand.key}, board={board_id}")
    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            response_text = resp.read().decode("utf-8").strip()
            status_code = resp.status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logger.error(f"Webhook HTTP error {e.code}: {body}")
        return {"status": "failed", "status_code": e.code, "error": body}
    except Exception as e:
        logger.error(f"Webhook request failed: {e}")
        return {"status": "failed", "error": str(e)}

    logger.info(f"Webhook response: {status_code} — {response_text[:200]}")
    return {
        "status":      "posted" if status_code == 200 else "warning",
        "status_code": status_code,
        "response":    response_text,
        "payload":     payload,
    }


# ── Public API ─────────────────────────────────────────────────────────────────

def post_video_pin(
    brand_key: str,
    video_path: Path,
    script_data: dict,
    dry_run: bool = False,
) -> dict:
    """
    Full 3-step Pinterest video posting flow:
        1. Upload video to catbox.moe
        2. Extract + upload thumbnail to catbox.moe
        3. POST to Make.com webhook

    Args:
        brand_key:   One of "deals", "fitover35", "menopause"
        video_path:  Path to the rendered .mp4 file
        script_data: Script dict from script_generator (title, hook, hashtags, …)
        dry_run:     Log what would happen but don't upload or POST

    Returns:
        dict with keys: platform, status, video_url, cover_image_url, response, error
    """
    video_path = Path(video_path).resolve()
    brand = get_brand(brand_key)

    webhook_url = WEBHOOKS.get(brand_key)
    if not webhook_url:
        logger.warning(f"No Make.com webhook configured for brand '{brand_key}'")
        return {"platform": "pinterest", "status": "skipped", "reason": "no_webhook"}

    if not video_path.exists():
        return {"platform": "pinterest", "status": "failed", "error": f"Video not found: {video_path}"}

    if dry_run:
        logger.info(f"[DRY RUN] Would post: {video_path.name} → Pinterest | brand={brand_key}")
        return {"platform": "pinterest", "status": "dry_run", "brand": brand_key}

    result: dict = {"platform": "pinterest", "status": "failed", "brand": brand_key}
    thumb_path: Optional[Path] = None

    try:
        # Step 1: Upload video
        video_url = _upload_to_catbox(video_path)
        result["video_url"] = video_url

        # Step 2: Extract + upload thumbnail
        thumb_path = _extract_thumbnail(video_path)
        cover_image_url = _upload_to_catbox(thumb_path)
        result["cover_image_url"] = cover_image_url

        # Step 3: POST to webhook
        webhook_result = _post_to_webhook(
            webhook_url=webhook_url,
            brand=brand,
            video_url=video_url,
            cover_image_url=cover_image_url,
            script_data=script_data,
        )
        result.update(webhook_result)

    except RuntimeError as e:
        logger.error(f"Pinterest post failed for {brand_key}: {e}")
        result["error"] = str(e)
    finally:
        # Clean up temp thumbnail
        if thumb_path and thumb_path.exists():
            try:
                thumb_path.unlink()
            except Exception:
                pass

    return result


# ── CLI entrypoint ─────────────────────────────────────────────────────────────

def main():
    import argparse
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    load_env()

    parser = argparse.ArgumentParser(description="Post a rendered video to Pinterest via Make.com")
    parser.add_argument("--brand", required=True, choices=list(WEBHOOKS.keys()), help="Brand key")
    parser.add_argument("--video", required=True, help="Path to the rendered .mp4 file")
    parser.add_argument("--title", default=None, help="Override pin title")
    parser.add_argument("--dry-run", action="store_true", help="Log only, don't upload or POST")
    args = parser.parse_args()

    brand = get_brand(args.brand)
    script_data = {
        "title":    args.title or f"{brand.name} — {Path(args.video).stem.replace('_', ' ')}",
        "hook":     brand.hook_styles[0].replace("{topic}", brand.topics[0]) if brand.hook_styles else "",
        "hashtags": brand.hashtags,
    }

    result = post_video_pin(
        brand_key=args.brand,
        video_path=Path(args.video),
        script_data=script_data,
        dry_run=args.dry_run,
    )

    print(json.dumps(result, indent=2))
    if result.get("status") not in ("posted", "dry_run"):
        sys.exit(1)


if __name__ == "__main__":
    main()
