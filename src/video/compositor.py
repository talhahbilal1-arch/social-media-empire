"""Core video composition engine with karaoke-style captions.

This module implements the VideoCompositor class which handles:
- 16:9 to 9:16 aspect ratio conversion via center-cropping
- Karaoke-style word-by-word caption highlighting
- Clip tracking for memory management
"""

import gc
from typing import TYPE_CHECKING, List, Optional

from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip

from src.models.brand import BrandConfig
from src.video.text_overlay import create_karaoke_captions, KaraokeConfig
from src.video.timing import WordTiming, SentenceTiming

if TYPE_CHECKING:
    pass

# Video output dimensions (9:16 vertical format)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Target frame rate for consistent playback
TARGET_FPS = 24


class VideoCompositor:
    """Compositor for creating vertical format social media videos.

    Handles aspect ratio conversion, karaoke-style captions,
    audio composition, and memory management for MoviePy clips.
    """

    def __init__(self, brand_config: BrandConfig) -> None:
        """Initialize compositor with brand configuration.

        Args:
            brand_config: Brand-specific settings for colors, voice, and CTAs
        """
        self.brand_config = brand_config
        self.clips_to_close: list = []

    def convert_to_vertical(self, video_path: str) -> VideoFileClip:
        """Convert 16:9 video to 9:16 by center cropping.

        Args:
            video_path: Path to input video file

        Returns:
            VideoFileClip resized to 1080x1920 (9:16)
        """
        # Load video and track for cleanup
        clip = VideoFileClip(video_path)
        self.clips_to_close.append(clip)

        # Calculate aspect ratios
        target_aspect = VIDEO_WIDTH / VIDEO_HEIGHT  # 0.5625 (9:16)
        current_aspect = clip.w / clip.h

        # Center crop based on aspect ratio difference
        if current_aspect > target_aspect:
            # Video is wider (most common for 16:9) - crop sides
            new_width = int(clip.h * target_aspect)
            x1 = int((clip.w - new_width) / 2)
            cropped = clip.cropped(x1=x1, y1=0, width=new_width, height=clip.h)
        else:
            # Video is taller - crop top and bottom
            new_height = int(clip.w / target_aspect)
            y1 = int((clip.h - new_height) / 2)
            cropped = clip.cropped(x1=0, y1=y1, width=clip.w, height=new_height)

        # Track cropped clip
        self.clips_to_close.append(cropped)

        # Resize to exact target dimensions
        resized = cropped.resized((VIDEO_WIDTH, VIDEO_HEIGHT))
        self.clips_to_close.append(resized)

        # Assert even dimensions (required for some codecs)
        assert resized.w % 2 == 0 and resized.h % 2 == 0, \
            f"Dimensions must be even: {resized.w}x{resized.h}"

        # Set target FPS
        final = resized.with_fps(TARGET_FPS)
        self.clips_to_close.append(final)

        return final

    def compose_video(
        self,
        video_path: str,
        audio_path: str,
        word_timings: List[WordTiming],
        output_path: str,
        sentence_timings: Optional[List[SentenceTiming]] = None  # Kept for compatibility
    ) -> None:
        """Compose final video with background, karaoke captions, and audio.

        Args:
            video_path: Path to stock video (any aspect ratio)
            audio_path: Path to TTS audio file
            word_timings: List of WordTiming for karaoke-style captions
            output_path: Where to write the final MP4
            sentence_timings: Deprecated, kept for compatibility

        Raises:
            FileNotFoundError: If video or audio files don't exist
            RuntimeError: If composition fails

        Note:
            Call cleanup() after this method completes to release memory.
        """
        # Convert stock video to vertical
        bg_clip = self.convert_to_vertical(video_path)

        # Load audio
        audio_clip = AudioFileClip(audio_path)
        self.clips_to_close.append(audio_clip)

        # Match video duration exactly to audio to prevent drift
        bg_clip = bg_clip.with_duration(audio_clip.duration)
        self.clips_to_close.append(bg_clip)

        # Create karaoke-style caption clips
        caption_clips = create_karaoke_captions(
            word_timings=word_timings,
            brand_config=self.brand_config
        )

        # Track all caption clips for cleanup
        for clip in caption_clips:
            self.clips_to_close.append(clip)

        # Compose all layers - background first, then captions on top
        video = CompositeVideoClip([bg_clip] + caption_clips)
        video = video.with_audio(audio_clip)
        self.clips_to_close.append(video)

        # Export with optimized settings
        video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=TARGET_FPS,
            preset='medium',
            ffmpeg_params=['-crf', '23'],
            threads=4,
            logger=None  # Suppress progress bar in production
        )

    def cleanup(self) -> None:
        """Close all tracked clips to prevent memory leaks.

        CRITICAL: Must be called after write_videofile() completes.
        Failure to call this will cause memory to accumulate in batch processing.
        """
        for clip in self.clips_to_close:
            try:
                clip.close()
            except Exception:
                pass  # Ignore close errors - clip may already be closed
        self.clips_to_close.clear()
        gc.collect()
