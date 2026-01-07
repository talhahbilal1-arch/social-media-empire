"""
Agent 3: Multi-Platform Poster
===============================
Runs 3x daily (9 AM, 1 PM, 9 PM UTC)

Posts content to multiple platforms:
- Pinterest (via Make.com webhook - scenarios already running)
- YouTube Shorts (via YouTube Data API)

Rate limits: 3 posts per platform per day to avoid spam detection.
"""
import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient
from core.notifications import send_alert
from core.youtube_client import YouTubeClient


class MultiPlatformPoster:
    """Posts content to Pinterest and YouTube."""

    # Rate limits per platform per day
    DAILY_LIMIT = 3

    # Supported platforms
    PLATFORMS = ['pinterest', 'youtube']

    def __init__(self):
        self.db = SupabaseClient()

        # Make.com webhook URL for Pinterest (triggers existing scenario)
        self.pinterest_webhook = os.environ.get('MAKECOM_PINTEREST_WEBHOOK')

        # YouTube OAuth client
        self.youtube_client = YouTubeClient()

        # Track what's enabled
        self.pinterest_enabled = bool(self.pinterest_webhook)
        self.youtube_enabled = self.youtube_client.oauth_configured

        if not self.pinterest_enabled:
            print("Note: Pinterest posting disabled (no MAKECOM_PINTEREST_WEBHOOK)")
        if not self.youtube_enabled:
            print("Note: YouTube posting disabled (OAuth not configured)")

    def run(self) -> Dict:
        """Main entry point - post content to all platforms."""
        run_id = self.db.start_agent_run('multi_platform_poster', os.environ.get('GITHUB_RUN_ID'))

        results = {
            'total_posted': 0,
            'total_failed': 0,
            'posts': [],
            'errors': []
        }

        try:
            # Get active brands
            brands = self.db.get_active_brands()
            print(f"Processing {len(brands)} active brands")

            for brand in brands:
                brand_id = brand['id']
                brand_name = brand['name']
                print(f"\n--- {brand_name} ---")

                for platform in self.PLATFORMS:
                    if platform == 'pinterest' and not self.pinterest_enabled:
                        continue
                    if platform == 'youtube' and not self.youtube_enabled:
                        continue

                    try:
                        posted = self._post_to_platform(brand_id, brand_name, platform, results)
                        results['total_posted'] += posted
                    except Exception as e:
                        error_msg = f"{brand_name}/{platform}: {str(e)}"
                        results['errors'].append(error_msg)
                        print(f"Error: {error_msg}")

            self.db.complete_agent_run(
                run_id,
                status='completed',
                items_processed=results['total_posted'] + results['total_failed'],
                items_created=results['total_posted'],
                items_failed=results['total_failed']
            )

        except Exception as e:
            results['errors'].append(str(e))
            self.db.complete_agent_run(run_id, status='failed', error_log=[str(e)])
            send_alert("Multi-Platform Poster Failed", str(e), severity="error")
            raise

        print(f"\nPosting complete: {results['total_posted']} posted, {results['total_failed']} failed")
        return results

    def _post_to_platform(self, brand_id: str, brand_name: str, platform: str, results: Dict) -> int:
        """Post content to a specific platform."""
        # Check daily limit
        posts_today = self._get_posts_today(brand_id, platform)
        remaining = self.DAILY_LIMIT - posts_today

        if remaining <= 0:
            print(f"  {platform}: Daily limit reached ({self.DAILY_LIMIT})")
            return 0

        # Get content ready to post
        content_list = self.db.get_content_for_posting(brand_id, platform, limit=remaining)

        if not content_list:
            print(f"  {platform}: No content ready to post")
            return 0

        print(f"  {platform}: Found {len(content_list)} items, posting up to {remaining}")

        posted_count = 0
        for content in content_list[:remaining]:
            try:
                success = False
                post_url = None
                platform_post_id = None

                if platform == 'pinterest':
                    success, post_url, platform_post_id = self._post_to_pinterest(content, brand_name)
                elif platform == 'youtube':
                    success, post_url, platform_post_id = self._post_to_youtube(content, brand_name)

                if success:
                    # Log the post
                    post_record = {
                        'content_id': content['id'],
                        'brand_id': brand_id,
                        'platform': platform,
                        'platform_post_id': platform_post_id,
                        'post_url': post_url,
                        'status': 'posted',
                        'posted_at': datetime.utcnow().isoformat()
                    }
                    self.db.log_post(post_record)

                    # Update content status
                    self.db.update_content_status(content['id'], 'posted')

                    posted_count += 1
                    results['posts'].append({
                        'content_id': content['id'],
                        'platform': platform,
                        'url': post_url
                    })
                    print(f"    Posted: {content['title'][:40]}...")
                else:
                    results['total_failed'] += 1

            except Exception as e:
                results['errors'].append(f"{content['id']}: {str(e)}")
                results['total_failed'] += 1

        return posted_count

    def _get_posts_today(self, brand_id: str, platform: str) -> int:
        """Count posts made today for rate limiting."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        response = self.db.client.table('posts_log').select('id')\
            .eq('brand_id', brand_id)\
            .eq('platform', platform)\
            .eq('status', 'posted')\
            .gte('posted_at', today_start.isoformat())\
            .execute()

        return len(response.data) if response.data else 0

    def _post_to_pinterest(self, content: Dict, brand_name: str) -> tuple:
        """
        Trigger Make.com webhook to post to Pinterest.
        The existing Make.com scenario handles the actual posting.
        """
        if not self.pinterest_webhook:
            return False, None, None

        try:
            # Prepare payload for Make.com webhook
            payload = {
                'content_id': content['id'],
                'brand': brand_name,
                'title': content.get('title', ''),
                'description': content.get('description', ''),
                'link': content.get('source_url') or content.get('affiliate_link', ''),
                'image_url': content.get('image_url') or (content.get('source_images', [None])[0] if content.get('source_images') else None),
                'hashtags': content.get('hashtags', []),
                'board_name': content.get('pinterest_board', 'General')
            }

            response = requests.post(
                self.pinterest_webhook,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code in [200, 201, 202]:
                # Make.com accepted the webhook
                result = response.json() if response.text else {}
                return True, result.get('pin_url'), result.get('pin_id')
            else:
                print(f"    Pinterest webhook failed: {response.status_code}")
                return False, None, None

        except Exception as e:
            print(f"    Pinterest error: {e}")
            return False, None, None

    def _post_to_youtube(self, content: Dict, brand_name: str) -> tuple:
        """
        Post to YouTube Shorts using OAuth 2.0.
        Requires YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN.
        """
        if not self.youtube_enabled:
            return False, None, None

        # Check if we have a video URL
        videos = content.get('videos', [])
        if not videos:
            print(f"    YouTube: No video available for content")
            return False, None, None

        video_url = None
        for v in videos:
            if isinstance(v, dict) and v.get('output_url'):
                video_url = v['output_url']
                break

        if not video_url:
            print(f"    YouTube: No rendered video URL found")
            return False, None, None

        # Prepare video metadata
        title = content.get('title', 'Untitled')
        description = content.get('description', '')

        # Add hashtags to description
        hashtags = content.get('hashtags', [])
        if hashtags:
            description += '\n\n' + ' '.join([f'#{tag}' for tag in hashtags[:10]])

        # Add affiliate link if present
        affiliate_link = content.get('affiliate_link') or content.get('source_url')
        if affiliate_link:
            description += f'\n\nShop here: {affiliate_link}'

        # Upload using YouTube client
        print(f"    YouTube: Uploading video...")
        success, youtube_url, video_id = self.youtube_client.upload_short(
            video_url=video_url,
            title=title,
            description=description,
            tags=hashtags[:20] if hashtags else None
        )

        if success:
            print(f"    YouTube: Uploaded successfully - {youtube_url}")
        else:
            print(f"    YouTube: Upload failed")

        return success, youtube_url, video_id


class PinterestDirectPoster:
    """
    Alternative: Direct Pinterest API posting.
    Requires PINTEREST_ACCESS_TOKEN (OAuth token).
    """

    def __init__(self):
        self.access_token = os.environ.get('PINTEREST_ACCESS_TOKEN')
        self.api_url = "https://api.pinterest.com/v5"

    def create_pin(self, board_id: str, title: str, description: str,
                   link: str, image_url: str) -> Optional[Dict]:
        """Create a pin on Pinterest."""
        if not self.access_token:
            return None

        try:
            response = requests.post(
                f"{self.api_url}/pins",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "board_id": board_id,
                    "title": title,
                    "description": description,
                    "link": link,
                    "media_source": {
                        "source_type": "image_url",
                        "url": image_url
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Pinterest API error: {e}")
            return None


def main():
    """Entry point for GitHub Actions."""
    print(f"Starting Multi-Platform Poster at {datetime.utcnow().isoformat()}")

    poster = MultiPlatformPoster()
    results = poster.run()

    print(f"\nResults: {json.dumps(results, indent=2)}")
    return results


if __name__ == '__main__':
    main()
