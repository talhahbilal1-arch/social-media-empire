"""Auto-generate Kit (ConvertKit) broadcast drafts from new articles.

When a new article is published, this script:
1. Reads the article HTML/markdown
2. Uses Gemini to generate a subject line (A/B variants) + 200-word email summary
3. Posts to Kit API as a DRAFT broadcast (not sent -- user reviews and sends)
4. Logs the broadcast_id to Supabase content_history

Usage::

    # Dry-run: generate email copy without hitting Kit API
    python -m email_marketing.article_broadcast --brand fitness --dry-run

    # From a specific article file
    python -m email_marketing.article_broadcast --file outputs/fitover35-website/articles/some-article.html

    # Latest N articles from Supabase
    python -m email_marketing.article_broadcast --brand fitness --latest 3

    # Actually create Kit draft
    python -m email_marketing.article_broadcast --brand fitness --latest 1
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Brand -> Kit form ID mapping (from CLAUDE.md)
BRAND_FORM_IDS = {
    "fitness": 8946984,
    "deals": 9144859,
    "menopause": 9144926,
}

# Brand -> site URL
BRAND_URLS = {
    "fitness": "https://fitover35.com",
    "deals": "https://dailydealdarling.com",
    "menopause": "https://menopause-planner-website.vercel.app",
}


def _strip_html(html: str) -> str:
    """Rough HTML tag stripper for extracting article text."""
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:8000]  # Cap for Gemini context


def _extract_title(html: str) -> str:
    """Pull <title> or <h1> from HTML."""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL | re.IGNORECASE)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    m = re.search(r"<title>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return "New Article"


def _generate_email_copy(
    article_text: str,
    article_title: str,
    article_url: str,
    brand: str,
) -> dict:
    """Use Gemini to generate subject lines + email body."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set -- using fallback template")
        return {
            "subject_a": f"New: {article_title}",
            "subject_b": f"{article_title} (just published)",
            "body": (
                f"A new article just went live on the site:\n\n"
                f"**{article_title}**\n\n"
                f"Read it here: {article_url}\n\n"
                f"-- The {brand.title()} Team"
            ),
        }

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""You are an email copywriter for the {brand} brand.
A new article was just published: "{article_title}"

Article text (truncated):
{article_text[:4000]}

Article URL: {article_url}

Generate:
1. Subject line A (under 60 chars, curiosity-driven, no clickbait)
2. Subject line B (under 60 chars, benefit-driven)
3. Email body (200 words max, plain text, friendly-expert tone):
   - Hook: one compelling question or insight from the article
   - Summary: 2-3 key takeaways
   - CTA: "Read the full article" with the URL
   - Sign-off: "-- The {brand.title()} Team"

Return as JSON: {{"subject_a": "...", "subject_b": "...", "body": "..."}}
Only return the JSON, no markdown fences."""

        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
        return json.loads(text)
    except Exception as e:
        logger.error("Gemini generation failed: %s -- using fallback", e)
        return {
            "subject_a": f"New: {article_title}",
            "subject_b": f"{article_title} (just published)",
            "body": (
                f"A new article just went live:\n\n"
                f"**{article_title}**\n\n"
                f"Read it here: {article_url}\n\n"
                f"-- The {brand.title()} Team"
            ),
        }


def _create_kit_draft(
    subject: str,
    body: str,
    api_secret: str,
) -> Optional[dict]:
    """Create a broadcast draft via Kit (ConvertKit) API v3."""
    import requests

    url = "https://api.convertkit.com/v3/broadcasts"
    payload = {
        "api_secret": api_secret,
        "subject": subject,
        "content": body,
        "description": f"Auto-generated {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "public": False,
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        broadcast = data.get("broadcast", data)
        logger.info("Kit broadcast draft created: ID=%s", broadcast.get("id"))
        return broadcast
    except Exception as e:
        logger.error("Kit API error: %s", e)
        return None


def _log_to_supabase(
    brand: str,
    article_title: str,
    broadcast_id: Optional[int],
    status: str,
) -> None:
    """Log the broadcast to Supabase content_history if available."""
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        return

    try:
        import requests

        row = {
            "brand": brand,
            "title": f"[broadcast] {article_title}",
            "status": status,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if broadcast_id:
            row["trending_topic"] = f"kit_broadcast_{broadcast_id}"

        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
        resp = requests.post(
            f"{supabase_url}/rest/v1/content_history",
            headers=headers,
            json=row,
            timeout=15,
        )
        if resp.status_code < 300:
            logger.info("Logged broadcast to Supabase")
        else:
            logger.warning("Supabase log failed: %s", resp.text[:200])
    except Exception as e:
        logger.warning("Supabase logging skipped: %s", e)


def process_article_file(
    file_path: Path,
    brand: str,
    dry_run: bool = True,
) -> None:
    """Process a single article file into a Kit broadcast draft."""
    content = file_path.read_text(encoding="utf-8", errors="replace")
    title = _extract_title(content)
    text = _strip_html(content)

    slug = file_path.stem
    base_url = BRAND_URLS.get(brand, "https://fitover35.com")
    article_url = f"{base_url}/articles/{slug}.html"

    logger.info("Generating email for: %s", title)

    email = _generate_email_copy(text, title, article_url, brand)

    print(f"\n{'='*60}")
    print(f"Article: {title}")
    print(f"Subject A: {email['subject_a']}")
    print(f"Subject B: {email['subject_b']}")
    print(f"Body:\n{email['body']}")
    print(f"{'='*60}\n")

    if dry_run:
        logger.info("DRY RUN -- not creating Kit draft")
        return

    kit_secret = os.environ.get("KIT_API_SECRET") or os.environ.get("CONVERTKIT_API_SECRET")
    if not kit_secret:
        logger.error("KIT_API_SECRET not set -- cannot create draft")
        return

    broadcast = _create_kit_draft(email["subject_a"], email["body"], kit_secret)
    broadcast_id = broadcast.get("id") if broadcast else None

    _log_to_supabase(
        brand=brand,
        article_title=title,
        broadcast_id=broadcast_id,
        status="broadcast_draft" if broadcast_id else "broadcast_failed",
    )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Generate Kit broadcast drafts from articles"
    )
    parser.add_argument("--brand", choices=["fitness", "deals", "menopause"], default="fitness")
    parser.add_argument("--file", type=Path, help="Path to a specific article file")
    parser.add_argument("--latest", type=int, default=1, help="Process N most recent articles")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Print only, no Kit API (default)")
    parser.add_argument("--send", action="store_true", help="Actually create Kit draft (overrides --dry-run)")
    args = parser.parse_args()

    dry_run = not args.send

    if args.file:
        if not args.file.exists():
            logger.error("File not found: %s", args.file)
            sys.exit(1)
        process_article_file(args.file, args.brand, dry_run=dry_run)
    else:
        # Find latest articles for brand
        brand_dirs = {
            "fitness": Path("outputs/fitover35-website/articles"),
            "deals": Path("outputs/dailydealdarling-website/articles"),
            "menopause": Path("outputs/menopause-planner-website/articles"),
        }
        article_dir = brand_dirs.get(args.brand)
        if not article_dir or not article_dir.exists():
            logger.error("Article directory not found for brand %s", args.brand)
            sys.exit(1)

        articles = sorted(article_dir.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not articles:
            logger.info("No articles found for %s", args.brand)
            sys.exit(0)

        for article_path in articles[: args.latest]:
            process_article_file(article_path, args.brand, dry_run=dry_run)


if __name__ == "__main__":
    main()
