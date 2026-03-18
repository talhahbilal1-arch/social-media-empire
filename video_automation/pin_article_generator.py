"""High-converting affiliate buying guide generator for per-pin articles.

Generates a Wirecutter-style buying guide (1200-1800 words) for each pin
during the content-engine run. One Gemini API call per article.
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
from google import genai

logger = logging.getLogger(__name__)

_client = None

GEMINI_MODEL = "gemini-2.0-flash"


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        _client = genai.Client(api_key=api_key)
    return _client


# ── Amazon Associates affiliate links ──────────────────────────────────────────
# Fitness uses tag=fitover35-20, deals and menopause use tag=dailydealdarling1-20.
# Direct /dp/ASIN links are preferred. For any product NOT in this list, the
# code falls back to Amazon search URLs (/s?k=...) which always work.

AMAZON_AFFILIATE_LINKS = {
    "fitness": {
        "creatine monohydrate": "https://www.amazon.com/dp/B002DYIZEO?tag=fitover35-20",
        "vitamin D3": "https://www.amazon.com/dp/B00GB85JR4?tag=fitover35-20",
        "magnesium glycinate": "https://www.amazon.com/dp/B000BD0RT0?tag=fitover35-20",
        "fish oil": "https://www.amazon.com/dp/B004O2I9JO?tag=fitover35-20",
        "ashwagandha": "https://www.amazon.com/dp/B078K18HYN?tag=fitover35-20",
        "protein powder": "https://www.amazon.com/dp/B000QSNYGI?tag=fitover35-20",
        "collagen peptides": "https://www.amazon.com/dp/B00K6JUG40?tag=fitover35-20",
        "resistance bands set": "https://www.amazon.com/dp/B01AVDVHTI?tag=fitover35-20",
        "adjustable dumbbells": "https://www.amazon.com/dp/B001ARYU58?tag=fitover35-20",
        "pull-up bar": "https://www.amazon.com/dp/B001EJMS6K?tag=fitover35-20",
        "foam roller": "https://www.amazon.com/dp/B0040EKZDY?tag=fitover35-20",
        "yoga mat": "https://www.amazon.com/dp/B01LYBOA9L?tag=fitover35-20",
        "stretching strap": "https://www.amazon.com/dp/B07YQ2BX91?tag=fitover35-20",
        "kettlebell": "https://www.amazon.com/dp/B003J9E5WO?tag=fitover35-20",
        "massage gun": "https://www.amazon.com/dp/B07MHBJYRH?tag=fitover35-20",
        "food scale": "https://www.amazon.com/dp/B004164SRA?tag=fitover35-20",
        "glass meal prep containers": "https://www.amazon.com/dp/B078RFVKNR?tag=fitover35-20",
        "protein shaker": "https://www.amazon.com/dp/B01LZ2GH5O?tag=fitover35-20",
        "workout gloves": "https://www.amazon.com/dp/B01MQGF4TQ?tag=fitover35-20",
        "_default": "https://www.amazon.com/dp/B001ARYU58?tag=fitover35-20",
    },
    "deals": {
        "air fryer": "https://www.amazon.com/dp/B07FDJMC9Q?tag=dailydealdarling1-20",
        "knife set": "https://www.amazon.com/dp/B07TLZXRK2?tag=dailydealdarling1-20",
        "meal prep containers": "https://www.amazon.com/dp/B078RFVKNR?tag=dailydealdarling1-20",
        "organizer bins": "https://www.amazon.com/dp/B07DFDS56B?tag=dailydealdarling1-20",
        "silk pillowcase": "https://www.amazon.com/dp/B07P3SQCV3?tag=dailydealdarling1-20",
        "LED face mask": "https://www.amazon.com/dp/B07D3KVL4Z?tag=dailydealdarling1-20",
        "label maker": "https://www.amazon.com/dp/B0719RFLTQ?tag=dailydealdarling1-20",
        "drawer dividers": "https://www.amazon.com/dp/B073VB74FJ?tag=dailydealdarling1-20",
        "throw pillows": "https://www.amazon.com/dp/B07DFDS56B?tag=dailydealdarling1-20",
        "LED candles": "https://www.amazon.com/dp/B07P3SQCV3?tag=dailydealdarling1-20",
        "_default": "https://www.amazon.com/dp/B07DFDS56B?tag=dailydealdarling1-20",
    },
    "menopause": {
        "black cohosh": "https://www.amazon.com/dp/B0019LTI86?tag=dailydealdarling1-20",
        "evening primrose oil": "https://www.amazon.com/dp/B00DWCZWHK?tag=dailydealdarling1-20",
        "magnesium glycinate": "https://www.amazon.com/dp/B000BD0RT0?tag=dailydealdarling1-20",
        "vitamin D3": "https://www.amazon.com/dp/B00GB85JR4?tag=dailydealdarling1-20",
        "cooling pillow": "https://www.amazon.com/dp/B07C7FQBDT?tag=dailydealdarling1-20",
        "bamboo sheets": "https://www.amazon.com/dp/B07QDFLQ7J?tag=dailydealdarling1-20",
        "cooling pajamas": "https://www.amazon.com/dp/B07YC684QN?tag=dailydealdarling1-20",
        "weighted blanket": "https://www.amazon.com/dp/B07H2DKQGJ?tag=dailydealdarling1-20",
        "symptom tracker journal": "https://www.amazon.com/dp/B0BW9GDRP7?tag=dailydealdarling1-20",
        "essential oils diffuser": "https://www.amazon.com/dp/B07L4R62GQ?tag=dailydealdarling1-20",
        "collagen powder": "https://www.amazon.com/dp/B00K6JUG40?tag=dailydealdarling1-20",
        "_default": "https://www.amazon.com/dp/B001G7QUXW?tag=dailydealdarling1-20",
    },
}

BRAND_AFFILIATE_TAGS = {
    "fitness": "fitover35-20",
    "deals": "dailydealdarling1-20",
    "menopause": "dailydealdarling1-20",
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


def _fetch_pexels_video(query, orientation='landscape'):
    """Fetch a short Pexels stock video URL for article hero."""
    api_key = os.environ.get('PEXELS_API_KEY', '')
    if not api_key:
        return None
    if not query:
        return None
    words = query.split()
    if len(words) > 6:
        query = ' '.join(words[:6])
    try:
        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": api_key},
            params={"query": query, "per_page": 5, "orientation": orientation, "size": "medium"},
            timeout=10,
        )
        if resp.status_code == 200:
            videos = resp.json().get('videos', [])
            if videos:
                for vf in videos[0].get('video_files', []):
                    if vf.get('quality') == 'hd' and vf.get('width', 0) <= 1920:
                        return vf['link']
                if videos[0].get('video_files'):
                    return videos[0]['video_files'][0]['link']
    except Exception as e:
        logger.warning(f"Pexels video fetch failed: {e}")
    return None


def _fetch_pexels_batch(query, count=5, orientation='landscape'):
    """Fetch multiple Pexels image URLs for a query. Returns list of URL strings."""
    api_key = os.environ.get('PEXELS_API_KEY', '')
    if not api_key or not query:
        return []
    words = query.split()
    if len(words) > 6:
        query = ' '.join(words[:6])
    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": query, "per_page": count, "orientation": orientation},
            timeout=10,
        )
        if resp.status_code == 200:
            return [p['src']['large'] for p in resp.json().get('photos', [])]
    except Exception as e:
        logger.warning(f"Pexels batch fetch failed for '{query}': {e}")
    return []


def _try_parse_json(content):
    """Try to parse content as JSON, stripping code fences if present."""
    if not content:
        return None
    text = content.strip()
    # Strip markdown code fences
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
    text = text.strip()
    if not text.startswith('{'):
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        logger.warning("JSON parse failed, falling back to markdown path")
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
        f'Check Price on Amazon \u2192</a>'
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
    """Generate a high-converting affiliate buying guide matching a pin's topic.

    Returns (slug, content) where content is either JSON (v3) or markdown (v2 fallback).
    Or (None, None) if skipped.
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
    year = datetime.now(timezone.utc).year
    affiliate_tag = BRAND_AFFILIATE_TAGS.get(brand_key, 'dailydealdarling1-20')

    # Brand-specific trust section
    trust_text = {
        'fitness': 'Written by Talhah Bilal, ISSA-certified personal trainer with 6+ years experience training men over 35.',
        'menopause': "Reviewed by our editorial team in consultation with women's health practitioners.",
        'deals': 'Our team tests and compares dozens of products monthly.',
    }.get(brand_key, 'Our team tests and compares dozens of products monthly.')

    # Brand-specific writing style notes
    if brand_key == 'fitness':
        style_notes = (
            'Include a "Pro-Coach Insight" blockquote (use > **Pro-Coach Insight:**) '
            'with specific timing, dosage, or technique advice. '
            'Write with high confidence and data-backed authority. '
            'Cite specific numbers or studies where possible.'
        )
    elif brand_key == 'menopause':
        style_notes = (
            'Include a "Symptom Checklist" section with specific symptoms this addresses '
            '(night sweats, fatigue, brain fog, mood changes). '
            'Write with warmth and empathy — acknowledge the struggle, then provide solutions.'
        )
    else:
        style_notes = (
            'Include a "Why It\'s Trending" or "Social Proof" mention (star ratings, '
            'review counts, Pinterest saves). '
            'Write in a curated, editorial tone — like a boutique magazine recommending the best.'
        )

    # Etsy CTA for menopause brand only
    etsy_section = ''
    if brand_key == 'menopause':
        etsy_section = (
            '\n\nETSY PLANNER CTA: In the conclusion, naturally mention and link to the '
            'Menopause Wellness Planner Bundle on Etsy as a practical next step.\n'
            'Use this exact link: https://www.etsy.com/listing/4435219468/'
            'menopause-wellness-planner-bundle?utm_source=Pinterest&utm_medium=organic\n'
            'Format: [Menopause Wellness Planner Bundle](link) — one sentence, benefit-driven.'
        )

    # ── Try JSON generation first ──────────────────────────────────────────
    available_keys = [k for k in brand_amazon.keys() if k != '_default']
    available_keys_str = ', '.join(available_keys) if available_keys else 'none available'

    json_prompt = f"""You are a high-converting buying guide expert. Generate ONLY valid JSON (no markdown, no backticks).

AVAILABLE PRODUCT KEYS: {available_keys_str}

BRAND VOICE:
{config['voice']}

ARTICLE TOPIC: {topic}
PIN TITLE: {pin_data.get('title', '')}
CATEGORY: {category}
{tips_section}

AFFILIATE TAG: {affiliate_tag}

Output EXACTLY this JSON structure (no markdown, no code fences, ONLY valid JSON):
{{
  "title": "Best [Product] for [Audience] ({year})",
  "meta_description": "155 chars max, SEO-optimized",
  "read_time": "4 min",
  "brands_tested": 8,
  "reviews_analyzed": "14,000+",
  "verdict": "Bold one-sentence finding after testing.",
  "before": {{"emoji": "😰", "title": "Before", "text": "The problem"}},
  "after": {{"emoji": "😴", "title": "After", "text": "The solution"}},
  "urgency_text": "Currently 15% off with Subscribe & Save on Amazon",
  "products": [
    {{
      "name": "Product Name",
      "badge": "Our Pick",
      "badge_type": "top",
      "price_low": 28,
      "price_high": 38,
      "rating": 4.6,
      "review_count": "12,400+",
      "subscribe_save": "15% off",
      "pexels_image_query": "vivid specific query for Pexels",
      "pexels_thumb_queries": ["query1", "query2", "query3"],
      "benefit_icons": [{{"emoji": "💧", "text": "Benefit"}}],
      "benefit_image_query": "detail image query",
      "benefit_headline": "Why X beats Y",
      "benefit_description": "Explanation.",
      "pros": ["Pro 1", "Pro 2", "Pro 3", "Pro 4"],
      "cons": ["Con 1", "Con 2"],
      "testimonials": [
        {{"name": "Sarah M.", "quote": "Authentic Amazon-style review."}},
        {{"name": "Linda R.", "quote": "Another real customer voice."}}
      ],
      "amazon_product_key": "key from AVAILABLE PRODUCT KEYS"
    }}
  ],
  "comparison_extra_rows": [{{"label": "Subscribe & Save", "values": ["✓ 15%", "✓ 10%", "✗"]}}],
  "methodology": ["Point 1", "Point 2", "Point 3", "Point 4"],
  "faq": [{{"q": "Question?", "a": "Answer."}}],
  "related_product_keys": ["key1", "key2", "key3"]
}}

RULES:
- 2-3 products only, use ONLY keys from AVAILABLE PRODUCT KEYS
- Ratings: 4.3-4.8 range (never 5.0)
- Review counts: realistic 1000-50000 range
- Testimonials: sound like real Amazon reviews from different customers
- BANNED: "In today's world", "it's important to note", "when it comes to", "let's dive in", "game-changer", "without further ado", "unlock your potential"
- Output ONLY JSON, no markdown, no backticks, no code fences"""

    try:
        response = _get_client().models.generate_content(
            model=GEMINI_MODEL,
            contents=json_prompt,
            config={"response_mime_type": "application/json", "max_output_tokens": 4000},
        )
        article_json = response.text.strip()
        parsed = _try_parse_json(article_json)
        if parsed and isinstance(parsed, dict):
            logger.info(f"JSON article generated successfully for '{topic}'")
            return slug, article_json
        else:
            logger.warning(f"JSON parsing failed, falling back to markdown for '{topic}'")
    except Exception as e:
        logger.warning(f"JSON generation failed: {e}, falling back to markdown")

    # ── Fallback to markdown generation ──────────────────────────────────
    markdown_prompt = f"""Write a high-converting affiliate buying guide for the {config['name']} website.
This is NOT a generic blog post. It answers: "Which one should I buy?"

BRAND VOICE:
{config['voice']}

ARTICLE TOPIC: {topic}
PIN TITLE: {pin_data.get('title', '')}
CATEGORY: {category}
{tips_section}
BRAND STYLE: {style_notes}

REQUIRED STRUCTURE (follow EXACTLY):

1. HERO + QUICK VERDICT (first 200 words, above the fold)
   - H1 title with buyer-intent keyword: "Best [Product] for [Audience] ({year})"
   - One-sentence expert verdict: "After researching X options, [Top Pick] is the best for most [audience] because [specific reason]."
   - QUICK PICKS BOX with 2-3 products:
     * Our Pick: [Product Name] — [one-line why]
     * Also Great: [Product Name] — [one-line why]
     * Budget Pick: [Product Name] — [one-line why]
   - Each pick must include its Amazon link from the APPROVED PRODUCTS list

2. WHY TRUST THIS GUIDE (50-100 words)
   {trust_text}

3. On its own line exactly: [SIGNUP_FORM_PLACEHOLDER]

4. DETAILED REVIEW FOR EACH PRODUCT (200-300 words each, 2-4 products)
   For EACH product include ALL of the following:
   - H2: "[Product Name] — Best for [specific use case]"
   - A product card comment on its OWN LINE (the template renders this as a visual card):
     <!--PRODUCT_CARD: name="Product Name" | url="amazon_url" | rating="4.7" | reviews="12400" | price_range="$30-50" | badge="Our Pick" -->
   - WHO IT'S FOR: Best for [specific audience/scenario]
   - WHAT WE LIKE: 3 specific, testable pros (NOT generic praise)
   - WHAT WE DON'T: 1-2 honest cons (builds trust, increases conversion)
   - BOTTOM LINE: One sentence summary with embedded Amazon link

5. COMPARISON TABLE (use markdown table format):
   | Feature | Product 1 | Product 2 | Product 3 |
   |---------|-----------|-----------|-----------|
   | Price Range | ... | ... | ... |
   | Best For | ... | ... | ... |
   | Our Rating | ... | ... | ... |

6. HOW WE CHOSE (100-150 words)
   What criteria matter and why we chose these products.

7. FAQ SECTION (3-5 questions)
   Format each EXACTLY as:
   **Q: [Question with long-tail keyword]?**
   A: [Concise 2-3 sentence answer]

8. FINAL VERDICT + CTA (100 words)
   Restate the top pick with its Amazon link.
   End with specific CTA: "Check today's price on Amazon" — NOT "pick what works for you"

CRITICAL RULES:
- ALL Amazon links must use DIRECT /dp/ASIN URLs from the approved list below. NEVER invent /dp/ URLs.
- If a product is NOT in the approved list, DO NOT LINK IT. Only recommend products we have links for.
- ALL Amazon links must include tag={affiliate_tag}
- For non-product articles (e.g. "benefits of creatine"), STILL end with 1-2 specific product recommendations with PRODUCT_CARD data.
- EVERY product mention must include the <!--PRODUCT_CARD: ...--> comment on its own line.
- Star ratings: realistic range 4.3-4.8 (never 5.0)
- Review counts: realistic range 1,000-50,000
- Price ranges: approximate but realistic
- badge values: "Our Pick", "Also Great", "Budget Pick", or "Best Value"

APPROVED PRODUCTS WITH AMAZON LINKS (use these EXACT URLs):
{products_text}

SEO KEYWORDS: Naturally include: {seo_keywords}

BANNED PHRASES: "In today's world", "it's important to note", "when it comes to",
"let's dive in", "without further ado", "at the end of the day", "it goes without saying"
{etsy_section}
OUTPUT FORMAT — Markdown with frontmatter:
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
        response = _get_client().models.generate_content(
            model=GEMINI_MODEL,
            contents=markdown_prompt,
            config={"max_output_tokens": 4000},
        )
        article_md = response.text.strip()
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


def _markdown_to_html_body(markdown_content, brand_key='deals'):
    """Convert markdown article body to HTML.

    Handles: headings, bold, italic, paragraphs, lists, links, tables,
    PRODUCT_CARD comments, and the SIGNUP_FORM_PLACEHOLDER.
    """
    # Strip frontmatter
    body = re.sub(r'^---\s*\n.*?\n---\s*\n?', '', markdown_content, flags=re.DOTALL)
    body = body.strip()

    lines = body.split('\n')
    html_lines = []
    in_list = False
    in_table = False
    first_table_row = True
    table_body_started = False

    for line in lines:
        stripped = line.strip()

        # Empty line
        if not stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if in_table:
                if table_body_started:
                    html_lines.append('</tbody>')
                html_lines.append('</table></div>')
                in_table = False
            continue

        # Product card comment — pass through without wrapping in <p>
        if stripped.startswith('<!--PRODUCT_CARD:'):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(stripped)
            continue

        # Signup form placeholder
        if '[SIGNUP_FORM_PLACEHOLDER]' in stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(stripped.replace('[SIGNUP_FORM_PLACEHOLDER]', '<!-- email-signup-placeholder -->'))
            continue

        # Table rows
        if stripped.startswith('|') and '|' in stripped[1:]:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if not in_table:
                html_lines.append('<div style="overflow-x:auto"><table>')
                in_table = True
                first_table_row = True
                table_body_started = False
            # Skip separator rows like | --- | --- |
            if re.match(r'^\|[\s\-:|]+\|$', stripped):
                continue
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            cells = [c for c in cells if c]
            if first_table_row:
                html_lines.append(
                    '<thead><tr>'
                    + ''.join(f'<th>{_inline_format(c, brand_key)}</th>' for c in cells)
                    + '</tr></thead>'
                )
                first_table_row = False
            else:
                if not table_body_started:
                    html_lines.append('<tbody>')
                    table_body_started = True
                html_lines.append(
                    '<tr>'
                    + ''.join(f'<td>{_inline_format(c, brand_key)}</td>' for c in cells)
                    + '</tr>'
                )
            continue

        # Close table if we hit a non-table line
        if in_table:
            if table_body_started:
                html_lines.append('</tbody>')
            html_lines.append('</table></div>')
            in_table = False

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if heading_match:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            level = len(heading_match.group(1))
            text = _inline_format(heading_match.group(2), brand_key)
            html_lines.append(f'<h{level}>{text}</h{level}>')
            continue

        # Blockquotes
        if stripped.startswith('> '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            text = _inline_format(stripped[2:], brand_key)
            html_lines.append(f'<blockquote>{text}</blockquote>')
            continue

        # List items
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            text = _inline_format(stripped[2:], brand_key)
            html_lines.append(f'  <li>{text}</li>')
            continue

        # Regular paragraph
        if in_list:
            html_lines.append('</ul>')
            in_list = False
        text = _inline_format(stripped, brand_key)
        html_lines.append(f'<p>{text}</p>')

    if in_list:
        html_lines.append('</ul>')
    if in_table:
        if table_body_started:
            html_lines.append('</tbody>')
        html_lines.append('</table></div>')

    return '\n'.join(html_lines)


def _inline_format(text, brand_key='deals'):
    """Apply inline markdown formatting (bold, italic, links)."""
    global _APPROVED_ASINS

    affiliate_tag = BRAND_AFFILIATE_TAGS.get(brand_key, 'dailydealdarling1-20')

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
                    url = f"https://www.amazon.com/s?k={search_q}&tag={affiliate_tag}"
            return f'<a href="{url}" target="_blank" rel="nofollow sponsored">{link_text}</a>'
        return f'<a href="{url}">{link_text}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _link_replace, text)
    # Bold **text**
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic *text*
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    return text


def _build_v3_article(article_data, brand_key, slug, pin_data=None):
    """Build v3 article from structured JSON data.

    Fetches images from Pexels and returns complete HTML.
    """
    from .article_templates import render_article_page

    site = BRAND_SITE_CONFIG[brand_key]

    # Resolve amazon_product_key → actual Amazon URLs
    brand_amazon = AMAZON_AFFILIATE_LINKS.get(brand_key, {})

    # Fetch hero image + optional video
    hero_query = article_data.get('title', slug)
    hero_url = _fetch_pexels_image(hero_query)
    video_url = _fetch_pexels_video(hero_query)

    # Enrich products with images
    for product in article_data.get('products', []):
        product_key = product.get('amazon_product_key', '')
        if product_key and product_key in brand_amazon:
            product['amazon_url'] = brand_amazon[product_key]
        else:
            product['amazon_url'] = brand_amazon.get('_default', '')

        # Fetch hero image for this product
        hero_img_query = product.get('pexels_image_query', product.get('name', ''))
        hero_img = _fetch_pexels_image(hero_img_query) if hero_img_query else None
        product['hero_image'] = hero_img

        # Fetch thumbnail images
        thumb_queries = product.get('pexels_thumb_queries', [])
        thumb_images = []
        for tq in thumb_queries[:3]:
            ti = _fetch_pexels_image(tq) if tq else None
            if ti:
                thumb_images.append(ti)
        product['thumb_images'] = thumb_images

        # Fetch benefit image
        benefit_img_query = product.get('benefit_image_query', '')
        benefit_img = _fetch_pexels_image(benefit_img_query) if benefit_img_query else None
        product['benefit_image'] = benefit_img

        # Add placeholder photos to testimonials
        testimonials = product.get('testimonials', [])
        for testimonial in testimonials:
            if 'photo' not in testimonial:
                testimonial['photo'] = None

    # Fetch portrait photos for testimonials (brand-specific queries)
    if brand_key == 'fitness':
        portrait_query = 'man portrait confident professional'
    elif brand_key == 'menopause':
        portrait_query = 'middle aged woman portrait warm confident'
    else:
        portrait_query = 'woman portrait friendly lifestyle'

    portrait_batch = _fetch_pexels_batch(portrait_query, count=5)
    portrait_idx = 0
    for product in article_data.get('products', []):
        for testimonial in product.get('testimonials', []):
            if portrait_idx < len(portrait_batch):
                testimonial['photo'] = portrait_batch[portrait_idx]
                portrait_idx += 1

    # Fetch related product images
    related_products = []
    for key in article_data.get('related_product_keys', [])[:3]:
        if key in brand_amazon:
            img = _fetch_pexels_image(key)
            related_products.append({
                'name': key,
                'amazon_url': brand_amazon[key],
                'image': img,
            })

    # Build enriched article data
    enriched_data = dict(article_data)
    enriched_data['hero_url'] = hero_url
    enriched_data['video_url'] = video_url
    enriched_data['category'] = pin_data.get('category', '') if pin_data else ''
    enriched_data['related_products'] = related_products

    # Store in pin_data for template
    if pin_data is None:
        pin_data = {}
    pin_data['_article_data'] = enriched_data

    # Delegate to template
    return render_article_page(
        brand_key=brand_key,
        title=enriched_data.get('title', ''),
        meta_desc=enriched_data.get('meta_description', ''),
        body_html='',  # v3 template handles rendering
        hero_url=hero_url,
        site_config=site,
        slug=slug,
        pin_data=pin_data,
    )


def _build_v2_article(markdown_content, brand_key, slug, pin_data=None):
    """Build v2 article from markdown (fallback path)."""
    from .article_templates import render_article_page

    site = BRAND_SITE_CONFIG[brand_key]
    title, meta_desc = _extract_frontmatter(markdown_content)
    if not title:
        title = slug.replace('-', ' ').title()
    if not meta_desc:
        meta_desc = f"{title} - {site['site_name']}"

    body_html = _markdown_to_html_body(markdown_content, brand_key)

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


def article_to_html(markdown_content, brand_key, slug, pin_data=None):
    """Convert article content to complete bridge-page HTML.

    Handles two paths:
    - JSON (v3): Structured data → fetch images → v3 template with enhanced sections
    - Markdown (v2 fallback): Existing path with product cards + FAQ schema
    """
    article_data = _try_parse_json(markdown_content)

    if article_data and isinstance(article_data, dict):
        return _build_v3_article(article_data, brand_key, slug, pin_data)
    else:
        return _build_v2_article(markdown_content, brand_key, slug, pin_data)


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
