"""YouTube Shorts upload functionality."""
from __future__ import annotations

import os
import logging
import tempfile
from typing import Optional
from dataclasses import dataclass
import requests

from utils.config import get_config
from utils.api_clients import YouTubeClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class YouTubeShortsUploader:
    """Uploads videos to YouTube as Shorts."""

    youtube_client: YouTubeClient = None

    def __post_init__(self):
        config = get_config()
        if self.youtube_client is None and config.youtube_refresh_token:
            self.youtube_client = YouTubeClient(
                client_id=config.youtube_client_id,
                client_secret=config.youtube_client_secret,
                refresh_token=config.youtube_refresh_token
            )

    def upload_short(
        self,
        video_url: str,
        title: str,
        description: str,
        tags: list[str],
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "public",
        notify_subscribers: bool = True
    ) -> dict:
        """Upload a video as a YouTube Short.

        Args:
            video_url: URL of video to download and upload
            title: Video title (max 100 chars for Shorts)
            description: Video description
            tags: List of tags/keywords
            category_id: YouTube category ID
            privacy_status: 'public', 'private', or 'unlisted'
            notify_subscribers: Whether to notify subscribers

        Returns:
            Result dict with video ID and URL
        """
        if not self.youtube_client:
            raise ValueError("YouTube client not configured. Set YouTube OAuth credentials.")

        logger.info(f"Uploading YouTube Short: {title[:50]}...")

        try:
            # Download video to temporary file
            video_path = self._download_video(video_url)

            try:
                # Format for Shorts
                short_title = self._format_shorts_title(title)
                short_description = self._format_shorts_description(description, tags)

                # Upload to YouTube
                result = self.youtube_client.upload_video(
                    video_path=video_path,
                    title=short_title,
                    description=short_description,
                    tags=tags[:500] if tags else [],  # YouTube tag limit
                    category_id=category_id,
                    privacy_status=privacy_status
                )

                video_id = result.get("id")
                logger.info(f"YouTube Short uploaded: {video_id}")

                return {
                    "success": True,
                    "id": video_id,
                    "url": f"https://youtube.com/shorts/{video_id}",
                    "title": short_title
                }

            finally:
                # Clean up temp file
                if os.path.exists(video_path):
                    os.remove(video_path)

        except Exception as e:
            logger.error(f"Failed to upload YouTube Short: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _download_video(self, video_url: str) -> str:
        """Download video from URL to temporary file."""
        logger.info(f"Downloading video from {video_url[:50]}...")

        response = requests.get(video_url, stream=True, timeout=60)
        response.raise_for_status()

        # Create temp file
        fd, temp_path = tempfile.mkstemp(suffix=".mp4")
        try:
            with os.fdopen(fd, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except Exception:
            os.close(fd)
            raise

        logger.info(f"Video downloaded to {temp_path}")
        return temp_path

    def _format_shorts_title(self, title: str, max_length: int = 100) -> str:
        """Format title for YouTube Shorts.

        Shorts titles should be catchy and include #Shorts tag.
        """
        # Remove any existing #Shorts tag
        title = title.replace("#Shorts", "").replace("#shorts", "").strip()

        # Truncate if needed (leave room for #Shorts)
        if len(title) > max_length - 8:  # 8 chars for " #Shorts"
            title = title[:max_length - 11] + "..."

        return f"{title} #Shorts"

    def _format_shorts_description(
        self,
        description: str,
        tags: list[str],
        max_length: int = 5000
    ) -> str:
        """Format description for YouTube Shorts."""
        # Add Shorts-specific text
        shorts_intro = "Watch till the end! 👀\n\n"

        # Add hashtags at the end
        hashtags = " ".join([t if t.startswith("#") else f"#{t}" for t in tags[:10]])

        # Add subscribe CTA
        subscribe_cta = "\n\n📌 Don't forget to LIKE, COMMENT, and SUBSCRIBE for more content!"

        # Combine
        full_description = f"{shorts_intro}{description}{subscribe_cta}\n\n{hashtags}"

        # Truncate if needed
        if len(full_description) > max_length:
            full_description = full_description[:max_length - 3] + "..."

        return full_description

    def upload_from_file(
        self,
        file_path: str,
        title: str,
        description: str,
        tags: list[str],
        **kwargs
    ) -> dict:
        """Upload a local video file as YouTube Short."""
        if not self.youtube_client:
            raise ValueError("YouTube client not configured")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Video file not found: {file_path}")

        logger.info(f"Uploading local file as YouTube Short: {file_path}")

        try:
            short_title = self._format_shorts_title(title)
            short_description = self._format_shorts_description(description, tags)

            result = self.youtube_client.upload_video(
                video_path=file_path,
                title=short_title,
                description=short_description,
                tags=tags,
                **kwargs
            )

            video_id = result.get("id")
            return {
                "success": True,
                "id": video_id,
                "url": f"https://youtube.com/shorts/{video_id}"
            }

        except Exception as e:
            logger.error(f"Failed to upload: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_upload_status(self, video_id: str) -> dict:
        """Check the processing status of an uploaded video."""
        if not self.youtube_client:
            raise ValueError("YouTube client not configured")

        try:
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                headers=self.youtube_client.headers,
                params={
                    "part": "status,processingDetails",
                    "id": video_id
                }
            )
            response.raise_for_status()
            data = response.json()

            if data.get("items"):
                item = data["items"][0]
                return {
                    "success": True,
                    "status": item.get("status", {}),
                    "processing": item.get("processingDetails", {})
                }
            return {
                "success": False,
                "error": "Video not found"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def is_configured(self) -> bool:
        """Check if YouTube upload is configured."""
        return self.youtube_client is not None

    def get_optimal_posting_times(self, timezone: str = "America/Los_Angeles") -> list[str]:
        """Get optimal YouTube Shorts posting times.

        Based on YouTube analytics best practices.
        """
        return [
            "09:00",  # Morning viewers
            "12:00",  # Lunch break
            "15:00",  # Afternoon
            "19:00"   # Prime time
        ]
