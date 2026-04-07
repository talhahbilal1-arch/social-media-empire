"""Template-based article renderer.

Reads standalone HTML template files and fills in variables.
Design changes = edit the HTML file (preview in browser).
Data changes = edit the JSON prompt.
Rendering = simple variable replacement (can't break).
"""

import html
import json
import os
import re
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ── Brand configurations (colors, fonts, experts) ─────────────────────────

BRAND_THEMES = {
    'fitness': {
        'heading_font': 'Instrument Serif',
        'body_font': 'DM Sans',
        'font_import': 'Instrument+Serif:ital@0;1&family=DM+Sans:wght@400;500;600;700',
        'colors': {
            'bg': '#111014', 'surface': '#1a181e', 'border': '#2e2c33',
            'accent': '#d4a843', 'accent_light': '#2a2520', 'text': '#e8e6ed',
            'muted': '#8a8894', 'warm': '#1e1c22',
        },
        'expert_name': 'Talhah Bilal',
        'expert_initials': 'TB',
        'expert_credentials': 'ISSA-CPT · Kinesiology Degree',
        'expert_bio': 'Reviewed by Talhah Bilal, a Kinesiology degree holder, ISSA-certified personal trainer, and competitive bodybuilder with over a decade of experience.',
        'site_tagline': 'Expert Verified',
        'cta_text': 'Check Current Price on Amazon',
    },
    'menopause': {
        'heading_font': 'Fraunces',
        'body_font': 'DM Sans',
        'font_import': 'Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=DM+Sans:wght@400;500;600;700',
        'colors': {
            'bg': '#FDFBF7', 'surface': '#FFFFFF', 'border': '#E8D5A3',
            'accent': '#3D6B4F', 'accent_light': '#EAF2EC', 'text': '#3A3A3A',
            'muted': '#8B7355', 'warm': '#F5EDE0',
        },
        'expert_name': 'The Menopause Planner Team',
        'expert_initials': 'MP',
        'expert_credentials': 'Wellness Guide · Research-Backed Reviews',
        'expert_bio': 'Reviewed in consultation with certified women\'s health practitioners and menopause specialists. Every recommendation is based on verified reviews and published research.',
        'site_tagline': 'Wellness Guide · Expert Reviewed',
        'cta_text': 'View Today\'s Amazon Deal',
    },
    'deals': {
        'heading_font': 'Fraunces',
        'body_font': 'DM Sans',
        'font_import': 'Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=DM+Sans:wght@400;500;600;700',
        'colors': {
            'bg': '#FAF9F6', 'surface': '#FFFFFF', 'border': '#E5E5E5',
            'accent': '#D4AF37', 'accent_light': '#FBF5E6', 'text': '#1A1A1A',
            'muted': '#6B6B6B', 'warm': '#F5F0E8',
        },
        'expert_name': 'Daily Deal Darling Team',
        'expert_initials': 'DD',
        'expert_credentials': 'Trending on Pinterest · Product Tested',
        'expert_bio': 'Our team tests and compares dozens of products monthly so you don\'t have to. We only recommend what we\'d buy ourselves.',
        'site_tagline': 'Trending · Product Tested',
        'cta_text': 'Check Today\'s Price on Amazon',
    },
}

# ── Fallback face images (always available, royalty-free) ──────────────────

FALLBACK_FACES = {
    'fitness': [
        'https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg?auto=compress&cs=tinysrgb&w=80',
        'https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?auto=compress&cs=tinysrgb&w=80',
        'https://images.pexels.com/photos/1681010/pexels-photo-1681010.jpeg?auto=compress&cs=tinysrgb&w=80',
        'https://images.pexels.com/photos/1300402/pexels-photo-1300402.jpeg?auto=compress&cs=tinysrgb&w=80',
    ],
    'menopause': [
        'https://images.pexels.com/photos/3807517/pexels-photo-3807517.jpeg?auto=compress&cs=tinysrgb&w=80',
        'https://images.pexels.com/photos/3807770/pexels-photo-3807770.jpeg?auto=compress&cs=tinysrgb&w=80',
        'https://images.pexels.com/photos/3807537/pexels-photo-3807537.jpeg?auto=compress&cs=tinysrgb&w=80',
        'https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=80',
    ],
    'deals': [
        'https://images.pexels.com/photos/3807517/pexels-photo-3807517.jpeg?auto=compress&cs=tinysrgb&w=80',
        'https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=80',
        'https://images.pexels.com/photos/3807770/pexels-photo-3807770.jpeg?auto=compress&cs=tinysrgb&w=80',
        'https://images.pexels.com/photos/3807537/pexels-photo-3807537.jpeg?auto=compress&cs=tinysrgb&w=80',
    ],
}

# ── Fallback hero images by category (always available) ────────────────────

FALLBACK_HERO_IMAGES = {
    'fitness': 'https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=900',
    'menopause': 'https://images.pexels.com/photos/6585764/pexels-photo-6585764.jpeg?auto=compress&cs=tinysrgb&w=900',
    'deals': 'https://images.pexels.com/photos/5632399/pexels-photo-5632399.jpeg?auto=compress&cs=tinysrgb&w=900',
    'default': 'https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=900',
}

FALLBACK_PRODUCT_IMAGES = {
    'fitness': 'https://images.pexels.com/photos/4164761/pexels-photo-4164761.jpeg?auto=compress&cs=tinysrgb&w=700',
    'menopause': 'https://images.pexels.com/photos/6311652/pexels-photo-6311652.jpeg?auto=compress&cs=tinysrgb&w=700',
    'deals': 'https://images.pexels.com/photos/5632381/pexels-photo-5632381.jpeg?auto=compress&cs=tinysrgb&w=700',
    'default': 'https://images.pexels.com/photos/5632399/pexels-photo-5632399.jpeg?auto=compress&cs=tinysrgb&w=700',
}


def _esc(text):
    """HTML-escape a string."""
    return html.escape(str(text)) if text else ''


def _ensure_image(url, fallback):
    """Return url if truthy, otherwise fallback. NEVER returns empty string."""
    if url and isinstance(url, str) and url.startswith('http'):
        return url
    return fallback


def _get_template_path():
    """Get the path to the base template file."""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_dir, 'article_page_templates', 'base_template.html')


def _build_quick_picks_html(products, theme):
    """Build the quick picks summary section."""
    picks = []
    badge_classes = ['top', 'great', 'budget']
    for i, p in enumerate(products[:3]):
        badge_class = badge_classes[i] if i < len(badge_classes) else 'budget'
        badge_text = p.get('badge', ['Our Pick', 'Also Great', 'Budget'][min(i, 2)])
        rating = p.get('rating', 4.5)
        review_count = p.get('review_count', '1,000+')
        price_low = p.get('price_low', 0)
        price_high = p.get('price_high', 0)
        price_str = f'${price_low}\u2013{price_high}' if price_low and price_high else ''
        picks.append(
            f'<div class="pick">'
            f'<span class="pick-badge {badge_class}">{_esc(badge_text)}</span>'
            f'<div class="pick-info">'
            f'<div class="pick-name">{_esc(p.get("name", ""))}</div>'
            f'<div class="pick-meta">\u2605 {rating} \u00b7 {_esc(review_count)} reviews</div>'
            f'</div>'
            f'<div class="pick-price">{price_str}</div>'
            f'</div>'
        )
    return f'<div class="picks">{"".join(picks)}</div>'


def _build_product_block_html(product, index, brand_key, theme):
    """Build a single product card."""
    badge_classes = ['top-pick', 'also-great', 'budget-pick']
    badge_emojis = ['\U0001f3c6', '\u26a1', '\U0001f4b0']
    badge_class = badge_classes[min(index, 2)]
    badge_emoji = badge_emojis[min(index, 2)]
    badge_text = product.get('badge', ['Our Pick', 'Also Great', 'Budget Pick'][min(index, 2)])

    name = _esc(product.get('name', 'Product'))
    rating = product.get('rating', 4.5)
    review_count = _esc(product.get('review_count', '1,000+'))
    price_low = product.get('price_low', 0)
    price_high = product.get('price_high', 0)
    price_str = f'${price_low} \u2013 ${price_high}' if price_low and price_high else ''
    subscribe_save = product.get('subscribe_save', '')
    if subscribe_save:
        price_str += f' \u00b7 Subscribe & Save {_esc(subscribe_save)}'

    amazon_url = _esc(product.get('amazon_url', '#'))
    image_url = _ensure_image(
        product.get('hero_image', ''),
        FALLBACK_PRODUCT_IMAGES.get(brand_key, FALLBACK_PRODUCT_IMAGES['default'])
    )
    who_for = _esc(product.get('who_for', ''))

    # Pros
    pros_html = ''
    for pro in product.get('pros', []):
        pros_html += f'<li>{_esc(pro)}</li>'

    # Cons
    cons_html = ''
    for con in product.get('cons', []):
        cons_html += f'<li>{_esc(con)}</li>'

    bottom_line = _esc(product.get('bottom_line', ''))

    # Amazon rating badge (replaces fake testimonials for FTC compliance)
    rating_badge_html = (
        f'<div class="amazon-rating-badge" style="display:flex;align-items:center;gap:8px;'
        f'padding:10px 14px;background:var(--warm);border-radius:8px;margin:12px 0">'
        f'<span style="color:#FF9900;font-weight:700">\u2605 {rating}</span>'
        f'<span style="font-size:.82rem;color:var(--muted)">Based on Amazon reviews</span>'
        f'</div>'
    )

    # Star display
    full_stars = int(rating)
    stars_html = '<span class="star">' + '\u2605' * full_stars + '</span>' + '\u2606' * (5 - full_stars)

    # Payment icons (only on first product)
    payments_html = ''
    if index == 0:
        payments_html = (
            '<div class="payments">'
            '<span class="pay">Visa</span>'
            '<span class="pay">Mastercard</span>'
            '<span class="pay">PayPal</span>'
            '<span class="pay">Amazon Pay</span>'
            '<span class="pay">Apple Pay</span>'
            '</div>'
        )

    return (
        f'<div class="product">'
        f'<div class="product-header">'
        f'<span class="product-badge {badge_class}">{badge_emoji} {_esc(badge_text)}</span>'
        f'<span class="product-stars">{stars_html} {rating} ({review_count} reviews)</span>'
        f'</div>'
        f'<h2>{name}</h2>'
        f'<p class="product-price">{price_str}</p>'
        f'<img class="product-img" src="{image_url}" alt="{name}" loading="lazy">'
        f'<div class="who-for"><strong>Best for:</strong> {who_for}</div>'
        f'<div class="pc">'
        f'<div class="pc-col pros"><h4>What We Like</h4><ul>{pros_html}</ul></div>'
        f'<div class="pc-col cons"><h4>Watch Out For</h4><ul>{cons_html}</ul></div>'
        f'</div>'
        f'<div class="bottom-line"><strong>Bottom line:</strong> {bottom_line}</div>'
        f'{rating_badge_html}'
        f'<a class="cta" href="{amazon_url}" target="_blank" rel="nofollow sponsored">'
        f'Check Today\'s Price on Amazon \u2192'
        f'<small>Free returns \u00b7 30-day guarantee \u00b7 Subscribe & Save available</small></a>'
        f'{payments_html}'
        f'</div>'
    )


def _build_comparison_table_html(products):
    """Build the comparison table."""
    if len(products) < 2:
        return ''
    headers = ['']
    for i, p in enumerate(products[:3]):
        emoji = ['\U0001f3c6', '\u26a1', '\U0001f4b0'][min(i, 2)]
        headers.append(f'{_esc(p.get("name", "")[:20])} {emoji}')

    rows = []
    fields = [
        ('Price', lambda p: f'${p.get("price_low", "?")}\u2013{p.get("price_high", "?")}'),
        ('Best for', lambda p: _esc(p.get('who_for', '')[:30])),
        ('Rating', lambda p: f'\u2605 {p.get("rating", "?")}'),
        ('Reviews', lambda p: _esc(p.get('review_count', '?'))),
        ('Buy first?', lambda p: ''),  # set below
    ]
    for label, getter in fields:
        row = f'<tr><td><strong>{label}</strong></td>'
        for i, p in enumerate(products[:3]):
            val = getter(p)
            if label == 'Buy first?':
                val = '<strong>YES</strong>' if i == 0 else ('Add 2nd' if i == 1 else 'Optional')
            css = ' class="winner"' if i == 0 else ''
            row += f'<td{css}>{val}</td>'
        row += '</tr>'
        rows.append(row)

    header_html = ''.join(f'<th>{h}</th>' for h in headers)
    return (
        f'<div class="comp"><table>'
        f'<tr>{header_html}</tr>'
        f'{"".join(rows)}'
        f'</table></div>'
    )


def _build_methodology_html(steps):
    """Build the How We Chose section grid."""
    items = []
    for i, step in enumerate(steps[:4], 1):
        items.append(
            f'<div class="method-item">'
            f'<div class="method-num">{i}</div>'
            f'<div class="method-text">{step}</div>'
            f'</div>'
        )
    return ''.join(items)


def _build_etsy_html(brand_key):
    """Return Etsy CTA HTML for menopause brand, empty string otherwise."""
    if brand_key != 'menopause':
        return ''
    return (
        '<div class="etsy">'
        '<div class="etsy-label">Digital Download \u2014 The Menopause Planner</div>'
        '<h3>Track What\'s Actually Helping</h3>'
        '<p>Log night sweats, sleep quality, and what you changed \u2014 see patterns your doctor can use.</p>'
        '<a href="https://www.etsy.com/listing/4435219468/menopause-wellness-planner-bundle?utm_source=Pinterest&utm_medium=organic" target="_blank" rel="noopener">Get the Planner on Etsy \u2192</a>'
        '</div>'
    )


def _build_faq_html(faq_items):
    """Build FAQ items HTML."""
    items = []
    for faq in faq_items:
        items.append(
            f'<div class="faq-item">'
            f'<div class="faq-q">{_esc(faq.get("q", ""))}</div>'
            f'<div class="faq-a">{_esc(faq.get("a", ""))}</div>'
            f'</div>'
        )
    return ''.join(items)


def _build_schemas(title, meta_desc, slug, site_config, expert_name, products, faq_items):
    """Build all Schema.org JSON-LD tags."""
    article_url = site_config['base_url'] + '/articles/' + slug + '.html'
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    article_schema = json.dumps({
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': title,
        'description': meta_desc,
        'datePublished': now_str,
        'dateModified': now_str,
        'author': {'@type': 'Organization', 'name': site_config.get('site_name', '')},
        'publisher': {
            '@type': 'Organization',
            'name': site_config.get('site_name', ''),
            'url': site_config.get('base_url', ''),
        },
        'mainEntityOfPage': {'@type': 'WebPage', '@id': article_url},
    })

    faq_schema = ''
    if faq_items:
        faq_entities = []
        for faq in faq_items:
            faq_entities.append({
                '@type': 'Question',
                'name': faq.get('q', ''),
                'acceptedAnswer': {'@type': 'Answer', 'text': faq.get('a', '')},
            })
        faq_schema = f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_entities})}</script>'

    product_schema = ''
    if products:
        p = products[0]
        product_schema = f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "Product", "name": p.get("name", title), "url": p.get("amazon_url", "")})}</script>'

    return (
        f'<script type="application/ld+json">{article_schema}</script>',
        faq_schema,
        product_schema,
    )


def render_article_from_template(brand_key, article_data, site_config, slug):
    """Render a complete article page from the HTML template file.

    This is the ONLY function you need to call. It reads the template,
    fills in all variables, and returns complete HTML.

    Args:
        brand_key: 'fitness', 'menopause', or 'deals'
        article_data: Dict with title, products, faq, etc. (from Claude API)
        site_config: Dict with base_url, site_name, output_dir
        slug: URL-safe article name

    Returns:
        Complete HTML string ready to save to disk.
    """
    theme = BRAND_THEMES.get(brand_key, BRAND_THEMES['deals'])
    c = theme['colors']

    # Read the template file
    template_path = _get_template_path()
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_html = f.read()
    except FileNotFoundError:
        logger.error(f'Template file not found: {template_path}')
        raise

    # Extract data with safe defaults
    title = article_data.get('title', slug.replace('-', ' ').title())
    meta_desc = article_data.get('meta_description', title)
    products = article_data.get('products', [])
    faq_items = article_data.get('faq', [])
    year = datetime.now(timezone.utc).year
    date_display = datetime.now(timezone.utc).strftime('%B %Y')

    # Ensure hero image always exists
    hero_image = _ensure_image(
        article_data.get('hero_url', ''),
        FALLBACK_HERO_IMAGES.get(brand_key, FALLBACK_HERO_IMAGES['default'])
    )

    # Build dynamic sections
    quick_picks = _build_quick_picks_html(products, theme)

    product_blocks = []
    for i, product in enumerate(products[:3]):
        product_blocks.append(_build_product_block_html(product, i, brand_key, theme))
    product_blocks_html = '\n'.join(product_blocks)

    comparison_html = _build_comparison_table_html(products)
    methodology = article_data.get('methodology', [
        f'Analyzed <strong>{article_data.get("reviews_analyzed", "5,000+")}</strong> verified reviews',
        'Cross-referenced with product specifications and expert opinions',
        'Excluded anything under <strong>4.0 stars</strong> or fewer than 500 reviews',
        'Prioritized <strong>value for money</strong> and real-world performance',
    ])
    methodology_html = _build_methodology_html(methodology)
    etsy_html = _build_etsy_html(brand_key)
    faq_html = _build_faq_html(faq_items)

    # Build schemas
    schema_article, schema_faq, schema_product = _build_schemas(
        title, meta_desc, slug, site_config, theme['expert_name'], products, faq_items
    )

    # Top product info (for sticky CTA)
    top_product = products[0] if products else {}
    top_name = top_product.get('name', title)
    top_url = top_product.get('amazon_url', '#')
    top_price = f'${top_product.get("price_low", "?")}-${top_product.get("price_high", "?")}'
    top_rating = top_product.get('rating', 4.5)
    top_save = top_product.get('subscribe_save', '')

    # Face images
    faces = FALLBACK_FACES.get(brand_key, FALLBACK_FACES['deals'])

    # Before/After
    before = article_data.get('before', {'emoji': '\U0001f630', 'text': 'The problem you had before'})
    after = article_data.get('after', {'emoji': '\U0001f60a', 'text': 'How life improves after'})

    # Final CTA text
    final_cta = article_data.get('final_cta_text', f'Start with the {top_name}. Most people notice a difference within the first week.')

    # ── Replace ALL template variables ─────────────────────────────────────
    replacements = {
        '{{PAGE_TITLE}}': _esc(title),
        '{{SITE_NAME}}': _esc(site_config.get('site_name', '')),
        '{{META_DESCRIPTION}}': _esc(meta_desc),
        '{{SEO_KEYWORDS}}': _esc(', '.join(article_data.get('seo_keywords', [slug.replace('-', ', ')]))),
        '{{ARTICLE_URL}}': _esc(site_config['base_url'] + '/articles/' + slug + '.html'),
        '{{HERO_IMAGE}}': hero_image,
        '{{FONT_IMPORT}}': theme['font_import'],
        '{{HEADING_FONT}}': theme['heading_font'],
        '{{BODY_FONT}}': theme['body_font'],
        '{{COLOR_BG}}': c['bg'],
        '{{COLOR_SURFACE}}': c['surface'],
        '{{COLOR_BORDER}}': c['border'],
        '{{COLOR_ACCENT}}': c['accent'],
        '{{COLOR_ACCENT_LIGHT}}': c['accent_light'],
        '{{COLOR_TEXT}}': c['text'],
        '{{COLOR_MUTED}}': c['muted'],
        '{{COLOR_WARM}}': c['warm'],
        '{{SITE_TAGLINE}}': theme['site_tagline'],
        '{{CATEGORY}}': _esc(article_data.get('category', 'Wellness')),
        '{{CRUMB_TITLE}}': _esc(title[:40]),
        '{{DATE_DISPLAY}}': date_display,
        '{{BRANDS_TESTED}}': str(article_data.get('brands_tested', 8)),
        '{{READ_TIME}}': article_data.get('read_time', '4 min'),
        '{{REVIEWS_ANALYZED}}': _esc(article_data.get('reviews_analyzed', '5,000+')),
        '{{EXPERT_NAME}}': _esc(theme['expert_name']),
        '{{EXPERT_INITIALS}}': theme['expert_initials'],
        '{{EXPERT_CREDENTIALS}}': _esc(theme['expert_credentials']),
        '{{EXPERT_BIO}}': _esc(theme['expert_bio']),
        '{{FACE_1}}': faces[0],
        '{{FACE_2}}': faces[1],
        '{{FACE_3}}': faces[2],
        '{{FACE_4}}': faces[3],
        '{{BEFORE_EMOJI}}': before.get('emoji', '\U0001f630'),
        '{{BEFORE_TEXT}}': _esc(before.get('text', '')),
        '{{AFTER_EMOJI}}': after.get('emoji', '\U0001f60a'),
        '{{AFTER_TEXT}}': _esc(after.get('text', '')),
        '{{VERDICT_TEXT}}': article_data.get('verdict', ''),
        '{{QUICK_PICKS_HTML}}': quick_picks,
        '{{PRODUCT_BLOCKS_HTML}}': product_blocks_html,
        '{{COMPARISON_TABLE_HTML}}': comparison_html,
        '{{METHODOLOGY_HTML}}': methodology_html,
        '{{ETSY_CTA_HTML}}': etsy_html,
        '{{FAQ_ITEMS_HTML}}': faq_html,
        '{{FINAL_CTA_TEXT}}': _esc(final_cta),
        '{{TOP_PRODUCT_NAME}}': _esc(top_name),
        '{{TOP_PRODUCT_URL}}': _esc(top_url),
        '{{TOP_PRODUCT_PRICE}}': top_price,
        '{{TOP_PRODUCT_RATING}}': str(top_rating),
        '{{TOP_PRODUCT_SAVE}}': _esc(top_save) if top_save else 'Free returns',
        '{{YEAR}}': str(year),
        '{{SCHEMA_ARTICLE}}': schema_article,
        '{{SCHEMA_FAQ}}': schema_faq,
        '{{SCHEMA_PRODUCT}}': schema_product,
    }

    result = template_html
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, str(value))

    # Verify no unfilled placeholders remain
    remaining = re.findall(r'\{\{[A-Z_]+\}\}', result)
    if remaining:
        logger.warning(f'Unfilled template placeholders in {slug}: {remaining}')
        # Fill remaining with empty string so page doesn't break
        for r in remaining:
            result = result.replace(r, '')

    return result
