"""Article Performance Tracker — Analyzes articles across all brand sites.

Scans generated articles for:
- Affiliate link counts per article
- Thin content (low word count)
- Missing affiliate links
- Suggests new article topics based on top-performing pin topics

Usage:
    python -m analytics.article_tracker
"""

import os
import sys
import re
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import defaultdict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_client import get_supabase_client

BRANDS = ["fitness", "deals", "menopause"]
BRAND_LABELS = {
    "fitness": "FitOver35",
    "deals": "Daily Deal Darling",
    "menopause": "Menopause Planner",
}

# Article directories (relative to project root)
ARTICLE_DIRS = {
    "fitness": "outputs/fitover35-website/articles",
    "deals": "outputs/dailydealdarling-website/articles",
    "menopause": "outputs/menopause-planner-website/articles",
}

# Amazon affiliate tags per brand
AFFILIATE_TAGS = {
    "fitness": "fitover35-20",
    "deals": "dailydealdarling1-20",
    "menopause": None,  # No Amazon tag for menopause brand
}

MIN_WORD_COUNT = 400  # Below this = thin content
MIN_AFFILIATE_LINKS = 1  # Articles should have at least 1 affiliate link


def get_project_root() -> str:
    """Get the project root directory."""
    # In GitHub Actions, use GITHUB_WORKSPACE; locally, use script location
    return os.environ.get(
        "GITHUB_WORKSPACE",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )


def scan_article_files(brand: str) -> list:
    """Scan HTML article files on disk for a brand."""
    root = get_project_root()
    article_dir = os.path.join(root, ARTICLE_DIRS.get(brand, ""))

    if not os.path.isdir(article_dir):
        return []

    articles = []
    for filename in os.listdir(article_dir):
        if not filename.endswith(".html"):
            continue

        filepath = os.path.join(article_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue

        # Strip HTML tags for word count
        text_only = re.sub(r"<[^>]+>", " ", content)
        text_only = re.sub(r"\s+", " ", text_only).strip()
        word_count = len(text_only.split())

        # Count Amazon affiliate links
        amazon_links = re.findall(r'https?://(?:www\.)?amazon\.com/[^"\'>\s]+', content)
        affiliate_links = [
            link for link in amazon_links
            if "tag=" in link
        ]

        # Check for wrong affiliate tag
        expected_tag = AFFILIATE_TAGS.get(brand)
        wrong_tag_links = []
        if expected_tag:
            wrong_tag_links = [
                link for link in affiliate_links
                if f"tag={expected_tag}" not in link
            ]

        # Count all outbound links
        all_links = re.findall(r'href="(https?://[^"]+)"', content)

        articles.append({
            "filename": filename,
            "slug": filename.replace(".html", ""),
            "brand": brand,
            "word_count": word_count,
            "total_links": len(all_links),
            "amazon_links": len(amazon_links),
            "affiliate_links": len(affiliate_links),
            "wrong_tag_links": len(wrong_tag_links),
            "is_thin": word_count < MIN_WORD_COUNT,
            "missing_affiliate": (
                len(affiliate_links) < MIN_AFFILIATE_LINKS
                and expected_tag is not None
            ),
        })

    return articles


def get_db_articles(db) -> list:
    """Fetch all articles from generated_articles table."""
    try:
        result = db.client.table("generated_articles") \
            .select("*") \
            .order("created_at", desc=True) \
            .execute()
        return result.data or []
    except Exception as e:
        print(f"  Error fetching articles from DB: {e}")
        return []


def get_top_pin_topics(db, limit: int = 20) -> list:
    """Get the most common pin topics from content_history (last 30 days)."""
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        result = db.client.table("content_history") \
            .select("topic, brand") \
            .gte("created_at", cutoff + "T00:00:00Z") \
            .execute()

        topic_counts = defaultdict(int)
        for row in (result.data or []):
            topic = row.get("topic", "")
            if topic:
                topic_counts[topic] += 1

        return sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    except Exception as e:
        print(f"  Error fetching top topics: {e}")
        return []


def get_existing_article_topics(db_articles: list) -> set:
    """Extract topics from existing articles."""
    topics = set()
    for article in db_articles:
        topic = article.get("topic", "")
        if topic:
            topics.add(topic.lower().strip())
    return topics


def suggest_new_topics(top_pin_topics: list, existing_topics: set) -> list:
    """Suggest new article topics based on popular pin topics not yet covered."""
    suggestions = []
    for topic, count in top_pin_topics:
        if topic.lower().strip() not in existing_topics:
            suggestions.append({
                "topic": topic,
                "pin_count": count,
                "reason": f"Popular pin topic ({count} pins) with no matching article",
            })
    return suggestions[:10]


def generate_report(all_articles: dict, db_articles: list,
                    suggestions: list) -> str:
    """Generate article performance report."""
    lines = []
    lines.append("=" * 60)
    lines.append("  ARTICLE PERFORMANCE REPORT")
    lines.append(f"  Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("=" * 60)
    lines.append("")

    total_articles = 0
    total_thin = 0
    total_missing_affiliate = 0

    for brand in BRANDS:
        label = BRAND_LABELS.get(brand, brand)
        articles = all_articles.get(brand, [])
        total_articles += len(articles)
        thin = [a for a in articles if a["is_thin"]]
        missing = [a for a in articles if a["missing_affiliate"]]
        total_thin += len(thin)
        total_missing_affiliate += len(missing)

        lines.append(f"--- {label} ({len(articles)} articles on disk) ---")

        # DB count
        db_count = len([a for a in db_articles if a.get("brand") == brand])
        lines.append(f"  In database: {db_count}")
        lines.append(f"  On disk: {len(articles)}")

        if articles:
            avg_words = sum(a["word_count"] for a in articles) // len(articles)
            avg_links = sum(a["affiliate_links"] for a in articles) / len(articles)
            lines.append(f"  Avg word count: {avg_words}")
            lines.append(f"  Avg affiliate links: {avg_links:.1f}")

        if thin:
            lines.append(f"  THIN CONTENT ({len(thin)} articles < {MIN_WORD_COUNT} words):")
            for a in thin[:5]:
                lines.append(f"    - {a['slug']} ({a['word_count']} words)")
            if len(thin) > 5:
                lines.append(f"    ... and {len(thin) - 5} more")

        if missing:
            lines.append(f"  MISSING AFFILIATES ({len(missing)} articles):")
            for a in missing[:5]:
                lines.append(f"    - {a['slug']} ({a['affiliate_links']} links)")
            if len(missing) > 5:
                lines.append(f"    ... and {len(missing) - 5} more")

        # Wrong tags
        wrong = [a for a in articles if a["wrong_tag_links"] > 0]
        if wrong:
            lines.append(f"  WRONG AFFILIATE TAG ({len(wrong)} articles):")
            for a in wrong[:5]:
                lines.append(f"    - {a['slug']} ({a['wrong_tag_links']} wrong tags)")

        lines.append("")

    # Summary
    lines.append(f"--- OVERALL ---")
    lines.append(f"  Total articles: {total_articles}")
    lines.append(f"  Thin content: {total_thin}")
    lines.append(f"  Missing affiliate links: {total_missing_affiliate}")
    lines.append("")

    # Suggestions
    if suggestions:
        lines.append("--- SUGGESTED NEW TOPICS ---")
        for i, s in enumerate(suggestions, 1):
            lines.append(f"  {i}. {s['topic']}")
            lines.append(f"     {s['reason']}")
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
    """Run article performance tracking."""
    print("=== Article Performance Tracker ===")
    print(f"  Started: {datetime.now(timezone.utc).isoformat()}")

    db = get_supabase_client()

    # Scan article files on disk
    print("\n  Scanning article files...")
    all_articles = {}
    for brand in BRANDS:
        articles = scan_article_files(brand)
        all_articles[brand] = articles
        print(f"  {BRAND_LABELS[brand]}: {len(articles)} articles")

    # Fetch DB records
    print("  Fetching articles from database...")
    db_articles = get_db_articles(db)
    print(f"  Found {len(db_articles)} articles in database")

    # Get top pin topics for suggestions
    print("  Fetching top pin topics...")
    top_pin_topics = get_top_pin_topics(db)

    # Generate suggestions
    existing_topics = get_existing_article_topics(db_articles)
    suggestions = suggest_new_topics(top_pin_topics, existing_topics)
    if suggestions:
        print(f"  Found {len(suggestions)} topic suggestions")

    # Generate report
    report = generate_report(all_articles, db_articles, suggestions)
    print(report)

    date_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    save_report(report, f"article-performance-{date_tag}.txt")

    # Update agent_runs
    try:
        db.client.table("agent_runs").upsert({
            "agent_name": "article_tracker",
            "last_run_at": datetime.now(timezone.utc).isoformat(),
            "status": "success",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="agent_name").execute()
    except Exception:
        pass

    print("\n=== Article Tracker Complete ===")


if __name__ == "__main__":
    main()
