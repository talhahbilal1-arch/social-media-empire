"""
Daily Report Agent - Sends daily summary email with system stats
================================================================
Runs once daily at 7:00 AM UTC to compile and send a comprehensive
report of system activity, content generation, and any issues.

Sections:
- Executive Summary (health status, key metrics)
- Content Generation (ideas, blogs, videos)
- Social Posting (by platform)
- Errors & Issues
- Trends Discovered
"""
import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient


class DailyReport:
    """
    Compiles and sends daily system report.

    Gathers stats from all tables for the last 24 hours
    and sends a formatted HTML email summary.
    """

    REPORT_WINDOW_HOURS = 24

    def __init__(self):
        self.db = SupabaseClient()
        self.email_from = os.environ.get('ALERT_EMAIL_FROM')
        self.email_password = os.environ.get('ALERT_EMAIL_PASSWORD')
        self.email_to = os.environ.get('ALERT_EMAIL_TO')

    def run(self) -> Dict:
        """Main entry point - compile and send daily report."""
        print(f"Starting Daily Report at {datetime.utcnow().isoformat()}")

        run_id = self.db.start_agent_run('daily_report', os.environ.get('GITHUB_RUN_ID'))

        results = {
            'report_date': datetime.utcnow().strftime('%Y-%m-%d'),
            'stats': {},
            'email_sent': False,
            'errors': []
        }

        try:
            # Gather all stats
            stats = self._gather_all_stats()
            results['stats'] = stats

            # Build and send email
            html = self._build_email_html(stats)
            sent = self._send_report(html, stats)
            results['email_sent'] = sent

            if sent:
                print("Daily report email sent successfully")
            else:
                print("Failed to send daily report email (email not configured)")

            # Complete run
            self.db.complete_agent_run(
                run_id,
                status='completed',
                items_processed=1,
                items_created=1 if sent else 0
            )

        except Exception as e:
            results['errors'].append(str(e))
            self.db.complete_agent_run(run_id, status='failed', error_log=[str(e)])
            raise

        return results

    def _gather_all_stats(self) -> Dict:
        """Gather stats from all tables."""
        hours = self.REPORT_WINDOW_HOURS

        stats = {
            'period_hours': hours,
            'generated_at': datetime.utcnow().isoformat(),
            'content': self.db.get_content_stats(hours),
            'videos': self.db.get_video_stats(hours),
            'posts': self.db.get_posting_stats(hours),
            'blogs': self.db.get_blog_stats(hours),
            'trends': self.db.get_trend_stats(hours),
            'agent_runs': self.db.get_agent_run_stats(hours),
        }

        # Calculate health status
        failed_runs = stats['agent_runs']['failed']
        stats['health'] = 'healthy' if failed_runs == 0 else 'issues' if failed_runs < 3 else 'critical'

        return stats

    def _build_email_html(self, stats: Dict) -> str:
        """Build HTML email content."""
        health_color = {
            'healthy': '#28a745',
            'issues': '#ffc107',
            'critical': '#dc3545'
        }.get(stats['health'], '#6c757d')

        health_icon = {
            'healthy': '&#9989;',  # Green checkmark
            'issues': '&#9888;',   # Warning
            'critical': '&#10060;' # Red X
        }.get(stats['health'], '&#8226;')

        # Build agent status rows
        agent_rows = ""
        for agent, data in stats['agent_runs'].get('by_agent', {}).items():
            status_color = '#28a745' if data['failed'] == 0 else '#dc3545'
            agent_rows += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{agent}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">{data['completed']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center; color: {status_color};">{data['failed']}</td>
            </tr>"""

        # Build platform posting rows
        platform_rows = ""
        for platform, count in stats['posts'].get('by_platform', {}).items():
            platform_rows += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{platform.title()}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">{count}</td>
            </tr>"""

        if not platform_rows:
            platform_rows = """
            <tr>
                <td colspan="2" style="padding: 8px; color: #666; text-align: center;">No posts logged yet</td>
            </tr>"""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">

        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">Social Media Empire</h1>
            <p style="margin: 10px 0 0; opacity: 0.9;">Daily Report - {datetime.utcnow().strftime('%B %d, %Y')}</p>
        </div>

        <!-- Executive Summary -->
        <div style="padding: 25px; border-bottom: 1px solid #eee;">
            <h2 style="margin: 0 0 20px; color: #333; font-size: 18px;">Executive Summary</h2>

            <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
                <div style="flex: 1; min-width: 120px; background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: {health_color};">{health_icon}</div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">System Health</div>
                    <div style="font-size: 14px; font-weight: 500; color: {health_color};">{stats['health'].upper()}</div>
                </div>
                <div style="flex: 1; min-width: 120px; background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #667eea;">{stats['content']['total']}</div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">Content Ideas</div>
                </div>
                <div style="flex: 1; min-width: 120px; background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #667eea;">{stats['posts']['posted']}</div>
                    <div style="font-size: 12px; color: #666; margin-top: 5px;">Posts Published</div>
                </div>
            </div>
        </div>

        <!-- Content Generation -->
        <div style="padding: 25px; border-bottom: 1px solid #eee;">
            <h2 style="margin: 0 0 15px; color: #333; font-size: 18px;">Content Generation</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; color: #666;">Content Ideas Created</td>
                    <td style="padding: 8px 0; text-align: right; font-weight: 500;">{stats['content']['total']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #666;">Blog Articles</td>
                    <td style="padding: 8px 0; text-align: right; font-weight: 500;">{stats['blogs']['published']} published / {stats['blogs']['total']} total</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #666;">Videos Rendered</td>
                    <td style="padding: 8px 0; text-align: right; font-weight: 500;">{stats['videos']['ready']} ready / {stats['videos']['total']} total</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #666;">Trends Discovered</td>
                    <td style="padding: 8px 0; text-align: right; font-weight: 500;">{stats['trends']['total']} ({stats['trends']['used']} used)</td>
                </tr>
            </table>
        </div>

        <!-- Social Posting -->
        <div style="padding: 25px; border-bottom: 1px solid #eee;">
            <h2 style="margin: 0 0 15px; color: #333; font-size: 18px;">Social Posting</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f8f9fa;">
                        <th style="padding: 10px; text-align: left; font-weight: 500;">Platform</th>
                        <th style="padding: 10px; text-align: center; font-weight: 500;">Posts</th>
                    </tr>
                </thead>
                <tbody>
                    {platform_rows}
                </tbody>
            </table>
            <p style="margin: 15px 0 0; font-size: 13px; color: #666;">
                Total: {stats['posts']['posted']} posted, {stats['posts']['failed']} failed
            </p>
        </div>

        <!-- Agent Runs -->
        <div style="padding: 25px; border-bottom: 1px solid #eee;">
            <h2 style="margin: 0 0 15px; color: #333; font-size: 18px;">Agent Status</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f8f9fa;">
                        <th style="padding: 10px; text-align: left; font-weight: 500;">Agent</th>
                        <th style="padding: 10px; text-align: center; font-weight: 500;">Completed</th>
                        <th style="padding: 10px; text-align: center; font-weight: 500;">Failed</th>
                    </tr>
                </thead>
                <tbody>
                    {agent_rows}
                </tbody>
            </table>
            <p style="margin: 15px 0 0; font-size: 13px; color: #666;">
                Total: {stats['agent_runs']['total']} runs ({stats['agent_runs']['failed']} failures)
            </p>
        </div>

        <!-- Footer -->
        <div style="padding: 20px; background: #f8f9fa; text-align: center; font-size: 12px; color: #666;">
            <p style="margin: 0;">Report generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            <p style="margin: 5px 0 0;">Social Media Content Empire - Autonomous Marketing System</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _send_report(self, html: str, stats: Dict) -> bool:
        """Send the report email."""
        if not all([self.email_from, self.email_password, self.email_to]):
            print("Email not configured - skipping send")
            print(f"Stats summary: {json.dumps(stats, indent=2)}")
            return False

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Daily Report - {datetime.utcnow().strftime('%B %d, %Y')} - {stats['health'].upper()}"
            msg['From'] = self.email_from
            msg['To'] = self.email_to

            # Plain text version
            text = f"""
Social Media Empire - Daily Report
{datetime.utcnow().strftime('%B %d, %Y')}

System Health: {stats['health'].upper()}

Content Generated: {stats['content']['total']}
Posts Published: {stats['posts']['posted']}
Blog Articles: {stats['blogs']['published']}
Videos Ready: {stats['videos']['ready']}
Trends Found: {stats['trends']['total']}

Agent Runs: {stats['agent_runs']['total']} ({stats['agent_runs']['failed']} failures)
"""

            msg.attach(MIMEText(text, 'plain'))
            msg.attach(MIMEText(html, 'html'))

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.email_from, self.email_password)
                server.sendmail(self.email_from, self.email_to, msg.as_string())

            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False


def main():
    """Entry point for GitHub Actions."""
    report = DailyReport()
    results = report.run()

    print(f"\nResults: {json.dumps(results, indent=2, default=str)}")

    return results


if __name__ == '__main__':
    main()
