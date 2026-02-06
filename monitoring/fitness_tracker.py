"""Fitness-focused tracking and analytics for the pivoted business.

Tracks the metrics that matter for revenue:
- Pins posted per day
- Website clicks from Pinterest
- Email signups
- Affiliate clicks
- Product sales
- Conversion rates
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

from utils.config import get_config

logger = logging.getLogger(__name__)


@dataclass
class FitnessMetrics:
    """Weekly business metrics snapshot."""
    period_start: str
    period_end: str
    pins_posted: int = 0
    pinterest_impressions: int = 0
    outbound_clicks: int = 0
    email_signups: int = 0
    affiliate_clicks: int = 0
    affiliate_revenue: float = 0.0
    product_sales: int = 0
    product_revenue: float = 0.0
    total_revenue: float = 0.0
    articles_published: int = 0
    youtube_views: int = 0

    @property
    def click_through_rate(self) -> float:
        if self.pinterest_impressions == 0:
            return 0.0
        return self.outbound_clicks / self.pinterest_impressions

    @property
    def email_conversion_rate(self) -> float:
        if self.outbound_clicks == 0:
            return 0.0
        return self.email_signups / self.outbound_clicks

    @property
    def revenue_per_click(self) -> float:
        if self.outbound_clicks == 0:
            return 0.0
        return self.total_revenue / self.outbound_clicks


def track_pin_posted(brand: str, platform: str, pin_url: str = "", destination_url: str = "") -> dict:
    """Log a pin/video posted to a platform.

    Args:
        brand: Brand identifier (fitnessmadeasy)
        platform: Platform name (pinterest, youtube_shorts)
        pin_url: URL of the posted pin
        destination_url: Where the pin links to

    Returns:
        Result dict with tracking ID
    """
    try:
        from database.supabase_client import get_supabase_client
        db = get_supabase_client()

        db.log_analytics_event(
            event_type="pin_posted",
            brand=brand,
            platform=platform,
            data={
                "pin_url": pin_url,
                "destination_url": destination_url,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        logger.info(f"Tracked pin posted: {brand} on {platform}")
        return {"success": True}

    except Exception as e:
        logger.error(f"Failed to track pin: {e}")
        return {"success": False, "error": str(e)}


def track_email_signup(email: str, source: str = "website", lead_magnet: str = "7-day-kickstart") -> dict:
    """Log an email signup.

    Args:
        email: Subscriber email (hashed for privacy)
        source: Where they signed up from
        lead_magnet: Which lead magnet they opted into

    Returns:
        Result dict
    """
    try:
        from database.supabase_client import get_supabase_client
        db = get_supabase_client()

        db.log_analytics_event(
            event_type="email_signup",
            brand="fitnessmadeasy",
            platform=source,
            data={
                "lead_magnet": lead_magnet,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        logger.info(f"Tracked email signup from {source}")
        return {"success": True}

    except Exception as e:
        logger.error(f"Failed to track signup: {e}")
        return {"success": False, "error": str(e)}


def track_affiliate_click(product_name: str, affiliate_url: str, network: str) -> dict:
    """Log an affiliate link click."""
    try:
        from database.supabase_client import get_supabase_client
        db = get_supabase_client()

        db.log_analytics_event(
            event_type="affiliate_click",
            brand="fitnessmadeasy",
            platform=network,
            data={
                "product": product_name,
                "url": affiliate_url,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        return {"success": True}

    except Exception as e:
        logger.error(f"Failed to track affiliate click: {e}")
        return {"success": False, "error": str(e)}


def generate_weekly_summary() -> str:
    """Generate a weekly business metrics summary.

    Returns:
        Formatted summary string for email/report
    """
    try:
        from database.supabase_client import get_supabase_client
        db = get_supabase_client()

        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)

        # Query analytics events for the past week
        # Pins posted
        pins = db.count_analytics_events("pin_posted", since=week_ago.isoformat())
        signups = db.count_analytics_events("email_signup", since=week_ago.isoformat())
        aff_clicks = db.count_analytics_events("affiliate_click", since=week_ago.isoformat())
        articles = db.count_analytics_events("article_published", since=week_ago.isoformat())

        summary = f"""
=== FITOVER35 WEEKLY BUSINESS METRICS ===
Period: {week_ago.strftime('%b %d')} - {now.strftime('%b %d, %Y')}

CONTENT OUTPUT
  Pins posted:         {pins}
  Articles published:  {articles}
  Target pins/week:    35-105 (5-15/day)

FUNNEL METRICS
  Email signups:       {signups}
  Affiliate clicks:    {aff_clicks}

REVENUE
  Affiliate revenue:   $0.00 (manual tracking needed)
  Product sales:       $0.00 (connect Gumroad webhook)

STATUS
  {"ON TRACK" if pins >= 35 else "BELOW TARGET"}: Pin output
  {"ON TRACK" if signups >= 5 else "NEEDS WORK"}: Email signups

NEXT ACTIONS
  - Review top-performing pins on Pinterest Analytics
  - Check affiliate dashboard for conversion data
  - Ensure all articles have affiliate product sections
=============================================
"""
        return summary

    except Exception as e:
        logger.error(f"Failed to generate weekly summary: {e}")
        return f"Weekly summary generation failed: {e}"
