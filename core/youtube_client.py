"""
YouTube Client with OAuth 2.0 for Shorts Uploading
===================================================
Handles YouTube Shorts uploads using OAuth 2.0 authentication.

Required GitHub Secrets:
- YOUTUBE_CLIENT_ID
- YOUTUBE_CLIENT_SECRET
- YOUTUBE_REFRESH_TOKEN

Setup:
1. Create project in Google Cloud Console
2. Enable YouTube Data API v3
3. Create OAuth 2.0 credentials (Desktop app)
4. Run get_refresh_token() once to obtain refresh token
5. Add credentials to GitHub Secrets
"""
import os
import json
import requests
from typing import Optional, Dict, Tuple
from datetime import datetime


class YouTubeClient:
    """YouTube API client with OAuth 2.0 for video uploads."""

    OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
    UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
    VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

    # YouTube Shorts requirements
    MAX_DURATION_SECONDS = 60
    MAX_FILE_SIZE_MB = 256

    def __init__(self):
        self.client_id = os.environ.get('YOUTUBE_CLIENT_ID')
        self.client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET')
        self.refresh_token = os.environ.get('YOUTUBE_REFRESH_TOKEN')
        self.access_token = None

        # Check if OAuth is configured
        self.oauth_configured = all([
            self.client_id,
            self.client_secret,
            self.refresh_token
        ])

        if not self.oauth_configured:
            missing = []
            if not self.client_id:
                missing.append('YOUTUBE_CLIENT_ID')
            if not self.client_secret:
                missing.append('YOUTUBE_CLIENT_SECRET')
            if not self.refresh_token:
                missing.append('YOUTUBE_REFRESH_TOKEN')
            print(f"YouTube OAuth not configured. Missing: {', '.join(missing)}")

    def _get_access_token(self) -> Optional[str]:
        """Exchange refresh token for access token."""
        if not self.oauth_configured:
            return None

        if self.access_token:
            return self.access_token

        try:
            response = requests.post(
                self.OAUTH_TOKEN_URL,
                data={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'refresh_token': self.refresh_token,
                    'grant_type': 'refresh_token'
                },
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get('access_token')
            return self.access_token

        except Exception as e:
            print(f"Failed to get access token: {e}")
            return None

    def upload_short(
        self,
        video_url: str,
        title: str,
        description: str,
        tags: list = None,
        category_id: str = "22"  # People & Blogs
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload a video as a YouTube Short.

        Args:
            video_url: URL of the video file to upload
            title: Video title (will add #Shorts automatically)
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (default: People & Blogs)

        Returns:
            Tuple of (success, video_url, video_id)
        """
        if not self.oauth_configured:
            print("YouTube OAuth not configured - cannot upload")
            return False, None, None

        access_token = self._get_access_token()
        if not access_token:
            return False, None, None

        try:
            # Download video from URL
            print(f"Downloading video from {video_url[:50]}...")
            video_response = requests.get(video_url, timeout=120)
            video_response.raise_for_status()
            video_data = video_response.content

            # Check file size
            file_size_mb = len(video_data) / (1024 * 1024)
            if file_size_mb > self.MAX_FILE_SIZE_MB:
                print(f"Video too large: {file_size_mb:.1f}MB (max {self.MAX_FILE_SIZE_MB}MB)")
                return False, None, None

            # Ensure title includes #Shorts for algorithm
            if '#Shorts' not in title and '#shorts' not in title:
                title = f"{title} #Shorts"

            # Prepare metadata
            metadata = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': description[:5000],  # Description limit
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }

            # Step 1: Initialize resumable upload
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'X-Upload-Content-Type': 'video/mp4',
                'X-Upload-Content-Length': str(len(video_data))
            }

            init_response = requests.post(
                f"{self.UPLOAD_URL}?uploadType=resumable&part=snippet,status",
                headers=headers,
                json=metadata,
                timeout=30
            )
            init_response.raise_for_status()

            # Get upload URL from response headers
            upload_url = init_response.headers.get('Location')
            if not upload_url:
                print("Failed to get upload URL")
                return False, None, None

            # Step 2: Upload video data
            print(f"Uploading video ({file_size_mb:.1f}MB)...")
            upload_headers = {
                'Content-Type': 'video/mp4',
                'Content-Length': str(len(video_data))
            }

            upload_response = requests.put(
                upload_url,
                headers=upload_headers,
                data=video_data,
                timeout=300  # 5 minutes for upload
            )
            upload_response.raise_for_status()

            # Parse response
            result = upload_response.json()
            video_id = result.get('id')

            if video_id:
                video_url = f"https://youtube.com/shorts/{video_id}"
                print(f"Upload successful: {video_url}")
                return True, video_url, video_id
            else:
                print(f"Upload response missing video ID: {result}")
                return False, None, None

        except requests.exceptions.RequestException as e:
            print(f"Upload failed: {e}")
            return False, None, None
        except Exception as e:
            print(f"Unexpected error during upload: {e}")
            return False, None, None

    def get_video_status(self, video_id: str) -> Optional[Dict]:
        """Check the status of an uploaded video."""
        if not self.oauth_configured:
            return None

        access_token = self._get_access_token()
        if not access_token:
            return None

        try:
            response = requests.get(
                self.VIDEOS_URL,
                params={
                    'part': 'status,snippet,statistics',
                    'id': video_id
                },
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            items = data.get('items', [])
            return items[0] if items else None

        except Exception as e:
            print(f"Failed to get video status: {e}")
            return None


def get_refresh_token():
    """
    Interactive script to obtain a refresh token.
    Run this ONCE locally to get the refresh token for GitHub Secrets.

    Prerequisites:
    1. Create OAuth 2.0 credentials in Google Cloud Console
    2. Download client_secret.json to this directory
    3. Run: python youtube_client.py
    """
    import webbrowser
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs

    # Load client secrets
    try:
        with open('client_secret.json', 'r') as f:
            secrets = json.load(f)
            client_config = secrets.get('installed', secrets.get('web', {}))
            client_id = client_config['client_id']
            client_secret = client_config['client_secret']
    except FileNotFoundError:
        print("Error: client_secret.json not found!")
        print("Download it from Google Cloud Console > APIs & Services > Credentials")
        return

    # OAuth parameters
    redirect_uri = 'http://localhost:8080'
    scope = 'https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube'

    # Build auth URL
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={scope}&"
        f"access_type=offline&"
        f"prompt=consent"
    )

    print("Opening browser for authorization...")
    print(f"If browser doesn't open, visit: {auth_url}")
    webbrowser.open(auth_url)

    # Simple handler to capture the auth code
    auth_code = None

    class AuthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal auth_code
            query = parse_qs(urlparse(self.path).query)
            auth_code = query.get('code', [None])[0]

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            if auth_code:
                self.wfile.write(b"<h1>Authorization successful!</h1><p>You can close this window.</p>")
            else:
                self.wfile.write(b"<h1>Authorization failed</h1>")

        def log_message(self, format, *args):
            pass  # Suppress logging

    # Start local server to receive callback
    server = HTTPServer(('localhost', 8080), AuthHandler)
    print("Waiting for authorization...")
    server.handle_request()

    if not auth_code:
        print("Failed to get authorization code")
        return

    # Exchange code for tokens
    print("Exchanging code for tokens...")
    response = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
    )

    if response.status_code != 200:
        print(f"Token exchange failed: {response.text}")
        return

    tokens = response.json()
    refresh_token = tokens.get('refresh_token')

    if refresh_token:
        print("\n" + "="*50)
        print("SUCCESS! Add these to GitHub Secrets:")
        print("="*50)
        print(f"\nYOUTUBE_CLIENT_ID={client_id}")
        print(f"\nYOUTUBE_CLIENT_SECRET={client_secret}")
        print(f"\nYOUTUBE_REFRESH_TOKEN={refresh_token}")
        print("\n" + "="*50)
    else:
        print("No refresh token in response. Make sure 'access_type=offline' is set.")
        print(f"Response: {tokens}")


if __name__ == '__main__':
    # Run the refresh token flow
    get_refresh_token()
