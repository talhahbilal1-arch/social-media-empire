"""External API clients for third-party integrations."""
import logging

_logger = logging.getLogger(__name__)

from src.clients.base import BaseClient

# Import each client with fault tolerance so one broken dependency
# doesn't prevent other clients from being used
try:
    from src.clients.gemini import GeminiClient
except ImportError as e:
    _logger.debug(f"GeminiClient unavailable: {e}")
    GeminiClient = None

try:
    from src.clients.pexels import PexelsClient
except ImportError as e:
    _logger.debug(f"PexelsClient unavailable: {e}")
    PexelsClient = None

try:
    from src.clients.tts import TTSClient, TTSResult
except ImportError as e:
    _logger.debug(f"TTSClient unavailable: {e}")
    TTSClient = None
    TTSResult = None

try:
    from src.clients.storage import SupabaseClient, UploadResult
except ImportError as e:
    _logger.debug(f"SupabaseClient unavailable: {e}")
    SupabaseClient = None
    UploadResult = None

try:
    from src.clients.late_api import LateAPIClient, LatePostResult, create_late_client
except ImportError as e:
    _logger.debug(f"LateAPIClient unavailable: {e}")
    LateAPIClient = None
    LatePostResult = None
    create_late_client = None

__all__ = [
    "BaseClient",
    "GeminiClient",
    "PexelsClient",
    "TTSClient",
    "TTSResult",
    "SupabaseClient",
    "UploadResult",
    "LateAPIClient",
    "LatePostResult",
    "create_late_client",
]
