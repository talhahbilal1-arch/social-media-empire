"""Pinterest pin image generator using Pillow.

Generates 1000x1500px (2:3) pin images with text overlays on Pexels backgrounds.
Uses brand styling from video_templates.py for colors and fonts.

5 overlay styles:
  - gradient: Black gradient bottom 60%, white bold text
  - box_dark: Dark semi-transparent box, centered text
  - numbered_list: Shows numbered items with a teaser
  - big_stat: Large number/percentage + short text
  - split_layout: Top 60% image, bottom 40% brand-color block

Usage:
    # Single pin
    python -m video_automation.pin_image_generator \
        --brand fitness \
        --headline "8 Exercises for Men Over 35" \
        --keyword "man gym workout" \
        --style gradient

    # Render to bytes (for pipeline use)
    from video_automation.pin_image_generator import render_pin_to_bytes
    jpeg_bytes = render_pin_to_bytes(brand, headline, subheadline, image_url, style)
"""

import argparse
import json
import logging
import os
import sys
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

# Map content_brain visual style names to PIL overlay styles
VISUAL_STYLE_MAP = {
    "bold_text_overlay": "gradient",
    "numbered_list_teaser": "numbered_list",
    "before_after_split": "split_layout",
    "infographic_stat": "big_stat",
    "editorial_magazine": "box_dark",
    "split_color_block": "split_layout",
    "step_by_step": "numbered_list",
}


def map_visual_style(content_brain_style):
    """Map a content_brain visual style name to a PIL overlay style."""
    return VISUAL_STYLE_MAP.get(content_brain_style, "gradient")


def _font_filename(name, bold=False):
    """Convert font name to a local filename."""
    safe = name.lower().replace(" ", "_")
    suffix = "_bold" if bold else ""
    return f"{safe}{suffix}.ttf"


def ensure_font(name, bold=False):
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


def load_font(name, size, bold=False):
    """Load a font at the given size, downloading if needed."""
    path = ensure_font(name, bold)
    if path and path.exists():
        return ImageFont.truetype(str(path), size)
    # Fallback to Pillow's default
    return ImageFont.load_default(size)


def fetch_background_from_url(image_url):
    """Download an image from a URL and return as PIL Image."""
    resp = requests.get(image_url, timeout=30)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert("RGB")


def fetch_background(keyword, api_key):
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


def resize_and_crop(img, w, h):
    """Resize image to cover target dimensions, then center-crop."""
    src_ratio = img.width / img.height
    dst_ratio = w / h

    if src_ratio > dst_ratio:
        new_h = h
        new_w = int(h * src_ratio)
    else:
        new_w = w
        new_h = int(w / src_ratio)

    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - w) // 2
    top = (new_h - h) // 2
    return img.crop((left, top, left + w, top + h))


def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# ═══════════════════════════════════════════════════════════════
# TEXT DRAWING HELPERS
# ═══════════════════════════════════════════════════════════════

def _wrap_text(text, font, max_width):
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


def _draw_text_with_shadow(draw, xy, text, font, fill, shadow_color=(0, 0, 0), shadow_offset=2):
    """Draw text with a dark shadow/outline for readability at thumbnail size."""
    x, y = xy
    # Draw shadow in 4 directions for outline effect
    for dx in (-shadow_offset, 0, shadow_offset):
        for dy in (-shadow_offset, 0, shadow_offset):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, fill=shadow_color, font=font)
    # Draw main text
    draw.text(xy, text, fill=fill, font=font)


def _draw_brand_accent_bar(draw, colors):
    """Draw a subtle brand color accent bar at the top of the pin."""
    accent_color = hex_to_rgb(colors.get("accent", "#FFD700"))
    draw.rectangle([(0, 0), (PIN_WIDTH, 8)], fill=accent_color)


def _draw_cta(draw, font, colors, y_position):
    """Draw a 'Tap to Learn More' CTA near the bottom."""
    cta_text = "Tap to Learn More \u2192"
    accent = hex_to_rgb(colors.get("accent", "#FFD700"))
    bbox = font.getbbox(cta_text)
    cta_w = bbox[2] - bbox[0]
    cta_h = bbox[3] - bbox[1]
    x = (PIN_WIDTH - cta_w) // 2

    # Draw CTA pill background
    pill_pad_x = 24
    pill_pad_y = 10
    draw.rounded_rectangle(
        [(x - pill_pad_x, y_position - pill_pad_y),
         (x + cta_w + pill_pad_x, y_position + cta_h + pill_pad_y)],
        radius=20,
        fill=(*accent, 220) if len(accent) == 3 else accent,
    )
    # CTA text in dark color for contrast
    draw.text((x, y_position), cta_text, fill=(0, 0, 0), font=font)


# ═══════════════════════════════════════════════════════════════
# OVERLAY STYLES (5 total)
# ═══════════════════════════════════════════════════════════════

def apply_gradient_overlay(img, colors):
    """Apply a black gradient covering bottom 60% of the image."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    gradient_start = int(PIN_HEIGHT * 0.4)
    for y in range(gradient_start, PIN_HEIGHT):
        progress = (y - gradient_start) / (PIN_HEIGHT - gradient_start)
        alpha = int(210 * progress)
        draw.line([(0, y), (PIN_WIDTH, y)], fill=(0, 0, 0, alpha))

    img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay).convert("RGB")


def apply_box_dark_overlay(img, colors):
    """Apply a dark semi-transparent box in the center."""
    bg_rgb = hex_to_rgb(colors.get("background", "#000000"))
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    box_margin = 60
    box_top = int(PIN_HEIGHT * 0.28)
    box_bottom = int(PIN_HEIGHT * 0.85)
    draw.rounded_rectangle(
        [(box_margin, box_top), (PIN_WIDTH - box_margin, box_bottom)],
        radius=20,
        fill=(*bg_rgb, 210),
    )

    img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay).convert("RGB")


def apply_numbered_list_overlay(img, colors):
    """Apply a dark gradient from top 30% to bottom for numbered list content."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Full-height gradient, lighter at top, darker at bottom
    for y in range(PIN_HEIGHT):
        progress = y / PIN_HEIGHT
        alpha = int(60 + 160 * progress)
        draw.line([(0, y), (PIN_WIDTH, y)], fill=(0, 0, 0, alpha))

    img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay).convert("RGB")


def apply_big_stat_overlay(img, colors):
    """Apply a strong dark overlay for big stat readability."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Heavy dark overlay so the big number stands out
    draw.rectangle([(0, 0), (PIN_WIDTH, PIN_HEIGHT)], fill=(0, 0, 0, 170))

    img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay).convert("RGB")


def apply_split_layout_overlay(img, colors):
    """Top 60% keeps image (slight darken), bottom 40% is solid brand color block."""
    primary_rgb = hex_to_rgb(colors.get("primary", "#1B5E20"))
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    split_y = int(PIN_HEIGHT * 0.6)

    # Slight darken on top image portion
    for y in range(split_y):
        draw.line([(0, y), (PIN_WIDTH, y)], fill=(0, 0, 0, 40))

    # Solid brand color block on bottom 40%
    draw.rectangle([(0, split_y), (PIN_WIDTH, PIN_HEIGHT)], fill=(*primary_rgb, 245))

    img = img.convert("RGBA")
    return Image.alpha_composite(img, overlay).convert("RGB")


OVERLAY_STYLES = {
    "gradient": apply_gradient_overlay,
    "box_dark": apply_box_dark_overlay,
    "numbered_list": apply_numbered_list_overlay,
    "big_stat": apply_big_stat_overlay,
    "split_layout": apply_split_layout_overlay,
}


# ═══════════════════════════════════════════════════════════════
# TEXT RENDERING (per-style)
# ═══════════════════════════════════════════════════════════════

def render_text(img, headline, subheadline, watermark, brand_style, overlay_style):
    """Render headline, subheadline, CTA, and watermark onto the image."""
    draw = ImageDraw.Draw(img)
    colors = brand_style["colors"]
    fonts = brand_style["fonts"]

    # Brand accent bar at top
    _draw_brand_accent_bar(draw, colors)

    # Determine text colors
    text_color = hex_to_rgb(colors["text_primary"])
    sub_color = hex_to_rgb(colors.get("text_secondary", "#CCCCCC"))
    wm_color = hex_to_rgb(colors.get("accent", "#FFFFFF"))

    # Load fonts — larger sizes for thumbnail readability
    heading_font = load_font(fonts["heading"], 76, bold=True)
    sub_font = load_font(fonts["body"], 38)
    cta_font = load_font(fonts.get("cta", fonts["body"]), 32)
    watermark_font = load_font(fonts["body"], 26)

    text_margin = 80
    max_text_width = PIN_WIDTH - (text_margin * 2)

    # Style-specific text positioning
    if overlay_style == "gradient":
        text_area_top = int(PIN_HEIGHT * 0.48)
        text_area_bottom = PIN_HEIGHT - 60
    elif overlay_style == "split_layout":
        text_area_top = int(PIN_HEIGHT * 0.63)
        text_area_bottom = PIN_HEIGHT - 40
    elif overlay_style == "big_stat":
        text_area_top = int(PIN_HEIGHT * 0.20)
        text_area_bottom = PIN_HEIGHT - 60
    elif overlay_style == "numbered_list":
        text_area_top = int(PIN_HEIGHT * 0.08)
        text_area_bottom = PIN_HEIGHT - 60
    else:  # box_dark
        text_area_top = int(PIN_HEIGHT * 0.33)
        text_area_bottom = int(PIN_HEIGHT * 0.82)

    # ── Big Stat special layout ──
    if overlay_style == "big_stat":
        _render_big_stat(draw, headline, subheadline, heading_font, sub_font,
                         text_color, sub_color, colors, max_text_width, text_margin)
        # CTA
        _draw_cta(draw, cta_font, colors, PIN_HEIGHT - 130)
        # Watermark
        bbox = watermark_font.getbbox(watermark)
        wm_w = bbox[2] - bbox[0]
        draw.text(((PIN_WIDTH - wm_w) // 2, PIN_HEIGHT - 50), watermark, fill=wm_color, font=watermark_font)
        return img

    # ── Numbered List special layout ──
    if overlay_style == "numbered_list":
        _render_numbered_list(draw, headline, subheadline, heading_font, sub_font,
                              text_color, sub_color, colors, max_text_width, text_margin)
        _draw_cta(draw, cta_font, colors, PIN_HEIGHT - 130)
        bbox = watermark_font.getbbox(watermark)
        wm_w = bbox[2] - bbox[0]
        draw.text(((PIN_WIDTH - wm_w) // 2, PIN_HEIGHT - 50), watermark, fill=wm_color, font=watermark_font)
        return img

    # ── Standard layout (gradient, box_dark, split_layout) ──
    headline_lines = _wrap_text(headline, heading_font, max_text_width)
    y = text_area_top
    line_height = 90

    for line in headline_lines:
        bbox = heading_font.getbbox(line)
        line_w = bbox[2] - bbox[0]
        x = (PIN_WIDTH - line_w) // 2
        _draw_text_with_shadow(draw, (x, y), line, heading_font, text_color)
        y += line_height

    # Subheadline
    if subheadline:
        y += 16
        sub_lines = _wrap_text(subheadline, sub_font, max_text_width)
        sub_line_height = 48
        for line in sub_lines:
            bbox = sub_font.getbbox(line)
            line_w = bbox[2] - bbox[0]
            x = (PIN_WIDTH - line_w) // 2
            _draw_text_with_shadow(draw, (x, y), line, sub_font, sub_color, shadow_offset=1)
            y += sub_line_height

    # Accent line
    line_y = y + 20
    accent_color = hex_to_rgb(colors.get("accent", "#FFD700"))
    draw.line(
        [(PIN_WIDTH // 2 - 60, line_y), (PIN_WIDTH // 2 + 60, line_y)],
        fill=accent_color,
        width=4,
    )

    # CTA
    cta_y = min(line_y + 40, text_area_bottom - 80)
    _draw_cta(draw, cta_font, colors, cta_y)

    # Watermark
    wm_y = text_area_bottom - 10
    bbox = watermark_font.getbbox(watermark)
    wm_w = bbox[2] - bbox[0]
    draw.text(((PIN_WIDTH - wm_w) // 2, wm_y), watermark, fill=wm_color, font=watermark_font)

    return img


def _render_big_stat(draw, headline, subheadline, heading_font, sub_font,
                     text_color, sub_color, colors, max_text_width, text_margin):
    """Render a large stat number (40% of frame) with supporting text."""
    accent = hex_to_rgb(colors.get("accent", "#FFD700"))

    # The headline IS the big stat (e.g., "87%", "3x", "14 Days")
    # Render it huge and centered
    stat_font = load_font(heading_font.path.split("/")[-1].replace(".ttf", "").replace("_bold", ""),
                          180, bold=True) if hasattr(heading_font, 'path') else heading_font

    # Try to use the same font family at 180pt
    font_name = None
    for name in GOOGLE_FONT_URLS:
        if name.lower().replace(" ", "_") in str(getattr(heading_font, 'path', '')).lower():
            font_name = name
            break
    if font_name:
        stat_font = load_font(font_name, 180, bold=True)
    else:
        stat_font = load_font("Oswald", 180, bold=True)

    # Draw big stat centered at ~35% from top
    stat_y = int(PIN_HEIGHT * 0.25)
    bbox = stat_font.getbbox(headline)
    stat_w = bbox[2] - bbox[0]
    stat_x = (PIN_WIDTH - stat_w) // 2
    _draw_text_with_shadow(draw, (stat_x, stat_y), headline, stat_font, accent, shadow_offset=3)

    # Draw subheadline below the stat
    if subheadline:
        sub_y = stat_y + 210
        sub_lines = _wrap_text(subheadline, sub_font, max_text_width)
        for line in sub_lines:
            bbox = sub_font.getbbox(line)
            line_w = bbox[2] - bbox[0]
            x = (PIN_WIDTH - line_w) // 2
            _draw_text_with_shadow(draw, (x, sub_y), line, sub_font, text_color, shadow_offset=1)
            sub_y += 50


def _render_numbered_list(draw, headline, subheadline, heading_font, sub_font,
                          text_color, sub_color, colors, max_text_width, text_margin):
    """Render a numbered list with headline at top and items below."""
    accent = hex_to_rgb(colors.get("accent", "#FFD700"))

    # Headline at top
    title_font = load_font(
        next((n for n in GOOGLE_FONT_URLS if n.lower().replace(" ", "_") in
              str(getattr(heading_font, 'path', '')).lower()), "Oswald"),
        64, bold=True
    )
    title_lines = _wrap_text(headline, title_font, max_text_width)
    y = int(PIN_HEIGHT * 0.10)
    for line in title_lines:
        bbox = title_font.getbbox(line)
        line_w = bbox[2] - bbox[0]
        x = (PIN_WIDTH - line_w) // 2
        _draw_text_with_shadow(draw, (x, y), line, title_font, text_color)
        y += 78

    # Accent divider
    y += 15
    draw.line([(text_margin, y), (PIN_WIDTH - text_margin, y)], fill=accent, width=3)
    y += 30

    # Parse numbered items from subheadline or generate placeholders
    items = []
    if subheadline:
        # Try to split on numbered patterns like "1. Item 2. Item" or newlines
        import re
        parts = re.split(r'\d+[\.\)]\s*', subheadline)
        items = [p.strip() for p in parts if p.strip()]

    if not items:
        # Use headline words as a single-item list
        items = [subheadline or headline]

    # Render up to 4 items
    item_font = load_font(
        next((n for n in GOOGLE_FONT_URLS if n.lower().replace(" ", "_") in
              str(getattr(sub_font, 'path', '')).lower()), "Open Sans"),
        40, bold=False
    )
    num_font = load_font("Oswald", 56, bold=True)

    for i, item in enumerate(items[:4]):
        num_str = str(i + 1)
        # Draw number circle
        circle_x = text_margin + 10
        circle_r = 30
        draw.ellipse(
            [(circle_x, y), (circle_x + circle_r * 2, y + circle_r * 2)],
            fill=accent,
        )
        # Number inside circle
        num_bbox = num_font.getbbox(num_str)
        num_w = num_bbox[2] - num_bbox[0]
        num_h = num_bbox[3] - num_bbox[1]
        draw.text(
            (circle_x + circle_r - num_w // 2, y + circle_r - num_h // 2 - 4),
            num_str, fill=(0, 0, 0), font=num_font
        )

        # Item text
        item_x = circle_x + circle_r * 2 + 20
        item_max_w = PIN_WIDTH - item_x - text_margin
        item_lines = _wrap_text(item, item_font, item_max_w)
        item_y = y + 8
        for line in item_lines:
            _draw_text_with_shadow(draw, (item_x, item_y), line, item_font, text_color, shadow_offset=1)
            item_y += 50
        y = max(item_y, y + circle_r * 2) + 25

    # "See all at link..." teaser
    if len(items) > 4 or True:  # Always show teaser
        teaser_font = load_font("Open Sans", 34, bold=False)
        teaser_text = "See the full list at the link..."
        bbox = teaser_font.getbbox(teaser_text)
        tw = bbox[2] - bbox[0]
        _draw_text_with_shadow(
            draw, ((PIN_WIDTH - tw) // 2, y + 10),
            teaser_text, teaser_font, accent, shadow_offset=1
        )


# ═══════════════════════════════════════════════════════════════
# MAIN RENDER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def render_pin_to_bytes(brand, headline, subheadline, keyword_or_url, style="gradient"):
    """Render a pin image and return JPEG bytes (for pipeline use).

    Args:
        brand: Brand key (e.g. 'fitness', 'deals', 'menopause')
        headline: Main text overlay (3-8 word hook)
        subheadline: Secondary text (full title or list items)
        keyword_or_url: Either a Pexels image URL or search keyword
        style: One of 'gradient', 'box_dark', 'numbered_list', 'big_stat', 'split_layout'

    Returns:
        bytes: JPEG image data
    """
    brand_style = BRAND_VIDEO_STYLES.get(brand)
    if not brand_style:
        raise ValueError(f"Unknown brand '{brand}'. Available: {list(BRAND_VIDEO_STYLES.keys())}")

    if style not in OVERLAY_STYLES:
        logger.warning(f"Unknown style '{style}', falling back to gradient")
        style = "gradient"

    # Get background image
    if keyword_or_url and (keyword_or_url.startswith("http://") or keyword_or_url.startswith("https://")):
        bg = fetch_background_from_url(keyword_or_url)
    else:
        config = get_config()
        bg = fetch_background(keyword_or_url or "abstract background", config.pexels_api_key)

    # Resize/crop to pin dimensions
    bg = resize_and_crop(bg, PIN_WIDTH, PIN_HEIGHT)

    # Apply overlay
    bg = OVERLAY_STYLES[style](bg, brand_style["colors"])

    # Render text
    watermark = brand_style.get("watermark_text", brand.replace("_", " ").title())
    bg = render_text(bg, headline, subheadline, watermark, brand_style, style)

    # Convert to JPEG bytes
    buffer = BytesIO()
    bg.save(buffer, "JPEG", quality=85, optimize=True)
    return buffer.getvalue()


def generate_pin(brand, headline, keyword, style="gradient",
                 subheadline=None, output_dir=None):
    """Generate a single Pinterest pin image and save to disk.

    Returns:
        Path to the saved JPEG file.
    """
    config = get_config()
    brand_style = BRAND_VIDEO_STYLES.get(brand)
    if not brand_style:
        raise ValueError(f"Unknown brand '{brand}'. Available: {list(BRAND_VIDEO_STYLES.keys())}")

    if style not in OVERLAY_STYLES:
        logger.warning(f"Unknown style '{style}', falling back to gradient")
        style = "gradient"

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

    # Save as JPEG
    if output_dir is None:
        output_dir = PROJECT_ROOT / "outputs" / "pins" / brand
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = headline[:50].lower()
    safe_name = "".join(c if c.isalnum() or c == " " else "" for c in safe_name)
    safe_name = safe_name.strip().replace(" ", "-")
    filename = f"{safe_name}_{style}.jpg"
    output_path = output_dir / filename

    bg.save(output_path, "JPEG", quality=85, optimize=True)
    logger.info(f"Pin saved: {output_path}")
    return output_path


def generate_batch(brand, category, count=5, style="gradient"):
    """Generate multiple pins from a content JSON file."""
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
    parser.add_argument("--brand", required=True, help="Brand key (e.g. fitness)")
    parser.add_argument("--headline", help="Pin headline text (single pin mode)")
    parser.add_argument("--keyword", help="Pexels search keyword (single pin mode)")
    parser.add_argument("--subheadline", help="Optional subheadline text")
    parser.add_argument("--style", default="gradient",
                        choices=list(OVERLAY_STYLES.keys()))
    parser.add_argument("--category", help="Content category for batch mode")
    parser.add_argument("--count", type=int, default=5, help="Number of pins in batch mode")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.headline:
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
