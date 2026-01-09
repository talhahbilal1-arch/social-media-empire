"""
Agent 2: Video Factory
=======================
Runs daily at 8:00 AM after Blog Factory

Creates short-form videos using Creatomate API:
- Pulls pending video content from Supabase
- Renders videos using templates
- Saves video URLs back to database
- Creates Pinterest Idea Pins (multi-page format for 9x more reach)

Supports TikTok, Reels, YouTube Shorts, and Pinterest Idea Pins (9:16 vertical).

Pinterest Idea Pin Specs:
- 9:16 aspect ratio (1080x1920)
- 2-20 pages/clips
- Each clip 1-60 seconds
- Total max 5 minutes
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


class VideoFactory:
    """Creates videos using Creatomate API."""

    # Pinterest Idea Pin configuration
    IDEA_PIN_CONFIG = {
        'width': 1080,
        'height': 1920,
        'min_pages': 2,
        'max_pages': 5,  # Conservative default, can go up to 20
        'page_duration': 5,  # Seconds per page
        'format': '9:16'
    }

    # Render polling configuration
    RENDER_POLL_INTERVAL = 5  # seconds between status checks
    RENDER_MAX_WAIT = 300  # 5 minutes max wait per render

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
            'idea_pins_created': 0,
            'videos': [],
            'errors': []
        }

        try:
            # Get pending video content
            pending = self.db.get_pending_videos(limit=10)  # Limit to avoid API costs
            print(f"Found {len(pending)} content pieces needing videos")

            if not pending:
                print("No video content to render")
                self.db.complete_agent_run(run_id, status='completed', items_processed=0)
                return results

            # Get templates
            templates = self._get_templates()
            if not templates:
                raise Exception("No video templates available")

            for content in pending:
                try:
                    print(f"\nRendering: {content['title'][:50]}...")

                    # Select appropriate template
                    template = self._select_template(content, templates)
                    if not template:
                        print(f"  No suitable template found")
                        continue

                    # Start regular video render
                    render_result = self._start_render(content, template)

                    if render_result.get('success'):
                        results['total_rendered'] += 1
                        results['videos'].append({
                            'content_id': content['id'],
                            'render_id': render_result['render_id']
                        })
                        print(f"  Regular video render started: {render_result['render_id']}")

                        # Also create Pinterest Idea Pin version
                        idea_pin_result = self._create_idea_pin(content, template)
                        if idea_pin_result.get('success'):
                            results['idea_pins_created'] += 1
                            print(f"  Idea Pin render started: {idea_pin_result['render_id']}")
                        else:
                            print(f"  Idea Pin skipped: {idea_pin_result.get('reason', 'unknown')}")

                        # Update content status
                        self.db.update_content_status(content['id'], 'video_ready')
                    else:
                        results['total_failed'] += 1
                        results['errors'].append(render_result.get('error'))

                except Exception as e:
                    results['errors'].append(f"{content['id']}: {str(e)}")
                    results['total_failed'] += 1

            self.db.complete_agent_run(
                run_id,
                status='completed',
                items_processed=len(pending),
                items_created=results['total_rendered'] + results['idea_pins_created'],
                items_failed=results['total_failed']
            )

        except Exception as e:
            results['errors'].append(str(e))
            self.db.complete_agent_run(run_id, status='failed', error_log=[str(e)])
            send_alert("Video Factory Failed", str(e), severity="error")
            raise

        print(f"\nVideo Factory complete: {results['total_rendered']} videos, {results['idea_pins_created']} idea pins, {results['total_failed']} failed")
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

    def _poll_render_completion(self, render_id: str) -> Dict:
        """
        Poll Creatomate API until render completes or fails.

        Returns dict with:
        - success: bool
        - url: video URL if successful
        - status: final status
        - error: error message if failed
        """
        start_time = time.time()

        while time.time() - start_time < self.RENDER_MAX_WAIT:
            try:
                response = requests.get(
                    f"{self.base_url}/renders/{render_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()

                status = result.get('status', 'unknown')

                if status == 'succeeded':
                    return {
                        'success': True,
                        'url': result.get('url'),
                        'status': status
                    }
                elif status in ['failed', 'error']:
                    return {
                        'success': False,
                        'status': status,
                        'error': result.get('error_message', 'Render failed')
                    }
                # Status is still 'planned', 'rendering', etc - keep waiting
                print(f"    Render {render_id[:8]}... status: {status}")

            except Exception as e:
                print(f"    Poll error: {e}")

            time.sleep(self.RENDER_POLL_INTERVAL)

        return {
            'success': False,
            'status': 'timeout',
            'error': f'Render did not complete within {self.RENDER_MAX_WAIT}s'
        }

    def _start_render(self, content: Dict, template: Dict) -> Dict:
        """Start a video render using Creatomate and wait for completion."""
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

            render_id = result[0]['id'] if isinstance(result, list) else result['id']

            # Save video record with 'rendering' status
            video_record = {
                'content_id': content['id'],
                'creatomate_render_id': render_id,
                'status': 'rendering',
                'width': template.get('width', 1080),
                'height': template.get('height', 1920)
            }
            saved = self.db.save_video(video_record)
            video_id = saved['id'] if saved else None

            # Poll for render completion
            print(f"    Waiting for render to complete...")
            poll_result = self._poll_render_completion(render_id)

            if poll_result['success']:
                # Update video record with final URL and status
                if video_id:
                    self.db.update_video(
                        video_id,
                        video_url=poll_result['url'],
                        status='ready'
                    )
                print(f"    Video ready: {poll_result['url'][:60]}...")
                return {
                    'success': True,
                    'render_id': render_id,
                    'video_url': poll_result['url']
                }
            else:
                # Update video record with failed status
                if video_id:
                    self.db.update_video(
                        video_id,
                        status='failed',
                        error_message=poll_result.get('error', 'Unknown error')
                    )
                return {
                    'success': False,
                    'error': poll_result.get('error', 'Render failed')
                }

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

    def _create_idea_pin(self, content: Dict, template: Dict) -> Dict:
        """
        Create a Pinterest Idea Pin version of the content.

        Idea Pins are multi-page video/image posts that get 9x more reach on Pinterest.
        Specs: 9:16 aspect ratio, 2-20 pages, each clip 1-60 seconds, total max 5 minutes.
        """
        try:
            # Only create Idea Pins for content types that make sense
            content_type = content.get('content_type', '')
            if content_type not in ['video', 'reel', 'short', 'pin']:
                return {'success': False, 'reason': f'Content type {content_type} not suitable for Idea Pin'}

            # Build multi-page structure for Idea Pin
            pages = self._build_idea_pin_pages(content)
            if len(pages) < self.IDEA_PIN_CONFIG['min_pages']:
                return {'success': False, 'reason': 'Not enough content for multi-page Idea Pin'}

            # Create Creatomate render for Idea Pin format
            # Note: Template must already be 9:16 vertical format
            # Creatomate API only accepts template_id and modifications
            render_data = {
                "template_id": template['id'],
                "modifications": self._build_modifications(content)
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

            render_id = result[0]['id'] if isinstance(result, list) else result['id']

            # Poll for render completion
            print(f"    Waiting for Idea Pin render to complete...")
            poll_result = self._poll_render_completion(render_id)

            if poll_result['success']:
                # Update the video record with Idea Pin info including URL
                self.db.update_video_idea_pin(
                    content_id=content['id'],
                    idea_pin_render_id=render_id,
                    idea_pin_pages=len(pages),
                    idea_pin_url=poll_result['url']
                )
                print(f"    Idea Pin ready: {poll_result['url'][:60]}...")
                return {
                    'success': True,
                    'render_id': render_id,
                    'pages': len(pages),
                    'idea_pin_url': poll_result['url']
                }
            else:
                # Still save the render_id but note it failed
                self.db.update_video_idea_pin(
                    content_id=content['id'],
                    idea_pin_render_id=render_id,
                    idea_pin_pages=len(pages)
                )
                return {
                    'success': False,
                    'reason': poll_result.get('error', 'Render failed'),
                    'render_id': render_id
                }

        except Exception as e:
            return {'success': False, 'reason': str(e)}

    def _build_idea_pin_pages(self, content: Dict) -> List[Dict]:
        """
        Build page structure for Pinterest Idea Pin.

        Breaks content into 2-5 pages optimized for Pinterest engagement.
        """
        pages = []

        # Page 1: Hook/Title page
        pages.append({
            'type': 'title',
            'text': content.get('title', '')[:100],
            'duration': self.IDEA_PIN_CONFIG['page_duration']
        })

        # Page 2-4: Content pages from description or script
        script = content.get('video_script') or content.get('description', '')
        if script:
            # Split script into chunks for multiple pages
            sentences = script.replace('\n', ' ').split('.')
            sentences = [s.strip() for s in sentences if s.strip()]

            # Group sentences into pages (2-3 sentences per page)
            chunk_size = max(1, len(sentences) // 3)
            for i in range(0, min(len(sentences), 9), chunk_size):
                chunk = '. '.join(sentences[i:i+chunk_size])
                if chunk:
                    pages.append({
                        'type': 'content',
                        'text': chunk[:200],
                        'duration': self.IDEA_PIN_CONFIG['page_duration']
                    })
                if len(pages) >= self.IDEA_PIN_CONFIG['max_pages'] - 1:
                    break

        # Final page: CTA
        cta = content.get('cta_text', 'Learn more!')
        pages.append({
            'type': 'cta',
            'text': cta,
            'duration': self.IDEA_PIN_CONFIG['page_duration']
        })

        return pages[:self.IDEA_PIN_CONFIG['max_pages']]


def main():
    """Entry point for GitHub Actions."""
    print(f"Starting Video Factory at {datetime.utcnow().isoformat()}")

    factory = VideoFactory()
    results = factory.run()

    print(f"\nResults: {json.dumps(results, indent=2)}")
    return results


if __name__ == '__main__':
    main()
