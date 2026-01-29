"""Cross-platform video posting orchestrator."""

import logging
from typing import Optional
from dataclasses import dataclass, field

from utils.config import get_config
from .pinterest_idea_pins import PinterestIdeaPinCreator
from .youtube_shorts import YouTubeShortsUploader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Brand to board/channel mappings
# pinterest_account_id: Late API account ID (get from Late API dashboard after connecting accounts)
# Set to None to use the default/first Pinterest account
BRAND_PLATFORM_CONFIG = {
    "daily_deal_darling": {
        "pinterest_account_id": None,  # TODO: Set after connecting to Late API
        "pinterest_board_id": "beauty-fashion-home",
        "youtube_playlist_id": None,
        "tiktok_account": "dailydealdarling",
        "instagram_account": "dailydealdarling",
        "link_url": "https://dailydealdarling.com"
    },
    "fitnessmadeasy": {
        "pinterest_account_id": None,  # TODO: Set after connecting to Late API
        "pinterest_board_id": "fitness-tips",
        "youtube_playlist_id": None,
        "tiktok_account": "fitnessmadeasy",
        "instagram_account": "fitnessmadeasy",
        "link_url": "https://fitnessmadeasy.com"
    },
    "menopause_planner": {
        "pinterest_account_id": None,  # Uses default Pinterest account
        "pinterest_board_id": "menopause-wellness-tips",
        "youtube_playlist_id": None,
        "tiktok_account": "menopauseplanner",
        "instagram_account": "menopauseplanner",
        "link_url": "https://menopauseplanner.com"
    },
    "nurse_planner": {
        "pinterest_account_id": None,  # Uses default Pinterest account
        "pinterest_board_id": "nurse-life-tips",
        "youtube_playlist_id": None,
        "tiktok_account": "nurseplanner",
        "instagram_account": "nurseplanner",
        "link_url": "https://nurseplanner.com"
    },
    "adhd_planner": {
        "pinterest_account_id": None,  # Uses default Pinterest account
        "pinterest_board_id": "adhd-productivity-tips",
        "youtube_playlist_id": None,
        "tiktok_account": "adhdplanner",
        "instagram_account": "adhdplanner",
        "link_url": "https://adhdplanner.com"
    }
}


@dataclass
class CrossPlatformPoster:
    """Orchestrates posting videos across multiple platforms."""

    pinterest_poster: PinterestIdeaPinCreator = field(default=None)
    youtube_poster: YouTubeShortsUploader = field(default=None)

    def __post_init__(self):
        config = get_config()
        if self.pinterest_poster is None:
            self.pinterest_poster = PinterestIdeaPinCreator()
        if self.youtube_poster is None:
            self.youtube_poster = YouTubeShortsUploader()

    def post_to_all(
        self,
        video_url: str,
        title: str,
        description: str,
        hashtags: list[str],
        brand: str,
        platforms: Optional[list[str]] = None
    ) -> dict[str, dict]:
        """Post video to all specified platforms.

        Args:
            video_url: URL of the rendered video
            title: Video title
            description: Video description
            hashtags: List of hashtags
            brand: Brand identifier
            platforms: List of platforms to post to

        Returns:
            Dict mapping platform to result
        """
        config = get_config()
        if platforms is None:
            platforms = config.platforms

        brand_config = BRAND_PLATFORM_CONFIG.get(
            brand, BRAND_PLATFORM_CONFIG["daily_deal_darling"]
        )

        results = {}

        for platform in platforms:
            try:
                if platform == "youtube_shorts":
                    result = self._post_to_youtube(
                        video_url, title, description, hashtags, brand_config
                    )
                elif platform == "pinterest":
                    result = self._post_to_pinterest(
                        video_url, title, description, hashtags, brand_config
                    )
                elif platform == "tiktok":
                    result = self._post_to_tiktok(
                        video_url, title, description, hashtags, brand_config
                    )
                elif platform == "instagram_reels":
                    result = self._post_to_instagram(
                        video_url, title, description, hashtags, brand_config
                    )
                else:
                    result = {"success": False, "error": f"Unknown platform: {platform}"}

                results[platform] = result
                logger.info(f"Posted to {platform}: {'success' if result.get('success') else 'failed'}")

            except Exception as e:
                logger.error(f"Error posting to {platform}: {e}")
                results[platform] = {"success": False, "error": str(e)}

        return results

    def _post_to_youtube(
        self,
        video_url: str,
        title: str,
        description: str,
        hashtags: list[str],
        brand_config: dict
    ) -> dict:
        """Post to YouTube Shorts."""
        try:
            # Check if YouTube is configured
            if not self.youtube_poster.is_configured():
                return {"success": False, "error": "YouTube not configured. Set YouTube OAuth credentials."}

            result = self.youtube_poster.upload_short(
                video_url=video_url,
                title=title[:100],  # YouTube title limit
                description=f"{description}\n\n{' '.join(hashtags)}",
                tags=hashtags
            )

            # Check if the YouTube upload actually succeeded
            if not result.get("success", False):
                return {
                    "success": False,
                    "error": result.get("error", "YouTube upload failed with unknown error")
                }

            return {
                "success": True,
                "platform_id": result.get("id"),
                "url": f"https://youtube.com/shorts/{result.get('id')}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _post_to_pinterest(
        self,
        video_url: str,
        title: str,
        description: str,
        hashtags: list[str],
        brand_config: dict
    ) -> dict:
        """Post to Pinterest as Idea Pin."""
        try:
            # Check if Pinterest is configured
            if not self.pinterest_poster.is_configured():
                logger.error("Pinterest posting failed: No Pinterest posting method configured")
                return {"success": False, "error": "Pinterest not configured. Set LATE_API_KEY (preferred) or MAKE_COM_PINTEREST_WEBHOOK."}

            board_id = brand_config.get("pinterest_board_id", "default")
            account_id = brand_config.get("pinterest_account_id")  # Optional: specific Late API account
            link_url = brand_config.get("link_url")  # Brand-specific destination link
            logger.info(f"Posting to Pinterest board: {board_id}" + (f" (account: {account_id})" if account_id else ""))

            result = self.pinterest_poster.create_video_idea_pin(
                board_id=board_id,
                title=title[:100],
                description=f"{description}\n\n{' '.join(hashtags)}",
                video_url=video_url,
                link=link_url,
                pinterest_account_id=account_id
            )

            # Check if the Pinterest posting actually succeeded
            if not result.get("success", False):
                error_msg = result.get("error", "Pinterest posting failed with unknown error")
                logger.error(f"Pinterest posting failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }

            logger.info(f"Pinterest posting succeeded: {result.get('id', 'pending')}")
            return {
                "success": True,
                "platform_id": result.get("id"),
                "url": result.get("url", "")
            }
        except Exception as e:
            logger.error(f"Pinterest posting exception: {e}")
            return {"success": False, "error": str(e)}

    def _post_to_tiktok(
        self,
        video_url: str,
        title: str,
        description: str,
        hashtags: list[str],
        brand_config: dict
    ) -> dict:
        """Post to TikTok via Make.com webhook.

        TikTok posting is handled through Make.com automation
        due to API restrictions.
        """
        import requests
        config = get_config()

        # Use a separate Make.com webhook for TikTok if configured
        webhook_url = config.make_com_pinterest_webhook.replace("pinterest", "tiktok")

        if not webhook_url or "pinterest" in webhook_url:
            return {"success": False, "error": "TikTok webhook not configured"}

        try:
            payload = {
                "platform": "tiktok",
                "video_url": video_url,
                "caption": f"{title}\n\n{' '.join(hashtags)}",
                "account": brand_config.get("tiktok_account")
            }
            response = requests.post(webhook_url, json=payload, timeout=30)
            response.raise_for_status()

            return {
                "success": True,
                "platform_id": "pending",  # Make.com handles actual posting
                "url": ""
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _post_to_instagram(
        self,
        video_url: str,
        title: str,
        description: str,
        hashtags: list[str],
        brand_config: dict
    ) -> dict:
        """Post to Instagram Reels via Make.com webhook.

        Instagram posting is handled through Make.com automation
        due to API complexity.
        """
        import requests
        config = get_config()

        # Use a separate Make.com webhook for Instagram if configured
        webhook_url = config.make_com_pinterest_webhook.replace("pinterest", "instagram")

        if not webhook_url or "pinterest" in webhook_url:
            return {"success": False, "error": "Instagram webhook not configured"}

        try:
            payload = {
                "platform": "instagram",
                "video_url": video_url,
                "caption": f"{title}\n\n{description}\n\n{' '.join(hashtags)}",
                "account": brand_config.get("instagram_account")
            }
            response = requests.post(webhook_url, json=payload, timeout=30)
            response.raise_for_status()

            return {
                "success": True,
                "platform_id": "pending",
                "url": ""
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def post_single_platform(
        self,
        platform: str,
        video_url: str,
        title: str,
        description: str,
        hashtags: list[str],
        brand: str
    ) -> dict:
        """Post to a single platform."""
        return self.post_to_all(
            video_url=video_url,
            title=title,
            description=description,
            hashtags=hashtags,
            brand=brand,
            platforms=[platform]
        ).get(platform, {"success": False, "error": "Platform not found"})

    def get_platform_status(self) -> dict[str, bool]:
        """Check which platforms are configured and available."""
        import os
        config = get_config()

        # Pinterest can use Late API (preferred) or Make.com webhook
        pinterest_configured = bool(os.getenv('LATE_API_KEY')) or bool(config.make_com_pinterest_webhook)

        return {
            "youtube_shorts": bool(config.youtube_refresh_token),
            "pinterest": pinterest_configured,
            "tiktok": bool(config.make_com_pinterest_webhook),  # Shares webhook
            "instagram_reels": bool(config.make_com_pinterest_webhook)  # Shares webhook
        }
