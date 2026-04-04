"""
Post rendered videos to Pinterest (via Make.com webhook) and YouTube Shorts (OAuth2).
Saves metadata JSON alongside video for tracking.
"""

import json
import logging
import mimetypes
import os
import time
import urllib.request
import urllib.error
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import BrandConfig, get_api_key

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# catbox.moe — anonymous public file host
# ---------------------------------------------------------------------------

def _upload_to_catbox(video_path: Path) -> Optional[str]:
    """
    Upload a local video file to catbox.moe and return its public URL.

    Uses multipart/form-data with fields: reqtype=fileupload, fileToUpload=<binary>.
    Returns None on failure so callers can fall back gracefully.
    """
    url = "https://catbox.moe/user/api.php"
    boundary = uuid.uuid4().hex

    mime_type = mimetypes.guess_type(str(video_path))[0] or "video/mp4"

    try:
        file_data = video_path.read_bytes()
    except OSError as e:
        logger.error(f"Cannot read video for catbox upload: {e}")
        return None

    # Build multipart body manually (no external deps)
    body_parts = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"reqtype\"\r\n\r\nfileupload",
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="fileToUpload"; filename="{video_path.name}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ),
    ]

    body = (
        body_parts[0].encode() + b"\r\n" +
        body_parts[1].encode() + file_data +
        f"\r\n--{boundary}--\r\n".encode()
    )

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    logger.info(f"Uploading {video_path.name} ({len(file_data) // 1024}KB) to catbox.moe ...")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            public_url = resp.read().decode("utf-8").strip()

        if public_url.startswith("https://"):
            logger.info(f"catbox.moe upload OK: {public_url}")
            return public_url

        logger.error(f"Unexpected catbox.moe response: {public_url}")
        return None

    except Exception as e:
        logger.error(f"catbox.moe upload failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Pinterest via Make.com webhook
# ---------------------------------------------------------------------------

def post_to_pinterest(
    brand: BrandConfig,
    video_path: Path,
    script_data: dict,
    supabase_video_url: Optional[str] = None,
) -> dict:
    """
    POST video metadata to Make.com webhook for Pinterest upload.

    Make.com receives the webhook and handles the actual Pinterest API call.
    Sends the Supabase public URL of the video (not the raw file).

    Args:
        brand: BrandConfig for this post
        video_path: Local path to the MP4 (used for metadata)
        script_data: Script dict from script_generator
        supabase_video_url: Public URL of the uploaded video (required for Pinterest)

    Returns:
        dict with status and webhook response
    """
    webhook_url = brand.pinterest_webhook_url
    if not webhook_url:
        env_var = brand.pinterest_webhook_env or "MAKE_WEBHOOK_<BRAND>"
        logger.warning(
            f"Pinterest webhook URL not configured for brand '{brand.key}'. "
            f"Set env var '{env_var}' to enable posting. Skipping."
        )
        return {"platform": "pinterest", "status": "skipped", "reason": "webhook_url_not_configured"}

    # Upload video to catbox.moe to get a publicly reachable URL for Pinterest
    public_video_url = _upload_to_catbox(video_path)
    if not public_video_url:
        logger.warning("catbox.moe upload failed; falling back to supabase_video_url")
        public_video_url = supabase_video_url or ""

    # Build hashtag string
    hashtags = " ".join(script_data.get("hashtags", []))

    payload = {
        "brand": brand.key,
        "brand_name": brand.name,
        "title": script_data["title"],
        "description": f"{script_data['hook']}\n\n{hashtags}",
        "video_url": public_video_url,
        "image_url": public_video_url,  # Make.com uses image_url for the pin thumbnail
        "link": brand.site_url,
        "affiliate_tag": brand.affiliate_tag,
        "pin_type": "video",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    payload_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload_bytes,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    logger.info(f"Posting to Pinterest webhook: {brand.key}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            response_text = resp.read().decode("utf-8")
            status_code = resp.status

        logger.info(f"Pinterest webhook response: {status_code} — {response_text[:200]}")
        return {
            "platform": "pinterest",
            "status": "posted" if status_code == 200 else "warning",
            "status_code": status_code,
            "response": response_text,
            "payload": payload,
        }

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        logger.error(f"Pinterest webhook HTTP error {e.code}: {body}")
        return {
            "platform": "pinterest",
            "status": "failed",
            "status_code": e.code,
            "error": body,
        }
    except Exception as e:
        logger.error(f"Pinterest webhook request failed: {e}")
        return {
            "platform": "pinterest",
            "status": "failed",
            "error": str(e),
        }


# ---------------------------------------------------------------------------
# YouTube Shorts via google-api-python-client
# ---------------------------------------------------------------------------

def _get_youtube_service(credentials_path: Optional[Path] = None):
    """Build an authenticated YouTube API client using OAuth2 refresh token."""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        raise RuntimeError(
            "google-api-python-client not installed. "
            "Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )

    client_id = get_api_key("YOUTUBE_CLIENT_ID")
    client_secret = get_api_key("YOUTUBE_CLIENT_SECRET")
    refresh_token = get_api_key("YOUTUBE_REFRESH_TOKEN")
    token_uri = "https://oauth2.googleapis.com/token"

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )

    # Force token refresh
    creds.refresh(Request())

    return build("youtube", "v3", credentials=creds)


def post_to_youtube(
    brand: BrandConfig,
    video_path: Path,
    script_data: dict,
    privacy_status: str = "public",
) -> dict:
    """
    Upload video to YouTube as a Short.

    Args:
        brand: BrandConfig
        video_path: Local MP4 path
        script_data: Script dict from script_generator
        privacy_status: "public", "private", or "unlisted"

    Returns:
        dict with status, video_id, and video URL
    """
    try:
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        raise RuntimeError(
            "google-api-python-client not installed. "
            "Run: pip install google-api-python-client"
        )

    hashtags = " ".join(script_data.get("hashtags", []))
    description = (
        f"{script_data['hook']}\n\n"
        + "\n".join(f"• {p}" for p in script_data.get("body_points", []))
        + f"\n\n{hashtags}\n\n#Shorts"
    )

    body = {
        "snippet": {
            "title": script_data["title"][:100],  # YouTube limit
            "description": description[:5000],
            "tags": [t.lstrip("#") for t in script_data.get("hashtags", [])],
            "categoryId": "22",  # People & Blogs
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    logger.info(f"Uploading to YouTube Shorts: {video_path.name}")

    try:
        youtube = _get_youtube_service()
        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=5 * 1024 * 1024,  # 5MB chunks
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                logger.debug(f"YouTube upload progress: {progress}%")

        video_id = response.get("id")
        video_url = f"https://www.youtube.com/shorts/{video_id}"
        logger.info(f"YouTube upload complete: {video_url}")

        return {
            "platform": "youtube",
            "status": "posted",
            "video_id": video_id,
            "video_url": video_url,
        }

    except Exception as e:
        logger.error(f"YouTube upload failed: {e}")
        return {
            "platform": "youtube",
            "status": "failed",
            "error": str(e),
        }


# ---------------------------------------------------------------------------
# Metadata persistence
# ---------------------------------------------------------------------------

def save_metadata(
    video_path: Path,
    brand: BrandConfig,
    script_data: dict,
    post_results: list[dict],
) -> Path:
    """
    Save a JSON metadata file alongside the video for tracking.

    Returns:
        Path to the JSON file
    """
    meta = {
        "brand": brand.key,
        "brand_name": brand.name,
        "video_file": video_path.name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": {
            "title": script_data.get("title"),
            "topic": script_data.get("topic"),
            "hook": script_data.get("hook"),
            "body_points": script_data.get("body_points"),
            "cta": script_data.get("cta"),
            "hashtags": script_data.get("hashtags"),
            "estimated_duration_seconds": script_data.get("estimated_duration_seconds"),
        },
        "post_results": post_results,
    }

    json_path = video_path.with_suffix(".json")
    json_path.write_text(json.dumps(meta, indent=2))
    logger.info(f"Metadata saved: {json_path.name}")
    return json_path


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def post_video(
    brand: BrandConfig,
    video_path: Path,
    script_data: dict,
    platforms: list[str],
    supabase_video_url: Optional[str] = None,
    dry_run: bool = False,
) -> list[dict]:
    """
    Post video to all requested platforms.

    Args:
        brand: BrandConfig
        video_path: Local MP4 file
        script_data: Generated script metadata
        platforms: List of platform names ("pinterest", "youtube")
        supabase_video_url: Public video URL for Pinterest webhook
        dry_run: If True, skip actual API calls

    Returns:
        List of result dicts per platform
    """
    results = []

    for platform in platforms:
        if dry_run:
            logger.info(f"[DRY RUN] Would post to {platform}")
            results.append({"platform": platform, "status": "dry_run"})
            continue

        if platform == "pinterest":
            result = post_to_pinterest(
                brand=brand,
                video_path=video_path,
                script_data=script_data,
                supabase_video_url=supabase_video_url,
            )
        elif platform == "youtube":
            result = post_to_youtube(
                brand=brand,
                video_path=video_path,
                script_data=script_data,
            )
        else:
            logger.warning(f"Unknown platform: {platform}")
            result = {"platform": platform, "status": "skipped", "reason": "unknown platform"}

        results.append(result)
        time.sleep(2)  # Be gentle between platform calls

    save_metadata(
        video_path=video_path,
        brand=brand,
        script_data=script_data,
        post_results=results,
    )

    return results
