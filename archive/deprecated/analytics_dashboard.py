"""Analytics dashboard for Social Media Empire performance tracking."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from dataclasses import dataclass, field

from utils.config import get_config
from database.supabase_client import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AnalyticsDashboard:
    """Comprehensive analytics tracking and reporting."""

    def __post_init__(self):
        self.db = get_supabase_client()

    def get_overview(self, days: int = 7) -> dict:
        """Get overview metrics for all brands."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        return {
            "period": f"Last {days} days",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "videos": self._get_video_metrics(start_date, end_date),
            "engagement": self._get_engagement_metrics(start_date, end_date),
            "email": self._get_email_metrics(start_date, end_date),
            "revenue": self._get_revenue_metrics(start_date, end_date),
            "by_brand": self._get_brand_breakdown(start_date, end_date),
            "by_platform": self._get_platform_breakdown(start_date, end_date),
            "trends": self._get_trends(start_date, end_date)
        }

    def _get_video_metrics(self, start_date: datetime, end_date: datetime) -> dict:
        """Get video creation and posting metrics."""
        try:
            # Query videos created in period
            result = self.db.client.table("videos").select("*").gte(
                "created_at", start_date.isoformat()
            ).lte(
                "created_at", end_date.isoformat()
            ).execute()

            videos = result.data if result.data else []

            return {
                "total_created": len(videos),
                "successfully_posted": len([v for v in videos if v.get("status") == "posted"]),
                "failed": len([v for v in videos if v.get("status") == "failed"]),
                "pending": len([v for v in videos if v.get("status") == "pending"]),
                "avg_per_day": round(len(videos) / max((end_date - start_date).days, 1), 1)
            }
        except Exception as e:
            logger.warning(f"Error getting video metrics: {e}")
            return {"total_created": 0, "successfully_posted": 0, "failed": 0, "pending": 0, "avg_per_day": 0}

    def _get_engagement_metrics(self, start_date: datetime, end_date: datetime) -> dict:
        """Get engagement metrics across platforms."""
        try:
            result = self.db.client.table("analytics_events").select("*").eq(
                "event_type", "engagement"
            ).gte(
                "created_at", start_date.isoformat()
            ).execute()

            events = result.data if result.data else []

            total_views = sum(e.get("data", {}).get("views", 0) for e in events)
            total_likes = sum(e.get("data", {}).get("likes", 0) for e in events)
            total_comments = sum(e.get("data", {}).get("comments", 0) for e in events)
            total_shares = sum(e.get("data", {}).get("shares", 0) for e in events)

            return {
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "engagement_rate": round((total_likes + total_comments + total_shares) / max(total_views, 1) * 100, 2)
            }
        except Exception as e:
            logger.warning(f"Error getting engagement metrics: {e}")
            return {"total_views": 0, "total_likes": 0, "total_comments": 0, "total_shares": 0, "engagement_rate": 0}

    def _get_email_metrics(self, start_date: datetime, end_date: datetime) -> dict:
        """Get email marketing metrics."""
        try:
            result = self.db.client.table("analytics_events").select("*").eq(
                "event_type", "email_subscriber"
            ).gte(
                "created_at", start_date.isoformat()
            ).execute()

            subscribers = result.data if result.data else []

            return {
                "new_subscribers": len(subscribers),
                "by_brand": self._count_by_field(subscribers, "brand"),
                "by_lead_magnet": self._count_by_field(subscribers, "lead_magnet")
            }
        except Exception as e:
            logger.warning(f"Error getting email metrics: {e}")
            return {"new_subscribers": 0, "by_brand": {}, "by_lead_magnet": {}}

    def _get_revenue_metrics(self, start_date: datetime, end_date: datetime) -> dict:
        """Get revenue and conversion metrics."""
        try:
            result = self.db.client.table("analytics_events").select("*").in_(
                "event_type", ["affiliate_click", "affiliate_sale", "product_sale"]
            ).gte(
                "created_at", start_date.isoformat()
            ).execute()

            events = result.data if result.data else []

            affiliate_clicks = [e for e in events if e.get("event_type") == "affiliate_click"]
            affiliate_sales = [e for e in events if e.get("event_type") == "affiliate_sale"]
            product_sales = [e for e in events if e.get("event_type") == "product_sale"]

            affiliate_revenue = sum(e.get("data", {}).get("commission", 0) for e in affiliate_sales)
            product_revenue = sum(e.get("data", {}).get("amount", 0) for e in product_sales)

            return {
                "affiliate_clicks": len(affiliate_clicks),
                "affiliate_sales": len(affiliate_sales),
                "affiliate_revenue": round(affiliate_revenue, 2),
                "product_sales": len(product_sales),
                "product_revenue": round(product_revenue, 2),
                "total_revenue": round(affiliate_revenue + product_revenue, 2),
                "conversion_rate": round(len(affiliate_sales) / max(len(affiliate_clicks), 1) * 100, 2)
            }
        except Exception as e:
            logger.warning(f"Error getting revenue metrics: {e}")
            return {
                "affiliate_clicks": 0, "affiliate_sales": 0, "affiliate_revenue": 0,
                "product_sales": 0, "product_revenue": 0, "total_revenue": 0, "conversion_rate": 0
            }

    def _get_brand_breakdown(self, start_date: datetime, end_date: datetime) -> dict:
        """Get metrics broken down by brand."""
        brands = ["daily_deal_darling", "menopause_planner", "nurse_planner", "adhd_planner"]
        breakdown = {}

        for brand in brands:
            try:
                # Get videos for brand
                videos_result = self.db.client.table("videos").select("*").eq(
                    "brand", brand
                ).gte(
                    "created_at", start_date.isoformat()
                ).execute()

                videos = videos_result.data if videos_result.data else []

                # Get subscribers for brand
                subs_result = self.db.client.table("analytics_events").select("*").eq(
                    "event_type", "email_subscriber"
                ).eq(
                    "brand", brand
                ).gte(
                    "created_at", start_date.isoformat()
                ).execute()

                subs = subs_result.data if subs_result.data else []

                breakdown[brand] = {
                    "videos_created": len(videos),
                    "new_subscribers": len(subs),
                    "videos_posted": len([v for v in videos if v.get("status") == "posted"])
                }

            except Exception as e:
                logger.warning(f"Error getting brand breakdown for {brand}: {e}")
                breakdown[brand] = {"videos_created": 0, "new_subscribers": 0, "videos_posted": 0}

        return breakdown

    def _get_platform_breakdown(self, start_date: datetime, end_date: datetime) -> dict:
        """Get metrics broken down by platform."""
        platforms = ["youtube_shorts", "pinterest", "tiktok", "instagram_reels"]
        breakdown = {}

        for platform in platforms:
            try:
                result = self.db.client.table("videos").select("*").eq(
                    "platform", platform
                ).gte(
                    "created_at", start_date.isoformat()
                ).execute()

                videos = result.data if result.data else []

                breakdown[platform] = {
                    "videos_posted": len([v for v in videos if v.get("status") == "posted"]),
                    "failed": len([v for v in videos if v.get("status") == "failed"])
                }

            except Exception as e:
                logger.warning(f"Error getting platform breakdown for {platform}: {e}")
                breakdown[platform] = {"videos_posted": 0, "failed": 0}

        return breakdown

    def _get_trends(self, start_date: datetime, end_date: datetime) -> dict:
        """Get trend analysis."""
        # Calculate daily metrics for trend analysis
        days = (end_date - start_date).days
        daily_data = []

        for i in range(days):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)

            try:
                videos_result = self.db.client.table("videos").select("count", count="exact").gte(
                    "created_at", day_start.isoformat()
                ).lt(
                    "created_at", day_end.isoformat()
                ).execute()

                daily_data.append({
                    "date": day_start.strftime("%Y-%m-%d"),
                    "videos": videos_result.count if videos_result.count else 0
                })

            except Exception:
                daily_data.append({
                    "date": day_start.strftime("%Y-%m-%d"),
                    "videos": 0
                })

        return {
            "daily_videos": daily_data,
            "growth_direction": "up" if len(daily_data) > 1 and daily_data[-1]["videos"] > daily_data[0]["videos"] else "stable"
        }

    def _count_by_field(self, items: list, field: str) -> dict:
        """Count items by a specific field."""
        counts = {}
        for item in items:
            data = item.get("data", {})
            value = data.get(field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def generate_daily_report(self) -> dict:
        """Generate a daily performance report."""
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        today_metrics = self.get_overview(days=1)
        week_metrics = self.get_overview(days=7)

        return {
            "report_date": today.isoformat(),
            "summary": {
                "videos_today": today_metrics["videos"]["total_created"],
                "videos_this_week": week_metrics["videos"]["total_created"],
                "subscribers_today": today_metrics["email"]["new_subscribers"],
                "subscribers_this_week": week_metrics["email"]["new_subscribers"],
                "revenue_this_week": week_metrics["revenue"]["total_revenue"]
            },
            "highlights": self._generate_highlights(today_metrics, week_metrics),
            "alerts": self._generate_alerts(today_metrics),
            "recommendations": self._generate_recommendations(week_metrics)
        }

    def _generate_highlights(self, today: dict, week: dict) -> list[str]:
        """Generate report highlights."""
        highlights = []

        if today["videos"]["total_created"] > 0:
            highlights.append(f"Created {today['videos']['total_created']} videos today")

        if week["email"]["new_subscribers"] > 0:
            highlights.append(f"Gained {week['email']['new_subscribers']} new subscribers this week")

        if week["revenue"]["total_revenue"] > 0:
            highlights.append(f"Generated ${week['revenue']['total_revenue']} in revenue")

        # Find best performing brand
        brand_metrics = week.get("by_brand", {})
        if brand_metrics:
            best_brand = max(brand_metrics.items(), key=lambda x: x[1].get("videos_created", 0))
            highlights.append(f"Top brand: {best_brand[0]} with {best_brand[1]['videos_created']} videos")

        return highlights if highlights else ["No activity to report"]

    def _generate_alerts(self, metrics: dict) -> list[str]:
        """Generate alerts for issues."""
        alerts = []

        if metrics["videos"]["failed"] > 0:
            alerts.append(f"⚠️ {metrics['videos']['failed']} videos failed to post")

        if metrics["videos"]["total_created"] == 0:
            alerts.append("⚠️ No videos created today - check automation")

        return alerts

    def _generate_recommendations(self, metrics: dict) -> list[str]:
        """Generate recommendations based on metrics."""
        recommendations = []

        # Check engagement rate
        if metrics["engagement"]["engagement_rate"] < 5:
            recommendations.append("Consider testing different hook styles to improve engagement")

        # Check email growth
        if metrics["email"]["new_subscribers"] < 10:
            recommendations.append("Review lead magnet promotion - consider adding more CTAs")

        # Check revenue
        if metrics["revenue"]["affiliate_clicks"] > 0 and metrics["revenue"]["conversion_rate"] < 2:
            recommendations.append("Affiliate conversion is low - review product recommendations")

        return recommendations if recommendations else ["Keep up the great work!"]


def get_dashboard_html(dashboard: AnalyticsDashboard, days: int = 7) -> str:
    """Generate an HTML dashboard view."""
    metrics = dashboard.get_overview(days)

    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Social Media Empire Dashboard</title>
    <style>
        body {{ font-family: system-ui; margin: 0; padding: 20px; background: #f5f5f5; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 2rem; font-weight: bold; color: #E91E63; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <h1>📊 Social Media Empire Dashboard</h1>
        <p>Period: {metrics['period']}</p>

        <h2>Video Performance</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{metrics['videos']['total_created']}</div>
                <div class="metric-label">Videos Created</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['videos']['successfully_posted']}</div>
                <div class="metric-label">Successfully Posted</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['videos']['avg_per_day']}</div>
                <div class="metric-label">Avg Per Day</div>
            </div>
        </div>

        <h2>Email Marketing</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{metrics['email']['new_subscribers']}</div>
                <div class="metric-label">New Subscribers</div>
            </div>
        </div>

        <h2>Revenue</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">${metrics['revenue']['total_revenue']}</div>
                <div class="metric-label">Total Revenue</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['revenue']['affiliate_clicks']}</div>
                <div class="metric-label">Affiliate Clicks</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics['revenue']['conversion_rate']}%</div>
                <div class="metric-label">Conversion Rate</div>
            </div>
        </div>
    </div>
</body>
</html>'''


if __name__ == "__main__":
    dashboard = AnalyticsDashboard()
    report = dashboard.generate_daily_report()

    print("\n" + "="*60)
    print("DAILY PERFORMANCE REPORT")
    print("="*60)
    print(f"\nDate: {report['report_date']}")

    print("\n📊 SUMMARY:")
    for key, value in report['summary'].items():
        print(f"  • {key}: {value}")

    print("\n✨ HIGHLIGHTS:")
    for highlight in report['highlights']:
        print(f"  • {highlight}")

    if report['alerts']:
        print("\n⚠️ ALERTS:")
        for alert in report['alerts']:
            print(f"  • {alert}")

    print("\n💡 RECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
