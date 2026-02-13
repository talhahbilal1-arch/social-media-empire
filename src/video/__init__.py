"""Video composition module for social media vertical videos.

This module provides:
- VideoCompositor: Main class for compositing videos
- create_karaoke_captions: Karaoke-style word-by-word captions
- KaraokeConfig: Configuration for karaoke styling
- Timing utilities: For audio-text synchronization
"""

from src.video.compositor import VideoCompositor
from src.video.text_overlay import create_karaoke_captions, KaraokeConfig, CaptionConfig
from src.video.timing import (
    WordTiming,
    SentenceTiming,
    extract_word_timings,
    group_words_into_sentences,
)

__all__ = [
    "VideoCompositor",
    "create_karaoke_captions",
    "KaraokeConfig",
    "CaptionConfig",
    "WordTiming",
    "SentenceTiming",
    "extract_word_timings",
    "group_words_into_sentences",
]
