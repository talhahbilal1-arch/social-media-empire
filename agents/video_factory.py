"""
Agent 2: Video Factory
=======================
Runs daily at 8:00 AM after Blog Factory

Creates short-form videos using Creatomate API:
- Pulls pending video content from Supabase
- Renders videos using templates
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

                    # Start render
                    render_result = self._start_render(content, template)

                    if render_result.get('success'):
                        results['total_rendered'] += 1
                        results['videos'].append({
                            'content_id': content['id'],
                            'render_id': render_result['render_id']
                        })
                        print(f"  Render started: {render_result['render_id']}")

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
            self.db.save_video(video_record)

            return {
                'success': True,
                'render_id': video_record['creatomate_render_id']
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


def main():
    """Entry point for GitHub Actions."""
    print(f"Starting Video Factory at {datetime.utcnow().isoformat()}")

    factory = VideoFactory()
    results = factory.run()

    print(f"\nResults: {json.dumps(results, indent=2)}")
    return results


if __name__ == '__main__':
    main()
