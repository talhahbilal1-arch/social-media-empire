"""YouTube Shorts upload client using OAuth2.

Handles uploading vertical videos as YouTube Shorts.
YouTube auto-detects Shorts based on vertical format and <60s duration.
"""

import os
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


@dataclass
class YouTubeUploadResult:
    """Result of a YouTube upload."""
    success: bool
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    error: Optional[str] = None


class YouTubeShortsClient:
    """Client for uploading YouTube Shorts.

    Uses OAuth2 for authentication since API key doesn't support uploads.
    Requires:
    - YOUTUBE_CLIENT_ID
    - YOUTUBE_CLIENT_SECRET
    - YOUTUBE_REFRESH_TOKEN
    """

    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    # Brand to channel mapping (can be same channel or different)
    BRAND_CHANNELS = {
        'menopause-planner': {
            'channel_name': 'TheMenopausePlanner',
            'default_tags': ['menopause', 'womens health', 'wellness', 'health tips', 'over 40'],
            'category_id': '26',  # Howto & Style
        },
        'daily-deal-darling': {
            'channel_name': 'DailyDealDarling',
            'default_tags': ['deals', 'savings', 'shopping', 'budget', 'discounts'],
            'category_id': '26',  # Howto & Style
        },
        'fitness-made-easy': {
            'channel_name': 'FitnessMadeEasy',
            'default_tags': ['fitness', 'workout', 'exercise', 'health', 'motivation'],
            'category_id': '17',  # Sports
        },
    }

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None
    ):
        """Initialize YouTube client with OAuth credentials."""
        self.client_id = client_id or os.getenv('YOUTUBE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('YOUTUBE_CLIENT_SECRET')
        self.refresh_token = refresh_token or os.getenv('YOUTUBE_REFRESH_TOKEN')
        self.logger = logging.getLogger(self.__class__.__name__)
        self._service = None

    def _get_credentials(self) -> Optional[Credentials]:
        """Get OAuth2 credentials from refresh token."""
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            self.logger.error("Missing YouTube OAuth credentials")
            return None

        try:
            credentials = Credentials(
                token=None,
                refresh_token=self.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.SCOPES
            )

            # Refresh the token
            credentials.refresh(Request())
            return credentials

        except Exception as e:
            self.logger.error(f"Failed to get credentials: {e}")
            return None

    def _get_service(self):
        """Get or create YouTube API service."""
        if self._service is None:
            credentials = self._get_credentials()
            if credentials is None:
                raise RuntimeError("Failed to obtain YouTube credentials")

            self._service = build('youtube', 'v3', credentials=credentials)

        return self._service

    def upload_short(
        self,
        video_path: str,
        title: str,
        description: str,
        brand: str,
        tags: Optional[list] = None,
        privacy_status: str = 'public',
        made_for_kids: bool = False
    ) -> YouTubeUploadResult:
        """Upload a video as a YouTube Short.

        Args:
            video_path: Path to the video file
            title: Video title (will add #Shorts if not present)
            description: Video description
            brand: Brand name for channel/tags lookup
            tags: Additional tags (brand defaults added automatically)
            privacy_status: 'public', 'unlisted', or 'private'
            made_for_kids: Whether content is made for kids

        Returns:
            YouTubeUploadResult with video ID and URL on success
        """
        video_path = Path(video_path)
        if not video_path.exists():
            return YouTubeUploadResult(
                success=False,
                error=f"Video file not found: {video_path}"
            )

        # Get brand config
        brand_config = self.BRAND_CHANNELS.get(brand, {})
        default_tags = brand_config.get('default_tags', [])
        category_id = brand_config.get('category_id', '22')  # Default: People & Blogs

        # Combine tags
        all_tags = list(set((tags or []) + default_tags + ['Shorts']))

        # Ensure #Shorts in title for better discoverability
        if '#Shorts' not in title and '#shorts' not in title.lower():
            title = f"{title} #Shorts"

        # Truncate title if too long (100 char limit)
        if len(title) > 100:
            title = title[:97] + "..."

        # Build video metadata
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': all_tags,
                'categoryId': category_id,
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': made_for_kids,
            }
        }

        try:
            service = self._get_service()

            # Create media upload
            media = MediaFileUpload(
                str(video_path),
                mimetype='video/mp4',
                resumable=True,
                chunksize=1024 * 1024  # 1MB chunks
            )

            # Execute upload
            self.logger.info(f"Uploading video: {title}")
            request = service.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    self.logger.info(f"Upload progress: {int(status.progress() * 100)}%")

            video_id = response['id']
            video_url = f"https://youtube.com/shorts/{video_id}"

            self.logger.info(f"Upload complete: {video_url}")

            return YouTubeUploadResult(
                success=True,
                video_id=video_id,
                video_url=video_url
            )

        except HttpError as e:
            error_msg = f"YouTube API error: {e.reason}"
            self.logger.error(error_msg)
            return YouTubeUploadResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Upload failed: {str(e)}"
            self.logger.error(error_msg)
            return YouTubeUploadResult(success=False, error=error_msg)

    def check_quota(self) -> Dict[str, Any]:
        """Check remaining API quota (approximate).

        Note: YouTube API doesn't provide direct quota checking.
        This attempts a lightweight API call to verify connectivity.
        """
        try:
            service = self._get_service()
            # Light API call to check connectivity
            response = service.channels().list(
                part='snippet',
                mine=True
            ).execute()

            return {
                'connected': True,
                'channel_title': response['items'][0]['snippet']['title'] if response.get('items') else 'Unknown',
            }

        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }


def create_youtube_client() -> Optional[YouTubeShortsClient]:
    """Factory function to create YouTube client if credentials exist."""
    client_id = os.getenv('YOUTUBE_CLIENT_ID')
    client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
    refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')

    if not all([client_id, client_secret, refresh_token]):
        logging.warning("YouTube credentials not configured. YouTube uploads disabled.")
        return None

    return YouTubeShortsClient(client_id, client_secret, refresh_token)
