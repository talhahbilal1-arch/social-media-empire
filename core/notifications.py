"""
Notifications - Email alerts for system health
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional


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
