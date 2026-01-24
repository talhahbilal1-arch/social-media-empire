"""Dynamic pop-in caption system with keyword highlighting and emojis.

Creates high-engagement captions that pop in word-by-word or in short phrases,
with keyword highlighting and occasional emojis.
"""

from typing import List, Optional, Callable, Tuple
from dataclasses import dataclass
from moviepy import TextClip, CompositeVideoClip
from src.models.brand import BrandConfig
from src.video.timing import WordTiming
import re


# Video dimensions (1080x1920 portrait)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Keywords to highlight in neon color
HIGHLIGHT_KEYWORDS = {
    'amazing', 'incredible', 'love', 'best', 'perfect', 'great', 'awesome',
    'wow', 'yes', 'free', 'save', 'deal', 'sale', 'new', 'hot', 'must',
    'easy', 'quick', 'simple', 'healthy', 'natural', 'powerful', 'secret',
    'tip', 'hack', 'trick', 'bonus', 'special', 'exclusive', 'limited',
    'never', 'always', 'stop', 'start', 'now', 'today', 'finally',
}

# Emotional words that get emojis
EMOJI_MAP = {
    'love': '❤️', 'heart': '❤️', 'happy': '😊', 'sad': '😢', 'cry': '😢',
    'wow': '😮', 'amazing': '🔥', 'hot': '🔥', 'fire': '🔥', 'cool': '😎',
    'money': '💰', 'save': '💰', 'deal': '💵', 'free': '🎁', 'gift': '🎁',
    'food': '🍽️', 'eat': '🍽️', 'healthy': '🥗', 'fitness': '💪', 'strong': '💪',
    'time': '⏰', 'quick': '⚡', 'fast': '⚡', 'easy': '✨', 'magic': '✨',
    'yes': '✅', 'no': '❌', 'stop': '🛑', 'go': '🚀', 'start': '🚀',
    'tip': '💡', 'idea': '💡', 'think': '🤔', 'question': '❓',
    'beauty': '💄', 'skin': '✨', 'glow': '✨', 'sleep': '😴', 'tired': '😴',
    'stress': '😰', 'relax': '😌', 'calm': '🧘', 'peace': '☮️',
}


@dataclass
class DynamicCaptionConfig:
    """Configuration for dynamic pop-in captions."""
    font_size: int = 85  # Large text
    font: str = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"  # Bold sans-serif
    text_color: str = "white"  # Main text color
    highlight_color: str = "#39FF14"  # Neon green for keywords
    stroke_color: str = "black"  # Thick outline
    stroke_width: int = 6  # Very thick for contrast
    words_per_phrase: int = 3  # 2-3 words per phrase
    pop_scale: float = 1.15  # Pop-in scale factor


def _get_emoji_for_phrase(phrase: str) -> str:
    """Get an emoji if the phrase contains emotional words."""
    phrase_lower = phrase.lower()
    for word, emoji in EMOJI_MAP.items():
        if word in phrase_lower:
            return emoji
    return ""


def _should_highlight(word: str) -> bool:
    """Check if word should be highlighted."""
    clean_word = re.sub(r'[^\w]', '', word.lower())
    return clean_word in HIGHLIGHT_KEYWORDS


def _make_pop_position(
    center_x: int,
    center_y: int,
    duration: float,
    pop_duration: float = 0.1
) -> Callable[[float], Tuple[int, int]]:
    """Create position function with pop-in effect."""
    def pos(t):
        return (center_x, center_y)
    return pos


def create_karaoke_captions(
    word_timings: List[WordTiming],
    brand_config: BrandConfig,
    config: Optional[DynamicCaptionConfig] = None
) -> List[TextClip]:
    """Create dynamic pop-in captions with highlighting and emojis.

    Features:
    - 2-3 word phrases that pop in
    - White text with thick black outline
    - Key words highlighted in neon green
    - Occasional emojis based on content

    Args:
        word_timings: List of WordTiming with start/end times for each word
        brand_config: Brand configuration
        config: Optional styling configuration

    Returns:
        List of TextClip objects to be composited onto the video
    """
    config = config or DynamicCaptionConfig()
    clips = []

    if not word_timings:
        return clips

    # Group words into short phrases (2-3 words)
    words_per_phrase = config.words_per_phrase

    for i in range(0, len(word_timings), words_per_phrase):
        group = word_timings[i:i + words_per_phrase]
        if not group:
            continue

        # Get timing for this phrase
        phrase_start = group[0].start
        phrase_end = group[-1].end
        phrase_duration = phrase_end - phrase_start

        if phrase_duration <= 0.05:
            continue

        # Build phrase and check for highlights
        words = [w.text for w in group]

        # Check if any word should be highlighted
        has_highlight = any(_should_highlight(w) for w in words)

        # Get emoji if applicable
        phrase_text = " ".join(words)
        emoji = _get_emoji_for_phrase(phrase_text)

        # Add emoji to phrase if found
        if emoji:
            phrase_text = f"{phrase_text} {emoji}"

        # Determine text color
        if has_highlight:
            text_color = config.highlight_color  # Neon green
        else:
            text_color = config.text_color  # White

        # Create text clip
        txt_clip = TextClip(
            text=phrase_text,
            font_size=config.font_size,
            font=config.font,
            color=text_color,
            stroke_color=config.stroke_color,
            stroke_width=config.stroke_width,
            method='label'
        )

        # Center position
        x_pos = (VIDEO_WIDTH - txt_clip.w) // 2
        y_pos = (VIDEO_HEIGHT - txt_clip.h) // 2

        # Apply position and timing
        txt_clip = txt_clip.with_position((x_pos, y_pos))
        txt_clip = txt_clip.with_start(phrase_start)
        txt_clip = txt_clip.with_duration(phrase_duration)

        clips.append(txt_clip)

    return clips


# Backward compatibility
KaraokeConfig = DynamicCaptionConfig
CaptionConfig = DynamicCaptionConfig
