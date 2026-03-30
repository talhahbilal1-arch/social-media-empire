"""Pin Performance Tracker — Aggregates pin metrics from Supabase.

Queries pinterest_pins and pinterest_analytics tables to identify:
- Top-performing pin styles, topics, and posting times
- Brand-level performance breakdowns
- Weekly trends and growth patterns

Stores aggregated results back to the analytics table and generates
a weekly report saved to ~/tall-command-center/briefings/.

Usage:
    python -m analytics.pin_tracker
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_client import get_supabase_client

BRANDS = ["fitness", "deals", "menopause"]
BRAND_LABELS = {
    "fitness": "FitOver35",
    "deals": "Daily Deal Darling",
    "menopause": "Menopause Planner",
}


def get_pins_for_period(db, start_date: str, end_date: str) -> list:
    """Fetch all pinterest_pins created within a date range."""
    try:
        result = db.client.table("pinterest_pins") \
            .select("*") \
            .gte("created_at", start_date + "T00:00:00Z") \
            .lte("created_at", end_date + "T23:59:59Z") \
            .execute()
        return result.data or []
    except Exception as e:
        print(f"  Error fetching pins: {e}")
        return []


def get_pinterest_analytics(db, start_date: str, end_date: str) -> list:
    """Fetch pinterest_analytics records for the period."""
    try:
        result = db.client.table("pinterest_analytics") \
            .select("*") \
            .gte("collected_at", start_date + "T00:00:00Z") \
            .lte("collected_at", end_date + "T23:59:59Z") \
            .execute()
        return result.data or []
    except Exception as e:
        print(f"  Error fetching pinterest_analytics: {e}")
        return []


def get_content_history(db, start_date: str, end_date: str) -> list:
    """Fetch content_history records for the period."""
    try:
        result = db.client.table("content_history") \
            .select("*") \
            .gte("created_at", start_date + "T00:00:00Z") \
            .lte("created_at", end_date + "T23:59:59Z") \
            .execute()
        return result.data or []
    except Exception as e:
        print(f"  Error fetching content_history: {e}")
        return []


def analyze_pins(pins: list) -> dict:
    """Analyze pin data to find patterns and top performers."""
    by_brand = defaultdict(list)
    by_status = defaultdict(int)
    by_style = defaultdict(int)
    by_topic = defaultdict(int)

    for pin in pins:
        brand = pin.get("brand", "unknown")
        by_brand[brand].append(pin)
        by_status[pin.get("status", "unknown")] += 1

        style = pin.get("visual_style", "unknown")
        if style and style != "unknown":
            by_style[style] += 1

        topic = pin.get("topic") or pin.get("niche", "")
        if topic:
            by_topic[topic] += 1

    # Brand summaries
    brand_summary = {}
    for brand in BRANDS:
        brand_pins = by_brand.get(brand, [])
        posted = [p for p in brand_pins if p.get("status") == "posted"]
        failed = [p for p in brand_pins if p.get("status") == "failed"]
        brand_summary[brand] = {
            "total": len(brand_pins),
            "posted": len(posted),
            "failed": len(failed),
            "success_rate": round(len(posted) / max(len(brand_pins), 1) * 100, 1),
        }

    # Top topics (sorted by frequency)
    top_topics = sorted(by_topic.items(), key=lambda x: x[1], reverse=True)[:10]

    # Top styles
    top_styles = sorted(by_style.items(), key=lambda x: x[1], reverse=True)

    return {
        "total_pins": len(pins),
        "brand_summary": brand_summary,
        "status_breakdown": dict(by_status),
        "top_topics": top_topics,
        "top_styles": top_styles,
    }


def analyze_board_analytics(analytics_records: list) -> dict:
    """Aggregate board-level analytics (impressions, saves, clicks)."""
    brand_totals = defaultdict(lambda: {
        "impressions": 0, "saves": 0, "clicks": 0, "pin_clicks": 0, "boards": 0
    })

    for record in analytics_records:
        brand = record.get("brand", "unknown")
        brand_totals[brand]["impressions"] += record.get("impressions", 0)
        brand_totals[brand]["saves"] += record.get("saves", 0)
        brand_totals[brand]["clicks"] += record.get("clicks", 0)
        brand_totals[brand]["pin_clicks"] += record.get("pin_clicks", 0)
        brand_totals[brand]["boards"] += 1

    return dict(brand_totals)


def save_weekly_summary(db, summary: dict) -> None:
    """Save the weekly analytics summary to Supabase analytics table."""
    try:
        for brand in BRANDS:
            brand_data = summary.get("brand_summary", {}).get(brand, {})
            db.client.table("analytics").insert({
                "brand": brand,
                "platform": "pinterest",
                "metric_name": "weekly_pins_total",
                "metric_value": brand_data.get("total", 0),
                "event_type": "weekly_summary",
                "data": json.dumps(brand_data),
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
        print("  Weekly summary saved to Supabase analytics table")
    except Exception as e:
        print(f"  Error saving weekly summary: {e}")


def generate_report(pin_analysis: dict, board_analytics: dict,
                    start_date: str, end_date: str) -> str:
    """Generate a human-readable weekly performance report."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"  PIN PERFORMANCE REPORT")
    lines.append(f"  Period: {start_date} to {end_date}")
    lines.append(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("=" * 60)
    lines.append("")

    # Overall
    lines.append(f"TOTAL PINS: {pin_analysis['total_pins']}")
    lines.append("")

    # Per-brand breakdown
    lines.append("--- BRAND BREAKDOWN ---")
    for brand in BRANDS:
        label = BRAND_LABELS.get(brand, brand)
        data = pin_analysis["brand_summary"].get(brand, {})
        lines.append(f"  {label}:")
        lines.append(f"    Total: {data.get('total', 0)}")
        lines.append(f"    Posted: {data.get('posted', 0)}")
        lines.append(f"    Failed: {data.get('failed', 0)}")
        lines.append(f"    Success Rate: {data.get('success_rate', 0)}%")

        # Board analytics if available
        ba = board_analytics.get(brand, {})
        if ba.get("impressions", 0) > 0 or ba.get("clicks", 0) > 0:
            lines.append(f"    Impressions: {ba.get('impressions', 0):,}")
            lines.append(f"    Saves: {ba.get('saves', 0):,}")
            lines.append(f"    Clicks: {ba.get('clicks', 0):,}")
            lines.append(f"    Pin Clicks: {ba.get('pin_clicks', 0):,}")
        lines.append("")

    # Status breakdown
    lines.append("--- STATUS BREAKDOWN ---")
    for status, count in pin_analysis["status_breakdown"].items():
        lines.append(f"  {status}: {count}")
    lines.append("")

    # Top topics
    if pin_analysis["top_topics"]:
        lines.append("--- TOP 10 TOPICS ---")
        for i, (topic, count) in enumerate(pin_analysis["top_topics"], 1):
            lines.append(f"  {i}. {topic} ({count} pins)")
        lines.append("")

    # Top styles
    if pin_analysis["top_styles"]:
        lines.append("--- PIN STYLES ---")
        for style, count in pin_analysis["top_styles"]:
            lines.append(f"  {style}: {count} pins")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def save_report(report_text: str, filename: str) -> str:
    """Save report to ~/tall-command-center/briefings/."""
    briefings_dir = Path.home() / "tall-command-center" / "briefings"
    briefings_dir.mkdir(parents=True, exist_ok=True)
    filepath = briefings_dir / filename
    filepath.write_text(report_text, encoding="utf-8")
    print(f"  Report saved to {filepath}")
    return str(filepath)


def main():
    """Run weekly pin performance tracking."""
    print("=== Pin Performance Tracker ===")
    print(f"  Started: {datetime.now(timezone.utc).isoformat()}")

    db = get_supabase_client()

    # Date range: last 7 days
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    start_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    print(f"  Period: {start_date} to {end_date}")

    # Fetch data
    print("\n  Fetching pins...")
    pins = get_pins_for_period(db, start_date, end_date)
    print(f"  Found {len(pins)} pins")

    print("  Fetching board analytics...")
    analytics_records = get_pinterest_analytics(db, start_date, end_date)
    print(f"  Found {len(analytics_records)} analytics records")

    # Analyze
    print("\n  Analyzing...")
    pin_analysis = analyze_pins(pins)
    board_analytics = analyze_board_analytics(analytics_records)

    # Save summary to Supabase
    save_weekly_summary(db, pin_analysis)

    # Generate and save report
    report = generate_report(pin_analysis, board_analytics, start_date, end_date)
    print(report)

    date_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    save_report(report, f"pin-performance-{date_tag}.txt")

    # Update agent_runs
    try:
        db.client.table("agent_runs").upsert({
            "agent_name": "pin_tracker",
            "last_run_at": datetime.now(timezone.utc).isoformat(),
            "status": "success",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="agent_name").execute()
    except Exception:
        pass

    print("\n=== Pin Tracker Complete ===")


if __name__ == "__main__":
    main()
