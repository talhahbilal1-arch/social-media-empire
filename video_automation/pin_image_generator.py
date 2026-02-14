"""Pinterest pin image generator using Pillow.

Generates 1000x1500px (2:3) pin images with text overlays on Pexels backgrounds.
Uses brand styling from video_templates.py for colors and fonts.

Usage:
    # Single pin
    python -m video_automation.pin_image_generator \
        --brand daily_deal_darling \
        --headline "8 Skincare Steps for Glowing Skin" \
        --keyword "woman skincare routine" \
        --style gradient

    # Batch from content JSON
    python -m video_automation.pin_image_generator \
        --brand daily_deal_darling \
        --category beauty \
        --count 5
"""

import argparse
import json
import logging
import os
import sys
import textwrap
from io import BytesIO
from pathlib import Path
from typing import Optional

import requests
from PIL import Image, ImageDraw, ImageFont

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from video_automation.video_templates import BRAND_VIDEO_STYLES
from utils.config import get_config

logger = logging.getLogger(__name__)

# Pin dimensions (Pinterest optimal 2:3 ratio)
PIN_WIDTH = 1000
PIN_HEIGHT = 1500

# Font cache directory
FONTS_DIR = PROJECT_ROOT / "assets" / "fonts"

# Google Fonts download URLs (TTF files)
GOOGLE_FONT_URLS = {
    "Playfair Display": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
    "Lato": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Regular.ttf",
    "Oswald": "https://github.com/google/fonts/raw/main/ofl/oswald/Oswald%5Bwght%5D.ttf",
    "Open Sans": "https://github.com/google/fonts/raw/main/ofl/opensans/OpenSans%5Bwdth%2Cwght%5D.ttf",
    "Merriweather": "https://github.com/google/fonts/raw/main/ofl/merriweather/Merriweather%5Bopsz%2Cwdth%2Cwght%5D.ttf",
    "Source Sans Pro": "https://github.com/google/fonts/raw/main/ofl/sourcesans3/SourceSans3%5Bwght%5D.ttf",
    "Montserrat": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
    "Roboto": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto%5Bwdth%2Cwght%5D.ttf",
    "Nunito": "https://github.com/google/fonts/raw/main/ofl/nunito/Nunito%5Bwght%5D.ttf",
}

# Bold variants for headings
GOOGLE_FONT_BOLD_URLS = {
    "Lato": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Bold.ttf",
    "Merriweather": "https://github.com/google/fonts/raw/main/ofl/merriweather/Merriweather%5Bopsz%2Cwdth%2Cwght%5D.ttf",
}

# Brand key -> content directory name mapping
BRAND_CONTENT_DIRS = {
    "daily_deal_darling": "dailydealdarling",
    "deals": "dailydealdarling",
    "fitnessmadeasy": "fitover35",
    "fitness": "fitover35",
    "menopause_planner": "menopauseplanner",
    "menopause": "menopauseplanner",
}


def _font_filename(name: str, bold: bool = False) -> str:
    """Convert font name to a local filename."""
    safe = name.lower().replace(" ", "_")
    suffix = "_bold" if bold else ""
    return f"{safe}{suffix}.ttf"


def ensure_font(name: str, bold: bool = False) -> Path:
    """Download a Google Font TTF if not already cached. Returns path to TTF file."""
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    local_path = FONTS_DIR / _font_filename(name, bold)

    if local_path.exists():
        return local_path

    # Try bold variant first if requested
    if bold and name in GOOGLE_FONT_BOLD_URLS:
        url = GOOGLE_FONT_BOLD_URLS[name]
    elif name in GOOGLE_FONT_URLS:
        url = GOOGLE_FONT_URLS[name]
    else:
        logger.warning(f"No download URL for font '{name}', falling back to default")
        return None

    logger.info(f"Downloading font: {name} ({'bold' if bold else 'regular'}) ...")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    local_path.write_bytes(resp.content)
    logger.info(f"Saved font to {local_path}")
    return local_path


def load_font(name: str, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a font at the given size, downloading if needed."""
    path = ensure_font(name, bold)
    if path and path.exists():
        return ImageFont.truetype(str(path), size)
    # Fallback to Pillow's default
    return ImageFont.load_default(size)


def fetch_background(keyword: str, api_key: str) -> Image.Image:
    """Fetch a portrait photo from Pexels and return as PIL Image."""
    from utils.api_clients import PexelsClient

    client = PexelsClient(api_key=api_key)
    photos = client.search_photos(keyword, per_page=5, orientation="portrait")

    if not photos:
        logger.warning(f"No Pexels photos for '{keyword}', using solid background")
        return Image.new("RGB", (PIN_WIDTH, PIN_HEIGHT), (40, 40, 40))

    # Pick the first result
    photo_url = client.get_photo_url(photos[0], size="large2x")
    if not photo_url:
        photo_url = client.get_photo_url(photos[0], size="original")

    resp = requests.get(photo_url, timeout=30)
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content)).convert("RGB")
    return img


def resize_and_crop(img: Image.Image, w: int, h: int) -> Image.Image:
    """Resize image to cover target dimensions, then center-crop."""
    src_ratio = img.width / img.height
    dst_ratio = w / h

    if src_ratio > dst_ratio:
        # Source is wider - fit by height, crop width
        new_h = h
        new_w = int(h * src_ratio)
    else:
        # Source is taller - fit by width, crop height
        new_w = w
        new_h = int(w / src_ratio)

    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Center crop
    left = (new_w - w) // 2
    top = (new_h - h) // 2
    return img.crop((left, top, left + w, top + h))


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def apply_gradient_overlay(img: Image.Image, colors: dict) -> Image.Image:
    """Apply a black gradient covering bottom 60% of the image."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    gradient_start = int(PIN_HEIGHT * 0.4)  # Start at 40% from top
    for y in range(gradient_start, PIN_HEIGHT):
        progress = (y - gradient_start) / (PIN_HEIGHT - gradient_start)
        alpha = int(200 * progress)  # Max 200/255 opacity
        draw.line([(0, y), (PIN_WIDTH, y)], fill=(0, 0, 0, alpha))

    img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay).convert("RGB")


def apply_box_light_overlay(img: Image.Image, colors: dict) -> Image.Image:
    """Apply a white semi-transparent box in the center."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    box_margin = 60
    box_top = int(PIN_HEIGHT * 0.3)
    box_bottom = int(PIN_HEIGHT * 0.85)
    draw.rounded_rectangle(
        [(box_margin, box_top), (PIN_WIDTH - box_margin, box_bottom)],
        radius=20,
        fill=(255, 255, 255, 210),
    )

    img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay).convert("RGB")


def apply_box_dark_overlay(img: Image.Image, colors: dict) -> Image.Image:
    """Apply a dark semi-transparent box in the center."""
    bg_rgb = hex_to_rgb(colors.get("background", "#000000"))
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    box_margin = 60
    box_top = int(PIN_HEIGHT * 0.3)
    box_bottom = int(PIN_HEIGHT * 0.85)
    draw.rounded_rectangle(
        [(box_margin, box_top), (PIN_WIDTH - box_margin, box_bottom)],
        radius=20,
        fill=(*bg_rgb, 210),
    )

    img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay).convert("RGB")


OVERLAY_STYLES = {
    "gradient": apply_gradient_overlay,
    "box_light": apply_box_light_overlay,
    "box_dark": apply_box_dark_overlay,
}


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def render_text(
    img: Image.Image,
    headline: str,
    subheadline: Optional[str],
    watermark: str,
    brand_style: dict,
    overlay_style: str,
) -> Image.Image:
    """Render headline, subheadline, and watermark text onto the image."""
    draw = ImageDraw.Draw(img)
    colors = brand_style["colors"]
    fonts = brand_style["fonts"]

    # Determine text color based on overlay style
    if overlay_style == "box_light":
        text_color = hex_to_rgb(colors.get("background", "#1A1A1A"))
        sub_color = text_color
        wm_color = hex_to_rgb(colors.get("primary", "#333333"))
    else:
        text_color = hex_to_rgb(colors["text_primary"])
        sub_color = hex_to_rgb(colors.get("text_secondary", "#CCCCCC"))
        wm_color = hex_to_rgb(colors.get("accent", "#FFFFFF"))

    # Load fonts
    heading_font = load_font(fonts["heading"], 64, bold=True)
    sub_font = load_font(fonts["body"], 36)
    watermark_font = load_font(fonts["body"], 28)

    # Text positioning depends on overlay style
    text_margin = 80
    max_text_width = PIN_WIDTH - (text_margin * 2)

    if overlay_style == "gradient":
        # Text goes in bottom 50%
        text_area_top = int(PIN_HEIGHT * 0.52)
        text_area_bottom = PIN_HEIGHT - 80
    else:
        # Text goes inside the box (30%-85% of height)
        text_area_top = int(PIN_HEIGHT * 0.35)
        text_area_bottom = int(PIN_HEIGHT * 0.82)

    # Wrap and draw headline
    headline_lines = _wrap_text(headline, heading_font, max_text_width)
    y = text_area_top
    line_height = 78

    for line in headline_lines:
        bbox = heading_font.getbbox(line)
        line_w = bbox[2] - bbox[0]
        x = (PIN_WIDTH - line_w) // 2  # Center text
        draw.text((x, y), line, fill=text_color, font=heading_font)
        y += line_height

    # Draw subheadline if provided
    if subheadline:
        y += 20  # Gap
        sub_lines = _wrap_text(subheadline, sub_font, max_text_width)
        sub_line_height = 46
        for line in sub_lines:
            bbox = sub_font.getbbox(line)
            line_w = bbox[2] - bbox[0]
            x = (PIN_WIDTH - line_w) // 2
            draw.text((x, y), line, fill=sub_color, font=sub_font)
            y += sub_line_height

    # Draw accent line
    line_y = y + 25
    accent_color = hex_to_rgb(colors.get("accent", "#FFD700"))
    line_w = 120
    draw.line(
        [(PIN_WIDTH // 2 - line_w // 2, line_y), (PIN_WIDTH // 2 + line_w // 2, line_y)],
        fill=accent_color,
        width=3,
    )

    # Draw watermark at bottom
    wm_y = text_area_bottom - 10
    bbox = watermark_font.getbbox(watermark)
    wm_w = bbox[2] - bbox[0]
    draw.text(
        ((PIN_WIDTH - wm_w) // 2, wm_y),
        watermark,
        fill=wm_color,
        font=watermark_font,
    )

    return img


def generate_pin(
    brand: str,
    headline: str,
    keyword: str,
    style: str = "gradient",
    subheadline: Optional[str] = None,
    output_dir: Optional[Path] = None,
) -> Path:
    """Generate a single Pinterest pin image.

    Args:
        brand: Brand key (e.g. 'daily_deal_darling')
        headline: Main headline text
        keyword: Pexels search keyword for background
        style: Overlay style ('gradient', 'box_light', 'box_dark')
        subheadline: Optional secondary text
        output_dir: Override output directory

    Returns:
        Path to the saved PNG file
    """
    config = get_config()
    brand_style = BRAND_VIDEO_STYLES.get(brand)
    if not brand_style:
        raise ValueError(f"Unknown brand '{brand}'. Available: {list(BRAND_VIDEO_STYLES.keys())}")

    if style not in OVERLAY_STYLES:
        raise ValueError(f"Unknown style '{style}'. Available: {list(OVERLAY_STYLES.keys())}")

    # Fetch background image
    logger.info(f"Fetching background for keyword: {keyword}")
    bg = fetch_background(keyword, config.pexels_api_key)

    # Resize/crop to pin dimensions
    bg = resize_and_crop(bg, PIN_WIDTH, PIN_HEIGHT)

    # Apply overlay
    bg = OVERLAY_STYLES[style](bg, brand_style["colors"])

    # Render text
    watermark = brand_style.get("watermark_text", brand.replace("_", " ").title())
    bg = render_text(bg, headline, subheadline, watermark, brand_style, style)

    # Save
    if output_dir is None:
        output_dir = PROJECT_ROOT / "outputs" / "pins" / brand
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename from headline
    safe_name = headline[:50].lower()
    safe_name = "".join(c if c.isalnum() or c == " " else "" for c in safe_name)
    safe_name = safe_name.strip().replace(" ", "-")
    filename = f"{safe_name}_{style}.png"
    output_path = output_dir / filename

    bg.save(output_path, "PNG", quality=95)
    logger.info(f"Pin saved: {output_path}")
    return output_path


def generate_batch(
    brand: str,
    category: str,
    count: int = 5,
    style: str = "gradient",
) -> list[Path]:
    """Generate multiple pins from a content JSON file.

    Reads from outputs/content/{brand_dir}/{category}_posts.json
    """
    brand_dir = BRAND_CONTENT_DIRS.get(brand, brand.replace("_", ""))
    content_path = PROJECT_ROOT / "outputs" / "content" / brand_dir / f"{category}_posts.json"

    if not content_path.exists():
        raise FileNotFoundError(f"Content file not found: {content_path}")

    with open(content_path, "r") as f:
        posts = json.load(f)

    output_dir = PROJECT_ROOT / "outputs" / "pins" / brand / category
    results = []

    for i, post in enumerate(posts[:count]):
        title = post.get("title", "")
        # Use the first list item's image_keyword, or fall back to title words
        items = post.get("list_items", [])
        keyword = items[0].get("image_keyword", title) if items else title

        logger.info(f"Generating pin {i+1}/{min(count, len(posts))}: {title[:60]}...")

        try:
            path = generate_pin(
                brand=brand,
                headline=title,
                keyword=keyword,
                style=style,
                output_dir=output_dir,
            )
            results.append(path)
        except Exception as e:
            logger.error(f"Failed to generate pin for '{title}': {e}")

    logger.info(f"Batch complete: {len(results)}/{min(count, len(posts))} pins generated")
    return results


def main():
    parser = argparse.ArgumentParser(description="Generate Pinterest pin images")
    parser.add_argument("--brand", required=True, help="Brand key (e.g. daily_deal_darling)")
    parser.add_argument("--headline", help="Pin headline text (single pin mode)")
    parser.add_argument("--keyword", help="Pexels search keyword (single pin mode)")
    parser.add_argument("--subheadline", help="Optional subheadline text")
    parser.add_argument("--style", default="gradient", choices=["gradient", "box_light", "box_dark"])
    parser.add_argument("--category", help="Content category for batch mode (e.g. beauty)")
    parser.add_argument("--count", type=int, default=5, help="Number of pins in batch mode")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.headline:
        # Single pin mode
        keyword = args.keyword or args.headline
        path = generate_pin(
            brand=args.brand,
            headline=args.headline,
            keyword=keyword,
            style=args.style,
            subheadline=args.subheadline,
        )
        print(f"Pin saved: {path}")

    elif args.category:
        # Batch mode
        paths = generate_batch(
            brand=args.brand,
            category=args.category,
            count=args.count,
            style=args.style,
        )
        print(f"Generated {len(paths)} pins:")
        for p in paths:
            print(f"  {p}")

    else:
        parser.error("Provide either --headline (single pin) or --category (batch mode)")


if __name__ == "__main__":
    main()
