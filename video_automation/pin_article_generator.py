"""Lightweight article generator for per-pin blog posts.

Generates a short SEO article (800-1200 words) for each pin during
the content-engine run. One Claude API call per article.
Articles are saved as HTML to the brand's website directory and
registered in the generated_articles Supabase table.
"""

import os
import re
import json
import logging
import urllib.parse
from datetime import datetime, timezone

import requests
import anthropic

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


# ── Amazon Associates affiliate links ──────────────────────────────────────────
# NOTE: All brands currently use tag=dailydealdarl-20 (single Associates account).
# When separate Associates accounts are set up per brand, update tags here:
#   fitness  -> tag=fitover35-20
#   deals    -> tag=dailydealdarl-20
#   menopause -> tag=menopauseplan-20
# Direct /dp/ASIN links are preferred. For any product NOT in this list, the
# code falls back to Amazon search URLs (/s?k=...) which always work.

AMAZON_AFFILIATE_LINKS = {
    "fitness": {
        "creatine monohydrate": "https://www.amazon.com/dp/B002DYIZEO?tag=dailydealdarl-20",
        "vitamin D3": "https://www.amazon.com/dp/B00GB85JR4?tag=dailydealdarl-20",
        "magnesium glycinate": "https://www.amazon.com/dp/B000BD0RT0?tag=dailydealdarl-20",
        "fish oil": "https://www.amazon.com/dp/B004O2I9JO?tag=dailydealdarl-20",
        "ashwagandha": "https://www.amazon.com/dp/B078K18HYN?tag=dailydealdarl-20",
        "protein powder": "https://www.amazon.com/dp/B000QSNYGI?tag=dailydealdarl-20",
        "collagen peptides": "https://www.amazon.com/dp/B00K6JUG40?tag=dailydealdarl-20",
        "resistance bands set": "https://www.amazon.com/dp/B01AVDVHTI?tag=dailydealdarl-20",
        "adjustable dumbbells": "https://www.amazon.com/dp/B001ARYU58?tag=dailydealdarl-20",
        "pull-up bar": "https://www.amazon.com/dp/B001EJMS6K?tag=dailydealdarl-20",
        "foam roller": "https://www.amazon.com/dp/B0040EKZDY?tag=dailydealdarl-20",
        "yoga mat": "https://www.amazon.com/dp/B01LYBOA9L?tag=dailydealdarl-20",
        "stretching strap": "https://www.amazon.com/dp/B07YQ2BX91?tag=dailydealdarl-20",
        "kettlebell": "https://www.amazon.com/dp/B003J9E5WO?tag=dailydealdarl-20",
        "massage gun": "https://www.amazon.com/dp/B07MHBJYRH?tag=dailydealdarl-20",
        "food scale": "https://www.amazon.com/dp/B004164SRA?tag=dailydealdarl-20",
        "glass meal prep containers": "https://www.amazon.com/dp/B078RFVKNR?tag=dailydealdarl-20",
        "protein shaker": "https://www.amazon.com/dp/B01LZ2GH5O?tag=dailydealdarl-20",
        "workout gloves": "https://www.amazon.com/dp/B01MQGF4TQ?tag=dailydealdarl-20",
        "_default": "https://www.amazon.com/dp/B001ARYU58?tag=dailydealdarl-20",
    },
    "deals": {
        "air fryer": "https://www.amazon.com/dp/B07FDJMC9Q?tag=dailydealdarl-20",
        "knife set": "https://www.amazon.com/dp/B07TLZXRK2?tag=dailydealdarl-20",
        "meal prep containers": "https://www.amazon.com/dp/B078RFVKNR?tag=dailydealdarl-20",
        "organizer bins": "https://www.amazon.com/dp/B07DFDS56B?tag=dailydealdarl-20",
        "silk pillowcase": "https://www.amazon.com/dp/B07P3SQCV3?tag=dailydealdarl-20",
        "LED face mask": "https://www.amazon.com/dp/B07D3KVL4Z?tag=dailydealdarl-20",
        "label maker": "https://www.amazon.com/dp/B0719RFLTQ?tag=dailydealdarl-20",
        "drawer dividers": "https://www.amazon.com/dp/B073VB74FJ?tag=dailydealdarl-20",
        "throw pillows": "https://www.amazon.com/dp/B07DFDS56B?tag=dailydealdarl-20",
        "LED candles": "https://www.amazon.com/dp/B07P3SQCV3?tag=dailydealdarl-20",
        "_default": "https://www.amazon.com/dp/B07DFDS56B?tag=dailydealdarl-20",
    },
    "menopause": {
        "black cohosh": "https://www.amazon.com/dp/B0019LTI86?tag=dailydealdarl-20",
        "evening primrose oil": "https://www.amazon.com/dp/B00DWCZWHK?tag=dailydealdarl-20",
        "magnesium glycinate": "https://www.amazon.com/dp/B000BD0RT0?tag=dailydealdarl-20",
        "vitamin D3": "https://www.amazon.com/dp/B00GB85JR4?tag=dailydealdarl-20",
        "cooling pillow": "https://www.amazon.com/dp/B07C7FQBDT?tag=dailydealdarl-20",
        "bamboo sheets": "https://www.amazon.com/dp/B07QDFLQ7J?tag=dailydealdarl-20",
        "cooling pajamas": "https://www.amazon.com/dp/B07YC684QN?tag=dailydealdarl-20",
        "weighted blanket": "https://www.amazon.com/dp/B07H2DKQGJ?tag=dailydealdarl-20",
        "symptom tracker journal": "https://www.amazon.com/dp/B0BW9GDRP7?tag=dailydealdarl-20",
        "essential oils diffuser": "https://www.amazon.com/dp/B07L4R62GQ?tag=dailydealdarl-20",
        "collagen powder": "https://www.amazon.com/dp/B00K6JUG40?tag=dailydealdarl-20",
        "_default": "https://www.amazon.com/dp/B001G7QUXW?tag=dailydealdarl-20",
    },
}


# ── Brand website config ────────────────────────────────────────────────────

BRAND_SITE_CONFIG = {
    "fitness": {
        "site_name": "FitOver35",
        "base_url": "https://fitover35.com",
        "output_dir": "outputs/fitover35-website/articles",
        "primary_color": "#1565C0",
        "accent_color": "#0D47A1",
        "logo_html": 'Fit<span style="color:#1565C0">Over35</span>',
        "nav_links": [
            ("Home", "../index.html"),
            ("Articles", "../blog.html"),
            ("About", "../about.html"),
            ("Contact", "../contact.html"),
        ],
        "has_css": True,
        "lead_magnet": "FREE 7-Day Fat Burn Kickstart Plan",
        "signup_form_id": "8946984",
        "signup_button_text": "Get Free Program",
    },
    "deals": {
        "site_name": "Daily Deal Darling",
        "base_url": "https://dailydealdarling.com",
        "output_dir": "outputs/dailydealdarling-website/articles",
        "primary_color": "#E91E63",
        "accent_color": "#C2185B",
        "logo_html": 'Daily Deal <span style="color:#E91E63">Darling</span>',
        "nav_links": [
            ("Home", "../index.html"),
            ("Articles", "./"),
            ("About", "../about.html"),
        ],
        "has_css": True,
        "lead_magnet": "FREE Weekly Deals Digest",
        "signup_form_id": "9144859",
        "signup_button_text": "Join Free",
    },
    "menopause": {
        "site_name": "The Menopause Planner",
        "base_url": "https://menopause-planner-website.vercel.app",  # no custom domain yet
        "output_dir": "outputs/menopause-planner-website/articles",
        "primary_color": "#7B1FA2",
        "accent_color": "#6A1B9A",
        "logo_html": 'The Menopause <span style="color:#7B1FA2">Planner</span>',
        "nav_links": [
            ("Home", "../index.html"),
            ("Articles", "./"),
            ("About", "../about.html"),
        ],
        "has_css": False,
        "lead_magnet": "FREE Menopause Symptom Tracker & Relief Guide",
        "signup_form_id": "9144926",
        "signup_button_text": "Get Free Guide",
    },
}


def _get_approved_asins():
    """Build set of all ASINs in our approved product lists."""
    asins = set()
    for brand_links in AMAZON_AFFILIATE_LINKS.values():
        for url in brand_links.values():
            m = re.search(r'/dp/([A-Z0-9]{10})', url)
            if m:
                asins.add(m.group(1))
    return asins


_APPROVED_ASINS = None  # lazy-loaded


def _fetch_pexels_image(query, orientation='landscape'):
    """Fetch a stock photo URL from Pexels. Returns URL string or None."""
    pexels_key = os.environ.get('PEXELS_API_KEY', '')
    if not pexels_key:
        logger.info("No PEXELS_API_KEY — skipping hero image fetch")
        return None
    if not query:
        return None
    # Shorten overly long queries (Pexels works best with 3-5 words)
    words = query.split()
    if len(words) > 6:
        query = ' '.join(words[:6])
    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": pexels_key},
            params={"query": query, "per_page": 5, "orientation": orientation},
            timeout=10,
        )
        if resp.status_code == 200:
            photos = resp.json().get('photos', [])
            if photos:
                img_url = photos[0]['src']['large']
                logger.info(f"Hero image found for '{query}': {img_url[:80]}...")
                return img_url
            logger.warning(f"No Pexels results for query: '{query}'")
        else:
            logger.warning(f"Pexels API returned {resp.status_code} for '{query}'")
    except Exception as e:
        logger.warning(f"Pexels hero image fetch failed for '{query}': {e}")
    return None


def _build_product_card(link_text, amazon_url, primary_color='#1565C0'):
    """Build a styled product card div with Amazon product image."""
    asin_match = re.search(r'/dp/([A-Z0-9]{10})', amazon_url)
    img_html = ''
    if asin_match:
        asin = asin_match.group(1)
        img_url = f"https://m.media-amazon.com/images/P/{asin}.01.LZZZZZZZ.jpg"
        img_html = (
            f'<a href="{amazon_url}" target="_blank" rel="nofollow sponsored" style="flex-shrink:0;">'
            f'<img src="{img_url}" alt="{link_text}" width="90" height="90" '
            f'style="object-fit:contain;border-radius:8px;background:#f8f8f8;padding:4px;" loading="lazy" '
            f'onerror="this.parentElement.style.display=\'none\'">'
            f'</a>'
        )
    return (
        f'<div style="border:1px solid #e5e7eb;border-radius:12px;padding:16px;margin:16px 0;'
        f'display:flex;gap:16px;align-items:center;background:#fafafa;">'
        f'{img_html}'
        f'<div>'
        f'<strong style="display:block;margin-bottom:8px;font-size:1em;color:#111;">{link_text}</strong>'
        f'<a href="{amazon_url}" target="_blank" rel="nofollow sponsored" '
        f'style="display:inline-block;background:#FF9900;color:#111;padding:7px 18px;'
        f'border-radius:6px;text-decoration:none;font-weight:700;font-size:0.88em;">'
        f'Check Price on Amazon →</a>'
        f'</div></div>'
    )


def _inject_product_cards(body_html, brand_key):
    """Replace bolded Amazon links and list-item Amazon links with product cards."""
    primary_color = BRAND_SITE_CONFIG[brand_key]['primary_color']

    def _card_from_match(url, link_text):
        return _build_product_card(link_text, url, primary_color)

    # 1. Replace <strong><a href="amazon_url">text</a></strong> → product card
    body_html = re.sub(
        r'<strong><a href="([^"]*amazon\.com[^"]*)"[^>]*>([^<]+)</a></strong>',
        lambda m: _card_from_match(m.group(1), m.group(2)),
        body_html,
    )

    # 2. Replace <li> elements whose primary content is an Amazon link → product card
    def _upgrade_li(match):
        li_content = match.group(1)
        am = re.search(r'<a href="([^"]*amazon\.com[^"]*)"[^>]*>([^<]+)</a>', li_content)
        if not am:
            return match.group(0)
        return _card_from_match(am.group(1), am.group(2))

    body_html = re.sub(r'<li>(.*?)</li>', _upgrade_li, body_html, flags=re.DOTALL)

    # 3. Remove empty <ul></ul> wrappers left behind after li upgrades
    body_html = re.sub(r'<ul>\s*</ul>', '', body_html)

    return body_html


def _make_slug(topic):
    """Create a URL-safe slug from a topic string."""
    slug = topic.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug[:60]


def generate_article_for_pin(brand_key, pin_data, supabase_client):
    """Generate a short blog article matching a pin's topic.

    Returns (slug, markdown_content) or (None, None) if skipped.
    """
    from .content_brain import BRAND_CONFIGS

    topic = pin_data.get('topic', '') or pin_data.get('trending_topic', '')
    if not topic:
        logger.warning("No topic in pin_data, skipping article generation")
        return None, None

    slug = _make_slug(topic)
    if not slug:
        return None, None

    # Check if article already exists
    try:
        existing = supabase_client.table('generated_articles') \
            .select('slug') \
            .eq('brand', brand_key) \
            .eq('slug', slug) \
            .limit(1) \
            .execute()
        if existing.data:
            logger.info(f"Article already exists for slug '{slug}', skipping")
            return slug, None
    except Exception as e:
        logger.warning(f"Could not check existing articles: {e}")

    config = BRAND_CONFIGS[brand_key]
    site_config = BRAND_SITE_CONFIG[brand_key]

    # Gather affiliate products with Amazon links
    brand_amazon = AMAZON_AFFILIATE_LINKS.get(brand_key, {})
    affiliate_products = config.get('affiliate_products', {})
    category = pin_data.get('category', '')
    products = affiliate_products.get(category, [])
    if not products:
        all_products = []
        for cat_products in affiliate_products.values():
            all_products.extend(cat_products)
        products = all_products[:5]

    # Build product + Amazon link pairs for the prompt
    product_links = []
    for product in products[:6]:
        amazon_url = brand_amazon.get(product, brand_amazon.get('_default', ''))
        if amazon_url:
            product_links.append(f'- {product}: {amazon_url}')
        else:
            product_links.append(f'- {product}')
    products_text = '\n'.join(product_links) if product_links else 'none available'

    # Get tips from pin if available (for the article to expand on)
    tips = pin_data.get('tips', [])
    tips_section = ''
    if tips:
        tips_section = f"""
PIN TIPS (expand on each of these in the article):
{chr(10).join(f'{i+1}. {t}' for i, t in enumerate(tips))}
"""

    seo_keywords = ', '.join(config.get('seo_keywords', [])[:6])

    # ── Brand-specific template structure instructions ──
    if brand_key == 'fitness':
        template_section = (
            '\nTEMPLATE-SPECIFIC SECTIONS (The Iron Standard — dark, data-heavy):\n'
            '- Include a "Pro-Coach Insight" blockquote (use > **Pro-Coach Insight:**) '
            'explaining specific timing, dosage, or technique for maximum results.\n'
            '- If reviewing a product, include a "Pros vs Cons" section with clear bullet points '
            'comparing to 1-2 alternatives.\n'
            '- Write with high confidence and data-backed authority. Cite specific numbers, '
            'studies, or personal experience metrics where possible.'
        )
        etsy_cta_section = ''
        req_num_seo = '5'
        req_num_filler = '6'
    elif brand_key == 'menopause':
        template_section = (
            '\nTEMPLATE-SPECIFIC SECTIONS (The Wellness Whisper — empathetic, editorial):\n'
            '- Include a "Symptom Checklist" section with a bulleted list of specific symptoms '
            'this topic/product addresses (e.g., night sweats, fatigue, brain fog, mood changes).\n'
            '- Include a "What to Look For" or "Clean Label Breakdown" section highlighting '
            'ingredients, non-GMO status, certifications, or material safety.\n'
            '- Write with warmth and empathy — acknowledge the struggle, then provide hope '
            'and practical solutions.'
        )
        etsy_cta_section = (
            '\n5. ETSY PLANNER CTA (menopause brand only): In the conclusion section, naturally'
            ' mention and link to the Menopause Wellness Planner Bundle on Etsy. Frame it as a'
            ' practical next step — a printable digital planner to track symptoms, sleep,'
            ' supplements, and mood all in one place.\n'
            '   Use this exact link: https://www.etsy.com/listing/4435219468/'
            'menopause-wellness-planner-bundle?utm_source=Pinterest&utm_medium=organic\n'
            '   Format: [Menopause Wellness Planner Bundle](https://www.etsy.com/listing/'
            '4435219468/menopause-wellness-planner-bundle?utm_source=Pinterest&utm_medium=organic)\n'
            '   Keep it natural — one sentence, benefit-driven (e.g. "If you want a structured'
            ' way to track what\'s helping, the [Menopause Wellness Planner Bundle](link) on Etsy'
            ' gives you a printable symptom tracker, sleep log, and supplement guide in one'
            ' instant download.")'
        )
        req_num_seo = '6'
        req_num_filler = '7'
    else:  # deals
        template_section = (
            '\nTEMPLATE-SPECIFIC SECTIONS (The Aesthetic Edit — minimalist, magazine-style):\n'
            '- Include a "Why It\'s Trending" or "Social Proof" section mentioning star ratings, '
            'review counts, Pinterest saves, or TikTok virality.\n'
            '- Include practical details like dimensions, color options, compatibility, '
            'or how the product fits into a modern home aesthetic.\n'
            '- Write in a curated, editorial tone — like a boutique magazine recommending '
            'the best of the best.'
        )
        etsy_cta_section = ''
        req_num_seo = '5'
        req_num_filler = '6'

    prompt = f"""Write a focused, valuable blog article for the {config['name']} website.

BRAND VOICE:
{config['voice']}

ARTICLE TOPIC: {topic}
PIN TITLE: {pin_data.get('title', '')}
CATEGORY: {category}
{tips_section}{template_section}

REQUIREMENTS:
1. LENGTH: 800-1200 words. Substantial enough to rank, no filler.
2. STRUCTURE:
   - H1 title (include primary keyword, click-worthy, format: "[Topic]: Does it actually work for [Goal]?" for fitness, "Managing [Topic]: Why [Product] is a Game Changer for Women 40+" for menopause, "The {datetime.now(timezone.utc).year} Glow-Up: Why [Topic] is Trending on Pinterest" for deals)
   - Meta description (155 chars max, includes keyword + "Best of {datetime.now(timezone.utc).year}" or "Expert Verified")
   - 3-5 H2 sections with standalone value — if tips were provided above, dedicate a section to each tip with deeper detail
   - Conversational, authoritative tone matching the brand voice
   - Clear conclusion with next steps
3. EMAIL CTA: After the 2nd section, include on its own line:
   [SIGNUP_FORM_PLACEHOLDER]
4. AMAZON PRODUCT RECOMMENDATIONS: Include 3-5 product recommendations woven naturally into the article — one near the top (early hook), at least one mid-article, and one near the bottom (final CTA). Each product must feel like a genuine, helpful suggestion.
   MANDATORY LINK RULES:
   - For products in the list below: use the EXACT URL provided, character-for-character.
   - For any product NOT in the list: use Amazon search format — https://www.amazon.com/s?k=product+name+here&tag=dailydealdarl-20
   - NEVER invent /dp/ASIN URLs for products not in the list — invalid ASINs return error pages.
   - ALL Amazon links must include tag=dailydealdarl-20
   Format: **[Product Name](amazon_url)** — honest 1-2 sentence review explaining exactly WHY this product helps for this specific topic.
   End the article with a brief "Best Picks" or "My Top Recommendations" section that lists 2-3 of the products with links — this dramatically increases click-through.
   Approved products with direct Amazon links (use these exact URLs):
{products_text}{etsy_cta_section}
{req_num_seo}. SEO KEYWORDS: Naturally include: {seo_keywords}
{req_num_filler}. FILLER BAN: Never use "in today's fast-paced world", "it's important to note",
   "when it comes to", "at the end of the day", "it goes without saying"

OUTPUT FORMAT — Return as Markdown with frontmatter:
---
title: "Article Title"
slug: "{slug}"
meta_description: "155 char description"
date: "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
brand: "{brand_key}"
keywords: ["keyword1", "keyword2", "keyword3"]
---

[Article content in Markdown]"""

    try:
        response = _get_client().messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        article_md = response.content[0].text.strip()
        return slug, article_md
    except Exception as e:
        logger.error(f"Article generation failed for '{topic}': {e}")
        return slug, None


def _extract_frontmatter(markdown_content):
    """Extract title and meta_description from frontmatter."""
    title = ""
    meta_desc = ""
    match = re.search(r'^---\s*\n(.*?)\n---', markdown_content, re.DOTALL)
    if match:
        fm = match.group(1)
        title_match = re.search(r'title:\s*"([^"]*)"', fm)
        if title_match:
            title = title_match.group(1)
        desc_match = re.search(r'meta_description:\s*"([^"]*)"', fm)
        if desc_match:
            meta_desc = desc_match.group(1)
    return title, meta_desc


def _markdown_to_html_body(markdown_content):
    """Simple markdown to HTML conversion for article body.

    Handles: headings, bold, italic, paragraphs, lists, links,
    and the SIGNUP_FORM_PLACEHOLDER.
    """
    # Strip frontmatter
    body = re.sub(r'^---\s*\n.*?\n---\s*\n?', '', markdown_content, flags=re.DOTALL)
    body = body.strip()

    lines = body.split('\n')
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Empty line
        if not stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            continue

        # Signup form placeholder
        if '[SIGNUP_FORM_PLACEHOLDER]' in stripped:
            html_lines.append(stripped.replace('[SIGNUP_FORM_PLACEHOLDER]', '<!-- email-signup-placeholder -->'))
            continue

        # Headings
        if stripped.startswith('# '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            level = len(stripped.split(' ')[0])
            text = stripped.lstrip('#').strip()
            text = _inline_format(text)
            html_lines.append(f'<h{level}>{text}</h{level}>')
            continue

        heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if heading_match:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            level = len(heading_match.group(1))
            text = _inline_format(heading_match.group(2))
            html_lines.append(f'<h{level}>{text}</h{level}>')
            continue

        # List items
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            text = _inline_format(stripped[2:])
            html_lines.append(f'  <li>{text}</li>')
            continue

        # Regular paragraph
        if in_list:
            html_lines.append('</ul>')
            in_list = False
        text = _inline_format(stripped)
        html_lines.append(f'<p>{text}</p>')

    if in_list:
        html_lines.append('</ul>')

    return '\n'.join(html_lines)


def _inline_format(text):
    """Apply inline markdown formatting (bold, italic, links)."""
    global _APPROVED_ASINS

    # Links [text](url) — Amazon affiliate links get nofollow + new tab
    def _link_replace(match):
        global _APPROVED_ASINS
        link_text = match.group(1)
        url = match.group(2)
        if 'amazon.com' in url and 'tag=' in url:
            # Sanitize: if Claude invented a /dp/ASIN not in our approved list,
            # replace with a search URL that always works.
            asin_m = re.search(r'/dp/([A-Z0-9]{10})', url)
            if asin_m:
                if _APPROVED_ASINS is None:
                    _APPROVED_ASINS = _get_approved_asins()
                if asin_m.group(1) not in _APPROVED_ASINS:
                    search_q = urllib.parse.quote_plus(link_text.strip())
                    url = f"https://www.amazon.com/s?k={search_q}&tag=dailydealdarl-20"
            return f'<a href="{url}" target="_blank" rel="nofollow sponsored">{link_text}</a>'
        return f'<a href="{url}">{link_text}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _link_replace, text)
    # Bold **text**
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic *text*
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    return text


def article_to_html(markdown_content, brand_key, slug, pin_data=None):
    """Convert markdown article to a complete bridge-page HTML.

    Uses brand-specific templates from article_templates module:
    - fitness  → 'The Iron Standard'  (dark, gritty, data-heavy)
    - menopause → 'The Wellness Whisper' (clean, empathetic, editorial)
    - deals    → 'The Aesthetic Edit'  (minimalist, boutique, magazine)
    """
    from .article_templates import render_article_page

    site = BRAND_SITE_CONFIG[brand_key]
    title, meta_desc = _extract_frontmatter(markdown_content)
    if not title:
        title = slug.replace('-', ' ').title()
    if not meta_desc:
        meta_desc = f"{title} - {site['site_name']}"

    body_html = _markdown_to_html_body(markdown_content)

    # Inject product cards (with Amazon images) for bolded product links
    body_html = _inject_product_cards(body_html, brand_key)

    # Fetch hero image — try multiple sources
    hero_url = None
    pexels_query = (pin_data or {}).get('pexels_search_term', '') \
        or (pin_data or {}).get('image_search_query', '') \
        or slug.replace('-', ' ')
    hero_url = _fetch_pexels_image(pexels_query)
    # Fallback: use the pin's own Pexels image if article fetch failed
    if not hero_url and pin_data:
        hero_url = pin_data.get('image_url', '') or pin_data.get('pexels_image_url', '')
        if hero_url:
            logger.info(f"Using pin's existing image as hero: {hero_url[:80]}...")

    # Delegate full page rendering to brand-specific template
    return render_article_page(
        brand_key=brand_key,
        title=title,
        meta_desc=meta_desc,
        body_html=body_html,
        hero_url=hero_url,
        site_config=site,
        slug=slug,
        pin_data=pin_data,
    )


def save_and_register_article(html_content, brand_key, slug, pin_data, supabase_client):
    """Save article HTML to disk and register in Supabase.

    Returns the public article URL.
    """
    site = BRAND_SITE_CONFIG[brand_key]

    workspace = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.dirname(__file__)))
    full_dir = os.path.join(workspace, site['output_dir'])
    os.makedirs(full_dir, exist_ok=True)

    file_path = os.path.join(full_dir, f"{slug}.html")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"Article saved: {file_path}")

    # Register in Supabase
    try:
        supabase_client.table('generated_articles').insert({
            'brand': brand_key,
            'slug': slug,
            'trending_topic': pin_data.get('topic', '') or pin_data.get('trending_topic', ''),
            'content_preview': html_content[:500],
            'word_count': len(html_content.split()),
            'created_at': datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception as e:
        logger.error(f"Failed to log article to Supabase: {e}")

    article_url = f"{site['base_url']}/articles/{slug}.html"
    return article_url
