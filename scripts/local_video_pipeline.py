#!/usr/bin/env python3
"""Local video pipeline — Mac-side renderer for Short Video Maker.

Scheduled by launchd (every 8 hours). Polls Supabase for pinterest_pins
rows with video_state='video_pending', renders each through the
localhost:3123 Short Video Maker container, uploads the MP4 + cover to
Supabase Storage, and (for brands with a Pinterest account connected)
posts via Zernio.

The content-engine GitHub Action writes the pending rows; this script
drains the queue. Everything is idempotent at the pin level — a failed
render marks the pin `video_failed` and the next cycle skips it (manual
requeue by flipping state back to `video_pending`).

Usage:
  local_video_pipeline.py                 # drain all pending across all brands
  local_video_pipeline.py --brand fitness # one brand only
  local_video_pipeline.py --limit 1       # cap per run
  local_video_pipeline.py --test          # stub content, no Supabase write
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Make the repo importable when launched directly by launchd.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load .env before importing anything that reads env vars at import time.
try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass  # dotenv is optional — env vars may already be set by launchd/cron

from video_automation.short_video_client import (  # noqa: E402
    generate_video,
    get_brand_config,
    is_short_video_maker_available,
    scenes_from_pin_content,
)
from video_automation.supabase_storage import (  # noqa: E402
    upload_pin_image,
    upload_pin_video,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("local_video_pipeline")

# Brands where Pinterest posting is wired up right now. Others get
# rendered + staged in Supabase Storage so the asset exists, but no post
# is attempted. When a brand's Pinterest account + board IDs are added,
# move its key into this set.
POSTING_BRANDS = {"fitness"}

# Brands this pipeline is allowed to process at all. Keep in sync with
# the content-engine's brand list.
ALL_BRANDS = ("fitness", "deals", "menopause", "pilottools", "homedecor", "beauty")


def _supabase_client():
    """Build a Supabase client using the same env vars as the workflow."""
    from supabase import create_client  # import lazily — SDK is heavy
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


def _query_pending_pins(client, brand: Optional[str], limit: Optional[int]) -> list:
    """Return pins waiting for local render, newest first."""
    q = (
        client.table("pinterest_pins")
        .select("*")
        .eq("video_state", "video_pending")
        .order("created_at", desc=True)
    )
    if brand:
        q = q.eq("brand", brand)
    if limit:
        q = q.limit(limit)
    return q.execute().data or []


def _pin_to_video_content(pin: dict) -> dict:
    """Reconstruct the video_content dict from a Supabase pin row.

    The content-engine serializes the full content_brain dict into
    `content_json` (JSONB). We prefer that. If it's missing (older
    row, hand-created, etc.) we fall back to the scalar columns and
    synthesize a minimal dict — videos from that path will be weaker
    but still renderable.
    """
    raw = pin.get("content_json")
    if raw:
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass
        elif isinstance(raw, dict):
            return raw

    # Fallback path for rows without content_json.
    tips = pin.get("tips") or []
    if isinstance(tips, str):
        try:
            tips = json.loads(tips)
        except json.JSONDecodeError:
            tips = []
    return {
        "hook": pin.get("overlay_headline") or pin.get("title") or "",
        "solution": pin.get("overlay_subtext") or "",
        "cta": "Save This For Later",
        "search_query": pin.get("pexels_search_term") or pin.get("niche") or "",
        "title": pin.get("title", ""),
        "description": pin.get("description", ""),
        "tips": tips,
    }


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _mark(client, pin_id, **updates) -> None:
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    try:
        client.table("pinterest_pins").update(updates).eq("id", pin_id).execute()
    except Exception as e:
        logger.error(f"pin {pin_id}: state update failed — {e}")


def _render_and_upload(brand: str, video_content: dict) -> Optional[dict]:
    """Render via container + upload MP4/cover to Supabase. Returns URLs or None."""
    scenes = scenes_from_pin_content(brand, video_content)
    if not scenes:
        logger.error(f"[{brand}] no scenes produced — skipping")
        return None

    logger.info(f"[{brand}] submitting {len(scenes)}-scene render")
    result = generate_video(brand, scenes, get_brand_config(brand))
    if not result:
        return None

    ts = _timestamp()
    try:
        video_url = upload_pin_video(
            result["video_bytes"], f"{brand}_smv_{ts}.mp4"
        )
    except Exception as e:
        logger.error(f"[{brand}] video upload failed — {e}")
        return None

    cover_url = ""
    if result.get("cover_bytes"):
        try:
            cover_url = upload_pin_image(
                result["cover_bytes"], f"{brand}_smv_cover_{ts}.jpg"
            )
        except Exception as e:
            logger.warning(f"[{brand}] cover upload failed — {e}")

    return {"video_url": video_url, "cover_url": cover_url, "video_id": result["video_id"]}


def _post_to_pinterest(brand: str, pin: dict, video_url: str) -> Optional[dict]:
    """Post via Zernio for brands we have a Pinterest account on. Returns the
    post result dict, or None if skipped/failed. Never raises."""
    from video_automation.pinterest_boards import get_board_id
    from video_automation.zernio_poster import is_zernio_configured, post_video_pin

    if brand not in POSTING_BRANDS:
        logger.info(f"[{brand}] skipping Pinterest post — brand not connected")
        return None
    if not is_zernio_configured():
        logger.warning(f"[{brand}] ZERNIO_API_KEY not set — skipping post")
        return None

    board_name = pin.get("board") or ""
    board_id = get_board_id(brand, board_name) or ""
    if not board_id or board_id == "PENDING":
        logger.warning(f"[{brand}] no board ID for '{board_name}' — skipping post")
        return None

    dest_url = pin.get("destination_url") or ""
    try:
        return post_video_pin(
            video_url=video_url,
            title=(pin.get("title") or "")[:100],
            description=(pin.get("description") or "")[:500],
            board_id=str(board_id),
            link=dest_url,
        )
    except Exception as e:
        logger.error(f"[{brand}] Zernio post errored — {e}")
        return None


def _process_pin(client, pin: dict) -> str:
    """Render, upload, optionally post one pin. Returns final video_state."""
    pin_id = pin["id"]
    brand = pin.get("brand") or "fitness"
    logger.info(f"pin {pin_id} [{brand}] starting")

    video_content = _pin_to_video_content(pin)

    upload = _render_and_upload(brand, video_content)
    if not upload:
        _mark(client, pin_id, video_state="video_failed",
              error_message="render or upload failed")
        return "video_failed"

    _mark(
        client, pin_id,
        video_state="video_ready",
        generated_image_url=upload["video_url"],
        background_image_url=upload["cover_url"] or None,
    )
    logger.info(f"pin {pin_id} [{brand}] video_ready → {upload['video_url']}")

    post_result = _post_to_pinterest(brand, pin, upload["video_url"])
    if post_result and post_result.get("status") == "success":
        _mark(
            client, pin_id,
            video_state="video_posted",
            status="posted",
            posted_at=datetime.now(timezone.utc).isoformat(),
            pin_id=post_result.get("pin_id") or None,
        )
        logger.info(f"pin {pin_id} [{brand}] posted → {post_result.get('pin_url', '')}")
        return "video_posted"

    return "video_ready"


def _test_one() -> None:
    """Render one stub video for fitness. No Supabase writes. Smoke-test only."""
    if not is_short_video_maker_available():
        logger.error("container at localhost:3123 is down — start Docker Desktop")
        sys.exit(1)

    stub = {
        "hook": "Why fat loss stops after 35",
        "solution": "Your hormones need a different approach now",
        "cta": "Save this for later",
        "search_query": "man exercising",
        "tips": [
            "Cut alcohol to one drink per week max",
            "Lift weights three times a week for strength",
            "Eat protein at every meal for satiety",
            "Walk ten thousand steps daily to stay mobile",
        ],
    }
    scenes = scenes_from_pin_content("fitness", stub)
    logger.info(f"submitting {len(scenes)}-scene test render")
    start = time.monotonic()
    result = generate_video("fitness", scenes, get_brand_config("fitness"))
    if not result:
        logger.error("test render failed")
        sys.exit(1)
    elapsed = time.monotonic() - start

    out_dir = REPO_ROOT / "temp"
    out_dir.mkdir(exist_ok=True)
    video_out = out_dir / f"smv_test_{_timestamp()}.mp4"
    video_out.write_bytes(result["video_bytes"])
    cover_out = video_out.with_suffix(".jpg")
    if result.get("cover_bytes"):
        cover_out.write_bytes(result["cover_bytes"])
    logger.info(f"test render OK in {elapsed:.1f}s → {video_out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brand", choices=ALL_BRANDS)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--test", action="store_true",
                        help="render one stub video, no Supabase interaction")
    args = parser.parse_args()

    if args.test:
        _test_one()
        return

    if not is_short_video_maker_available():
        logger.warning("short_video_maker container is down — exiting cleanly")
        return

    client = _supabase_client()
    pins = _query_pending_pins(client, args.brand, args.limit)
    if not pins:
        logger.info("no pins with video_state=video_pending — nothing to do")
        return

    logger.info(f"found {len(pins)} pending pins")
    for pin in pins:
        try:
            _process_pin(client, pin)
        except Exception as e:
            logger.exception(f"pin {pin.get('id')} crashed: {e}")
            try:
                _mark(client, pin["id"], video_state="video_failed",
                      error_message=str(e)[:500])
            except Exception:
                pass


if __name__ == "__main__":
    main()
