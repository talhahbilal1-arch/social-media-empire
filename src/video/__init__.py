"""Video composition module for social media vertical videos.

This module provides:
- VideoCompositor: Main class for compositing videos
- create_text_overlay: Factory for creating text clips
- TextOverlayConfig: Configuration for text styling
- Timing utilities: For audio-text synchronization
"""

from src.video.compositor import VideoCompositor
from src.video.text_overlay import create_text_overlay, TextOverlayConfig
from src.video.timing import (
    WordTiming,
    SentenceTiming,
    extract_word_timings,
    group_words_into_sentences,
)

__all__ = [
    "VideoCompositor",
    "create_text_overlay",
    "TextOverlayConfig",
    "WordTiming",
    "SentenceTiming",
    "extract_word_timings",
    "group_words_into_sentences",
]
