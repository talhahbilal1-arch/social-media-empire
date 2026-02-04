"""
YouTube Direct Upload via YouTube Data API v3
Bypasses Late.dev for direct YouTube uploads
"""

import os
import json
import pickle
import requests
from pathlib import Path
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import tempfile

# OAuth scopes required for YouTube upload
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# Paths for credentials
CREDENTIALS_DIR = Path(__file__).parent.parent / "config"
CLIENT_SECRETS_FILE = CREDENTIALS_DIR / "youtube_client_secret.json"
TOKEN_FILE = CREDENTIALS_DIR / "youtube_token.pickle"


def get_authenticated_service():
    """
    Get authenticated YouTube API service.
    Will prompt for OAuth consent if no valid token exists.
    """
    credentials = None

    # Load existing token if available
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            credentials = pickle.load(token)

    # Refresh or get new credentials if needed
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing expired YouTube credentials...")
            credentials.refresh(Request())
        else:
            if not CLIENT_SECRETS_FILE.exists():
                raise FileNotFoundError(
                    f"YouTube client secrets not found at {CLIENT_SECRETS_FILE}\n"
                    "Please download from Google Cloud Console and save there."
                )

            print("Starting YouTube OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS_FILE),
                SCOPES
            )
            credentials = flow.run_local_server(port=8080)

        # Save credentials for future use
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(credentials, token)
        print("YouTube credentials saved!")

    return build('youtube', 'v3', credentials=credentials)


def download_video(video_url: str) -> str:
    """Download video from URL to temp file for upload"""
    print(f"Downloading video from URL...")

    response = requests.get(video_url, stream=True)
    response.raise_for_status()

    # Create temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')

    for chunk in response.iter_content(chunk_size=8192):
        temp_file.write(chunk)

    temp_file.close()
    print(f"Video downloaded to: {temp_file.name}")
    return temp_file.name


def upload_to_youtube(
    video_url: str,
    title: str,
    description: str,
    tags: list = None,
    category_id: str = "22",  # 22 = People & Blogs
    privacy_status: str = "public",
    scheduled_time: str = None,
    is_short: bool = True
) -> dict:
    """
    Upload video to YouTube directly via API.

    Args:
        video_url: URL of video to upload (will be downloaded first)
        title: Video title (max 100 chars)
        description: Video description
        tags: List of tags
        category_id: YouTube category (22=People&Blogs, 26=Howto&Style, 17=Sports)
        privacy_status: "public", "private", or "unlisted"
        scheduled_time: ISO timestamp for scheduled publish (makes video private until then)
        is_short: If True, adds #Shorts tag

    Returns:
        dict with video ID and URL
    """
    # Get authenticated service
    youtube = get_authenticated_service()

    # Download video to temp file
    video_file = download_video(video_url)

    try:
        # Prepare tags
        if tags is None:
            tags = []
        if is_short and "Shorts" not in tags:
            tags.append("Shorts")

        # Build request body
        body = {
            'snippet': {
                'title': title[:100],  # YouTube limit
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }

        # Handle scheduled publishing
        if scheduled_time:
            body['status']['privacyStatus'] = 'private'
            body['status']['publishAt'] = scheduled_time

        # Create media upload object
        media = MediaFileUpload(
            video_file,
            mimetype='video/mp4',
            resumable=True
        )

        # Execute upload
        print(f"Uploading to YouTube: {title}")
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")

        video_id = response['id']
        video_url = f"https://youtube.com/shorts/{video_id}" if is_short else f"https://youtube.com/watch?v={video_id}"

        print(f"✅ Upload complete!")
        print(f"   Video ID: {video_id}")
        print(f"   URL: {video_url}")

        return {
            'id': video_id,
            'url': video_url,
            'status': response['status']['privacyStatus']
        }

    finally:
        # Clean up temp file
        if os.path.exists(video_file):
            os.remove(video_file)


def setup_oauth():
    """
    Interactive setup for YouTube OAuth.
    Run this once to authorize the app.
    """
    print("=" * 60)
    print("YouTube OAuth Setup")
    print("=" * 60)

    if not CLIENT_SECRETS_FILE.exists():
        print(f"""
To set up YouTube API access:

1. Go to Google Cloud Console:
   https://console.cloud.google.com/

2. Create a new project or select existing one

3. Enable the YouTube Data API v3:
   APIs & Services > Library > YouTube Data API v3 > Enable

4. Create OAuth credentials:
   APIs & Services > Credentials > Create Credentials > OAuth client ID
   - Application type: Desktop app
   - Name: YouTube Shorts Automation

5. Download the JSON file and save it as:
   {CLIENT_SECRETS_FILE}

6. Run this script again to complete OAuth authorization.
""")
        return False

    print("Client secrets found! Starting OAuth flow...")
    print("A browser window will open for authorization.")
    print()

    try:
        service = get_authenticated_service()

        # Test the connection
        response = service.channels().list(
            part='snippet',
            mine=True
        ).execute()

        if response.get('items'):
            channel = response['items'][0]['snippet']
            print(f"✅ Successfully connected to YouTube!")
            print(f"   Channel: {channel['title']}")
            return True
        else:
            print("❌ No YouTube channel found for this account")
            return False

    except Exception as e:
        print(f"❌ OAuth setup failed: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Direct Upload")
    parser.add_argument("--setup", action="store_true", help="Run OAuth setup")
    parser.add_argument("--test", action="store_true", help="Test connection")
    args = parser.parse_args()

    if args.setup or args.test:
        setup_oauth()
    else:
        print("Use --setup to configure YouTube OAuth")
        print("Use --test to test the connection")
