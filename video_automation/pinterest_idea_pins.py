"""Pinterest Idea Pin creation via Late API (preferred) or Make.com webhook (fallback)."""

import logging
import os
from typing import Optional
from dataclasses import dataclass

from utils.config import get_config
from utils.api_clients import PinterestClient

# Try to import Late API client
try:
    from src.clients.late_api import LateAPIClient, create_late_client
    LATE_API_AVAILABLE = True
except ImportError:
    LATE_API_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PinterestIdeaPinCreator:
    """Creates Pinterest Idea Pins via Late API (preferred) or Make.com webhook (fallback).

    Late API handles Pinterest's complex video upload workflow properly, while
    Make.com webhooks have issues with video pins (error 235 "Sorry, this image is broken").
    """

    pinterest_client: PinterestClient = None
    late_client: "LateAPIClient" = None

    def __post_init__(self):
        config = get_config()

        # Try Late API first (preferred for video pins)
        if self.late_client is None and LATE_API_AVAILABLE:
            late_api_key = os.getenv('LATE_API_KEY')
            if late_api_key:
                try:
                    self.late_client = LateAPIClient(api_key=late_api_key)
                    logger.info("Pinterest posting using Late API")
                except Exception as e:
                    logger.warning(f"Failed to initialize Late API client: {e}")
                    self.late_client = None

        # Fallback to Make.com webhook
        if self.pinterest_client is None and config.make_com_pinterest_webhook:
            self.pinterest_client = PinterestClient(
                webhook_url=config.make_com_pinterest_webhook
            )
            if self.late_client is None:
                logger.info("Pinterest posting using Make.com webhook (fallback)")

        # Cache for additional Late API clients (for multi-account support)
        self._late_clients_cache = {}

    def _get_late_client(self, api_key_env: Optional[str] = None) -> Optional["LateAPIClient"]:
        """Get the appropriate Late API client for the given API key environment variable.

        Args:
            api_key_env: Environment variable name for the API key (e.g., 'LATE_API_KEY', 'LATE_API_KEY_2')

        Returns:
            LateAPIClient instance or None if not available
        """
        if not LATE_API_AVAILABLE:
            return None

        # Default to LATE_API_KEY if not specified
        if api_key_env is None:
            api_key_env = "LATE_API_KEY"

        # Return default client for primary API key
        if api_key_env == "LATE_API_KEY" and self.late_client is not None:
            return self.late_client

        # Check cache for secondary clients
        if api_key_env in self._late_clients_cache:
            return self._late_clients_cache[api_key_env]

        # Try to create a new client for the specified API key
        api_key = os.getenv(api_key_env)
        if api_key:
            try:
                client = LateAPIClient(api_key=api_key)
                self._late_clients_cache[api_key_env] = client
                logger.info(f"Created Late API client for {api_key_env}")
                return client
            except Exception as e:
                logger.warning(f"Failed to create Late API client for {api_key_env}: {e}")
                return None

        logger.warning(f"API key not found for {api_key_env}")
        return None

    def create_video_idea_pin(
        self,
        board_id: str,
        title: str,
        description: str,
        video_url: str,
        link: Optional[str] = None,
        pinterest_account_id: Optional[str] = None,
        api_key_env: Optional[str] = None
    ) -> dict:
        """Create a video-based Idea Pin.

        Uses Late API if available (handles video uploads properly), otherwise
        falls back to Make.com webhook.

        Args:
            board_id: Pinterest board ID or name
            title: Pin title (max 100 characters)
            description: Pin description
            video_url: URL of the video to pin
            link: Optional destination link
            pinterest_account_id: Late API Pinterest account ID (for multi-account support)
            api_key_env: Environment variable name for the API key (for multi-account support)

        Returns:
            Result dict with success status and pin details
        """
        # Determine which Late API client to use
        late_client = self._get_late_client(api_key_env)

        # Try Late API first (preferred for video pins)
        if late_client is not None:
            return self._create_via_late_api(
                board_id=board_id,
                title=title,
                description=description,
                video_url=video_url,
                link=link,
                account_id=pinterest_account_id,
                late_client=late_client
            )

        # Fallback to Make.com webhook
        if self.pinterest_client is not None:
            return self._create_via_webhook(
                board_id=board_id,
                title=title,
                description=description,
                video_url=video_url,
                link=link
            )

        raise ValueError("Pinterest not configured. Set LATE_API_KEY or MAKE_COM_PINTEREST_WEBHOOK.")

    def _create_via_late_api(
        self,
        board_id: str,
        title: str,
        description: str,
        video_url: str,
        link: Optional[str] = None,
        account_id: Optional[str] = None,
        late_client: Optional["LateAPIClient"] = None
    ) -> dict:
        """Create video pin via Late API."""
        logger.info(f"Creating Pinterest video pin via Late API: {title[:50]}...")
        if account_id:
            logger.info(f"Using specific Pinterest account: {account_id}")

        # Use provided client or fall back to default
        client = late_client or self.late_client
        if client is None:
            return {"success": False, "error": "No Late API client available", "method": "late_api"}

        try:
            result = client.create_pinterest_video_pin(
                video_url=video_url,
                title=title[:100],
                description=description[:500],
                link=link,
                board_id=board_id,
                publish_now=True,
                account_id=account_id
            )

            if result.success:
                logger.info(f"Pinterest video pin created successfully via Late API")
                return {
                    "success": True,
                    "id": result.post_id or "pending",
                    "url": result.platform_post_url or "",
                    "status": "created",
                    "method": "late_api"
                }
            else:
                logger.error(f"Late API failed: {result.error}")
                return {
                    "success": False,
                    "error": result.error,
                    "method": "late_api"
                }

        except Exception as e:
            logger.error(f"Failed to create Pinterest video pin via Late API: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "late_api"
            }

    def _create_via_webhook(
        self,
        board_id: str,
        title: str,
        description: str,
        video_url: str,
        link: Optional[str] = None
    ) -> dict:
        """Create video pin via Make.com webhook (fallback)."""
        logger.info(f"Creating Pinterest Idea Pin via Make.com: {title[:50]}...")

        try:
            # Create single-page video Idea Pin
            pages = [
                {
                    "media_url": video_url,
                    "description": description[:500]  # Pinterest description limit
                }
            ]

            result = self.pinterest_client.create_idea_pin(
                board_id=board_id,
                title=title[:100],  # Pinterest title limit
                pages=pages,
                link=link
            )

            logger.info(f"Pinterest Idea Pin created successfully via Make.com")
            return {
                "success": True,
                "id": result.get("id", "pending"),
                "url": result.get("url", ""),
                "status": result.get("status", "created"),
                "method": "webhook"
            }

        except Exception as e:
            logger.error(f"Failed to create Pinterest Idea Pin via Make.com: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "webhook"
            }

    def create_multi_page_idea_pin(
        self,
        board_id: str,
        title: str,
        pages: list[dict],
        link: Optional[str] = None
    ) -> dict:
        """Create a multi-page Idea Pin.

        Args:
            board_id: Pinterest board ID or name
            title: Pin title
            pages: List of dicts with 'media_url' and 'description'
            link: Optional destination link

        Returns:
            Result dict with success status and pin details
        """
        if not self.pinterest_client:
            raise ValueError("Pinterest client not configured")

        logger.info(f"Creating multi-page Pinterest Idea Pin with {len(pages)} pages")

        try:
            # Validate and format pages
            formatted_pages = []
            for page in pages[:20]:  # Pinterest max 20 pages
                formatted_pages.append({
                    "media_url": page.get("media_url", ""),
                    "description": page.get("description", "")[:500]
                })

            result = self.pinterest_client.create_idea_pin(
                board_id=board_id,
                title=title[:100],
                pages=formatted_pages,
                link=link
            )

            return {
                "success": True,
                "id": result.get("id", "pending"),
                "url": result.get("url", ""),
                "pages_count": len(formatted_pages)
            }

        except Exception as e:
            logger.error(f"Failed to create multi-page Idea Pin: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def create_image_idea_pin(
        self,
        board_id: str,
        title: str,
        description: str,
        image_urls: list[str],
        link: Optional[str] = None
    ) -> dict:
        """Create an image-based Idea Pin from multiple images.

        Args:
            board_id: Pinterest board ID
            title: Pin title
            description: Pin description (applied to first page)
            image_urls: List of image URLs
            link: Optional destination link

        Returns:
            Result dict
        """
        # Convert images to pages format
        pages = []
        for i, url in enumerate(image_urls[:20]):
            pages.append({
                "media_url": url,
                "description": description if i == 0 else ""
            })

        return self.create_multi_page_idea_pin(
            board_id=board_id,
            title=title,
            pages=pages,
            link=link
        )

    def format_description_with_hashtags(
        self,
        description: str,
        hashtags: list[str],
        max_length: int = 500
    ) -> str:
        """Format description with hashtags for Pinterest.

        Args:
            description: Base description text
            hashtags: List of hashtags
            max_length: Maximum total length

        Returns:
            Formatted description string
        """
        # Convert hashtags to Pinterest-friendly format (no # symbol needed)
        tags_text = " ".join(hashtags)

        # Calculate available space for description
        available_for_desc = max_length - len(tags_text) - 2  # 2 for newlines

        if len(description) > available_for_desc:
            description = description[:available_for_desc - 3] + "..."

        return f"{description}\n\n{tags_text}"

    def get_optimal_posting_times(self, timezone: str = "America/Los_Angeles") -> list[str]:
        """Get optimal Pinterest posting times.

        Based on Pinterest best practices, returns times in 24h format.
        """
        # Pinterest optimal posting times (PST/PDT)
        return [
            "06:00",  # Early morning
            "12:00",  # Lunch time
            "18:00",  # Early evening
            "21:00"   # Late evening (highest engagement)
        ]

    def is_configured(self) -> bool:
        """Check if Pinterest posting is configured."""
        return self.late_client is not None or self.pinterest_client is not None

    def get_posting_method(self) -> str:
        """Get the current posting method being used."""
        if self.late_client is not None:
            return "late_api"
        elif self.pinterest_client is not None:
            return "webhook"
        return "not_configured"
