"""Article -> social-media queue item.

Reads a published article (HTML on disk OR the latest N rows from the Supabase
``content_history`` table) and asks Gemini to produce:

* a 5-8 tweet thread summarising the article
* a 300-600 word LinkedIn post (professional tone)
* a single hook tweet that links back to the article

The result is written as a :class:`~automation.social_posting.models.QueueItem`
JSON file under ``automation/social_posting/queue/<brand>/<date>-<slug>.json``.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from typing import Optional

from . import config
from .models import LinkedInPayload, QueueItem, TweetItem, TwitterPayload

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Article loading
# ---------------------------------------------------------------------------
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)


def _strip_html(html: str) -> str:
    no_tags = _TAG_RE.sub(" ", html)
    return _WS_RE.sub(" ", unescape(no_tags)).strip()


def _extract_title(html: str, fallback: str) -> str:
    for pattern in (_H1_RE, _TITLE_RE):
        match = pattern.search(html)
        if match:
            title = _strip_html(match.group(1))
            if title:
                return title
    return fallback


def load_article_from_file(path: Path) -> dict:
    """Read an HTML article from disk into ``{slug,title,body,url}``."""
    if not path.is_file():
        raise FileNotFoundError(path)
    raw = path.read_text(encoding="utf-8")
    title = _extract_title(raw, fallback=path.stem.replace("-", " ").title())
    body = _strip_html(raw)
    return {
        "slug": path.stem,
        "title": title,
        "body": body[:8000],  # cap so prompt stays small
        "url": "",  # caller fills in based on brand
    }


def load_latest_from_supabase(brand: str, limit: int = 1) -> list[dict]:
    """Pull the latest ``limit`` articles for a brand from ``content_history``."""
    from database.supabase_client import SupabaseClient  # local import

    sb = SupabaseClient.from_config()
    rows = (
        sb.client.table("content_history")
        .select("*")
        .eq("brand", brand)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
        .data
        or []
    )
    out: list[dict] = []
    for row in rows:
        out.append(
            {
                "slug": row.get("slug") or row.get("article_slug") or "untitled",
                "title": row.get("title") or row.get("trending_topic") or "Untitled",
                "body": row.get("body") or row.get("content") or row.get("summary") or "",
                "url": row.get("url") or row.get("article_url") or "",
            }
        )
    return out


# ---------------------------------------------------------------------------
# Gemini generation
# ---------------------------------------------------------------------------
_PROMPT = """You are a social-media editor for the {brand_name} brand
({brand_url}). Repurpose the article below into platform-native content.

Article title: {title}
Article URL: {url}
Article body (truncated):
\"\"\"
{body}
\"\"\"

Return STRICT JSON matching this schema (no commentary):

{{
  "hook_tweet": "single tweet (<=270 chars, must end with the article URL)",
  "thread": [
    "tweet 1 (<=270 chars, hook)",
    "tweet 2 (<=270 chars)",
    "tweet 3 (<=270 chars)",
    "tweet 4 (<=270 chars)",
    "tweet 5 (<=270 chars)",
    "tweet 6 (<=270 chars, CTA back to article)"
  ],
  "linkedin": "300-600 word LinkedIn post in professional tone with line breaks; end with article URL on its own line"
}}

Rules:
- Thread MUST contain 5-8 tweets.
- Every tweet MUST be <=270 characters.
- LinkedIn post MUST be 1500-3500 characters.
- Do not use markdown headings or hashtags inside tweets except brand hashtags.
- Suggested hashtags: {hashtags}
"""


def _generate_with_gemini(article: dict, brand_cfg) -> dict:
    """Call the project's shared Gemini wrapper. Raises RuntimeError on failure."""
    from video_automation.gemini_client import generate_json  # local import

    prompt = _PROMPT.format(
        brand_name=brand_cfg.name,
        brand_url=brand_cfg.site_url,
        title=article["title"],
        url=article["url"],
        body=article["body"],
        hashtags=" ".join(brand_cfg.hashtags),
    )
    raw = generate_json(prompt, max_tokens=2200)
    return json.loads(raw)


def _truncate_tweet(text: str, limit: int = 280) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "\u2026"


# ---------------------------------------------------------------------------
# Queue writing
# ---------------------------------------------------------------------------
def build_queue_item(brand: str, article: dict, generated: dict) -> QueueItem:
    brand_cfg = config.get_brand(brand)
    article_url = article.get("url") or f"{brand_cfg.site_url}/articles/{article['slug']}.html"

    hook_text = _truncate_tweet(generated["hook_tweet"])
    thread_items = [TweetItem(text=_truncate_tweet(t)) for t in generated["thread"]]

    twitter = TwitterPayload(
        hook_tweet=TweetItem(text=hook_text),
        thread=thread_items,
    )
    linkedin = LinkedInPayload(text=generated["linkedin"].strip())

    return QueueItem(
        brand=brand,
        article_slug=article["slug"],
        article_url=article_url,
        article_title=article["title"],
        created_at=datetime.now(timezone.utc),
        platforms=["twitter", "linkedin"],
        twitter=twitter,
        linkedin=linkedin,
    )


def write_queue_item(item: QueueItem) -> Path:
    brand_dir = config.QUEUE_DIR / item.brand
    brand_dir.mkdir(parents=True, exist_ok=True)
    date = item.created_at.strftime("%Y-%m-%d")
    out_path = brand_dir / f"{date}-{item.article_slug}.json"
    out_path.write_text(item.model_dump_json(indent=2), encoding="utf-8")
    logger.info("Queued %s", out_path)
    return out_path


# ---------------------------------------------------------------------------
# Public entrypoints
# ---------------------------------------------------------------------------
def repurpose_file(brand: str, article_path: Path) -> Path:
    article = load_article_from_file(article_path)
    brand_cfg = config.get_brand(brand)
    article["url"] = f"{brand_cfg.site_url}/articles/{article['slug']}.html"
    generated = _generate_with_gemini(article, brand_cfg)
    item = build_queue_item(brand, article, generated)
    return write_queue_item(item)


def repurpose_latest(brand: str, n: int = 1) -> list[Path]:
    brand_cfg = config.get_brand(brand)
    articles = load_latest_from_supabase(brand, limit=n)
    paths: list[Path] = []
    for article in articles:
        if not article.get("url"):
            article["url"] = f"{brand_cfg.site_url}/articles/{article['slug']}.html"
        generated = _generate_with_gemini(article, brand_cfg)
        item = build_queue_item(brand, article, generated)
        paths.append(write_queue_item(item))
    return paths


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Repurpose an article into queued social posts.")
    p.add_argument("--brand", required=True, choices=sorted(config.BRANDS))
    p.add_argument("--file", type=Path, help="Path to an article HTML file.")
    p.add_argument("--latest", type=int, help="Pull latest N articles from Supabase.")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = _build_argparser().parse_args(argv)

    if not args.file and not args.latest:
        print("Pass --file PATH or --latest N", file=sys.stderr)
        return 2

    if not config.have_gemini():
        print("GEMINI_API_KEY not set; cannot generate content.", file=sys.stderr)
        return 3

    if args.file:
        path = repurpose_file(args.brand, args.file)
        print(path)
        return 0

    paths = repurpose_latest(args.brand, n=args.latest or 1)
    for p in paths:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
