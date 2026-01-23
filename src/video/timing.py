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


def extract_word_timings(submaker: edge_tts.SubMaker) -> List[WordTiming]:
    """Extract word-level timing from edge-tts SubMaker.

    Args:
        submaker: SubMaker instance that has been fed WordBoundary events

    Returns:
        List of WordTiming objects with start/end in seconds

    Note:
        SubMaker stores timing in offset (list of (start, end) tuples in milliseconds)
        and text in subs (list of words). We convert to seconds for consistency.
    """
    word_timings = []

    for text, (start_ms, end_ms) in zip(submaker.subs, submaker.offset):
        word_timings.append(WordTiming(
            text=text,
            start=start_ms / 1000.0,  # Convert milliseconds to seconds
            end=end_ms / 1000.0
        ))

    return word_timings
