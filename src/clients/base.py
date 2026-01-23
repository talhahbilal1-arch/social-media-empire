"""Base client with shared retry logic and logging."""
import logging
import time
from typing import Optional
import backoff
import httpx


class BaseClient:
    """Base class for API clients with retry logic and structured logging.

    Provides:
    - HTTP client with connection pooling
    - Exponential backoff on transient errors
    - Structured logging with duration/status/error metadata
    - Context manager support for cleanup
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        logger_name: Optional[str] = None
    ):
        """Initialize base client.

        Args:
            base_url: Base URL for API requests
            api_key: Optional API key for Authorization header
            timeout: Request timeout in seconds
            logger_name: Logger name (defaults to class name)
        """
        self.base_url = base_url
        self.logger = logging.getLogger(logger_name or self.__class__.__name__)

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers=headers
        )

    def _should_retry(self, exception: Exception) -> bool:
        """Determine if exception is retryable.

        Only retry on:
        - 429 (rate limit)
        - 5xx (server errors)
        - Network errors

        Do NOT retry on 4xx client errors (except 429).
        """
        if isinstance(exception, httpx.HTTPStatusError):
            status = exception.response.status_code
            return status == 429 or status >= 500
        return isinstance(exception, (httpx.RequestError, httpx.TimeoutException))

    @backoff.on_exception(
        backoff.expo,
        (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException),
        max_tries=8,
        max_time=300,  # 5 minutes max
        giveup=lambda e: not BaseClient._should_retry_static(e),
        on_backoff=lambda details: logging.getLogger("BaseClient").warning(
            f"Backing off {details['wait']:.1f}s after {details['tries']} tries"
        )
    )
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with automatic retry on transient errors.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: URL path (appended to base_url)
            **kwargs: Additional arguments passed to httpx.request

        Returns:
            httpx.Response on success

        Raises:
            httpx.HTTPStatusError: On non-retryable 4xx errors
        """
        start = time.time()

        try:
            response = self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()

            duration = time.time() - start
            self.logger.info(
                f"{method} {endpoint}",
                extra={
                    "duration_ms": round(duration * 1000, 2),
                    "status": response.status_code
                }
            )
            return response

        except Exception as e:
            duration = time.time() - start
            self.logger.error(
                f"{method} {endpoint} failed: {e}",
                extra={
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e)
                }
            )
            raise

    @staticmethod
    def _should_retry_static(exception: Exception) -> bool:
        """Static version for backoff giveup lambda."""
        if isinstance(exception, httpx.HTTPStatusError):
            status = exception.response.status_code
            return status == 429 or status >= 500
        return isinstance(exception, (httpx.RequestError, httpx.TimeoutException))

    def close(self) -> None:
        """Close the HTTP client connection pool."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
