"""Daily Revenue Report — Generates a daily briefing with key metrics.

Queries Supabase for:
- Daily pin count and article count per brand
- Error count and unresolved errors
- Week-over-week growth percentages
- Anomaly detection (drops > 30%, zero-output days)

Outputs to ~/tall-command-center/briefings/daily-report-YYYY-MM-DD.txt

Usage:
    python -m analytics.daily_report
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone
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

# Anomaly thresholds
DROP_THRESHOLD = 0.30  # 30% drop triggers alert
EXPECTED_DAILY_PINS = 5  # Per brand


def count_pins_for_date(db, date_str: str, brand: str) -> int:
    """Count pins posted on a specific date for a brand."""
    try:
        result = db.client.table("content_history") \
            .select("id", count="exact") \
            .eq("brand", brand) \
            .gte("created_at", date_str + "T00:00:00Z") \
            .lte("created_at", date_str + "T23:59:59Z") \
            .execute()
        return result.count if result.count else 0
    except Exception:
        return 0


def count_articles_for_date(db, date_str: str, brand: str = None) -> int:
    """Count articles generated on a specific date."""
    try:
        query = db.client.table("generated_articles") \
            .select("id", count="exact") \
            .gte("created_at", date_str + "T00:00:00Z") \
            .lte("created_at", date_str + "T23:59:59Z")
        if brand:
            query = query.eq("brand", brand)
        result = query.execute()
        return result.count if result.count else 0
    except Exception:
        return 0


def count_errors_for_date(db, date_str: str) -> dict:
    """Count errors on a specific date, broken down by severity."""
    try:
        result = db.client.table("errors") \
            .select("severity") \
            .gte("created_at", date_str + "T00:00:00Z") \
            .lte("created_at", date_str + "T23:59:59Z") \
            .execute()
        errors = result.data or []
        breakdown = {"high": 0, "medium": 0, "low": 0}
        for err in errors:
            sev = err.get("severity", "medium")
            breakdown[sev] = breakdown.get(sev, 0) + 1
        return {
            "total": len(errors),
            "by_severity": breakdown,
        }
    except Exception:
        return {"total": 0, "by_severity": {}}


def get_unresolved_errors(db) -> list:
    """Get recent unresolved errors."""
    try:
        result = db.client.table("errors") \
            .select("error_type, error_message, severity, created_at") \
            .eq("resolved", False) \
            .order("created_at", desc=True) \
            .limit(10) \
            .execute()
        return result.data or []
    except Exception:
        return []


def calculate_growth(current: int, previous: int) -> str:
    """Calculate week-over-week growth percentage."""
    if previous == 0:
        if current == 0:
            return "0%"
        return "+100% (new)"
    pct = ((current - previous) / previous) * 100
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.0f}%"


def detect_anomalies(today_pins: dict, last_week_pins: dict,
                     today_errors: dict) -> list:
    """Detect anomalies that need attention."""
    anomalies = []

    for brand in BRANDS:
        today_count = today_pins.get(brand, 0)
        last_week_count = last_week_pins.get(brand, 0)

        # Zero-output day
        if today_count == 0:
            anomalies.append({
                "type": "ZERO_OUTPUT",
                "brand": brand,
                "message": f"{BRAND_LABELS[brand]}: No pins posted today",
                "severity": "high",
            })

        # Drop > 30%
        if last_week_count > 0:
            drop_pct = (last_week_count - today_count) / last_week_count
            if drop_pct > DROP_THRESHOLD:
                anomalies.append({
                    "type": "OUTPUT_DROP",
                    "brand": brand,
                    "message": (
                        f"{BRAND_LABELS[brand]}: Pin output dropped "
                        f"{drop_pct:.0%} vs same day last week "
                        f"({today_count} vs {last_week_count})"
                    ),
                    "severity": "medium",
                })

    # High error count
    if today_errors.get("total", 0) >= 5:
        anomalies.append({
            "type": "ERROR_SPIKE",
            "brand": "all",
            "message": f"Error spike: {today_errors['total']} errors today",
            "severity": "high",
        })

    return anomalies


def get_agent_status(db) -> list:
    """Get status of all known agents."""
    try:
        result = db.client.table("agent_runs") \
            .select("agent_name, last_run_at, status") \
            .order("last_run_at", desc=True) \
            .execute()
        return result.data or []
    except Exception:
        return []


def generate_report(today_str: str, today_pins: dict, today_articles: dict,
                    last_week_pins: dict, last_week_articles: dict,
                    today_errors: dict, unresolved: list,
                    anomalies: list, agents: list) -> str:
    """Generate the daily report text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"  DAILY REVENUE REPORT")
    lines.append(f"  Date: {today_str}")
    lines.append(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("=" * 60)

    # Anomalies first (if any)
    if anomalies:
        lines.append("")
        lines.append("!!! ANOMALIES DETECTED !!!")
        for a in anomalies:
            lines.append(f"  [{a['severity'].upper()}] {a['message']}")
        lines.append("")

    # Pin output
    lines.append("")
    lines.append("--- PINS POSTED TODAY ---")
    total_today = 0
    total_last_week = 0
    for brand in BRANDS:
        label = BRAND_LABELS[brand]
        t = today_pins.get(brand, 0)
        lw = last_week_pins.get(brand, 0)
        growth = calculate_growth(t, lw)
        total_today += t
        total_last_week += lw
        lines.append(f"  {label}: {t} pins (WoW: {growth})")

    lines.append(f"  TOTAL: {total_today} pins (WoW: {calculate_growth(total_today, total_last_week)})")

    # Articles
    lines.append("")
    lines.append("--- ARTICLES GENERATED TODAY ---")
    total_art_today = 0
    total_art_lw = 0
    for brand in BRANDS:
        label = BRAND_LABELS[brand]
        t = today_articles.get(brand, 0)
        lw = last_week_articles.get(brand, 0)
        growth = calculate_growth(t, lw)
        total_art_today += t
        total_art_lw += lw
        lines.append(f"  {label}: {t} articles (WoW: {growth})")

    lines.append(f"  TOTAL: {total_art_today} articles (WoW: {calculate_growth(total_art_today, total_art_lw)})")

    # Errors
    lines.append("")
    lines.append("--- ERRORS ---")
    lines.append(f"  Today: {today_errors.get('total', 0)} errors")
    sev = today_errors.get("by_severity", {})
    if sev:
        lines.append(f"    High: {sev.get('high', 0)} | Medium: {sev.get('medium', 0)} | Low: {sev.get('low', 0)}")

    if unresolved:
        lines.append(f"  Unresolved ({len(unresolved)}):")
        for err in unresolved[:5]:
            msg = (err.get("error_message", ""))[:60]
            lines.append(f"    - [{err.get('severity', '?')}] {err.get('error_type', '?')}: {msg}")
        if len(unresolved) > 5:
            lines.append(f"    ... and {len(unresolved) - 5} more")

    # Agent status
    if agents:
        lines.append("")
        lines.append("--- AGENT STATUS ---")
        for agent in agents:
            name = agent.get("agent_name", "?")
            status = agent.get("status", "?")
            last_run = agent.get("last_run_at", "never")
            if last_run and last_run != "never":
                last_run = last_run[:19].replace("T", " ")
            lines.append(f"  {name}: {status} (last: {last_run})")

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
    """Run daily revenue report generation."""
    print("=== Daily Revenue Report ===")
    print(f"  Started: {datetime.now(timezone.utc).isoformat()}")

    db = get_supabase_client()

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    last_week_str = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

    # Collect today's data
    print("\n  Collecting today's metrics...")
    today_pins = {}
    today_articles = {}
    last_week_pins = {}
    last_week_articles = {}

    for brand in BRANDS:
        today_pins[brand] = count_pins_for_date(db, today_str, brand)
        today_articles[brand] = count_articles_for_date(db, today_str, brand)
        last_week_pins[brand] = count_pins_for_date(db, last_week_str, brand)
        last_week_articles[brand] = count_articles_for_date(db, last_week_str, brand)
        print(f"  {BRAND_LABELS[brand]}: {today_pins[brand]} pins, {today_articles[brand]} articles")

    # Errors
    print("  Collecting error data...")
    today_errors = count_errors_for_date(db, today_str)
    unresolved = get_unresolved_errors(db)
    print(f"  Errors today: {today_errors['total']}, Unresolved: {len(unresolved)}")

    # Agent status
    agents = get_agent_status(db)

    # Anomaly detection
    anomalies = detect_anomalies(today_pins, last_week_pins, today_errors)
    if anomalies:
        print(f"\n  !!! {len(anomalies)} anomalies detected !!!")
        for a in anomalies:
            print(f"    [{a['severity']}] {a['message']}")

    # Generate report
    report = generate_report(
        today_str, today_pins, today_articles,
        last_week_pins, last_week_articles,
        today_errors, unresolved, anomalies, agents,
    )
    print(report)

    save_report(report, f"daily-report-{today_str}.txt")

    # Log to analytics table
    try:
        db.client.table("analytics").insert({
            "brand": "all",
            "platform": "system",
            "metric_name": "daily_report",
            "metric_value": sum(today_pins.values()),
            "event_type": "daily_report",
            "data": json.dumps({
                "pins": today_pins,
                "articles": today_articles,
                "errors": today_errors["total"],
                "anomalies": len(anomalies),
            }),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as e:
        print(f"  Warning: Could not log to analytics: {e}")

    # Update agent_runs
    try:
        db.client.table("agent_runs").upsert({
            "agent_name": "daily_report",
            "last_run_at": datetime.now(timezone.utc).isoformat(),
            "status": "success",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="agent_name").execute()
    except Exception:
        pass

    print("\n=== Daily Report Complete ===")


if __name__ == "__main__":
    main()
