"""Daily Trend Scout — discovers what's trending RIGHT NOW for each brand.

Runs every morning at 6 AM PST (1 hour before content-engine).
Fetches real-time signals from 3 sources:
  1. Pinterest RSS feeds from popular niche accounts
  2. pytrends gprop='images' (Google Image Search — best Pinterest proxy)
  3. Google News RSS for breaking niche news

Claude synthesizes all signals into exactly 3 ranked topics per brand,
stored in the `daily_trending` Supabase table for content-engine to consume.
"""

import os
import json
import random
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import anthropic
import feedparser
import requests
from pytrends.request import TrendReq

logger = logging.getLogger(__name__)

_client = None


def _get_anthropic_client():
    """Lazy initialization of Anthropic client."""
    global _client
    if _client is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


# ═══════════════════════════════════════════════════════════════
# NICHE-SPECIFIC FEED AND KEYWORD CONFIGS
# ═══════════════════════════════════════════════════════════════

SCOUT_CONFIGS = {
    "fitness": {
        "rss_feeds": [
            "https://www.pinterest.com/menshealth/fitness/.rss",
            "https://www.pinterest.com/musaboramedia/mens-fitness/.rss",
            "https://www.pinterest.com/healthmagazine/fitness-tips/.rss",
            "https://www.pinterest.com/bodybuilding/workouts/.rss",
        ],
        "pytrends_seeds": ["mens fitness", "workout tips", "creatine"],
        "news_keywords": ["mens fitness", "workout trends", "supplements study"],
        "relevance_filter": (
            "Men's fitness, strength training, nutrition, supplements, fat loss, "
            "muscle building, home workouts, recovery, testosterone, sleep optimization. "
            "EXCLUDE: women's fitness, yoga, dance, pregnancy, children."
        ),
    },
    "deals": {
        "rss_feeds": [
            "https://www.pinterest.com/realsimple/home-organizing-ideas/.rss",
            "https://www.pinterest.com/bhg/best-home-products/.rss",
            "https://www.pinterest.com/goodhousekeeping/home-products/.rss",
            "https://www.pinterest.com/buzzfeed/home-finds/.rss",
        ],
        "pytrends_seeds": ["home organization", "kitchen gadgets", "amazon finds"],
        "news_keywords": ["home products trending", "kitchen gadgets", "home organization"],
        "relevance_filter": (
            "Home, kitchen, organization, self care, beauty, gifting, seasonal decor, "
            "cleaning, budget finds, home improvement. "
            "EXCLUDE: industrial, B2B, automotive, luxury >$500, sports equipment."
        ),
    },
    "menopause": {
        "rss_feeds": [
            "https://www.pinterest.com/healthline/menopause/.rss",
            "https://www.pinterest.com/prevention/menopause/.rss",
            "https://www.pinterest.com/webmd/womens-health/.rss",
            "https://www.pinterest.com/everydayhealth/menopause/.rss",
        ],
        "pytrends_seeds": ["menopause relief", "perimenopause", "hot flash remedies"],
        "news_keywords": ["menopause treatment", "perimenopause research", "HRT news"],
        "relevance_filter": (
            "Menopause, perimenopause, HRT, natural remedies, supplements, nutrition, "
            "sleep issues, mood changes, bone health, weight management. "
            "EXCLUDE: pregnancy, fertility, pediatric, men's health."
        ),
    },
}


# ═══════════════════════════════════════════════════════════════
# DATA SOURCE 1: PINTEREST RSS FEEDS
# ═══════════════════════════════════════════════════════════════

def fetch_pinterest_rss_trends(brand_key):
    """Parse RSS feeds from popular Pinterest accounts in this niche.

    Pinterest RSS is unreliable — many boards have disabled feeds or return 404.
    Each feed is wrapped in try/except so failures don't block other sources.
    """
    config = SCOUT_CONFIGS[brand_key]
    trends = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)

    for feed_url in config["rss_feeds"]:
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo and not feed.entries:
                logger.debug(f"RSS feed unavailable: {feed_url}")
                continue

            for entry in feed.entries[:10]:
                # Parse published date if available
                published = entry.get("published_parsed") or entry.get("updated_parsed")
                if published:
                    entry_dt = datetime(*published[:6], tzinfo=timezone.utc)
                    if entry_dt < cutoff:
                        continue

                title = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()
                link = entry.get("link", "")

                if title:
                    trends.append({
                        "topic": title,
                        "description": summary[:200] if summary else "",
                        "source": "pinterest_rss",
                        "source_url": link,
                    })
        except Exception as e:
            logger.debug(f"RSS feed error ({feed_url}): {e}")
            continue

    logger.info(f"Pinterest RSS for {brand_key}: {len(trends)} entries")
    return trends


# ═══════════════════════════════════════════════════════════════
# DATA SOURCE 2: PYTRENDS IMAGE SEARCH (Pinterest proxy)
# ═══════════════════════════════════════════════════════════════

def fetch_image_search_trends(brand_key):
    """Use pytrends with gprop='images' — Google Image Search rising queries.

    This is the best proxy for Pinterest trends without requiring Pinterest auth,
    since Pinterest content is heavily indexed in Google Images.
    """
    config = SCOUT_CONFIGS[brand_key]
    trends = []
    pytrends = TrendReq(hl='en-US', tz=480)

    # Method 1: Related queries for seed keywords (image search)
    for keyword in config["pytrends_seeds"]:
        try:
            pytrends.build_payload(
                [keyword], timeframe='now 7-d', geo='US', gprop='images'
            )
            related = pytrends.related_queries()
            if keyword in related:
                rising = related[keyword].get('rising')
                if rising is not None and not rising.empty:
                    for _, row in rising.head(5).iterrows():
                        trends.append({
                            "topic": row['query'],
                            "score": min(int(row['value']), 100),
                            "source": "pytrends_images",
                            "seed_keyword": keyword,
                        })

                top = related[keyword].get('top')
                if top is not None and not top.empty:
                    for _, row in top.head(3).iterrows():
                        trends.append({
                            "topic": row['query'],
                            "score": int(row['value']),
                            "source": "pytrends_images_top",
                            "seed_keyword": keyword,
                        })
        except Exception as e:
            logger.warning(f"pytrends images error for '{keyword}': {e}")
            continue

    # Method 2: General trending searches filtered for relevance
    try:
        daily_trending = pytrends.trending_searches(pn='united_states')
        if not daily_trending.empty:
            for topic in daily_trending[0].head(20).tolist():
                trends.append({
                    "topic": topic,
                    "score": 40,
                    "source": "pytrends_daily",
                })
    except Exception as e:
        logger.warning(f"Daily trending searches error: {e}")

    logger.info(f"pytrends for {brand_key}: {len(trends)} entries")
    return trends


# ═══════════════════════════════════════════════════════════════
# DATA SOURCE 3: GOOGLE NEWS RSS
# ═══════════════════════════════════════════════════════════════

def fetch_google_news_trends(brand_key):
    """Parse Google News RSS for breaking news in each niche.

    Uses news.google.com/rss/search?q={keyword} — no auth required.
    Filters to entries from the last 48 hours.
    """
    config = SCOUT_CONFIGS[brand_key]
    trends = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)

    for keyword in config["news_keywords"]:
        try:
            url = f"https://news.google.com/rss/search?q={requests.utils.quote(keyword)}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(url)

            for entry in feed.entries[:5]:
                published = entry.get("published_parsed")
                if published:
                    entry_dt = datetime(*published[:6], tzinfo=timezone.utc)
                    if entry_dt < cutoff:
                        continue

                title = entry.get("title", "").strip()
                link = entry.get("link", "")

                if title:
                    trends.append({
                        "topic": title,
                        "source": "google_news",
                        "source_url": link,
                        "keyword": keyword,
                    })
        except Exception as e:
            logger.warning(f"Google News RSS error for '{keyword}': {e}")
            continue

    logger.info(f"Google News for {brand_key}: {len(trends)} entries")
    return trends


# ═══════════════════════════════════════════════════════════════
# CLAUDE SYNTHESIS — pick exactly 3 trending topics
# ═══════════════════════════════════════════════════════════════

def synthesize_daily_trends(brand_key, raw_trends, yesterday_topics):
    """Use Claude to filter, rank, and select exactly 3 topics from raw signals.

    Args:
        brand_key: Brand identifier
        raw_trends: Combined list of raw trend entries from all 3 sources
        yesterday_topics: List of topic strings used yesterday (to avoid repeats)

    Returns:
        List of 3 topic dicts matching the daily_trending.topics schema
    """
    from .content_brain import BRAND_CONFIGS

    brand_config = BRAND_CONFIGS[brand_key]
    scout_config = SCOUT_CONFIGS[brand_key]

    # Collect board names and affiliate products for the prompt
    boards = brand_config.get("pinterest_boards", [])
    affiliate_products = brand_config.get("affiliate_products", {})
    all_products = []
    for cat_products in affiliate_products.values():
        all_products.extend(cat_products)

    response = _get_anthropic_client().messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""You are a Pinterest content strategist selecting today's trending topics.

BRAND: {brand_key} — {brand_config['name']}
DATE: {datetime.now(timezone.utc).strftime('%A, %B %d, %Y')}

RELEVANCE FILTER: {scout_config['relevance_filter']}

PINTEREST BOARDS: {json.dumps(boards)}
AFFILIATE PRODUCTS: {json.dumps(all_products[:15])}

YESTERDAY'S TOPICS (do NOT repeat these):
{json.dumps(yesterday_topics) if yesterday_topics else '[]'}

RAW TREND SIGNALS FROM 3 SOURCES:
{json.dumps(raw_trends[:60], indent=1)}

YOUR TASK:
1. FILTER — Keep only topics relevant to this brand (use the relevance filter)
2. DEDUPLICATE — Merge overlapping/similar topics
3. RANK — Score by: trendiness (hot RIGHT NOW), Pinterest visual fit, click potential
4. SELECT — Pick exactly 3 topics, ranked #1 (hottest) to #3

For each topic, provide:
- A refined, Pinterest-friendly topic title (specific, not generic)
- Trend score (0-100)
- Why it's trending right now
- A content angle for creating pins about it
- 2-3 pin title ideas
- Which board to post to
- Relevant affiliate products from the list above

Return ONLY this JSON array (no markdown, no backticks):
[
    {{
        "rank": 1,
        "topic": "specific trending topic title",
        "trend_score": 92,
        "why_trending": "explanation of why this is hot right now",
        "content_angle": "how to create engaging pin content about this",
        "pin_ideas": ["Pin Title Idea 1", "Pin Title Idea 2"],
        "board": "Board Name From List Above",
        "affiliate_products": ["product1", "product2"],
        "sources": ["source1", "source2"]
    }},
    {{
        "rank": 2,
        ...
    }},
    {{
        "rank": 3,
        ...
    }}
]"""
        }]
    )

    content = response.content[0].text.strip()
    try:
        topics = json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON array from response
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            topics = json.loads(match.group())
        else:
            raise ValueError(f"Claude did not return valid JSON: {content[:300]}")

    # Ensure exactly 3 topics
    if len(topics) > 3:
        topics = topics[:3]

    return topics


# ═══════════════════════════════════════════════════════════════
# FALLBACK — static topics if all sources fail
# ═══════════════════════════════════════════════════════════════

def _get_fallback_topics(brand_key):
    """Pick 3 random topics from BRAND_CONFIGS if all trend sources fail."""
    from .content_brain import BRAND_CONFIGS

    config = BRAND_CONFIGS[brand_key]
    all_topics = []
    for category, topics in config['topics_by_category'].items():
        for topic in topics:
            all_topics.append({"topic": topic, "category": category})

    selected = random.sample(all_topics, min(3, len(all_topics)))
    boards = config.get("pinterest_boards", ["General"])

    return [
        {
            "rank": i + 1,
            "topic": t["topic"],
            "trend_score": 30,
            "why_trending": "Fallback — no live trend data available",
            "content_angle": "Evergreen content with proven engagement",
            "pin_ideas": [],
            "board": boards[i % len(boards)],
            "affiliate_products": [],
            "sources": ["fallback_static"],
        }
        for i, t in enumerate(selected)
    ]


# ═══════════════════════════════════════════════════════════════
# MASTER ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════

def run_daily_trend_scout(supabase_client):
    """Discover today's trending topics for all 3 brands and store in Supabase.

    Returns dict of {brand: {"topics": [...], "raw_count": int}}.
    """
    today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    results = {}

    for brand_key in ['fitness', 'deals', 'menopause']:
        print(f"\n{'='*60}")
        print(f"TREND SCOUT: {brand_key.upper()} — {today_str}")
        print(f"{'='*60}")

        # Fetch yesterday's topics to avoid repeats
        yesterday_topics = []
        try:
            yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
            yesterday_result = supabase_client.table('daily_trending') \
                .select('topics') \
                .eq('brand', brand_key) \
                .eq('trend_date', yesterday) \
                .limit(1) \
                .execute()
            if yesterday_result.data:
                raw = yesterday_result.data[0]['topics']
                yesterday_data = json.loads(raw) if isinstance(raw, str) else raw
                yesterday_topics = [t.get('topic', '') for t in yesterday_data]
                print(f"  Yesterday's topics: {yesterday_topics}")
        except Exception as e:
            logger.warning(f"Could not fetch yesterday's topics: {e}")

        # Fetch from all 3 sources
        raw_trends = []

        print("  Fetching Pinterest RSS...")
        try:
            rss = fetch_pinterest_rss_trends(brand_key)
            raw_trends.extend(rss)
            print(f"    {len(rss)} entries")
        except Exception as e:
            print(f"    RSS failed: {e}")

        print("  Fetching pytrends images...")
        try:
            images = fetch_image_search_trends(brand_key)
            raw_trends.extend(images)
            print(f"    {len(images)} entries")
        except Exception as e:
            print(f"    pytrends failed: {e}")

        print("  Fetching Google News...")
        try:
            news = fetch_google_news_trends(brand_key)
            raw_trends.extend(news)
            print(f"    {len(news)} entries")
        except Exception as e:
            print(f"    Google News failed: {e}")

        print(f"  Total raw signals: {len(raw_trends)}")

        # Synthesize with Claude or fall back
        if raw_trends:
            print("  Synthesizing with Claude...")
            try:
                topics = synthesize_daily_trends(brand_key, raw_trends, yesterday_topics)
            except Exception as e:
                logger.error(f"Claude synthesis failed for {brand_key}: {e}")
                print(f"  Claude synthesis failed: {e} — using fallback")
                topics = _get_fallback_topics(brand_key)
        else:
            print("  All sources returned nothing — using fallback topics")
            topics = _get_fallback_topics(brand_key)

        # Print selected topics
        for t in topics:
            print(f"  #{t['rank']}: {t['topic']} (score: {t.get('trend_score', '?')})")

        # Upsert into Supabase (ON CONFLICT brand + trend_date)
        try:
            supabase_client.table('daily_trending').upsert(
                {
                    'brand': brand_key,
                    'trend_date': today_str,
                    'topics': json.dumps(topics),
                    'raw_data': json.dumps(raw_trends[:50]),
                    'sources_summary': json.dumps({
                        'pinterest_rss': len([t for t in raw_trends if t.get('source') == 'pinterest_rss']),
                        'pytrends': len([t for t in raw_trends if 'pytrends' in t.get('source', '')]),
                        'google_news': len([t for t in raw_trends if t.get('source') == 'google_news']),
                        'total': len(raw_trends),
                    }),
                },
                on_conflict='brand,trend_date'
            ).execute()
            print(f"  Saved to daily_trending table")
        except Exception as e:
            logger.error(f"Failed to save daily trends for {brand_key}: {e}")
            print(f"  ERROR saving to Supabase: {e}")

        results[brand_key] = {
            "topics": topics,
            "raw_count": len(raw_trends),
        }

    # Update agent_runs
    try:
        supabase_client.table('agent_runs').upsert({
            'agent_name': 'trend_discovery',
            'last_run_at': datetime.now(timezone.utc).isoformat(),
            'status': 'success',
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }, on_conflict='agent_name').execute()
    except Exception:
        pass

    return results
