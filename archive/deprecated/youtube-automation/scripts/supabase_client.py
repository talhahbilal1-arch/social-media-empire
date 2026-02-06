"""
Supabase Client for YouTube Shorts Automation
Handles all database operations for script management
"""

import os
from datetime import datetime
from typing import Optional, Dict, List, Any
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://bjacmhjtpkdcxngkasux.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


def get_client() -> Client:
    """Get Supabase client instance"""
    if not SUPABASE_KEY:
        raise ValueError("SUPABASE_SERVICE_KEY not set!")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ===========================================
# SCRIPT OPERATIONS
# ===========================================

def get_next_pending_script() -> Optional[Dict]:
    """Get the oldest pending script for processing"""
    client = get_client()

    result = client.table("youtube_scripts") \
        .select("*") \
        .eq("status", "pending") \
        .order("created_at") \
        .limit(1) \
        .execute()

    if result.data and len(result.data) > 0:
        return result.data[0]
    return None


def get_script_by_id(script_id: int) -> Optional[Dict]:
    """Get a script by ID"""
    client = get_client()

    result = client.table("youtube_scripts") \
        .select("*") \
        .eq("id", script_id) \
        .single() \
        .execute()

    return result.data if result.data else None


def create_script(
    title: str,
    script_text: str,
    description: str = "",
    hashtags: str = "",
    thumbnail_text: str = ""
) -> Dict:
    """Create a new script"""
    client = get_client()

    data = {
        "title": title,
        "script_text": script_text,
        "description": description,
        "hashtags": hashtags,
        "thumbnail_text": thumbnail_text,
        "status": "pending"
    }

    result = client.table("youtube_scripts") \
        .insert(data) \
        .execute()

    return result.data[0] if result.data else None


def update_script_status(
    script_id: int,
    status: str,
    **kwargs
) -> Dict:
    """Update script status and optional fields"""
    client = get_client()

    data = {"status": status}

    # Add any additional fields
    for key, value in kwargs.items():
        if value is not None:
            data[key] = value

    # Set published_at if publishing
    if status == "published":
        data["published_at"] = datetime.utcnow().isoformat()

    result = client.table("youtube_scripts") \
        .update(data) \
        .eq("id", script_id) \
        .execute()

    return result.data[0] if result.data else None


def mark_script_processing(script_id: int) -> Dict:
    """Mark a script as being processed"""
    return update_script_status(script_id, "processing")


def mark_script_published(
    script_id: int,
    video_url: str = None,
    youtube_post_id: str = None,
    late_post_id: str = None
) -> Dict:
    """Mark a script as published"""
    return update_script_status(
        script_id,
        "published",
        video_url=video_url,
        youtube_post_id=youtube_post_id,
        late_post_id=late_post_id
    )


def mark_script_failed(
    script_id: int,
    error_message: str
) -> Dict:
    """Mark a script as failed"""
    # Get current retry count
    script = get_script_by_id(script_id)
    retry_count = (script.get("retry_count", 0) or 0) + 1

    return update_script_status(
        script_id,
        "failed",
        error_message=error_message,
        retry_count=retry_count
    )


def update_script_audio(script_id: int, audio_url: str) -> Dict:
    """Update script with generated audio URL"""
    client = get_client()

    result = client.table("youtube_scripts") \
        .update({"audio_url": audio_url}) \
        .eq("id", script_id) \
        .execute()

    return result.data[0] if result.data else None


def update_script_video(
    script_id: int,
    video_url: str,
    did_talk_id: str = None
) -> Dict:
    """Update script with generated video URL"""
    client = get_client()

    data = {"video_url": video_url}
    if did_talk_id:
        data["did_talk_id"] = did_talk_id

    result = client.table("youtube_scripts") \
        .update(data) \
        .eq("id", script_id) \
        .execute()

    return result.data[0] if result.data else None


def get_all_scripts(status: str = None, limit: int = 50) -> List[Dict]:
    """Get all scripts, optionally filtered by status"""
    client = get_client()

    query = client.table("youtube_scripts").select("*")

    if status:
        query = query.eq("status", status)

    result = query.order("created_at", desc=True).limit(limit).execute()

    return result.data if result.data else []


def reset_failed_scripts() -> int:
    """Reset failed scripts back to pending (for retry)"""
    client = get_client()

    result = client.table("youtube_scripts") \
        .update({"status": "pending", "error_message": None}) \
        .eq("status", "failed") \
        .lt("retry_count", 3) \
        .execute()

    return len(result.data) if result.data else 0


# ===========================================
# ERROR LOGGING
# ===========================================

def log_error(
    script_id: int,
    error_type: str,
    error_message: str,
    context: Dict = None
) -> Dict:
    """Log an error to the errors table"""
    client = get_client()

    data = {
        "script_id": script_id,
        "error_type": error_type,
        "error_message": error_message,
        "error_context": context or {}
    }

    result = client.table("youtube_automation_errors") \
        .insert(data) \
        .execute()

    return result.data[0] if result.data else None


# ===========================================
# STATS TRACKING
# ===========================================

def update_daily_stats(
    scripts_processed: int = 0,
    videos_created: int = 0,
    videos_published: int = 0,
    errors_count: int = 0,
    elevenlabs_chars: int = 0,
    did_credits: float = 0
) -> Dict:
    """Update or create daily stats"""
    client = get_client()

    today = datetime.utcnow().date().isoformat()

    # Try to get existing stats for today
    existing = client.table("youtube_automation_stats") \
        .select("*") \
        .eq("date", today) \
        .execute()

    if existing.data and len(existing.data) > 0:
        # Update existing
        current = existing.data[0]
        data = {
            "scripts_processed": current["scripts_processed"] + scripts_processed,
            "videos_created": current["videos_created"] + videos_created,
            "videos_published": current["videos_published"] + videos_published,
            "errors_count": current["errors_count"] + errors_count,
            "elevenlabs_chars_used": current["elevenlabs_chars_used"] + elevenlabs_chars,
            "did_credits_used": float(current["did_credits_used"] or 0) + did_credits
        }

        result = client.table("youtube_automation_stats") \
            .update(data) \
            .eq("date", today) \
            .execute()
    else:
        # Create new
        data = {
            "date": today,
            "scripts_processed": scripts_processed,
            "videos_created": videos_created,
            "videos_published": videos_published,
            "errors_count": errors_count,
            "elevenlabs_chars_used": elevenlabs_chars,
            "did_credits_used": did_credits
        }

        result = client.table("youtube_automation_stats") \
            .insert(data) \
            .execute()

    return result.data[0] if result.data else None


def get_stats(days: int = 7) -> List[Dict]:
    """Get stats for the last N days"""
    client = get_client()

    result = client.table("youtube_automation_stats") \
        .select("*") \
        .order("date", desc=True) \
        .limit(days) \
        .execute()

    return result.data if result.data else []


# ===========================================
# TEST / UTILITY FUNCTIONS
# ===========================================

def test_connection() -> bool:
    """Test database connection"""
    try:
        client = get_client()
        result = client.table("youtube_scripts").select("id").limit(1).execute()
        print("✅ Supabase connection successful!")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False


def get_pending_count() -> int:
    """Get count of pending scripts"""
    client = get_client()

    result = client.table("youtube_scripts") \
        .select("id", count="exact") \
        .eq("status", "pending") \
        .execute()

    return result.count if result.count else 0


if __name__ == "__main__":
    print("=" * 50)
    print("Testing Supabase Connection")
    print("=" * 50)

    # Test connection
    if test_connection():
        # Show pending scripts count
        pending = get_pending_count()
        print(f"\nPending scripts: {pending}")

        # Show recent scripts
        scripts = get_all_scripts(limit=5)
        print(f"\nRecent scripts ({len(scripts)}):")
        for s in scripts:
            print(f"  [{s['status']}] {s['title'][:40]}...")
