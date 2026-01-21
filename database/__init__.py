"""Database module for Social Media Empire."""

from .supabase_client import SupabaseClient, get_supabase_client

__all__ = ["SupabaseClient", "get_supabase_client"]
