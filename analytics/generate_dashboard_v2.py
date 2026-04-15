"""Dashboard Generator v2 — Real-time monitoring dashboard for fitover35.com.

Renders outputs/fitover35-website/dashboard/index.html from live Supabase data
plus optional Gumroad + GitHub Actions feeds. Uses the server-side template at
analytics/dashboard_template.html (pure string substitution — no Jinja2).

All queries fail gracefully: missing tables, missing env vars, or API errors
leave that section showing "data unavailable" or zeroed stats. Dashboard still
renders with ZERO data across the board.

Environment (all optional except SUPABASE_URL/SUPABASE_KEY):
    SUPABASE_URL, SUPABASE_KEY       — required for operations panels
    GUMROAD_ACCESS_TOKEN             — enables real revenue numbers
    GITHUB_TOKEN                     — enables workflow health pill
    GITHUB_REPOSITORY                — owner/repo for workflow health check
                                       (defaults to talhahbilal1-arch/social-media-empire)

Usage:
    python3 -m analytics.generate_dashboard_v2
"""
from __future__ import annotations

import html
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

# Allow running as a module or directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BRANDS: list[str] = ["fitness", "deals", "menopause"]
BRAND_LABELS: dict[str, str] = {
    "fitness": "FitOver35",
    "deals": "Daily Deal Darling",
    "menopause": "Menopause Planner",
}
BRAND_SITES: dict[str, str] = {
    "fitness": "https://fitover35.com",
    "deals": "https://dailydealdarling.com",
    "menopause": "https://menopause-planner-website.vercel.app",
}

# Estimated Amazon commission rate per click — used only if Amazon data missing.
# Treated as informational; exposed via data.json for transparency.
AMAZON_EST_CLICK_VALUE: float = 0.05

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "dashboard_template.html"
)
DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "outputs",
    "fitover35-website",
    "dashboard",
)


# ──────────────────────────────────────────────────────────────────────
# Supabase helpers (all fail-soft)
# ──────────────────────────────────────────────────────────────────────

def get_db() -> Optional[Any]:
    """Return a Supabase client wrapper or None if unavailable."""
    try:
        from database.supabase_client import get_supabase_client
        return get_supabase_client()
    except Exception as exc:  # noqa: BLE001
        print(f"  [warn] Supabase unavailable: {exc}")
        return None


def _iso_cutoff(hours: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


def count_pins_by_brand(db: Any, hours: int) -> dict[str, int]:
    """Count pins per brand in the last N hours. Tries content_history first."""
    cutoff = _iso_cutoff(hours)
    counts: dict[str, int] = {b: 0 for b in BRANDS}
    for brand in BRANDS:
        for table in ("content_history", "pinterest_pins"):
            try:
                res = (
                    db.client.table(table)
                    .select("id", count="exact")
                    .eq("brand", brand)
                    .gte("created_at", cutoff)
                    .execute()
                )
                counts[brand] = int(res.count or 0)
                break  # First table that works wins
            except Exception:
                continue
    return counts


def count_articles_by_brand(db: Any, hours: int) -> dict[str, int]:
    """Count articles per brand in the last N hours."""
    cutoff = _iso_cutoff(hours)
    counts: dict[str, int] = {b: 0 for b in BRANDS}
    for brand in BRANDS:
        try:
            res = (
                db.client.table("generated_articles")
                .select("id", count="exact")
                .eq("brand", brand)
                .gte("created_at", cutoff)
                .execute()
            )
            counts[brand] = int(res.count or 0)
        except Exception:
            # Fallback: content_history with article_published status
            try:
                res = (
                    db.client.table("content_history")
                    .select("id", count="exact")
                    .eq("brand", brand)
                    .eq("status", "article_published")
                    .gte("created_at", cutoff)
                    .execute()
                )
                counts[brand] = int(res.count or 0)
            except Exception:
                counts[brand] = 0
    return counts


def error_breakdown_24h(db: Any) -> dict[str, int]:
    """Return {'total', 'high', 'medium', 'low'} for errors in last 24h."""
    cutoff = _iso_cutoff(24)
    out: dict[str, int] = {"total": 0, "high": 0, "medium": 0, "low": 0}
    try:
        res = (
            db.client.table("errors")
            .select("severity")
            .gte("created_at", cutoff)
            .execute()
        )
        rows = res.data or []
        out["total"] = len(rows)
        for row in rows:
            sev = (row.get("severity") or "medium").lower()
            if sev in out:
                out[sev] += 1
            else:
                out["medium"] += 1
    except Exception as exc:  # noqa: BLE001
        print(f"  [warn] errors table read failed: {exc}")
    return out


def top_articles(db: Any, limit: int = 10) -> tuple[list[dict[str, Any]], str]:
    """
    Return (rows, metric_label). Tries, in order:
      1. pin_clicks table (affiliate click counts)
      2. article_analytics table (pageviews)
      3. pinterest_pins ordered by clicks
    Returns ([], '') if nothing available.
    """
    # Option 1: pin_clicks aggregate
    try:
        res = (
            db.client.table("pin_clicks")
            .select("article_url, brand, clicks")
            .order("clicks", desc=True)
            .limit(limit)
            .execute()
        )
        rows = res.data or []
        if rows:
            return (
                [
                    {
                        "title": r.get("article_url", "")[:80],
                        "brand": r.get("brand", ""),
                        "metric": int(r.get("clicks", 0) or 0),
                        "url": r.get("article_url", "#"),
                    }
                    for r in rows
                ],
                "by affiliate clicks",
            )
    except Exception:
        pass

    # Option 2: article_analytics pageviews
    try:
        res = (
            db.client.table("article_analytics")
            .select("title, brand, pageviews, url")
            .order("pageviews", desc=True)
            .limit(limit)
            .execute()
        )
        rows = res.data or []
        if rows:
            return (
                [
                    {
                        "title": r.get("title") or r.get("url", "")[:80],
                        "brand": r.get("brand", ""),
                        "metric": int(r.get("pageviews", 0) or 0),
                        "url": r.get("url", "#"),
                    }
                    for r in rows
                ],
                "by pageviews",
            )
    except Exception:
        pass

    # Option 3: pinterest_pins clicks
    try:
        res = (
            db.client.table("pinterest_pins")
            .select("title, brand, clicks, destination_url")
            .order("clicks", desc=True)
            .limit(limit)
            .execute()
        )
        rows = [r for r in (res.data or []) if (r.get("clicks") or 0) > 0]
        if rows:
            return (
                [
                    {
                        "title": r.get("title", "") or "(untitled)",
                        "brand": r.get("brand", ""),
                        "metric": int(r.get("clicks", 0) or 0),
                        "url": r.get("destination_url", "#"),
                    }
                    for r in rows
                ],
                "by pin clicks",
            )
    except Exception:
        pass

    return ([], "")


def total_pin_clicks_24h(db: Any) -> int:
    """Sum of pinterest_pins.clicks created in last 24h — used for Amazon est."""
    cutoff = _iso_cutoff(24)
    try:
        res = (
            db.client.table("pinterest_pins")
            .select("clicks")
            .gte("created_at", cutoff)
            .execute()
        )
        return sum(int(r.get("clicks") or 0) for r in (res.data or []))
    except Exception:
        return 0


# ──────────────────────────────────────────────────────────────────────
# Gumroad
# ──────────────────────────────────────────────────────────────────────

def gumroad_revenue() -> dict[str, float]:
    """Return revenue totals from Gumroad /v2/sales. Empty dict if unavailable."""
    token = os.environ.get("GUMROAD_ACCESS_TOKEN", "").strip()
    if not token:
        return {}

    now = datetime.now(timezone.utc)
    day_cutoff = now - timedelta(hours=24)
    week_cutoff = now - timedelta(days=7)
    month_cutoff = now - timedelta(days=30)

    totals = {"today": 0.0, "week": 0.0, "month": 0.0, "alltime": 0.0}
    page = 1
    max_pages = 20  # safety cap — 20 * ~100 sales = 2000 sales

    while page <= max_pages:
        params = urllib.parse.urlencode({"access_token": token, "page": page})
        url = f"https://api.gumroad.com/v2/sales?{params}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rcc-dashboard"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
            print(f"  [warn] Gumroad page {page} failed: {exc}")
            break

        sales = payload.get("sales", [])
        if not sales:
            break

        for s in sales:
            try:
                created = datetime.fromisoformat(
                    s["created_at"].replace("Z", "+00:00")
                )
                # price is in cents
                amount = float(s.get("price", 0)) / 100.0
            except (KeyError, ValueError):
                continue

            totals["alltime"] += amount
            if created >= month_cutoff:
                totals["month"] += amount
            if created >= week_cutoff:
                totals["week"] += amount
            if created >= day_cutoff:
                totals["today"] += amount

        if not payload.get("next_page_url"):
            break
        page += 1

    return totals


# ──────────────────────────────────────────────────────────────────────
# GitHub Actions workflow health
# ──────────────────────────────────────────────────────────────────────

def workflow_health() -> tuple[str, str]:
    """
    Return (status_label, css_class) for content-engine.yml latest run.
      success  → 'green'
      in_progress → 'yellow'
      failure/cancelled → 'red'
      unknown/no token → 'grey'
    """
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get(
        "GITHUB_REPOSITORY", "talhahbilal1-arch/social-media-empire"
    ).strip()
    if not token or not repo:
        return ("unknown", "pill-grey")

    url = (
        f"https://api.github.com/repos/{repo}/actions/workflows/"
        f"content-engine.yml/runs?per_page=1"
    )
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "rcc-dashboard",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"  [warn] GitHub workflow health fetch failed: {exc}")
        return ("unknown", "pill-grey")

    runs = data.get("workflow_runs", [])
    if not runs:
        return ("no runs", "pill-grey")

    run = runs[0]
    status = run.get("status", "")  # queued | in_progress | completed
    conclusion = run.get("conclusion", "")  # success | failure | cancelled | ...

    if status != "completed":
        return (status or "running", "pill-yellow")
    if conclusion == "success":
        return ("healthy", "pill-green")
    if conclusion in ("failure", "timed_out"):
        return ("failing", "pill-red")
    if conclusion == "cancelled":
        return ("cancelled", "pill-yellow")
    return (conclusion or "unknown", "pill-grey")


# ──────────────────────────────────────────────────────────────────────
# Rendering
# ──────────────────────────────────────────────────────────────────────

def _esc(s: Any) -> str:
    return html.escape(str(s or ""), quote=True)


def _bar_html(counts: dict[str, int]) -> str:
    """Render stacked bar rows for brand counts. Shows "no data yet" if empty."""
    max_val = max(counts.values(), default=0)
    if max_val == 0:
        return '<div class="no-data">no data yet</div>'

    rows: list[str] = []
    for brand in BRANDS:
        count = counts.get(brand, 0)
        pct = (count / max_val * 100) if max_val else 0
        rows.append(
            f'<div class="bar-row">'
            f'<div class="bar-label">'
            f'<span class="name">{_esc(BRAND_LABELS[brand])}</span>'
            f'<span class="count">{count}</span>'
            f'</div>'
            f'<div class="bar-track">'
            f'<div class="bar-fill bar-{brand}" style="width: {pct:.1f}%"></div>'
            f'</div>'
            f'</div>'
        )
    return "".join(rows)


def _top_articles_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<div class="no-data">no data yet</div>'

    parts: list[str] = [
        '<table><thead><tr>'
        '<th>#</th><th>Brand</th><th>Title</th><th class="num">Metric</th>'
        '</tr></thead><tbody>'
    ]
    for idx, r in enumerate(rows, start=1):
        brand = r.get("brand", "")
        tag_class = f"tag-{brand}" if brand in BRANDS else ""
        brand_label = BRAND_LABELS.get(brand, brand or "—")
        title = r["title"][:80]
        url = r.get("url") or "#"
        parts.append(
            f'<tr>'
            f'<td class="num">{idx}</td>'
            f'<td><span class="brand-tag {tag_class}">{_esc(brand_label)}</span></td>'
            f'<td><a href="{_esc(url)}" target="_blank" rel="noopener">{_esc(title)}</a></td>'
            f'<td class="num">{r["metric"]:,}</td>'
            f'</tr>'
        )
    parts.append("</tbody></table>")
    return "".join(parts)


def _error_class(total: int) -> str:
    if total == 0:
        return "zero"
    if total < 5:
        return "some"
    return "high"


def render_html(data: dict[str, Any]) -> str:
    """Substitute all __TOKENS__ in the template with rendered values."""
    with open(TEMPLATE_PATH, encoding="utf-8") as fh:
        tpl = fh.read()

    rev = data["revenue"]
    pins_today = data["pins_today"]
    articles_week = data["articles_week"]
    errs = data["errors_24h"]
    wf_label, wf_class = data["workflow"]
    top_rows = data["top_articles"]
    top_label = data["top_articles_metric"]

    subs = {
        "__LAST_UPDATED__": _esc(data["generated_at"]),
        "__WORKFLOW_STATUS__": _esc(wf_label),
        "__WORKFLOW_CLASS__": _esc(wf_class),
        "__REV_TODAY__": f"{rev['today']:,.2f}",
        "__REV_WEEK__": f"{rev['week']:,.2f}",
        "__REV_MONTH__": f"{rev['month']:,.2f}",
        "__REV_ALLTIME__": f"{rev['alltime']:,.2f}",
        "__PINS_TODAY_TOTAL__": str(sum(pins_today.values())),
        "__PINS_TODAY_BARS__": _bar_html(pins_today),
        "__ARTICLES_WEEK_TOTAL__": str(sum(articles_week.values())),
        "__ARTICLES_WEEK_BARS__": _bar_html(articles_week),
        "__ERROR_COUNT__": str(errs["total"]),
        "__ERROR_CLASS__": _error_class(errs["total"]),
        "__ERR_HIGH__": str(errs["high"]),
        "__ERR_MEDIUM__": str(errs["medium"]),
        "__ERR_LOW__": str(errs["low"]),
        "__TOP_METRIC_LABEL__": _esc(top_label),
        "__TOP_ARTICLES_TABLE__": _top_articles_table(top_rows),
    }
    for key, val in subs.items():
        tpl = tpl.replace(key, val)
    return tpl


# ──────────────────────────────────────────────────────────────────────
# Orchestration
# ──────────────────────────────────────────────────────────────────────

def collect_data() -> dict[str, Any]:
    """Gather all metrics. Each step is fail-soft."""
    print("=== Dashboard v2 — collecting data ===")

    db = get_db()

    if db is not None:
        print("  > pins last 24h")
        pins_today = count_pins_by_brand(db, 24)
        print("  > articles last 7d")
        articles_week = count_articles_by_brand(db, 24 * 7)
        print("  > errors last 24h")
        errs = error_breakdown_24h(db)
        print("  > top articles")
        top_rows, top_label = top_articles(db, limit=10)
        pin_clicks_24h = total_pin_clicks_24h(db)
    else:
        pins_today = {b: 0 for b in BRANDS}
        articles_week = {b: 0 for b in BRANDS}
        errs = {"total": 0, "high": 0, "medium": 0, "low": 0}
        top_rows, top_label = [], ""
        pin_clicks_24h = 0

    print("  > gumroad revenue")
    gum = gumroad_revenue()
    revenue = {
        "today": gum.get("today", 0.0),
        "week": gum.get("week", 0.0),
        "month": gum.get("month", 0.0),
        "alltime": gum.get("alltime", 0.0),
        "amazon_est_today": pin_clicks_24h * AMAZON_EST_CLICK_VALUE,
        "source": "gumroad" if gum else "unavailable",
    }
    # Add estimated Amazon into today's bucket for display (kept separate in data.json)
    revenue["today"] += revenue["amazon_est_today"]

    print("  > workflow health")
    workflow = workflow_health()

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "pins_today": pins_today,
        "articles_week": articles_week,
        "errors_24h": errs,
        "top_articles": top_rows,
        "top_articles_metric": top_label,
        "revenue": revenue,
        "workflow": workflow,
        "pin_clicks_24h": pin_clicks_24h,
    }


def write_outputs(data: dict[str, Any], output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    html_out = render_html(data)
    html_path = os.path.join(output_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html_out)
    print(f"  wrote {html_path} ({len(html_out):,} chars)")

    json_path = os.path.join(output_dir, "data.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)
    print(f"  wrote {json_path}")


def main() -> None:
    output_dir = os.environ.get("DASHBOARD_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    data = collect_data()
    write_outputs(data, output_dir)

    # Best-effort: record agent run. Safe to fail.
    try:
        db = get_db()
        if db is not None:
            db.client.table("agent_runs").upsert(
                {
                    "agent_name": "dashboard_v2",
                    "last_run_at": datetime.now(timezone.utc).isoformat(),
                    "status": "success",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                on_conflict="agent_name",
            ).execute()
    except Exception:
        pass

    print("=== Dashboard v2 complete ===")


if __name__ == "__main__":
    main()
