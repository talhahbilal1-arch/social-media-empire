"""External API clients for third-party integrations."""
from src.clients.base import BaseClient
from src.clients.gemini import GeminiClient
from src.clients.pexels import PexelsClient
from src.clients.tts import TTSClient, TTSResult
from src.clients.storage import SupabaseClient, UploadResult

__all__ = [
    "BaseClient",
    "GeminiClient",
    "PexelsClient",
    "TTSClient",
    "TTSResult",
    "SupabaseClient",
    "UploadResult"
]
