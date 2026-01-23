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
