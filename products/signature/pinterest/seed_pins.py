"""Seed Blueprint launch pins into Supabase as content_ready rows.

Reads pins.json and inserts each pin into the pinterest_pins table with
status='content_ready'. The next content-engine.yml run picks them up,
renders the image with PIL, uploads to Supabase Storage, and posts via
Make.com — exactly the same path as auto-generated daily pins.

Also logs each pin to content_history so the variety tracker sees them
(matching what content-engine.yml does in Phase 0).

Usage:
    python3 products/signature/pinterest/seed_pins.py --dry-run
    python3 products/signature/pinterest/seed_pins.py --count 1
    python3 products/signature/pinterest/seed_pins.py
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add project root to path so the database/utils modules import cleanly
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PINS_FILE = Path(__file__).parent / "pins.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("seed_pins")


def load_pins() -> list[dict[str, Any]]:
    """Load pin definitions from pins.json."""
    if not PINS_FILE.exists():
        raise FileNotFoundError(f"pins.json not found at {PINS_FILE}")
    with PINS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    pins = data.get("pins", [])
    if not pins:
        raise ValueError("pins.json contains no pins under the 'pins' key")
    return pins


def build_pinterest_pins_row(pin: dict[str, Any]) -> dict[str, Any]:
    """Build a row for the pinterest_pins table.

    Mirrors the schema written by content-engine.yml Phase 0, so the
    rendering loop in Phase 1 picks the row up without modification.
    """
    tips = pin.get("tips", []) or []
    overlay_headline = (pin.get("graphic_title") or pin.get("title") or "")[:60]
    return {
        "brand": pin["brand"],
        "title": pin["title"],
        "description": pin["description"],
        "overlay_headline": overlay_headline,
        "overlay_subtext": tips[0] if tips else "",
        "tips": tips,
        "pexels_search_term": pin.get("image_query", ""),
        "board_id": str(pin["board_id"]),
        "destination_url": pin["link_url"],
        "topic": pin.get("topic", ""),
        "niche": pin.get("category", "product_promotion"),
        "visual_style": pin.get("style", "gradient"),
        "status": "content_ready",
    }


def build_content_history_row(pin: dict[str, Any]) -> dict[str, Any]:
    """Build a row for content_history (variety tracking + dedup)."""
    return {
        "brand": pin["brand"],
        "title": pin["title"],
        "description": pin["description"],
        "topic": pin.get("topic", ""),
        "category": pin.get("category", "product_promotion"),
        "angle_framework": "blueprint_launch_seed",
        "visual_style": pin.get("style", "gradient"),
        "board": "Workouts for Men Over 35",
        "description_opener": "bold_claim",
        "image_query": pin.get("image_query", ""),
        "destination_url": pin["link_url"],
        "posting_method": "seeded",
        "status": "content_ready",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def insert_pin(client: Any, pin: dict[str, Any], dry_run: bool) -> int | None:
    """Insert one pin into pinterest_pins (and content_history). Returns new row ID or None."""
    pp_row = build_pinterest_pins_row(pin)
    ch_row = build_content_history_row(pin)

    label = pin.get("id", pin["title"][:40])
    if dry_run:
        logger.info("[DRY RUN] Would insert pin '%s'", label)
        logger.info("  pinterest_pins payload: %s", json.dumps(pp_row, indent=2))
        return None

    new_id: int | None = None
    try:
        result = client.table("pinterest_pins").insert(pp_row).execute()
        if result.data:
            new_id = result.data[0].get("id")
        logger.info("Inserted pinterest_pins id=%s for '%s'", new_id, label)
    except Exception as e:
        # Schema may be missing extended columns — fall back to core columns only
        # (mirrors the degraded-mode path in content-engine.yml)
        logger.warning("Full insert failed (%s) — retrying with core columns", e)
        core_row = {
            "brand": pp_row["brand"],
            "title": pp_row["title"],
            "description": pp_row["description"],
            "board_id": pp_row["board_id"],
            "destination_url": pp_row["destination_url"],
            "status": "content_ready",
        }
        result = client.table("pinterest_pins").insert(core_row).execute()
        if result.data:
            new_id = result.data[0].get("id")
        logger.warning(
            "Inserted in DEGRADED MODE id=%s — run 002_fix_pinterest_pins_schema.sql in Supabase",
            new_id,
        )

    try:
        client.table("content_history").insert(ch_row).execute()
        logger.info("Logged to content_history for '%s'", label)
    except Exception as e:
        logger.warning("content_history log failed for '%s': %s", label, e)

    return new_id


def get_client() -> Any:
    """Return a raw Supabase client. Prefers the project's wrapper; falls back to env vars."""
    try:
        from database.supabase_client import get_supabase_client
        return get_supabase_client().client
    except Exception as e:
        logger.warning("get_supabase_client() failed (%s); falling back to env vars", e)
        import os
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "").strip()
        key = os.environ.get("SUPABASE_KEY", "").strip()
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in env") from e
        return create_client(url, key)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seed Blueprint launch pins into Supabase as content_ready rows."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be inserted without writing to Supabase.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Limit how many pins to seed this run (omit to seed all).",
    )
    args = parser.parse_args()

    pins = load_pins()
    if args.count is not None:
        if args.count < 1:
            logger.error("--count must be >= 1")
            return 2
        pins = pins[: args.count]
    logger.info("Loaded %d pin(s) to seed (dry_run=%s)", len(pins), args.dry_run)

    client = None if args.dry_run else get_client()

    inserted_ids: list[int] = []
    for pin in pins:
        try:
            new_id = insert_pin(client, pin, args.dry_run)
            if new_id is not None:
                inserted_ids.append(new_id)
        except Exception as e:
            logger.error("Failed to insert '%s': %s", pin.get("id", "?"), e)

    if args.dry_run:
        logger.info("Dry run complete — no rows written")
    else:
        logger.info("Seed complete. New pinterest_pins IDs: %s", inserted_ids)
    return 0


if __name__ == "__main__":
    sys.exit(main())
