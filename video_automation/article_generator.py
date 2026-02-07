"""Article Generator.

Creates a unique, SEO-optimized article for each trending topic in the weekly calendar.
Articles are published to the brand's website BEFORE the pins are posted.
Each article includes: value content, email capture CTA, affiliate product recommendations.
"""

import os
import json
import logging
from datetime import datetime

import anthropic

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    """Lazy-initialize the Anthropic client to prevent import-time failures."""
    global _client
    if _client is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client

# Load affiliate config
AFFILIATE_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'monetization', 'affiliate_config.json'
)


def _load_affiliate_config():
    try:
        with open(AFFILIATE_CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Affiliate config not found at {AFFILIATE_CONFIG_PATH}")
        return {}


def generate_article_for_trend(brand_key, trending_topic, article_slug, supabase_client):
    """Generate a full SEO article for a specific trending topic."""
    from .content_brain import BRAND_CONFIGS

    affiliate_config = _load_affiliate_config()
    brand_affiliates = affiliate_config.get(brand_key, {}).get('programs', [])
    brand_config = BRAND_CONFIGS[brand_key]

    lead_magnets = {
        "fitness": "FREE 7-Day Fat Burn Kickstart Plan",
        "deals": "FREE Weekly Deals Digest — best finds delivered to your inbox",
        "menopause": "FREE Menopause Symptom Tracker & Relief Guide"
    }

    response = _get_client().messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"""Write a comprehensive, valuable article for the {brand_config['name']} website about this trending topic:

TRENDING TOPIC: {trending_topic['topic']}
WHY IT'S TRENDING: {trending_topic.get('why_trending', trending_topic.get('reason', 'Currently popular'))}
ARTICLE URL SLUG: {article_slug}

BRAND VOICE: {brand_config['voice']}

ARTICLE REQUIREMENTS:

1. LENGTH: 1,200-1,800 words. Substantial enough to rank in Google, not padded with fluff.

2. STRUCTURE:
   - Compelling H1 title (include primary keyword, make it click-worthy)
   - Meta description (155 chars, includes keyword)
   - Opening paragraph that hooks immediately
   - 4-6 H2 sections that each provide standalone value
   - Conversational but authoritative tone
   - Conclusion with clear next steps

3. EMAIL CAPTURE CTA — Insert naturally after the 2nd or 3rd section:
   "Want more? Get our {lead_magnets.get(brand_key, 'FREE guide')} — delivered straight to your inbox. [SIGNUP_FORM_PLACEHOLDER]"

4. AFFILIATE PRODUCT RECOMMENDATIONS — Include 2-3 product recommendations naturally:
   **[Product Name]** — [1-2 sentence honest review]. [AFFILIATE_LINK_PLACEHOLDER:{brand_key}:{'{product_category}'}]
   Available: {json.dumps([p.get('name', '') for p in brand_affiliates])}

5. INTERNAL LINKS — Include 2-3 links to other articles:
   [Related: Article Title](/articles/related-slug/)

6. SEO KEYWORDS — Naturally include these:
   {', '.join(brand_config['seo_keywords'][:8])}

7. IMAGES — Include 3-4 image placeholders:
   ![Alt text](PEXELS_IMAGE_PLACEHOLDER:specific search query)

8. The article MUST provide genuine value. This is a real resource, not thin content.

OUTPUT FORMAT — Return as Markdown with frontmatter:
---
title: "Article Title Here"
slug: "{article_slug}"
meta_description: "155 char meta description"
date: "{datetime.utcnow().strftime('%Y-%m-%d')}"
brand: "{brand_key}"
trending_topic: "{trending_topic['topic']}"
keywords: ["keyword1", "keyword2", "keyword3"]
---

[Article content in Markdown]"""
        }]
    )

    article_content = response.content[0].text.strip()

    # Log the article generation
    try:
        supabase_client.table('generated_articles').insert({
            'brand': brand_key,
            'slug': article_slug,
            'trending_topic': trending_topic['topic'],
            'content_preview': article_content[:500],
            'word_count': len(article_content.split()),
            'created_at': datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        logger.error(f"Failed to log article: {e}")

    return article_content


MAX_ARTICLES_PER_BRAND = 3  # Limit per run to prevent workflow timeout


def generate_articles_for_weekly_calendar(calendar, brand_key, supabase_client):
    """Generate articles for all unique trending topics in the weekly calendar."""
    if not calendar or 'days' not in calendar:
        print(f"No calendar data for {brand_key}, skipping article generation")
        return {}

    # Extract unique article slugs and their topics
    articles_needed = {}
    for day in calendar['days']:
        for pin in day.get('pins', []):
            slug = pin.get('article_slug', '')
            topic_name = pin.get('trending_topic', '')
            if slug and slug not in articles_needed:
                articles_needed[slug] = topic_name

    total = len(articles_needed)
    if total > MAX_ARTICLES_PER_BRAND:
        print(f"Limiting {brand_key} from {total} to {MAX_ARTICLES_PER_BRAND} articles per run")
        articles_needed = dict(list(articles_needed.items())[:MAX_ARTICLES_PER_BRAND])

    print(f"Generating {len(articles_needed)} articles for {brand_key}")

    # Get trending topics from the calendar's parent data if available
    trending_topics_list = []
    if isinstance(calendar, dict) and 'trending_topics' in calendar:
        trending_topics_list = calendar['trending_topics']

    generated = {}
    for slug, topic_name in articles_needed.items():
        # Find the full trending topic data
        trending_topic = None
        for t in trending_topics_list:
            if t.get('topic', '').lower() in topic_name.lower() or topic_name.lower() in t.get('topic', '').lower():
                trending_topic = t
                break

        if not trending_topic:
            trending_topic = {'topic': topic_name, 'why_trending': 'Currently trending in this niche'}

        print(f"  Generating article: {slug}")
        try:
            article = generate_article_for_trend(brand_key, trending_topic, slug, supabase_client)
            generated[slug] = article
            print(f"  Done ({len(article.split())} words)")
        except Exception as e:
            logger.error(f"Article generation failed for {slug}: {e}")
            generated[slug] = None

    return generated


def publish_article_to_website(article_content, brand_key, slug):
    """Publish the generated article to the brand's website directory."""
    website_paths = {
        "fitness": "outputs/fitover35-website/articles",
        "deals": "outputs/dailydealdarling-website/articles",
        "menopause": "outputs/menopause-planner-website/articles"
    }

    articles_dir = website_paths.get(brand_key, website_paths["fitness"])
    workspace = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.dirname(__file__)))
    full_dir = os.path.join(workspace, articles_dir)

    os.makedirs(full_dir, exist_ok=True)

    file_path = os.path.join(full_dir, f"{slug}.md")
    with open(file_path, 'w') as f:
        f.write(article_content)

    print(f"Article published: {file_path}")
    return file_path
