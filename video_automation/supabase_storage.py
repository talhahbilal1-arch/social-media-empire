"""Supabase Storage utility for uploading rendered pin images.

Uploads JPEG images to a public 'pin-images' bucket and returns
the public URL for use in Make.com webhook payloads.

Uses the Supabase Storage REST API directly (no SDK dependency).
"""

import os
import logging
import requests
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

BUCKET_NAME = "pin-images"


def _get_storage_config():
    """Get Supabase URL and service role key from environment."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    return url, key


def _storage_headers(key):
    """Build headers for Supabase Storage REST API."""
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }


def ensure_bucket(url, key):
    """Create the pin-images bucket if it doesn't exist."""
    headers = _storage_headers(key)
    headers["Content-Type"] = "application/json"

    # Check if bucket exists
    resp = requests.get(
        f"{url}/storage/v1/bucket/{BUCKET_NAME}",
        headers=headers,
        timeout=15,
    )
    if resp.status_code == 200:
        return  # Already exists

    # Create public bucket
    resp = requests.post(
        f"{url}/storage/v1/bucket",
        headers=headers,
        json={
            "id": BUCKET_NAME,
            "name": BUCKET_NAME,
            "public": True,
        },
        timeout=15,
    )
    if resp.status_code in (200, 201):
        logger.info(f"Created Supabase Storage bucket: {BUCKET_NAME}")
    else:
        # Bucket may already exist (race condition) — that's fine
        if "already exists" not in resp.text.lower():
            logger.warning(f"Bucket creation response: {resp.status_code} {resp.text[:200]}")


def upload_pin_image(image_bytes, filename):
    """Upload a rendered pin image to Supabase Storage.

    Args:
        image_bytes: JPEG image as bytes (from BytesIO.getvalue())
        filename: Target filename (e.g. 'fitness_20260216_143022.jpg')

    Returns:
        Public URL string for the uploaded image.
    """
    url, key = _get_storage_config()
    ensure_bucket(url, key)

    headers = _storage_headers(key)
    headers["Content-Type"] = "image/jpeg"

    # Upload (upsert to overwrite if exists)
    upload_url = f"{url}/storage/v1/object/{BUCKET_NAME}/{filename}"
    resp = requests.post(
        upload_url,
        headers=headers,
        data=image_bytes,
        timeout=30,
    )

    if resp.status_code in (200, 201):
        public_url = f"{url}/storage/v1/object/public/{BUCKET_NAME}/{filename}"
        logger.info(f"Uploaded pin image: {public_url}")
        return public_url

    # Try upsert if file already exists
    if resp.status_code == 409:
        headers["x-upsert"] = "true"
        resp = requests.post(
            upload_url,
            headers=headers,
            data=image_bytes,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{url}/storage/v1/object/public/{BUCKET_NAME}/{filename}"
            return public_url

    raise RuntimeError(
        f"Failed to upload pin image: {resp.status_code} {resp.text[:300]}"
    )


def cleanup_old_images(max_age_days=7):
    """Delete pin images older than max_age_days from Supabase Storage.

    Returns number of files deleted.
    """
    url, key = _get_storage_config()
    headers = _storage_headers(key)
    headers["Content-Type"] = "application/json"

    # List all files in the bucket
    resp = requests.post(
        f"{url}/storage/v1/object/list/{BUCKET_NAME}",
        headers=headers,
        json={"prefix": "", "limit": 1000},
        timeout=30,
    )

    if resp.status_code != 200:
        logger.warning(f"Failed to list storage files: {resp.status_code}")
        return 0

    files = resp.json()
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    to_delete = []

    for f in files:
        # Supabase returns created_at in ISO format
        created = f.get("created_at", "")
        if not created:
            continue
        try:
            file_date = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if file_date < cutoff:
                to_delete.append(f["name"])
        except (ValueError, KeyError):
            continue

    if not to_delete:
        logger.info("No old pin images to clean up")
        return 0

    # Delete in batch
    resp = requests.delete(
        f"{url}/storage/v1/object/{BUCKET_NAME}",
        headers=headers,
        json={"prefixes": to_delete},
        timeout=30,
    )

    if resp.status_code in (200, 201):
        logger.info(f"Cleaned up {len(to_delete)} old pin images")
    else:
        logger.warning(f"Cleanup response: {resp.status_code} {resp.text[:200]}")

    return len(to_delete)
