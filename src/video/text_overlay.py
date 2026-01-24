"""Karaoke-style caption system with word-by-word highlighting.

Creates large, bold captions in the center of the video where each word
changes from yellow to white as it's being spoken.
"""

from typing import List, Optional
from dataclasses import dataclass
from moviepy import TextClip, CompositeVideoClip
from src.models.brand import BrandConfig
from src.video.timing import WordTiming


# Video dimensions (1080x1920 portrait)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920


@dataclass
class KaraokeConfig:
    """Configuration for karaoke-style captions."""
    font_size: int = 80  # Large text
    font: str = "Helvetica"  # System font that works on macOS
    highlight_color: str = "yellow"  # Current word color
    spoken_color: str = "white"  # Already spoken words
    unspoken_color: str = "white"  # Words not yet spoken (dimmer)
    stroke_color: str = "black"  # Outline for readability
    stroke_width: int = 5  # Thick outline for bold look
    words_per_line: int = 4  # Words to show at once
    line_spacing: int = 20  # Space between lines


def create_karaoke_captions(
    word_timings: List[WordTiming],
    brand_config: BrandConfig,
    config: Optional[KaraokeConfig] = None
) -> List[TextClip]:
    """Create karaoke-style captions with word-by-word highlighting.

    Each word appears in yellow when being spoken, then turns white.
    Text is displayed in the center of the video.

    Args:
        word_timings: List of WordTiming with start/end times for each word
        brand_config: Brand configuration (for potential color overrides)
        config: Optional karaoke styling configuration

    Returns:
        List of TextClip objects to be composited onto the video
    """
    config = config or KaraokeConfig()
    clips = []

    if not word_timings:
        return clips

    # Group words into chunks for display
    chunks = []
    for i in range(0, len(word_timings), config.words_per_line):
        chunk = word_timings[i:i + config.words_per_line]
        chunks.append(chunk)

    # For each chunk, create the caption display
    for chunk_idx, chunk in enumerate(chunks):
        if not chunk:
            continue

        # Calculate chunk timing
        chunk_start = chunk[0].start
        chunk_end = chunk[-1].end

        # Get all words in this chunk as text
        chunk_words = [w.text for w in chunk]
        full_text = " ".join(chunk_words)

        # Create base text (all white) that shows for entire chunk duration
        base_clip = TextClip(
            text=full_text,
            font_size=config.font_size,
            font=config.font,
            color=config.spoken_color,
            stroke_color=config.stroke_color,
            stroke_width=config.stroke_width,
            method='caption',
            size=(VIDEO_WIDTH - 160, None),  # Width with margins
            text_align='center'
        )

        # Position in center of screen
        x_pos = (VIDEO_WIDTH - base_clip.w) // 2
        y_pos = (VIDEO_HEIGHT - base_clip.h) // 2

        base_clip = base_clip.with_position((x_pos, y_pos))
        base_clip = base_clip.with_start(chunk_start)
        base_clip = base_clip.with_duration(chunk_end - chunk_start)
        clips.append(base_clip)

        # For each word in the chunk, create a yellow highlight that shows during that word
        for word_idx, word_timing in enumerate(chunk):
            # Build text with only this word highlighted
            # We need to create a clip that shows just this word in yellow
            # positioned exactly where it appears in the full text

            # Create the highlighted word clip
            highlight_clip = TextClip(
                text=word_timing.text,
                font_size=config.font_size,
                font=config.font,
                color=config.highlight_color,
                stroke_color=config.stroke_color,
                stroke_width=config.stroke_width,
                method='label',
                text_align='center'
            )

            # Calculate horizontal position of this word within the chunk
            # Get width of words before this one
            words_before = chunk_words[:word_idx]
            if words_before:
                prefix_text = " ".join(words_before) + " "
                prefix_clip = TextClip(
                    text=prefix_text,
                    font_size=config.font_size,
                    font=config.font,
                    color=config.spoken_color,
                    method='label'
                )
                prefix_width = prefix_clip.w
                prefix_clip.close()
            else:
                prefix_width = 0

            # Position highlight over the word
            # The base_clip is centered, so we need to calculate from its left edge
            word_x = x_pos + prefix_width + (base_clip.w - base_clip.w) // 2

            # For caption method, text starts from left of the clip
            # We need to account for centering
            text_start_x = x_pos
            word_x = text_start_x + prefix_width

            highlight_clip = highlight_clip.with_position((word_x, y_pos))
            highlight_clip = highlight_clip.with_start(word_timing.start)
            highlight_clip = highlight_clip.with_duration(word_timing.end - word_timing.start)
            clips.append(highlight_clip)

    return clips


def create_simple_karaoke(
    word_timings: List[WordTiming],
    brand_config: BrandConfig,
    config: Optional[KaraokeConfig] = None
) -> List[TextClip]:
    """Simplified karaoke - show each word one at a time, yellow while speaking.

    This is a simpler approach that shows words individually as they're spoken.

    Args:
        word_timings: List of WordTiming with start/end times for each word
        brand_config: Brand configuration
        config: Optional styling configuration

    Returns:
        List of TextClip objects
    """
    config = config or KaraokeConfig()
    clips = []

    # Group into phrases of N words
    phrase_size = config.words_per_line

    for i in range(0, len(word_timings), phrase_size):
        phrase_words = word_timings[i:i + phrase_size]
        if not phrase_words:
            continue

        phrase_start = phrase_words[0].start
        phrase_end = phrase_words[-1].end
        phrase_text = " ".join([w.text for w in phrase_words])

        # Create the phrase with ALL words in white (base layer)
        white_clip = TextClip(
            text=phrase_text,
            font_size=config.font_size,
            font=config.font,
            color=config.spoken_color,
            stroke_color=config.stroke_color,
            stroke_width=config.stroke_width,
            method='caption',
            size=(VIDEO_WIDTH - 200, None),
            text_align='center'
        )

        # Center position
        x_pos = (VIDEO_WIDTH - white_clip.w) // 2
        y_pos = (VIDEO_HEIGHT - white_clip.h) // 2

        white_clip = white_clip.with_position((x_pos, y_pos))
        white_clip = white_clip.with_start(phrase_start)
        white_clip = white_clip.with_duration(phrase_end - phrase_start)
        clips.append(white_clip)

        # Now create yellow highlights for each word as it's spoken
        for j, word_timing in enumerate(phrase_words):
            # Build the phrase with current word in yellow, others transparent
            words_before = [w.text for w in phrase_words[:j]]
            words_after = [w.text for w in phrase_words[j+1:]]

            # Create a version with just this word visible (in yellow)
            # Position it precisely over where the word appears

            # Measure prefix width
            if words_before:
                prefix = " ".join(words_before) + " "
                prefix_clip = TextClip(
                    text=prefix,
                    font_size=config.font_size,
                    font=config.font,
                    method='label'
                )
                prefix_w = prefix_clip.w
                prefix_clip.close()
            else:
                prefix_w = 0

            # Create yellow word
            yellow_word = TextClip(
                text=word_timing.text,
                font_size=config.font_size,
                font=config.font,
                color=config.highlight_color,
                stroke_color=config.stroke_color,
                stroke_width=config.stroke_width,
                method='label'
            )

            # Position it over the word location
            word_x = x_pos + prefix_w
            yellow_word = yellow_word.with_position((word_x, y_pos))
            yellow_word = yellow_word.with_start(word_timing.start)
            yellow_word = yellow_word.with_duration(word_timing.end - word_timing.start)
            clips.append(yellow_word)

    return clips


# Keep backward compatibility
def create_text_overlay(*args, **kwargs):
    """Deprecated - use create_karaoke_captions instead."""
    return []


def create_caption(*args, **kwargs):
    """Deprecated - use create_karaoke_captions instead."""
    return []


# Export config class with old name for compatibility
CaptionConfig = KaraokeConfig
