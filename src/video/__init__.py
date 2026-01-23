"""Video composition module for creating vertical format social media videos.

This module provides the VideoCompositor class for transforming landscape stock
footage into vertical format (9:16) with text overlays, audio, and brand styling.
"""

from src.video.compositor import VideoCompositor
from src.video.text_overlay import create_text_overlay, TextOverlayConfig

__all__ = [
    "VideoCompositor",
    "create_text_overlay",
    "TextOverlayConfig",
]
