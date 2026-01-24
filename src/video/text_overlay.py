"""Text overlay system with caption-style subtitles synced to audio.

This module provides functionality to create readable captions/subtitles
positioned at the bottom of vertical videos, synced with TTS audio timing.
"""

from typing import Literal, Optional, List
from dataclasses import dataclass
from moviepy import TextClip, ColorClip, CompositeVideoClip
from src.models.brand import BrandConfig


# Video dimensions (1080x1920 portrait for TikTok/Instagram/YouTube Shorts)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
SAFE_ZONE_MARGIN = 120  # 120px from edges per roadmap requirements

# Caption positioning - bottom area for subtitle-style display
CAPTION_BOTTOM_MARGIN = 200  # Distance from bottom edge
CAPTION_PADDING = 20  # Padding inside background box


@dataclass
class CaptionConfig:
    """Configuration for caption appearance."""
    font_size: int = 56  # Slightly smaller for subtitle readability
    stroke_width: int = 4  # Thicker stroke for contrast
    text_align: str = 'center'
    bg_color: str = 'black'  # Background box color
    bg_opacity: float = 0.7  # Semi-transparent background
    text_color: str = 'white'  # White text for readability
    stroke_color: str = 'black'  # Black stroke for contrast


PositionType = Literal["top", "center", "bottom"]


def create_caption(
    text: str,
    start_time: float,
    duration: float,
    brand_config: BrandConfig,
    config: Optional[CaptionConfig] = None
) -> List:
    """Create a caption with semi-transparent background at the bottom of the screen.

    Args:
        text: Text content to display as caption
        start_time: When the caption appears (seconds)
        duration: How long the caption is visible (seconds)
        brand_config: Brand configuration (used for fallback colors)
        config: Optional override for caption styling

    Returns:
        List of clips [background_clip, text_clip] for compositing
    """
    config = config or CaptionConfig()

    # Create text clip with high contrast colors
    txt_clip = TextClip(
        text=text,
        font_size=config.font_size,
        color=config.text_color,
        stroke_color=config.stroke_color,
        stroke_width=config.stroke_width,
        method='caption',
        size=(VIDEO_WIDTH - 2 * SAFE_ZONE_MARGIN - 2 * CAPTION_PADDING, None),
        text_align=config.text_align,
        margin=(5, 5)
    )

    # Calculate background box dimensions
    bg_width = VIDEO_WIDTH - 2 * SAFE_ZONE_MARGIN + 20
    bg_height = txt_clip.h + 2 * CAPTION_PADDING

    # Calculate Y position (bottom of screen, above safe zone)
    y_pos = VIDEO_HEIGHT - CAPTION_BOTTOM_MARGIN - bg_height
    x_pos = (VIDEO_WIDTH - bg_width) // 2

    # Create semi-transparent background
    bg_clip = ColorClip(
        size=(bg_width, bg_height),
        color=(0, 0, 0)  # Black
    )
    bg_clip = bg_clip.with_opacity(config.bg_opacity)
    bg_clip = bg_clip.with_position((x_pos, y_pos))
    bg_clip = bg_clip.with_start(start_time)
    bg_clip = bg_clip.with_duration(duration)

    # Position text centered within background
    text_x = x_pos + (bg_width - txt_clip.w) // 2
    text_y = y_pos + CAPTION_PADDING
    txt_clip = txt_clip.with_position((text_x, text_y))
    txt_clip = txt_clip.with_start(start_time)
    txt_clip = txt_clip.with_duration(duration)

    return [bg_clip, txt_clip]


def create_text_overlay(
    text: str,
    start_time: float,
    duration: float,
    brand_config: BrandConfig,
    position: PositionType = "bottom",
    config: Optional[CaptionConfig] = None
) -> TextClip:
    """Create a text overlay clip - now defaults to caption style at bottom.

    Args:
        text: Text content to display
        start_time: When the text appears (seconds)
        duration: How long the text is visible (seconds)
        brand_config: Brand configuration for colors
        position: Vertical position - "top", "center", or "bottom" (default: bottom)
        config: Optional override for text styling

    Returns:
        TextClip positioned as readable caption
    """
    config = config or CaptionConfig()

    # Create text with high-contrast subtitle styling
    txt_clip = TextClip(
        text=text,
        font_size=config.font_size,
        color=config.text_color,
        stroke_color=config.stroke_color,
        stroke_width=config.stroke_width,
        method='caption',
        size=(VIDEO_WIDTH - 2 * SAFE_ZONE_MARGIN, None),
        text_align=config.text_align,
        margin=(5, 5)
    )

    # Calculate absolute Y position based on position parameter
    if position == "top":
        y_pos = SAFE_ZONE_MARGIN
    elif position == "bottom":
        # Position at bottom with margin for mobile UI
        y_pos = VIDEO_HEIGHT - CAPTION_BOTTOM_MARGIN - txt_clip.h
    else:  # center
        y_pos = (VIDEO_HEIGHT - txt_clip.h) / 2

    x_pos = SAFE_ZONE_MARGIN

    # Apply position and timing
    txt_clip = txt_clip.with_position((x_pos, y_pos))
    txt_clip = txt_clip.with_start(start_time)
    txt_clip = txt_clip.with_duration(duration)

    return txt_clip
