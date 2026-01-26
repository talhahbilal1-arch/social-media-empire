"""Dynamic karaoke-style captions with word-by-word highlighting and pop-in animation.

Features:
- Word-by-word color change (white → neon cyan) as words are spoken
- Pop-in scale animation for each phrase
- Bold sans-serif font with thick black outline
- Safe zone positioning
- Automatic emoji insertion for emotional content
"""

from typing import List, Optional, Callable, Tuple
from dataclasses import dataclass
from moviepy import TextClip, CompositeVideoClip, ColorClip
from src.models.brand import BrandConfig
from src.video.timing import WordTiming
import re


# Video dimensions (1080x1920 portrait)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Safe zones for social media (avoid UI elements)
SAFE_MARGIN_TOP = 150
SAFE_MARGIN_BOTTOM = 350  # Avoid like/subscribe buttons
SAFE_MARGIN_SIDES = 80

# Position in lower third of screen
CAPTION_Y_POSITION = int(VIDEO_HEIGHT * 0.70)  # 70% from top = lower area

# Emotional words that get emojis
EMOJI_MAP = {
    'love': '❤️', 'heart': '❤️', 'healthy': '💚', 'health': '💚',
    'happy': '😊', 'joy': '😊', 'smile': '😊',
    'sad': '😢', 'struggle': '😢', 'struggled': '😢', 'hard': '😤',
    'amazing': '🔥', 'incredible': '🔥', 'awesome': '🔥',
    'wow': '😮', 'shocked': '😮', 'surprise': '😮',
    'money': '💰', 'save': '💵', 'deal': '💵', 'free': '🎁',
    'food': '🍽️', 'eat': '🍴', 'delicious': '😋', 'yummy': '😋',
    'fitness': '💪', 'strong': '💪', 'workout': '💪', 'exercise': '🏋️',
    'tired': '😴', 'sleep': '😴', 'exhausted': '😩',
    'stress': '😰', 'anxious': '😰', 'worry': '😟',
    'relax': '😌', 'calm': '🧘', 'peace': '☮️',
    'beauty': '💄', 'skin': '✨', 'glow': '✨', 'shine': '✨',
    'tip': '💡', 'secret': '🤫', 'hack': '🔑',
    'yes': '✅', 'perfect': '👌', 'exactly': '💯',
    'no': '❌', 'never': '🚫', 'stop': '🛑',
    'quick': '⚡', 'fast': '⚡', 'easy': '✨', 'simple': '👍',
    'woman': '👩', 'women': '👩', 'girl': '👧', 'ladies': '💃',
    'hot': '🔥', 'cool': '😎', 'best': '🏆', 'winner': '🏆',
    'morning': '🌅', 'night': '🌙', 'day': '☀️',
    'coffee': '☕', 'water': '💧', 'drink': '🥤',
}


@dataclass
class KaraokeConfig:
    """Configuration for karaoke-style captions."""
    font_size: int = 80  # Large bold text
        font: str = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Heavy bold
    base_color: str = "white"  # Bright white for non-highlighted words
    highlight_color: str = "#00FFFF"  # Neon cyan for current word
    alt_highlight: str = "#FFFF00"  # Electric yellow (alternate)
    stroke_color: str = "black"  # Thick solid black outline
    stroke_width: int = 4  # Thick for readability
    words_per_phrase: int = 3  # 2-3 words shown at once


def _get_phrase_emoji(words: List[str]) -> str:
    """Get emoji for phrase based on emotional content."""
    phrase = " ".join(words).lower()
    for keyword, emoji in EMOJI_MAP.items():
        if keyword in phrase:
            return emoji
    return ""


def _create_padded_text_clip(
    text: str,
    font_size: int,
    font: str,
    color: str,
    stroke_color: Optional[str] = None,
    stroke_width: int = 0,
    padding: int = 20
) -> TextClip:
    """Create a TextClip with padding to prevent clipping.

    MoviePy's TextClip sometimes clips descenders. This adds padding
    by using method='caption' with extra vertical space.
    """
    # Use caption method with explicit size to add padding
    # First create a label to measure the text
    measure_clip = TextClip(
        text=text,
        font_size=font_size,
        font=font,
        color=color,
        method='label'
    )
    text_w = measure_clip.w
    text_h = measure_clip.h
    measure_clip.close()

    # Create with extra padding using caption method
    clip_args = {
        'text': text,
        'font_size': font_size,
        'font': font,
        'color': color,
        'size': (text_w + padding * 2, text_h + padding * 2),
        'method': 'caption'
    }
    if stroke_color and stroke_width > 0:
        clip_args['stroke_color'] = stroke_color
        clip_args['stroke_width'] = stroke_width

    return TextClip(**clip_args)


def _create_word_clip(
    word: str,
    font_size: int,
    font: str,
    color: str,
    stroke_color: str,
    stroke_width: int
) -> TextClip:
    """Create a single word text clip."""
    return TextClip(
        text=word,
        font_size=font_size,
        font=font,
        color=color,
        stroke_color=stroke_color,
        stroke_width=stroke_width,
        method='label'
    )


def create_karaoke_captions(
    word_timings: List[WordTiming],
    brand_config: BrandConfig,
    config: Optional[KaraokeConfig] = None
) -> List[TextClip]:
    """Create karaoke-style captions with word-by-word highlighting.

    Shows 2-3 word phrases with the current spoken word highlighted
    in neon cyan/yellow while others stay white. Includes emojis.

    Args:
        word_timings: List of WordTiming with start/end times
        brand_config: Brand configuration
        config: Optional styling configuration

    Returns:
        List of TextClip objects for compositing
    """
    config = config or KaraokeConfig()
    clips = []

    if not word_timings:
        return clips

    words_per_phrase = config.words_per_phrase  # 2-3 words

    # Process in phrase groups
    for phrase_idx in range(0, len(word_timings), words_per_phrase):
        phrase_words = word_timings[phrase_idx:phrase_idx + words_per_phrase]
        if not phrase_words:
            continue

        # Get emoji for this phrase
        word_texts = [w.text for w in phrase_words]
        emoji = _get_phrase_emoji(word_texts)

        # For each word in the phrase, create a frame with that word highlighted
        for highlight_idx, current_word in enumerate(phrase_words):
            word_start = current_word.start
            word_end = current_word.end
            word_duration = word_end - word_start

            if word_duration <= 0.02:
                continue

            # Alternate highlight colors for variety
            highlight_color = config.highlight_color if highlight_idx % 2 == 0 else config.alt_highlight

            # Build the phrase text with colors
            # We'll create one TextClip per word and position them
            word_clips_for_frame = []
            word_widths = []

            # First pass: create clips with padding to prevent clipping
            for i, wt in enumerate(phrase_words):
                is_highlighted = (i == highlight_idx)
                color = highlight_color if is_highlighted else config.base_color

                clip = _create_padded_text_clip(
                    text=wt.text,
                    font_size=config.font_size,
                    font=config.font,
                    color=color,
                    stroke_color=config.stroke_color if config.stroke_color else None,
                    stroke_width=config.stroke_width if config.stroke_width else 0,
                    padding=30  # Extra padding to prevent clipping
                )
                word_clips_for_frame.append(clip)
                word_widths.append(clip.w)

            # Add emoji clip on last word of phrase
            emoji_clip = None
            emoji_width = 0
            if emoji and highlight_idx == len(phrase_words) - 1:
                emoji_clip = TextClip(
                    text=emoji,
                    font_size=config.font_size,
                    font=config.font,
                    method='label'
                )
                emoji_width = emoji_clip.w + 10  # 10px spacing before emoji

            # Calculate total width with spacing
            space_width = 20  # Fixed space between words
            total_width = sum(word_widths) + space_width * (len(word_widths) - 1) + emoji_width

            # If too wide, reduce and rebuild
            if total_width > VIDEO_WIDTH - 2 * SAFE_MARGIN_SIDES:
                # Close old clips
                for c in word_clips_for_frame:
                    c.close()
                if emoji_clip:
                    emoji_clip.close()

                # Rebuild with smaller font
                smaller_font = int(config.font_size * 0.7)
                word_clips_for_frame = []
                word_widths = []

                for i, wt in enumerate(phrase_words):
                    is_highlighted = (i == highlight_idx)
                    color = highlight_color if is_highlighted else config.base_color

                    clip = _create_padded_text_clip(
                        text=wt.text,
                        font_size=smaller_font,
                        font=config.font,
                        color=color,
                        stroke_color=config.stroke_color if config.stroke_color else None,
                        stroke_width=max(1, config.stroke_width - 1) if config.stroke_width else 0,
                        padding=25
                    )
                    word_clips_for_frame.append(clip)
                    word_widths.append(clip.w)

                if emoji and highlight_idx == len(phrase_words) - 1:
                    emoji_clip = TextClip(
                        text=emoji,
                        font_size=smaller_font,
                        font=config.font,
                        method='label'
                    )
                    emoji_width = emoji_clip.w + 10
                else:
                    emoji_clip = None
                    emoji_width = 0

                total_width = sum(word_widths) + space_width * (len(word_widths) - 1) + emoji_width

            # Calculate starting X to center the phrase
            start_x = (VIDEO_WIDTH - total_width) // 2
            start_x = max(SAFE_MARGIN_SIDES, start_x)

            # Get text height and center vertically on the Y position
            text_height = word_clips_for_frame[0].h if word_clips_for_frame else 100
            # Offset Y position to account for text height (center the text on the line)
            y_pos = CAPTION_Y_POSITION - (text_height // 2)

            # Position each word clip
            current_x = start_x
            for i, word_clip in enumerate(word_clips_for_frame):
                # Ensure within bounds
                safe_x = max(SAFE_MARGIN_SIDES, min(current_x, VIDEO_WIDTH - word_clip.w - SAFE_MARGIN_SIDES))

                positioned = word_clip.with_position((safe_x, y_pos))
                positioned = positioned.with_start(word_start)
                positioned = positioned.with_duration(word_duration)
                clips.append(positioned)

                current_x += word_widths[i] + space_width

            # Add emoji if present
            if emoji_clip:
                emoji_x = current_x - space_width + 10
                safe_emoji_x = max(SAFE_MARGIN_SIDES, min(emoji_x, VIDEO_WIDTH - emoji_clip.w - SAFE_MARGIN_SIDES))

                positioned_emoji = emoji_clip.with_position((safe_emoji_x, y_pos))
                positioned_emoji = positioned_emoji.with_start(word_start)
                positioned_emoji = positioned_emoji.with_duration(word_duration)
                clips.append(positioned_emoji)

    return clips


# Backward compatibility
CaptionConfig = KaraokeConfig
DynamicCaptionConfig = KaraokeConfig
