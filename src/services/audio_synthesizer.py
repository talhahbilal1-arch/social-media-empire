"""Audio synthesizer service with TTS and caching."""
import logging
from pathlib import Path
from typing import Optional
import hashlib

from src.clients.tts import TTSClient, TTSResult
from src.models.brand import BrandConfig
from src.models.content import AudioResult
from src.utils.cache import FileCache
from src.video.timing import WordTiming


class AudioSynthesizer:
    """Generate TTS audio with brand-specific voices and caching.

    Uses Edge-TTS for audio generation with word timing extraction.
    Caches by hash of (script text + voice ID) to prevent redundant generation.

    Cache strategy:
    - Audio files: Stored in cache/audio/ directory with hash-based names
    - Metadata cache: JSON with word timings, duration, voice info
    - Cache key: hash of script text + voice ID
    """

    def __init__(self, cache_dir: Path = None):
        """Initialize AudioSynthesizer.

        Args:
            cache_dir: Directory for audio cache (defaults to cache/audio)
        """
        self.cache_dir = cache_dir or Path("cache/audio")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_cache = FileCache("audio_metadata")
        self.logger = logging.getLogger(self.__class__.__name__)

    def _cache_key(self, script_text: str, voice: str) -> str:
        """Generate cache key from script text and voice.

        Uses hash to handle long scripts and special characters.
        """
        content = f"{voice}_{script_text}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _audio_path(self, cache_key: str) -> Path:
        """Get audio file path for cache key."""
        return self.cache_dir / f"{cache_key}.mp3"

    def _get_cached(self, cache_key: str) -> Optional[AudioResult]:
        """Get cached audio result if exists and file is valid."""
        metadata = self.metadata_cache.get(cache_key)
        if not metadata:
            return None

        audio_path = Path(metadata.get("audio_path", ""))
        if not audio_path.exists() or audio_path.stat().st_size == 0:
            # File missing or empty - invalidate cache
            self.metadata_cache.delete(cache_key)
            self.logger.info(
                "Cache INVALID (file missing)",
                extra={"cache_key": cache_key}
            )
            return None

        # Reconstruct WordTiming objects from cached data
        word_timings = [
            WordTiming(
                text=wt["text"],
                start=wt["start"],
                end=wt["end"]
            )
            for wt in metadata.get("word_timings", [])
        ]

        self.logger.debug(
            "Cache HIT for audio",
            extra={"cache_key": cache_key, "path": str(audio_path)}
        )

        return AudioResult(
            audio_path=audio_path,
            word_timings=word_timings,
            duration_ms=metadata.get("duration_ms", 0.0)
        )
