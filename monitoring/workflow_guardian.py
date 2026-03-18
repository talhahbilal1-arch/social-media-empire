"""Workflow Guardian - Auto-retry failed workflows and monitor content freshness."""
import subprocess
import json
import logging
import os
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class WorkflowGuardian:
    """Monitor and auto-retry failed GitHub Actions workflows."""

    REPO = 'talhahbilal1-arch/social-media-empire'

    # All active workflows ranked by priority (30 total, updated March 2026)
    CRITICAL_WORKFLOWS = [
        'content-engine.yml',       # 3x daily — core pipeline
        'fitness-articles.yml',     # Article generation
        'system-health.yml',        # Self-healing (this workflow)
        'rescue-poster.yml',        # Every 2 hrs — rescue failed pins
    ]

    IMPORTANT_WORKFLOWS = [
        'weekly-discovery.yml',     # Monday trend discovery
        'daily-trend-scout.yml',    # Daily trend scouting
        'seo-content-machine.yml',  # MWF SEO content
        'video-automation-morning.yml',  # Daily video generation
        'video-pins.yml',           # Daily Remotion video pins
        'tiktok-content.yml',       # 3x daily TikTok content
        'tiktok-poster.yml',        # Daily TikTok posting
        'menopause-newsletter.yml', # Weekly menopause newsletter
        'toolpilot-deploy.yml',     # PilotTools site deploy
        'toolpilot-content.yml',    # Mon-Fri content generation
        'toolpilot-newsletter.yml', # Weekly newsletter
        'youtube-fitness.yml',      # YouTube Shorts
    ]

    OPERATIONAL_WORKFLOWS = [
        'deploy-brand-sites.yml',   # Manual Vercel deploy
        'pinterest-analytics.yml',  # Weekly analytics
        'emergency-alert.yml',      # Daily alerts
        'self-improve.yml',         # Weekly self-improvement
        'weekly-summary.yml',       # Weekly report
        'analytics-collector.yml',  # Daily analytics
        'revenue-activation.yml',   # Weekly revenue analysis
        'revenue-intelligence.yml', # Daily revenue intelligence
        'check-affiliate-links.yml',  # Weekly link validation
        'toolpilot-report.yml',     # Weekly health report
        'toolpilot-weekly.yml',     # Weekly tasks
        'auto-merge.yml',           # PR auto-merge
        'subdomain-deploy.yml',     # Subdomain deploys
        'validate-workflows.yml',   # CI workflow validation
    ]

    # Max retries per workflow within a 6-hour window
    MAX_RETRIES_PER_WINDOW = 2

    def analyze_and_heal(self, hours=2):
        """Check for failed workflows in the last N hours and retry them."""
        results = {
            'checked': 0, 'failed': 0, 'retried': 0,
            'skipped_max_retries': 0, 'errors': [],
            'content_fresh': True,
        }

        all_workflows = (
            self.CRITICAL_WORKFLOWS
            + self.IMPORTANT_WORKFLOWS
            + self.OPERATIONAL_WORKFLOWS
        )

        for workflow in all_workflows:
            try:
                runs = self._get_recent_runs(workflow, count=5)
                if runs is None:
                    continue
                results['checked'] += 1

                # Find the most recent run
                latest = runs[0] if runs else None
                if not latest or latest.get('conclusion') != 'failure':
                    continue

                created = datetime.fromisoformat(
                    latest['created_at'].replace('Z', '+00:00')
                )
                if datetime.now(timezone.utc) - created > timedelta(hours=hours):
                    continue

                results['failed'] += 1

                # Check how many recent failures to avoid retry loops
                recent_failures = sum(
                    1 for r in runs
                    if r.get('conclusion') == 'failure'
                    and (datetime.now(timezone.utc) - datetime.fromisoformat(
                        r['created_at'].replace('Z', '+00:00')
                    )) < timedelta(hours=6)
                )

                if recent_failures >= self.MAX_RETRIES_PER_WINDOW:
                    logger.warning(
                        f"{workflow}: {recent_failures} failures in 6h — "
                        f"skipping retry (max {self.MAX_RETRIES_PER_WINDOW})"
                    )
                    results['skipped_max_retries'] += 1
                    results['errors'].append(
                        f"{workflow}: repeated failures ({recent_failures} in 6h)"
                    )
                    continue

                # Retry the workflow
                logger.info(f"Retrying {workflow} (failure at {latest['created_at']})")
                if self._retry_workflow(workflow):
                    results['retried'] += 1
                else:
                    results['errors'].append(f"Failed to retry {workflow}")

            except Exception as e:
                results['errors'].append(f"Error checking {workflow}: {str(e)}")

        # Content freshness check
        results['content_fresh'] = self._check_content_freshness()

        logger.info(
            f"WorkflowGuardian: checked={results['checked']}, "
            f"failed={results['failed']}, retried={results['retried']}, "
            f"skipped={results['skipped_max_retries']}, "
            f"content_fresh={results['content_fresh']}"
        )
        return results

    def _get_recent_runs(self, workflow, count=5):
        """Fetch recent workflow runs via gh CLI."""
        cmd = (
            f'gh api repos/{self.REPO}/actions/workflows/{workflow}/runs '
            f'--jq ".workflow_runs[:{count}]"'
        )
        output = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        if output.returncode != 0:
            logger.warning(f"Could not check {workflow}: {output.stderr}")
            return None
        return json.loads(output.stdout) if output.stdout.strip() else []

    def _retry_workflow(self, workflow):
        """Trigger a new run of the given workflow."""
        result = subprocess.run(
            f'gh workflow run {workflow}',
            shell=True, capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            logger.info(f"Successfully retried {workflow}")
            return True
        logger.error(f"Retry failed for {workflow}: {result.stderr}")
        return False

    def _check_content_freshness(self):
        """Verify that content-engine has produced output in the last 24h."""
        try:
            runs = self._get_recent_runs('content-engine.yml', count=10)
            if not runs:
                return False

            now = datetime.now(timezone.utc)
            recent_success = any(
                r.get('conclusion') == 'success'
                and (now - datetime.fromisoformat(
                    r['created_at'].replace('Z', '+00:00')
                )) < timedelta(hours=24)
                for r in runs
            )

            if not recent_success:
                logger.warning(
                    "Content freshness alert: no successful content-engine "
                    "run in the last 24 hours"
                )
                # Auto-trigger a content-engine run
                logger.info("Auto-triggering content-engine to restore freshness")
                self._retry_workflow('content-engine.yml')

            return recent_success

        except Exception as e:
            logger.error(f"Content freshness check failed: {e}")
            return True  # Assume fresh on error to avoid false alerts
