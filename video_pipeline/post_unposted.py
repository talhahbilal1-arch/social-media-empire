"""
Scan output/ for unposted videos and post them to Pinterest.

A video is considered "posted" when a sibling .posted.json file exists
alongside the .mp4.  This script finds all .mp4 files lacking that
sentinel, posts them, and writes the sentinel on success.

Usage:
    python -m video_pipeline.post_unposted               # post all brands
    python -m video_pipeline.post_unposted --brand deals # deals only
    python -m video_pipeline.post_unposted --dry-run     # log only, no posting
    python -m video_pipeline.post_unposted --headed      # headed browser (first login)

Output directory is resolved as:
    <repo-root>/output/       (siblings: .mp4 and .posted.json files)
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from .config import load_env, BRANDS, get_brand
from .pinterest_poster import post_pin

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "output"
STALE_AFTER_HOURS = 48  # Skip videos older than this


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_brand_from_filename(mp4_path: Path) -> Optional[str]:
    """
    Infer brand key from filename.

    Filename pattern: {brand}_{YYYYMMDD_HHMMSS}.mp4
    e.g. deals_20260404_160613.mp4 → "deals"
    """
    stem = mp4_path.stem  # e.g. "deals_20260404_160613"
    for brand_key in BRANDS:
        if stem.startswith(brand_key + "_") or stem == brand_key:
            return brand_key
    return None


def _is_stale(mp4_path: Path) -> bool:
    """Return True if the video is older than STALE_AFTER_HOURS."""
    mtime = datetime.fromtimestamp(mp4_path.stat().st_mtime, tz=timezone.utc)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=STALE_AFTER_HOURS)
    return mtime < cutoff


def _load_script_data(mp4_path: Path) -> Optional[dict]:
    """
    Try to load script_data from a sibling .json file (the metadata saved by
    the video pipeline's poster.save_metadata()).  Returns None if absent.
    """
    json_path = mp4_path.with_suffix(".json")
    if json_path.exists():
        try:
            data = json.loads(json_path.read_text())
            # poster.save_metadata() nests script data under "script" key
            return data.get("script") or data
        except Exception as e:
            logger.warning(f"Could not parse {json_path.name}: {e}")
    return None


def _write_posted_sentinel(mp4_path: Path, result: dict) -> Path:
    """
    Write <video>.posted.json alongside the video to mark it as posted.
    Returns the path to the sentinel file.
    """
    sentinel_path = mp4_path.with_suffix(".posted.json")
    sentinel_path.write_text(json.dumps(result, indent=2))
    logger.info(f"Wrote sentinel: {sentinel_path.name}")
    return sentinel_path


def _find_unposted_videos(output_dir: Path, brand_filter: Optional[str] = None) -> list[Path]:
    """
    Return a sorted list of .mp4 files in output_dir that:
      - have no sibling .posted.json
      - are not stale (within 48h)
      - match brand_filter (if provided)

    Sorted oldest-first so we post in chronological order.
    """
    if not output_dir.exists():
        logger.warning(f"Output directory not found: {output_dir}")
        return []

    videos = sorted(output_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
    unposted = []

    for mp4 in videos:
        # Skip temp/error files
        if mp4.parent.name in ("_temp", "_errors"):
            continue

        # Already posted?
        if mp4.with_suffix(".posted.json").exists():
            logger.debug(f"Already posted: {mp4.name}")
            continue

        # Brand filter
        brand_key = _extract_brand_from_filename(mp4)
        if brand_key is None:
            logger.warning(f"Cannot determine brand from filename: {mp4.name} — skipping")
            continue
        if brand_filter and brand_key != brand_filter:
            continue

        # Stale check
        if _is_stale(mp4):
            logger.info(f"Skipping stale video (>{STALE_AFTER_HOURS}h): {mp4.name}")
            continue

        unposted.append(mp4)

    return unposted


# ── Main logic ────────────────────────────────────────────────────────────────

def run(
    brand_filter: Optional[str] = None,
    dry_run: bool = False,
    headed: bool = False,
    output_dir: Optional[Path] = None,
) -> dict:
    """
    Find and post all unposted videos.

    Returns a summary dict: {total, posted, skipped, failed, results}.
    """
    output_dir = output_dir or OUTPUT_DIR
    videos = _find_unposted_videos(output_dir, brand_filter)

    if not videos:
        logger.info("No unposted videos found.")
        return {"total": 0, "posted": 0, "skipped": 0, "failed": 0, "results": []}

    logger.info(f"Found {len(videos)} unposted video(s) to post:")
    for v in videos:
        logger.info(f"  • {v.name}")

    summary = {"total": len(videos), "posted": 0, "skipped": 0, "failed": 0, "results": []}

    for mp4 in videos:
        brand_key = _extract_brand_from_filename(mp4)
        script_data = _load_script_data(mp4)

        logger.info(f"{'[DRY RUN] ' if dry_run else ''}Posting: {mp4.name} (brand={brand_key})")

        result = post_pin(
            video_path=mp4,
            brand_key=brand_key,
            script_data=script_data,
            headless=not headed,
            dry_run=dry_run,
        )

        result["video_file"] = mp4.name  # keep relative name for readability

        if result["status"] == "posted":
            summary["posted"] += 1
            _write_posted_sentinel(mp4, result)
            logger.info(f"✓ Posted: {mp4.name}")

        elif result["status"] == "dry_run":
            summary["skipped"] += 1
            logger.info(f"→ [DRY RUN] Would post: {mp4.name}")

        elif result["status"] == "auth_required":
            logger.error(
                "Pinterest session expired. Run once with --headed to re-authenticate:\n"
                f"  python -m video_pipeline.post_unposted --headed --brand {brand_key}"
            )
            summary["failed"] += 1
            summary["results"].append(result)
            # No point continuing — all videos will hit the same auth wall
            break

        else:
            summary["failed"] += 1
            logger.error(f"✗ Failed: {mp4.name} — {result.get('error')}")

        summary["results"].append(result)

        # Polite pause between posts
        if not dry_run and mp4 != videos[-1]:
            time.sleep(5)

    return summary


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    load_env()

    parser = argparse.ArgumentParser(
        description="Find and post unposted videos to Pinterest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Scans output/ for .mp4 files without a sibling .posted.json.
Videos older than {STALE_AFTER_HOURS}h are skipped as stale.

Examples:
  python -m video_pipeline.post_unposted
  python -m video_pipeline.post_unposted --brand deals
  python -m video_pipeline.post_unposted --dry-run
  python -m video_pipeline.post_unposted --headed  # first login
""",
    )
    parser.add_argument(
        "--brand",
        choices=list(BRANDS.keys()),
        default=None,
        help="Filter to a specific brand (default: all brands)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Log only, don't post")
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in visible mode (required for first login)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help=f"Override output directory (default: {OUTPUT_DIR})",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    output_dir = Path(args.output_dir) if args.output_dir else None

    summary = run(
        brand_filter=args.brand,
        dry_run=args.dry_run,
        headed=args.headed,
        output_dir=output_dir,
    )

    # Print summary table
    print(f"\n{'=' * 50}")
    print(f"Post-unposted summary")
    print(f"  Total found : {summary['total']}")
    print(f"  Posted      : {summary['posted']}")
    print(f"  Skipped     : {summary['skipped']}")
    print(f"  Failed      : {summary['failed']}")
    if summary["results"]:
        print(f"\nResults:")
        for r in summary["results"]:
            icon = {"posted": "✓", "dry_run": "→", "failed": "✗", "auth_required": "⚠"}.get(
                r.get("status", ""), "?"
            )
            print(f"  {icon} [{r.get('status')}] {r.get('video_file', '')} {r.get('pin_url', '')}")
    print("=" * 50)

    # Exit code: 0 if all succeeded (or dry run), 1 if any failed
    if summary["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
