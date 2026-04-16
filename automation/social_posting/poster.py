"""Read queued items from disk and post them to the configured platforms.

Usage::

    python -m automation.social_posting.poster                 # dry-run, all platforms
    python -m automation.social_posting.poster --live          # actually post
    python -m automation.social_posting.poster --platform twitter --live
    python -m automation.social_posting.poster --limit 1       # one item only

Safety: posting requires the explicit ``--live`` flag. Without it the poster
runs in dry-run mode (prints what it would post but never hits the network).
"""
from __future__ import annotations

import argparse
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from . import config
from .models import PostResult, QueueItem

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Queue I/O
# ---------------------------------------------------------------------------
def iter_queue_files() -> list[Path]:
    """Return queued JSON files sorted by mtime (oldest first — FIFO)."""
    files: list[Path] = []
    for brand_dir in sorted(config.QUEUE_DIR.iterdir()) if config.QUEUE_DIR.exists() else []:
        if not brand_dir.is_dir():
            continue
        files.extend(sorted(brand_dir.glob("*.json"), key=lambda p: p.stat().st_mtime))
    return files


def load_item(path: Path) -> QueueItem:
    return QueueItem.model_validate_json(path.read_text(encoding="utf-8"))


def archive_item(path: Path, results: list[PostResult]) -> Path:
    """Move ``path`` from queue/ to posted/ with a timestamp + result summary."""
    brand = path.parent.name
    out_dir = config.POSTED_DIR / brand
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    new_path = out_dir / f"{ts}-{path.name}"
    shutil.move(str(path), str(new_path))

    sidecar = new_path.with_suffix(".results.json")
    sidecar.write_text(
        "[" + ",".join(r.model_dump_json() for r in results) + "]",
        encoding="utf-8",
    )
    return new_path


# ---------------------------------------------------------------------------
# Per-platform posting
# ---------------------------------------------------------------------------
def _post_twitter(item: QueueItem, dry_run: bool) -> PostResult:
    if not item.twitter:
        return PostResult(platform="twitter", success=False, error="no twitter payload")
    if dry_run:
        logger.info("[dry-run] twitter hook: %s", item.twitter.hook_tweet.text[:80])
        for i, t in enumerate(item.twitter.thread, start=1):
            logger.info("[dry-run] thread %d/%d: %s", i, len(item.twitter.thread), t.text[:80])
        return PostResult(platform="twitter", success=True, post_id="dry-run")
    if not config.have_twitter():
        return PostResult(platform="twitter", success=False, error="missing TWITTER_* secrets")

    from .twitter_client import TwitterClient

    client = TwitterClient()
    try:
        if item.twitter.thread:
            results = client.post_thread([t.text for t in item.twitter.thread])
            tid, url = results[0]
        else:
            tid, url = client.post_tweet(item.twitter.hook_tweet.text)
        return PostResult(platform="twitter", success=True, post_id=tid, post_url=url)
    except Exception as exc:
        logger.exception("Twitter post failed")
        return PostResult(platform="twitter", success=False, error=str(exc))


def _post_linkedin(item: QueueItem, dry_run: bool) -> PostResult:
    if not item.linkedin:
        return PostResult(platform="linkedin", success=False, error="no linkedin payload")
    if dry_run:
        logger.info("[dry-run] linkedin (%d chars): %s",
                    len(item.linkedin.text), item.linkedin.text[:120])
        return PostResult(platform="linkedin", success=True, post_id="dry-run")
    if not config.have_linkedin():
        return PostResult(platform="linkedin", success=False, error="missing LINKEDIN_* secrets")

    from .linkedin_client import LinkedInClient

    client = LinkedInClient()
    try:
        if item.linkedin.image_path:
            urn, url = client.post_with_image(item.linkedin.text, item.linkedin.image_path)
        else:
            urn, url = client.post(item.linkedin.text)
        return PostResult(platform="linkedin", success=True, post_id=urn, post_url=url)
    except Exception as exc:
        logger.exception("LinkedIn post failed")
        return PostResult(platform="linkedin", success=False, error=str(exc))


def _post_bluesky(item: QueueItem, dry_run: bool) -> PostResult:
    return PostResult(platform="bluesky", success=False, error="bluesky not yet implemented")


def _post_threads(item: QueueItem, dry_run: bool) -> PostResult:
    return PostResult(platform="threads", success=False, error="threads not yet implemented")


PLATFORM_FUNCS = {
    "twitter": _post_twitter,
    "linkedin": _post_linkedin,
    "bluesky": _post_bluesky,
    "threads": _post_threads,
}


# ---------------------------------------------------------------------------
# Supabase logging (best-effort)
# ---------------------------------------------------------------------------
def _log_to_supabase(item: QueueItem, results: list[PostResult]) -> None:
    if not config.have_supabase():
        return
    try:
        from database.supabase_client import SupabaseClient

        sb = SupabaseClient.from_config()
        for r in results:
            sb.client.table("social_posts").insert(
                {
                    "brand": item.brand,
                    "platform": r.platform,
                    "article_slug": item.article_slug,
                    "article_url": item.article_url,
                    "post_id": r.post_id,
                    "post_url": r.post_url,
                    "success": r.success,
                    "error": r.error,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ).execute()
    except Exception as exc:
        # Most likely the table doesn't exist — that's an explicit fallback.
        logger.warning("Supabase logging skipped: %s", exc)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def post_item(
    item: QueueItem,
    platforms: Iterable[str],
    dry_run: bool,
) -> list[PostResult]:
    requested = set(platforms) & set(item.platforms)
    results: list[PostResult] = []
    for plat in item.platforms:
        if plat not in requested:
            continue
        func = PLATFORM_FUNCS.get(plat)
        if func is None:
            results.append(PostResult(platform=plat, success=False, error="unknown platform"))
            continue
        results.append(func(item, dry_run))
    return results


def run(
    platforms: list[str],
    dry_run: bool,
    limit: Optional[int] = None,
) -> int:
    files = iter_queue_files()
    if limit is not None:
        files = files[:limit]
    if not files:
        logger.info("Queue is empty; nothing to post.")
        return 0

    failures = 0
    for path in files:
        try:
            item = load_item(path)
        except Exception as exc:
            logger.error("Skipping malformed queue file %s: %s", path, exc)
            failures += 1
            continue

        logger.info("Posting %s (brand=%s, slug=%s)", path.name, item.brand, item.article_slug)
        results = post_item(item, platforms=platforms, dry_run=dry_run)

        for r in results:
            status = "OK" if r.success else "FAIL"
            logger.info("  -> %s %s id=%s err=%s", r.platform, status, r.post_id, r.error)
            if not r.success and not dry_run:
                failures += 1

        if not dry_run and any(r.success for r in results):
            _log_to_supabase(item, results)
            archive_item(path, results)

    return 1 if failures else 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Post queued items to social platforms.")
    p.add_argument(
        "--platform",
        choices=["twitter", "linkedin", "bluesky", "threads", "all"],
        default="all",
        help="Which platform to post to (default: all).",
    )
    p.add_argument("--live", action="store_true",
                   help="Actually post. Without this flag, runs in dry-run mode.")
    p.add_argument("--limit", type=int, default=None, help="Max items to process.")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = _build_argparser().parse_args(argv)
    platforms = (
        ["twitter", "linkedin", "bluesky", "threads"]
        if args.platform == "all"
        else [args.platform]
    )
    dry_run = not args.live
    if dry_run:
        logger.info("DRY-RUN mode (pass --live to actually post).")
    return run(platforms=platforms, dry_run=dry_run, limit=args.limit)


if __name__ == "__main__":
    raise SystemExit(main())
