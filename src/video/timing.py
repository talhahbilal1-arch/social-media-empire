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


def group_words_into_sentences(
    word_timings: List[WordTiming],
    sentences: List[str]
) -> List[SentenceTiming]:
    """Group word timings into sentence-level timing blocks.

    Args:
        word_timings: List of word timings from extract_word_timings
        sentences: List of sentences (in order they appear in script)

    Returns:
        List of SentenceTiming objects matching the sentence order

    Algorithm:
        For each sentence, count its words and consume that many word timings.
        The sentence's start time is the first word's start.
        The sentence's duration spans from first word start to last word end.

    Note:
        This assumes sentences were split by punctuation and words match
        the TTS output order exactly. Minor word count mismatches are handled
        by using available words.
    """
    sentence_timings = []
    word_index = 0

    for sentence in sentences:
        # Count words in this sentence
        sentence_words = sentence.split()
        num_words = len(sentence_words)

        # Check if we have enough words remaining
        if word_index >= len(word_timings):
            break  # No more timing data available

        # Calculate how many words we can actually use
        available_words = min(num_words, len(word_timings) - word_index)

        if available_words > 0:
            # Get timing boundaries for this sentence
            start_time = word_timings[word_index].start
            end_time = word_timings[word_index + available_words - 1].end
            duration = end_time - start_time

            sentence_timings.append(SentenceTiming(
                text=sentence,
                start=start_time,
                duration=duration
            ))

            word_index += available_words

    return sentence_timings
