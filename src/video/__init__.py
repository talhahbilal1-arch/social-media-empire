"""Video composition module for social media vertical videos.

This module provides:
- VideoCompositor: Main class for compositing videos
- create_caption: Factory for creating caption clips with backgrounds
- create_text_overlay: Factory for creating text clips
- CaptionConfig: Configuration for caption styling
- Timing utilities: For audio-text synchronization
"""

from src.video.compositor import VideoCompositor
from src.video.text_overlay import create_text_overlay, create_caption, CaptionConfig
from src.video.timing import (
    WordTiming,
    SentenceTiming,
    extract_word_timings,
    group_words_into_sentences,
)

__all__ = [
    "VideoCompositor",
    "create_text_overlay",
    "create_caption",
    "CaptionConfig",
    "WordTiming",
    "SentenceTiming",
    "extract_word_timings",
    "group_words_into_sentences",
]
