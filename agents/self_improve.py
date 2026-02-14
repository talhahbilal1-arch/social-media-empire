"""
Agent 5: Self-Improvement Engine
=================================
Runs weekly on Sundays to analyze and optimize the system

Analyzes:
- Content performance patterns
- Optimal posting times
- Best performing topics and formats
- Underperforming content to retire

Automatically updates:
- Content Brain prompts and preferences
- Posting schedules
- Winning patterns database

Logs all changes for audit trail.
"""
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient
from core.claude_client import ClaudeClient
from core.notifications import send_alert


class SelfImprovementEngine:
    """Analyzes performance and optimizes the content system."""

    def __init__(self):
        self.db = SupabaseClient()
        self.claude = ClaudeClient()

    def run(self) -> Dict:
        """Main entry point - analyze and optimize for all brands."""
        run_id = self.db.start_agent_run('self_improve', os.environ.get('GITHUB_RUN_ID'))

        results = {
            'brands_analyzed': 0,
            'patterns_updated': 0,
            'configs_updated': 0,
            'changes': [],
            'errors': []
        }

        try:
            brands = self.db.get_active_brands()
            print(f"Analyzing {len(brands)} brands...")

            for brand in brands:
                print(f"\n{'='*50}")
                print(f"Analyzing: {brand['display_name']}")
                print(f"{'='*50}")

                brand_results = self._analyze_brand(brand)

                results['brands_analyzed'] += 1
                results['patterns_updated'] += brand_results.get('patterns_updated', 0)
                results['configs_updated'] += brand_results.get('configs_updated', 0)
                results['changes'].extend(brand_results.get('changes', []))
                results['errors'].extend(brand_results.get('errors', []))

            self.db.complete_agent_run(
                run_id,
                status='completed',
                items_processed=len(brands),
                items_created=results['patterns_updated']
            )

            # Send summary if significant changes
            if results['changes']:
                self._send_summary(results)

        except Exception as e:
            results['errors'].append(str(e))
            self.db.complete_agent_run(run_id, status='failed', error_log=[str(e)])
            send_alert("Self-Improvement Failed", str(e), severity="error")
            raise

        print(f"\nSelf-improvement complete: {results['patterns_updated']} patterns updated")
        return results

    def _analyze_brand(self, brand: Dict) -> Dict:
        """Analyze and optimize a single brand."""
        brand_id = brand['id']

        results = {
            'patterns_updated': 0,
            'configs_updated': 0,
            'changes': [],
            'errors': []
        }

        # Collect analytics data from last 30 days
        analytics_data = self._get_analytics_data(brand_id, days=30)
        print(f"  Collected {len(analytics_data)} analytics records")

        if len(analytics_data) < 10:
            print("  Not enough data for analysis (need at least 10 records)")
            return results

        # Get current patterns
        current_patterns = self.db.get_winning_patterns(brand_id)

        # Analyze with Claude
        try:
            analysis = self.claude.analyze_performance(analytics_data, current_patterns)
            print(f"  Analysis complete")
        except Exception as e:
            results['errors'].append(f"Analysis failed: {str(e)}")
            return results

        # Process new patterns
        for pattern in analysis.get('new_patterns', []):
            try:
                pattern_record = {
                    'brand_id': brand_id,
                    'pattern_type': pattern['pattern_type'],
                    'pattern_value': pattern['pattern_value'],
                    'avg_engagement': pattern.get('confidence', 0.5),
                    'sample_size': 1,
                    'confidence_score': pattern.get('confidence', 0.5),
                    'is_active': True
                }
                self.db.upsert_pattern(pattern_record)
                results['patterns_updated'] += 1

                # Log the change
                change = {
                    'agent_name': 'self_improve',
                    'brand_id': brand_id,
                    'change_type': 'pattern_added',
                    'new_value': pattern,
                    'reason': pattern.get('reason', 'Performance analysis')
                }
                self.db.log_system_change(change)
                results['changes'].append(change)

                print(f"    Added pattern: {pattern['pattern_type']} = {pattern['pattern_value']}")

            except Exception as e:
                results['errors'].append(f"Pattern update failed: {str(e)}")

        # Process patterns to retire
        for retire in analysis.get('retire_patterns', []):
            try:
                # Find and deactivate the pattern
                for p in current_patterns:
                    if (p['pattern_type'] == retire['pattern_type'] and
                        p['pattern_value'] == retire['pattern_value']):
                        self.db.upsert_pattern({
                            **p,
                            'is_active': False
                        })

                        change = {
                            'agent_name': 'self_improve',
                            'brand_id': brand_id,
                            'change_type': 'pattern_retired',
                            'old_value': p,
                            'reason': retire.get('reason', 'Underperforming')
                        }
                        self.db.log_system_change(change)
                        results['changes'].append(change)

                        print(f"    Retired pattern: {retire['pattern_type']} = {retire['pattern_value']}")
                        break

            except Exception as e:
                results['errors'].append(f"Pattern retirement failed: {str(e)}")

        # Process schedule changes
        for schedule_change in analysis.get('schedule_changes', []):
            try:
                current_config = self.db.get_config(brand_id, 'posting_schedule') or {}

                platform = schedule_change['platform']
                old_time = schedule_change.get('current_time')
                new_time = schedule_change['suggested_time']

                if platform in current_config:
                    old_times = current_config[platform].get('times', [])
                    if old_time in old_times:
                        old_times.remove(old_time)
                        old_times.append(new_time)
                        old_times.sort()
                        current_config[platform]['times'] = old_times

                        self.db.update_config(
                            brand_id,
                            'posting_schedule',
                            current_config,
                            updated_by='self_improve'
                        )
                        results['configs_updated'] += 1

                        change = {
                            'agent_name': 'self_improve',
                            'brand_id': brand_id,
                            'change_type': 'schedule_updated',
                            'config_key': 'posting_schedule',
                            'old_value': {'time': old_time},
                            'new_value': {'time': new_time},
                            'reason': schedule_change.get('reason', 'Optimization')
                        }
                        self.db.log_system_change(change)
                        results['changes'].append(change)

                        print(f"    Updated {platform} schedule: {old_time} -> {new_time}")

            except Exception as e:
                results['errors'].append(f"Schedule update failed: {str(e)}")

        # Log recommendations for manual review
        for rec in analysis.get('content_recommendations', []):
            print(f"    Recommendation: [{rec.get('priority', 'medium')}] {rec.get('recommendation')}")

        return results

    def _get_analytics_data(self, brand_id: str, days: int = 30) -> List[Dict]:
        """Get analytics data for analysis."""
        # This would join analytics with content_bank to get full picture
        # For MVP, get recent analytics and enrich with content data

        analytics = []

        # Get posts for this brand
        posts = self.db.get_posts_for_analytics(hours_ago=days * 24)

        for post in posts:
            post_analytics = self.db.client.table('analytics').select('*')\
                .eq('post_id', post['id'])\
                .order('recorded_at', desc=True)\
                .limit(1)\
                .execute()

            if post_analytics.data:
                latest = post_analytics.data[0]

                # Get content details
                content = self.db.client.table('content_bank').select('*')\
                    .eq('id', post.get('content_id'))\
                    .single()\
                    .execute()

                if content.data:
                    analytics.append({
                        'post_id': post['id'],
                        'platform': post['platform'],
                        'content_type': content.data.get('content_type'),
                        'title': content.data.get('title'),
                        'hashtags': content.data.get('hashtags', []),
                        'posted_at': post.get('posted_at'),
                        **latest
                    })

        return analytics

    def _send_summary(self, results: Dict) -> None:
        """Send summary of changes made."""
        changes_text = "\n".join([
            f"- {c['change_type']}: {c.get('reason', 'N/A')}"
            for c in results['changes'][:10]
        ])

        message = f"""Weekly self-improvement analysis complete.

Changes Made:
{changes_text}

Patterns Updated: {results['patterns_updated']}
Configs Updated: {results['configs_updated']}

Review the system_changes table for full details.
"""

        send_alert(
            subject="Weekly Optimization Complete",
            message=message,
            severity="info"
        )


def main():
    """Entry point for GitHub Actions."""
    print(f"Starting Self-Improvement Engine at {datetime.utcnow().isoformat()}")

    engine = SelfImprovementEngine()
    results = engine.run()

    print(f"\nResults: {json.dumps(results, indent=2)}")
    return results


if __name__ == '__main__':
    main()
