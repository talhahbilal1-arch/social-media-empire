"""Edge-TTS client for text-to-speech with estimated word timing."""
import asyncio
import logging
import time
import re
from pathlib import Path
from typing import Optional, List
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
    - Word timing estimation for subtitle sync
    - Configurable voices per brand
    - Retry on service errors

    No API key required. Uses Microsoft's Edge browser TTS service.
    """

    # Brand voice mappings
    BRAND_VOICES = {
        "menopause": "en-US-JennyNeural",
        "daily_deal": "en-US-AriaNeural",
        "fitness": "en-US-EmmaNeural",
    }

    # Default voice if brand not found
    DEFAULT_VOICE = "en-US-AriaNeural"

    def __init__(
        self,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ):
        """Initialize TTS client."""
        self.voice = voice or self.DEFAULT_VOICE
        self.rate = rate
        self.pitch = pitch
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def for_brand(cls, brand_name: str, **kwargs) -> "TTSClient":
        """Create client with voice preset for brand."""
        normalized = brand_name.lower().split("-")[0].replace("_", "")
        voice = cls.BRAND_VOICES.get(normalized, cls.DEFAULT_VOICE)
        return cls(voice=voice, **kwargs)

    def _estimate_word_timings(self, text: str, total_duration_sec: float) -> List[WordTiming]:
        """Estimate word timings based on total duration and word lengths.

        Distributes time proportionally based on character count per word.
        """
        # Split text into words, preserving punctuation attached to words
        words = text.split()
        if not words:
            return []

        # Calculate total character weight (longer words take more time)
        # Add base weight per word for pauses
        BASE_WEIGHT = 2  # Base time units per word
        word_weights = [len(word) + BASE_WEIGHT for word in words]
        total_weight = sum(word_weights)

        # Distribute duration proportionally
        word_timings = []
        current_time = 0.0

        for word, weight in zip(words, word_weights):
            word_duration = (weight / total_weight) * total_duration_sec
            end_time = current_time + word_duration

            word_timings.append(WordTiming(
                text=word,
                start=current_time,
                end=end_time
            ))
            current_time = end_time

        return word_timings

    async def _generate_async(
        self,
        text: str,
        output_path: Path
    ) -> TTSResult:
        """Async implementation of TTS generation."""
        start = time.time()

        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            pitch=self.pitch
        )

        # Collect sentence boundaries for duration
        total_duration_100ns = 0

        with open(output_path, "wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                elif chunk["type"] == "SentenceBoundary":
                    # Get total duration from sentence boundary
                    offset = chunk.get("offset", 0)
                    duration = chunk.get("duration", 0)
                    end_time = offset + duration
                    if end_time > total_duration_100ns:
                        total_duration_100ns = end_time

        # Convert 100-nanosecond units to seconds
        total_duration_sec = total_duration_100ns / 10_000_000
        total_duration_ms = total_duration_sec * 1000

        # Estimate word timings based on total duration
        word_timings = self._estimate_word_timings(text, total_duration_sec)

        gen_time = time.time() - start
        self.logger.info(
            f"Generated TTS ({len(text)} chars, {len(word_timings)} words, {total_duration_ms:.0f}ms)",
            extra={
                "generation_time_ms": round(gen_time * 1000, 2),
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
        """Generate audio from text with estimated word timings."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        last_error = None
        for attempt in range(max_retries):
            try:
                return asyncio.run(self._generate_async(text, output_path))
            except Exception as e:
                last_error = e
                wait_time = (attempt + 1) * 2
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
        """List available voices."""
        voices = await edge_tts.list_voices()
        return voices
