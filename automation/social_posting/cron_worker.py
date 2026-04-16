"""Cron worker: post exactly one queued item and exit.

Designed to be called hourly by a GitHub Action. Picks the oldest queue item
(FIFO), posts it to all configured platforms, and moves it to posted/.

Usage::

    python -m automation.social_posting.cron_worker              # dry-run
    python -m automation.social_posting.cron_worker --live       # actually post
    python -m automation.social_posting.cron_worker --platform twitter --live
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

QUEUE_DIR = Path(__file__).parent / "queue"


def _oldest_queue_item() -> Path | None:
    """Return the path of the oldest .json file across all brand subdirs."""
    items: list[Path] = []
    if not QUEUE_DIR.exists():
        return None
    for brand_dir in sorted(QUEUE_DIR.iterdir()):
        if brand_dir.is_dir():
            items.extend(sorted(brand_dir.glob("*.json")))
    return items[0] if items else None


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="Post one queued item")
    parser.add_argument("--live", action="store_true", help="Actually post (default: dry-run)")
    parser.add_argument(
        "--platform",
        choices=["twitter", "linkedin", "all"],
        default="all",
        help="Platform to post to (default: all)",
    )
    args = parser.parse_args()

    item_path = _oldest_queue_item()
    if item_path is None:
        logger.info("Queue is empty -- nothing to post")
        sys.exit(0)

    logger.info("Processing queue item: %s", item_path)

    with open(item_path) as f:
        item_data = json.load(f)

    brand = item_path.parent.name
    logger.info("Brand: %s | Title: %s", brand, item_data.get("title", "untitled"))

    # Delegate to poster with --limit 1
    from .poster import post_items, load_queue_items

    items = load_queue_items(brand_filter=brand, limit=1)
    if not items:
        logger.info("No items loaded for brand %s", brand)
        sys.exit(0)

    results = post_items(
        items,
        live=args.live,
        platform=args.platform,
    )

    posted = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)

    logger.info("Done: %d posted, %d failed", posted, failed)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
