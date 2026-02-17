"""Workflow Guardian - Auto-retry failed workflows."""
import subprocess
import json
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class WorkflowGuardian:
    """Monitor and auto-retry failed GitHub Actions workflows."""

    CRITICAL_WORKFLOWS = [
        'content-engine.yml',
        'weekly-discovery.yml',
        'fitness-articles.yml',
        'youtube-fitness.yml',
    ]

    def analyze_and_heal(self, hours=2):
        """Check for failed workflows in the last N hours and retry them."""
        results = {'checked': 0, 'failed': 0, 'retried': 0, 'errors': []}

        for workflow in self.CRITICAL_WORKFLOWS:
            try:
                # Get recent runs
                cmd = f'gh api repos/talhahbilal1-arch/social-media-empire/actions/workflows/{workflow}/runs --jq ".workflow_runs[:3]"'
                output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)

                if output.returncode != 0:
                    logger.warning(f"Could not check {workflow}: {output.stderr}")
                    continue

                runs = json.loads(output.stdout) if output.stdout.strip() else []
                results['checked'] += 1

                for run in runs:
                    if run.get('conclusion') == 'failure':
                        created = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00'))
                        if datetime.now(timezone.utc) - created < timedelta(hours=hours):
                            results['failed'] += 1
                            logger.info(f"Found failed run for {workflow}, attempting retry...")

                            retry_cmd = f'gh workflow run {workflow}'
                            retry = subprocess.run(retry_cmd, shell=True, capture_output=True, text=True, timeout=30)

                            if retry.returncode == 0:
                                results['retried'] += 1
                                logger.info(f"Successfully retried {workflow}")
                            else:
                                results['errors'].append(f"Failed to retry {workflow}: {retry.stderr}")
                            break  # Only retry once per workflow

            except Exception as e:
                results['errors'].append(f"Error checking {workflow}: {str(e)}")

        logger.info(f"WorkflowGuardian: checked={results['checked']}, failed={results['failed']}, retried={results['retried']}")
        return results
