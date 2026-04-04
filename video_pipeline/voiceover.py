"""
Generate MP3 voiceover from script text using the ElevenLabs Python SDK.
Returns duration in seconds.
"""

import logging
import os
import struct
import wave
from pathlib import Path
from typing import Optional

from .config import get_api_key

logger = logging.getLogger(__name__)

# Default voice IDs per style (ElevenLabs built-in voices)
DEFAULT_VOICE_IDS = {
    "motivational": "pNInz6obpgDQGcFmaJgB",   # Adam — deep, energetic
    "friendly": "EXAVITQu4vr4xnSDxMaL",        # Bella — warm, upbeat
    "calm": "21m00Tcm4TlvDq8ikWAM",             # Rachel — soothing
    "professional": "onwK4e9ZLuTAKqWW03F4",     # Daniel — clear, neutral
}
FALLBACK_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam


def _get_voice_id(voice_style: str) -> str:
    """Map a brand voice_style string to an ElevenLabs voice ID."""
    env_voice = os.environ.get("ELEVENLABS_VOICE_ID")
    if env_voice:
        return env_voice

    for key, voice_id in DEFAULT_VOICE_IDS.items():
        if key in voice_style.lower():
            return voice_id

    return FALLBACK_VOICE_ID


def _estimate_duration_from_text(text: str) -> float:
    """Rough estimate: average TTS speaks ~150 words per minute."""
    words = len(text.split())
    return round((words / 150) * 60, 1)


def _get_mp3_duration(path: Path) -> float:
    """
    Estimate MP3 duration by file size (rough but works without mutagen).
    Falls back to text-based estimate if path doesn't exist.
    """
    try:
        size_bytes = path.stat().st_size
        # Assume 128kbps = 16KB/s
        return round(size_bytes / 16_000, 1)
    except Exception:
        return 0.0


def generate_voiceover(
    script_text: str,
    output_path: Path,
    voice_style: str = "professional",
    model_id: str = "eleven_turbo_v2_5",
) -> float:
    """
    Generate an MP3 voiceover from script_text using ElevenLabs.

    Args:
        script_text: The narration text to convert to speech
        output_path: Where to save the MP3 file
        voice_style: Brand voice style string (used to pick voice ID)
        model_id: ElevenLabs model. eleven_turbo_v2_5 is fast + high quality.

    Returns:
        Duration of the audio in seconds (estimated)
    """
    try:
        from elevenlabs import ElevenLabs
    except ImportError:
        raise RuntimeError(
            "elevenlabs not installed. Run: pip install elevenlabs"
        )

    api_key = get_api_key("ELEVENLABS_API_KEY")
    voice_id = _get_voice_id(voice_style)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(
        f"Generating voiceover: voice_id={voice_id}, model={model_id}, "
        f"output={output_path}"
    )

    try:
        client = ElevenLabs(api_key=api_key)

        audio_generator = client.text_to_speech.convert(
            text=script_text,
            voice_id=voice_id,
            model_id=model_id,
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        )

        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                if chunk:
                    f.write(chunk)

        duration = _get_mp3_duration(output_path)
        if duration < 1.0:
            # Fallback to text estimate
            duration = _estimate_duration_from_text(script_text)

        logger.info(f"Voiceover saved: {output_path} (~{duration}s)")
        return duration

    except Exception as e:
        logger.error(f"ElevenLabs voiceover generation failed: {e}")
        # Clean up partial file
        if output_path.exists():
            output_path.unlink()
        raise
