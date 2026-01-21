"""Supabase database client for Social Media Empire."""

from datetime import datetime, timezone
from typing import Optional, Any
from dataclasses import dataclass
from supabase import create_client, Client

from utils.config import get_config


@dataclass
class SupabaseClient:
    """Wrapper for Supabase database operations."""

    client: Client

    @classmethod
    def from_config(cls) -> "SupabaseClient":
        """Create client from environment configuration."""
        config = get_config()
        client = create_client(config.supabase_url, config.supabase_key)
        return cls(client=client)

    # ==================== Video Content ====================

    def log_video_creation(
        self,
        brand: str,
        platform: str,
        video_url: str,
        title: str,
        description: str,
        status: str = "created"
    ) -> dict:
        """Log a created video to the database."""
        data = {
            "brand": brand,
            "platform": platform,
            "video_url": video_url,
            "title": title,
            "description": description,
            "status": status,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = self.client.table("videos").insert(data).execute()
        return result.data[0] if result.data else {}

    def update_video_status(
        self,
        video_id: int,
        status: str,
        platform_id: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> dict:
        """Update video posting status."""
        data = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        if platform_id:
            data["platform_id"] = platform_id
        if error_message:
            data["error_message"] = error_message

        result = self.client.table("videos").update(data).eq("id", video_id).execute()
        return result.data[0] if result.data else {}

    def get_recent_videos(
        self,
        brand: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 10
    ) -> list[dict]:
        """Get recent videos, optionally filtered by brand/platform."""
        query = self.client.table("videos").select("*").order("created_at", desc=True).limit(limit)
        if brand:
            query = query.eq("brand", brand)
        if platform:
            query = query.eq("platform", platform)
        result = query.execute()
        return result.data or []

    # ==================== Content Bank ====================

    def get_unused_content(
        self,
        brand: str,
        content_type: str,
        limit: int = 5
    ) -> list[dict]:
        """Get unused content ideas from the bank."""
        result = (
            self.client.table("content_bank")
            .select("*")
            .eq("brand", brand)
            .eq("content_type", content_type)
            .eq("used", False)
            .limit(limit)
            .execute()
        )
        return result.data or []

    def mark_content_used(self, content_id: int) -> dict:
        """Mark content as used."""
        data = {
            "used": True,
            "used_at": datetime.now(timezone.utc).isoformat()
        }
        result = self.client.table("content_bank").update(data).eq("id", content_id).execute()
        return result.data[0] if result.data else {}

    def add_content_to_bank(
        self,
        brand: str,
        content_type: str,
        topic: str,
        details: dict
    ) -> dict:
        """Add new content to the content bank."""
        data = {
            "brand": brand,
            "content_type": content_type,
            "topic": topic,
            "details": details,
            "used": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = self.client.table("content_bank").insert(data).execute()
        return result.data[0] if result.data else {}

    # ==================== Email Subscribers ====================

    def add_subscriber(
        self,
        email: str,
        brand: str,
        source: str = "website",
        lead_magnet: Optional[str] = None
    ) -> dict:
        """Add a new email subscriber."""
        data = {
            "email": email,
            "brand": brand,
            "source": source,
            "lead_magnet": lead_magnet,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = self.client.table("subscribers").insert(data).execute()
        return result.data[0] if result.data else {}

    def get_subscribers(
        self,
        brand: Optional[str] = None,
        status: str = "active"
    ) -> list[dict]:
        """Get subscribers, optionally filtered by brand."""
        query = self.client.table("subscribers").select("*").eq("status", status)
        if brand:
            query = query.eq("brand", brand)
        result = query.execute()
        return result.data or []

    # ==================== Analytics ====================

    def log_analytics_event(
        self,
        event_type: str,
        brand: str,
        platform: str,
        data: dict
    ) -> dict:
        """Log an analytics event."""
        event_data = {
            "event_type": event_type,
            "brand": brand,
            "platform": platform,
            "data": data,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = self.client.table("analytics").insert(event_data).execute()
        return result.data[0] if result.data else {}

    def get_daily_stats(self, date: Optional[str] = None) -> dict:
        """Get stats for a specific date (defaults to today)."""
        if not date:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Get video counts
        videos = self.client.table("videos").select("brand, platform, status").gte(
            "created_at", f"{date}T00:00:00"
        ).lte("created_at", f"{date}T23:59:59").execute()

        # Get subscriber counts
        subscribers = self.client.table("subscribers").select("brand").gte(
            "created_at", f"{date}T00:00:00"
        ).lte("created_at", f"{date}T23:59:59").execute()

        return {
            "date": date,
            "videos_created": len(videos.data or []),
            "new_subscribers": len(subscribers.data or []),
            "videos_by_brand": self._count_by_field(videos.data or [], "brand"),
            "videos_by_platform": self._count_by_field(videos.data or [], "platform"),
            "subscribers_by_brand": self._count_by_field(subscribers.data or [], "brand")
        }

    @staticmethod
    def _count_by_field(data: list[dict], field: str) -> dict:
        """Count occurrences by a specific field."""
        counts = {}
        for item in data:
            value = item.get(field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    # ==================== Error Logging ====================

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: dict
    ) -> dict:
        """Log an error to the database."""
        data = {
            "error_type": error_type,
            "error_message": error_message,
            "context": context,
            "resolved": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = self.client.table("errors").insert(data).execute()
        return result.data[0] if result.data else {}

    def get_unresolved_errors(self, limit: int = 50) -> list[dict]:
        """Get unresolved errors."""
        result = (
            self.client.table("errors")
            .select("*")
            .eq("resolved", False)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    def resolve_error(self, error_id: int, resolution_notes: str = "") -> dict:
        """Mark an error as resolved."""
        data = {
            "resolved": True,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "resolution_notes": resolution_notes
        }
        result = self.client.table("errors").update(data).eq("id", error_id).execute()
        return result.data[0] if result.data else {}


_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Get or create the global Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient.from_config()
    return _supabase_client
