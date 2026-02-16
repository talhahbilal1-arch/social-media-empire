"""
Notifications - Email alerts for system health

Rules:
- NO email for any error seen fewer than 10 consecutive times
- NO email for successful health checks
- NO email for warnings that auto-resolve
- SEND email ONLY when:
  - Same error has failed to self-heal 10 consecutive times
  - A critical agent has been down for 48+ hours
  - The self-healer itself crashes
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List


def send_alert(subject: str,
               message: str,
               severity: str = "warning",
               details: Optional[dict] = None) -> bool:
    """
    Send an email alert when something goes wrong.

    Uses Gmail SMTP. Requires these environment variables:
    - ALERT_EMAIL_FROM: Gmail address to send from
    - ALERT_EMAIL_PASSWORD: Gmail app password (not regular password)
    - ALERT_EMAIL_TO: Email address to send alerts to

    Returns True if sent successfully, False otherwise.
    """
    email_from = os.environ.get('ALERT_EMAIL_FROM')
    email_password = os.environ.get('ALERT_EMAIL_PASSWORD')
    email_to = os.environ.get('ALERT_EMAIL_TO')

    # If email not configured, just log and return
    if not all([email_from, email_password, email_to]):
        print(f"[ALERT - {severity.upper()}] {subject}")
        print(f"Message: {message}")
        if details:
            print(f"Details: {details}")
        return False

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[{severity.upper()}] Social Media Empire: {subject}"
        msg['From'] = email_from
        msg['To'] = email_to

        # Plain text version
        text_content = f"""
Social Media Content Empire Alert
==================================

Severity: {severity.upper()}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

{message}
"""
        if details:
            text_content += f"\nDetails:\n{_format_details(details)}"

        # HTML version
        severity_color = {
            'info': '#17a2b8',
            'warning': '#ffc107',
            'error': '#dc3545',
            'critical': '#721c24'
        }.get(severity, '#6c757d')

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ background: {severity_color}; color: white; padding: 20px; }}
        .header h1 {{ margin: 0; font-size: 20px; }}
        .content {{ padding: 20px; }}
        .timestamp {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
        .message {{ font-size: 16px; line-height: 1.6; margin-bottom: 20px; }}
        .details {{ background: #f8f9fa; border-radius: 4px; padding: 15px; font-family: monospace; font-size: 13px; white-space: pre-wrap; }}
        .footer {{ padding: 15px 20px; background: #f8f9fa; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Social Media Empire Alert</h1>
        </div>
        <div class="content">
            <p class="timestamp">{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <div class="message">{message.replace(chr(10), '<br>')}</div>
            {"<div class='details'>" + _format_details_html(details) + "</div>" if details else ""}
        </div>
        <div class="footer">
            This is an automated alert from your Social Media Content Empire system.
        </div>
    </div>
</body>
</html>
"""

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        # Send via Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_from, email_password)
            server.sendmail(email_from, email_to, msg.as_string())

        print(f"Alert sent: {subject}")
        return True

    except Exception as e:
        print(f"Failed to send alert: {e}")
        print(f"[ALERT - {severity.upper()}] {subject}: {message}")
        return False


def _format_details(details: dict) -> str:
    """Format details dict for plain text."""
    lines = []
    for key, value in details.items():
        lines.append(f"  {key}: {value}")
    return "\n".join(lines)


def _format_details_html(details: dict) -> str:
    """Format details dict for HTML."""
    lines = []
    for key, value in details.items():
        lines.append(f"<strong>{key}:</strong> {value}")
    return "<br>".join(lines)


def send_daily_summary(stats: dict) -> bool:
    """
    Send a daily summary email (optional, for visibility).
    Only sends if explicitly enabled via SEND_DAILY_SUMMARY=true
    """
    if os.environ.get('SEND_DAILY_SUMMARY', '').lower() != 'true':
        return False

    subject = f"Daily Summary - {datetime.utcnow().strftime('%Y-%m-%d')}"

    message = f"""
Your Social Media Empire ran successfully today!

Content Generated: {stats.get('content_generated', 0)}
Videos Created: {stats.get('videos_created', 0)}
Posts Published: {stats.get('posts_published', 0)}
Blog Articles: {stats.get('blogs_published', 0)}

Top Performing Content:
{stats.get('top_content', 'No data yet')}

System Health: All agents running normally
"""

    return send_alert(subject, message, severity="info", details=stats)


# ==========================================
# THRESHOLD-BASED NOTIFICATION SYSTEM
# ==========================================

# Critical agents that warrant faster alerting
CRITICAL_AGENTS = ['content_brain', 'video_factory', 'content_pipeline']

# Minimum consecutive failures before sending email
FAILURE_THRESHOLD = 10

# Minimum hours between re-notifications for the same error
NOTIFICATION_COOLDOWN_HOURS = 24


def should_send_alert(agent_name: str,
                      consecutive_failures: int,
                      hours_down: float = 0,
                      last_notified_at: Optional[str] = None) -> bool:
    """
    Determine whether to send an email alert based on failure threshold rules.

    Returns True ONLY when:
    - The same error has failed to self-heal 10+ consecutive times
    - A critical agent has been down for 48+ hours
    - Respects 24-hour cooldown between re-notifications
    """
    # Check cooldown - don't re-notify within 24 hours
    if last_notified_at:
        try:
            last_notified = datetime.fromisoformat(last_notified_at.replace('Z', '+00:00')).replace(tzinfo=None)
            hours_since_notify = (datetime.utcnow() - last_notified).total_seconds() / 3600
            if hours_since_notify < NOTIFICATION_COOLDOWN_HOURS:
                return False
        except (ValueError, TypeError):
            pass

    # Critical agents: alert if down for 48+ hours regardless of failure count
    if agent_name in CRITICAL_AGENTS and hours_down >= 48:
        return True

    # Standard threshold: 10 consecutive failures
    if consecutive_failures >= FAILURE_THRESHOLD:
        return True

    return False


def send_critical_alert(agent_name: str,
                        error_message: str,
                        consecutive_failures: int,
                        timestamps: Optional[List[str]] = None,
                        suggested_fix: str = "") -> bool:
    """
    Send a critical alert email for persistent failures.

    Subject format: EMPIRE CRITICAL: [agent_name] failed 10x -- needs manual fix
    Body includes: error message, attempt count, last 3 timestamps, suggested fix.
    """
    subject = f"EMPIRE CRITICAL: {agent_name} failed {consecutive_failures}x -- needs manual fix"

    # Format timestamps
    ts_text = "No timestamp data"
    if timestamps:
        ts_text = "\n".join([f"  - {ts}" for ts in timestamps[-3:]])

    message = f"""CRITICAL ALERT: {agent_name} has failed {consecutive_failures} consecutive times.

Error Message:
  {error_message}

Consecutive Failures: {consecutive_failures}
Last 3 Failure Timestamps:
{ts_text}

Suggested Manual Fix:
  {suggested_fix or 'Check GitHub Actions logs and Supabase dashboard for details.'}

This alert was sent because the self-healer could not resolve this issue after {consecutive_failures} attempts.
Manual intervention is required.
"""

    return send_alert(
        subject=subject,
        message=message,
        severity="critical",
        details={
            'agent': agent_name,
            'consecutive_failures': consecutive_failures,
            'error': error_message[:200]
        }
    )
