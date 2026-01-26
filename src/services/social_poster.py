"""Social media posting service for Pinterest and YouTube.

Handles posting generated videos to:
- Pinterest via Make.com webhook
- YouTube Shorts via YouTube Data API
- Supabase storage for video hosting
"""

import os
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

from supabase import create_client, Client

from src.clients.youtube_shorts import YouTubeShortsClient, create_youtube_client
from src.clients.late_api import LateAPIClient, create_late_client


@dataclass
class PostResult:
    """Result of posting to a platform."""
    platform: str
    success: bool
    url: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoMetadata:
    """Metadata for video posting."""
    brand: str
    title: str
    description: str
    script: str
    tags: List[str] = field(default_factory=list)
    link: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)


class SocialPoster:
    """Service for posting videos to social media platforms.

    Supports:
    - Pinterest via Make.com webhook
    - YouTube Shorts via YouTube Data API
    - Supabase for video storage/hosting
    """

    # Brand to link mapping
    BRAND_LINKS = {
        'menopause-planner': 'https://www.etsy.com/shop/TheMenopausePlanner',
        'daily-deal-darling': 'https://dailydealdarling.com',
        'fitness-made-easy': 'https://fitnessmadeeasy.com',
    }

    # Brand hashtags
    BRAND_HASHTAGS = {
        'menopause-planner': ['#menopause', '#womenshealth', '#over40', '#wellness', '#healthtips'],
        'daily-deal-darling': ['#deals', '#savings', '#shopping', '#budget', '#frugalliving'],
        'fitness-made-easy': ['#fitness', '#workout', '#health', '#exercise', '#motivation'],
    }

    def __init__(
        self,
        late_client: Optional[LateAPIClient] = None,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        youtube_client: Optional[YouTubeShortsClient] = None
    ):
        """Initialize social poster with platform credentials."""
        self.late_client = late_client or create_late_client()
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')
        self.youtube_client = youtube_client or create_youtube_client()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize Supabase client
        self._supabase: Optional[Client] = None
        if self.supabase_url and self.supabase_key:
            try:
                self._supabase = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                self.logger.warning(f"Failed to initialize Supabase: {e}")

    def upload_to_supabase(self, video_path: str, brand: str) -> Optional[str]:
        """Upload video to Supabase storage and return public URL.

        Args:
            video_path: Local path to video file
            brand: Brand name for organizing storage

        Returns:
            Public URL of uploaded video, or None on failure
        """
        if not self._supabase:
            self.logger.error("Supabase client not initialized")
            return None

        video_path = Path(video_path)
        if not video_path.exists():
            self.logger.error(f"Video file not found: {video_path}")
            return None

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{brand}/{timestamp}_{video_path.name}"

        try:
            # Read video file
            with open(video_path, 'rb') as f:
                video_data = f.read()

            # Upload to Supabase storage
            bucket_name = 'videos'

            # Try to create bucket if it doesn't exist
            try:
                self._supabase.storage.create_bucket(bucket_name, {'public': True})
            except Exception:
                pass  # Bucket likely already exists

            # Upload file
            result = self._supabase.storage.from_(bucket_name).upload(
                filename,
                video_data,
                {'content-type': 'video/mp4'}
            )

            # Get public URL
            public_url = self._supabase.storage.from_(bucket_name).get_public_url(filename)

            self.logger.info(f"Uploaded to Supabase: {public_url}")
            return public_url

        except Exception as e:
            self.logger.error(f"Supabase upload failed: {e}")
            return None

    def post_to_pinterest(
        self,
        video_url: str,
        metadata: VideoMetadata
    ) -> PostResult:
        """Post video to Pinterest via Make.com webhook.

        Args:
            video_url: Public URL of the video
            metadata: Video metadata for the pin

        Returns:
            PostResult with success status and any errors
        """
        if not self.make_webhook_url:
            return PostResult(
                platform='pinterest',
                success=False,
                error='Make.com webhook URL not configured'
            )

        # Build description with hashtags
        hashtags = metadata.hashtags or self.BRAND_HASHTAGS.get(metadata.brand, [])
        description = f"{metadata.description}\n\n{' '.join(hashtags)}"

        # Get brand link
        link = metadata.link or self.BRAND_LINKS.get(metadata.brand, '')

        # Prepare webhook payload
        payload = {
            'brand': metadata.brand,
            'video_url': video_url,
            'title': metadata.title,
            'description': description,
            'link': link,
            'tags': metadata.tags,
            'timestamp': datetime.now().isoformat()
        }

        try:
            self.logger.info(f"Posting to Pinterest via Make.com: {metadata.title}")

            response = requests.post(
                self.make_webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code == 200:
                self.logger.info("Pinterest webhook triggered successfully")
                return PostResult(
                    platform='pinterest',
                    success=True,
                    metadata={'webhook_response': response.text}
                )
            else:
                error = f"Webhook returned {response.status_code}: {response.text}"
                self.logger.error(error)
                return PostResult(
                    platform='pinterest',
                    success=False,
                    error=error
                )

        except requests.exceptions.Timeout:
            return PostResult(
                platform='pinterest',
                success=False,
                error='Webhook request timed out'
            )
        except Exception as e:
            return PostResult(
                platform='pinterest',
                success=False,
                error=str(e)
            )

    def post_to_youtube(
        self,
        video_path: str,
        metadata: VideoMetadata,
        privacy_status: str = 'public'
    ) -> PostResult:
        """Post video to YouTube Shorts.

        Args:
            video_path: Local path to video file
            metadata: Video metadata
            privacy_status: 'public', 'unlisted', or 'private'

        Returns:
            PostResult with video URL on success
        """
        if not self.youtube_client:
            return PostResult(
                platform='youtube',
                success=False,
                error='YouTube client not configured (missing OAuth credentials)'
            )

        # Build description with hashtags
        hashtags = metadata.hashtags or self.BRAND_HASHTAGS.get(metadata.brand, [])
        description = f"{metadata.description}\n\n{' '.join(hashtags)}"

        # Add link to description
        link = metadata.link or self.BRAND_LINKS.get(metadata.brand, '')
        if link:
            description += f"\n\n{link}"

        try:
            result = self.youtube_client.upload_short(
                video_path=video_path,
                title=metadata.title,
                description=description,
                brand=metadata.brand,
                tags=metadata.tags,
                privacy_status=privacy_status
            )

            if result.success:
                return PostResult(
                    platform='youtube',
                    success=True,
                    url=result.video_url,
                    metadata={'video_id': result.video_id}
                )
            else:
                return PostResult(
                    platform='youtube',
                    success=False,
                    error=result.error
                )

        except Exception as e:
            return PostResult(
                platform='youtube',
                success=False,
                error=str(e)
            )

    def post_to_all_platforms(
        self,
        video_path: str,
        metadata: VideoMetadata,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, PostResult]:
        """Post video to all configured platforms.

        Args:
            video_path: Local path to video file
            metadata: Video metadata
            platforms: List of platforms to post to. Default: all available

        Returns:
            Dict mapping platform name to PostResult
        """
        results = {}
        platforms = platforms or ['pinterest', 'youtube']

        # First, upload to Supabase to get public URL
        video_url = None
        if 'pinterest' in platforms:
            video_url = self.upload_to_supabase(video_path, metadata.brand)
            if not video_url:
                results['supabase'] = PostResult(
                    platform='supabase',
                    success=False,
                    error='Failed to upload video to Supabase'
                )
                # Continue anyway - YouTube doesn't need Supabase URL
            else:
                results['supabase'] = PostResult(
                    platform='supabase',
                    success=True,
                    url=video_url
                )

        # Post to Pinterest
        if 'pinterest' in platforms:
            if video_url:
                results['pinterest'] = self.post_to_pinterest(video_url, metadata)
            else:
                results['pinterest'] = PostResult(
                    platform='pinterest',
                    success=False,
                    error='No video URL available (Supabase upload failed)'
                )

        # Post to YouTube
        if 'youtube' in platforms:
            results['youtube'] = self.post_to_youtube(video_path, metadata)

        # Log summary
        successes = sum(1 for r in results.values() if r.success)
        self.logger.info(f"Posted to {successes}/{len(results)} platforms")

        return results


def post_to_all_platforms(
    video_path: str,
    brand: str,
    title: str,
    description: str,
    script: str = '',
    tags: Optional[List[str]] = None,
    platforms: Optional[List[str]] = None
) -> Dict[str, PostResult]:
    """Convenience function to post video to all platforms.

    Args:
        video_path: Path to video file
        brand: Brand name
        title: Video title
        description: Video description
        script: Original script text
        tags: Additional tags
        platforms: Platforms to post to

    Returns:
        Dict of platform -> PostResult
    """
    metadata = VideoMetadata(
        brand=brand,
        title=title,
        description=description,
        script=script,
        tags=tags or []
    )

    poster = SocialPoster()
    return poster.post_to_all_platforms(video_path, metadata, platforms)
