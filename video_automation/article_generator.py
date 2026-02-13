"""Article Generator.

Creates a unique, SEO-optimized article for each trending topic in the weekly calendar.
Articles are published to the brand's website BEFORE the pins are posted.
Each article includes: value content, email capture CTA, affiliate product recommendations.
"""

import os
import json
import re
import logging
from datetime import datetime, timezone

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


# ── Research-Writer Prompts ─────────────────────────────────────────────────

ARTICLE_RESEARCH_PROMPT = """You are a content researcher for the {brand_name} brand.

BRAND VOICE: {voice}

Research the following trending topic for an SEO article:
TOPIC: {topic}
WHY IT'S TRENDING: {why_trending}

Compile:
1. 3-5 statistics with sources (cite author/organization and year — use real, well-known studies or health organizations)
2. 2-3 expert perspectives (real researchers, doctors, or recognized authorities who have published on this topic)
3. 1 common misconception the audience likely holds
4. 3 opening hook options:
   - bold_statement: A confident, specific claim that challenges conventional thinking
   - story_hook: A brief relatable anecdote that creates connection
   - data_hook: Lead with a surprising statistic
5. 5-7 suggested H2 section headings for the article

Return ONLY valid JSON:
{{
    "statistics": [
        {{"fact": "The finding", "source": "Author/Organization, Year"}}
    ],
    "expert_perspectives": [
        {{"expert": "Name and credentials", "insight": "What they found or recommend"}}
    ],
    "misconception": "A common myth about this topic",
    "hooks": {{
        "bold_statement": "Hook text",
        "story_hook": "Hook text",
        "data_hook": "Hook text"
    }},
    "suggested_sections": ["Section heading 1", "Section heading 2"]
}}
"""

ARTICLE_GENERATION_PROMPT = """Write a comprehensive, valuable article for the {brand_name} website about this trending topic:

TRENDING TOPIC: {topic}
WHY IT'S TRENDING: {why_trending}
ARTICLE URL SLUG: {article_slug}

BRAND VOICE: {voice}

OPEN THE ARTICLE WITH THIS HOOK:
{best_hook}

RESEARCH TO WEAVE INTO THE ARTICLE (cite conversationally, not as footnotes):
{research_json}

Examples of good inline citations:
- "A 2024 study published in [Journal] found that..."
- "According to [Expert Name], a [credentials]..."
- "The [Organization] recommends..."
Do NOT add a references section. Weave citations naturally into the text.

ARTICLE REQUIREMENTS:

1. LENGTH: 1,200-1,800 words. Substantial enough to rank in Google, not padded with fluff.

2. STRUCTURE:
   - Compelling H1 title (include primary keyword, make it click-worthy)
   - Meta description (155 chars, includes keyword)
   - Opening with the hook above, then transition into value
   - 4-6 H2 sections that each provide standalone value
   - Conversational but authoritative tone
   - Conclusion with clear next steps

3. EMAIL CAPTURE CTA — Insert naturally after the 2nd or 3rd section:
   "Want more? Get our {lead_magnet} — delivered straight to your inbox. [SIGNUP_FORM_PLACEHOLDER]"

4. AFFILIATE PRODUCT RECOMMENDATIONS — Include 2-3 product recommendations naturally:
   **[Product Name]** — [1-2 sentence honest review]. [AFFILIATE_LINK_PLACEHOLDER:{brand_key}:{{product_category}}]
   Available: {affiliate_names}

5. INTERNAL LINKS — Include 2-3 links to other articles:
   [Related: Article Title](/articles/related-slug/)

6. SEO KEYWORDS — Naturally include these:
   {seo_keywords}

7. IMAGES — Include 3-4 image placeholders:
   ![Alt text](PEXELS_IMAGE_PLACEHOLDER:specific search query)

8. VOICE CHECK: Read your output back. If any sentence sounds like a corporate blog, a textbook, or generic health content, rewrite it in the brand voice.

9. FILLER BAN: Do not use: "in today's fast-paced world", "it's important to note", "when it comes to", "at the end of the day", "it goes without saying"

OUTPUT FORMAT — Return as Markdown with frontmatter:
---
title: "Article Title Here"
slug: "{article_slug}"
meta_description: "155 char meta description"
date: "{date_today}"
brand: "{brand_key}"
trending_topic: "{topic}"
keywords: ["keyword1", "keyword2", "keyword3"]
---

[Article content in Markdown]"""

ARTICLE_REVIEW_PROMPT = """You are a senior editor reviewing an article before publication for the {brand_name} brand.

BRAND VOICE: {voice}

Review and improve the following article. Check for:

1. VOICE: Every sentence should match the brand voice above. Rewrite anything that sounds generic, clinical, or corporate.
2. UNSUPPORTED CLAIMS: Soften any health/fitness/product claims that lack a citation. Add "research suggests" or "according to [source]" where needed.
3. FILLER: Remove or replace: "in today's fast-paced world", "it's important to note", "when it comes to", "at the end of the day", "it goes without saying", "the fact of the matter is", "in conclusion"
4. SPECIFICITY: Replace vague advice with specific, actionable recommendations.
5. FLOW: Ensure smooth transitions between sections.

Return the IMPROVED article in the same format (Markdown with frontmatter). Keep all placeholders ([SIGNUP_FORM_PLACEHOLDER], [AFFILIATE_LINK_PLACEHOLDER:...], PEXELS_IMAGE_PLACEHOLDER:...) intact.

ARTICLE TO REVIEW:
{article_content}
"""


def _research_topic(brand_key, brand_config, trending_topic):
    """Research a trending topic before writing the article."""
    logger.info(f"Researching topic: {trending_topic.get('topic', '?')}")
    prompt = ARTICLE_RESEARCH_PROMPT.format(
        brand_name=brand_config['name'],
        voice=brand_config['voice'],
        topic=trending_topic['topic'],
        why_trending=trending_topic.get('why_trending', trending_topic.get('reason', 'Currently popular'))
    )
    try:
        response = _get_client().messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        # Parse JSON from response
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                return json.loads(json_match.group())
    except Exception as e:
        logger.warning(f"Research step failed: {e}")
    return {}


def _review_article(brand_config, article_content):
    """Lightweight editorial review pass."""
    logger.info("Running editorial review")
    prompt = ARTICLE_REVIEW_PROMPT.format(
        brand_name=brand_config['name'],
        voice=brand_config['voice'],
        article_content=article_content
    )
    try:
        response = _get_client().messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        reviewed = response.content[0].text.strip()
        # Safety: if review output is suspiciously short, keep original
        if len(reviewed) < len(article_content) * 0.6:
            logger.warning("Review output too short, keeping original")
            return article_content
        return reviewed
    except Exception as e:
        logger.warning(f"Editorial review failed: {e} — keeping original")
        return article_content


def generate_article_for_trend(brand_key, trending_topic, article_slug, supabase_client):
    """Generate a full SEO article for a specific trending topic.

    Uses a 3-step content-research-writer methodology:
    1. Research: statistics, expert perspectives, hooks
    2. Article Generation: with research data + best hook
    3. Editorial Review: voice, claims, filler check

    Set ENHANCED_ARTICLES=false env var to skip steps 1 + 3.
    """
    from .content_brain import BRAND_CONFIGS

    enhanced = os.environ.get('ENHANCED_ARTICLES', 'true').lower() != 'false'

    affiliate_config = _load_affiliate_config()
    brand_affiliates = affiliate_config.get(brand_key, {}).get('programs', [])
    brand_config = BRAND_CONFIGS[brand_key]

    lead_magnets = {
        "fitness": "FREE 7-Day Fat Burn Kickstart Plan",
        "deals": "FREE Weekly Deals Digest — best finds delivered to your inbox",
        "menopause": "FREE Menopause Symptom Tracker & Relief Guide"
    }

    # Step 1: Research (skip if not enhanced)
    research = {}
    best_hook = ""
    if enhanced:
        research = _research_topic(brand_key, brand_config, trending_topic)
        # Pick best hook: prefer data_hook, fall back to bold_statement
        hooks = research.get('hooks', {})
        best_hook = hooks.get('data_hook', '') or hooks.get('bold_statement', '')

    # Step 2: Generate article (with or without research)
    research_json = json.dumps(research, indent=2) if research else "No research data — use your expertise."

    response = _get_client().messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": ARTICLE_GENERATION_PROMPT.format(
                brand_name=brand_config['name'],
                topic=trending_topic['topic'],
                why_trending=trending_topic.get('why_trending', trending_topic.get('reason', 'Currently popular')),
                article_slug=article_slug,
                voice=brand_config['voice'],
                best_hook=best_hook or "Write a compelling opening hook that immediately grabs the reader.",
                research_json=research_json,
                lead_magnet=lead_magnets.get(brand_key, 'FREE guide'),
                brand_key=brand_key,
                affiliate_names=json.dumps([p.get('name', '') for p in brand_affiliates]),
                seo_keywords=', '.join(brand_config['seo_keywords'][:8]),
                date_today=datetime.now(timezone.utc).strftime('%Y-%m-%d'),
            )
        }]
    )

    article_content = response.content[0].text.strip()

    # Step 3: Editorial Review (skip if not enhanced)
    if enhanced:
        article_content = _review_article(brand_config, article_content)

    # Log the article generation
    try:
        supabase_client.table('generated_articles').insert({
            'brand': brand_key,
            'slug': article_slug,
            'trending_topic': trending_topic['topic'],
            'content_preview': article_content[:500],
            'word_count': len(article_content.split()),
            'created_at': datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception as e:
        logger.error(f"Failed to log article: {e}")

    return article_content


MAX_ARTICLES_PER_BRAND = 2  # Reduced from 3 to offset extra API calls per article


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
