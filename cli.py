#!/usr/bin/env python3
"""Command-line interface for video generation.

This module provides a CLI for generating videos using the VideoGenerator
pipeline. Supports single brand or all brands with configurable count.

Usage:
    python cli.py --brand menopause-planner --count 1
    python cli.py --brand all --count 2
    python cli.py --brand daily-deal-darling --count 1 --no-upload

Exit codes:
    0: All videos generated successfully
    1: One or more videos failed to generate
"""

import argparse
import sys
import time
from typing import Dict, List

from src.orchestration import VideoGenerator
from src.orchestration.video_generator import BatchResult
from src.utils.brand_loader import BrandLoader, list_brands


def parse_args(args: List[str] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Generate videos for social media brands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --brand menopause-planner --count 1
  python cli.py --brand all --count 2
  python cli.py --brand daily-deal-darling --count 1 --no-upload
        """,
    )

    parser.add_argument(
        "--brand",
        required=True,
        help='Brand slug (e.g., "menopause-planner") or "all" for all brands',
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of videos to generate per brand (default: 1)",
    )

    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip uploading videos to Supabase storage",
    )

    return parser.parse_args(args)


def resolve_brands(brand_arg: str) -> List[str]:
    """Resolve brand argument to list of brand slugs.

    Args:
        brand_arg: Brand slug or "all" for all brands

    Returns:
        List of brand slugs to process

    Raises:
        SystemExit: If brand slug is invalid
    """
    if brand_arg.lower() == "all":
        brands = list_brands()
        if not brands:
            print("Error: No brands found in config/brands/", file=sys.stderr)
            sys.exit(1)
        return brands

    # Validate brand exists by attempting to load it
    loader = BrandLoader()
    try:
        loader.load(brand_arg)
        return [brand_arg]
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def print_progress(brand: str, video_num: int, total: int, success: bool, error: str = None) -> None:
    """Print progress for a single video generation.

    Args:
        brand: Brand slug
        video_num: Current video number (1-indexed)
        total: Total videos for this brand
        success: Whether generation succeeded
        error: Error message if failed
    """
    if success:
        print(f"  Video {video_num}/{total}: SUCCESS")
    else:
        error_msg = error if error else "Unknown error"
        print(f"  Video {video_num}/{total}: FAILED - {error_msg}")


def print_summary(results: Dict[str, BatchResult], total_duration: float) -> None:
    """Print summary table of generation results.

    Args:
        results: Dictionary mapping brand slug to BatchResult
        total_duration: Total elapsed time in seconds
    """
    # Column widths
    brand_width = 24
    success_width = 7
    failed_width = 6
    total_width = 5

    # Calculate totals
    total_success = sum(r.success_count for r in results.values())
    total_failed = sum(r.failure_count for r in results.values())
    total_count = sum(r.total_count for r in results.values())

    # Print header
    print()
    print("=" * 80)
    print("GENERATION SUMMARY")
    print("=" * 80)

    # Print column headers
    header = (
        f"{'Brand':<{brand_width}} | "
        f"{'Success':>{success_width}} | "
        f"{'Failed':>{failed_width}} | "
        f"{'Total':>{total_width}}"
    )
    print(header)

    # Print separator
    separator = (
        f"{'-' * brand_width}-+-"
        f"{'-' * success_width}-+-"
        f"{'-' * failed_width}-+-"
        f"{'-' * total_width}"
    )
    print(separator)

    # Print each brand row
    for brand_slug, batch_result in results.items():
        row = (
            f"{brand_slug:<{brand_width}} | "
            f"{batch_result.success_count:>{success_width}} | "
            f"{batch_result.failure_count:>{failed_width}} | "
            f"{batch_result.total_count:>{total_width}}"
        )
        print(row)

    # Print separator
    print(separator)

    # Print totals row
    totals_row = (
        f"{'TOTAL':<{brand_width}} | "
        f"{total_success:>{success_width}} | "
        f"{total_failed:>{failed_width}} | "
        f"{total_count:>{total_width}}"
    )
    print(totals_row)

    # Print footer
    print("=" * 80)
    print(f"Total time: {total_duration:.1f}s")


def main(args: List[str] = None) -> int:
    """Main entry point for CLI.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for any failures)
    """
    parsed_args = parse_args(args)

    # Resolve brand(s)
    brand_slugs = resolve_brands(parsed_args.brand)

    # Determine upload setting
    upload = not parsed_args.no_upload

    # Track start time
    start_time = time.time()

    # Create generator
    generator = VideoGenerator()

    # Generate videos and collect results
    results: Dict[str, BatchResult] = {}

    for brand_slug in brand_slugs:
        print(f"[Brand: {brand_slug}] Generating {parsed_args.count} video(s)...")

        # Load brand config
        loader = BrandLoader()
        brand_config = loader.load(brand_slug)

        # Generate batch for this brand
        batch_result = generator.generate_batch(
            brand_config,
            count=parsed_args.count,
            upload=upload,
        )

        # Print progress for each video
        for i, result in enumerate(batch_result.results, start=1):
            print_progress(
                brand_slug,
                i,
                parsed_args.count,
                result.success,
                result.error,
            )

        results[brand_slug] = batch_result

    # Calculate total duration
    total_duration = time.time() - start_time

    # Print summary
    print_summary(results, total_duration)

    # Determine exit code
    total_failures = sum(r.failure_count for r in results.values())
    return 1 if total_failures > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
