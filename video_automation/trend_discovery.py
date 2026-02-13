"""Trend Discovery Engine.

Finds trending topics across Google Trends and Pinterest for each brand niche.
Runs weekly (Sunday nights) to plan the following week's content.
"""

import os
import json
import random
import logging
import requests
from datetime import datetime, timedelta, timezone

import anthropic
from pytrends.request import TrendReq

logger = logging.getLogger(__name__)

_client = None

def _get_anthropic_client():
    """Lazy initialization of Anthropic client to avoid empty API key at import time."""
    global _client
    if _client is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client

# ═══════════════════════════════════════════════════════════════
# NICHE CONFIGURATION FOR TREND DISCOVERY
# ═══════════════════════════════════════════════════════════════

NICHE_CONFIGS = {
    "fitness": {
        "google_trends_keywords": [
            "men fitness over 35",
            "workout for men",
            "muscle building",
            "fat loss men",
            "supplements for men",
            "home workout",
            "protein powder",
            "creatine",
            "testosterone boost",
            "meal prep fitness"
        ],
        "google_trends_category": 45,  # Health & Fitness
        "pinterest_trends_searches": [
            "mens fitness",
            "workout routine",
            "muscle building meals",
            "home gym setup",
            "fat loss tips",
            "protein recipes",
            "supplement reviews"
        ],
        "trending_search_queries": [
            "trending fitness topics this week",
            "popular workout trends 2026",
            "viral fitness tips men",
            "trending supplements right now",
            "popular gym exercises trending"
        ],
        "relevance_filter": """Filter these trends to ONLY keep ones relevant to men's fitness,
        especially men over 30-40. Remove anything about: women's fitness, children,
        yoga/pilates (unless specifically for men), dance fitness, pregnancy fitness.
        Keep: strength training, nutrition, supplements, fat loss, muscle building,
        home workouts, fitness gear, recovery, sleep optimization, testosterone."""
    },
    "deals": {
        "google_trends_keywords": [
            "best home products",
            "kitchen gadgets",
            "home organization",
            "home decor ideas",
            "amazon finds",
            "best deals home",
            "self care products",
            "gift ideas women",
            "budget home makeover",
            "cleaning products best"
        ],
        "google_trends_category": 11,  # Home & Garden
        "pinterest_trends_searches": [
            "home organization ideas",
            "kitchen must haves",
            "home decor trends",
            "self care routine",
            "gift ideas for her",
            "apartment decor",
            "cleaning hacks"
        ],
        "trending_search_queries": [
            "trending home products this week",
            "popular kitchen gadgets 2026",
            "viral home finds tiktok pinterest",
            "trending home decor styles",
            "popular self care products right now"
        ],
        "relevance_filter": """Filter these trends to ONLY keep ones relevant to home, lifestyle,
        and deals for women 25-45. Remove anything about: industrial/commercial products,
        B2B services, luxury items over $500, automotive, sports equipment.
        Keep: kitchen, home decor, organization, self care, beauty, gifting, seasonal home,
        cleaning, budget finds, home improvement DIY."""
    },
    "menopause": {
        "google_trends_keywords": [
            "menopause symptoms",
            "perimenopause",
            "hot flashes relief",
            "menopause weight gain",
            "hormone balance",
            "menopause supplements",
            "menopause sleep",
            "menopause anxiety",
            "HRT menopause",
            "natural menopause remedies"
        ],
        "google_trends_category": 45,  # Health & Fitness
        "pinterest_trends_searches": [
            "menopause relief",
            "perimenopause tips",
            "hormone balance natural",
            "menopause self care",
            "menopause nutrition",
            "hot flash remedies",
            "menopause wellness"
        ],
        "trending_search_queries": [
            "trending menopause topics this week",
            "menopause news latest",
            "popular menopause remedies 2026",
            "menopause awareness trending",
            "new menopause treatments"
        ],
        "relevance_filter": """Filter these trends to ONLY keep ones relevant to menopause,
        perimenopause, and women's midlife health. Remove anything about: pregnancy,
        fertility treatments, pediatric health, men's health.
        Keep: menopause symptoms, perimenopause, HRT, natural remedies, supplements,
        nutrition for menopause, sleep issues, mood changes, bone health, heart health
        in menopause, weight management during menopause."""
    }
}


# ═══════════════════════════════════════════════════════════════
# DATA SOURCE 1: GOOGLE TRENDS
# ═══════════════════════════════════════════════════════════════

def fetch_google_trends(brand_key):
    """Fetch trending and rising search topics from Google Trends."""
    config = NICHE_CONFIGS[brand_key]
    pytrends = TrendReq(hl='en-US', tz=480)  # PST timezone

    all_trends = []

    try:
        # Method 1: Related queries for each seed keyword
        for keyword in config['google_trends_keywords'][:5]:
            try:
                pytrends.build_payload([keyword], timeframe='now 7-d', geo='US')

                related = pytrends.related_queries()
                if keyword in related:
                    rising = related[keyword].get('rising')
                    if rising is not None and not rising.empty:
                        for _, row in rising.head(5).iterrows():
                            all_trends.append({
                                'topic': row['query'],
                                'score': min(int(row['value']), 100),
                                'type': 'rising',
                                'source': 'google_trends',
                                'seed_keyword': keyword
                            })

                    top = related[keyword].get('top')
                    if top is not None and not top.empty:
                        for _, row in top.head(5).iterrows():
                            all_trends.append({
                                'topic': row['query'],
                                'score': int(row['value']),
                                'type': 'top',
                                'source': 'google_trends',
                                'seed_keyword': keyword
                            })
            except Exception as e:
                logger.warning(f"Google Trends error for '{keyword}': {e}")
                continue

        # Method 2: Trending searches (daily trending)
        try:
            trending = pytrends.trending_searches(pn='united_states')
            if not trending.empty:
                for topic in trending[0].head(20).tolist():
                    all_trends.append({
                        'topic': topic,
                        'score': 50,
                        'type': 'daily_trending',
                        'source': 'google_trends',
                        'seed_keyword': 'general'
                    })
        except Exception as e:
            logger.warning(f"Daily trending error: {e}")

        # Method 3: Interest over time to find surging topics
        try:
            keywords_batch = config['google_trends_keywords'][:5]
            pytrends.build_payload(keywords_batch, timeframe='today 1-m', geo='US')
            interest = pytrends.interest_over_time()

            if not interest.empty:
                last_week = interest.tail(7).mean()
                prev_week = interest.iloc[-14:-7].mean()

                for kw in keywords_batch:
                    if kw in last_week and kw in prev_week:
                        if prev_week[kw] > 0:
                            growth = ((last_week[kw] - prev_week[kw]) / prev_week[kw]) * 100
                            if growth > 10:
                                all_trends.append({
                                    'topic': kw,
                                    'score': min(int(growth), 100),
                                    'type': 'surging',
                                    'source': 'google_trends_growth',
                                    'seed_keyword': kw
                                })
        except Exception as e:
            logger.warning(f"Interest over time error: {e}")

    except Exception as e:
        logger.error(f"Google Trends overall error for {brand_key}: {e}")

    return all_trends


# ═══════════════════════════════════════════════════════════════
# DATA SOURCE 2: PINTEREST TRENDS (via Claude analysis)
# ═══════════════════════════════════════════════════════════════

def fetch_pinterest_trends(brand_key):
    """Discover what's trending on Pinterest for this niche via Claude analysis."""
    config = NICHE_CONFIGS[brand_key]

    response = _get_anthropic_client().messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""You are a Pinterest trends analyst. Based on your knowledge of what's
currently popular and trending on Pinterest, identify the top 10 trending topics
in this niche: {brand_key}

Pinterest-specific search terms to consider: {', '.join(config['pinterest_trends_searches'])}

For each trending topic, provide:
1. The specific trending topic/search term
2. Why it's trending (seasonal, viral, news-related, etc.)
3. A score from 1-100 for how hot this trend is right now

IMPORTANT: Focus on what's trending RIGHT NOW ({datetime.now().strftime('%B %Y')}), not evergreen topics.
Think about: seasonal trends, viral content, new products, cultural moments, health news.

Return ONLY a JSON array, no other text:
[
    {{"topic": "...", "reason": "...", "score": 85}},
    ...
]"""
        }]
    )

    try:
        content = response.content[0].text.strip()
        if content.startswith('```'):
            content = content.split('\n', 1)[1].rsplit('```', 1)[0]
        trends = json.loads(content)

        return [{
            'topic': t['topic'],
            'score': t.get('score', 50),
            'type': 'pinterest_trending',
            'source': 'pinterest_claude_analysis',
            'reason': t.get('reason', '')
        } for t in trends]
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Pinterest trends parse error: {e}")
        return []


# ═══════════════════════════════════════════════════════════════
# DATA SOURCE 3: WEB SEARCH FOR CURRENT TRENDS
# ═══════════════════════════════════════════════════════════════

def fetch_web_trends(brand_key):
    """Use Claude to synthesize trending topics from web knowledge."""
    config = NICHE_CONFIGS[brand_key]

    response = _get_anthropic_client().messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": f"""You are a content strategist researching what's trending RIGHT NOW
(the current week of {datetime.now().strftime('%B %Y')}) in the {brand_key} niche.

Think about:
- What news stories are relevant to this niche right now?
- What seasonal topics are people searching for in February?
- What products are getting buzz?
- What health/wellness trends are gaining momentum?
- What viral content or challenges are happening?
- What cultural events or awareness months are relevant?

Search queries to consider: {', '.join(config['trending_search_queries'])}

Return the top 10 currently trending topics as a JSON array:
[
    {{"topic": "specific trending topic", "reason": "why it's trending now", "score": 75, "content_angle": "how to create engaging content about this"}},
    ...
]

RULES:
- Be SPECIFIC — "creatine and hair loss study" not just "supplements"
- Focus on RIGHT NOW trends, not evergreen topics
- Include the content angle — how would a Pinterest creator make this interesting?
- Score should reflect how timely and trending this is (100 = viral right now, 50 = moderately popular, 25 = emerging)

Return ONLY the JSON array, no other text."""
        }]
    )

    try:
        content = response.content[0].text.strip()
        if content.startswith('```'):
            content = content.split('\n', 1)[1].rsplit('```', 1)[0]
        trends = json.loads(content)

        return [{
            'topic': t['topic'],
            'score': t.get('score', 50),
            'type': 'web_trending',
            'source': 'web_claude_analysis',
            'reason': t.get('reason', ''),
            'content_angle': t.get('content_angle', '')
        } for t in trends]
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Web trends parse error: {e}")
        return []


# ═══════════════════════════════════════════════════════════════
# TREND AGGREGATION + RANKING
# ═══════════════════════════════════════════════════════════════

def discover_weekly_trends(brand_key):
    """Master function: Fetch trends from all sources, filter, rank, select top 5."""
    config = NICHE_CONFIGS[brand_key]

    print(f"\n{'='*60}")
    print(f"DISCOVERING TRENDS FOR: {brand_key.upper()}")
    print(f"{'='*60}")

    all_trends = []

    print("Fetching Google Trends...")
    google_trends = fetch_google_trends(brand_key)
    all_trends.extend(google_trends)
    print(f"  Found {len(google_trends)} Google Trends results")

    print("Analyzing Pinterest trends...")
    pinterest_trends = fetch_pinterest_trends(brand_key)
    all_trends.extend(pinterest_trends)
    print(f"  Found {len(pinterest_trends)} Pinterest trend results")

    print("Searching web for current trends...")
    web_trends = fetch_web_trends(brand_key)
    all_trends.extend(web_trends)
    print(f"  Found {len(web_trends)} web trend results")

    print(f"\nTotal raw trends: {len(all_trends)}")

    if not all_trends:
        print("WARNING: No trends found from any source. Using fallback topics.")
        return get_fallback_trends(brand_key)

    # Use Claude to filter, deduplicate, rank, and select the best trends
    pins_per_week = {"fitness": 21, "deals": 14, "menopause": 14}

    response = _get_anthropic_client().messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"""You are a content strategist selecting the best trending topics for a Pinterest brand.

BRAND: {brand_key}
RELEVANCE FILTER: {config['relevance_filter']}

Here are all the trending topics discovered from multiple sources:
{json.dumps(all_trends, indent=2)}

YOUR TASK:
1. FILTER — Remove any topics that don't pass the relevance filter above
2. DEDUPLICATE — Merge similar/overlapping topics into single entries
3. RANK — Score each remaining topic on: trendiness (is it hot RIGHT NOW?),
   Pinterest fit (will this work as visual content?), and engagement potential
   (will people click?)
4. SELECT — Pick the top 5 trending topics for this brand's week of content

For each selected topic, provide:
- A refined topic title (specific, Pinterest-friendly)
- The combined trend score (0-100)
- Why this topic is trending
- 3-4 specific pin ideas (titles) based on this trend
- What type of article would match this trend
- What affiliate products could be recommended in the article

Return ONLY this JSON:
{{
    "week_of": "{(datetime.now(timezone.utc) + timedelta(days=(7 - datetime.now(timezone.utc).weekday()) % 7)).strftime('%Y-%m-%d')}",
    "brand": "{brand_key}",
    "trending_topics": [
        {{
            "rank": 1,
            "topic": "specific trending topic title",
            "trend_score": 92,
            "why_trending": "explanation of why this is hot right now",
            "pin_ideas": [
                "Pin title idea 1 (curiosity-driven hook)",
                "Pin title idea 2 (different angle on same trend)",
                "Pin title idea 3 (controversy or myth-bust angle)",
                "Pin title idea 4 (personal story angle)"
            ],
            "article_concept": "What the matching website article should cover",
            "affiliate_products": ["product type 1", "product type 2", "product type 3"],
            "pins_to_assign": 3
        }}
    ]
}}

The "pins_to_assign" should total up to {pins_per_week[brand_key]} pins/week.
Distribute more pins to higher-ranked (more trending) topics."""
        }]
    )

    try:
        content = response.content[0].text.strip()
        if content.startswith('```'):
            content = content.split('\n', 1)[1].rsplit('```', 1)[0]
        weekly_trends = json.loads(content)

        print(f"\nSelected {len(weekly_trends.get('trending_topics', []))} trending topics for the week")
        for t in weekly_trends.get('trending_topics', []):
            print(f"  #{t['rank']}: {t['topic']} (score: {t['trend_score']}, pins: {t['pins_to_assign']})")

        return weekly_trends
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Trend ranking parse error: {e}")
        return get_fallback_trends(brand_key)


def get_fallback_trends(brand_key):
    """If all trend discovery fails, use evergreen topics that always perform."""
    fallbacks = {
        "fitness": {
            "week_of": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "brand": "fitness",
            "trending_topics": [
                {"rank": 1, "topic": "protein timing for muscle growth over 35", "trend_score": 60, "pins_to_assign": 5,
                 "why_trending": "Evergreen fitness topic",
                 "pin_ideas": ["The protein window myth debunked", "What I eat in a day for muscle at 38", "Morning protein vs evening protein results"],
                 "article_concept": "Complete guide to protein timing for men over 35", "affiliate_products": ["protein powder", "meal prep containers"]},
                {"rank": 2, "topic": "home gym essentials on a budget", "trend_score": 55, "pins_to_assign": 5,
                 "why_trending": "Evergreen fitness topic",
                 "pin_ideas": ["$200 home gym that replaced my membership", "5 pieces of equipment I actually use daily"],
                 "article_concept": "Building a home gym under $300", "affiliate_products": ["resistance bands", "adjustable dumbbells", "pull-up bar"]},
                {"rank": 3, "topic": "belly fat after 35 real solutions", "trend_score": 55, "pins_to_assign": 4,
                 "why_trending": "Evergreen fitness topic",
                 "pin_ideas": ["Why crunches won't fix belly fat after 35", "The morning habit that targets belly fat"],
                 "article_concept": "Evidence-based belly fat reduction for men over 35", "affiliate_products": ["body fat calipers", "meal plan service"]},
                {"rank": 4, "topic": "creatine for men over 35", "trend_score": 50, "pins_to_assign": 4,
                 "why_trending": "Evergreen fitness topic",
                 "pin_ideas": ["I took creatine for 90 days at 37", "Creatine monohydrate vs HCL honest review"],
                 "article_concept": "Complete creatine guide for men over 35", "affiliate_products": ["creatine monohydrate", "creatine HCL"]},
                {"rank": 5, "topic": "sleep and recovery optimization", "trend_score": 45, "pins_to_assign": 3,
                 "why_trending": "Evergreen fitness topic",
                 "pin_ideas": ["The sleep hack that improved my recovery 40%", "Why 6 hours isn't enough after 35"],
                 "article_concept": "Sleep optimization for fitness recovery", "affiliate_products": ["magnesium supplement", "sleep mask"]}
            ]
        },
        "deals": {
            "week_of": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "brand": "deals",
            "trending_topics": [
                {"rank": 1, "topic": "spring organization refresh", "trend_score": 60, "pins_to_assign": 4,
                 "why_trending": "Seasonal",
                 "pin_ideas": ["The $30 closet system that changed my mornings", "Pantry organization before and after"],
                 "article_concept": "Spring organization guide under $100", "affiliate_products": ["storage containers", "label maker"]},
                {"rank": 2, "topic": "kitchen gadgets worth buying 2026", "trend_score": 55, "pins_to_assign": 4,
                 "why_trending": "Evergreen",
                 "pin_ideas": ["The kitchen tool I use more than my stove", "5 gadgets under $25 I actually kept"],
                 "article_concept": "Best kitchen gadgets under $30", "affiliate_products": ["air fryer accessories", "vegetable chopper"]},
                {"rank": 3, "topic": "self care routine affordable", "trend_score": 50, "pins_to_assign": 3,
                 "why_trending": "Evergreen",
                 "pin_ideas": ["My $15 self care Sunday routine", "Drugstore products that rival luxury brands"],
                 "article_concept": "Affordable self care routine guide", "affiliate_products": ["face masks", "bath products"]},
                {"rank": 4, "topic": "valentines day gift ideas", "trend_score": 50, "pins_to_assign": 3,
                 "why_trending": "Seasonal February",
                 "pin_ideas": ["Gift ideas she actually wants under $50", "Last minute gift guide"],
                 "article_concept": "Valentine's Day gift guide", "affiliate_products": ["jewelry", "home spa set"]}
            ]
        },
        "menopause": {
            "week_of": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "brand": "menopause",
            "trending_topics": [
                {"rank": 1, "topic": "managing hot flashes naturally", "trend_score": 60, "pins_to_assign": 4,
                 "why_trending": "Evergreen",
                 "pin_ideas": ["The cooling trick my doctor recommended", "Foods that trigger hot flashes"],
                 "article_concept": "Natural hot flash management guide", "affiliate_products": ["cooling pillow", "black cohosh"]},
                {"rank": 2, "topic": "menopause and sleep disruption", "trend_score": 55, "pins_to_assign": 4,
                 "why_trending": "Evergreen",
                 "pin_ideas": ["The bedtime routine that fixed my menopause insomnia", "Why melatonin might not be enough"],
                 "article_concept": "Sleep solutions for menopause", "affiliate_products": ["magnesium glycinate", "cooling sheets"]},
                {"rank": 3, "topic": "perimenopause symptoms checklist", "trend_score": 50, "pins_to_assign": 3,
                 "why_trending": "Evergreen",
                 "pin_ideas": ["12 perimenopause signs your doctor might miss", "Is this perimenopause or just stress?"],
                 "article_concept": "Complete perimenopause symptoms guide", "affiliate_products": ["menopause planner", "hormone test kit"]},
                {"rank": 4, "topic": "menopause weight gain strategies", "trend_score": 50, "pins_to_assign": 3,
                 "why_trending": "Evergreen",
                 "pin_ideas": ["Why your old diet stopped working", "The metabolism shift nobody warned me about"],
                 "article_concept": "Managing weight during menopause", "affiliate_products": ["protein powder", "food scale"]}
            ]
        }
    }

    return fallbacks.get(brand_key, fallbacks["fitness"])


# ═══════════════════════════════════════════════════════════════
# WEEKLY CONTENT CALENDAR BUILDER
# ═══════════════════════════════════════════════════════════════

def build_weekly_calendar(weekly_trends, brand_key, supabase_client):
    """Build a 7-day content calendar from discovered trends."""
    from .content_brain import BRAND_CONFIGS
    pins_per_day = {"fitness": 3, "deals": 2, "menopause": 2}
    daily_count = pins_per_day[brand_key]
    brand_config = BRAND_CONFIGS[brand_key]

    topics = weekly_trends.get('trending_topics', [])
    if not topics:
        print(f"No trending topics for {brand_key}, skipping calendar build")
        return None

    week_start = datetime.now(timezone.utc) + timedelta(days=(7 - datetime.now(timezone.utc).weekday()) % 7)
    week_start_str = week_start.strftime('%Y-%m-%d')

    response = _get_anthropic_client().messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=6000,
        messages=[{
            "role": "user",
            "content": f"""Create a detailed 7-day Pinterest content calendar for the {brand_key} brand.

PINS PER DAY: {daily_count}
TOTAL PINS THIS WEEK: {daily_count * 7}
PINTEREST BOARDS: {json.dumps(brand_config['pinterest_boards'])}

TRENDING TOPICS FOR THIS WEEK (with allocated pin counts):
{json.dumps(topics, indent=2)}

For each day (Monday through Sunday), assign specific pins. Each pin needs:
- Which trending topic it's about
- A specific pin title (curiosity-driven, not generic)
- A brief description concept
- Pin type: "static_image", "infographic", "carousel", or "video"
- Which Pinterest board to target

RULES:
- Spread each trending topic's pins across different days
- Vary pin types across the week
- Each day's pins should feel different from each other
- Pin titles must all be unique and use different hook frameworks
- Make the distribution feel natural, not robotic

Return ONLY this JSON:
{{
    "brand": "{brand_key}",
    "week_starting": "{week_start_str}",
    "days": [
        {{
            "day": "Monday",
            "date": "{week_start_str}",
            "pins": [
                {{
                    "slot": 1,
                    "trending_topic": "the trending topic this pin is about",
                    "title": "Specific curiosity-driven pin title",
                    "description_concept": "Brief concept for the description",
                    "pin_type": "static_image",
                    "board": "Board Name",
                    "article_slug": "url-friendly-article-slug"
                }}
            ]
        }}
    ]
}}"""
        }]
    )

    try:
        content = response.content[0].text.strip()
        if content.startswith('```'):
            content = content.split('\n', 1)[1].rsplit('```', 1)[0]
        calendar = json.loads(content)

        # Store the calendar in Supabase
        try:
            supabase_client.table('weekly_calendar').insert({
                'brand': brand_key,
                'week_starting': calendar.get('week_starting', week_start_str),
                'calendar_data': json.dumps(calendar),
                'trends_data': json.dumps(weekly_trends),
                'created_at': datetime.now(timezone.utc).isoformat()
            }).execute()
            print(f"Weekly calendar for {brand_key} saved to Supabase")
        except Exception as e:
            logger.error(f"Failed to save calendar to Supabase (table may not exist): {e}")
            print(f"WARNING: Calendar generated but not saved to Supabase. Run weekly_calendar_schema.sql first.")

        return calendar

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Calendar build error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# PERFORMANCE REVIEW
# ═══════════════════════════════════════════════════════════════

def review_last_week_performance(brand_key, supabase_client):
    """Check how last week's trending topics performed."""
    one_week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    try:
        last_calendar = supabase_client.table('weekly_calendar') \
            .select('*') \
            .eq('brand', brand_key) \
            .lt('created_at', datetime.now(timezone.utc).isoformat()) \
            .gte('created_at', one_week_ago) \
            .order('created_at', desc=True) \
            .limit(1) \
            .execute()

        last_week_pins = supabase_client.table('content_history') \
            .select('*') \
            .eq('brand', brand_key) \
            .gte('created_at', one_week_ago) \
            .execute()

        return {
            "pins_generated": len(last_week_pins.data) if last_week_pins.data else 0,
            "topics_used": list(set(p.get('topic', '') for p in (last_week_pins.data or []))),
            "had_calendar": bool(last_calendar.data),
            "insights": "Check Pinterest analytics dashboard for click data",
            "avoid_topics": [],
            "boost_topics": []
        }
    except Exception as e:
        logger.error(f"Performance review error: {e}")
        return {"pins_generated": 0, "insights": f"Review failed: {e}", "avoid_topics": [], "boost_topics": []}


# ═══════════════════════════════════════════════════════════════
# MASTER ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════

def run_weekly_discovery(supabase_client):
    """Master function called every Sunday night. Discovers trends and builds calendars."""
    results = {}

    for brand_key in ['fitness', 'deals', 'menopause']:
        print(f"\n{'#'*60}")
        print(f"# WEEKLY DISCOVERY: {brand_key.upper()}")
        print(f"{'#'*60}")

        # Step 1: Review last week
        print("\n--- Reviewing last week's performance ---")
        review = review_last_week_performance(brand_key, supabase_client)
        print(f"Last week: {review.get('pins_generated', 0)} pins generated")

        # Step 2: Discover this week's trends
        print("\n--- Discovering this week's trends ---")
        trends = discover_weekly_trends(brand_key)

        # Step 3: Build the weekly calendar
        print("\n--- Building weekly content calendar ---")
        try:
            calendar = build_weekly_calendar(trends, brand_key, supabase_client)
        except Exception as e:
            logger.error(f"Calendar build failed for {brand_key}: {e}")
            print(f"ERROR building calendar for {brand_key}: {e}")
            calendar = None

        results[brand_key] = {
            'trends': trends,
            'calendar': calendar,
            'last_week_review': review
        }

    return results
