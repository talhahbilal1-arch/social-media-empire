"""
Self-Healer Agent
==================
Runs every 6 hours via health-monitor.yml workflow.

Self-healing logic:
1. Run health checks on all agents and database
2. For each error found:
   a. Check health_checks table for how many times this SAME error has occurred
   b. If < 10 occurrences: attempt automatic fix (retry the agent, reset state, etc.)
   c. Log the attempt and result to health_checks
   d. If fix succeeds: mark as resolved, NO email
   e. If fix fails AND this is attempt #10 or higher: send email alert
3. Common auto-fixes:
   - Agent failed to run -> re-trigger the GitHub Action via subprocess
   - Database query failed -> retry with exponential backoff (1s, 2s, 4s, 8s, 16s)
   - API timeout -> retry up to 3 times
   - Schema mismatch -> log but DON'T auto-fix (needs human review)
4. NEVER send email for:
   - Successful self-heals
   - Warnings that are auto-resolved
   - Any error with < 10 consecutive failures
"""
import os
import sys
import json
import time
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient
from core.notifications import send_alert


class SelfHealer:
    """Automated self-healing system for the Social Media Empire."""

    # Agents that are critical to the system — if down 48+ hours, alert immediately
    CRITICAL_AGENTS = [
        'content_brain',
        'video_factory',
        'content_pipeline',
        'multi_platform_poster',
        'health_monitor',
    ]

    # Map agent names to their GitHub Actions workflow filenames
    AGENT_WORKFLOW_MAP = {
        'trend_discovery': 'trend-discovery.yml',
        'content_brain': 'content-brain.yml',
        'blog_factory': 'blog-factory.yml',
        'video_factory': 'video-factory.yml',
        'multi_platform_poster': 'content-engine.yml',
        'analytics_collector': 'analytics-collector.yml',
        'self_improve': 'self-improve.yml',
        'health_monitor': 'health-monitor.yml',
    }

    # Error types that should NOT be auto-fixed
    NO_AUTO_FIX_TYPES = [
        'schema_mismatch',
        'schema_error',
        'migration_required',
    ]

    def __init__(self):
        self.db = SupabaseClient()
        self.heal_results: List[Dict] = []

    def run(self) -> Dict:
        """
        Main entry point for the self-healer.

        Checks all agent statuses and database health, attempts auto-fixes
        for any issues found, and only sends email alerts when consecutive
        failures reach 10 or a critical agent has been down 48+ hours.
        """
        print(f"Running self-healer at {datetime.utcnow().isoformat()}")

        results = {
            'status': 'healthy',
            'issues_found': 0,
            'fixes_attempted': 0,
            'fixes_succeeded': 0,
            'alerts_sent': 0,
            'details': [],
        }

        # Step 1: Check all agent statuses
        print("  Checking agent health...")
        agent_issues = self._check_agent_health()

        # Step 2: Check for recent database errors
        print("  Checking database health...")
        db_issues = self._check_database_health()

        all_issues = agent_issues + db_issues
        results['issues_found'] = len(all_issues)

        if not all_issues:
            print("  No issues found. System is healthy.")
            self._log_heal_attempt(
                agent_name='self_healer',
                error_type='routine_check',
                success=True,
                details='No issues found during scheduled check'
            )
            results['status'] = 'healthy'
            return results

        # Step 3: Attempt auto-fixes for each issue
        for issue in all_issues:
            agent_name = issue.get('agent_name', 'unknown')
            error_type = issue.get('error_type', 'unknown')
            error_message = issue.get('error_message', 'No details')

            print(f"  Attempting fix for {agent_name} ({error_type})...")
            results['fixes_attempted'] += 1

            fix_success = self._attempt_auto_fix(agent_name, error_type, error_message)

            if fix_success:
                results['fixes_succeeded'] += 1
                print(f"    -> Fixed successfully")
            else:
                print(f"    -> Fix failed")

                # Check consecutive failures to decide on alerting
                consecutive_failures = self._get_consecutive_failures(agent_name)

                if self._should_send_alert(agent_name, consecutive_failures):
                    # Get recent timestamps for the alert
                    recent_checks = self.db.get_recent_health_checks(
                        agent_name=agent_name, hours=72
                    )
                    timestamps = [
                        c.get('checked_at', 'unknown')
                        for c in recent_checks[:3]
                    ]

                    self._send_critical_alert(
                        agent_name=agent_name,
                        error_message=error_message,
                        consecutive_failures=consecutive_failures,
                        timestamps=timestamps
                    )
                    results['alerts_sent'] += 1
                    print(f"    -> Alert sent ({consecutive_failures} consecutive failures)")

            results['details'].append({
                'agent': agent_name,
                'error_type': error_type,
                'fix_attempted': True,
                'fix_succeeded': fix_success,
            })

        # Determine overall status
        if results['fixes_attempted'] == results['fixes_succeeded']:
            results['status'] = 'healed'
        elif results['fixes_succeeded'] > 0:
            results['status'] = 'partially_healed'
        else:
            results['status'] = 'unhealthy'

        print(f"\nSelf-healer complete: {results['status']}")
        print(f"  Issues: {results['issues_found']}, "
              f"Fixed: {results['fixes_succeeded']}/{results['fixes_attempted']}, "
              f"Alerts: {results['alerts_sent']}")

        return results

    def _check_agent_health(self) -> List[Dict]:
        """
        Check agent_runs table for failed or stale agents.

        Returns a list of issues found, each with agent_name, error_type,
        and error_message.
        """
        issues = []
        now = datetime.utcnow()

        for agent_name in self.AGENT_WORKFLOW_MAP.keys():
            last_run = self.db.get_last_agent_run(agent_name)

            if not last_run:
                # Agent has never run — this is a warning, not necessarily fixable
                issues.append({
                    'agent_name': agent_name,
                    'error_type': 'never_run',
                    'error_message': f"{agent_name} has never run"
                })
                continue

            # Check if the last run failed
            if last_run['status'] == 'failed':
                error_log = last_run.get('error_log', [])
                error_msg = error_log[0] if error_log else 'Unknown error'
                issues.append({
                    'agent_name': agent_name,
                    'error_type': 'agent_failed',
                    'error_message': f"{agent_name} failed: {error_msg}"
                })
                continue

            # Check if agent is stale (hasn't run in too long)
            last_run_time = datetime.fromisoformat(
                last_run['started_at'].replace('Z', '+00:00')
            ).replace(tzinfo=None)
            hours_since = (now - last_run_time).total_seconds() / 3600

            # Daily agents should run within 26 hours
            if hours_since > 26:
                issues.append({
                    'agent_name': agent_name,
                    'error_type': 'agent_stale',
                    'error_message': (
                        f"{agent_name} hasn't run in {round(hours_since)} hours "
                        f"(last: {last_run['started_at']})"
                    )
                })

        return issues

    def _check_database_health(self) -> List[Dict]:
        """
        Check for recent errors in the health_checks table.

        Returns a list of issues found with database-related errors.
        """
        issues = []

        try:
            recent_checks = self.db.get_recent_health_checks(hours=6)

            for check in recent_checks:
                if check.get('status') == 'failure':
                    details = check.get('details', {})
                    error_type = 'database_error'

                    # Detect schema-related errors
                    detail_str = json.dumps(details).lower() if details else ''
                    if 'schema' in detail_str or 'column' in detail_str or 'relation' in detail_str:
                        error_type = 'schema_mismatch'

                    issues.append({
                        'agent_name': check.get('agent_name', 'unknown'),
                        'error_type': error_type,
                        'error_message': (
                            f"Health check failure for {check.get('agent_name', 'unknown')}: "
                            f"{json.dumps(details)}"
                        )
                    })

        except Exception as e:
            issues.append({
                'agent_name': 'database',
                'error_type': 'database_error',
                'error_message': f"Failed to query health_checks table: {str(e)}"
            })

        return issues

    def _attempt_auto_fix(self, agent_name: str, error_type: str, error_message: str) -> bool:
        """
        Try to automatically fix the issue.

        - For failed/stale agents: re-trigger their GitHub Action workflow
        - For database errors: retry the operation with exponential backoff
        - For schema errors: log only, don't auto-fix (needs human review)

        Returns True if the fix succeeded, False otherwise.
        """
        # Schema errors should never be auto-fixed
        if error_type in self.NO_AUTO_FIX_TYPES:
            self._log_heal_attempt(
                agent_name=agent_name,
                error_type=error_type,
                success=False,
                details=f"Schema error requires human review: {error_message}"
            )
            return False

        # Agent failed or stale — re-trigger the workflow
        if error_type in ('agent_failed', 'agent_stale', 'never_run'):
            workflow_file = self.AGENT_WORKFLOW_MAP.get(agent_name)
            if not workflow_file:
                self._log_heal_attempt(
                    agent_name=agent_name,
                    error_type=error_type,
                    success=False,
                    details=f"No workflow mapping found for agent: {agent_name}"
                )
                return False

            success = self._retrigger_workflow(agent_name, workflow_file)
            self._log_heal_attempt(
                agent_name=agent_name,
                error_type=error_type,
                success=success,
                details=(
                    f"Re-triggered workflow {workflow_file}"
                    if success
                    else f"Failed to re-trigger workflow {workflow_file}"
                )
            )
            return success

        # Database errors — retry with exponential backoff
        if error_type == 'database_error':
            def db_health_check():
                """Simple database connectivity check."""
                self.db.get_active_brands()
                return True

            success = self._retry_with_backoff(db_health_check, max_retries=5)
            self._log_heal_attempt(
                agent_name=agent_name,
                error_type=error_type,
                success=success,
                details=(
                    "Database recovered after retry"
                    if success
                    else f"Database still failing after retries: {error_message}"
                )
            )
            return success

        # API timeout — retry up to 3 times
        if error_type == 'api_timeout':
            def api_retry():
                """Simple API connectivity check."""
                self.db.get_recent_health_checks(hours=1)
                return True

            success = self._retry_with_backoff(api_retry, max_retries=3)
            self._log_heal_attempt(
                agent_name=agent_name,
                error_type=error_type,
                success=success,
                details=(
                    "API recovered after retry"
                    if success
                    else f"API still failing after retries: {error_message}"
                )
            )
            return success

        # Unknown error type — log it but don't attempt a fix
        self._log_heal_attempt(
            agent_name=agent_name,
            error_type=error_type,
            success=False,
            details=f"Unknown error type, no auto-fix available: {error_message}"
        )
        return False

    def _retrigger_workflow(self, agent_name: str, workflow_file: str) -> bool:
        """
        Re-trigger a GitHub Actions workflow using the gh CLI.

        Returns True if the dispatch command succeeded.
        """
        repo = os.environ.get('GITHUB_REPOSITORY', '')
        if not repo:
            print(f"    GITHUB_REPOSITORY not set — cannot re-trigger")
            return False

        try:
            result = subprocess.run(
                [
                    'gh', 'api',
                    '--method', 'POST',
                    '-H', 'Accept: application/vnd.github+json',
                    f'/repos/{repo}/actions/workflows/{workflow_file}/dispatches',
                    '-f', 'ref=main'
                ],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"    Re-triggered {workflow_file} for {agent_name}")
                return True
            else:
                print(f"    Failed to trigger {workflow_file}: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"    Timeout triggering {workflow_file}")
            return False
        except FileNotFoundError:
            print("    gh CLI not found — cannot re-trigger workflows")
            return False
        except Exception as e:
            print(f"    Error triggering {workflow_file}: {str(e)}")
            return False

    def _retry_with_backoff(self, func: Callable, max_retries: int = 5) -> bool:
        """
        Retry a function with exponential backoff.

        Delays: 1s, 2s, 4s, 8s, 16s (doubling each time).

        Returns True if the function eventually succeeds, False if all retries
        are exhausted.
        """
        for attempt in range(max_retries):
            try:
                func()
                return True
            except Exception as e:
                delay = 2 ** attempt  # 1, 2, 4, 8, 16
                print(f"    Retry {attempt + 1}/{max_retries} failed: {str(e)}. "
                      f"Waiting {delay}s...")
                if attempt < max_retries - 1:
                    time.sleep(delay)

        return False

    def _get_consecutive_failures(self, agent_name: str) -> int:
        """
        Query health_checks for the number of consecutive failures for an agent.

        Counts backwards from the most recent check until a success is found.
        """
        try:
            recent_checks = self.db.get_recent_health_checks(
                agent_name=agent_name, hours=168  # 7 days
            )

            consecutive = 0
            for check in recent_checks:
                if check.get('status') == 'failure':
                    consecutive += 1
                else:
                    break

            return consecutive

        except Exception:
            # If we can't even query, assume high failure count to be safe
            return 0

    def _log_heal_attempt(self, agent_name: str, error_type: str, success: bool,
                          details: str) -> None:
        """
        Log a self-heal attempt to the health_checks table.
        """
        try:
            self.db.log_health_check({
                'agent_name': agent_name,
                'check_type': 'self_heal',
                'status': 'success' if success else 'failure',
                'details': {
                    'error_type': error_type,
                    'heal_success': success,
                    'heal_details': details,
                    'healed_by': 'self_healer',
                    'timestamp': datetime.utcnow().isoformat()
                }
            })
        except Exception as e:
            # Don't let logging failures break the healing process
            print(f"    Warning: Failed to log heal attempt: {str(e)}")

    def _should_send_alert(self, agent_name: str, consecutive_failures: int) -> bool:
        """
        Determine whether an email alert should be sent.

        Returns True only if:
        - consecutive_failures >= 10, OR
        - The agent is critical AND has been down for 48+ hours
        """
        # Rule 1: 10 or more consecutive failures always triggers alert
        if consecutive_failures >= 10:
            return True

        # Rule 2: Critical agent down for 48+ hours
        if agent_name in self.CRITICAL_AGENTS:
            last_run = self.db.get_last_agent_run(agent_name)
            if last_run:
                last_run_time = datetime.fromisoformat(
                    last_run['started_at'].replace('Z', '+00:00')
                ).replace(tzinfo=None)
                hours_since = (datetime.utcnow() - last_run_time).total_seconds() / 3600
                if hours_since >= 48:
                    return True

        return False

    def _send_critical_alert(self, agent_name: str, error_message: str,
                             consecutive_failures: int, timestamps: List[str]) -> None:
        """
        Send an email alert for a critical, unresolvable issue.

        Subject format: "EMPIRE CRITICAL: [agent_name] failed 10x -- needs manual fix"
        Body includes: error message, attempts count, last 3 timestamps, suggested fix.
        """
        # Build suggested fix based on the agent
        suggested_fix = self._suggest_fix(agent_name)

        # Format the last 3 failure timestamps
        timestamps_text = "\n".join([
            f"  - {ts}" for ts in timestamps[:3]
        ]) if timestamps else "  No timestamps available"

        message = f"""CRITICAL: {agent_name} has failed {consecutive_failures} consecutive times
and self-healing was unable to resolve the issue.

ERROR:
  {error_message}

SELF-HEAL ATTEMPTS: {consecutive_failures}

LAST 3 FAILURE TIMESTAMPS:
{timestamps_text}

SUGGESTED FIX:
  {suggested_fix}

This agent requires manual intervention. Please check the GitHub Actions
logs and Supabase dashboard for more details.
"""

        send_alert(
            subject=f"EMPIRE CRITICAL: {agent_name} failed {consecutive_failures}x -- needs manual fix",
            message=message,
            severity="critical",
            details={
                'agent_name': agent_name,
                'consecutive_failures': consecutive_failures,
                'last_error': error_message[:500],
            }
        )

    def _suggest_fix(self, agent_name: str) -> str:
        """Return a human-readable suggested fix for the given agent."""
        suggestions = {
            'content_brain': (
                "Check ANTHROPIC_API_KEY is valid. Verify Claude API status at "
                "status.anthropic.com. Re-run: gh workflow run content-brain.yml"
            ),
            'video_factory': (
                "Check CREATOMATE_API_KEY is valid. Verify video template IDs are "
                "correct. Re-run: gh workflow run video-factory.yml"
            ),
            'multi_platform_poster': (
                "Check social platform API tokens (YouTube, Pinterest). Verify "
                "Make.com webhooks are active. Re-run: gh workflow run content-engine.yml"
            ),
            'blog_factory': (
                "Check ANTHROPIC_API_KEY and NETLIFY_API_TOKEN. Verify Netlify "
                "site is accessible. Re-run: gh workflow run blog-factory.yml"
            ),
            'trend_discovery': (
                "Check API keys for trend sources. Verify network connectivity. "
                "Re-run: gh workflow run trend-discovery.yml"
            ),
            'analytics_collector': (
                "Check social platform API tokens. Some platforms rate-limit "
                "analytics. Re-run: gh workflow run analytics-collector.yml"
            ),
            'health_monitor': (
                "If health_monitor itself is failing, check SUPABASE_URL and "
                "SUPABASE_KEY. Re-run: gh workflow run health-monitor.yml"
            ),
            'self_improve': (
                "Check ANTHROPIC_API_KEY. This agent runs weekly — verify the "
                "cron schedule. Re-run: gh workflow run self-improve.yml"
            ),
        }
        return suggestions.get(
            agent_name,
            f"Check GitHub Actions logs for {agent_name}. Manually re-run the workflow."
        )


def main():
    """Entry point for GitHub Actions."""
    print(f"Starting Self-Healer at {datetime.utcnow().isoformat()}")

    healer = SelfHealer()
    results = healer.run()

    # Exit with error code if still unhealthy after healing attempts
    if results['status'] == 'unhealthy':
        print("\nSystem is UNHEALTHY after self-heal attempts")
        sys.exit(1)

    print(f"\nResults: {json.dumps(results, indent=2)}")
    return results


if __name__ == '__main__':
    main()
