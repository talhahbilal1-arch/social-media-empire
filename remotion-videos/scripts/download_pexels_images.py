#!/usr/bin/env python3
"""
Download stock images from Pexels CDN for each brand's slideshow.
Uses direct CDN URLs (no API key required).
Each brand gets 4 vertical (9:16) images for the slideshow video.
"""

import os
import sys
import requests
from pathlib import Path
import time

# Output directory
IMAGES_DIR = Path(__file__).parent.parent / "public" / "assets" / "images"

# Direct Pexels CDN URLs for vertical/portrait images
# These are pre-selected, high-quality vertical images that work well for Pinterest
BRAND_IMAGES = {
    'daily-deal-darling': {
        'folder': 'daily-deal-darling',
        'images': [
            # Kitchen/home aesthetic images
            'https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop',  # Kitchen gadgets
            'https://images.pexels.com/photos/4259140/pexels-photo-4259140.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop',  # Woman cooking
            'https://images.pexels.com/photos/1643383/pexels-photo-1643383.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop',  # Home decor
            'https://images.pexels.com/photos/5632399/pexels-photo-5632399.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop',  # Shopping/lifestyle
        ],
    },
    'fitnessmadeasy': {
        'folder': 'fitnessmadeasy',
        'images': [
            # Fitness/workout images
            'https://images.pexels.com/photos/4498606/pexels-photo-4498606.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop',  # Woman workout
            'https://images.pexels.com/photos/4498574/pexels-photo-4498574.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop',  # Stretching
            'https://images.pexels.com/photos/4498362/pexels-photo-4498362.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop',  # Fitness equipment
            'https://images.pexels.com/photos/4498155/pexels-photo-4498155.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop',  # Plank exercise
        ],
    },
    'menopause-planner': {
        'folder': 'menopause-planner',
        'images': [
            # Wellness/spa/relaxation images
            'https://images.pexels.com/photos/3757952/pexels-photo-3757952.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop',  # Spa relaxation
            'https://images.pexels.com/photos/1638280/pexels-photo-1638280.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop',  # Herbal tea
            'https://images.pexels.com/photos/3822864/pexels-photo-3822864.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop',  # Meditation
            'https://images.pexels.com/photos/4056535/pexels-photo-4056535.jpeg?auto=compress&cs=tinysrgb&w=1080&h=1920&fit=crop',  # Self-care journal
        ],
    },
}


def download_image(url: str, output_path: Path, timeout: int = 60) -> bool:
    """Download an image from URL."""
    try:
        print(f"    Downloading...")
        response = requests.get(url, stream=True, timeout=timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Verify file size
        size = output_path.stat().st_size
        if size < 10000:  # Less than 10KB is probably an error
            print(f"    Warning: File too small ({size} bytes)")
            output_path.unlink()
            return False

        print(f"    Saved: {output_path.name} ({size / 1024:.1f} KB)")
        return True
    except Exception as e:
        print(f"    Error: {e}")
        if output_path.exists():
            output_path.unlink()
        return False


def download_images_for_brand(brand_key: str) -> bool:
    """
    Download 4 slideshow images for a brand.

    Args:
        brand_key: The brand key from BRAND_IMAGES

    Returns:
        True if all images downloaded successfully
    """
    if brand_key not in BRAND_IMAGES:
        print(f"ERROR: Unknown brand '{brand_key}'")
        return False

    config = BRAND_IMAGES[brand_key]
    output_dir = IMAGES_DIR / config['folder']
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"Downloading images for: {brand_key}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*50}")

    success_count = 0

    for i, image_url in enumerate(config['images'], 1):
        image_path = output_dir / f'slide{i}.jpg'

        # Skip if already exists and has valid size
        if image_path.exists() and image_path.stat().st_size > 10000:
            print(f"\n  [{i}/4] Already exists: {image_path.name}")
            success_count += 1
            continue

        print(f"\n  [{i}/4] {image_url[:60]}...")

        if download_image(image_url, image_path):
            success_count += 1

        # Small delay to be nice
        time.sleep(0.5)

    print(f"\nCompleted: {success_count}/4 images for {brand_key}")
    return success_count >= 4


def main():
    """Main entry point."""
    print("=" * 60)
    print("Pexels CDN Image Downloader for Brand Slideshows")
    print("=" * 60)

    # Parse command line arguments
    if len(sys.argv) > 1:
        target_brand = sys.argv[1]
        # Normalize brand name
        if target_brand == 'daily_deal_darling':
            target_brand = 'daily-deal-darling'
        elif target_brand == 'menopause_planner':
            target_brand = 'menopause-planner'
        brands_to_process = [target_brand]
    else:
        brands_to_process = list(BRAND_IMAGES.keys())

    print(f"\nBrands to process: {', '.join(brands_to_process)}")

    results = {}

    for brand_key in brands_to_process:
        results[brand_key] = download_images_for_brand(brand_key)

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for brand, success in results.items():
        status = "SUCCESS" if success else "INCOMPLETE"
        print(f"  {brand}: {status}")

    success_count = sum(1 for s in results.values() if s)
    print(f"\nOverall: {success_count}/{len(results)} brands completed")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
