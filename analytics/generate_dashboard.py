"""Dashboard Generator — Creates a static HTML dashboard from Supabase data.

Queries Supabase for pins, articles, errors, and agent status,
then generates outputs/dashboard.html with a clean dark-themed design.

Usage:
    python -m analytics.generate_dashboard
"""

import os
import sys
import json
from datetime import datetime, timedelta, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_client import get_supabase_client

BRANDS = ["fitness", "deals", "menopause"]
BRAND_LABELS = {
    "fitness": "FitOver35",
    "deals": "Daily Deal Darling",
    "menopause": "Menopause Planner",
}
BRAND_COLORS = {
    "fitness": "#2563eb",
    "deals": "#8b5cf6",
    "menopause": "#ec4899",
}
BRAND_SITES = {
    "fitness": "https://fitover35.com",
    "deals": "https://dailydealdarling.com",
    "menopause": "https://menopause-planner-website.vercel.app",
}


def get_total_pins_by_brand(db) -> dict:
    """Get total pin count per brand from content_history."""
    counts = {}
    for brand in BRANDS:
        try:
            result = db.client.table("content_history") \
                .select("id", count="exact") \
                .eq("brand", brand) \
                .execute()
            counts[brand] = result.count if result.count else 0
        except Exception:
            counts[brand] = 0
    return counts


def get_total_articles_by_brand(db) -> dict:
    """Get total article count per brand from generated_articles."""
    counts = {}
    for brand in BRANDS:
        try:
            result = db.client.table("generated_articles") \
                .select("id", count="exact") \
                .eq("brand", brand) \
                .execute()
            counts[brand] = result.count if result.count else 0
        except Exception:
            counts[brand] = 0
    return counts


def get_pins_last_7_days(db) -> dict:
    """Get pin count per brand for the last 7 days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    counts = {}
    for brand in BRANDS:
        try:
            result = db.client.table("content_history") \
                .select("id", count="exact") \
                .eq("brand", brand) \
                .gte("created_at", cutoff + "T00:00:00Z") \
                .execute()
            counts[brand] = result.count if result.count else 0
        except Exception:
            counts[brand] = 0
    return counts


def get_recent_errors(db, limit: int = 5) -> list:
    """Get most recent unresolved errors."""
    try:
        result = db.client.table("errors") \
            .select("error_type, error_message, severity, created_at") \
            .eq("resolved", False) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return result.data or []
    except Exception:
        return []


def get_agent_status(db) -> list:
    """Get all agent run statuses."""
    try:
        result = db.client.table("agent_runs") \
            .select("agent_name, last_run_at, status") \
            .order("last_run_at", desc=True) \
            .execute()
        return result.data or []
    except Exception:
        return []


def get_recent_pins(db, limit: int = 10) -> list:
    """Get most recently posted pins."""
    try:
        result = db.client.table("pinterest_pins") \
            .select("brand, title, status, created_at, destination_url") \
            .eq("status", "posted") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return result.data or []
    except Exception:
        return []


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    if not text:
        return ""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def generate_html(total_pins: dict, total_articles: dict,
                  pins_7d: dict, errors: list, agents: list,
                  recent_pins: list) -> str:
    """Generate the dashboard HTML."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Build metric cards
    cards_html = ""
    for brand in BRANDS:
        label = BRAND_LABELS[brand]
        color = BRAND_COLORS[brand]
        site = BRAND_SITES[brand]
        pins = total_pins.get(brand, 0)
        articles = total_articles.get(brand, 0)
        week_pins = pins_7d.get(brand, 0)
        cards_html += f"""
        <div class="card" style="border-top: 4px solid {color};">
            <h3>{escape_html(label)}</h3>
            <a href="{site}" target="_blank" class="site-link">{site}</a>
            <div class="metrics">
                <div class="metric">
                    <span class="metric-value">{pins:,}</span>
                    <span class="metric-label">Total Pins</span>
                </div>
                <div class="metric">
                    <span class="metric-value">{articles:,}</span>
                    <span class="metric-label">Total Articles</span>
                </div>
                <div class="metric">
                    <span class="metric-value">{week_pins}</span>
                    <span class="metric-label">Pins (7d)</span>
                </div>
            </div>
        </div>"""

    # Build error rows
    error_rows = ""
    if errors:
        for err in errors:
            sev = err.get("severity", "medium")
            sev_class = "severity-high" if sev == "high" else ("severity-medium" if sev == "medium" else "severity-low")
            msg = escape_html((err.get("error_message", ""))[:80])
            etype = escape_html(err.get("error_type", ""))
            created = (err.get("created_at", ""))[:19].replace("T", " ")
            error_rows += f"""
            <tr>
                <td><span class="badge {sev_class}">{sev}</span></td>
                <td>{etype}</td>
                <td>{msg}</td>
                <td>{created}</td>
            </tr>"""
    else:
        error_rows = '<tr><td colspan="4" class="no-data">No unresolved errors</td></tr>'

    # Build agent rows
    agent_rows = ""
    if agents:
        for agent in agents:
            name = escape_html(agent.get("agent_name", ""))
            status = agent.get("status", "unknown")
            status_class = "status-success" if status == "success" else ("status-idle" if status == "idle" else "status-error")
            last_run = (agent.get("last_run_at") or "never")[:19].replace("T", " ")
            agent_rows += f"""
            <tr>
                <td>{name}</td>
                <td><span class="badge {status_class}">{status}</span></td>
                <td>{last_run}</td>
            </tr>"""
    else:
        agent_rows = '<tr><td colspan="3" class="no-data">No agent data</td></tr>'

    # Build recent pins
    recent_html = ""
    if recent_pins:
        for pin in recent_pins:
            brand = pin.get("brand", "")
            color = BRAND_COLORS.get(brand, "#666")
            title = escape_html((pin.get("title", ""))[:60])
            created = (pin.get("created_at", ""))[:10]
            dest = pin.get("destination_url", "#")
            recent_html += f"""
            <div class="pin-item">
                <span class="pin-brand" style="color: {color};">{BRAND_LABELS.get(brand, brand)}</span>
                <a href="{escape_html(dest)}" target="_blank" class="pin-title">{title}</a>
                <span class="pin-date">{created}</span>
            </div>"""
    else:
        recent_html = '<div class="no-data">No recent pins</div>'

    # Totals
    total_all_pins = sum(total_pins.values())
    total_all_articles = sum(total_articles.values())
    total_7d_pins = sum(pins_7d.values())

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Media Empire - Analytics Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid #1e293b;
            margin-bottom: 30px;
        }}
        header h1 {{ font-size: 28px; color: #f8fafc; margin-bottom: 5px; }}
        header .subtitle {{ color: #94a3b8; font-size: 14px; }}
        .summary {{
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .summary-item {{
            background: #1e293b;
            padding: 20px 30px;
            border-radius: 12px;
            text-align: center;
        }}
        .summary-item .value {{
            font-size: 36px;
            font-weight: 700;
            color: #f8fafc;
        }}
        .summary-item .label {{
            font-size: 13px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 24px;
        }}
        .card h3 {{ font-size: 18px; margin-bottom: 4px; color: #f8fafc; }}
        .site-link {{ color: #94a3b8; font-size: 12px; text-decoration: none; }}
        .site-link:hover {{ color: #e2e8f0; }}
        .metrics {{ display: flex; gap: 20px; margin-top: 16px; }}
        .metric {{ text-align: center; flex: 1; }}
        .metric-value {{ display: block; font-size: 28px; font-weight: 700; color: #f8fafc; }}
        .metric-label {{ display: block; font-size: 12px; color: #94a3b8; text-transform: uppercase; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{
            font-size: 18px;
            color: #f8fafc;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #1e293b;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ text-align: left; padding: 10px 12px; color: #94a3b8; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid #1e293b; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #1e293b; font-size: 14px; }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        .severity-high {{ background: #7f1d1d; color: #fca5a5; }}
        .severity-medium {{ background: #78350f; color: #fcd34d; }}
        .severity-low {{ background: #14532d; color: #86efac; }}
        .status-success {{ background: #14532d; color: #86efac; }}
        .status-idle {{ background: #1e293b; color: #94a3b8; }}
        .status-error {{ background: #7f1d1d; color: #fca5a5; }}
        .no-data {{ text-align: center; color: #64748b; padding: 20px; }}
        .pin-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 0;
            border-bottom: 1px solid #1e293b;
        }}
        .pin-brand {{ font-size: 12px; font-weight: 600; min-width: 120px; }}
        .pin-title {{ color: #e2e8f0; text-decoration: none; flex: 1; font-size: 14px; }}
        .pin-title:hover {{ color: #93c5fd; }}
        .pin-date {{ color: #64748b; font-size: 12px; }}
        footer {{ text-align: center; padding: 20px 0; color: #475569; font-size: 12px; }}
        @media (max-width: 768px) {{
            .grid {{ grid-template-columns: 1fr; }}
            .summary {{ flex-direction: column; align-items: center; }}
            .metrics {{ flex-direction: column; gap: 10px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Social Media Empire</h1>
            <div class="subtitle">Analytics Dashboard | Last updated: {now}</div>
        </header>

        <div class="summary">
            <div class="summary-item">
                <div class="value">{total_all_pins:,}</div>
                <div class="label">Total Pins</div>
            </div>
            <div class="summary-item">
                <div class="value">{total_all_articles:,}</div>
                <div class="label">Total Articles</div>
            </div>
            <div class="summary-item">
                <div class="value">{total_7d_pins}</div>
                <div class="label">Pins (7 Days)</div>
            </div>
            <div class="summary-item">
                <div class="value">{len(errors)}</div>
                <div class="label">Open Errors</div>
            </div>
        </div>

        <div class="grid">
            {cards_html}
        </div>

        <div class="section">
            <h2>Recent Pins</h2>
            {recent_html}
        </div>

        <div class="section">
            <h2>Unresolved Errors</h2>
            <table>
                <thead><tr><th>Severity</th><th>Type</th><th>Message</th><th>Date</th></tr></thead>
                <tbody>{error_rows}</tbody>
            </table>
        </div>

        <div class="section">
            <h2>Agent Status</h2>
            <table>
                <thead><tr><th>Agent</th><th>Status</th><th>Last Run</th></tr></thead>
                <tbody>{agent_rows}</tbody>
            </table>
        </div>

        <footer>
            Social Media Empire Analytics | Auto-generated by daily-analytics workflow
        </footer>
    </div>
</body>
</html>"""

    return html


def main():
    """Generate dashboard HTML from Supabase data."""
    print("=== Dashboard Generator ===")
    print(f"  Started: {datetime.now(timezone.utc).isoformat()}")

    db = get_supabase_client()

    print("  Fetching data...")
    total_pins = get_total_pins_by_brand(db)
    total_articles = get_total_articles_by_brand(db)
    pins_7d = get_pins_last_7_days(db)
    errors = get_recent_errors(db)
    agents = get_agent_status(db)
    recent_pins = get_recent_pins(db)

    for brand in BRANDS:
        print(f"  {BRAND_LABELS[brand]}: {total_pins[brand]} pins, {total_articles[brand]} articles")

    print("  Generating HTML...")
    html = generate_html(total_pins, total_articles, pins_7d, errors, agents, recent_pins)

    # Write to outputs/dashboard.html
    project_root = os.environ.get(
        "GITHUB_WORKSPACE",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    output_path = os.path.join(project_root, "outputs", "dashboard.html")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Dashboard written to {output_path}")

    # Update agent_runs
    try:
        db.client.table("agent_runs").upsert({
            "agent_name": "dashboard_generator",
            "last_run_at": datetime.now(timezone.utc).isoformat(),
            "status": "success",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="agent_name").execute()
    except Exception:
        pass

    print("=== Dashboard Generation Complete ===")


if __name__ == "__main__":
    main()
