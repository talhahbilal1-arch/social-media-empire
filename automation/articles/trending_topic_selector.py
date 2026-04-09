"""
Trending topic selector for article generation.

Queries the daily_trending Supabase table for today's hot topics per brand,
enriches the top topic with Gemini Google Search grounding for real-time context,
then falls back to the brand's static keyword list if no trending data is available.

Usage (CLI / GitHub Actions):
    python automation/articles/trending_topic_selector.py \\
        --brand fitness \\
        --mark-used \\
        --state-file fitover35_keyword_state.json

Outputs:
  - keyword, category, slug, filename written to $GITHUB_OUTPUT
  - trending_context.json written to CWD (read by article generators)
"""

import os
import json
import random
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path where trending context is written for the article generator to pick up
TRENDING_CONTEXT_FILE = "trending_context.json"


# ─────────────────────────────────────────────────────────────────────────────
# Supabase helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_supabase_client():
    """Return a Supabase client using env vars, or None on failure."""
    try:
        from supabase import create_client
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_KEY')
        if not url or not key:
            logger.info("SUPABASE_URL/KEY not set — skipping trending lookup")
            return None
        return create_client(url, key)
    except Exception as e:
        logger.warning(f"Could not create Supabase client: {e}")
        return None


def fetch_today_trending_topics(brand_key: str) -> Optional[list]:
    """Query daily_trending for today's synthesized topics for this brand.

    Returns a list of topic dicts (rank, topic, why_trending, trend_score, …)
    or None if the table has no row for today.
    """
    client = _get_supabase_client()
    if not client:
        return None

    today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    try:
        result = (
            client.table('daily_trending')
            .select('topics')
            .eq('brand', brand_key)
            .eq('trend_date', today_str)
            .limit(1)
            .execute()
        )
        if not result.data:
            logger.info(f"No trending row for {brand_key} on {today_str}")
            return None
        raw = result.data[0]['topics']
        topics = json.loads(raw) if isinstance(raw, str) else raw
        logger.info(f"Loaded {len(topics)} trending topics for {brand_key} ({today_str})")
        return topics
    except Exception as e:
        logger.warning(f"Failed to fetch trending topics for {brand_key}: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Gemini web grounding
# ─────────────────────────────────────────────────────────────────────────────

def enrich_with_web_search(topic: str, brand_key: str) -> dict:
    """Use Gemini with Google Search grounding to get the latest info on a topic.

    Returns dict with:
        trending_context       — why the topic is hot right now
        search_results_summary — current stats, studies, product news
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return {'trending_context': '', 'search_results_summary': ''}

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        prompt = (
            f'Search for the latest information about: "{topic}"\n\n'
            f"Context: Content for a {brand_key} lifestyle website. "
            "We need CURRENT, UP-TO-DATE information to write a high-quality article.\n\n"
            "Provide:\n"
            "1. Why this topic is trending RIGHT NOW (recent news, studies, cultural moments)\n"
            "2. The most current statistics or data points (cite year/source)\n"
            "3. Recent expert opinions or new research (2025–2026 preferred)\n"
            "4. Any recent product launches, clinical findings, or news relevant to this topic\n\n"
            "Be specific with dates and sources. Focus on information from 2025–2026."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                max_output_tokens=1500,
                temperature=0.3,
            ),
        )

        summary = response.text.strip()
        logger.info(f"Web search enrichment complete for: {topic}")
        return {
            'trending_context': f"Live web research on '{topic}' (sourced {datetime.now(timezone.utc).strftime('%Y-%m-%d')})",
            'search_results_summary': summary,
        }
    except Exception as e:
        logger.warning(f"Web search enrichment failed for '{topic}': {e}")
        return {'trending_context': '', 'search_results_summary': ''}


# ─────────────────────────────────────────────────────────────────────────────
# Static fallbacks (brand-specific keyword lists)
# ─────────────────────────────────────────────────────────────────────────────

def _generate_slug(keyword: str) -> str:
    slug = keyword.lower().replace(' ', '-').replace('?', '').replace("'", '')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug[:60].rstrip('-')


def _static_keyword_fallback(brand_key: str, state_file: Optional[str] = None) -> dict:
    """Pick a keyword from the brand's static list, respecting used-keyword state."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

    if brand_key == 'fitness':
        from automation.articles.fitover35_keywords import (
            SEED_KEYWORDS, load_used_keywords, save_used_keyword, generate_slug,
        )
        sf = state_file or 'fitover35_keyword_state.json'
    elif brand_key == 'deals':
        from automation.articles.dailydealdarling_keywords import (
            SEED_KEYWORDS, load_used_keywords, save_used_keyword, generate_slug,
        )
        sf = state_file or 'dailydealdarling_keyword_state.json'
    else:
        # menopause — use generic keyword_selector
        from automation.articles.keyword_selector import (
            SEED_KEYWORDS, load_used_keywords, save_used_keyword,
        )
        sf = state_file or 'keyword_state.json'
        generate_slug = _generate_slug

    used = load_used_keywords(sf)
    available = [kw for kw in SEED_KEYWORDS if kw[0] not in used]
    if not available:
        logger.warning("All keywords used — resetting state")
        Path(sf).unlink(missing_ok=True)
        available = list(SEED_KEYWORDS)

    selected = random.choice(available)
    keyword, category, _ = selected

    return {
        'keyword': keyword,
        'category': category,
        'slug': generate_slug(keyword),
        'trending_context': '',
        'search_results_summary': '',
        'from_trending': False,
        '_state_file': sf,
        '_save_fn': save_used_keyword,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main selector
# ─────────────────────────────────────────────────────────────────────────────

def select_topic_for_brand(
    brand_key: str,
    use_web_search: bool = True,
    state_file: Optional[str] = None,
) -> dict:
    """Select the best article topic for a brand.

    Priority:
      1. Today's trending data from Supabase  (+ Gemini web grounding)
      2. Static brand keyword list            (no live enrichment)

    Returns:
        {keyword, category, slug, trending_context,
         search_results_summary, from_trending}
    """
    trending = fetch_today_trending_topics(brand_key)

    if trending:
        # Prefer #1, but add variety by occasionally picking from top 3
        top = sorted(trending, key=lambda x: x.get('rank', 99))[:3]
        selected = top[0] if random.random() < 0.6 else random.choice(top)

        topic_text = selected.get('topic', '')
        why_trending = selected.get('why_trending', '')

        slug = _generate_slug(topic_text)

        # Web grounding enrichment
        web = {'trending_context': why_trending, 'search_results_summary': ''}
        if use_web_search and topic_text:
            web = enrich_with_web_search(topic_text, brand_key)
            if not web.get('trending_context') and why_trending:
                web['trending_context'] = why_trending

        logger.info(f"Trending topic selected for {brand_key}: {topic_text}")
        return {
            'keyword': topic_text,
            'category': selected.get('board', 'general').lower().replace(' ', '_'),
            'slug': slug,
            'trending_context': web['trending_context'],
            'search_results_summary': web['search_results_summary'],
            'from_trending': True,
            'trend_score': selected.get('trend_score', 0),
            'content_angle': selected.get('content_angle', ''),
            '_state_file': None,
            '_save_fn': None,
        }

    # Fallback
    logger.info(f"Falling back to static keywords for {brand_key}")
    return _static_keyword_fallback(brand_key, state_file)


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Select a trending (or static fallback) article topic for a brand'
    )
    parser.add_argument(
        '--brand',
        required=True,
        choices=['fitness', 'deals', 'menopause'],
        help='Brand key'
    )
    parser.add_argument(
        '--mark-used',
        action='store_true',
        help='Mark selected keyword as used in the state file'
    )
    parser.add_argument(
        '--state-file',
        default=None,
        help='Path to keyword state file (for static fallback deduplication)'
    )
    parser.add_argument(
        '--no-web-search',
        action='store_true',
        help='Skip Gemini web grounding enrichment'
    )

    args = parser.parse_args()

    result = select_topic_for_brand(
        brand_key=args.brand,
        use_web_search=not args.no_web_search,
        state_file=args.state_file,
    )

    keyword = result['keyword']
    slug = result['slug']
    category = result['category']
    filename = f"{slug}.html"

    # Mark as used in static keyword state (only for fallback path)
    if args.mark_used and result.get('_save_fn') and result.get('_state_file'):
        result['_save_fn'](keyword, result['_state_file'])
        logger.info(f"Marked '{keyword}' as used in {result['_state_file']}")

    # Write trending context sidecar file for the article generator
    context_payload = {
        'keyword': keyword,
        'trending_context': result.get('trending_context', ''),
        'search_results_summary': result.get('search_results_summary', ''),
        'from_trending': result.get('from_trending', False),
        'trend_score': result.get('trend_score', 0),
        'content_angle': result.get('content_angle', ''),
        'generated_at': datetime.now(timezone.utc).isoformat(),
    }
    Path(TRENDING_CONTEXT_FILE).write_text(json.dumps(context_payload, indent=2))
    logger.info(f"Trending context written to {TRENDING_CONTEXT_FILE}")

    # Print human-readable summary
    source = "trending" if result.get('from_trending') else "static fallback"
    print(f"Selected keyword ({source}): {keyword}")
    print(f"Category: {category}")
    print(f"Slug: {slug}")
    print(f"Filename: {filename}")

    # Write to $GITHUB_OUTPUT
    github_output = os.environ.get('GITHUB_OUTPUT', '')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"keyword={keyword}\n")
            f.write(f"category={category}\n")
            f.write(f"slug={slug}\n")
            f.write(f"filename={filename}\n")
    else:
        print(f"\nkeyword={keyword}")
        print(f"category={category}")
        print(f"slug={slug}")
        print(f"filename={filename}")

    return 0


if __name__ == '__main__':
    exit(main())
