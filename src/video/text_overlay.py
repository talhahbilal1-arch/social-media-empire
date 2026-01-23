"""Text overlay system with safe zone positioning and brand color integration.

This module provides functionality to create text overlays for video content
with brand-specific styling and safe zone positioning to avoid mobile UI elements.
"""

from typing import Literal, Optional
from dataclasses import dataclass
from moviepy import TextClip
from src.models.brand import BrandConfig


# Video dimensions (1080x1920 portrait for TikTok/Instagram/YouTube Shorts)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
SAFE_ZONE_MARGIN = 120  # 120px from edges per roadmap requirements


@dataclass
class TextOverlayConfig:
    """Configuration for text overlay appearance."""
    font_size: int = 64
    stroke_width: int = 3
    margin: tuple[int, int] = (5, 5)  # Prevent stroke cutoff
    text_align: str = 'center'


PositionType = Literal["top", "center", "bottom"]


def create_text_overlay(
    text: str,
    start_time: float,
    duration: float,
    brand_config: BrandConfig,
    position: PositionType = "center",
    config: Optional[TextOverlayConfig] = None
) -> TextClip:
    """Create a text overlay clip with brand colors and safe zone positioning.

    Args:
        text: Text content to display
        start_time: When the text appears (seconds)
        duration: How long the text is visible (seconds)
        brand_config: Brand configuration for colors
        position: Vertical position - "top", "center", or "bottom"
        config: Optional override for text styling

    Returns:
        TextClip positioned within safe zones with brand styling

    Note:
        Uses absolute coordinate positioning (not string positions like "center")
        due to known bugs in MoviePy 2.x with string-based positioning.
    """
    # Use default config if not provided
    config = config or TextOverlayConfig()

    # Extract colors from brand_config. The Color type has .as_hex() method
    text_color = brand_config.colors.secondary.as_hex()
    stroke_color = brand_config.colors.primary.as_hex()

    # Create TextClip with Pillow (default in MoviePy 2.x)
    txt_clip = TextClip(
        text=text,
        font_size=config.font_size,
        color=text_color,
        stroke_color=stroke_color,
        stroke_width=config.stroke_width,
        method='caption',  # Auto-wrap text to fit width
        size=(VIDEO_WIDTH - 2 * SAFE_ZONE_MARGIN, None),  # Width constrained, auto height
        text_align=config.text_align,
        margin=config.margin
    )

    # Calculate absolute Y position based on position parameter
    if position == "top":
        y_pos = SAFE_ZONE_MARGIN
    elif position == "bottom":
        y_pos = VIDEO_HEIGHT - SAFE_ZONE_MARGIN - txt_clip.h
    else:  # center
        y_pos = (VIDEO_HEIGHT - txt_clip.h) / 2

    x_pos = SAFE_ZONE_MARGIN  # Centered horizontally within safe zone

    # Apply position and timing
    txt_clip = txt_clip.with_position((x_pos, y_pos))
    txt_clip = txt_clip.with_start(start_time)
    txt_clip = txt_clip.with_duration(duration)

    return txt_clip
