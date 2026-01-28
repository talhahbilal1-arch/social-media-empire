"""Pexels API client for video search and download."""
import logging
import time
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass
import requests

from src.clients.base import BaseClient
from config.settings import settings


@dataclass
class VideoFile:
    """Represents a video file option from Pexels."""
    quality: str  # hd, sd, uhd
    width: int
    height: int
    url: str
    file_type: str  # video/mp4


@dataclass
class PexelsVideo:
    """Represents a video from Pexels search results."""
    id: int
    width: int
    height: int
    duration: int  # seconds
    url: str  # Pexels page URL
    image: str  # Thumbnail URL
    video_files: list[VideoFile]

    def get_best_file(self, min_height: int = 720) -> Optional[VideoFile]:
        """Get highest quality file meeting minimum height.

        Args:
            min_height: Minimum video height (default 720p)

        Returns:
            Best matching VideoFile or None
        """
        suitable = [f for f in self.video_files if f.height >= min_height]
        if not suitable:
            return self.video_files[0] if self.video_files else None
        return max(suitable, key=lambda f: f.height)


class PexelsClient(BaseClient):
    """Client for Pexels video search and download API.

    Handles:
    - Video search by keyword
    - Rate limit header parsing (X-Ratelimit-*)
    - Streaming downloads for large files (50-500MB typical)
    - Structured logging with duration and status

    Rate limits: 200 requests/hour, 20,000 requests/month on free tier.
    """

    BASE_URL = "https://api.pexels.com"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Pexels client.

        Args:
            api_key: Pexels API key (defaults to settings.PEXELS_API_KEY)
        """
        self.api_key = api_key or settings.PEXELS_API_KEY
        if not self.api_key:
            raise ValueError("PEXELS_API_KEY not configured")

        # Pexels uses different auth header format
        super().__init__(
            base_url=self.BASE_URL,
            api_key=None,  # Don't use Bearer format
            timeout=60.0  # Longer timeout for video operations
        )
        # Override with Pexels-style auth header
        self.client.headers["Authorization"] = self.api_key
        self.logger = logging.getLogger(self.__class__.__name__)

        # Track rate limits
        self._rate_limit: Optional[int] = None
        self._rate_remaining: Optional[int] = None
        self._rate_reset: Optional[int] = None

    def _parse_rate_limits(self, headers: dict) -> dict:
        """Parse and log Pexels rate limit headers.

        Headers:
        - X-Ratelimit-Limit: Total allowed per hour
        - X-Ratelimit-Remaining: Remaining this hour
        - X-Ratelimit-Reset: Unix timestamp when limit resets
        """
        self._rate_limit = int(headers.get("X-Ratelimit-Limit", 0))
        self._rate_remaining = int(headers.get("X-Ratelimit-Remaining", 0))
        self._rate_reset = int(headers.get("X-Ratelimit-Reset", 0))

        rate_info = {
            "limit": self._rate_limit,
            "remaining": self._rate_remaining,
            "reset": self._rate_reset
        }

        if self._rate_remaining and self._rate_remaining < 10:
            self.logger.warning(
                f"Approaching rate limit: {self._rate_remaining} requests remaining",
                extra=rate_info
            )

        return rate_info

    def search_videos(
        self,
        query: str,
        per_page: int = 15,
        orientation: str = "landscape",
        min_duration: int = 10,
        max_duration: int = 60
    ) -> list[PexelsVideo]:
        """Search for videos matching query.

        Args:
            query: Search keywords
            per_page: Results per page (max 80)
            orientation: landscape, portrait, or square
            min_duration: Minimum video duration in seconds
            max_duration: Maximum video duration in seconds

        Returns:
            List of PexelsVideo objects
        """
        start = time.time()

        response = self._request(
            "GET",
            "/videos/search",
            params={
                "query": query,
                "per_page": min(per_page, 80),
                "orientation": orientation
            }
        )

        self._parse_rate_limits(dict(response.headers))
        data = response.json()

        videos = []
        for v in data.get("videos", []):
            # Filter by duration
            duration = v.get("duration", 0)
            if duration < min_duration or duration > max_duration:
                continue

            video_files = [
                VideoFile(
                    quality=f.get("quality", ""),
                    width=f.get("width", 0),
                    height=f.get("height", 0),
                    url=f.get("link", ""),
                    file_type=f.get("file_type", "video/mp4")
                )
                for f in v.get("video_files", [])
            ]

            videos.append(PexelsVideo(
                id=v["id"],
                width=v.get("width", 0),
                height=v.get("height", 0),
                duration=duration,
                url=v.get("url", ""),
                image=v.get("image", ""),
                video_files=video_files
            ))

        duration = time.time() - start
        self.logger.info(
            f"Search '{query}' returned {len(videos)} videos",
            extra={
                "duration_ms": round(duration * 1000, 2),
                "query": query,
                "results": len(videos)
            }
        )

        return videos

    def download_video(
        self,
        video: PexelsVideo,
        destination: Path,
        min_height: int = 720,
        chunk_size: int = 8192
    ) -> Path:
        """Download video file with streaming.

        Args:
            video: PexelsVideo object to download
            destination: Path to save file (directory or full path)
            min_height: Minimum video height (default 720p)
            chunk_size: Download chunk size in bytes

        Returns:
            Path to downloaded file

        Raises:
            ValueError: If no suitable video file found
        """
        video_file = video.get_best_file(min_height)
        if not video_file:
            raise ValueError(f"No video file found for video {video.id}")

        # Determine destination path
        dest_path = Path(destination)
        if dest_path.is_dir():
            dest_path = dest_path / f"pexels_{video.id}.mp4"

        start = time.time()
        downloaded = 0

        # Use requests directly for streaming (httpx client doesn't support stream=True easily)
        with requests.get(video_file.url, stream=True, timeout=120) as response:
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))

            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Log progress every 5MB
                    if total_size and downloaded % (5 * 1024 * 1024) < chunk_size:
                        progress = (downloaded / total_size) * 100
                        self.logger.debug(
                            f"Download progress: {progress:.1f}%",
                            extra={"downloaded_mb": downloaded / (1024 * 1024)}
                        )

        duration = time.time() - start
        self.logger.info(
            f"Downloaded video {video.id} ({downloaded / (1024*1024):.1f}MB)",
            extra={
                "duration_ms": round(duration * 1000, 2),
                "video_id": video.id,
                "size_mb": round(downloaded / (1024 * 1024), 2),
                "height": video_file.height
            }
        )

        return dest_path

    @property
    def rate_limit_remaining(self) -> Optional[int]:
        """Get remaining rate limit from last request."""
        return self._rate_remaining
