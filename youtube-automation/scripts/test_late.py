"""
Late.dev API Test Script
Tests YouTube video upload and scheduling
"""

import os
import requests
from datetime import datetime, timedelta

# Configuration
API_KEY = os.getenv("LATE_API_KEY")
YOUTUBE_ACCOUNT_ID = os.getenv("LATE_YOUTUBE_ACCOUNT_ID")
BASE_URL = "https://api.getlate.dev/v1"

def get_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

def list_accounts():
    """List connected social accounts"""
    url = f"{BASE_URL}/accounts"
    response = requests.get(url, headers=get_headers())

    if response.status_code == 200:
        data = response.json()
        accounts = data.get("accounts", data) if isinstance(data, dict) else data
        print("Connected accounts:")
        if isinstance(accounts, list):
            for acc in accounts:
                print(f"  - {acc.get('platform', 'unknown')}: {acc.get('id')} ({acc.get('name', 'unnamed')})")
        else:
            print(f"  Response: {data}")
        return accounts
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_account(account_id: str = None):
    """Get details for a specific account"""
    aid = account_id or YOUTUBE_ACCOUNT_ID
    if not aid:
        print("No account ID provided")
        return None

    url = f"{BASE_URL}/accounts/{aid}"
    response = requests.get(url, headers=get_headers())

    if response.status_code == 200:
        account = response.json()
        print(f"Account Details:")
        print(f"  ID: {account.get('id')}")
        print(f"  Name: {account.get('name')}")
        print(f"  Platform: {account.get('platform')}")
        return account
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def upload_video(
    video_url: str,
    title: str,
    description: str,
    scheduled_time: str = None,  # ISO format
    privacy: str = "public",
    hashtags: list = None
):
    """Upload and optionally schedule a video to YouTube"""
    if not YOUTUBE_ACCOUNT_ID:
        print("ERROR: LATE_YOUTUBE_ACCOUNT_ID not set!")
        return None

    url = f"{BASE_URL}/posts"

    # Build description with hashtags
    full_description = description
    if hashtags:
        full_description += "\n\n" + " ".join([f"#{tag}" for tag in hashtags])

    payload = {
        "platforms": [
            {
                "platform": "youtube",
                "accountId": YOUTUBE_ACCOUNT_ID,
                "platformSpecificData": {
                    "privacyStatus": privacy,
                    "title": title,
                    "description": full_description
                }
            }
        ],
        "content": title,
        "mediaItems": [
            {
                "type": "video",
                "url": video_url
            }
        ]
    }

    if scheduled_time:
        payload["scheduledFor"] = scheduled_time
        print(f"Scheduling video for: {scheduled_time}")
    else:
        print("Uploading video immediately...")

    print(f"  Title: {title}")
    print(f"  Privacy: {privacy}")

    response = requests.post(url, json=payload, headers=get_headers())

    if response.status_code in [200, 201]:
        result = response.json()
        print(f"Upload successful!")
        print(f"  Post ID: {result.get('id')}")
        print(f"  Status: {result.get('status')}")
        return result
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_post_status(post_id: str):
    """Check status of a scheduled/uploaded post"""
    url = f"{BASE_URL}/posts/{post_id}"
    response = requests.get(url, headers=get_headers())

    if response.status_code == 200:
        result = response.json()
        print(f"Post Status:")
        print(f"  ID: {result.get('id')}")
        print(f"  Status: {result.get('status')}")
        print(f"  Scheduled: {result.get('scheduledFor', 'Not scheduled')}")
        platforms = result.get('platforms', [])
        for p in platforms:
            print(f"  {p.get('platform')}: {p.get('status')} - {p.get('url', 'No URL yet')}")
        return result
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def list_posts(limit: int = 10):
    """List recent posts"""
    url = f"{BASE_URL}/posts"
    params = {"limit": limit}
    response = requests.get(url, headers=get_headers(), params=params)

    if response.status_code == 200:
        data = response.json()
        posts = data.get("posts", data) if isinstance(data, dict) else data
        print(f"Recent posts:")
        if isinstance(posts, list):
            for post in posts[:limit]:
                print(f"  - {post.get('id')}: {post.get('content', 'No title')[:40]}... ({post.get('status')})")
        return posts
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def delete_post(post_id: str):
    """Delete a scheduled post"""
    url = f"{BASE_URL}/posts/{post_id}"
    response = requests.delete(url, headers=get_headers())

    if response.status_code in [200, 204]:
        print(f"Post {post_id} deleted successfully")
        return True
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Late.dev API")
    print("=" * 50)

    if not API_KEY:
        print("ERROR: LATE_API_KEY not set!")
        print("Run: export LATE_API_KEY=your_key_here")
        exit(1)

    # List connected accounts
    print("\n1. Listing connected accounts...")
    list_accounts()

    # Get YouTube account details
    if YOUTUBE_ACCOUNT_ID:
        print(f"\n2. Getting YouTube account details...")
        get_account()
    else:
        print("\n2. LATE_YOUTUBE_ACCOUNT_ID not set - skipping account details")

    # List recent posts
    print("\n3. Listing recent posts...")
    list_posts(5)

    print("\n" + "=" * 50)
    print("Test complete!")
    print("=" * 50)

    print("\nTo upload a video:")
    print("  scheduled = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'")
    print("  upload_video(")
    print("      video_url='https://your-video-url.mp4',")
    print("      title='Your Video Title',")
    print("      description='Your description',")
    print("      scheduled_time=scheduled,")
    print("      privacy='private',  # Use 'private' for testing")
    print("      hashtags=['fitness', 'health']")
    print("  )")
