#!/usr/bin/env python3
"""
Anti-Gravity: Autonomous Affiliate Marketing Engine.

CLI orchestrator that runs the full pipeline:
  1. Discover high-buyer-intent keywords (Gemini)
  2. Write 1,500+ word SEO articles with Chain-of-Density (Gemini)
  3. Publish to Vercel (static site) or WordPress (REST API)
  4. Verify post is live (HTTP 200)
  5. Create 3 Pinterest pin variations staggered across 48 hours

Usage:
  python -m anti_gravity.main discover --niche "ergonomic office furniture"
  python -m anti_gravity.main write --keyword "best standing desks under 500"
  python -m anti_gravity.main run --niche "home fitness equipment" --count 3
  python -m anti_gravity.main run --niche "AI writing tools" --dry-run
  python -m anti_gravity.main stats
"""

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Ensure anti_gravity package is importable when run as script
sys.path.insert(0, str(Path(__file__).parent.parent))

from anti_gravity.core.config import settings
from anti_gravity.core.database import Database
from anti_gravity.services.writer import Writer
from anti_gravity.services.wordpress import WordPressClient
from anti_gravity.services.pinterest import PinterestClient
from anti_gravity.services.vercel_deploy import VercelDeployer

# ---------------------------------------------------------------------------
# Global logger → logs/automation.log + console
# ---------------------------------------------------------------------------

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(settings.LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("anti_gravity")


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class AntiGravity:
    """Main orchestrator for the affiliate marketing pipeline."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.db = Database()
        self.writer = Writer()

        # Publishing backends — Vercel is primary, WordPress is fallback
        self.vercel = None
        self.wp = None
        self.pinterest = None

        if not dry_run:
            # Try Vercel first (always available if CLI is installed)
            try:
                self.vercel = VercelDeployer()
                logger.info("Vercel deployer initialized")
            except Exception as e:
                logger.warning(f"Vercel disabled: {e}")

            # WordPress as fallback
            try:
                self.wp = WordPressClient()
            except ValueError as e:
                logger.warning(f"WordPress disabled: {e}")

            try:
                self.pinterest = PinterestClient()
            except ValueError as e:
                logger.warning(f"Pinterest disabled: {e}")

    # --- Step 1: Discover keywords ---

    def discover(self, niche: str, count: int = 5) -> list[str]:
        """Brainstorm keywords and save to the database."""
        logger.info(f"Discovering {count} keywords for niche: {niche}")
        raw = self.writer.brainstorm_keywords(niche, count=count)
        keywords = [item["keyword"] for item in raw if "keyword" in item]

        # Filter out already-used keywords
        fresh = [kw for kw in keywords if not self.db.keyword_used(kw)]
        self.db.save_keywords(fresh, niche)

        logger.info(f"Discovered {len(fresh)} fresh keywords (filtered {len(keywords) - len(fresh)} duplicates)")
        for i, kw in enumerate(fresh, 1):
            print(f"  {i}. {kw}")
        return fresh

    # --- Step 2: Write + publish a single article ---

    def process_keyword(self, keyword: str, affiliate_link: str = "[AFFILIATE_LINK]") -> dict:
        """Full pipeline for one keyword: write → publish → verify → pin."""
        logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Processing: {keyword}")

        # Check for duplicate
        if self.db.keyword_used(keyword):
            logger.warning(f"Keyword already used: {keyword}")
            return {"keyword": keyword, "skipped": True, "reason": "duplicate"}

        # Write article
        article = self.writer.write_article(keyword, affiliate_link=affiliate_link)
        logger.info(f"Article written: {article['title']} ({article['word_count']} words)")

        result = {
            "keyword": keyword,
            "title": article["title"],
            "slug": article["slug"],
            "word_count": article["word_count"],
            "image_prompt": article.get("image_prompt", ""),
            "published": False,
            "live": False,
            "pins_created": 0,
        }

        if self.dry_run:
            print(f"\n{'=' * 70}")
            print(f"TITLE: {article['title']}")
            print(f"SLUG:  {article['slug']}")
            print(f"WORDS: {article['word_count']}")
            print(f"META:  {article['meta_description']}")
            print(f"IMAGE: {article['image_prompt']}")
            print(f"{'=' * 70}")
            preview = article["html"][:3000]
            print(preview)
            if len(article["html"]) > 3000:
                print("\n... [truncated] ...")
            print(f"{'=' * 70}\n")

            # Save to DB as draft
            post_id = self.db.save_post(
                slug=article["slug"],
                keyword=keyword,
                title=article["title"],
                word_count=article["word_count"],
                status="dry_run",
            )
            self.db.mark_keyword_used(keyword)
            result["post_id"] = post_id
            return result

        # --- Publish to Vercel (primary) or WordPress (fallback) ---
        post_url = None

        if self.vercel:
            logger.info("Publishing via Vercel...")
            deploy_result = self.vercel.publish_article(
                title=article["title"],
                slug=article["slug"],
                html=article["html"],
                meta_description=article["meta_description"],
                word_count=article["word_count"],
                keyword=keyword,
                image_prompt=article.get("image_prompt", ""),
            )

            if deploy_result.success:
                result["published"] = True
                post_url = deploy_result.post_url
                result["post_url"] = post_url
                result["deploy_url"] = deploy_result.deploy_url

                post_id = self.db.save_post(
                    slug=article["slug"],
                    keyword=keyword,
                    title=article["title"],
                    url=post_url,
                    commission_link=affiliate_link,
                    word_count=article["word_count"],
                    status="publish",
                )
                self.db.mark_keyword_used(keyword)

                # Verify post is live
                if post_url:
                    is_live = self.vercel.verify_article_live(post_url)
                    result["live"] = is_live
                    if is_live:
                        self.db.mark_post_live(post_id, post_url)
                    else:
                        logger.warning("Post not yet live — Pinterest pins deferred")
                        return result
            else:
                logger.error(f"Vercel deploy failed: {deploy_result.error}")
                result["error"] = deploy_result.error

        elif self.wp:
            logger.info("Publishing via WordPress...")
            seo_meta = self.wp.build_seo_meta(
                meta_description=article["meta_description"],
                focus_keyword=keyword,
                og_title=article["title"],
            )

            wp_result = self.wp.create_post(
                title=article["title"],
                content=article["html"],
                slug=article["slug"],
                excerpt=article["meta_description"],
                meta=seo_meta,
            )

            if wp_result.success:
                result["published"] = True
                result["wp_post_id"] = wp_result.post_id
                post_url = wp_result.post_url
                result["post_url"] = post_url

                post_id = self.db.save_post(
                    slug=wp_result.slug or article["slug"],
                    keyword=keyword,
                    title=article["title"],
                    wp_post_id=wp_result.post_id,
                    url=post_url,
                    commission_link=affiliate_link,
                    word_count=article["word_count"],
                    status="publish",
                )
                self.db.mark_keyword_used(keyword)

                if post_url:
                    is_live = self.wp.verify_post_live(post_url)
                    result["live"] = is_live
                    if is_live:
                        self.db.mark_post_live(post_id, post_url)
                    else:
                        logger.warning("Post not yet live — Pinterest pins deferred")
                        return result
            else:
                logger.error(f"WordPress publish failed: {wp_result.error}")
                result["error"] = wp_result.error
        else:
            logger.warning("No publisher available — saving as local draft only")
            post_id = self.db.save_post(
                slug=article["slug"],
                keyword=keyword,
                title=article["title"],
                word_count=article["word_count"],
                status="local_draft",
            )
            self.db.mark_keyword_used(keyword)

        # --- Create Pinterest pins ---
        if self.pinterest and post_url and result.get("live"):
            variations = self.writer.generate_pin_variations(
                title=article["title"],
                keyword=keyword,
                url=post_url,
            )

            for i, v in enumerate(variations, 1):
                self.db.save_pin(
                    post_id=post_id,
                    variation=i,
                    title=v.get("pin_title", ""),
                    description=v.get("pin_description", ""),
                )

            pin_results = self.pinterest.post_variations(variations)
            result["pins_created"] = sum(1 for p in pin_results if p["success"])

            for pr in pin_results:
                if pr["success"] and pr["pin_id"]:
                    self.db.mark_pin_posted(pr["variation"], pr["pin_id"])

            logger.info(f"Created {result['pins_created']}/3 pins")

        return result

    # --- Batch mode ---

    def run(
        self,
        niche: str,
        count: int = 5,
        affiliate_link: str = "[AFFILIATE_LINK]",
        delay_minutes: int = 5,
    ) -> list[dict]:
        """Full pipeline: discover → write → publish → pin for N keywords."""
        logger.info(f"Starting Anti-Gravity run: niche='{niche}', count={count}")

        # Discover fresh keywords
        keywords = self.discover(niche, count=count)

        if not keywords:
            # Fall back to unused keywords in the database
            keywords = self.db.get_unused_keywords(limit=count)
            if keywords:
                logger.info(f"Using {len(keywords)} unused keywords from database")
            else:
                logger.error("No keywords available. Try a different niche.")
                return []

        results = []
        for i, kw in enumerate(keywords[:count]):
            try:
                result = self.process_keyword(kw, affiliate_link=affiliate_link)
                results.append(result)

                # Delay between articles (rate limiting / natural pacing)
                if i < len(keywords) - 1 and not self.dry_run:
                    logger.info(f"Waiting {delay_minutes} minutes before next article...")
                    time.sleep(delay_minutes * 60)

            except Exception as e:
                logger.error(f"Failed to process '{kw}': {e}", exc_info=True)
                results.append({"keyword": kw, "error": str(e)})

        return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anti-gravity",
        description="Anti-Gravity: Autonomous Affiliate Marketing Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover keywords only
  python -m anti_gravity.main discover --niche "home office furniture"

  # Write a single article (dry run)
  python -m anti_gravity.main write --keyword "best standing desks under 500" --dry-run

  # Full pipeline: 3 articles with publishing + Pinterest
  python -m anti_gravity.main run --niche "AI writing tools" --count 3

  # Show database stats
  python -m anti_gravity.main stats
        """,
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # --- discover ---
    p_discover = sub.add_parser("discover", help="Brainstorm keywords for a niche")
    p_discover.add_argument("--niche", required=True, help="Seed niche to research")
    p_discover.add_argument("--count", type=int, default=5, help="Number of keywords (default: 5)")

    # --- write ---
    p_write = sub.add_parser("write", help="Write and publish a single article")
    p_write.add_argument("--keyword", required=True, help="Target keyword")
    p_write.add_argument("--affiliate-link", default="[AFFILIATE_LINK]", help="Affiliate URL")
    p_write.add_argument("--dry-run", action="store_true", help="Generate without publishing")

    # --- run ---
    p_run = sub.add_parser("run", help="Full pipeline: discover → write → publish → pin")
    p_run.add_argument("--niche", required=True, help="Seed niche")
    p_run.add_argument("--count", type=int, default=5, help="Number of articles (default: 5)")
    p_run.add_argument("--affiliate-link", default="[AFFILIATE_LINK]", help="Affiliate URL")
    p_run.add_argument("--delay", type=int, default=5, help="Minutes between articles (default: 5)")
    p_run.add_argument("--dry-run", action="store_true", help="Generate without publishing")

    # --- stats ---
    sub.add_parser("stats", help="Show database statistics")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "stats":
        db = Database()
        stats = db.get_stats()
        print("\nAnti-Gravity Database Stats")
        print("=" * 40)
        for k, v in stats.items():
            print(f"  {k.replace('_', ' ').title()}: {v}")
        print("=" * 40)
        return

    dry_run = getattr(args, "dry_run", False)
    engine = AntiGravity(dry_run=dry_run)

    if args.command == "discover":
        engine.discover(args.niche, count=args.count)

    elif args.command == "write":
        result = engine.process_keyword(args.keyword, affiliate_link=args.affiliate_link)
        _print_result(result)

    elif args.command == "run":
        results = engine.run(
            niche=args.niche,
            count=args.count,
            affiliate_link=args.affiliate_link,
            delay_minutes=args.delay,
        )
        _print_summary(results)


def _print_result(result: dict):
    """Print a single article result."""
    print(f"\n{'=' * 60}")
    if result.get("skipped"):
        print(f"SKIPPED: {result['keyword']} ({result.get('reason', '')})")
    elif result.get("error"):
        print(f"ERROR: {result.get('keyword', '?')} — {result['error']}")
    else:
        status = "LIVE" if result.get("live") else "PUBLISHED" if result.get("published") else "DRAFT"
        print(f"[{status}] {result.get('title', result.get('keyword', '?'))}")
        print(f"  Words: {result.get('word_count', '?')}")
        if result.get("post_url"):
            print(f"  URL:   {result['post_url']}")
        if result.get("pins_created"):
            print(f"  Pins:  {result['pins_created']}/3 created")
    print(f"{'=' * 60}\n")


def _print_summary(results: list[dict]):
    """Print batch run summary."""
    print(f"\n{'=' * 60}")
    print("ANTI-GRAVITY RUN SUMMARY")
    print(f"{'=' * 60}")

    for r in results:
        if r.get("skipped"):
            icon = "SKIP"
        elif r.get("error"):
            icon = "FAIL"
        elif r.get("live"):
            icon = " OK "
        elif r.get("published"):
            icon = "PUBL"
        else:
            icon = "DRFT"

        title = r.get("title", r.get("keyword", "unknown"))[:50]
        pins = r.get("pins_created", 0)
        print(f"  [{icon}] {title} | {r.get('word_count', '?')} words | {pins} pins")

    total = len(results)
    published = sum(1 for r in results if r.get("published"))
    live = sum(1 for r in results if r.get("live"))
    pins = sum(r.get("pins_created", 0) for r in results)

    print(f"\n  Total: {total} | Published: {published} | Live: {live} | Pins: {pins}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
