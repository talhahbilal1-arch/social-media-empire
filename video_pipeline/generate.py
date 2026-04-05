"""
CLI entry point for the video pipeline.

Usage:
    python -m video_pipeline.generate --brand fitover35 --count 1
    python -m video_pipeline.generate --brand daily_deal_darling --count 3 --dry-run
    python -m video_pipeline.generate --brand menopause_planner --platforms pinterest,youtube
    python -m video_pipeline.generate --brand pilottools --skip-post
"""

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from .config import load_env, get_brand, BRANDS
from .script_generator import generate_script
from .voiceover import generate_voiceover
from .video_renderer import create_video, create_video_remotion
from .poster import post_video
from .auto_post_pinterest import auto_post_pinterest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "output"
TEMP_DIR = Path(__file__).parent.parent / "output" / "_temp"


def _make_output_path(brand_key: str, index: int = 0) -> Path:
    """Build output path: output/{brand}_{YYYYMMDD_HHMMSS}_{index}.mp4"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    suffix = f"_{index}" if index > 0 else ""
    return OUTPUT_DIR / f"{brand_key}_{ts}{suffix}.mp4"


def run_pipeline(
    brand_key: str,
    count: int = 1,
    dry_run: bool = False,
    skip_post: bool = False,
    platforms: list[str] = None,
    topic: str = None,
    format: str = "pinterest",
) -> list[dict]:
    """
    Execute the full video pipeline for a brand.

    Args:
        brand_key: Brand identifier (e.g. "fitover35")
        count: Number of videos to generate
        dry_run: Generate script only, skip voiceover/render/post
        skip_post: Render video but don't post to platforms
        platforms: List of platforms to post to (default: ["pinterest"])
        topic: Optional specific topic (picks randomly if None)

    Returns:
        List of result dicts per video
    """
    if platforms is None:
        platforms = ["pinterest"]

    brand = get_brand(brand_key)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    for i in range(count):
        run_label = f"[{brand.name}] Video {i + 1}/{count}"
        logger.info(f"{'=' * 60}")
        logger.info(f"{run_label} — starting pipeline")
        result = {"brand": brand_key, "index": i, "status": "started"}

        try:
            # --- Step 1: Generate script ---
            logger.info(f"{run_label} → Step 1: Generating script (format={format})...")
            script_data = generate_script(brand=brand, topic=topic, format=format)
            result["title"] = script_data["title"]
            result["topic"] = script_data.get("topic")
            logger.info(f"{run_label} → Script: '{script_data['title']}'")

            if dry_run:
                logger.info(f"{run_label} → [DRY RUN] Stopping after script generation")
                _print_script_summary(script_data)
                result["status"] = "dry_run"
                results.append(result)
                continue

            output_path = _make_output_path(brand_key, i)

            # --- Step 2: Generate voiceover ---
            voiceover_path = TEMP_DIR / f"{brand_key}_{i}_voiceover.mp3"
            logger.info(f"{run_label} → Step 2: Generating voiceover...")
            try:
                duration = generate_voiceover(
                    script_text=script_data["full_script"],
                    output_path=voiceover_path,
                    voice_style=brand.voice_style,
                )
                result["voiceover_duration_s"] = duration
                logger.info(f"{run_label} → Voiceover: {duration}s")
            except Exception as e:
                logger.warning(f"{run_label} → Voiceover failed ({e}), continuing without audio")
                voiceover_path = None
                duration = script_data.get("estimated_duration_seconds", 45)

            # Update estimated duration from actual voiceover
            if voiceover_path:
                script_data["estimated_duration_seconds"] = duration

            # --- Step 3: Render video ---
            logger.info(f"{run_label} → Step 3: Rendering video (renderer={format})...")
            if format == "pinterest":
                rendered_path = create_video_remotion(
                    brand=brand,
                    script_data=script_data,
                    voiceover_path=voiceover_path,
                    output_path=output_path,
                )
            else:
                rendered_path = create_video(
                    brand=brand,
                    script_data=script_data,
                    voiceover_path=voiceover_path,
                    output_path=output_path,
                )
            result["video_path"] = str(rendered_path)
            logger.info(f"{run_label} → Video: {rendered_path.name}")

            # --- Step 4: Post to platforms ---
            if skip_post:
                logger.info(f"{run_label} → [SKIP POST] Skipping platform posting")
                result["post_results"] = []
                result["status"] = "rendered"
            elif format == "pinterest":
                # Pinterest format: upload to catbox.moe and write pending JSON
                logger.info(f"{run_label} → Step 4: Queuing for Pinterest (catbox.moe upload)...")
                post_result = auto_post_pinterest(
                    video_path=rendered_path,
                    brand_key=brand_key,
                    script_data=script_data,
                )
                result["post_results"] = [post_result]
                result["status"] = "posted" if post_result.get("status") != "failed" else "failed"
                if post_result.get("status") == "pending":
                    logger.info(
                        f"{run_label} → Pinterest: queued {post_result.get('pending_json_path', '')}"
                    )
                else:
                    logger.warning(f"{run_label} → Pinterest: {post_result.get('status')} — {post_result.get('error', '')}")
            else:
                logger.info(f"{run_label} → Step 4: Posting to {platforms}...")
                post_results = post_video(
                    brand=brand,
                    video_path=rendered_path,
                    script_data=script_data,
                    platforms=platforms,
                    dry_run=dry_run,
                )
                result["post_results"] = post_results
                result["status"] = "posted"
                _log_post_summary(run_label, post_results)

            # Clean up temp voiceover
            if voiceover_path and voiceover_path.exists():
                voiceover_path.unlink()

        except Exception as e:
            logger.error(f"{run_label} → FAILED: {e}", exc_info=True)
            result["status"] = "failed"
            result["error"] = str(e)

        results.append(result)

    return results


def _print_script_summary(script_data: dict) -> None:
    """Print a human-readable script summary to stdout."""
    print("\n" + "=" * 60)
    print(f"TITLE:  {script_data.get('title')}")
    print(f"TOPIC:  {script_data.get('topic')}")
    print(f"HOOK:   {script_data.get('hook')}")
    print("POINTS:")
    for p in script_data.get("body_points", []):
        print(f"  • {p}")
    print(f"CTA:    {script_data.get('cta')}")
    print(f"TAGS:   {' '.join(script_data.get('hashtags', []))}")
    print(f"SCRIPT: {script_data.get('full_script', '')[:200]}...")
    print("=" * 60 + "\n")


def _log_post_summary(label: str, post_results: list[dict]) -> None:
    for r in post_results:
        status = r.get("status", "unknown")
        platform = r.get("platform", "unknown")
        if status == "posted":
            url = r.get("video_url", r.get("response", ""))
            logger.info(f"{label} → {platform}: ✓ posted {url}")
        elif status == "dry_run":
            logger.info(f"{label} → {platform}: [dry run]")
        else:
            logger.warning(f"{label} → {platform}: ✗ {status} — {r.get('error', '')}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate and post vertical video content for lifestyle brands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available brands: {', '.join(BRANDS.keys())}

Examples:
  python -m video_pipeline.generate --brand fitover35
  python -m video_pipeline.generate --brand daily_deal_darling --count 3
  python -m video_pipeline.generate --brand menopause_planner --dry-run
  python -m video_pipeline.generate --brand pilottools --skip-post --count 2
  python -m video_pipeline.generate --brand fitover35 --platforms pinterest,youtube
""",
    )

    parser.add_argument(
        "--brand",
        required=True,
        choices=list(BRANDS.keys()),
        help="Brand to generate content for",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        metavar="N",
        help="Number of videos to generate (default: 1)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate script only, skip voiceover/render/post",
    )
    parser.add_argument(
        "--skip-post",
        action="store_true",
        help="Render video but skip posting to platforms",
    )
    parser.add_argument(
        "--platforms",
        default="pinterest",
        help="Comma-separated list of platforms to post to (default: pinterest)",
    )
    parser.add_argument(
        "--format",
        default="pinterest",
        choices=["pinterest", "standard"],
        help="Video format: 'pinterest' (10-12s Remotion, default) or 'standard' (30-60s FFmpeg)",
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Specific topic override (random from brand topics if not set)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load environment variables
    load_env()

    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]

    logger.info(
        f"Starting video pipeline: brand={args.brand}, count={args.count}, "
        f"platforms={platforms}, dry_run={args.dry_run}"
    )

    results = run_pipeline(
        brand_key=args.brand,
        count=args.count,
        dry_run=args.dry_run,
        skip_post=args.skip_post,
        platforms=platforms,
        topic=args.topic,
        format=args.format,
    )

    # Summary
    total = len(results)
    succeeded = sum(1 for r in results if r.get("status") in ("posted", "rendered", "dry_run"))
    failed = total - succeeded

    print(f"\n{'=' * 60}")
    print(f"Pipeline complete: {succeeded}/{total} succeeded, {failed} failed")
    for r in results:
        status = r.get("status", "unknown")
        title = r.get("title", "untitled")
        icon = "✓" if status in ("posted", "rendered", "dry_run") else "✗"
        print(f"  {icon} [{status}] {title}")
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
