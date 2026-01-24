"""Content generation data models.

This module provides dataclasses for content generation pipeline output,
including scripts, audio results, and complete generated content bundles.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.video.timing import WordTiming


@dataclass
class Script:
    """Generated script with metadata for video creation.

    Holds the AI-generated script content along with metadata needed
    for video production including search terms and timing estimates.
    """

    topic: str
    voiceover: str
    search_terms: List[str]
    brand_slug: str
    cta_text: str
    estimated_duration: float  # seconds (calculated at ~150 words/min)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize script to dictionary for caching.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "topic": self.topic,
            "voiceover": self.voiceover,
            "search_terms": self.search_terms,
            "brand_slug": self.brand_slug,
            "cta_text": self.cta_text,
            "estimated_duration": self.estimated_duration,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Script":
        """Deserialize script from dictionary.

        Args:
            data: Dictionary from cache or API response.

        Returns:
            Script instance with loaded data.
        """
        return cls(
            topic=data["topic"],
            voiceover=data["voiceover"],
            search_terms=data["search_terms"],
            brand_slug=data["brand_slug"],
            cta_text=data["cta_text"],
            estimated_duration=data["estimated_duration"],
        )

    @staticmethod
    def estimate_duration(text: str, words_per_minute: float = 150.0) -> float:
        """Estimate speaking duration for text.

        Args:
            text: Text to estimate duration for.
            words_per_minute: Speaking rate (default 150 WPM for natural speech).

        Returns:
            Estimated duration in seconds.
        """
        word_count = len(text.split())
        return (word_count / words_per_minute) * 60.0


@dataclass
class AudioResult:
    """TTS audio generation result with timing data.

    Contains the path to generated audio file and word-level timing
    information for text overlay synchronization.
    """

    audio_path: Path
    word_timings: List[WordTiming]
    duration_ms: float  # milliseconds

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds."""
        return self.duration_ms / 1000.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize audio result to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "audio_path": str(self.audio_path),
            "word_timings": [
                {"text": wt.text, "start": wt.start, "end": wt.end}
                for wt in self.word_timings
            ],
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AudioResult":
        """Deserialize audio result from dictionary.

        Args:
            data: Dictionary from cache.

        Returns:
            AudioResult instance with loaded data.
        """
        return cls(
            audio_path=Path(data["audio_path"]),
            word_timings=[
                WordTiming(text=wt["text"], start=wt["start"], end=wt["end"])
                for wt in data["word_timings"]
            ],
            duration_ms=data["duration_ms"],
        )


@dataclass
class GeneratedContent:
    """Complete generated content bundle for video production.

    Bundles together all components needed to produce a final video:
    the script, downloaded stock video, synthesized audio, and metadata.
    """

    script: Script
    video_path: Path
    audio_result: AudioResult
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete content to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "script": self.script.to_dict(),
            "video_path": str(self.video_path),
            "audio_result": self.audio_result.to_dict(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeneratedContent":
        """Deserialize complete content from dictionary.

        Args:
            data: Dictionary from cache.

        Returns:
            GeneratedContent instance with loaded data.
        """
        return cls(
            script=Script.from_dict(data["script"]),
            video_path=Path(data["video_path"]),
            audio_result=AudioResult.from_dict(data["audio_result"]),
            metadata=data.get("metadata", {}),
        )
