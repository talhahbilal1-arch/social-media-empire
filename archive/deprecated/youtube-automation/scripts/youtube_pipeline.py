"""
YouTube Shorts Automation Pipeline
Complete end-to-end video generation and publishing
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Import local modules
from supabase_client import (
    get_next_pending_script,
    mark_script_processing,
    mark_script_published,
    mark_script_failed,
    update_script_audio,
    update_script_video,
    log_error,
    update_daily_stats,
    test_connection
)

# ===========================================
# CONFIGURATION
# ===========================================

# API Keys from environment
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

DID_API_KEY = os.getenv("DID_API_KEY")
DID_AVATAR_IMAGE_URL = os.getenv("DID_AVATAR_IMAGE_URL")

LATE_API_KEY = os.getenv("LATE_API_KEY")
LATE_YOUTUBE_ACCOUNT_ID = os.getenv("LATE_YOUTUBE_ACCOUNT_ID")

SUPABASE_URL = os.getenv("SUPABASE_URL")

# Default avatar if none specified (D-ID compatible public image)
# Using a D-ID sample presenter image that's known to work
DEFAULT_AVATAR_URL = "https://d-id-public-bucket.s3.us-west-2.amazonaws.com/alice.jpg"


# ===========================================
# ELEVENLABS - VOICE GENERATION
# ===========================================

def generate_audio(text: str) -> tuple[bytes, int]:
    """
    Generate audio from text using ElevenLabs
    Returns: (audio_bytes, character_count)
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.4,
            "use_speaker_boost": True
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        return response.content, len(text)
    else:
        raise Exception(f"ElevenLabs error: {response.status_code} - {response.text}")


def upload_audio_to_supabase(audio_bytes: bytes, filename: str) -> str:
    """Upload audio to Supabase Storage and return public URL"""
    from supabase import create_client

    client = create_client(SUPABASE_URL, os.getenv("SUPABASE_SERVICE_KEY"))

    # Upload to 'audio' bucket
    bucket = client.storage.from_("audio")

    result = bucket.upload(
        filename,
        audio_bytes,
        {"content-type": "audio/mpeg"}
    )

    # Get public URL
    public_url = bucket.get_public_url(filename)
    return public_url


# ===========================================
# D-ID - AVATAR VIDEO GENERATION
# ===========================================

def create_avatar_video(audio_url: str, avatar_url: str = None) -> str:
    """
    Create talking avatar video using D-ID
    Returns: talk_id for polling
    """
    import base64

    url = "https://api.d-id.com/talks"

    # D-ID uses Basic auth
    auth_string = base64.b64encode(f"{DID_API_KEY}:".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/json"
    }

    payload = {
        "source_url": avatar_url or DID_AVATAR_IMAGE_URL or DEFAULT_AVATAR_URL,
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

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        return response.json()["id"]
    else:
        raise Exception(f"D-ID error: {response.status_code} - {response.text}")


def poll_video_status(talk_id: str, max_attempts: int = 60) -> str:
    """
    Poll D-ID for video completion
    Returns: video URL when ready
    """
    import base64

    url = f"https://api.d-id.com/talks/{talk_id}"
    auth_string = base64.b64encode(f"{DID_API_KEY}:".encode()).decode()

    headers = {"Authorization": f"Basic {auth_string}"}

    for attempt in range(max_attempts):
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            status = data.get("status")

            if status == "done":
                return data.get("result_url")
            elif status == "error":
                raise Exception(f"D-ID render failed: {data.get('error')}")

            # Still processing
            print(f"  Video rendering: {status} (attempt {attempt + 1}/{max_attempts})")

        time.sleep(5)

    raise Exception("D-ID render timeout")


# ===========================================
# YOUTUBE UPLOAD (Direct API or Late.dev)
# ===========================================

# Set to True to use direct YouTube API, False for Late.dev
USE_DIRECT_YOUTUBE_API = True


def upload_to_youtube(
    video_url: str,
    title: str,
    description: str,
    hashtags: str = "",
    scheduled_time: str = None
) -> dict:
    """
    Upload video to YouTube.
    Uses direct API if USE_DIRECT_YOUTUBE_API=True, otherwise Late.dev
    Returns: dict with video ID
    """
    # Build full description
    full_description = description
    if hashtags:
        full_description += "\n\n" + hashtags

    if USE_DIRECT_YOUTUBE_API:
        return upload_to_youtube_direct(video_url, title, full_description, hashtags, scheduled_time)
    else:
        return upload_to_youtube_late(video_url, title, full_description, scheduled_time)


def upload_to_youtube_direct(
    video_url: str,
    title: str,
    description: str,
    hashtags: str = "",
    scheduled_time: str = None
) -> dict:
    """
    Upload video to YouTube directly via YouTube Data API v3
    """
    from youtube_uploader import upload_to_youtube as yt_upload

    # Parse hashtags into tags list
    tags = []
    if hashtags:
        tags = [tag.strip().lstrip('#') for tag in hashtags.split() if tag.startswith('#')]

    result = yt_upload(
        video_url=video_url,
        title=title,
        description=description,
        tags=tags,
        category_id="26",  # Howto & Style (good for fitness)
        privacy_status="public",
        scheduled_time=scheduled_time,
        is_short=True
    )

    return {"id": result["id"], "url": result["url"]}


def upload_to_youtube_late(
    video_url: str,
    title: str,
    description: str,
    scheduled_time: str = None
) -> dict:
    """
    Upload video to YouTube via Late.dev (backup method)
    """
    url = "https://getlate.dev/api/v1/posts"

    headers = {
        "Authorization": f"Bearer {LATE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Default schedule: tomorrow at noon PST
    if not scheduled_time:
        tomorrow = datetime.utcnow() + timedelta(days=1)
        scheduled_time = tomorrow.replace(hour=20, minute=0, second=0, microsecond=0).isoformat() + "Z"

    payload = {
        "platforms": [
            {
                "platform": "youtube",
                "accountId": LATE_YOUTUBE_ACCOUNT_ID,
                "platformSpecificData": {
                    "privacyStatus": "public",
                    "title": title[:100],
                    "description": description
                }
            }
        ],
        "content": title,
        "mediaItems": [
            {
                "type": "video",
                "url": video_url
            }
        ],
        "scheduledFor": scheduled_time
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        return response.json()
    else:
        raise Exception(f"Late.dev error: {response.status_code} - {response.text}")


# ===========================================
# MAIN PIPELINE
# ===========================================

def process_single_script(script: dict, dry_run: bool = False) -> dict:
    """
    Process a single script through the entire pipeline
    Returns: result dict with status and details
    """
    script_id = script["id"]
    result = {
        "script_id": script_id,
        "title": script["title"],
        "status": "processing",
        "steps": []
    }

    try:
        # Step 1: Mark as processing
        mark_script_processing(script_id)
        result["steps"].append("marked_processing")

        # Step 2: Generate audio
        print(f"\n📢 Generating audio for: {script['title'][:40]}...")
        audio_bytes, char_count = generate_audio(script["script_text"])
        result["steps"].append("audio_generated")
        result["chars_used"] = char_count

        # Step 3: Upload audio to Supabase Storage
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"audio_{script_id}_{timestamp}.mp3"

        if not dry_run:
            audio_url = upload_audio_to_supabase(audio_bytes, audio_filename)
            update_script_audio(script_id, audio_url)
            result["audio_url"] = audio_url
            result["steps"].append("audio_uploaded")
        else:
            print("  [DRY RUN] Skipping audio upload")
            audio_url = "https://example.com/test-audio.mp3"
            result["steps"].append("audio_skipped_dry_run")

        # Step 4: Create avatar video
        print(f"🎬 Creating avatar video...")

        if not dry_run:
            talk_id = create_avatar_video(audio_url)
            result["did_talk_id"] = talk_id
            result["steps"].append("video_started")

            # Step 5: Wait for video
            print(f"⏳ Waiting for video render...")
            video_url = poll_video_status(talk_id)
            update_script_video(script_id, video_url, talk_id)
            result["video_url"] = video_url
            result["steps"].append("video_ready")
        else:
            print("  [DRY RUN] Skipping video generation")
            video_url = "https://example.com/test-video.mp4"
            result["steps"].append("video_skipped_dry_run")

        # Step 6: Upload to YouTube
        print(f"📤 Uploading to YouTube...")

        if not dry_run:
            youtube_result = upload_to_youtube(
                video_url=video_url,
                title=script["title"],
                description=script.get("description", ""),
                hashtags=script.get("hashtags", "")
            )

            late_post_id = youtube_result.get("id")

            mark_script_published(
                script_id,
                video_url=video_url,
                late_post_id=late_post_id
            )

            result["late_post_id"] = late_post_id
            result["steps"].append("published")
        else:
            print("  [DRY RUN] Skipping YouTube upload")
            result["steps"].append("publish_skipped_dry_run")

        # Update stats (optional - table may not exist)
        try:
            update_daily_stats(
                scripts_processed=1,
                videos_created=1 if not dry_run else 0,
                videos_published=1 if not dry_run else 0,
                elevenlabs_chars=char_count
            )
        except Exception as stats_error:
            print(f"  ⚠️ Stats update skipped: {stats_error}")

        result["status"] = "success"
        print(f"✅ Script processed successfully!")

    except Exception as e:
        error_msg = str(e)
        result["status"] = "failed"
        result["error"] = error_msg

        mark_script_failed(script_id, error_msg)
        log_error(script_id, "pipeline_error", error_msg, {"steps": result["steps"]})
        try:
            update_daily_stats(errors_count=1)
        except Exception:
            pass  # Stats table may not exist

        print(f"❌ Pipeline failed: {error_msg}")

    return result


def run_pipeline(dry_run: bool = False, max_scripts: int = 1):
    """
    Run the full pipeline for pending scripts
    """
    print("=" * 60)
    print("YouTube Shorts Automation Pipeline")
    print("=" * 60)

    # Check environment
    missing = []
    if not ELEVENLABS_API_KEY:
        missing.append("ELEVENLABS_API_KEY")
    if not DID_API_KEY:
        missing.append("DID_API_KEY")
    if not LATE_API_KEY:
        missing.append("LATE_API_KEY")
    if not LATE_YOUTUBE_ACCOUNT_ID:
        missing.append("LATE_YOUTUBE_ACCOUNT_ID")

    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return

    # Test database connection
    if not test_connection():
        return

    # Process scripts
    processed = 0
    for i in range(max_scripts):
        script = get_next_pending_script()

        if not script:
            print(f"\n📭 No pending scripts found")
            break

        print(f"\n{'='*60}")
        print(f"Processing script {i+1}/{max_scripts}: {script['title']}")
        print(f"{'='*60}")

        result = process_single_script(script, dry_run=dry_run)
        processed += 1

        if result["status"] == "success":
            print(f"\n✅ Completed: {result['title']}")
        else:
            print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")

    print(f"\n{'='*60}")
    print(f"Pipeline complete! Processed: {processed} scripts")
    print(f"{'='*60}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Shorts Automation Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Skip actual API calls")
    parser.add_argument("--max", type=int, default=1, help="Max scripts to process")
    args = parser.parse_args()

    # Load .env file if exists
    env_path = Path(__file__).parent.parent / "config" / ".env"
    if env_path.exists():
        print(f"Loading environment from: {env_path}")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

    run_pipeline(dry_run=args.dry_run, max_scripts=args.max)
