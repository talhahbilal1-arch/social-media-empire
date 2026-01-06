"""
Agent 4: Analytics Collector
=============================
Runs daily at 11:00 PM to collect engagement metrics

Pulls analytics from:
- Pinterest API
- YouTube Analytics
- TikTok (via Make.com webhook or manual import)
- Instagram (via Make.com webhook or manual import)

Saves to analytics table for Self-Improvement agent to analyze.
"""
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient
from core.notifications import send_alert


class AnalyticsCollector:
    """Collects engagement analytics from social platforms."""

    def __init__(self):
        self.db = SupabaseClient()

    def run(self) -> Dict:
        """Main entry point - collect analytics for recent posts."""
        run_id = self.db.start_agent_run('analytics_collector', os.environ.get('GITHUB_RUN_ID'))

        results = {
            'posts_analyzed': 0,
            'analytics_saved': 0,
            'by_platform': {},
            'errors': []
        }

        try:
            # Get posts from last 7 days that need analytics
            posts = self._get_posts_needing_analytics()
            print(f"Found {len(posts)} posts to analyze")

            for post in posts:
                try:
                    platform = post['platform']
                    analytics = self._collect_for_platform(post)

                    if analytics:
                        self.db.save_analytics(analytics)
                        results['analytics_saved'] += 1
                        results['by_platform'][platform] = results['by_platform'].get(platform, 0) + 1

                    results['posts_analyzed'] += 1

                except Exception as e:
                    results['errors'].append(f"{post['id']}: {str(e)}")

            # Update daily aggregates
            self._update_daily_aggregates()

            self.db.complete_agent_run(
                run_id,
                status='completed',
                items_processed=results['posts_analyzed'],
                items_created=results['analytics_saved'],
                items_failed=len(results['errors'])
            )

        except Exception as e:
            results['errors'].append(str(e))
            self.db.complete_agent_run(run_id, status='failed', error_log=[str(e)])
            send_alert("Analytics Collector Failed", str(e), severity="error")
            raise

        print(f"\nAnalytics collection complete: {results['analytics_saved']} records saved")
        return results

    def _get_posts_needing_analytics(self) -> List[Dict]:
        """Get recent posts that need analytics collection."""
        # Get posts from last 7 days
        return self.db.get_posts_for_analytics(hours_ago=168)  # 7 days

    def _collect_for_platform(self, post: Dict) -> Optional[Dict]:
        """Collect analytics for a specific post based on platform."""
        platform = post['platform']

        collectors = {
            'pinterest': self._collect_pinterest,
            'youtube': self._collect_youtube,
            'tiktok': self._collect_tiktok,
            'instagram': self._collect_instagram,
        }

        collector = collectors.get(platform)
        if collector:
            return collector(post)

        return None

    def _collect_pinterest(self, post: Dict) -> Optional[Dict]:
        """
        Collect Pinterest analytics.

        Note: Pinterest Analytics API requires an approved app.
        For now, this is a placeholder that can be filled in once
        you have API access, or you can import data from Make.com.
        """
        # Pinterest API would go here
        # For MVP, return placeholder or check if data came from Make.com

        # Check if we have data from Make.com webhook
        # (Make.com can push analytics to a Supabase webhook)

        return {
            'post_id': post['id'],
            'platform': 'pinterest',
            'views': 0,  # Placeholder
            'impressions': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'saves': 0,
            'clicks': 0,
            'recorded_at': datetime.utcnow().isoformat()
        }

    def _collect_youtube(self, post: Dict) -> Optional[Dict]:
        """
        Collect YouTube analytics.

        Requires YouTube Data API v3 with youtube.readonly scope.
        """
        api_key = os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            return None

        video_id = post.get('platform_post_id')
        if not video_id:
            return None

        try:
            import requests
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/videos",
                params={
                    'part': 'statistics',
                    'id': video_id,
                    'key': api_key
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if data.get('items'):
                stats = data['items'][0].get('statistics', {})
                return {
                    'post_id': post['id'],
                    'platform': 'youtube',
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'shares': 0,
                    'saves': 0,
                    'clicks': 0,
                    'recorded_at': datetime.utcnow().isoformat()
                }
        except Exception as e:
            print(f"  YouTube API error: {e}")

        return None

    def _collect_tiktok(self, post: Dict) -> Optional[Dict]:
        """
        Collect TikTok analytics.

        TikTok's API is limited. Best approach is to:
        1. Use Make.com to collect and push to Supabase
        2. Or manually import from TikTok analytics

        This is a placeholder for when data is available.
        """
        return {
            'post_id': post['id'],
            'platform': 'tiktok',
            'views': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'saves': 0,
            'clicks': 0,
            'recorded_at': datetime.utcnow().isoformat()
        }

    def _collect_instagram(self, post: Dict) -> Optional[Dict]:
        """
        Collect Instagram analytics.

        Requires Instagram Graph API via Facebook Business account.
        For MVP, use Make.com to collect and push to Supabase.
        """
        return {
            'post_id': post['id'],
            'platform': 'instagram',
            'views': 0,
            'impressions': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'saves': 0,
            'clicks': 0,
            'recorded_at': datetime.utcnow().isoformat()
        }

    def _update_daily_aggregates(self) -> None:
        """Update daily aggregate analytics for faster querying."""
        # This would aggregate today's analytics into analytics_daily table
        # Implemented as a simple pass for MVP
        pass


def main():
    """Entry point for GitHub Actions."""
    print(f"Starting Analytics Collector at {datetime.utcnow().isoformat()}")

    collector = AnalyticsCollector()
    results = collector.run()

    print(f"\nResults: {json.dumps(results, indent=2)}")
    return results


if __name__ == '__main__':
    main()
