"""Core video composition engine for aspect ratio conversion and overlay rendering.

This module implements the VideoCompositor class which handles:
- 16:9 to 9:16 aspect ratio conversion via center-cropping
- Clip tracking for memory management
- Brand-specific styling and overlays
"""

import gc
from typing import TYPE_CHECKING

from moviepy import VideoFileClip

from src.models.brand import BrandConfig

if TYPE_CHECKING:
    pass

# Video output dimensions (9:16 vertical format)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Safe zone margin to avoid text cutoff on platforms
SAFE_ZONE_MARGIN = 120

# Target frame rate for consistent playback
TARGET_FPS = 24


class VideoCompositor:
    """Compositor for creating vertical format social media videos.

    Handles aspect ratio conversion, text overlays, audio composition,
    and memory management for MoviePy clips.
    """

    def __init__(self, brand_config: BrandConfig) -> None:
        """Initialize compositor with brand configuration.

        Args:
            brand_config: Brand-specific settings for colors, voice, and CTAs
        """
        self.brand_config = brand_config
        self.clips_to_close: list = []

    def cleanup(self) -> None:
        """Close all tracked clips to prevent memory leaks.

        CRITICAL: Must be called after write_videofile() completes.
        Failure to call this will cause memory to accumulate in batch processing.
        """
        for clip in self.clips_to_close:
            try:
                clip.close()
            except Exception:
                pass  # Ignore close errors - clip may already be closed
        self.clips_to_close.clear()
        gc.collect()
