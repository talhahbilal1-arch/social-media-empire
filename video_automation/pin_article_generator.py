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
from datetime import datetime, timezone

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
# CRITICAL: Always use direct product links (/dp/ASIN?tag=...), never /s? search URLs

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
        "kettlebell": "https://www.amazon.com/dp/B003J9E5WO?tag=dailydealdarl-20",
        "massage gun": "https://www.amazon.com/dp/B07MHBJYRH?tag=dailydealdarl-20",
        "food scale": "https://www.amazon.com/dp/B004164SRA?tag=dailydealdarl-20",
        "glass meal prep containers": "https://www.amazon.com/dp/B078RFVKNR?tag=dailydealdarl-20",
        "protein shaker": "https://www.amazon.com/dp/B01LZ2GH5O?tag=dailydealdarl-20",
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
        "has_css": False,
        "lead_magnet": "FREE Weekly Deals Digest",
        "signup_form_id": "5641382",
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
        "signup_form_id": "5641382",
        "signup_button_text": "Get Free Guide",
    },
}


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

    prompt = f"""Write a focused, valuable blog article for the {config['name']} website.

BRAND VOICE:
{config['voice']}

ARTICLE TOPIC: {topic}
PIN TITLE: {pin_data.get('title', '')}
CATEGORY: {category}
{tips_section}
REQUIREMENTS:
1. LENGTH: 800-1200 words. Substantial enough to rank, no filler.
2. STRUCTURE:
   - H1 title (include primary keyword, click-worthy)
   - Meta description (155 chars max, includes keyword)
   - 3-5 H2 sections with standalone value — if tips were provided above, dedicate a section to each tip with deeper detail
   - Conversational, authoritative tone matching the brand voice
   - Clear conclusion with next steps
3. EMAIL CTA: After the 2nd section, include on its own line:
   [SIGNUP_FORM_PLACEHOLDER]
4. AMAZON PRODUCT RECOMMENDATIONS: Include 2-3 product recommendations naturally within the article.
   Link each product to its Amazon page using markdown links.
   CRITICAL: All Amazon links must be DIRECT PRODUCT LINKS in format: https://www.amazon.com/dp/[ASIN]?tag=dailydealdarl-20
   NEVER use Amazon search URLs (/s?k=...) — these are broken and don't convert to sales.
   Format: **[Product Name]**({amazon_url}) — honest 1-sentence review of why this product helps.
   Available products with Amazon links:
{products_text}
5. SEO KEYWORDS: Naturally include: {seo_keywords}
6. FILLER BAN: Never use "in today's fast-paced world", "it's important to note",
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
    # Links [text](url) — Amazon affiliate links get nofollow + new tab
    def _link_replace(match):
        link_text = match.group(1)
        url = match.group(2)
        if 'amazon.com' in url and 'tag=' in url:
            return f'<a href="{url}" target="_blank" rel="nofollow sponsored">{link_text}</a>'
        return f'<a href="{url}">{link_text}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _link_replace, text)
    # Bold **text**
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic *text*
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    return text


def article_to_html(markdown_content, brand_key, slug):
    """Convert markdown article to a complete HTML page."""
    site = BRAND_SITE_CONFIG[brand_key]
    title, meta_desc = _extract_frontmatter(markdown_content)
    if not title:
        title = slug.replace('-', ' ').title()
    if not meta_desc:
        meta_desc = f"{title} - {site['site_name']}"

    body_html = _markdown_to_html_body(markdown_content)

    # Replace email signup placeholder with actual form
    signup_html = (
        f'<div style="background:#f0f4f8;padding:24px;border-radius:12px;margin:32px 0;text-align:center;">'
        f'<h3 style="margin:0 0 8px">{site["lead_magnet"]}</h3>'
        f'<p style="margin:0 0 16px;color:#555">Join our community for weekly tips and guides.</p>'
        f'<script src="https://f.convertkit.com/ckjs/ck.5.js"></script>'
        f'<form action="https://app.convertkit.com/forms/{site["signup_form_id"]}/subscriptions" method="post" data-sv-form="{site["signup_form_id"]}">'
        f'<input type="email" name="email_address" placeholder="Enter your email" required style="padding:12px;border:1px solid #ddd;border-radius:6px;width:60%;margin-right:8px">'
        f'<button type="submit" style="padding:12px 24px;background:{site["primary_color"]};color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:bold">{site["signup_button_text"]}</button>'
        f'</form>'
        f'</div>'
    )
    body_html = body_html.replace('<!-- email-signup-placeholder -->', signup_html)

    # Menopause Planner: insert Etsy CTA before affiliate disclosure
    if brand_key == "menopause":
        etsy_cta = (
            '<div style="background:linear-gradient(135deg,#f3e8ff,#ede0f7);border:2px solid #c084fc;border-radius:14px;padding:28px;margin:36px 0;text-align:center;">'
            '<p style="font-size:0.8em;font-weight:700;letter-spacing:0.08em;color:#7B1FA2;text-transform:uppercase;margin:0 0 8px">The Menopause Planner — Digital Download</p>'
            '<h3 style="margin:0 0 10px;font-size:1.3em;color:#111">Track Every Symptom. Reclaim Your Sleep.</h3>'
            '<p style="margin:0 0 18px;color:#444;font-size:0.97em">A printable digital planner built specifically for women navigating menopause — track symptoms, sleep patterns, supplements, and mood in one place. Instant download, print at home.</p>'
            '<a href="https://www.etsy.com/listing/4435219468/menopause-wellness-planner-bundle?utm_source=Pinterest&amp;utm_medium=organic" target="_blank" rel="noopener" style="display:inline-block;background:#7B1FA2;color:#fff;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:700;font-size:1em">Get the Planner on Etsy →</a>'
            '<p style="margin:12px 0 0;font-size:0.82em;color:#777">Instant download • Print at home • One-time purchase</p>'
            '</div>'
        )
        body_html = body_html.replace('<p style="font-size:12px;', f'{etsy_cta}\n    <p style="font-size:12px;')

    # Build nav
    nav_html = '\n'.join(
        f'        <a href="{url}" style="color:#333;text-decoration:none;margin:0 12px">{label}</a>'
        for label, url in site['nav_links']
    )

    # Affiliate disclosure
    disclosure = (
        '<p style="font-size:12px;color:#888;margin-top:40px;padding-top:16px;'
        'border-top:1px solid #eee"><em>This article contains affiliate links. '
        'If you purchase through these links, we may earn a small commission at '
        'no extra cost to you. This helps us continue creating free content.</em></p>'
    )

    date_str = datetime.now(timezone.utc).strftime('%B %d, %Y')
    og_url = f"{site['base_url']}/articles/{slug}.html"

    if site.get('has_css'):
        # FitOver35 uses external stylesheet
        style_tag = '  <link rel="stylesheet" href="../css/styles.css">'
    else:
        # Inline minimal styles for other brands
        style_tag = f'''  <style>
    body {{ font-family: 'Inter', -apple-system, sans-serif; color: #333; line-height: 1.7; margin: 0; padding: 0; }}
    .header {{ background: #fff; border-bottom: 1px solid #eee; padding: 16px 0; }}
    .container {{ max-width: 800px; margin: 0 auto; padding: 0 20px; }}
    h1 {{ font-size: 2em; line-height: 1.2; margin: 32px 0 16px; color: #111; }}
    h2 {{ font-size: 1.4em; margin: 28px 0 12px; color: #222; }}
    p {{ margin: 0 0 16px; }}
    ul {{ margin: 0 0 16px; padding-left: 24px; }}
    li {{ margin-bottom: 8px; }}
    a {{ color: {site["primary_color"]}; }}
    strong {{ color: #111; }}
    .article-meta {{ color: #888; font-size: 14px; margin-bottom: 24px; }}
  </style>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{meta_desc}">
  <meta name="author" content="{site['site_name']}">
  <meta name="robots" content="index, follow">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{og_url}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{meta_desc[:160]}">
  <title>{title} - {site['site_name']}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
{style_tag}
</head>
<body>
  <header class="header">
    <div class="container" style="display:flex;align-items:center;justify-content:space-between">
      <a href="../index.html" style="font-size:1.4em;font-weight:700;text-decoration:none;color:#111">{site['logo_html']}</a>
      <nav>
{nav_html}
      </nav>
    </div>
  </header>

  <article class="container" style="padding-top:32px;padding-bottom:48px">
    <p class="article-meta" style="color:#888;font-size:14px">{date_str}</p>
{body_html}
    {disclosure}
  </article>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{title}",
    "datePublished": "{datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
    "author": {{
      "@type": "Organization",
      "name": "{site['site_name']}"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "{site['site_name']}"
    }},
    "description": "{meta_desc}"
  }}
  </script>
</body>
</html>'''

    return html


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
