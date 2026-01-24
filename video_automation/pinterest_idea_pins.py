"""Pinterest Idea Pin creation via Make.com webhook."""

import logging
from typing import Optional
from dataclasses import dataclass

from utils.config import get_config
from utils.api_clients import PinterestClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PinterestIdeaPinCreator:
    """Creates Pinterest Idea Pins via Make.com webhook integration."""

    pinterest_client: PinterestClient = None

    def __post_init__(self):
        config = get_config()
        if self.pinterest_client is None and config.make_com_pinterest_webhook:
            self.pinterest_client = PinterestClient(
                webhook_url=config.make_com_pinterest_webhook
            )

    def create_video_idea_pin(
        self,
        board_id: str,
        title: str,
        description: str,
        video_url: str,
        link: Optional[str] = None
    ) -> dict:
        """Create a video-based Idea Pin.

        Args:
            board_id: Pinterest board ID or name
            title: Pin title (max 100 characters)
            description: Pin description
            video_url: URL of the video to pin
            link: Optional destination link

        Returns:
            Result dict with success status and pin details
        """
        if not self.pinterest_client:
            raise ValueError("Pinterest client not configured. Set MAKE_COM_PINTEREST_WEBHOOK.")

        logger.info(f"Creating Pinterest Idea Pin: {title[:50]}...")

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

            logger.info(f"Pinterest Idea Pin created successfully")
            return {
                "success": True,
                "id": result.get("id", "pending"),
                "url": result.get("url", ""),
                "status": result.get("status", "created")
            }

        except Exception as e:
            logger.error(f"Failed to create Pinterest Idea Pin: {e}")
            return {
                "success": False,
                "error": str(e)
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
        return self.pinterest_client is not None
