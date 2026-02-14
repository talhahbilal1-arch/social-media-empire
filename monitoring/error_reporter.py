"""Error reporting and alerting for Social Media Empire."""

import logging
import traceback
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field
import requests
import resend

from utils.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Error severity levels
SEVERITY_LEVELS = {
    "critical": {
        "alert_immediately": True,
        "color": "#FF0000",
        "emoji": "🚨"
    },
    "high": {
        "alert_immediately": True,
        "color": "#FF6600",
        "emoji": "⚠️"
    },
    "medium": {
        "alert_immediately": False,
        "color": "#FFCC00",
        "emoji": "📢"
    },
    "low": {
        "alert_immediately": False,
        "color": "#00CC00",
        "emoji": "ℹ️"
    }
}


@dataclass
class ErrorReport:
    """Structure for an error report."""
    error_type: str
    error_message: str
    severity: str = "medium"
    context: dict = field(default_factory=dict)
    stack_trace: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved: bool = False


@dataclass
class ErrorReporter:
    """Reports errors via email and logs to database."""

    alert_email: str = ""
    resend_api_key: str = ""

    def __post_init__(self):
        config = get_config()
        if not self.alert_email:
            self.alert_email = config.alert_email
        if not self.resend_api_key:
            self.resend_api_key = config.resend_api_key

        if self.resend_api_key:
            resend.api_key = self.resend_api_key

    def report(
        self,
        error_type: str,
        error_message: str,
        severity: str = "medium",
        context: Optional[dict] = None,
        exception: Optional[Exception] = None
    ) -> ErrorReport:
        """Report an error.

        Args:
            error_type: Category of error (e.g., "api_failure", "generation_error")
            error_message: Human-readable error message
            severity: "critical", "high", "medium", or "low"
            context: Additional context dict
            exception: Optional exception object

        Returns:
            ErrorReport object
        """
        stack_trace = None
        if exception:
            stack_trace = "".join(traceback.format_exception(
                type(exception), exception, exception.__traceback__
            ))

        report = ErrorReport(
            error_type=error_type,
            error_message=error_message,
            severity=severity,
            context=context or {},
            stack_trace=stack_trace
        )

        # Log to console
        logger.error(f"[{severity.upper()}] {error_type}: {error_message}")

        # Log to database
        self._log_to_database(report)

        # Email alerts disabled — all notifications consolidated to weekly summary
        # Self-healing runs every 6 hours to auto-resolve issues

        return report

    def _log_to_database(self, report: ErrorReport) -> None:
        """Log error to Supabase database."""
        try:
            from database.supabase_client import get_supabase_client
            db = get_supabase_client()

            db.log_error(
                error_type=report.error_type,
                error_message=report.error_message,
                context={
                    "severity": report.severity,
                    "context": report.context,
                    "stack_trace": report.stack_trace,
                    "timestamp": report.timestamp
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log error to database: {e}")

    def _send_email_alert(self, report: ErrorReport) -> None:
        """Send email alert for critical errors."""
        if not self.resend_api_key or not self.alert_email:
            logger.warning("Email alerting not configured")
            return

        severity_config = SEVERITY_LEVELS.get(report.severity, SEVERITY_LEVELS["medium"])

        subject = f"{severity_config['emoji']} [{report.severity.upper()}] {report.error_type}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: {severity_config['color']}; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">{severity_config['emoji']} Error Alert</h1>
            </div>

            <div style="padding: 20px;">
                <h2>Error Type: {report.error_type}</h2>
                <p><strong>Severity:</strong> {report.severity.upper()}</p>
                <p><strong>Timestamp:</strong> {report.timestamp}</p>

                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <h3>Error Message:</h3>
                    <p>{report.error_message}</p>
                </div>

                {"<div style='background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0;'>" +
                 "<h3>Context:</h3><pre>" + str(report.context) + "</pre></div>"
                 if report.context else ""}

                {"<div style='background: #f8d7da; padding: 15px; border-radius: 5px; margin: 15px 0;'>" +
                 "<h3>Stack Trace:</h3><pre style='overflow-x: auto; font-size: 12px;'>" +
                 report.stack_trace + "</pre></div>"
                 if report.stack_trace else ""}

                <hr>
                <p style="font-size: 12px; color: #666;">
                    This alert was sent automatically by Social Media Empire monitoring.
                </p>
            </div>
        </body>
        </html>
        """

        try:
            resend.Emails.send({
                "from": "alerts@socialmediaempire.com",
                "to": [self.alert_email],
                "subject": subject,
                "html": html_content
            })
            logger.info(f"Alert email sent to {self.alert_email}")
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")

    def report_exception(
        self,
        exception: Exception,
        context: Optional[dict] = None,
        severity: str = "high"
    ) -> ErrorReport:
        """Convenience method to report an exception."""
        return self.report(
            error_type=type(exception).__name__,
            error_message=str(exception),
            severity=severity,
            context=context,
            exception=exception
        )

    def get_recent_errors(self, limit: int = 50) -> list[dict]:
        """Get recent errors from database."""
        try:
            from database.supabase_client import get_supabase_client
            db = get_supabase_client()
            return db.get_unresolved_errors(limit=limit)
        except Exception as e:
            logger.error(f"Failed to get recent errors: {e}")
            return []

    def get_error_summary(self) -> dict:
        """Get summary of recent errors."""
        errors = self.get_recent_errors(limit=100)

        # Count by type
        by_type = {}
        for error in errors:
            error_type = error.get("error_type", "unknown")
            by_type[error_type] = by_type.get(error_type, 0) + 1

        # Count by severity
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for error in errors:
            context = error.get("context", {})
            severity = context.get("severity", "medium")
            if severity in by_severity:
                by_severity[severity] += 1

        return {
            "total_unresolved": len(errors),
            "by_type": by_type,
            "by_severity": by_severity,
            "most_recent": errors[0] if errors else None
        }

    def send_daily_error_digest(self) -> bool:
        """Send daily digest of errors."""
        if not self.alert_email:
            return False

        summary = self.get_error_summary()

        if summary["total_unresolved"] == 0:
            logger.info("No errors to report in daily digest")
            return True

        subject = f"📊 Daily Error Digest - {summary['total_unresolved']} Unresolved"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #333; color: white; padding: 20px; text-align: center;">
                <h1>Daily Error Digest</h1>
            </div>

            <div style="padding: 20px;">
                <h2>Summary</h2>
                <p><strong>Total Unresolved:</strong> {summary['total_unresolved']}</p>

                <h3>By Severity:</h3>
                <ul>
                    <li>🚨 Critical: {summary['by_severity']['critical']}</li>
                    <li>⚠️ High: {summary['by_severity']['high']}</li>
                    <li>📢 Medium: {summary['by_severity']['medium']}</li>
                    <li>ℹ️ Low: {summary['by_severity']['low']}</li>
                </ul>

                <h3>By Type:</h3>
                <ul>
                    {''.join([f"<li>{k}: {v}</li>" for k, v in summary['by_type'].items()])}
                </ul>

                <hr>
                <p style="font-size: 12px; color: #666;">
                    Review and resolve errors in the admin dashboard.
                </p>
            </div>
        </body>
        </html>
        """

        try:
            resend.Emails.send({
                "from": "alerts@socialmediaempire.com",
                "to": [self.alert_email],
                "subject": subject,
                "html": html_content
            })
            return True
        except Exception as e:
            logger.error(f"Failed to send daily digest: {e}")
            return False


# Singleton instance
_reporter: Optional[ErrorReporter] = None


def get_error_reporter() -> ErrorReporter:
    """Get or create the global ErrorReporter instance."""
    global _reporter
    if _reporter is None:
        _reporter = ErrorReporter()
    return _reporter


def report_error(
    error_type: str,
    error_message: str,
    severity: str = "medium",
    context: Optional[dict] = None,
    exception: Optional[Exception] = None
) -> ErrorReport:
    """Convenience function to report an error."""
    reporter = get_error_reporter()
    return reporter.report(
        error_type=error_type,
        error_message=error_message,
        severity=severity,
        context=context,
        exception=exception
    )


def main():
    """CLI entry point for error reporting."""
    import argparse

    parser = argparse.ArgumentParser(description="Error reporting utilities")
    parser.add_argument("--summary", action="store_true", help="Show error summary")
    parser.add_argument("--digest", action="store_true", help="Send daily digest")
    parser.add_argument("--test", action="store_true", help="Send test error")

    args = parser.parse_args()

    reporter = ErrorReporter()

    if args.summary:
        summary = reporter.get_error_summary()
        print(f"\nError Summary:")
        print(f"  Total Unresolved: {summary['total_unresolved']}")
        print(f"  By Severity: {summary['by_severity']}")
        print(f"  By Type: {summary['by_type']}")

    elif args.digest:
        success = reporter.send_daily_error_digest()
        print(f"Daily digest sent: {success}")

    elif args.test:
        report = reporter.report(
            error_type="test_error",
            error_message="This is a test error alert",
            severity="high",
            context={"test": True, "source": "cli"}
        )
        print(f"Test error reported: {report.error_type}")


if __name__ == "__main__":
    main()
