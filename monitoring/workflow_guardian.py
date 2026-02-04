"""
Workflow Guardian - Intelligent Self-Healing System for Social Media Empire.

This module monitors all GitHub Actions workflows, detects failures,
analyzes error patterns, and automatically takes remediation actions.

Features:
- Real-time workflow monitoring
- Pattern-based error classification
- Automatic retry for transient failures
- Known-fix application for common issues
- Alert escalation for manual intervention
- Comprehensive logging and reporting
"""

import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WorkflowGuardian")


class FailureCategory(Enum):
    """Categories of workflow failures."""
    TRANSIENT = "transient"  # Network issues, rate limits - retry
    CREDENTIAL = "credential"  # API keys, tokens - alert
    CONFIGURATION = "configuration"  # Missing config - may auto-fix
    RESOURCE = "resource"  # Billing, quotas - alert
    CODE = "code"  # Bug in code - create issue
    EXTERNAL = "external"  # Third-party service down - wait and retry
    UNKNOWN = "unknown"  # Needs investigation


@dataclass
class FailurePattern:
    """Pattern for matching and handling specific failure types."""
    name: str
    category: FailureCategory
    patterns: list[str]  # Regex patterns to match in logs
    auto_retry: bool = False
    retry_delay_minutes: int = 5
    max_retries: int = 3
    auto_fix_action: Optional[str] = None
    alert_immediately: bool = False
    description: str = ""


@dataclass
class WorkflowRun:
    """Represents a GitHub Actions workflow run."""
    id: int
    name: str
    status: str
    conclusion: Optional[str]
    created_at: datetime
    head_branch: str
    html_url: str
    logs_url: Optional[str] = None
    failure_category: Optional[FailureCategory] = None
    failure_pattern: Optional[str] = None
    retry_count: int = 0


@dataclass
class RemediationAction:
    """An action taken to remediate a failure."""
    workflow_run_id: int
    action_type: str  # "retry", "fix", "alert", "issue"
    description: str
    success: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: dict = field(default_factory=dict)


# Known failure patterns and how to handle them
FAILURE_PATTERNS = [
    FailurePattern(
        name="rate_limit_429",
        category=FailureCategory.TRANSIENT,
        patterns=[r"429", r"rate.?limit", r"too.?many.?requests", r"quota.?exceeded"],
        auto_retry=True,
        retry_delay_minutes=15,
        max_retries=3,
        description="API rate limit exceeded"
    ),
    FailurePattern(
        name="network_timeout",
        category=FailureCategory.TRANSIENT,
        patterns=[r"timeout", r"ETIMEDOUT", r"connection.?refused", r"network.?error"],
        auto_retry=True,
        retry_delay_minutes=5,
        max_retries=3,
        description="Network connectivity issue"
    ),
    FailurePattern(
        name="git_push_403",
        category=FailureCategory.CREDENTIAL,
        patterns=[r"fatal:.+403", r"unable to access.+403", r"git.+push.+403"],
        auto_retry=False,
        alert_immediately=True,
        description="Git push permission denied"
    ),
    FailurePattern(
        name="oauth_token_expired",
        category=FailureCategory.CREDENTIAL,
        patterns=[r"token.+expired", r"invalid.+token", r"401.+unauthorized", r"oauth.+error"],
        auto_retry=False,
        alert_immediately=True,
        auto_fix_action="refresh_oauth_token",
        description="OAuth token needs refresh"
    ),
    FailurePattern(
        name="api_key_invalid",
        category=FailureCategory.CREDENTIAL,
        patterns=[r"invalid.+api.?key", r"api.?key.+not.+found", r"authentication.+failed"],
        auto_retry=False,
        alert_immediately=True,
        description="API key invalid or missing"
    ),
    FailurePattern(
        name="payment_required",
        category=FailureCategory.RESOURCE,
        patterns=[r"402", r"payment.?required", r"billing", r"subscription.+expired"],
        auto_retry=False,
        alert_immediately=True,
        description="Payment or billing issue"
    ),
    FailurePattern(
        name="gemini_model_not_found",
        category=FailureCategory.CONFIGURATION,
        patterns=[r"model.+not.+found", r"404.+model", r"gemini.+not.+found"],
        auto_retry=False,
        auto_fix_action="update_gemini_model",
        description="Gemini model name incorrect"
    ),
    FailurePattern(
        name="module_not_found",
        category=FailureCategory.CODE,
        patterns=[r"ModuleNotFoundError", r"ImportError", r"No module named"],
        auto_retry=False,
        description="Python module import error"
    ),
    FailurePattern(
        name="syntax_error",
        category=FailureCategory.CODE,
        patterns=[r"SyntaxError", r"IndentationError", r"invalid syntax"],
        auto_retry=False,
        description="Python syntax error"
    ),
    FailurePattern(
        name="service_unavailable",
        category=FailureCategory.EXTERNAL,
        patterns=[r"503", r"service.?unavailable", r"temporarily.?unavailable"],
        auto_retry=True,
        retry_delay_minutes=10,
        max_retries=5,
        description="External service temporarily down"
    ),
    FailurePattern(
        name="late_api_forbidden",
        category=FailureCategory.CREDENTIAL,
        patterns=[r"getlate\.dev.+403", r"late.+api.+forbidden"],
        auto_retry=False,
        alert_immediately=True,
        description="Late API access forbidden"
    ),
]


class WorkflowGuardian:
    """Main guardian class for monitoring and healing workflows."""

    def __init__(self, github_token: Optional[str] = None, repo: Optional[str] = None):
        """Initialize the workflow guardian.

        Args:
            github_token: GitHub API token (defaults to GITHUB_TOKEN env var)
            repo: Repository in format "owner/repo" (defaults to GITHUB_REPOSITORY)
        """
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.repo = repo or os.environ.get("GITHUB_REPOSITORY")
        self.actions_taken: list[RemediationAction] = []
        self.retry_tracker: dict[int, int] = {}  # run_id -> retry_count

        if not self.github_token:
            logger.warning("GITHUB_TOKEN not set - some features will be limited")

        if not self.repo:
            # Try to get from git remote
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    capture_output=True, text=True, check=True
                )
                url = result.stdout.strip()
                # Extract owner/repo from URL
                match = re.search(r"github\.com[/:]([^/]+/[^/.]+)", url)
                if match:
                    self.repo = match.group(1).replace(".git", "")
            except Exception:
                pass

    def _github_api(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """Make a GitHub API request."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"

        url = f"https://api.github.com{endpoint}"

        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json() if response.text else {}

    def get_recent_runs(self, hours: int = 6) -> list[WorkflowRun]:
        """Get workflow runs from the last N hours."""
        if not self.repo:
            logger.error("Repository not configured")
            return []

        runs = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        try:
            data = self._github_api(f"/repos/{self.repo}/actions/runs?per_page=50")

            for run in data.get("workflow_runs", []):
                created_at = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))

                if created_at < cutoff:
                    continue

                runs.append(WorkflowRun(
                    id=run["id"],
                    name=run["name"],
                    status=run["status"],
                    conclusion=run.get("conclusion"),
                    created_at=created_at,
                    head_branch=run["head_branch"],
                    html_url=run["html_url"],
                    logs_url=run.get("logs_url")
                ))
        except Exception as e:
            logger.error(f"Failed to fetch workflow runs: {e}")

        return runs

    def get_failed_runs(self, hours: int = 6) -> list[WorkflowRun]:
        """Get failed workflow runs from the last N hours."""
        all_runs = self.get_recent_runs(hours)
        return [r for r in all_runs if r.conclusion == "failure"]

    def get_run_logs(self, run_id: int) -> str:
        """Get logs for a specific workflow run using gh CLI."""
        try:
            result = subprocess.run(
                ["gh", "run", "view", str(run_id), "--log"],
                capture_output=True, text=True, timeout=60
            )
            return result.stdout + result.stderr
        except Exception as e:
            logger.warning(f"Failed to get logs for run {run_id}: {e}")
            return ""

    def classify_failure(self, run: WorkflowRun, logs: str = None) -> tuple[FailureCategory, Optional[str]]:
        """Classify a failure based on logs."""
        if logs is None:
            logs = self.get_run_logs(run.id)

        logs_lower = logs.lower()

        for pattern in FAILURE_PATTERNS:
            for regex in pattern.patterns:
                if re.search(regex, logs_lower):
                    return pattern.category, pattern.name

        return FailureCategory.UNKNOWN, None

    def should_retry(self, run: WorkflowRun, pattern_name: Optional[str]) -> bool:
        """Determine if a failed run should be retried."""
        if not pattern_name:
            return False

        pattern = next((p for p in FAILURE_PATTERNS if p.name == pattern_name), None)
        if not pattern or not pattern.auto_retry:
            return False

        # Check retry count
        current_retries = self.retry_tracker.get(run.id, 0)
        if current_retries >= pattern.max_retries:
            logger.info(f"Max retries ({pattern.max_retries}) reached for {run.name}")
            return False

        return True

    def retry_workflow(self, run: WorkflowRun) -> bool:
        """Retry a failed workflow run."""
        logger.info(f"Retrying workflow: {run.name} (run {run.id})")

        try:
            self._github_api(
                f"/repos/{self.repo}/actions/runs/{run.id}/rerun-failed-jobs",
                method="POST"
            )

            self.retry_tracker[run.id] = self.retry_tracker.get(run.id, 0) + 1

            self.actions_taken.append(RemediationAction(
                workflow_run_id=run.id,
                action_type="retry",
                description=f"Retried failed workflow: {run.name}",
                success=True,
                details={"retry_count": self.retry_tracker[run.id]}
            ))

            return True
        except Exception as e:
            logger.error(f"Failed to retry workflow {run.id}: {e}")
            return False

    def create_alert(self, run: WorkflowRun, category: FailureCategory, pattern_name: str) -> bool:
        """Create an alert for a failure requiring attention."""
        pattern = next((p for p in FAILURE_PATTERNS if p.name == pattern_name), None)
        description = pattern.description if pattern else "Unknown failure"

        alert_message = f"""
WORKFLOW FAILURE ALERT
======================
Workflow: {run.name}
Run ID: {run.id}
Branch: {run.head_branch}
Time: {run.created_at.isoformat()}
Category: {category.value}
Pattern: {pattern_name}
Description: {description}
URL: {run.html_url}

This failure requires manual attention.
"""

        logger.warning(alert_message)

        # Log to database if available
        try:
            from database.supabase_client import get_supabase_client
            db = get_supabase_client()
            db.client.table("errors").insert({
                "error_type": "workflow_failure",
                "severity": "high" if category in [FailureCategory.CREDENTIAL, FailureCategory.RESOURCE] else "medium",
                "message": f"{run.name}: {description}",
                "context": {
                    "run_id": run.id,
                    "workflow": run.name,
                    "category": category.value,
                    "pattern": pattern_name,
                    "url": run.html_url
                },
                "resolved": False
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to log alert to database: {e}")

        # Send email alert if configured
        self._send_email_alert(run, category, pattern_name, description)

        self.actions_taken.append(RemediationAction(
            workflow_run_id=run.id,
            action_type="alert",
            description=f"Alert created for {run.name}: {description}",
            success=True
        ))

        return True

    def _send_email_alert(self, run: WorkflowRun, category: FailureCategory,
                          pattern_name: str, description: str):
        """Send email alert for critical failures."""
        resend_key = os.environ.get("RESEND_API_KEY")
        alert_email = os.environ.get("ALERT_EMAIL")

        if not resend_key or not alert_email:
            return

        try:
            import resend
            resend.api_key = resend_key

            severity_emoji = "🔴" if category in [FailureCategory.CREDENTIAL, FailureCategory.RESOURCE] else "🟡"

            resend.Emails.send({
                "from": "alerts@socialmediaempire.com",
                "to": [alert_email],
                "subject": f"{severity_emoji} Workflow Guardian Alert: {run.name}",
                "html": f"""
                <h1>Workflow Failure Detected</h1>
                <table style="border-collapse: collapse;">
                    <tr><td><strong>Workflow:</strong></td><td>{run.name}</td></tr>
                    <tr><td><strong>Category:</strong></td><td>{category.value}</td></tr>
                    <tr><td><strong>Issue:</strong></td><td>{description}</td></tr>
                    <tr><td><strong>Time:</strong></td><td>{run.created_at.strftime('%Y-%m-%d %H:%M UTC')}</td></tr>
                    <tr><td><strong>Branch:</strong></td><td>{run.head_branch}</td></tr>
                </table>
                <p><a href="{run.html_url}">View workflow run</a></p>
                <p><strong>Pattern:</strong> {pattern_name}</p>
                <hr>
                <p><em>This alert was generated by the Workflow Guardian self-healing system.</em></p>
                """
            })
            logger.info(f"Email alert sent for {run.name}")
        except Exception as e:
            logger.warning(f"Failed to send email alert: {e}")

    def create_issue(self, run: WorkflowRun, category: FailureCategory,
                     pattern_name: str, logs_snippet: str = "") -> bool:
        """Create a GitHub issue for failures requiring code changes."""
        if not self.github_token:
            logger.warning("Cannot create issue without GITHUB_TOKEN")
            return False

        pattern = next((p for p in FAILURE_PATTERNS if p.name == pattern_name), None)
        description = pattern.description if pattern else "Unknown failure"

        # Truncate logs
        if len(logs_snippet) > 2000:
            logs_snippet = logs_snippet[:2000] + "\n... (truncated)"

        issue_body = f"""
## Workflow Failure Report

**Workflow:** {run.name}
**Run ID:** [{run.id}]({run.html_url})
**Category:** {category.value}
**Pattern:** {pattern_name}
**Time:** {run.created_at.isoformat()}

### Description
{description}

### Log Snippet
```
{logs_snippet}
```

### Suggested Actions
- Review the full workflow logs
- Check recent code changes that might have caused this
- Verify all required secrets are configured

---
*This issue was automatically created by the Workflow Guardian.*
"""

        try:
            self._github_api(
                f"/repos/{self.repo}/issues",
                method="POST",
                data={
                    "title": f"[Auto] Workflow Failure: {run.name} - {description}",
                    "body": issue_body,
                    "labels": ["bug", "automated", "workflow-failure"]
                }
            )

            self.actions_taken.append(RemediationAction(
                workflow_run_id=run.id,
                action_type="issue",
                description=f"Created issue for {run.name}",
                success=True
            ))

            return True
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            return False

    def analyze_and_heal(self, hours: int = 6, dry_run: bool = False) -> dict:
        """Main method: analyze all recent failures and take healing actions."""
        logger.info(f"Starting workflow analysis for last {hours} hours...")

        failed_runs = self.get_failed_runs(hours)
        logger.info(f"Found {len(failed_runs)} failed runs")

        results = {
            "analyzed": 0,
            "retried": 0,
            "alerted": 0,
            "issues_created": 0,
            "skipped": 0,
            "failures_by_category": {},
            "failures_by_workflow": {},
            "actions": []
        }

        for run in failed_runs:
            results["analyzed"] += 1

            # Get logs and classify
            logs = self.get_run_logs(run.id)
            category, pattern_name = self.classify_failure(run, logs)

            run.failure_category = category
            run.failure_pattern = pattern_name

            # Track by category
            cat_name = category.value
            results["failures_by_category"][cat_name] = results["failures_by_category"].get(cat_name, 0) + 1

            # Track by workflow
            results["failures_by_workflow"][run.name] = results["failures_by_workflow"].get(run.name, 0) + 1

            logger.info(f"Run {run.id} ({run.name}): {category.value} - {pattern_name or 'no pattern'}")

            if dry_run:
                results["skipped"] += 1
                continue

            # Take action based on category
            pattern = next((p for p in FAILURE_PATTERNS if p.name == pattern_name), None)

            if pattern and pattern.auto_retry and self.should_retry(run, pattern_name):
                if self.retry_workflow(run):
                    results["retried"] += 1
            elif pattern and pattern.alert_immediately:
                if self.create_alert(run, category, pattern_name):
                    results["alerted"] += 1
            elif category == FailureCategory.CODE:
                # Create issue for code problems
                logs_snippet = logs[-3000:] if logs else ""
                if self.create_issue(run, category, pattern_name, logs_snippet):
                    results["issues_created"] += 1
            elif category == FailureCategory.UNKNOWN:
                # Alert for unknown failures
                if self.create_alert(run, category, pattern_name or "unknown"):
                    results["alerted"] += 1
            else:
                results["skipped"] += 1

        results["actions"] = [
            {
                "run_id": a.workflow_run_id,
                "type": a.action_type,
                "description": a.description,
                "success": a.success
            }
            for a in self.actions_taken
        ]

        return results

    def get_health_summary(self) -> dict:
        """Get a summary of workflow health."""
        all_runs = self.get_recent_runs(hours=24)

        total = len(all_runs)
        successful = sum(1 for r in all_runs if r.conclusion == "success")
        failed = sum(1 for r in all_runs if r.conclusion == "failure")
        in_progress = sum(1 for r in all_runs if r.status in ["in_progress", "queued"])

        # Group by workflow
        by_workflow = {}
        for run in all_runs:
            if run.name not in by_workflow:
                by_workflow[run.name] = {"success": 0, "failure": 0, "other": 0}
            if run.conclusion == "success":
                by_workflow[run.name]["success"] += 1
            elif run.conclusion == "failure":
                by_workflow[run.name]["failure"] += 1
            else:
                by_workflow[run.name]["other"] += 1

        # Calculate health score (0-100)
        health_score = 100
        if total > 0:
            health_score = int((successful / total) * 100)

        return {
            "health_score": health_score,
            "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "unhealthy",
            "last_24h": {
                "total": total,
                "successful": successful,
                "failed": failed,
                "in_progress": in_progress
            },
            "by_workflow": by_workflow,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


def main():
    """CLI entry point for the workflow guardian."""
    import argparse

    parser = argparse.ArgumentParser(description="Workflow Guardian - Self-Healing System")
    parser.add_argument("--analyze", action="store_true", help="Analyze and heal recent failures")
    parser.add_argument("--health", action="store_true", help="Get health summary")
    parser.add_argument("--hours", type=int, default=6, help="Hours to look back (default: 6)")
    parser.add_argument("--dry-run", action="store_true", help="Analyze without taking actions")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    guardian = WorkflowGuardian()

    if args.health:
        result = guardian.get_health_summary()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"WORKFLOW HEALTH SUMMARY")
            print(f"{'='*50}")
            print(f"Health Score: {result['health_score']}%")
            print(f"Status: {result['status'].upper()}")
            print(f"\nLast 24 hours:")
            print(f"  Total runs: {result['last_24h']['total']}")
            print(f"  Successful: {result['last_24h']['successful']}")
            print(f"  Failed: {result['last_24h']['failed']}")
            print(f"  In Progress: {result['last_24h']['in_progress']}")
            print(f"\nBy Workflow:")
            for wf, stats in result['by_workflow'].items():
                print(f"  {wf}: {stats['success']} ok, {stats['failure']} failed")

    elif args.analyze:
        result = guardian.analyze_and_heal(hours=args.hours, dry_run=args.dry_run)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*50}")
            print(f"WORKFLOW GUARDIAN ANALYSIS")
            print(f"{'='*50}")
            print(f"Analyzed: {result['analyzed']} failed runs")
            print(f"Retried: {result['retried']}")
            print(f"Alerted: {result['alerted']}")
            print(f"Issues Created: {result['issues_created']}")
            print(f"Skipped: {result['skipped']}")

            if result['failures_by_category']:
                print(f"\nFailures by Category:")
                for cat, count in result['failures_by_category'].items():
                    print(f"  {cat}: {count}")

            if result['failures_by_workflow']:
                print(f"\nFailures by Workflow:")
                for wf, count in result['failures_by_workflow'].items():
                    print(f"  {wf}: {count}")

            if result['actions']:
                print(f"\nActions Taken:")
                for action in result['actions']:
                    status = "✓" if action['success'] else "✗"
                    print(f"  {status} [{action['type']}] {action['description']}")

    else:
        # Default: run analysis
        result = guardian.analyze_and_heal(hours=args.hours, dry_run=args.dry_run)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
