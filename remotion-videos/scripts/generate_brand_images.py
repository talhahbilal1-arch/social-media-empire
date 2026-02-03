#!/usr/bin/env python3
"""
Generate AI images for each brand using Google Gemini Imagen 3.

Usage:
    python generate_brand_images.py [brand_id]

    If no brand_id is provided, generates images for all brands.

Requirements:
    - GEMINI_API_KEY environment variable set
    - google-generativeai package installed: pip install google-generativeai
"""

import os
import sys
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai package not installed.")
    print("Install with: pip install google-generativeai")
    sys.exit(1)

# Configure Gemini API
API_KEY = os.environ.get('GEMINI_API_KEY')
if not API_KEY:
    print("ERROR: GEMINI_API_KEY environment variable not set.")
    print("Get your API key from: https://aistudio.google.com/app/apikey")
    sys.exit(1)

genai.configure(api_key=API_KEY)

# Output directory for generated images
IMAGES_DIR = Path(__file__).parent.parent / "public" / "assets" / "images"

# Brand-specific image prompts
# Each brand gets 4 images that transition throughout the video
BRAND_IMAGE_PROMPTS = {
    'daily_deal_darling': {
        'folder': 'daily-deal-darling',
        'prompts': [
            "Aesthetic flat lay of kitchen gadgets and home items on marble counter, soft warm lighting, Pinterest style vertical composition, cozy vibes, professional product photography, 9:16 aspect ratio",
            "Happy woman in bright modern kitchen using a gadget while cooking, lifestyle photography, natural lighting, vertical format, warm inviting atmosphere",
            "Close-up of trending home products beautifully arranged, soft bokeh background, product photography style, pastel colors, vertical 9:16 format",
            "Cozy home scene with decorative items candles and plants, lifestyle aesthetic, warm golden tones, Pinterest-worthy composition, vertical format",
        ],
    },
    'fitnessmadeasy': {
        'folder': 'fitnessmadeasy',
        'prompts': [
            "Fit woman over 35 doing ab exercises at home in living room, bright natural lighting, motivational fitness photography, athletic wear, vertical 9:16 format",
            "Athletic mature woman stretching in modern home setting, healthy lifestyle, natural light, empowering pose, vertical format, clean background",
            "Close-up of fitness equipment dumbbells and yoga mat, clean minimalist aesthetic, motivational energy, vertical Pinterest format, bright colors",
            "Woman doing plank exercise in sunny room, strong and confident, age-positive fitness photography, vertical 9:16 composition",
        ],
    },
    'menopause_planner': {
        'folder': 'menopause-planner',
        'prompts': [
            "Serene woman in her 50s practicing self-care, spa-like bathroom setting, calming wellness photography, soft lavender tones, vertical 9:16 format",
            "Beautiful arrangement of natural supplements and herbal tea on soft fabric, feminine aesthetic, wellness vibes, calming colors, vertical format",
            "Mature woman meditating peacefully in nature garden setting, golden hour lighting, mindfulness photography, serene expression, vertical 9:16",
            "Elegant wellness journal with candles and flowers, self-care aesthetic, calming purple and pink tones, soft focus, vertical format",
        ],
    },
}


def generate_images_for_brand(brand_id: str) -> bool:
    """
    Generate 4 AI images for a brand using Gemini Imagen 3.

    Args:
        brand_id: The brand identifier from BRAND_IMAGE_PROMPTS

    Returns:
        True if all images generated successfully, False otherwise
    """
    if brand_id not in BRAND_IMAGE_PROMPTS:
        print(f"ERROR: Unknown brand '{brand_id}'")
        print(f"Available brands: {', '.join(BRAND_IMAGE_PROMPTS.keys())}")
        return False

    config = BRAND_IMAGE_PROMPTS[brand_id]
    output_dir = IMAGES_DIR / config['folder']
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"Generating images for: {brand_id}")
    print(f"Output directory: {output_dir}")
    print(f"{'='*50}")

    # Initialize Imagen model
    try:
        model = genai.ImageGenerationModel("imagen-3.0-generate-001")
    except Exception as e:
        print(f"ERROR: Could not initialize Imagen model: {e}")
        print("Note: Imagen 3 requires access to be enabled for your API key.")
        return False

    success_count = 0

    for i, prompt in enumerate(config['prompts'], 1):
        image_path = output_dir / f'slide{i}.png'

        # Skip if image already exists
        if image_path.exists():
            print(f"\n  [{i}/4] Already exists: {image_path.name}")
            success_count += 1
            continue

        print(f"\n  [{i}/4] Generating...")
        print(f"       Prompt: {prompt[:60]}...")

        try:
            result = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="9:16",  # Vertical for Pinterest/TikTok/Reels
                safety_filter_level="block_only_high",
            )

            # Save the generated image
            if result.images:
                result.images[0].save(str(image_path))
                print(f"       Saved: {image_path.name}")
                success_count += 1
            else:
                print(f"       ERROR: No image generated")

        except Exception as e:
            print(f"       ERROR: {e}")

    print(f"\nCompleted: {success_count}/4 images for {brand_id}")
    return success_count == 4


def main():
    """Main entry point."""
    print("=" * 60)
    print("Google Gemini Imagen 3 - Brand Image Generator")
    print("=" * 60)

    # Parse command line arguments
    if len(sys.argv) > 1:
        brand_id = sys.argv[1]
        brands_to_generate = [brand_id]
    else:
        brands_to_generate = list(BRAND_IMAGE_PROMPTS.keys())

    print(f"\nBrands to process: {', '.join(brands_to_generate)}")
    print(f"Images directory: {IMAGES_DIR}")

    results = {}

    for brand_id in brands_to_generate:
        results[brand_id] = generate_images_for_brand(brand_id)

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for brand_id, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        print(f"  {brand_id}: {status}")

    success_count = sum(1 for s in results.values() if s)
    print(f"\nOverall: {success_count}/{len(results)} brands completed successfully")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
