"""Daily report generation for Social Media Empire."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from dataclasses import dataclass
import resend

from utils.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DailyReportGenerator:
    """Generates and sends daily performance reports."""

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

    def generate_report(self, date: Optional[str] = None) -> dict:
        """Generate daily report data.

        Args:
            date: Date string (YYYY-MM-DD), defaults to today

        Returns:
            Report data dict
        """
        if not date:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Gather data from various sources
        video_stats = self._get_video_stats(date)
        email_stats = self._get_email_stats(date)
        error_stats = self._get_error_stats(date)
        health_status = self._get_health_status()
        pinterest_stats = self._get_pinterest_analytics(date)

        # Calculate overall health score
        health_score = self._calculate_health_score(
            video_stats, email_stats, error_stats, health_status
        )

        return {
            "date": date,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "health_score": health_score,
            "videos": video_stats,
            "email": email_stats,
            "errors": error_stats,
            "system_health": health_status,
            "pinterest": pinterest_stats,
            "brands": self._get_brand_breakdown(date)
        }

    def _get_video_stats(self, date: str) -> dict:
        """Get video generation statistics."""
        try:
            from database.supabase_client import get_supabase_client
            db = get_supabase_client()

            stats = db.get_daily_stats(date)

            return {
                "created": stats.get("videos_created", 0),
                "target": 12,  # 3 videos x 4 brands
                "completion_rate": min(100, (stats.get("videos_created", 0) / 12) * 100),
                "by_brand": stats.get("videos_by_brand", {}),
                "by_platform": stats.get("videos_by_platform", {})
            }
        except Exception as e:
            logger.error(f"Failed to get video stats: {e}")
            return {"created": 0, "target": 12, "completion_rate": 0, "error": str(e)}

    def _get_email_stats(self, date: str) -> dict:
        """Get email marketing statistics."""
        try:
            from database.supabase_client import get_supabase_client
            db = get_supabase_client()

            stats = db.get_daily_stats(date)

            return {
                "new_subscribers": stats.get("new_subscribers", 0),
                "by_brand": stats.get("subscribers_by_brand", {}),
                "emails_sent": 0,  # Would come from email provider API
                "open_rate": 0,    # Would come from email provider API
            }
        except Exception as e:
            logger.error(f"Failed to get email stats: {e}")
            return {"new_subscribers": 0, "error": str(e)}

    def _get_error_stats(self, date: str) -> dict:
        """Get error statistics."""
        try:
            from database.supabase_client import get_supabase_client
            db = get_supabase_client()

            errors = db.get_unresolved_errors(limit=100)

            # Count today's errors
            today_errors = [
                e for e in errors
                if e.get("created_at", "").startswith(date)
            ]

            # Categorize by severity
            critical = sum(1 for e in today_errors if "critical" in str(e.get("context", {})))
            high = sum(1 for e in today_errors if "high" in str(e.get("context", {})))

            return {
                "total_today": len(today_errors),
                "total_unresolved": len(errors),
                "critical": critical,
                "high": high,
                "requires_attention": critical + high > 0
            }
        except Exception as e:
            logger.error(f"Failed to get error stats: {e}")
            return {"total_today": 0, "error": str(e)}

    def _get_pinterest_analytics(self, date: str) -> dict:
        """Get latest Pinterest board analytics from weekly collection."""
        try:
            from database.supabase_client import get_supabase_client
            db = get_supabase_client()

            # Get latest analytics for each brand
            analytics_by_brand = {}

            # Query latest pinterest_analytics records for each brand
            result = db.client.table("pinterest_analytics").select(
                "brand, board_name, impressions, saves, clicks, pin_clicks, collected_at"
            ).order("collected_at", desc=True).limit(20).execute()

            if result.data:
                # Group by brand, keep only latest per brand
                latest_by_brand = {}
                for record in result.data:
                    brand = record.get("brand")
                    if brand not in latest_by_brand:
                        latest_by_brand[brand] = record

                # Aggregate metrics per brand
                for brand, record in latest_by_brand.items():
                    analytics_by_brand[brand] = {
                        "impressions": record.get("impressions", 0),
                        "saves": record.get("saves", 0),
                        "clicks": record.get("clicks", 0),
                        "pin_clicks": record.get("pin_clicks", 0),
                        "collected_at": record.get("collected_at", "N/A")
                    }

            return {
                "by_brand": analytics_by_brand,
                "total_impressions": sum(
                    b.get("impressions", 0) for b in analytics_by_brand.values()
                ),
                "total_saves": sum(
                    b.get("saves", 0) for b in analytics_by_brand.values()
                ),
                "last_collected": max(
                    (b.get("collected_at") for b in analytics_by_brand.values()),
                    default="Never"
                )
            }
        except Exception as e:
            logger.error(f"Failed to get Pinterest analytics: {e}")
            return {
                "by_brand": {},
                "total_impressions": 0,
                "total_saves": 0,
                "last_collected": "N/A",
                "error": str(e)
            }

    def _get_health_status(self) -> dict:
        """Get current system health status."""
        try:
            from .health_checker import run_health_check
            return run_health_check(full=False)
        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {"healthy": False, "error": str(e)}

    def _get_brand_breakdown(self, date: str) -> dict:
        """Get per-brand statistics."""
        config = get_config()
        brands = {}

        try:
            from database.supabase_client import get_supabase_client
            db = get_supabase_client()

            for brand in config.brands:
                videos = db.get_recent_videos(brand=brand, limit=10)
                today_videos = [
                    v for v in videos
                    if v.get("created_at", "").startswith(date)
                ]

                brands[brand] = {
                    "videos_today": len(today_videos),
                    "target": 3,
                    "status": "on_track" if len(today_videos) >= 3 else "behind"
                }
        except Exception as e:
            logger.error(f"Failed to get brand breakdown: {e}")

        return brands

    def _calculate_health_score(
        self,
        video_stats: dict,
        email_stats: dict,
        error_stats: dict,
        health_status: dict
    ) -> int:
        """Calculate overall health score (0-100)."""
        score = 100

        # Video completion (40 points)
        video_completion = video_stats.get("completion_rate", 0)
        score -= max(0, 40 - (video_completion * 0.4))

        # System health (30 points)
        if not health_status.get("healthy", False):
            unhealthy = sum(
                1 for c in health_status.get("checks", [])
                if c.get("status") != "healthy"
            )
            score -= min(30, unhealthy * 10)

        # Errors (30 points)
        if error_stats.get("critical", 0) > 0:
            score -= 20
        if error_stats.get("high", 0) > 0:
            score -= min(10, error_stats.get("high", 0) * 5)

        return max(0, int(score))

    def send_report(self, report: Optional[dict] = None) -> bool:
        """Send daily report via email.

        Args:
            report: Optional pre-generated report, generates fresh if not provided

        Returns:
            True if sent successfully
        """
        if not self.alert_email:
            logger.warning("No alert email configured")
            return False

        if not report:
            report = self.generate_report()

        # Determine emoji based on health score
        score = report.get("health_score", 0)
        if score >= 90:
            status_emoji = "🟢"
            status_text = "Excellent"
        elif score >= 70:
            status_emoji = "🟡"
            status_text = "Good"
        elif score >= 50:
            status_emoji = "🟠"
            status_text = "Needs Attention"
        else:
            status_emoji = "🔴"
            status_text = "Critical"

        subject = f"{status_emoji} Daily Report - {report['date']} - Score: {score}/100"

        html_content = self._generate_html_report(report, status_emoji, status_text)

        try:
            resend.Emails.send({
                "from": "reports@socialmediaempire.com",
                "to": [self.alert_email],
                "subject": subject,
                "html": html_content
            })
            logger.info(f"Daily report sent to {self.alert_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send daily report: {e}")
            return False

    def _generate_html_report(
        self,
        report: dict,
        status_emoji: str,
        status_text: str
    ) -> str:
        """Generate HTML content for the report email."""
        video_stats = report.get("videos", {})
        email_stats = report.get("email", {})
        error_stats = report.get("errors", {})
        pinterest_stats = report.get("pinterest", {})
        brands = report.get("brands", {})

        # Brand rows
        brand_rows = ""
        for brand, data in brands.items():
            status_color = "#28a745" if data.get("status") == "on_track" else "#dc3545"
            brand_rows += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{brand.replace('_', ' ').title()}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{data.get('videos_today', 0)}/{data.get('target', 3)}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center; color: {status_color};">{data.get('status', 'unknown').replace('_', ' ').title()}</td>
            </tr>
            """

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0;">Social Media Empire</h1>
                <h2 style="margin: 10px 0 0 0;">Daily Performance Report</h2>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">{report['date']}</p>
            </div>

            <div style="background: #f8f9fa; padding: 20px; text-align: center;">
                <div style="font-size: 48px;">{status_emoji}</div>
                <div style="font-size: 24px; font-weight: bold;">Health Score: {report.get('health_score', 0)}/100</div>
                <div style="color: #666;">{status_text}</div>
            </div>

            <div style="padding: 20px;">
                <h2 style="border-bottom: 2px solid #667eea; padding-bottom: 10px;">📹 Video Content</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 36px; font-weight: bold; color: #1976d2;">{video_stats.get('created', 0)}</div>
                        <div>Videos Created</div>
                    </div>
                    <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 36px; font-weight: bold; color: #388e3c;">{video_stats.get('completion_rate', 0):.0f}%</div>
                        <div>Completion Rate</div>
                    </div>
                </div>

                <h3>Brand Breakdown</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <tr style="background: #f5f5f5;">
                        <th style="padding: 10px; text-align: left;">Brand</th>
                        <th style="padding: 10px; text-align: center;">Videos</th>
                        <th style="padding: 10px; text-align: center;">Status</th>
                    </tr>
                    {brand_rows}
                </table>

                <h2 style="border-bottom: 2px solid #667eea; padding-bottom: 10px;">📧 Email Marketing</h2>
                <div style="background: #fff3e0; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 36px; font-weight: bold; color: #e65100;">{email_stats.get('new_subscribers', 0)}</div>
                    <div>New Subscribers Today</div>
                </div>

                <h2 style="border-bottom: 2px solid #667eea; padding-bottom: 10px;">📌 Pinterest Analytics</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="background: #f3e5f5; padding: 20px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 36px; font-weight: bold; color: #7b1fa2;">{pinterest_stats.get('total_impressions', 0):,}</div>
                        <div>Total Impressions</div>
                    </div>
                    <div style="background: #e1f5fe; padding: 20px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 36px; font-weight: bold; color: #0277bd;">{pinterest_stats.get('total_saves', 0):,}</div>
                        <div>Total Saves</div>
                    </div>
                </div>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; font-size: 12px; margin-bottom: 20px;">
                    <strong>Last Collected:</strong> {pinterest_stats.get('last_collected', 'Never')}
                </div>

                <h2 style="border-bottom: 2px solid #667eea; padding-bottom: 10px;">⚠️ Errors & Issues</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="background: {'#ffebee' if error_stats.get('critical', 0) > 0 else '#f5f5f5'}; padding: 20px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold;">{error_stats.get('critical', 0)}</div>
                        <div>Critical Errors</div>
                    </div>
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 24px; font-weight: bold;">{error_stats.get('total_unresolved', 0)}</div>
                        <div>Unresolved Total</div>
                    </div>
                </div>

                {'<div style="background: #ffebee; padding: 15px; border-radius: 8px; border-left: 4px solid #f44336;">' +
                 '<strong>⚠️ Action Required:</strong> There are critical errors that need attention.</div>'
                 if error_stats.get('requires_attention') else ''}
            </div>

            <div style="background: #f5f5f5; padding: 20px; text-align: center; border-radius: 0 0 10px 10px;">
                <p style="margin: 0; color: #666; font-size: 12px;">
                    Generated at {report.get('generated_at', 'Unknown')}<br>
                    Social Media Empire Automation System
                </p>
            </div>
        </body>
        </html>
        """

        return html


def generate_daily_report(date: Optional[str] = None, send: bool = False) -> dict:
    """Generate daily report, optionally sending via email."""
    generator = DailyReportGenerator()
    report = generator.generate_report(date)

    if send:
        generator.send_report(report)

    return report


def main():
    """CLI entry point for daily reports."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Generate daily reports")
    parser.add_argument("--date", help="Date for report (YYYY-MM-DD)")
    parser.add_argument("--send", action="store_true", help="Send report via email")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    report = generate_daily_report(date=args.date, send=args.send)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"DAILY REPORT - {report['date']}")
        print(f"{'='*50}")
        print(f"Health Score: {report['health_score']}/100")
        print(f"\nVideos: {report['videos'].get('created', 0)}/{report['videos'].get('target', 12)}")
        print(f"New Subscribers: {report['email'].get('new_subscribers', 0)}")
        print(f"Errors: {report['errors'].get('total_today', 0)} today, {report['errors'].get('total_unresolved', 0)} unresolved")

        if args.send:
            print("\n✓ Report sent via email")


if __name__ == "__main__":
    main()
