"""
D-ID API Test Script
Tests avatar video generation from audio + image
"""

import os
import requests
import time
import base64
from pathlib import Path

# Configuration
API_KEY = os.getenv("DID_API_KEY")
BASE_URL = "https://api.d-id.com"

def get_headers():
    """Get authorization headers for D-ID API"""
    # D-ID uses Basic auth with API key
    auth_string = base64.b64encode(f"{API_KEY}:".encode()).decode()
    return {
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/json"
    }

def get_credits():
    """Check remaining credits"""
    url = f"{BASE_URL}/credits"
    response = requests.get(url, headers=get_headers())

    if response.status_code == 200:
        credits = response.json()
        print("Credits Info:")
        print(f"  Remaining: {credits.get('remaining', 'N/A')}")
        print(f"  Total: {credits.get('total', 'N/A')}")
        return credits
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def list_presenters():
    """List available presenters/avatars"""
    url = f"{BASE_URL}/clips/presenters"
    response = requests.get(url, headers=get_headers())

    if response.status_code == 200:
        data = response.json()
        presenters = data.get("presenters", [])
        print(f"Available presenters ({len(presenters)} found):")
        for p in presenters[:10]:  # Show first 10
            print(f"  - {p.get('presenter_id')}: {p.get('name', 'Unnamed')}")
        return presenters
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def upload_image(image_path: str):
    """Upload an image to use as avatar source"""
    url = f"{BASE_URL}/images"

    # Remove Content-Type for multipart upload
    headers = {"Authorization": get_headers()["Authorization"]}

    with open(image_path, "rb") as f:
        files = {"image": (Path(image_path).name, f, "image/jpeg")}
        response = requests.post(url, headers=headers, files=files)

    if response.status_code in [200, 201]:
        result = response.json()
        image_url = result.get("url")
        print(f"Image uploaded successfully!")
        print(f"URL: {image_url}")
        print(f"Add this to your .env: DID_AVATAR_IMAGE_URL={image_url}")
        return image_url
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def create_talk(
    audio_url: str,
    source_url: str,  # Image URL
    output_path: str = "output/test_video.mp4"
):
    """Create a talking avatar video from audio and image"""
    url = f"{BASE_URL}/talks"

    payload = {
        "source_url": source_url,
        "script": {
            "type": "audio",
            "audio_url": audio_url
        },
        "config": {
            "fluent": True,
            "pad_audio": 0.5,
            "stitch": True
        }
    }

    print(f"Creating talk video...")
    print(f"  Audio: {audio_url}")
    print(f"  Image: {source_url}")

    response = requests.post(url, json=payload, headers=get_headers())

    if response.status_code in [200, 201]:
        result = response.json()
        talk_id = result.get("id")
        print(f"Talk created! ID: {talk_id}")

        # Poll for completion
        return poll_talk_status(talk_id, output_path)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def create_talk_with_text(
    text: str,
    source_url: str,  # Image URL
    voice_id: str = "en-US-GuyNeural",  # Microsoft TTS voice
    output_path: str = "output/test_video.mp4"
):
    """Create a talking avatar video with D-ID's built-in TTS"""
    url = f"{BASE_URL}/talks"

    payload = {
        "source_url": source_url,
        "script": {
            "type": "text",
            "input": text,
            "provider": {
                "type": "microsoft",
                "voice_id": voice_id
            }
        },
        "config": {
            "fluent": True,
            "pad_audio": 0.5,
            "stitch": True
        }
    }

    print(f"Creating talk video with text...")
    print(f"  Text: {text[:50]}...")
    print(f"  Image: {source_url}")

    response = requests.post(url, json=payload, headers=get_headers())

    if response.status_code in [200, 201]:
        result = response.json()
        talk_id = result.get("id")
        print(f"Talk created! ID: {talk_id}")

        # Poll for completion
        return poll_talk_status(talk_id, output_path)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def poll_talk_status(talk_id: str, output_path: str, max_attempts: int = 60):
    """Poll for video generation completion"""
    url = f"{BASE_URL}/talks/{talk_id}"

    print("Waiting for video generation...")
    for attempt in range(max_attempts):
        response = requests.get(url, headers=get_headers())

        if response.status_code == 200:
            result = response.json()
            status = result.get("status")

            if status == "done":
                video_url = result.get("result_url")
                print(f"\nVideo ready!")
                print(f"URL: {video_url}")

                # Download video
                download_video(video_url, output_path)
                return output_path

            elif status == "error":
                error = result.get("error", {})
                print(f"\nError: {error.get('description', 'Unknown error')}")
                return None

            elif status in ["created", "started"]:
                print(f"  Status: {status} (attempt {attempt + 1}/{max_attempts})", end="\r")

        time.sleep(5)

    print("\nTimeout waiting for video generation")
    return None

def download_video(url: str, output_path: str):
    """Download the generated video"""
    print(f"Downloading video...")
    response = requests.get(url)

    if response.status_code == 200:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Video saved to: {output_path}")
        print(f"File size: {len(response.content) / 1024 / 1024:.2f} MB")
    else:
        print(f"Error downloading: {response.status_code}")

def get_talk(talk_id: str):
    """Get status/info for a specific talk"""
    url = f"{BASE_URL}/talks/{talk_id}"
    response = requests.get(url, headers=get_headers())

    if response.status_code == 200:
        result = response.json()
        print(f"Talk Info:")
        print(f"  ID: {result.get('id')}")
        print(f"  Status: {result.get('status')}")
        print(f"  Created: {result.get('created_at')}")
        if result.get("result_url"):
            print(f"  Video URL: {result.get('result_url')}")
        return result
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("Testing D-ID API")
    print("=" * 50)

    if not API_KEY:
        print("ERROR: DID_API_KEY not set!")
        print("Run: export DID_API_KEY=your_key_here")
        exit(1)

    # Check credits
    print("\n1. Checking credits...")
    get_credits()

    # List available presenters
    print("\n2. Listing available presenters...")
    list_presenters()

    print("\n" + "=" * 50)
    print("Basic tests complete!")
    print("=" * 50)

    print("\nTo create a video:")
    print("1. Upload your headshot:")
    print("   image_url = upload_image('assets/avatar_photo.jpg')")
    print("\n2. Generate with ElevenLabs audio:")
    print("   create_talk(audio_url, image_url)")
    print("\n3. Or use D-ID's built-in TTS:")
    print("   create_talk_with_text('Your script here', image_url)")
