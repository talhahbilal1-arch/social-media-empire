"""Gemini API client for text generation with rate limit handling."""
import logging
import time
from typing import Optional
import backoff
from google import genai
from google.genai import types

from config.settings import settings


class GeminiClient:
    """Client for Google Gemini text generation API.

    Handles:
    - 429 rate limit errors with exponential backoff (8 retries, 5 min max)
    - Structured logging with duration and status
    - Model selection (default: gemini-1.5-flash-latest)

    Note: Free tier is 5 RPM as of Dec 2025. Retry logic is essential.
    """

    DEFAULT_MODEL = "gemini-1.5-flash-latest"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Initialize Gemini client.

        Args:
            api_key: Gemini API key (defaults to settings.GEMINI_API_KEY)
            model: Model ID (defaults to gemini-1.5-flash-latest)
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        self.model = model or self.DEFAULT_MODEL
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client = genai.Client(api_key=self.api_key)

    def _is_rate_limit_error(self, exception: Exception) -> bool:
        """Check if exception is a rate limit (429) error."""
        error_str = str(exception).lower()
        return "429" in error_str or "rate" in error_str or "quota" in error_str

    @backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=8,
        max_time=300,  # 5 minutes max
        giveup=lambda e: "429" not in str(e) and "rate" not in str(e).lower() and "quota" not in str(e).lower(),
        on_backoff=lambda details: logging.getLogger("GeminiClient").warning(
            f"Rate limit hit, backing off {details['wait']:.1f}s (attempt {details['tries']}/8)"
        )
    )
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """Generate text from prompt.

        Args:
            prompt: Input prompt for generation
            max_tokens: Maximum output tokens (default 1024)
            temperature: Sampling temperature 0-1 (default 0.7)

        Returns:
            Generated text string

        Raises:
            Exception: On non-retryable errors or after max retries
        """
        start = time.time()

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
            )

            duration = time.time() - start
            self.logger.info(
                f"Generated text ({len(response.text)} chars)",
                extra={
                    "duration_ms": round(duration * 1000, 2),
                    "model": self.model,
                    "prompt_length": len(prompt)
                }
            )
            return response.text

        except Exception as e:
            duration = time.time() - start
            self.logger.error(
                f"Generation failed: {e}",
                extra={
                    "duration_ms": round(duration * 1000, 2),
                    "model": self.model,
                    "error": str(e)
                }
            )
            raise
