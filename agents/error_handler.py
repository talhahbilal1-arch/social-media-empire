"""
Error Handler Agent - Monitors failures, auto-retries, and escalates
=====================================================================
Runs every 15 minutes to detect failed agent runs, attempt automatic
retries via GitHub Actions API, and send alerts for critical failures.

Features:
- Detects failed agent runs from agent_runs table
- Logs errors to error_log table
- Auto-retries failed workflows up to MAX_RETRIES times
- Detects error patterns (repeated failures)
- Sends email alerts for critical/exhausted errors
"""
import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient
from core.notifications import send_alert


class ErrorHandler:
    """
    Monitors agent failures and handles auto-recovery.

    Workflow:
    1. Find failed runs in last SCAN_WINDOW_HOURS
    2. Check if already logged in error_log
    3. Log new errors
    4. Check if eligible for retry
    5. Trigger retry via GitHub API
    6. Detect patterns and send alerts
    """

    # Configuration
    MAX_RETRIES = 2                    # Max retry attempts per failure
    RETRY_COOLDOWN_MINUTES = 30        # Wait before retrying same agent
    SCAN_WINDOW_HOURS = 6              # Look back window for failures
    PATTERN_WINDOW_HOURS = 24          # Window to detect patterns

    # Agent to workflow mapping
    AGENT_WORKFLOWS = {
        'content_brain': 'content-brain.yml',
        'video_factory': 'video-factory.yml',
        'multi_platform_poster': 'multi-platform-poster.yml',
        'analytics_collector': 'analytics-collector.yml',
        'self_improve': 'self-improve.yml',
        'health_monitor': 'health-monitor.yml',
        'trend_discovery': 'trend-discovery.yml',
        'blog_factory': 'blog-factory.yml',
        'homepage_updater': 'homepage-updater.yml',
    }

    # Error types that are NOT retryable (permanent failures)
    NON_RETRYABLE_ERRORS = [
        'missing environment variable',
        'invalid api key',
        'authentication failed',
        'permission denied',
        'quota exceeded',
    ]

    def __init__(self):
        self.db = SupabaseClient()
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.repo = os.environ.get('GITHUB_REPOSITORY', 'talhahbilal1-arch/social-media-empire')

    def run(self) -> Dict:
        """Main entry point - scan for errors and handle them."""
        print(f"Starting Error Handler at {datetime.utcnow().isoformat()}")

        run_id = self.db.start_agent_run('error_handler', os.environ.get('GITHUB_RUN_ID'))

        results = {
            'errors_found': 0,
            'errors_logged': 0,
            'retries_triggered': 0,
            'retries_exhausted': 0,
            'alerts_sent': 0,
            'patterns_detected': [],
            'errors': []
        }

        try:
            # Step 1: Find failed runs
            failed_runs = self.db.get_failed_agent_runs(hours=self.SCAN_WINDOW_HOURS)
            results['errors_found'] = len(failed_runs)
            print(f"Found {len(failed_runs)} failed runs in last {self.SCAN_WINDOW_HOURS} hours")

            # Step 2: Process each failure
            for run in failed_runs:
                result = self._process_failure(run)

                if result.get('logged'):
                    results['errors_logged'] += 1
                if result.get('retried'):
                    results['retries_triggered'] += 1
                if result.get('exhausted'):
                    results['retries_exhausted'] += 1
                if result.get('alerted'):
                    results['alerts_sent'] += 1
                if result.get('error'):
                    results['errors'].append(result['error'])

            # Step 3: Detect error patterns
            patterns = self._detect_patterns()
            results['patterns_detected'] = patterns

            for pattern in patterns:
                if pattern['failure_count'] >= 3:
                    self._send_pattern_alert(pattern)
                    results['alerts_sent'] += 1

            # Complete run
            self.db.complete_agent_run(
                run_id,
                status='completed',
                items_processed=results['errors_found'],
                items_created=results['retries_triggered'],
                items_failed=results['retries_exhausted']
            )

            print(f"Error Handler completed: {results['retries_triggered']} retries, "
                  f"{results['alerts_sent']} alerts")

        except Exception as e:
            results['errors'].append(str(e))
            self.db.complete_agent_run(run_id, status='failed', error_log=[str(e)])
            send_alert(
                "Error Handler Failed",
                f"The error handler itself failed: {str(e)}",
                severity="critical"
            )
            raise

        return results

    def _process_failure(self, run: Dict) -> Dict:
        """Process a single failed run."""
        result = {
            'logged': False,
            'retried': False,
            'exhausted': False,
            'alerted': False,
            'error': None
        }

        agent_name = run['agent_name']
        run_id = run['id']
        error_messages = run.get('error_log', [])
        error_message = error_messages[0] if error_messages else 'Unknown error'

        print(f"Processing failure: {agent_name} - {error_message[:100]}")

        try:
            # Check if already logged
            existing = self.db.get_error_by_run_id(run_id)

            if existing:
                # Already logged - check if needs retry
                error_record = existing
            else:
                # Log new error
                error_record = self._log_new_error(run, error_message)
                result['logged'] = True

            if not error_record:
                result['error'] = f"Failed to get/create error record for {agent_name}"
                return result

            # Check if eligible for retry
            if self._should_retry(error_record, error_message):
                success = self._trigger_retry(agent_name, error_record['id'])
                if success:
                    result['retried'] = True
                    print(f"Triggered retry for {agent_name}")
                else:
                    result['error'] = f"Failed to trigger retry for {agent_name}"
            elif error_record['retry_count'] >= self.MAX_RETRIES:
                # Exhausted retries
                if error_record['retry_status'] != 'exhausted':
                    self.db.update_error_status(error_record['id'], 'exhausted')
                    self._send_exhausted_alert(agent_name, error_message, error_record)
                    result['exhausted'] = True
                    result['alerted'] = True

        except Exception as e:
            result['error'] = f"Error processing {agent_name}: {str(e)}"

        return result

    def _log_new_error(self, run: Dict, error_message: str) -> Optional[Dict]:
        """Log a new error to the error_log table."""
        error_type = self._classify_error(error_message)
        workflow_name = self.AGENT_WORKFLOWS.get(run['agent_name'])

        error_data = {
            'agent_name': run['agent_name'],
            'agent_run_id': run['id'],
            'error_type': error_type,
            'error_message': error_message[:2000],  # Truncate if too long
            'workflow_name': workflow_name,
            'retry_count': 0,
            'retry_status': 'pending'
        }

        return self.db.log_error(error_data)

    def _classify_error(self, error_message: str) -> str:
        """Classify error type based on message."""
        error_lower = error_message.lower()

        if any(term in error_lower for term in ['timeout', 'timed out', 'deadline']):
            return 'timeout'
        elif any(term in error_lower for term in ['api', 'http', '401', '403', '429', '500', '502', '503']):
            return 'api'
        elif any(term in error_lower for term in ['data', 'json', 'parse', 'decode', 'key error']):
            return 'data'
        elif any(term in error_lower for term in ['import', 'module', 'attribute', 'type error']):
            return 'runtime'
        else:
            return 'unknown'

    def _should_retry(self, error_record: Dict, error_message: str) -> bool:
        """Determine if an error should be retried."""
        # Already exhausted or resolved
        if error_record['retry_status'] in ['exhausted', 'resolved']:
            return False

        # Max retries reached
        if error_record['retry_count'] >= self.MAX_RETRIES:
            return False

        # Check if error is retryable
        error_lower = error_message.lower()
        for non_retryable in self.NON_RETRYABLE_ERRORS:
            if non_retryable in error_lower:
                print(f"Error not retryable: {non_retryable}")
                return False

        # Check cooldown
        created_at = error_record['created_at']
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        cooldown_end = created_at + timedelta(minutes=self.RETRY_COOLDOWN_MINUTES * (error_record['retry_count'] + 1))
        if datetime.utcnow().replace(tzinfo=cooldown_end.tzinfo) < cooldown_end:
            print(f"In cooldown until {cooldown_end.isoformat()}")
            return False

        return True

    def _trigger_retry(self, agent_name: str, error_id: str) -> bool:
        """Trigger a workflow retry via GitHub Actions API."""
        if not self.github_token:
            print("GITHUB_TOKEN not configured - cannot trigger retry")
            return False

        workflow_name = self.AGENT_WORKFLOWS.get(agent_name)
        if not workflow_name:
            print(f"No workflow mapping for {agent_name}")
            return False

        try:
            # Increment retry count first
            self.db.increment_error_retry(error_id)

            # Trigger workflow via GitHub API
            url = f"https://api.github.com/repos/{self.repo}/actions/workflows/{workflow_name}/dispatches"

            response = requests.post(
                url,
                headers={
                    'Authorization': f'Bearer {self.github_token}',
                    'Accept': 'application/vnd.github.v3+json'
                },
                json={'ref': 'main'},
                timeout=30
            )

            if response.status_code == 204:
                print(f"Successfully triggered {workflow_name}")
                return True
            else:
                print(f"Failed to trigger workflow: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error triggering retry: {e}")
            return False

    def _detect_patterns(self) -> List[Dict]:
        """Detect error patterns (agents with multiple failures)."""
        return self.db.get_error_patterns(hours=self.PATTERN_WINDOW_HOURS)

    def _send_exhausted_alert(self, agent_name: str, error_message: str, error_record: Dict) -> None:
        """Send alert when retries are exhausted."""
        send_alert(
            f"{agent_name} Failed - Retries Exhausted",
            f"Agent {agent_name} has failed {error_record['retry_count']} times and "
            f"automatic retries have been exhausted.\n\n"
            f"Error: {error_message[:500]}\n\n"
            f"Manual intervention required. Check GitHub Actions for details.",
            severity="error",
            details={
                'agent': agent_name,
                'retry_count': error_record['retry_count'],
                'error_type': error_record.get('error_type', 'unknown'),
                'workflow': error_record.get('workflow_name')
            }
        )

    def _send_pattern_alert(self, pattern: Dict) -> None:
        """Send alert for detected error pattern."""
        send_alert(
            f"Error Pattern Detected: {pattern['agent_name']}",
            f"Agent {pattern['agent_name']} has failed {pattern['failure_count']} times "
            f"in the last {self.PATTERN_WINDOW_HOURS} hours.\n\n"
            f"This indicates a systemic issue that requires investigation.",
            severity="warning",
            details=pattern
        )


def main():
    """Entry point for GitHub Actions."""
    handler = ErrorHandler()
    results = handler.run()

    print(f"\nResults: {json.dumps(results, indent=2)}")

    # Exit with error if we found patterns or exhausted retries
    if results['retries_exhausted'] > 0 or len(results['patterns_detected']) > 0:
        print("\nWarning: Issues detected that need attention")

    return results


if __name__ == '__main__':
    main()
