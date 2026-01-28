"""Video fetcher service with Pexels integration and caching."""
import logging
from pathlib import Path
from typing import Optional, List

from src.clients.pexels import PexelsClient, PexelsVideo
from src.utils.cache import FileCache


class VideoFetcher:
    """Fetch stock videos from Pexels with caching.

    Downloads landscape videos suitable for 9:16 vertical cropping.
    Caches by search term hash to prevent redundant downloads.

    Cache strategy:
    - Metadata cache: JSON with video ID, path, search terms
    - Video files: Stored in cache/videos/ directory
    - Cache key: hash of sorted search terms (order-independent)
    """

    # Default search parameters
    DEFAULT_MIN_DURATION = 10  # seconds
    DEFAULT_MAX_DURATION = 60  # seconds
    DEFAULT_MIN_HEIGHT = 720   # pixels (720p minimum)

    def __init__(
        self,
        pexels_client: PexelsClient = None,
        cache_dir: Path = None
    ):
        """Initialize VideoFetcher.

        Args:
            pexels_client: PexelsClient instance (creates new if None)
            cache_dir: Directory for video cache (defaults to cache/videos)
        """
        self.client = pexels_client or PexelsClient()
        self.cache_dir = cache_dir or Path("cache/videos")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_cache = FileCache("video_metadata")
        self.logger = logging.getLogger(self.__class__.__name__)

    def _cache_key(self, search_terms: List[str]) -> str:
        """Generate cache key from search terms (order-independent)."""
        # Sort terms to make cache key order-independent
        sorted_terms = sorted([t.lower().strip() for t in search_terms])
        return "_".join(sorted_terms)

    def _get_cached(self, cache_key: str) -> Optional[Path]:
        """Get cached video path if exists and file is valid."""
        metadata = self.metadata_cache.get(cache_key)
        if not metadata:
            return None

        video_path = Path(metadata.get("path", ""))
        if video_path.exists() and video_path.stat().st_size > 0:
            self.logger.debug(
                f"Cache HIT for search terms",
                extra={"cache_key": cache_key, "path": str(video_path)}
            )
            return video_path

        # File doesn't exist or is empty - invalidate cache
        self.metadata_cache.delete(cache_key)
        self.logger.info(
            f"Cache INVALID (file missing)",
            extra={"cache_key": cache_key, "expected_path": str(video_path)}
        )
        return None

    def fetch(
        self,
        search_terms: List[str],
        target_duration: float = 30.0,
        min_height: int = None
    ) -> Path:
        """Fetch video matching search terms with appropriate duration.

        Args:
            search_terms: List of Pexels search keywords (tries each in order)
            target_duration: Target video duration in seconds
            min_height: Minimum video height (defaults to DEFAULT_MIN_HEIGHT)

        Returns:
            Path to downloaded video file

        Raises:
            ValueError: If no suitable video found for any search term

        Strategy:
            1. Check cache first
            2. Search with duration buffer (0.8x to 1.5x target)
            3. Try each search term until success
            4. Download best quality video
            5. Cache metadata and return path
        """
        if not search_terms:
            raise ValueError("At least one search term required")

        cache_key = self._cache_key(search_terms)
        min_height = min_height or self.DEFAULT_MIN_HEIGHT

        # Check cache
        cached_path = self._get_cached(cache_key)
        if cached_path:
            return cached_path

        self.logger.info(
            f"Cache MISS, searching Pexels",
            extra={"search_terms": search_terms, "target_duration": target_duration}
        )

        # Calculate duration bounds (allow some flexibility)
        min_duration = max(self.DEFAULT_MIN_DURATION, int(target_duration * 0.8))
        max_duration = min(self.DEFAULT_MAX_DURATION, int(target_duration * 1.5))

        # Try each search term
        last_error = None
        for term in search_terms:
            try:
                video = self._search_and_select(term, min_duration, max_duration)
                if video:
                    path = self._download_and_cache(video, cache_key, search_terms)
                    return path
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"Search term '{term}' failed: {e}",
                    extra={"term": term}
                )
                continue

        # All terms failed
        raise ValueError(
            f"No suitable video found for terms: {search_terms}. Last error: {last_error}"
        )

    def _search_and_select(
        self,
        term: str,
        min_duration: int,
        max_duration: int
    ) -> Optional[PexelsVideo]:
        """Search for videos and select best match.

        Prefers landscape orientation for vertical cropping.
        """
        videos = self.client.search_videos(
            query=term,
            per_page=10,
            orientation="landscape",  # Better for 9:16 cropping
            min_duration=min_duration,
            max_duration=max_duration
        )

        if not videos:
            return None

        # Select first video with good quality file
        for video in videos:
            best_file = video.get_best_file(min_height=self.DEFAULT_MIN_HEIGHT)
            if best_file:
                self.logger.debug(
                    f"Selected video {video.id}",
                    extra={
                        "duration": video.duration,
                        "resolution": f"{best_file.width}x{best_file.height}"
                    }
                )
                return video

        return None

    def _download_and_cache(
        self,
        video: PexelsVideo,
        cache_key: str,
        search_terms: List[str]
    ) -> Path:
        """Download video and cache metadata."""
        # Download to cache directory
        video_path = self.client.download_video(video, self.cache_dir)

        # Store metadata for cache lookup
        self.metadata_cache.set(cache_key, {
            "path": str(video_path),
            "video_id": video.id,
            "duration": video.duration,
            "search_terms": search_terms,
            "pexels_url": video.url
        })

        self.logger.info(
            f"Downloaded and cached video",
            extra={
                "video_id": video.id,
                "path": str(video_path),
                "duration": video.duration
            }
        )

        return video_path

    def clear_cache(self) -> int:
        """Clear all cached videos and metadata.

        Returns:
            Number of files deleted
        """
        # Clear metadata
        metadata_count = self.metadata_cache.clear()

        # Clear video files
        video_count = 0
        for video_file in self.cache_dir.glob("*.mp4"):
            video_file.unlink()
            video_count += 1

        self.logger.info(
            f"Cleared cache",
            extra={"metadata_entries": metadata_count, "video_files": video_count}
        )

        return metadata_count + video_count
