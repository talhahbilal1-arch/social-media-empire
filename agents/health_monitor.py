"""
Agent 6: Health Monitor
========================
Runs hourly to check system health.

Monitors:
- All agent execution status
- API connections (Claude, Supabase, video API, social platforms)
- Database health
- Content pipeline status

Sends email alert ONLY when something is wrong.
Silence = everything is working.
"""
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient
from core.notifications import send_alert, should_send_alert, send_critical_alert


class HealthMonitor:
    """System health monitoring and alerting."""

    # Expected agent schedules (for detecting missed runs)
    AGENT_SCHEDULES = {
        'trend_discovery': {'hour': 6, 'frequency': 'daily'},
        'content_brain': {'hour': 6, 'frequency': 'daily'},
        'blog_factory': {'hour': 7, 'frequency': 'daily'},
        'video_factory': {'hour': 8, 'frequency': 'daily'},
        'multi_platform_poster': {'hours': [0, 14, 19], 'frequency': 'daily'},
        'analytics_collector': {'hour': 23, 'frequency': 'daily'},
        'self_improve': {'day': 6, 'frequency': 'weekly'}  # Sunday
    }

    # Thresholds for alerts
    THRESHOLDS = {
        'max_failures_before_alert': 2,  # Alert after N consecutive failures
        'max_hours_without_content': 48,  # Alert if no content for N hours
        'min_pending_content': 5,  # Alert if pipeline running low
        'max_api_response_time_ms': 5000,  # Alert if APIs slow
    }

    def __init__(self):
        self.db = SupabaseClient()
        self.issues: List[Dict] = []
        self.warnings: List[Dict] = []

    def run(self) -> Dict:
        """Run all health checks."""
        print(f"Running health check at {datetime.utcnow().isoformat()}")

        results = {
            'status': 'healthy',
            'checks_run': 0,
            'issues': [],
            'warnings': [],
            'details': {}
        }

        # Run all checks
        checks = [
            ('agent_runs', self._check_agent_runs),
            ('api_connections', self._check_api_connections),
            ('content_pipeline', self._check_content_pipeline),
            ('database_health', self._check_database_health),
        ]

        for check_name, check_func in checks:
            try:
                print(f"  Running: {check_name}")
                check_result = check_func()
                results['details'][check_name] = check_result
                results['checks_run'] += 1
            except Exception as e:
                self.issues.append({
                    'check': check_name,
                    'severity': 'error',
                    'message': f"Check failed: {str(e)}"
                })

        # Compile results
        results['issues'] = self.issues
        results['warnings'] = self.warnings

        if self.issues:
            results['status'] = 'unhealthy'
        elif self.warnings:
            results['status'] = 'degraded'

        # Log the health check
        self._log_health_check(results)

        # Send alert if there are issues
        if self.issues:
            self._send_alert(results)

        print(f"\nHealth check complete: {results['status']}")
        print(f"  Issues: {len(self.issues)}, Warnings: {len(self.warnings)}")

        return results

    def _check_agent_runs(self) -> Dict:
        """Check if all agents ran successfully on schedule."""
        result = {'agents': {}, 'missed_runs': [], 'failed_runs': []}
        now = datetime.utcnow()

        for agent_name, schedule in self.AGENT_SCHEDULES.items():
            # Get last run
            last_run = self.db.get_last_agent_run(agent_name)

            if not last_run:
                result['agents'][agent_name] = {'status': 'never_run'}
                self.warnings.append({
                    'check': 'agent_runs',
                    'agent': agent_name,
                    'message': f"{agent_name} has never run"
                })
                continue

            last_run_time = datetime.fromisoformat(last_run['started_at'].replace('Z', '+00:00')).replace(tzinfo=None)
            hours_since = (now - last_run_time).total_seconds() / 3600

            result['agents'][agent_name] = {
                'last_run': last_run['started_at'],
                'status': last_run['status'],
                'hours_since': round(hours_since, 1)
            }

            # Check for failures
            if last_run['status'] == 'failed':
                result['failed_runs'].append(agent_name)
                self.issues.append({
                    'check': 'agent_runs',
                    'severity': 'error',
                    'agent': agent_name,
                    'message': f"{agent_name} failed. Error: {last_run.get('error_log', ['Unknown'])[0] if last_run.get('error_log') else 'Unknown'}"
                })

            # Check for missed runs (daily agents should run within 26 hours)
            if schedule.get('frequency') == 'daily' and hours_since > 26:
                result['missed_runs'].append(agent_name)
                self.warnings.append({
                    'check': 'agent_runs',
                    'agent': agent_name,
                    'message': f"{agent_name} hasn't run in {round(hours_since)} hours"
                })

        return result

    def _check_api_connections(self) -> Dict:
        """Check all external API connections."""
        result = {'apis': {}}

        # Check Supabase (already connected via self.db)
        try:
            start = datetime.utcnow()
            brands = self.db.get_active_brands()
            duration = (datetime.utcnow() - start).total_seconds() * 1000
            result['apis']['supabase'] = {
                'status': 'connected',
                'response_time_ms': round(duration),
                'brands_found': len(brands)
            }
            if duration > self.THRESHOLDS['max_api_response_time_ms']:
                self.warnings.append({
                    'check': 'api_connections',
                    'api': 'supabase',
                    'message': f"Supabase slow: {round(duration)}ms"
                })
        except Exception as e:
            result['apis']['supabase'] = {'status': 'error', 'error': str(e)}
            self.issues.append({
                'check': 'api_connections',
                'severity': 'critical',
                'api': 'supabase',
                'message': f"Supabase connection failed: {str(e)}"
            })

        # Check Claude API
        claude_api_key = os.environ.get('ANTHROPIC_API_KEY')
        if claude_api_key:
            try:
                start = datetime.utcnow()
                # Just check if we can reach the API
                response = requests.get(
                    "https://api.anthropic.com/v1/messages",
                    headers={"x-api-key": claude_api_key, "anthropic-version": "2023-06-01"},
                    timeout=10
                )
                duration = (datetime.utcnow() - start).total_seconds() * 1000
                # 401 is expected for GET, 405 means server is responding
                result['apis']['claude'] = {
                    'status': 'connected' if response.status_code in [401, 405] else 'unknown',
                    'response_time_ms': round(duration),
                    'http_status': response.status_code
                }
            except Exception as e:
                result['apis']['claude'] = {'status': 'error', 'error': str(e)}
                self.issues.append({
                    'check': 'api_connections',
                    'severity': 'error',
                    'api': 'claude',
                    'message': f"Claude API unreachable: {str(e)}"
                })
        else:
            result['apis']['claude'] = {'status': 'not_configured'}

        # Check Creatomate (video API)
        creatomate_key = os.environ.get('CREATOMATE_API_KEY')
        if creatomate_key:
            try:
                response = requests.get(
                    "https://api.creatomate.com/v1/templates",
                    headers={"Authorization": f"Bearer {creatomate_key}"},
                    timeout=10
                )
                result['apis']['creatomate'] = {
                    'status': 'connected' if response.status_code == 200 else 'error',
                    'http_status': response.status_code
                }
            except Exception as e:
                result['apis']['creatomate'] = {'status': 'error', 'error': str(e)}
        else:
            result['apis']['creatomate'] = {'status': 'not_configured'}

        # Check Netlify
        netlify_token = os.environ.get('NETLIFY_API_TOKEN')
        if netlify_token:
            try:
                response = requests.get(
                    "https://api.netlify.com/api/v1/sites",
                    headers={"Authorization": f"Bearer {netlify_token}"},
                    timeout=10
                )
                result['apis']['netlify'] = {
                    'status': 'connected' if response.status_code == 200 else 'error',
                    'http_status': response.status_code
                }
            except Exception as e:
                result['apis']['netlify'] = {'status': 'error', 'error': str(e)}
        else:
            result['apis']['netlify'] = {'status': 'not_configured'}

        return result

    def _check_content_pipeline(self) -> Dict:
        """Check content generation and posting pipeline health."""
        result = {'brands': {}}

        brands = self.db.get_active_brands()

        for brand in brands:
            brand_id = brand['id']
            brand_name = brand['name']

            brand_result = {}

            # Check pending content count
            pending = self.db.get_pending_content(brand_id, limit=100)
            brand_result['pending_content'] = len(pending)

            if len(pending) < self.THRESHOLDS['min_pending_content']:
                self.warnings.append({
                    'check': 'content_pipeline',
                    'brand': brand_name,
                    'message': f"Low content inventory: {len(pending)} pieces pending"
                })

            # Check recent posts
            recent_posts = self.db.get_posts_for_analytics(hours_ago=48)
            brand_posts = [p for p in recent_posts if True]  # Would filter by brand if needed
            brand_result['posts_last_48h'] = len(brand_posts)

            # Check for stalled content (pending too long)
            old_pending = [p for p in pending if p.get('created_at')]
            if old_pending:
                oldest = min(datetime.fromisoformat(p['created_at'].replace('Z', '+00:00')).replace(tzinfo=None)
                            for p in old_pending)
                hours_old = (datetime.utcnow() - oldest).total_seconds() / 3600
                brand_result['oldest_pending_hours'] = round(hours_old)

                if hours_old > self.THRESHOLDS['max_hours_without_content']:
                    self.warnings.append({
                        'check': 'content_pipeline',
                        'brand': brand_name,
                        'message': f"Content stalled: oldest pending is {round(hours_old)} hours old"
                    })

            result['brands'][brand_name] = brand_result

        return result

    def _check_database_health(self) -> Dict:
        """Check database size and cleanup needs."""
        result = {}

        # Get table sizes (approximate via row counts)
        tables = [
            'trending_discoveries',
            'content_bank',
            'blog_articles',
            'posts_log',
            'analytics',
            'health_checks',
            'agent_runs'
        ]

        try:
            # Check recent health checks for patterns
            recent_checks = self.db.get_recent_health_checks(hours=24)
            result['health_checks_24h'] = len(recent_checks)

            # Count failures in recent checks
            failures = [c for c in recent_checks if c.get('status') == 'failure']
            result['failures_24h'] = len(failures)

            if len(failures) > 5:
                self.warnings.append({
                    'check': 'database_health',
                    'message': f"High failure rate: {len(failures)} failures in last 24h"
                })

        except Exception as e:
            result['error'] = str(e)

        return result

    def _log_health_check(self, results: Dict) -> None:
        """Log health check result to database with consecutive failure tracking."""
        status = 'success' if results['status'] == 'healthy' else 'failure'

        # Get previous consecutive failure count
        consecutive = 0
        try:
            recent = self.db.get_recent_health_checks(agent_name='health_monitor', hours=168)
            if recent and status == 'failure':
                # Count consecutive failures
                for check in recent:
                    if check.get('status') == 'failure':
                        consecutive += 1
                    else:
                        break
                consecutive += 1  # Include current failure
        except Exception:
            pass

        try:
            self.db.log_health_check({
                'agent_name': 'health_monitor',
                'check_type': 'scheduled',
                'status': status,
                'consecutive_failures': consecutive if status == 'failure' else 0,
                'details': {
                    'checks_run': results['checks_run'],
                    'issue_count': len(results['issues']),
                    'warning_count': len(results['warnings'])
                }
            })
        except Exception as e:
            print(f"  Failed to log health check: {e}")

    def _send_alert(self, results: Dict) -> None:
        """Send alert email ONLY when threshold-based rules are met.

        Rules:
        - NO email for errors seen fewer than 10 consecutive times
        - NO email for successful health checks
        - NO email for warnings that auto-resolve
        - SEND email ONLY when same error has failed 10+ consecutive times
          or a critical agent has been down 48+ hours
        """
        # Check each issue against the threshold
        for issue in results['issues']:
            agent_name = issue.get('agent', issue.get('api', issue.get('check', 'unknown')))
            error_msg = issue.get('message', 'Unknown error')

            # Get consecutive failure count for this agent
            consecutive = 0
            hours_down = 0
            last_notified = None
            try:
                recent = self.db.get_recent_health_checks(agent_name=agent_name, hours=168)
                for check in recent:
                    if check.get('status') == 'failure':
                        consecutive += 1
                    else:
                        break

                if recent:
                    last_notified = recent[0].get('last_notified_at')

                # Calculate hours down for critical agents
                last_run = self.db.get_last_agent_run(agent_name)
                if last_run:
                    last_run_time = datetime.fromisoformat(
                        last_run['started_at'].replace('Z', '+00:00')
                    ).replace(tzinfo=None)
                    hours_down = (datetime.utcnow() - last_run_time).total_seconds() / 3600
            except Exception:
                pass

            # Only send if threshold is met
            if should_send_alert(agent_name, consecutive, hours_down, last_notified):
                print(f"  ALERTING: {agent_name} has {consecutive} consecutive failures")
                send_critical_alert(
                    agent_name=agent_name,
                    error_message=error_msg,
                    consecutive_failures=consecutive,
                    suggested_fix=f"Check {agent_name} in GitHub Actions and Supabase dashboard."
                )
            else:
                print(f"  {agent_name}: {consecutive} failures (threshold: 10) - no email yet")


def main():
    """Entry point for GitHub Actions."""
    print(f"Starting Health Monitor at {datetime.utcnow().isoformat()}")

    monitor = HealthMonitor()
    results = monitor.run()

    # Exit with error code if unhealthy (for GitHub Actions)
    if results['status'] == 'unhealthy':
        print("\nSystem is UNHEALTHY - check alerts")
        sys.exit(1)

    print(f"\nResults: {json.dumps(results, indent=2)}")
    return results


if __name__ == '__main__':
    main()
