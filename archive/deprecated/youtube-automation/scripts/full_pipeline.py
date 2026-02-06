"""
Full Pipeline Test Script
Runs the complete video generation pipeline locally for testing
"""

import os
import sys
import json
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import test modules
from test_elevenlabs import generate_speech, get_usage as get_elevenlabs_usage
from test_did import create_talk, get_credits as get_did_credits
from test_late import upload_video, list_accounts

def load_settings():
    """Load settings from config file"""
    settings_path = Path(__file__).parent.parent / "config" / "settings.json"
    if settings_path.exists():
        with open(settings_path) as f:
            return json.load(f)
    return {}

def check_environment():
    """Verify all required environment variables are set"""
    required_vars = [
        "ELEVENLABS_API_KEY",
        "ELEVENLABS_VOICE_ID",
        "DID_API_KEY",
        "DID_AVATAR_IMAGE_URL",
        "LATE_API_KEY",
        "LATE_YOUTUBE_ACCOUNT_ID"
    ]

    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        return False

    print("✅ All environment variables set")
    return True

def check_api_credits():
    """Check remaining credits/quota for all APIs"""
    print("\n📊 Checking API credits...")

    print("\nElevenLabs:")
    get_elevenlabs_usage()

    print("\nD-ID:")
    get_did_credits()

    print("\nLate.dev:")
    list_accounts()

def run_pipeline(
    script_text: str,
    title: str,
    description: str,
    hashtags: list = None,
    dry_run: bool = False
):
    """
    Run the full video generation pipeline

    Args:
        script_text: The script to convert to video
        title: YouTube video title
        description: YouTube video description
        hashtags: List of hashtags (without #)
        dry_run: If True, stop before YouTube upload
    """
    print("\n" + "=" * 60)
    print("🚀 Starting Full Pipeline")
    print("=" * 60)

    settings = load_settings()
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Step 1: Generate Audio
    print("\n📢 Step 1: Generating audio with ElevenLabs...")
    audio_path = str(output_dir / f"audio_{timestamp}.mp3")

    result = generate_speech(script_text, audio_path)
    if not result:
        print("❌ Audio generation failed")
        return None

    print(f"✅ Audio saved: {audio_path}")

    # Step 2: Generate Avatar Video
    print("\n🎬 Step 2: Creating avatar video with D-ID...")

    # For D-ID, we need a publicly accessible audio URL
    # In production, this would be uploaded to Google Drive first
    # For testing, we need to host the audio somewhere accessible

    avatar_image_url = os.getenv("DID_AVATAR_IMAGE_URL")

    # Note: D-ID requires a publicly accessible audio URL
    # You'll need to upload the audio to Google Drive, S3, or similar
    # and make it publicly accessible

    print("⚠️  Note: D-ID requires a publicly accessible audio URL")
    print("   For local testing, upload the audio file to Google Drive")
    print("   and use the sharing link.")

    if dry_run:
        print("\n🔸 Dry run - skipping D-ID video generation")
        video_url = "https://example.com/test-video.mp4"
    else:
        # In real usage, you'd provide the Google Drive link here
        audio_url = input("\nEnter public audio URL (or press Enter to skip): ").strip()

        if not audio_url:
            print("⏭️  Skipping video generation")
            video_url = None
        else:
            video_path = str(output_dir / f"video_{timestamp}.mp4")
            result = create_talk(audio_url, avatar_image_url, video_path)

            if not result:
                print("❌ Video generation failed")
                return None

            print(f"✅ Video saved: {video_path}")
            video_url = result  # In production, this would be uploaded somewhere

    # Step 3: Upload to YouTube
    print("\n📤 Step 3: Uploading to YouTube via Late.dev...")

    if dry_run or not video_url:
        print("🔸 Dry run - skipping YouTube upload")
        print("\n✅ Pipeline test complete (dry run)")
        return {
            "audio_path": audio_path,
            "video_url": video_url,
            "status": "dry_run"
        }

    # Schedule for tomorrow at noon PST
    from datetime import datetime, timedelta
    scheduled_time = (datetime.utcnow() + timedelta(days=1)).replace(
        hour=20, minute=0, second=0, microsecond=0  # 12 PM PST = 8 PM UTC
    ).isoformat() + "Z"

    result = upload_video(
        video_url=video_url,
        title=title,
        description=description,
        scheduled_time=scheduled_time,
        privacy="private",  # Use private for testing
        hashtags=hashtags or ["fitness", "health", "menover40"]
    )

    if result:
        print(f"✅ Video scheduled for upload!")
        print(f"   Post ID: {result.get('id')}")
    else:
        print("❌ Upload failed")

    print("\n" + "=" * 60)
    print("🎉 Pipeline Complete!")
    print("=" * 60)

    return {
        "audio_path": audio_path,
        "video_url": video_url,
        "youtube_post_id": result.get("id") if result else None,
        "status": "success"
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the full video pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Run without uploading")
    parser.add_argument("--check-credits", action="store_true", help="Check API credits only")
    args = parser.parse_args()

    print("=" * 60)
    print("YouTube Shorts Automation - Full Pipeline Test")
    print("=" * 60)

    # Check environment
    if not check_environment():
        print("\nSet missing variables and try again.")
        sys.exit(1)

    if args.check_credits:
        check_api_credits()
        sys.exit(0)

    # Test script
    test_script = """
    Stop taking zinc for testosterone unless you're actually deficient.

    A 2023 study found that zinc supplementation only raised testosterone
    in men who were already low to begin with.

    If your zinc levels are normal, you're wasting your money.

    Here's what to do instead:

    First, get a blood test. Check your zinc AND testosterone levels.

    Second, if you're deficient, 15 to 30 milligrams daily is enough.
    More isn't better.

    Third, focus on what actually works: sleep, strength training,
    and managing stress.

    Follow for more evidence-based fitness tips.
    """

    test_title = "Stop Taking Zinc for Testosterone"
    test_description = """
Learn why zinc supplementation might not boost your testosterone, and what actually works.

Based on 2023 research.

🔔 Subscribe for daily fitness tips for men 35+

    """.strip()

    result = run_pipeline(
        script_text=test_script.strip(),
        title=test_title,
        description=test_description,
        hashtags=["testosterone", "fitness", "menover40", "health", "workout"],
        dry_run=args.dry_run
    )

    if result:
        print("\nResult:", json.dumps(result, indent=2))
