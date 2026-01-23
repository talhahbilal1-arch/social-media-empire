"""Audio-text synchronization utilities.

This module provides timing extraction and grouping for text overlays
that sync with TTS voiceover audio.
"""
from dataclasses import dataclass
from typing import List
import edge_tts


@dataclass
class WordTiming:
    """Timing information for a single word from TTS."""
    text: str
    start: float  # seconds
    end: float    # seconds

    @property
    def duration(self) -> float:
        """Duration in seconds."""
        return self.end - self.start


@dataclass
class SentenceTiming:
    """Timing information for a sentence block."""
    text: str
    start: float    # seconds - when sentence starts in audio
    duration: float # seconds - how long to display

    @property
    def end(self) -> float:
        """End time in seconds."""
        return self.start + self.duration
