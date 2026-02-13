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

    def synthesize(
        self,
        script_text: str,
        brand_config: BrandConfig
    ) -> AudioResult:
        """Generate TTS audio from script text.

        Args:
            script_text: Voiceover text to synthesize
            brand_config: Brand configuration with TTS voice

        Returns:
            AudioResult with audio path, word timings, and duration

        Flow:
            1. Check cache for existing audio
            2. If cache miss: create TTSClient with brand voice
            3. Generate audio with word timing
            4. Cache metadata and return
        """
        voice = brand_config.tts_voice
        cache_key = self._cache_key(script_text, voice)

        # Check cache first
        cached = self._get_cached(cache_key)
        if cached:
            self.logger.info(
                f"Cache HIT for {brand_config.slug} audio",
                extra={"cache_key": cache_key, "voice": voice}
            )
            return cached

        self.logger.info(
            f"Cache MISS, generating audio for {brand_config.slug}",
            extra={"cache_key": cache_key, "voice": voice, "text_length": len(script_text)}
        )

        # Create TTS client with brand voice
        tts_client = TTSClient.for_brand(brand_config.slug)

        # Generate audio with word timing
        audio_path = self._audio_path(cache_key)
        tts_result = tts_client.generate(script_text, audio_path)

        # Create AudioResult
        audio_result = AudioResult(
            audio_path=tts_result.audio_path,
            word_timings=tts_result.word_timings,
            duration_ms=tts_result.duration_ms
        )

        # Cache metadata (word timings as dicts for JSON serialization)
        self.metadata_cache.set(cache_key, {
            "audio_path": str(audio_result.audio_path),
            "word_timings": [
                {"text": wt.text, "start": wt.start, "end": wt.end}
                for wt in audio_result.word_timings
            ],
            "duration_ms": audio_result.duration_ms,
            "voice": voice,
            "brand_slug": brand_config.slug,
            "text_length": len(script_text)
        })

        self.logger.info(
            "Generated and cached audio",
            extra={
                "path": str(audio_path),
                "duration_ms": audio_result.duration_ms,
                "word_count": len(audio_result.word_timings)
            }
        )

        return audio_result

    def synthesize_script(self, script: "Script", brand_config: BrandConfig) -> AudioResult:
        """Convenience method to synthesize audio from Script dataclass.

        Args:
            script: Script dataclass with voiceover text
            brand_config: Brand configuration with TTS voice

        Returns:
            AudioResult with audio path and word timings
        """
        from src.models.content import Script  # Avoid circular import
        return self.synthesize(script.voiceover, brand_config)

    def clear_cache(self) -> int:
        """Clear all cached audio files and metadata.

        Returns:
            Number of files deleted
        """
        # Clear metadata
        metadata_count = self.metadata_cache.clear()

        # Clear audio files
        audio_count = 0
        for audio_file in self.cache_dir.glob("*.mp3"):
            audio_file.unlink()
            audio_count += 1

        self.logger.info(
            "Cleared cache",
            extra={"metadata_entries": metadata_count, "audio_files": audio_count}
        )

        return metadata_count + audio_count
