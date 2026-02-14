"""
Supabase Client - Database operations for all agents
"""
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from supabase import create_client, Client


class SupabaseClient:
    """Wrapper for Supabase operations used by all agents."""

    def __init__(self):
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables required")

        self.client: Client = create_client(url, key)

    # ==========================================
    # BRANDS
    # ==========================================

    def get_active_brands(self) -> List[Dict]:
        """Get all active brands."""
        response = self.client.table('brands').select('*').eq('is_active', True).execute()
        return response.data

    def get_brand_by_name(self, name: str) -> Optional[Dict]:
        """Get a brand by its name."""
        response = self.client.table('brands').select('*').eq('name', name).single().execute()
        return response.data

    # ==========================================
    # TRENDING DISCOVERIES (Agent 7)
    # ==========================================

    def save_trend(self, trend: Dict) -> Dict:
        """Save a new trending discovery."""
        response = self.client.table('trending_discoveries').insert(trend).execute()
        return response.data[0] if response.data else None

    def save_trends_batch(self, trends: List[Dict]) -> List[Dict]:
        """Save multiple trends at once."""
        if not trends:
            return []
        response = self.client.table('trending_discoveries').insert(trends).execute()
        return response.data

    def get_unused_trends(self, brand_id: str, limit: int = 10) -> List[Dict]:
        """Get unused trends that haven't expired."""
        response = self.client.table('trending_discoveries').select('*')\
            .eq('brand_id', brand_id)\
            .eq('used', False)\
            .gt('expires_at', datetime.utcnow().isoformat())\
            .order('relevance_score', desc=True)\
            .order('discovered_at', desc=True)\
            .limit(limit)\
            .execute()
        return response.data

    def mark_trend_used(self, trend_id: str) -> None:
        """Mark a trend as used."""
        self.client.table('trending_discoveries').update({
            'used': True,
            'used_at': datetime.utcnow().isoformat()
        }).eq('id', trend_id).execute()

    def cleanup_expired_trends(self) -> int:
        """Delete trends older than 14 days."""
        cutoff = (datetime.utcnow() - timedelta(days=14)).isoformat()
        response = self.client.table('trending_discoveries')\
            .delete()\
            .lt('discovered_at', cutoff)\
            .execute()
        return len(response.data) if response.data else 0

    # ==========================================
    # CONTENT BANK (Agent 1)
    # ==========================================

    def save_content(self, content: Dict) -> Dict:
        """Save new content to the content bank."""
        response = self.client.table('content_bank').insert(content).execute()
        return response.data[0] if response.data else None

    def save_content_batch(self, contents: List[Dict]) -> List[Dict]:
        """Save multiple content pieces at once."""
        if not contents:
            return []
        response = self.client.table('content_bank').insert(contents).execute()
        return response.data

    def get_pending_content(self, brand_id: str, content_type: str = None, limit: int = 10) -> List[Dict]:
        """Get pending content for processing."""
        query = self.client.table('content_bank').select('*')\
            .eq('brand_id', brand_id)\
            .eq('status', 'pending')

        if content_type:
            query = query.eq('content_type', content_type)

        response = query.order('created_at', desc=False).limit(limit).execute()
        return response.data

    def get_content_for_posting(self, brand_id: str, platform: str, limit: int = 5) -> List[Dict]:
        """Get content ready to post that hasn't been posted to this platform."""
        # Get content that's ready
        response = self.client.table('content_bank').select('*, videos(*)')\
            .eq('brand_id', brand_id)\
            .in_('status', ['pending', 'video_ready'])\
            .order('performance_score', desc=True)\
            .limit(limit * 2)\
            .execute()

        content = response.data

        # Filter out already posted to this platform
        ready_content = []
        for c in content:
            posts = self.client.table('posts_log').select('id')\
                .eq('content_id', c['id'])\
                .eq('platform', platform)\
                .eq('status', 'posted')\
                .execute()

            if not posts.data:
                ready_content.append(c)
                if len(ready_content) >= limit:
                    break

        return ready_content

    def update_content_status(self, content_id: str, status: str) -> None:
        """Update content status."""
        self.client.table('content_bank').update({
            'status': status,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', content_id).execute()

    # ==========================================
    # BLOG ARTICLES (Agent 8)
    # ==========================================

    def save_blog_article(self, article: Dict) -> Dict:
        """Save a new blog article."""
        response = self.client.table('blog_articles').insert(article).execute()
        return response.data[0] if response.data else None

    def get_pending_blogs(self, brand_id: str, limit: int = 5) -> List[Dict]:
        """Get blogs ready for publishing."""
        response = self.client.table('blog_articles').select('*')\
            .eq('brand_id', brand_id)\
            .eq('status', 'ready')\
            .order('created_at', desc=False)\
            .limit(limit)\
            .execute()
        return response.data

    def update_blog_status(self, blog_id: str, status: str, **kwargs) -> None:
        """Update blog article status."""
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow().isoformat(),
            **kwargs
        }
        self.client.table('blog_articles').update(update_data).eq('id', blog_id).execute()

    def get_recent_blogs(self, brand_id: str, limit: int = 10) -> List[Dict]:
        """Get recent published blogs for internal linking."""
        response = self.client.table('blog_articles').select('id, title, slug, published_url')\
            .eq('brand_id', brand_id)\
            .eq('status', 'published')\
            .order('published_at', desc=True)\
            .limit(limit)\
            .execute()
        return response.data

    def link_blog_to_social(self, blog_id: str, content_id: str) -> None:
        """Create link between blog and social content."""
        self.client.table('blog_to_social').insert({
            'blog_article_id': blog_id,
            'content_id': content_id
        }).execute()

    # ==========================================
    # VIDEOS (Agent 2)
    # ==========================================

    def save_video(self, video: Dict) -> Dict:
        """Save a new video record."""
        response = self.client.table('videos').insert(video).execute()
        return response.data[0] if response.data else None

    def update_video(self, video_id: str, **kwargs) -> None:
        """Update video record."""
        self.client.table('videos').update(kwargs).eq('id', video_id).execute()

    def get_pending_videos(self, limit: int = 10) -> List[Dict]:
        """Get content that needs video rendering."""
        response = self.client.table('content_bank').select('*')\
            .eq('status', 'pending')\
            .in_('content_type', ['video', 'reel', 'short'])\
            .is_('video_script', 'not.null')\
            .order('created_at', desc=False)\
            .limit(limit)\
            .execute()
        return response.data

    # ==========================================
    # POSTS LOG (Agent 3)
    # ==========================================

    def log_post(self, post: Dict) -> Dict:
        """Log a social media post."""
        response = self.client.table('posts_log').insert(post).execute()
        return response.data[0] if response.data else None

    def update_post(self, post_id: str, **kwargs) -> None:
        """Update a post log entry."""
        self.client.table('posts_log').update(kwargs).eq('id', post_id).execute()

    def get_posts_for_analytics(self, hours_ago: int = 24) -> List[Dict]:
        """Get recent posts that need analytics collection."""
        cutoff = (datetime.utcnow() - timedelta(hours=hours_ago)).isoformat()
        response = self.client.table('posts_log').select('*')\
            .eq('status', 'posted')\
            .gt('posted_at', cutoff)\
            .execute()
        return response.data

    # ==========================================
    # ANALYTICS (Agent 4)
    # ==========================================

    def save_analytics(self, analytics: Dict) -> Dict:
        """Save analytics record."""
        response = self.client.table('analytics').insert(analytics).execute()
        return response.data[0] if response.data else None

    def get_content_analytics(self, content_id: str) -> List[Dict]:
        """Get all analytics for a piece of content."""
        posts = self.client.table('posts_log').select('id, platform')\
            .eq('content_id', content_id).execute()

        all_analytics = []
        for post in posts.data:
            analytics = self.client.table('analytics').select('*')\
                .eq('post_id', post['id'])\
                .order('recorded_at', desc=True)\
                .limit(1)\
                .execute()
            if analytics.data:
                all_analytics.extend(analytics.data)

        return all_analytics

    # ==========================================
    # WINNING PATTERNS (Agent 5)
    # ==========================================

    def get_winning_patterns(self, brand_id: str, pattern_type: str = None) -> List[Dict]:
        """Get active winning patterns for a brand."""
        query = self.client.table('winning_patterns').select('*')\
            .eq('brand_id', brand_id)\
            .eq('is_active', True)

        if pattern_type:
            query = query.eq('pattern_type', pattern_type)

        response = query.order('avg_engagement', desc=True).execute()
        return response.data

    def upsert_pattern(self, pattern: Dict) -> Dict:
        """Insert or update a winning pattern."""
        response = self.client.table('winning_patterns').upsert(
            pattern,
            on_conflict='brand_id,pattern_type,pattern_value,platform'
        ).execute()
        return response.data[0] if response.data else None

    # ==========================================
    # SYSTEM CONFIG
    # ==========================================

    def get_config(self, brand_id: str, config_key: str) -> Optional[Dict]:
        """Get a configuration value."""
        response = self.client.table('system_config').select('config_value')\
            .eq('brand_id', brand_id)\
            .eq('config_key', config_key)\
            .single()\
            .execute()
        return response.data['config_value'] if response.data else None

    def update_config(self, brand_id: str, config_key: str, config_value: Dict, updated_by: str = 'manual') -> None:
        """Update a configuration value."""
        self.client.table('system_config').upsert({
            'brand_id': brand_id,
            'config_key': config_key,
            'config_value': config_value,
            'updated_by': updated_by,
            'updated_at': datetime.utcnow().isoformat()
        }, on_conflict='brand_id,config_key').execute()

    # ==========================================
    # SYSTEM CHANGES LOG
    # ==========================================

    def log_system_change(self, change: Dict) -> None:
        """Log a system change for audit trail."""
        self.client.table('system_changes').insert(change).execute()

    # ==========================================
    # HEALTH CHECKS (Agent 6)
    # ==========================================

    def log_health_check(self, check: Dict) -> None:
        """Log a health check result."""
        self.client.table('health_checks').insert(check).execute()

    def get_recent_health_checks(self, agent_name: str = None, hours: int = 24) -> List[Dict]:
        """Get recent health checks."""
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        query = self.client.table('health_checks').select('*')\
            .gt('checked_at', cutoff)

        if agent_name:
            query = query.eq('agent_name', agent_name)

        response = query.order('checked_at', desc=True).execute()
        return response.data

    def get_last_agent_run(self, agent_name: str) -> Optional[Dict]:
        """Get the last run for an agent."""
        response = self.client.table('agent_runs').select('*')\
            .eq('agent_name', agent_name)\
            .order('started_at', desc=True)\
            .limit(1)\
            .execute()
        return response.data[0] if response.data else None

    # ==========================================
    # AGENT RUNS
    # ==========================================

    def start_agent_run(self, agent_name: str, run_id: str = None) -> str:
        """Start tracking an agent run."""
        response = self.client.table('agent_runs').insert({
            'agent_name': agent_name,
            'run_id': run_id,
            'status': 'started',
            'started_at': datetime.utcnow().isoformat()
        }).execute()
        return response.data[0]['id'] if response.data else None

    def update_agent_run(self, run_id: str, **kwargs) -> None:
        """Update an agent run."""
        self.client.table('agent_runs').update(kwargs).eq('id', run_id).execute()

    def complete_agent_run(self, run_id: str, status: str, items_processed: int = 0,
                          items_created: int = 0, items_failed: int = 0, error_log: List[str] = None) -> None:
        """Mark an agent run as complete."""
        started = self.client.table('agent_runs').select('started_at')\
            .eq('id', run_id).single().execute()

        duration = None
        if started.data:
            start_time = datetime.fromisoformat(started.data['started_at'].replace('Z', '+00:00'))
            duration = int((datetime.utcnow().replace(tzinfo=start_time.tzinfo) - start_time).total_seconds())

        self.client.table('agent_runs').update({
            'status': status,
            'items_processed': items_processed,
            'items_created': items_created,
            'items_failed': items_failed,
            'error_log': error_log or [],
            'completed_at': datetime.utcnow().isoformat(),
            'duration_seconds': duration
        }).eq('id', run_id).execute()
