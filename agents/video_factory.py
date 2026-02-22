"""
Agent 2: Video Factory
=======================
Runs daily at 8:00 AM after Blog Factory

Creates short-form videos using Creatomate API:
- Pulls pending video content from Supabase
- Renders videos using templates
- Polls for render completion
- Posts completed videos to Pinterest via Late API
- Saves video URLs back to database

Supports TikTok, Reels, and YouTube Shorts formats (9:16 vertical).
"""
import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient
from core.notifications import send_alert


# Brand-specific Late API and Pinterest configuration
BRAND_PINTEREST_CONFIG = {
    "daily_deal_darling": {
        "api_key_envs": ["LATE_API_KEY_DDD", "LATE_API_KEY_2", "LATE_API_KEY"],
        "account_id_env": "PINTEREST_DDD_ACCOUNT_ID",
        "account_id_env_alt": "PINTEREST_DEALS_ACCOUNT_ID",
        "board_id_env": "PINTEREST_DDD_BOARD_ID",
        "board_id_env_alt": "PINTEREST_DEALS_BOARD_ID",
        "link": "https://dailydealdarling.com",
        "hashtags": "#beautyfinds #skincare #beautytips #womensfashion #homedecor #giftsforher",
    },
    "fitnessmadeasy": {
        "api_key_envs": ["LATE_API_KEY", "LATE_API_KEY_3"],
        "account_id_env": "PINTEREST_FITNESS_ACCOUNT_ID",
        "account_id_env_alt": None,
        "board_id_env": "PINTEREST_FITNESS_BOARD_ID",
        "board_id_env_alt": None,
        "link": "https://fitnessmadeasy.com",
        "hashtags": "#fitover35 #metabolismboost #womenshealth #homeworkout #fitnessover40",
    },
    "menopause_planner": {
        "api_key_envs": ["LATE_API_KEY_MENO", "LATE_API_KEY_4", "LATE_API_KEY"],
        "account_id_env": "PINTEREST_MENO_ACCOUNT_ID",
        "account_id_env_alt": "PINTEREST_MENOPAUSE_ACCOUNT_ID",
        "board_id_env": "PINTEREST_MENO_BOARD_ID",
        "board_id_env_alt": "PINTEREST_MENOPAUSE_BOARD_ID",
        "link": "https://www.etsy.com/listing/4435219468/menopause-wellness-planner-bundle",
        "hashtags": "#menopause #menopauserelief #sleeptips #nightsweats #perimenopause",
    },
}


class VideoFactory:
    """Creates videos using Creatomate API."""

    def __init__(self):
        self.db = SupabaseClient()
        self.api_key = os.environ.get('CREATOMATE_API_KEY')
        self.base_url = "https://api.creatomate.com/v1"

        if not self.api_key:
            print("Warning: CREATOMATE_API_KEY not set - video creation disabled")
            self.enabled = False
        else:
            self.enabled = True

    def run(self) -> Dict:
        """Main entry point - create videos for pending content."""
        if not self.enabled:
            return {'status': 'disabled', 'reason': 'API key not configured'}

        run_id = self.db.start_agent_run('video_factory', os.environ.get('GITHUB_RUN_ID'))

        results = {
            'total_rendered': 0,
            'total_failed': 0,
            'videos': [],
            'errors': []
        }

        try:
            # Get pending video content
            try:
                pending = self.db.get_pending_videos(limit=10)  # Limit to avoid API costs
            except Exception as e:
                print(f"[video_factory] Database error fetching pending videos: {e}")
                pending = []
            print(f"Found {len(pending)} content pieces needing videos")

            if not pending:
                print("No video content to render")
                self.db.complete_agent_run(run_id, status='completed', items_processed=0)
                return results

            # Get templates
            templates = self._get_templates()
            if not templates:
                raise Exception("No video templates available")

            # Phase 1: Start all renders
            render_jobs = []
            for content in pending:
                try:
                    print(f"\nRendering: {content['title'][:50]}...")

                    # Select appropriate template
                    template = self._select_template(content, templates)
                    if not template:
                        print(f"  No suitable template found")
                        continue

                    # Start render
                    render_result = self._start_render(content, template)

                    if render_result.get('success'):
                        render_jobs.append({
                            'content': content,
                            'render_id': render_result['render_id']
                        })
                        print(f"  Render started: {render_result['render_id']}")
                    else:
                        results['total_failed'] += 1
                        results['errors'].append(render_result.get('error'))

                except Exception as e:
                    results['errors'].append(f"{content['id']}: {str(e)}")
                    results['total_failed'] += 1

            # Phase 2: Poll renders for completion and post to Pinterest
            if render_jobs:
                print(f"\nWaiting for {len(render_jobs)} renders to complete...")
                completed_videos = self._poll_renders(render_jobs)

                for video in completed_videos:
                    if video.get('video_url'):
                        results['total_rendered'] += 1
                        results['videos'].append({
                            'content_id': video['content']['id'],
                            'render_id': video['render_id'],
                            'video_url': video['video_url']
                        })

                        # Update content status
                        try:
                            self.db.update_content_status(video['content']['id'], 'video_ready')
                        except Exception as e:
                            print(f"[video_factory] Database error updating content status: {e}")

                        # Post to Pinterest via Late API
                        post_result = self._post_to_pinterest(video)
                        if post_result.get('success'):
                            results['videos'][-1]['pinterest_post_id'] = post_result.get('post_id')
                            print(f"  Posted to Pinterest: {post_result.get('post_id')}")
                            try:
                                self.db.update_content_status(video['content']['id'], 'posted')
                            except Exception as e:
                                print(f"[video_factory] Database error updating post status: {e}")
                        else:
                            print(f"  Pinterest posting failed: {post_result.get('error')}")
                            results['errors'].append(f"Pinterest: {post_result.get('error')}")
                    else:
                        results['total_failed'] += 1
                        results['errors'].append(f"Render failed: {video.get('error', 'unknown')}")

            self.db.complete_agent_run(
                run_id,
                status='completed',
                items_processed=len(pending),
                items_created=results['total_rendered'],
                items_failed=results['total_failed']
            )

        except Exception as e:
            results['errors'].append(str(e))
            self.db.complete_agent_run(run_id, status='failed', error_log=[str(e)])
            send_alert("Video Factory Failed", str(e), severity="error")
            raise

        print(f"\nVideo Factory complete: {results['total_rendered']} rendered, {results['total_failed']} failed")
        return results

    def _get_templates(self) -> List[Dict]:
        """Get available templates from Creatomate."""
        try:
            response = requests.get(
                f"{self.base_url}/templates",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching templates: {e}")
            return []

    def _select_template(self, content: Dict, templates: List[Dict]) -> Optional[Dict]:
        """Select the best template for this content."""
        content_type = content.get('content_type', 'video')

        # Filter by format (9:16 for shorts)
        vertical_templates = [
            t for t in templates
            if t.get('height', 0) > t.get('width', 0)  # Vertical
        ]

        if vertical_templates:
            return vertical_templates[0]

        return templates[0] if templates else None

    def _start_render(self, content: Dict, template: Dict) -> Dict:
        """Start a video render using Creatomate."""
        try:
            # Build modifications based on content
            modifications = self._build_modifications(content)

            render_data = {
                "template_id": template['id'],
                "modifications": modifications
            }

            response = requests.post(
                f"{self.base_url}/renders",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=render_data,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            # Save video record
            video_record = {
                'content_id': content['id'],
                'creatomate_render_id': result[0]['id'] if isinstance(result, list) else result['id'],
                'status': 'rendering',
                'width': template.get('width', 1080),
                'height': template.get('height', 1920)
            }
            try:
                self.db.save_video(video_record)
            except Exception as e:
                print(f"[video_factory] Database error saving video record: {e}")

            return {
                'success': True,
                'render_id': video_record['creatomate_render_id']
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _poll_renders(self, render_jobs: List[Dict], max_wait: int = 600, interval: int = 15) -> List[Dict]:
        """Poll Creatomate for render completion.

        Args:
            render_jobs: List of {'content': ..., 'render_id': ...} dicts
            max_wait: Maximum seconds to wait (default 10 minutes)
            interval: Seconds between polls (default 15)

        Returns:
            List of completed render dicts with video_url added
        """
        completed = []
        remaining = list(render_jobs)
        elapsed = 0

        while remaining and elapsed < max_wait:
            time.sleep(interval)
            elapsed += interval

            still_pending = []
            for job in remaining:
                try:
                    response = requests.get(
                        f"{self.base_url}/renders/{job['render_id']}",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        timeout=30
                    )
                    response.raise_for_status()
                    render = response.json()
                    status = render.get('status', '')

                    if status == 'succeeded':
                        video_url = render.get('url', '')
                        print(f"  Render {job['render_id'][:12]}... completed: {video_url[:80]}")
                        job['video_url'] = video_url
                        completed.append(job)

                        # Update video record in database
                        try:
                            self.db.client.table('videos').update({
                                'status': 'completed',
                                'video_url': video_url
                            }).eq('creatomate_render_id', job['render_id']).execute()
                        except Exception as e:
                            print(f"  DB update error: {e}")

                    elif status == 'failed':
                        error = render.get('error_message', 'Render failed')
                        print(f"  Render {job['render_id'][:12]}... failed: {error}")
                        job['error'] = error
                        completed.append(job)
                    else:
                        still_pending.append(job)

                except Exception as e:
                    print(f"  Error polling render {job['render_id'][:12]}...: {e}")
                    still_pending.append(job)

            remaining = still_pending
            if remaining:
                print(f"  {len(remaining)} renders still pending ({elapsed}s elapsed)...")

        # Mark timed-out renders as failed
        for job in remaining:
            job['error'] = f'Render timed out after {max_wait}s'
            completed.append(job)

        return completed

    def _post_to_pinterest(self, video: Dict) -> Dict:
        """Post a rendered video to Pinterest via Late API.

        Args:
            video: Dict with 'content', 'video_url', and 'render_id'

        Returns:
            Result dict with success status
        """
        content = video['content']
        video_url = video.get('video_url')
        if not video_url:
            return {'success': False, 'error': 'No video URL'}

        brand = content.get('brand', '')
        config = BRAND_PINTEREST_CONFIG.get(brand)
        if not config:
            print(f"  No Pinterest config for brand: {brand}")
            return {'success': False, 'error': f'No Pinterest config for brand: {brand}'}

        # Find a working Late API key
        late_key = None
        for key_env in config['api_key_envs']:
            late_key = os.environ.get(key_env)
            if late_key:
                break
        if not late_key:
            return {'success': False, 'error': f'No Late API key found (tried: {config["api_key_envs"]})'}

        # Get account and board IDs (try primary env var, then alt)
        account_id = os.environ.get(config['account_id_env'], '')
        if not account_id and config.get('account_id_env_alt'):
            account_id = os.environ.get(config['account_id_env_alt'], '')

        board_id = os.environ.get(config['board_id_env'], '')
        if not board_id and config.get('board_id_env_alt'):
            board_id = os.environ.get(config['board_id_env_alt'], '')

        # Auto-detect account ID if not set
        if not account_id:
            try:
                acct_resp = requests.get(
                    'https://getlate.dev/api/v1/accounts',
                    headers={'Authorization': f'Bearer {late_key}'},
                    timeout=15
                )
                acct_resp.raise_for_status()
                accounts = acct_resp.json()
                if isinstance(accounts, dict):
                    accounts = accounts.get('accounts', accounts.get('data', []))
                for acct in accounts:
                    if acct.get('platform') == 'pinterest':
                        account_id = acct.get('_id') or acct.get('id')
                        break
            except Exception as e:
                return {'success': False, 'error': f'Failed to detect Pinterest account: {e}'}

        if not account_id:
            return {'success': False, 'error': 'No Pinterest account ID found'}

        # Build description with hashtags
        title = content.get('title', '')
        description = content.get('description', '')
        hashtags = config.get('hashtags', '')
        content_text = f"{title}\n\n{description}\n\n{hashtags}"

        # Build Late API payload
        platform_data = {
            'platform': 'pinterest',
            'accountId': account_id,
            'platformSpecificData': {
                'link': config['link'],
            }
        }
        if board_id:
            platform_data['platformSpecificData']['boardId'] = board_id

        payload = {
            'content': content_text,
            'platforms': [platform_data],
            'mediaItems': [{'type': 'video', 'url': video_url}],
        }

        try:
            response = requests.post(
                'https://getlate.dev/api/v1/posts',
                headers={
                    'Authorization': f'Bearer {late_key}',
                    'Content-Type': 'application/json'
                },
                json=payload,
                timeout=120
            )

            if response.status_code < 400:
                result = response.json()
                post = result.get('post', result)
                post_id = post.get('_id', '')
                print(f"  Pinterest video posted: {post_id}")

                # Log to posts_log
                try:
                    self.db.log_post({
                        'brand': brand,
                        'platform': 'pinterest',
                        'content_id': content.get('id'),
                        'platform_post_id': post_id,
                        'video_url': video_url,
                        'status': 'posted',
                        'posted_at': datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    print(f"  DB log error: {e}")

                return {'success': True, 'post_id': post_id}
            else:
                error_text = response.text[:300]
                print(f"  Late API error {response.status_code}: {error_text}")
                return {'success': False, 'error': f'Late API {response.status_code}: {error_text}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _build_modifications(self, content: Dict) -> Dict:
        """Build template modifications from content."""
        # Map content fields to common template variable names
        modifications = {}

        if content.get('title'):
            modifications['Title'] = content['title']
            modifications['title'] = content['title']
            modifications['Headline'] = content['title']

        if content.get('description'):
            modifications['Description'] = content['description'][:150]
            modifications['description'] = content['description'][:150]

        if content.get('cta_text'):
            modifications['CTA'] = content['cta_text']
            modifications['cta'] = content['cta_text']
            modifications['Call To Action'] = content['cta_text']

        # Add any source images
        if content.get('source_images'):
            for i, img in enumerate(content['source_images'][:5]):
                modifications[f'Image-{i+1}'] = img
                modifications[f'image_{i+1}'] = img

        return modifications


def main():
    """Entry point for GitHub Actions."""
    print(f"Starting Video Factory at {datetime.utcnow().isoformat()}")

    factory = VideoFactory()
    results = factory.run()

    print(f"\nResults: {json.dumps(results, indent=2)}")
    return results


if __name__ == '__main__':
    main()
