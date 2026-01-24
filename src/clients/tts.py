"""Edge-TTS client for text-to-speech with word timing."""
import asyncio
import logging
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import edge_tts

from src.video.timing import WordTiming


@dataclass
class TTSResult:
    """Result of TTS generation."""
    audio_path: Path
    word_timings: list[WordTiming]
    duration_ms: float  # Total audio duration


class TTSClient:
    """Client for Microsoft Edge Text-to-Speech.

    Handles:
    - Audio generation from text
    - Word timing extraction for subtitle sync
    - Configurable voices per brand
    - Retry on service errors

    No API key required. Uses Microsoft's Edge browser TTS service.
    """

    # Brand voice mappings (from project decision 02-02)
    BRAND_VOICES = {
        "menopause": "en-US-JennyNeural",
        "daily_deal": "en-US-AriaNeural",
        "fitness": "en-US-EmmaNeural",  # Changed from SaraNeural (unavailable)
    }

    # Default voice if brand not found
    DEFAULT_VOICE = "en-US-AriaNeural"

    def __init__(
        self,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ):
        """Initialize TTS client.

        Args:
            voice: Voice ID (e.g., 'en-US-JennyNeural')
            rate: Speech rate adjustment (e.g., '+10%', '-5%')
            pitch: Pitch adjustment (e.g., '+5Hz', '-10Hz')
        """
        self.voice = voice or self.DEFAULT_VOICE
        self.rate = rate
        self.pitch = pitch
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def for_brand(cls, brand_name: str, **kwargs) -> "TTSClient":
        """Create client with voice preset for brand.

        Args:
            brand_name: Brand identifier (menopause, daily_deal, fitness)
            **kwargs: Additional arguments passed to __init__

        Returns:
            TTSClient configured for brand voice
        """
        # Normalize slug: "menopause-planner" -> "menopause" to match BRAND_VOICES keys
        normalized = brand_name.lower().split("-")[0].replace("_", "")
        voice = cls.BRAND_VOICES.get(normalized, cls.DEFAULT_VOICE)
        return cls(voice=voice, **kwargs)

    async def _generate_async(
        self,
        text: str,
        output_path: Path
    ) -> TTSResult:
        """Async implementation of TTS generation.

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file

        Returns:
            TTSResult with audio path and word timings
        """
        start = time.time()
        word_timings: list[WordTiming] = []

        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            pitch=self.pitch
        )

        with open(output_path, "wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # Extract word timing from WordBoundary event
                    # offset is in 100-nanosecond units, convert to seconds
                    offset_100ns = chunk["offset"]
                    duration_100ns = chunk["duration"]
                    word = chunk["text"]

                    start_sec = offset_100ns / 10_000_000  # 100ns to seconds
                    duration_sec = duration_100ns / 10_000_000
                    end_sec = start_sec + duration_sec

                    # CRITICAL: Use text=word (not word=word) per WordTiming dataclass
                    word_timings.append(WordTiming(
                        text=word,
                        start=start_sec,
                        end=end_sec
                    ))

        duration = time.time() - start

        # Calculate total audio duration from last word
        total_duration_ms = 0.0
        if word_timings:
            total_duration_ms = word_timings[-1].end * 1000

        self.logger.info(
            f"Generated TTS ({len(text)} chars, {len(word_timings)} words)",
            extra={
                "duration_ms": round(duration * 1000, 2),
                "voice": self.voice,
                "text_length": len(text),
                "word_count": len(word_timings),
                "audio_duration_ms": round(total_duration_ms, 2)
            }
        )

        return TTSResult(
            audio_path=output_path,
            word_timings=word_timings,
            duration_ms=total_duration_ms
        )

    def generate(
        self,
        text: str,
        output_path: Path,
        max_retries: int = 3
    ) -> TTSResult:
        """Generate audio from text with word timings.

        Sync wrapper around async implementation with retry logic.

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file (.mp3)
            max_retries: Number of retries on failure

        Returns:
            TTSResult with audio path and word timings

        Raises:
            Exception: After max retries exhausted
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        last_error = None
        for attempt in range(max_retries):
            try:
                return asyncio.run(self._generate_async(text, output_path))
            except Exception as e:
                last_error = e
                wait_time = (attempt + 1) * 2  # 2, 4, 6 seconds
                self.logger.warning(
                    f"TTS attempt {attempt + 1}/{max_retries} failed: {e}",
                    extra={"wait_seconds": wait_time}
                )
                if attempt < max_retries - 1:
                    time.sleep(wait_time)

        self.logger.error(
            f"TTS generation failed after {max_retries} attempts",
            extra={"error": str(last_error)}
        )
        raise last_error

    @staticmethod
    async def list_voices() -> list[dict]:
        """List available voices.

        Returns:
            List of voice info dicts with Name, Gender, Locale
        """
        voices = await edge_tts.list_voices()
        return voices
