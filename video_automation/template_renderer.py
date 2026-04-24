"""Clean brand-specific article renderer.

Three distinct article designs:
- Deals (DailyDealDarling): Product-forward, first-person, PAS framework
- Fitness (FitOver35): Value-first education, dark theme, gear at end only
- Menopause (MenopausePlanner): Warm wellness, free resource + Etsy product

No before/after cards, no comparison tables, no trust badges, no payment icons,
no fake social proof, no sticky bars, no methodology sections.
"""

import html
import json
import os
import re
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ── Fallback hero images ─────────────────────────────────────────────────

FALLBACK_HERO_IMAGES = {
    'fitness': 'https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=900',
    'menopause': 'https://images.pexels.com/photos/6585764/pexels-photo-6585764.jpeg?auto=compress&cs=tinysrgb&w=900',
    'deals': 'https://images.pexels.com/photos/5632399/pexels-photo-5632399.jpeg?auto=compress&cs=tinysrgb&w=900',
    'pilottools': 'https://images.pexels.com/photos/546819/pexels-photo-546819.jpeg?auto=compress&cs=tinysrgb&w=900',
    'homedecor': 'https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg?auto=compress&cs=tinysrgb&w=900',
    'beauty': 'https://images.pexels.com/photos/3373739/pexels-photo-3373739.jpeg?auto=compress&cs=tinysrgb&w=900',
    'default': 'https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=900',
}

# Brand Google Analytics IDs
_BRAND_GA_IDS = {
    'fitness': 'G-1FC6FH34L9',
    'deals': 'G-HVCLZPEYNS',
    'menopause': 'G-02ZPS3H3GC',
}

# Brand Kit signup form IDs
_BRAND_FORM_IDS = {
    'fitness': '8946984',
    'deals': '9144859',
    'menopause': '9144926',
}

# Cross-promotion: which brands each site promotes and with what tagline
_CROSS_PROMO_DATA = {
    'fitness': [
        {'name': 'Daily Deal Darling', 'tagline': 'Fitness gear deals curated daily — save without settling.', 'url': 'https://www.dailydealdarling.com'},
        {'name': 'The Menopause Planner', 'tagline': 'Wellness tools for women navigating hormonal changes.', 'url': 'https://menopause-planner-website.vercel.app'},
    ],
    'deals': [
        {'name': 'Home Decor Edit', 'tagline': 'Budget-friendly home upgrades that look expensive.', 'url': 'https://www.dailydealdarling.com'},
        {'name': 'FitOver35', 'tagline': 'Science-backed fitness for men over 35.', 'url': 'https://fitover35.com'},
    ],
    'menopause': [
        {'name': 'The Beauty Shelf', 'tagline': 'Skincare that actually works for mature skin.', 'url': 'https://www.dailydealdarling.com'},
        {'name': 'FitOver35', 'tagline': 'Fitness and wellness for the over-35 crowd.', 'url': 'https://fitover35.com'},
    ],
    'pilottools': [
        {'name': 'Daily Deal Darling', 'tagline': 'The sharpest deal-finding tools, reviewed and ranked.', 'url': 'https://www.dailydealdarling.com'},
        {'name': 'FitOver35', 'tagline': 'AI fitness apps and training science for men over 35.', 'url': 'https://fitover35.com'},
    ],
    'homedecor': [
        {'name': 'Daily Deal Darling', 'tagline': 'Budget home finds that look a million bucks.', 'url': 'https://www.dailydealdarling.com'},
        {'name': 'The Beauty Shelf', 'tagline': 'Vanity essentials and bathroom beauty picks.', 'url': 'https://www.dailydealdarling.com'},
    ],
    'beauty': [
        {'name': 'The Menopause Planner', 'tagline': 'Skincare and wellness through hormonal changes.', 'url': 'https://menopause-planner-website.vercel.app'},
        {'name': 'Home Decor Edit', 'tagline': 'Vanity organization and bathroom upgrade ideas.', 'url': 'https://www.dailydealdarling.com'},
    ],
}

# Per-brand visual theme for the cross-promo section
_CROSS_PROMO_THEME = {
    'fitness':   {'bg': '#0a0a0a', 'border': '#333', 'label': '#E8C547', 'font': 'Space Grotesk', 'card_bg': '#1a1a1a', 'card_border': '#222', 'name': '#fff', 'tagline': '#888', 'btn_bg': '#E8C547', 'btn_fg': '#111'},
    'deals':     {'bg': '#fdf5f7', 'border': '#f0d5dc', 'label': '#C47D8E', 'font': 'Lora', 'card_bg': '#fff', 'card_border': '#f0d5dc', 'name': '#2D2D2D', 'tagline': '#666', 'btn_bg': '#C47D8E', 'btn_fg': '#fff'},
    'menopause': {'bg': '#f5ede0', 'border': '#e8dcc8', 'label': '#6B705C', 'font': 'DM Serif Display', 'card_bg': '#fff', 'card_border': '#DDBEA9', 'name': '#3a3a3a', 'tagline': '#666', 'btn_bg': '#6B705C', 'btn_fg': '#fff'},
    'pilottools': {'bg': '#0c1a2e', 'border': '#1e293b', 'label': '#0EA5E9', 'font': 'Space Grotesk', 'card_bg': '#1e293b', 'card_border': '#334155', 'name': '#f1f5f9', 'tagline': '#94a3b8', 'btn_bg': '#0EA5E9', 'btn_fg': '#fff'},
    'homedecor': {'bg': '#f5f0e8', 'border': '#e8dcc8', 'label': '#6B705C', 'font': 'DM Serif Display', 'card_bg': '#fff', 'card_border': '#DDBEA9', 'name': '#3a3a3a', 'tagline': '#666', 'btn_bg': '#6B705C', 'btn_fg': '#fff'},
    'beauty':    {'bg': '#fdf5f5', 'border': '#f0e0e0', 'label': '#D4A0A0', 'font': 'Lora', 'card_bg': '#fff', 'card_border': '#f0d0d0', 'name': '#3a3a3a', 'tagline': '#666', 'btn_bg': '#D4A0A0', 'btn_fg': '#fff'},
}


def _cross_promo_section(brand_key):
    """Return a themed 'From Our Network' cross-promotion section."""
    promos = _CROSS_PROMO_DATA.get(brand_key, [])
    if not promos:
        return ''
    t = _CROSS_PROMO_THEME.get(brand_key, _CROSS_PROMO_THEME['deals'])
    cards = ''
    for promo in promos:
        name = _esc(promo['name'])
        tagline = _esc(promo['tagline'])
        url = _esc(promo['url'])
        cards += f'''
        <div style="background:{t['card_bg']};border:1px solid {t['card_border']};border-radius:10px;padding:18px 20px;flex:1;min-width:220px;">
          <div style="font-family:'{t['font']}',serif;font-weight:600;font-size:1em;color:{t['name']};margin-bottom:6px;">{name}</div>
          <p style="margin:0 0 14px;font-size:0.88em;color:{t['tagline']};line-height:1.5;">{tagline}</p>
          <a href="{url}" target="_blank" rel="noopener"
             style="display:inline-block;background:{t['btn_bg']};color:{t['btn_fg']};padding:8px 18px;border-radius:6px;text-decoration:none;font-weight:600;font-size:0.85em;">
            Visit Site &rarr;</a>
        </div>'''
    return f'''
    <section style="margin:40px 0;padding:24px;background:{t['bg']};border-radius:12px;border-top:2px solid {t['border']};">
      <p style="font-size:0.72em;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:{t['label']};margin:0 0 14px;">From Our Network</p>
      <div style="display:flex;gap:16px;flex-wrap:wrap;">
        {cards}
      </div>
    </section>'''


def _esc(text):
    """HTML-escape a string."""
    return html.escape(str(text)) if text else ''


def _ensure_image(url, fallback):
    """Return url if truthy, otherwise fallback."""
    if url and isinstance(url, str) and url.startswith('http'):
        return url
    return fallback


def _build_schema_json(title, meta_desc, slug, site_config, faq_items=None):
    """Build Article + FAQ Schema.org JSON-LD."""
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

    schemas = f'<script type="application/ld+json">{article_schema}</script>'

    if faq_items:
        faq_entities = []
        for faq in faq_items:
            faq_entities.append({
                '@type': 'Question',
                'name': faq.get('q', ''),
                'acceptedAnswer': {'@type': 'Answer', 'text': faq.get('a', '')},
            })
        schemas += f'\n<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_entities})}</script>'

    return schemas


def _star_html(rating):
    """Render star rating as text."""
    full = int(float(rating))
    return '\u2605' * full + '\u2606' * (5 - full) + f' {rating}'


# ═══════════════════════════════════════════════════════════════════════════
# DEALS — DailyDealDarling: Product-forward, first-person, PAS framework
# ═══════════════════════════════════════════════════════════════════════════

def _render_deals_article(article_data, site_config, slug):
    """Render a clean deals article — conversational product review blog post."""
    title = _esc(article_data.get('title', slug.replace('-', ' ').title()))
    meta_desc = _esc(article_data.get('meta_description', title))
    hero_url = _ensure_image(article_data.get('hero_url', ''), FALLBACK_HERO_IMAGES['deals'])
    ga_id = _BRAND_GA_IDS.get('deals', '')
    form_id = _BRAND_FORM_IDS.get('deals', '')
    year = datetime.now(timezone.utc).year
    date_display = datetime.now(timezone.utc).strftime('%B %d, %Y')
    faq_items = article_data.get('faq', [])
    schemas = _build_schema_json(title, meta_desc, slug, site_config, faq_items)

    # Intro paragraphs
    intro_html = ''
    for p in article_data.get('intro_paragraphs', []):
        intro_html += f'<p>{_esc(p)}</p>\n'

    # Product cards
    products_html = ''
    for product in article_data.get('products', []):
        is_winner = product.get('is_winner', False)
        name = _esc(product.get('name', 'Product'))
        price = _esc(product.get('price', ''))
        rating = product.get('rating', 4.5)
        review_count = _esc(product.get('review_count', '1,000+'))
        review_text = _esc(product.get('personal_review_text', ''))
        section_heading = _esc(product.get('section_heading', name))
        amazon_url = _esc(product.get('amazon_url', '#'))
        product_img = _esc(product.get('product_image', ''))

        winner_border = 'border: 2px solid #C47D8E;' if is_winner else 'border: 1px solid #e5e7eb;'
        winner_label = '<span style="display:inline-block;background:#C47D8E;color:#fff;font-size:0.78em;padding:3px 12px;border-radius:4px;margin-bottom:10px;font-weight:600;">The one I bought</span>' if is_winner else ''

        img_block = ''
        if product_img:
            img_block = (
                f'<a href="{amazon_url}" target="_blank" rel="nofollow sponsored" style="flex-shrink:0;">'
                f'<img src="{product_img}" alt="{name}" width="100" height="100" '
                f'style="object-fit:contain;border-radius:8px;background:#fff;padding:4px;" loading="lazy" '
                f'onerror="this.parentElement.style.display=\'none\'"></a>'
            )

        products_html += f'''
        <div style="{winner_border}border-radius:12px;padding:20px;margin:24px 0;background:#fff;">
          {winner_label}
          <h2 style="font-family:'Lora',serif;font-size:1.3em;margin:0 0 8px;color:#2D2D2D;">{section_heading}</h2>
          <div style="display:flex;gap:16px;align-items:flex-start;margin:12px 0;">
            {img_block}
            <div>
              <div style="font-size:0.9em;color:#666;margin-bottom:6px;">{_star_html(rating)} &middot; {review_count} reviews &middot; {price}</div>
              <p style="margin:0;color:#444;line-height:1.6;">{review_text}</p>
            </div>
          </div>
          <a href="{amazon_url}" target="_blank" rel="nofollow sponsored"
             style="display:inline-block;background:#C47D8E;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none;font-weight:600;font-size:0.95em;margin-top:12px;">
            See it on Amazon &rarr;</a>
        </div>'''

    # Verdict
    verdict_html = ''
    verdict_text = article_data.get('verdict_text', '')
    if verdict_text:
        verdict_html = f'''
        <div style="border-left:3px solid #C47D8E;padding:16px 20px;margin:28px 0;background:#fdf5f7;border-radius:0 8px 8px 0;">
          <p style="margin:0;font-family:'Lora',serif;font-style:italic;color:#2D2D2D;line-height:1.6;">{_esc(verdict_text)}</p>
        </div>'''

    # FAQ
    faq_html = ''
    for faq in faq_items:
        faq_html += f'''
        <div style="margin:16px 0;">
          <h3 style="font-family:'Lora',serif;font-size:1.05em;color:#2D2D2D;margin:0 0 6px;">{_esc(faq.get('q', ''))}</h3>
          <p style="color:#555;margin:0;line-height:1.6;">{_esc(faq.get('a', ''))}</p>
        </div>'''

    # Email signup
    signup_html = ''
    if form_id:
        signup_html = f'''
        <div style="background:#fdf5f7;border-radius:12px;padding:24px;margin:32px 0;text-align:center;">
          <p style="font-family:'Lora',serif;font-size:1.1em;color:#2D2D2D;margin:0 0 12px;">Get the best deals in your inbox every week</p>
          <script async data-uid="{form_id}" src="https://dailydealdarling.ck.page/{form_id}/index.js"></script>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Daily Deal Darling</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{_esc(site_config['base_url'])}/articles/{slug}.html">
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
{schemas}
{"<script async src='https://www.googletagmanager.com/gtag/js?id=" + ga_id + "'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','" + ga_id + "')</script>" if ga_id else ''}
  <!-- AdSense -->
  <meta name="google-adsense-account" content="ca-pub-7018489366035978">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7018489366035978" crossorigin="anonymous"></script>
</head>
<body style="margin:0;padding:0;background:#FAFAFA;color:#2D2D2D;font-family:'Inter',sans-serif;line-height:1.7;">

<nav style="background:#fff;border-bottom:1px solid #eee;padding:14px 20px;">
  <div style="max-width:680px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;">
    <a href="../index.html" style="text-decoration:none;font-family:'Lora',serif;font-size:1.15em;color:#2D2D2D;font-weight:600;">Daily Deal <span style="color:#C47D8E;">Darling</span></a>
    <a href="./" style="text-decoration:none;color:#666;font-size:0.9em;">All Articles</a>
  </div>
</nav>

<main style="max-width:680px;margin:0 auto;padding:32px 20px;">
  <p style="font-size:0.82em;color:#999;margin:0 0 8px;">{date_display}</p>
  <h1 style="font-family:'Lora',serif;font-size:1.8em;line-height:1.3;margin:0 0 20px;color:#2D2D2D;">{title}</h1>

  <img src="{hero_url}" alt="{title}" style="width:100%;border-radius:10px;margin:0 0 24px;" loading="lazy">

  {intro_html}

  {products_html}

  {verdict_html}

  {f'<h2 style="font-family:Lora,serif;margin:36px 0 16px;">FAQ</h2>' + faq_html if faq_html else ''}

  {signup_html}

  {_cross_promo_section('deals')}
</main>

<footer style="border-top:1px solid #eee;padding:24px 20px;text-align:center;color:#999;font-size:0.82em;">
  <p>&copy; {year} Daily Deal Darling. Affiliate links may earn a commission.</p>
</footer>

</body>
</html>'''


# ═══════════════════════════════════════════════════════════════════════════
# FITNESS — FitOver35: Dark theme, value-first education, gear at end only
# ═══════════════════════════════════════════════════════════════════════════

def _render_fitness_article(article_data, site_config, slug):
    """Render a clean fitness article — 90% education, compact gear section at bottom."""
    title = _esc(article_data.get('title', slug.replace('-', ' ').title()))
    meta_desc = _esc(article_data.get('meta_description', title))
    hero_url = _ensure_image(article_data.get('hero_url', ''), FALLBACK_HERO_IMAGES['fitness'])
    ga_id = _BRAND_GA_IDS.get('fitness', '')
    form_id = _BRAND_FORM_IDS.get('fitness', '')
    year = datetime.now(timezone.utc).year
    date_display = datetime.now(timezone.utc).strftime('%B %d, %Y')
    faq_items = article_data.get('faq', [])
    schemas = _build_schema_json(title, meta_desc, slug, site_config, faq_items)

    # Intro hook
    intro_hook = article_data.get('intro_hook', '')
    intro_html = f'<p style="font-size:1.05em;line-height:1.7;color:#ccc;">{_esc(intro_hook)}</p>' if intro_hook else ''

    # Educational sections with tip boxes
    sections_html = ''
    for section in article_data.get('sections', []):
        heading = _esc(section.get('heading', ''))
        body_html = ''
        for p in section.get('body_paragraphs', []):
            body_html += f'<p style="color:#ccc;line-height:1.7;margin:0 0 14px;">{_esc(p)}</p>\n'

        tip_box = ''
        tip_text = section.get('tip_box_text', '')
        if tip_text:
            tip_box = f'''
            <div style="background:#1a1a0a;border-left:3px solid #E8C547;padding:14px 18px;margin:18px 0;border-radius:0 8px 8px 0;">
              <p style="margin:0;color:#E8C547;font-weight:600;font-size:0.88em;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">The Fix</p>
              <p style="margin:0;color:#ddd;line-height:1.6;">{_esc(tip_text)}</p>
            </div>'''

        sections_html += f'''
        <section style="margin:32px 0;">
          <h2 style="font-family:'Space Grotesk',sans-serif;font-size:1.35em;color:#fff;margin:0 0 14px;">{heading}</h2>
          {body_html}
          {tip_box}
        </section>'''

    # Compact gear section at the bottom
    gear_html = ''
    gear_items = article_data.get('gear_recommendations', [])
    if gear_items:
        gear_cards = ''
        for item in gear_items:
            name = _esc(item.get('name', ''))
            price = _esc(item.get('price', ''))
            rating = item.get('rating', 4.5)
            review_count = _esc(item.get('review_count', ''))
            note = _esc(item.get('one_line_note', ''))
            amazon_url = _esc(item.get('amazon_url', '#'))
            product_img = _esc(item.get('product_image', ''))

            img_block = ''
            if product_img:
                img_block = (
                    f'<img src="{product_img}" alt="{name}" width="56" height="56" '
                    f'style="object-fit:contain;border-radius:6px;background:#222;padding:3px;flex-shrink:0;" loading="lazy" '
                    f'onerror="this.style.display=\'none\'">'
                )

            gear_cards += f'''
            <div style="display:flex;gap:12px;align-items:center;padding:14px 0;border-bottom:1px solid #222;">
              {img_block}
              <div style="flex:1;min-width:0;">
                <div style="font-weight:600;color:#fff;font-size:0.95em;">{name}</div>
                <div style="font-size:0.82em;color:#888;">{_star_html(rating)} &middot; {review_count} &middot; {price}</div>
                <div style="font-size:0.88em;color:#aaa;margin-top:2px;">{note}</div>
              </div>
              <a href="{amazon_url}" target="_blank" rel="nofollow sponsored"
                 style="color:#E8C547;text-decoration:none;font-size:0.85em;white-space:nowrap;font-weight:500;">
                See on Amazon &rarr;</a>
            </div>'''

        gear_html = f'''
        <section style="margin:40px 0;padding-top:28px;border-top:1px solid #333;">
          <h2 style="font-family:'Space Grotesk',sans-serif;font-size:1.1em;color:#E8C547;margin:0 0 4px;">What I Use</h2>
          <p style="color:#888;font-size:0.88em;margin:0 0 14px;">Here&rsquo;s my gear if you&rsquo;re curious. No pressure.</p>
          {gear_cards}
        </section>'''

    # FAQ
    faq_html = ''
    for faq in faq_items:
        faq_html += f'''
        <div style="margin:16px 0;">
          <h3 style="font-family:'Space Grotesk',sans-serif;font-size:1em;color:#fff;margin:0 0 6px;">{_esc(faq.get('q', ''))}</h3>
          <p style="color:#aaa;margin:0;line-height:1.6;">{_esc(faq.get('a', ''))}</p>
        </div>'''

    # Email signup
    signup_html = ''
    if form_id:
        signup_html = f'''
        <div style="background:#1a1a0a;border:1px solid #333;border-radius:10px;padding:22px;margin:32px 0;text-align:center;">
          <p style="font-family:'Space Grotesk',sans-serif;color:#E8C547;font-size:1em;margin:0 0 10px;">Free: 7-Day Fat Burn Kickstart Plan</p>
          <script async data-uid="{form_id}" src="https://fitover35.ck.page/{form_id}/index.js"></script>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | FitOver35</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{_esc(site_config['base_url'])}/articles/{slug}.html">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
{schemas}
{"<script async src='https://www.googletagmanager.com/gtag/js?id=" + ga_id + "'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','" + ga_id + "')</script>" if ga_id else ''}
  <!-- AdSense -->
  <meta name="google-adsense-account" content="ca-pub-7018489366035978">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7018489366035978" crossorigin="anonymous"></script>
</head>
<body style="margin:0;padding:0;background:#111;color:#fff;font-family:'Inter',sans-serif;line-height:1.7;">

<nav style="background:#0a0a0a;border-bottom:1px solid #222;padding:14px 20px;">
  <div style="max-width:700px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;">
    <a href="../index.html" style="text-decoration:none;font-family:'Space Grotesk',sans-serif;font-size:1.15em;color:#fff;font-weight:600;">Fit<span style="color:#E8C547;">Over35</span></a>
    <div style="display:flex;gap:16px;">
      <a href="../blog.html" style="text-decoration:none;color:#888;font-size:0.9em;">Articles</a>
      <a href="../about.html" style="text-decoration:none;color:#888;font-size:0.9em;">About</a>
    </div>
  </div>
</nav>

<main style="max-width:700px;margin:0 auto;padding:32px 20px;">
  <p style="font-size:0.82em;color:#666;margin:0 0 8px;">{date_display} &middot; By Talhah Bilal, ISSA-CPT</p>
  <h1 style="font-family:'Space Grotesk',sans-serif;font-size:1.8em;line-height:1.3;margin:0 0 20px;color:#fff;">{title}</h1>

  <img src="{hero_url}" alt="{title}" style="width:100%;border-radius:10px;margin:0 0 24px;" loading="lazy">

  {intro_html}

  {sections_html}

  {gear_html}

  {f'<section style="margin:36px 0;"><h2 style="font-family:Space Grotesk,sans-serif;font-size:1.2em;color:#E8C547;margin:0 0 16px;">FAQ</h2>' + faq_html + '</section>' if faq_html else ''}

  {signup_html}

  {_cross_promo_section('fitness')}
</main>

<footer style="border-top:1px solid #222;padding:24px 20px;text-align:center;color:#666;font-size:0.82em;">
  <p>&copy; {year} FitOver35. Affiliate links may earn a commission.</p>
</footer>

</body>
</html>'''


# ═══════════════════════════════════════════════════════════════════════════
# MENOPAUSE — MenopausePlanner: Warm wellness, free tracker + Etsy planner
# ═══════════════════════════════════════════════════════════════════════════

ETSY_PLANNER_URL = 'https://www.etsy.com/listing/4435219468/menopause-wellness-planner-bundle?utm_source=Pinterest&utm_medium=organic'


def _render_menopause_article(article_data, site_config, slug):
    """Render a clean menopause article — warm wellness, value-first, Etsy at end."""
    title = _esc(article_data.get('title', slug.replace('-', ' ').title()))
    meta_desc = _esc(article_data.get('meta_description', title))
    hero_url = _ensure_image(article_data.get('hero_url', ''), FALLBACK_HERO_IMAGES['menopause'])
    ga_id = _BRAND_GA_IDS.get('menopause', '')
    form_id = _BRAND_FORM_IDS.get('menopause', '')
    year = datetime.now(timezone.utc).year
    date_display = datetime.now(timezone.utc).strftime('%B %d, %Y')
    faq_items = article_data.get('faq', [])
    schemas = _build_schema_json(title, meta_desc, slug, site_config, faq_items)

    # Intro hook
    intro_hook = article_data.get('intro_hook', '')
    intro_html = f'<p style="font-size:1.05em;line-height:1.7;color:#555;">{_esc(intro_hook)}</p>' if intro_hook else ''

    # Educational sections with tip boxes
    sections_html = ''
    for section in article_data.get('sections', []):
        heading = _esc(section.get('heading', ''))
        body_html = ''
        for p in section.get('body_paragraphs', []):
            body_html += f'<p style="color:#555;line-height:1.7;margin:0 0 14px;">{_esc(p)}</p>\n'

        tip_box = ''
        tip_text = section.get('tip_box_text', '')
        if tip_text:
            tip_box = f'''
            <div style="background:#f0ebe3;border-left:3px solid #6B705C;padding:14px 18px;margin:18px 0;border-radius:0 8px 8px 0;">
              <p style="margin:0;color:#6B705C;font-weight:600;font-size:0.88em;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">Try This</p>
              <p style="margin:0;color:#444;line-height:1.6;">{_esc(tip_text)}</p>
            </div>'''

        sections_html += f'''
        <section style="margin:32px 0;">
          <h2 style="font-family:'DM Serif Display',serif;font-size:1.35em;color:#3a3a3a;margin:0 0 14px;">{heading}</h2>
          {body_html}
          {tip_box}
        </section>'''

    # Free resource CTA
    free_resource_html = ''
    free_resource = article_data.get('free_resource_cta', {})
    if free_resource:
        fr_heading = _esc(free_resource.get('heading', 'Free: Symptom Tracker Printable'))
        fr_desc = _esc(free_resource.get('description', 'Track your symptoms and spot patterns.'))
        fr_button = _esc(free_resource.get('button_text', 'Download Free Tracker'))
        free_resource_html = f'''
        <div style="background:linear-gradient(135deg,#f5ede0,#e8dcc8);border-radius:12px;padding:24px;margin:32px 0;text-align:center;">
          <p style="font-family:'DM Serif Display',serif;font-size:1.15em;color:#3a3a3a;margin:0 0 8px;">{fr_heading}</p>
          <p style="color:#666;margin:0 0 14px;font-size:0.92em;">{fr_desc}</p>
          <script async data-uid="{form_id}" src="https://menopause-planner.ck.page/{form_id}/index.js"></script>
        </div>'''

    # Etsy planner CTA
    etsy_html = ''
    etsy_section = article_data.get('etsy_product_section', {})
    if etsy_section:
        etsy_heading = _esc(etsy_section.get('heading', 'The Menopause Wellness Planner'))
        etsy_desc = _esc(etsy_section.get('description', ''))
        etsy_price = _esc(etsy_section.get('price', '$14.99'))
        etsy_button = _esc(etsy_section.get('button_text', 'Get the Planner on Etsy'))
        etsy_html = f'''
        <div style="background:#fff;border:2px solid #DDBEA9;border-radius:12px;padding:24px;margin:32px 0;text-align:center;">
          <p style="font-size:0.78em;font-weight:600;letter-spacing:0.08em;color:#6B705C;text-transform:uppercase;margin:0 0 6px;">Digital Download &mdash; {etsy_price}</p>
          <p style="font-family:'DM Serif Display',serif;font-size:1.2em;color:#3a3a3a;margin:0 0 10px;">{etsy_heading}</p>
          <p style="color:#666;margin:0 0 16px;font-size:0.92em;">{etsy_desc}</p>
          <a href="{ETSY_PLANNER_URL}" target="_blank" rel="noopener"
             style="display:inline-block;background:#6B705C;color:#fff;padding:11px 24px;border-radius:8px;text-decoration:none;font-weight:600;font-size:0.95em;">
            {etsy_button} &rarr;</a>
          <p style="margin:10px 0 0;font-size:0.78em;color:#999;">Instant download &bull; Print at home &bull; One-time purchase</p>
        </div>'''
    else:
        # Always include Etsy CTA even if Gemini didn't generate one
        etsy_html = f'''
        <div style="background:#fff;border:2px solid #DDBEA9;border-radius:12px;padding:24px;margin:32px 0;text-align:center;">
          <p style="font-size:0.78em;font-weight:600;letter-spacing:0.08em;color:#6B705C;text-transform:uppercase;margin:0 0 6px;">Digital Download &mdash; $14.99</p>
          <p style="font-family:'DM Serif Display',serif;font-size:1.2em;color:#3a3a3a;margin:0 0 10px;">The Menopause Wellness Planner</p>
          <p style="color:#666;margin:0 0 16px;font-size:0.92em;">Track symptoms, sleep, supplements, and mood in one place. Built for women navigating this transition.</p>
          <a href="{ETSY_PLANNER_URL}" target="_blank" rel="noopener"
             style="display:inline-block;background:#6B705C;color:#fff;padding:11px 24px;border-radius:8px;text-decoration:none;font-weight:600;font-size:0.95em;">
            Get the Planner on Etsy &rarr;</a>
          <p style="margin:10px 0 0;font-size:0.78em;color:#999;">Instant download &bull; Print at home &bull; One-time purchase</p>
        </div>'''

    # Amazon products (gentle, compact)
    amazon_html = ''
    amazon_items = article_data.get('amazon_products', [])
    if amazon_items:
        amazon_cards = ''
        for item in amazon_items:
            name = _esc(item.get('name', ''))
            price = _esc(item.get('price', ''))
            rating = item.get('rating', 4.5)
            review_count = _esc(item.get('review_count', ''))
            note = _esc(item.get('one_line_note', ''))
            amazon_url = _esc(item.get('amazon_url', '#'))
            product_img = _esc(item.get('product_image', ''))

            img_block = ''
            if product_img:
                img_block = (
                    f'<img src="{product_img}" alt="{name}" width="52" height="52" '
                    f'style="object-fit:contain;border-radius:6px;background:#f9f6f0;padding:3px;flex-shrink:0;" loading="lazy" '
                    f'onerror="this.style.display=\'none\'">'
                )

            amazon_cards += f'''
            <div style="display:flex;gap:12px;align-items:center;padding:14px 0;border-bottom:1px solid #e8dcc8;">
              {img_block}
              <div style="flex:1;min-width:0;">
                <div style="font-weight:600;color:#3a3a3a;font-size:0.92em;">{name}</div>
                <div style="font-size:0.8em;color:#8B7355;">{_star_html(rating)} &middot; {review_count} &middot; {price}</div>
                <div style="font-size:0.85em;color:#666;margin-top:2px;">{note}</div>
              </div>
              <a href="{amazon_url}" target="_blank" rel="nofollow sponsored"
                 style="color:#6B705C;text-decoration:none;font-size:0.82em;white-space:nowrap;font-weight:500;">
                See on Amazon &rarr;</a>
            </div>'''

        amazon_html = f'''
        <section style="margin:32px 0;padding-top:24px;border-top:1px solid #e8dcc8;">
          <h2 style="font-family:'DM Serif Display',serif;font-size:1.1em;color:#6B705C;margin:0 0 4px;">What&rsquo;s Been Helping Me</h2>
          <p style="color:#999;font-size:0.85em;margin:0 0 12px;">A few things I keep on my nightstand.</p>
          {amazon_cards}
        </section>'''

    # FAQ
    faq_html = ''
    for faq in faq_items:
        faq_html += f'''
        <div style="margin:16px 0;">
          <h3 style="font-family:'DM Serif Display',serif;font-size:1em;color:#3a3a3a;margin:0 0 6px;">{_esc(faq.get('q', ''))}</h3>
          <p style="color:#666;margin:0;line-height:1.6;">{_esc(faq.get('a', ''))}</p>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | The Menopause Planner</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{_esc(site_config['base_url'])}/articles/{slug}.html">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
{schemas}
{"<script async src='https://www.googletagmanager.com/gtag/js?id=" + ga_id + "'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','" + ga_id + "')</script>" if ga_id else ''}
  <!-- AdSense -->
  <meta name="google-adsense-account" content="ca-pub-7018489366035978">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7018489366035978" crossorigin="anonymous"></script>
</head>
<body style="margin:0;padding:0;background:#FAF7F0;color:#3a3a3a;font-family:'Outfit',sans-serif;line-height:1.7;">

<nav style="background:#fff;border-bottom:1px solid #e8dcc8;padding:14px 20px;">
  <div style="max-width:680px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;">
    <a href="../index.html" style="text-decoration:none;font-family:'DM Serif Display',serif;font-size:1.15em;color:#3a3a3a;">The Menopause <span style="color:#6B705C;">Planner</span></a>
    <a href="./" style="text-decoration:none;color:#8B7355;font-size:0.9em;">All Articles</a>
  </div>
</nav>

<main style="max-width:680px;margin:0 auto;padding:32px 20px;">
  <p style="font-size:0.82em;color:#A5A58D;margin:0 0 8px;">{date_display}</p>
  <h1 style="font-family:'DM Serif Display',serif;font-size:1.8em;line-height:1.3;margin:0 0 20px;color:#3a3a3a;">{title}</h1>

  <img src="{hero_url}" alt="{title}" style="width:100%;border-radius:10px;margin:0 0 24px;" loading="lazy">

  {intro_html}

  {sections_html}

  {free_resource_html}

  {etsy_html}

  {amazon_html}

  {f'<section style="margin:36px 0;"><h2 style="font-family:DM Serif Display,serif;font-size:1.2em;color:#6B705C;margin:0 0 16px;">FAQ</h2>' + faq_html + '</section>' if faq_html else ''}

  {_cross_promo_section('menopause')}
</main>

<footer style="border-top:1px solid #e8dcc8;padding:24px 20px;text-align:center;color:#A5A58D;font-size:0.82em;">
  <p>&copy; {year} The Menopause Planner. Affiliate links may earn a commission.</p>
</footer>

</body>
</html>'''


# ═══════════════════════════════════════════════════════════════════════════
# PILOTTOOLS — Dark/tech theme, value-first education, SaaS tool recs
# ═══════════════════════════════════════════════════════════════════════════

def _render_pilottools_article(article_data, site_config, slug):
    """Render a clean PilotTools article — dark tech theme, AI tool education."""
    title = _esc(article_data.get('title', slug.replace('-', ' ').title()))
    meta_desc = _esc(article_data.get('meta_description', title))
    hero_url = _ensure_image(article_data.get('hero_url', ''), FALLBACK_HERO_IMAGES.get('pilottools', FALLBACK_HERO_IMAGES['default']))
    ga_id = _BRAND_GA_IDS.get('pilottools', '')
    form_id = _BRAND_FORM_IDS.get('pilottools', '')
    year = datetime.now(timezone.utc).year
    date_display = datetime.now(timezone.utc).strftime('%B %d, %Y')
    faq_items = article_data.get('faq', [])
    schemas = _build_schema_json(title, meta_desc, slug, site_config, faq_items)

    # Intro hook
    intro_hook = article_data.get('intro_hook', '')
    intro_html = f'<p style="font-size:1.05em;line-height:1.7;color:#94a3b8;">{_esc(intro_hook)}</p>' if intro_hook else ''

    # Educational sections with tip boxes
    sections_html = ''
    for section in article_data.get('sections', []):
        heading = _esc(section.get('heading', ''))
        body_html = ''
        for p in section.get('body_paragraphs', []):
            body_html += f'<p style="color:#cbd5e1;line-height:1.7;margin:0 0 14px;">{_esc(p)}</p>\n'

        tip_box = ''
        tip_text = section.get('tip_box_text', '')
        if tip_text:
            tip_box = f'''
            <div style="background:#0c2d48;border-left:3px solid #0EA5E9;padding:14px 18px;margin:18px 0;border-radius:0 8px 8px 0;">
              <p style="margin:0;color:#0EA5E9;font-weight:600;font-size:0.88em;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">Pro Tip</p>
              <p style="margin:0;color:#e2e8f0;line-height:1.6;">{_esc(tip_text)}</p>
            </div>'''

        sections_html += f'''
        <section style="margin:32px 0;">
          <h2 style="font-family:'Space Grotesk',sans-serif;font-size:1.35em;color:#f1f5f9;margin:0 0 14px;">{heading}</h2>
          {body_html}
          {tip_box}
        </section>'''

    # Tool recommendations
    tools_html = ''
    tool_items = article_data.get('tool_recommendations', [])
    if tool_items:
        tool_cards = ''
        for item in tool_items:
            name = _esc(item.get('name', ''))
            price = _esc(item.get('price', ''))
            best_for = _esc(item.get('best_for', ''))
            note = _esc(item.get('one_line_note', ''))
            category = _esc(item.get('category', ''))
            aff_url = _esc(item.get('affiliate_url', '#'))

            tool_cards += f'''
            <div style="display:flex;gap:12px;align-items:center;padding:14px 0;border-bottom:1px solid #1e293b;">
              <div style="background:#0EA5E9;color:#fff;padding:6px 10px;border-radius:6px;font-size:0.75em;font-weight:600;text-transform:uppercase;white-space:nowrap;">{category}</div>
              <div style="flex:1;min-width:0;">
                <div style="font-weight:600;color:#f1f5f9;font-size:0.95em;">{name}</div>
                <div style="font-size:0.82em;color:#64748b;">{price} &middot; {best_for}</div>
                <div style="font-size:0.88em;color:#94a3b8;margin-top:2px;">{note}</div>
              </div>
              <a href="{aff_url}" target="_blank" rel="nofollow sponsored"
                 style="color:#0EA5E9;text-decoration:none;font-size:0.85em;white-space:nowrap;font-weight:500;">
                Try it &rarr;</a>
            </div>'''

        tools_html = f'''
        <section style="margin:40px 0;padding-top:28px;border-top:1px solid #1e293b;">
          <h2 style="font-family:'Space Grotesk',sans-serif;font-size:1.1em;color:#0EA5E9;margin:0 0 4px;">Recommended Tools</h2>
          <p style="color:#64748b;font-size:0.88em;margin:0 0 14px;">The tools mentioned in this article, with current pricing.</p>
          {tool_cards}
        </section>'''

    # FAQ
    faq_html = ''
    for faq in faq_items:
        faq_html += f'''
        <div style="margin:16px 0;">
          <h3 style="font-family:'Space Grotesk',sans-serif;font-size:1em;color:#f1f5f9;margin:0 0 6px;">{_esc(faq.get('q', ''))}</h3>
          <p style="color:#94a3b8;margin:0;line-height:1.6;">{_esc(faq.get('a', ''))}</p>
        </div>'''

    # Email signup
    signup_html = ''
    if form_id:
        signup_html = f'''
        <div style="background:#0c2d48;border:1px solid #1e293b;border-radius:10px;padding:22px;margin:32px 0;text-align:center;">
          <p style="font-family:'Space Grotesk',sans-serif;color:#0EA5E9;font-size:1em;margin:0 0 10px;">Free: Top 25 AI Tools Cheat Sheet (2026)</p>
          <script async data-uid="{form_id}" src="https://pilottools.ck.page/{form_id}/index.js"></script>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | PilotTools</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{_esc(site_config['base_url'])}/articles/{slug}.html">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
{schemas}
{"<script async src='https://www.googletagmanager.com/gtag/js?id=" + ga_id + "'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','" + ga_id + "')</script>" if ga_id else ''}
  <!-- AdSense -->
  <meta name="google-adsense-account" content="ca-pub-7018489366035978">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7018489366035978" crossorigin="anonymous"></script>
</head>
<body style="margin:0;padding:0;background:#0f172a;color:#f1f5f9;font-family:'Inter',sans-serif;line-height:1.7;">

<nav style="background:#020617;border-bottom:1px solid #1e293b;padding:14px 20px;">
  <div style="max-width:700px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;">
    <a href="../index.html" style="text-decoration:none;font-family:'Space Grotesk',sans-serif;font-size:1.15em;color:#f1f5f9;font-weight:600;">Pilot<span style="color:#0EA5E9;">Tools</span></a>
    <div style="display:flex;gap:16px;">
      <a href="../blog.html" style="text-decoration:none;color:#64748b;font-size:0.9em;">Articles</a>
      <a href="../about.html" style="text-decoration:none;color:#64748b;font-size:0.9em;">About</a>
    </div>
  </div>
</nav>

<main style="max-width:700px;margin:0 auto;padding:32px 20px;">
  <p style="font-size:0.82em;color:#475569;margin:0 0 8px;">{date_display}</p>
  <h1 style="font-family:'Space Grotesk',sans-serif;font-size:1.8em;line-height:1.3;margin:0 0 20px;color:#f1f5f9;">{title}</h1>

  <img src="{hero_url}" alt="{title}" style="width:100%;border-radius:10px;margin:0 0 24px;" loading="lazy">

  {intro_html}

  {sections_html}

  {tools_html}

  {f'<section style="margin:36px 0;"><h2 style="font-family:Space Grotesk,sans-serif;font-size:1.2em;color:#0EA5E9;margin:0 0 16px;">FAQ</h2>' + faq_html + '</section>' if faq_html else ''}

  {signup_html}

  {_cross_promo_section('pilottools')}
</main>

<footer style="border-top:1px solid #1e293b;padding:24px 20px;text-align:center;color:#475569;font-size:0.82em;">
  <p>&copy; {year} PilotTools. Some links may earn a commission.</p>
</footer>

</body>
</html>'''


# ═══════════════════════════════════════════════════════════════════════════
# HOMEDECOR — Warm cream/sage theme, room transformation, product-forward
# ═══════════════════════════════════════════════════════════════════════════

def _render_homedecor_article(article_data, site_config, slug):
    """Render a clean home decor article — warm palette, room-by-room transformation."""
    title = _esc(article_data.get('title', slug.replace('-', ' ').title()))
    meta_desc = _esc(article_data.get('meta_description', title))
    hero_url = _ensure_image(article_data.get('hero_url', ''), FALLBACK_HERO_IMAGES.get('homedecor', FALLBACK_HERO_IMAGES['default']))
    ga_id = _BRAND_GA_IDS.get('homedecor', '')
    form_id = _BRAND_FORM_IDS.get('homedecor', '')
    year = datetime.now(timezone.utc).year
    date_display = datetime.now(timezone.utc).strftime('%B %d, %Y')
    faq_items = article_data.get('faq', [])
    schemas = _build_schema_json(title, meta_desc, slug, site_config, faq_items)

    # Intro paragraphs (PAS framework like deals)
    intro_html = ''
    for p in article_data.get('intro_paragraphs', []):
        intro_html += f'<p>{_esc(p)}</p>\n'

    # Product cards
    products_html = ''
    for product in article_data.get('products', []):
        is_winner = product.get('is_winner', False)
        name = _esc(product.get('name', 'Product'))
        price = _esc(product.get('price', ''))
        rating = product.get('rating', 4.5)
        review_count = _esc(product.get('review_count', '1,000+'))
        review_text = _esc(product.get('personal_review_text', ''))
        section_heading = _esc(product.get('section_heading', name))
        amazon_url = _esc(product.get('amazon_url', '#'))
        product_img = _esc(product.get('product_image', ''))

        winner_border = 'border: 2px solid #6B705C;' if is_winner else 'border: 1px solid #e8dcc8;'
        winner_label = '<span style="display:inline-block;background:#6B705C;color:#fff;font-size:0.78em;padding:3px 12px;border-radius:4px;margin-bottom:10px;font-weight:600;">Editor\'s Pick</span>' if is_winner else ''

        img_block = ''
        if product_img:
            img_block = (
                f'<a href="{amazon_url}" target="_blank" rel="nofollow sponsored" style="flex-shrink:0;">'
                f'<img src="{product_img}" alt="{name}" width="100" height="100" '
                f'style="object-fit:contain;border-radius:8px;background:#fff;padding:4px;" loading="lazy" '
                f'onerror="this.parentElement.style.display=\'none\'"></a>'
            )

        products_html += f'''
        <div style="{winner_border}border-radius:12px;padding:20px;margin:24px 0;background:#fff;">
          {winner_label}
          <h2 style="font-family:'DM Serif Display',serif;font-size:1.3em;margin:0 0 8px;color:#3a3a3a;">{section_heading}</h2>
          <div style="display:flex;gap:16px;align-items:flex-start;margin:12px 0;">
            {img_block}
            <div>
              <div style="font-size:0.9em;color:#8B7355;margin-bottom:6px;">{_star_html(rating)} &middot; {review_count} reviews &middot; {price}</div>
              <p style="margin:0;color:#555;line-height:1.6;">{review_text}</p>
            </div>
          </div>
          <a href="{amazon_url}" target="_blank" rel="nofollow sponsored"
             style="display:inline-block;background:#6B705C;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none;font-weight:600;font-size:0.95em;margin-top:12px;">
            See it on Amazon &rarr;</a>
        </div>'''

    # Verdict
    verdict_html = ''
    verdict_text = article_data.get('verdict_text', '')
    if verdict_text:
        verdict_html = f'''
        <div style="border-left:3px solid #A5A58D;padding:16px 20px;margin:28px 0;background:#f5f0e8;border-radius:0 8px 8px 0;">
          <p style="margin:0;font-family:'DM Serif Display',serif;font-style:italic;color:#3a3a3a;line-height:1.6;">{_esc(verdict_text)}</p>
        </div>'''

    # FAQ
    faq_html = ''
    for faq in faq_items:
        faq_html += f'''
        <div style="margin:16px 0;">
          <h3 style="font-family:'DM Serif Display',serif;font-size:1.05em;color:#3a3a3a;margin:0 0 6px;">{_esc(faq.get('q', ''))}</h3>
          <p style="color:#666;margin:0;line-height:1.6;">{_esc(faq.get('a', ''))}</p>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Home Decor Edit</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{_esc(site_config['base_url'])}/articles/{slug}.html">
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
{schemas}
{"<script async src='https://www.googletagmanager.com/gtag/js?id=" + ga_id + "'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','" + ga_id + "')</script>" if ga_id else ''}
  <!-- AdSense -->
  <meta name="google-adsense-account" content="ca-pub-7018489366035978">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7018489366035978" crossorigin="anonymous"></script>
</head>
<body style="margin:0;padding:0;background:#FAF7F0;color:#3a3a3a;font-family:'Outfit',sans-serif;line-height:1.7;">

<nav style="background:#fff;border-bottom:1px solid #e8dcc8;padding:14px 20px;">
  <div style="max-width:680px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;">
    <a href="../index.html" style="text-decoration:none;font-family:'DM Serif Display',serif;font-size:1.15em;color:#3a3a3a;">Home Decor <span style="color:#6B705C;">Edit</span></a>
    <a href="./" style="text-decoration:none;color:#8B7355;font-size:0.9em;">All Articles</a>
  </div>
</nav>

<main style="max-width:680px;margin:0 auto;padding:32px 20px;">
  <p style="font-size:0.82em;color:#A5A58D;margin:0 0 8px;">{date_display}</p>
  <h1 style="font-family:'DM Serif Display',serif;font-size:1.8em;line-height:1.3;margin:0 0 20px;color:#3a3a3a;">{title}</h1>

  <img src="{hero_url}" alt="{title}" style="width:100%;border-radius:10px;margin:0 0 24px;" loading="lazy">

  {intro_html}

  {products_html}

  {verdict_html}

  {f'<h2 style="font-family:DM Serif Display,serif;margin:36px 0 16px;">FAQ</h2>' + faq_html if faq_html else ''}

  {_cross_promo_section('homedecor')}
</main>

<footer style="border-top:1px solid #e8dcc8;padding:24px 20px;text-align:center;color:#A5A58D;font-size:0.82em;">
  <p>&copy; {year} Home Decor Edit. Affiliate links may earn a commission.</p>
</footer>

</body>
</html>'''


# ═══════════════════════════════════════════════════════════════════════════
# BEAUTY — Soft pink/rose theme, personal review style, product-forward
# ═══════════════════════════════════════════════════════════════════════════

def _render_beauty_article(article_data, site_config, slug):
    """Render a clean beauty article — soft pink theme, honest product reviews."""
    title = _esc(article_data.get('title', slug.replace('-', ' ').title()))
    meta_desc = _esc(article_data.get('meta_description', title))
    hero_url = _ensure_image(article_data.get('hero_url', ''), FALLBACK_HERO_IMAGES.get('beauty', FALLBACK_HERO_IMAGES['default']))
    ga_id = _BRAND_GA_IDS.get('beauty', '')
    form_id = _BRAND_FORM_IDS.get('beauty', '')
    year = datetime.now(timezone.utc).year
    date_display = datetime.now(timezone.utc).strftime('%B %d, %Y')
    faq_items = article_data.get('faq', [])
    schemas = _build_schema_json(title, meta_desc, slug, site_config, faq_items)

    # Intro paragraphs (PAS framework)
    intro_html = ''
    for p in article_data.get('intro_paragraphs', []):
        intro_html += f'<p>{_esc(p)}</p>\n'

    # Product cards
    products_html = ''
    for product in article_data.get('products', []):
        is_winner = product.get('is_winner', False)
        name = _esc(product.get('name', 'Product'))
        price = _esc(product.get('price', ''))
        rating = product.get('rating', 4.5)
        review_count = _esc(product.get('review_count', '1,000+'))
        review_text = _esc(product.get('personal_review_text', ''))
        section_heading = _esc(product.get('section_heading', name))
        amazon_url = _esc(product.get('amazon_url', '#'))
        product_img = _esc(product.get('product_image', ''))

        winner_border = 'border: 2px solid #D4A0A0;' if is_winner else 'border: 1px solid #f0e0e0;'
        winner_label = '<span style="display:inline-block;background:#D4A0A0;color:#fff;font-size:0.78em;padding:3px 12px;border-radius:4px;margin-bottom:10px;font-weight:600;">My Top Pick</span>' if is_winner else ''

        img_block = ''
        if product_img:
            img_block = (
                f'<a href="{amazon_url}" target="_blank" rel="nofollow sponsored" style="flex-shrink:0;">'
                f'<img src="{product_img}" alt="{name}" width="100" height="100" '
                f'style="object-fit:contain;border-radius:8px;background:#fff;padding:4px;" loading="lazy" '
                f'onerror="this.parentElement.style.display=\'none\'"></a>'
            )

        products_html += f'''
        <div style="{winner_border}border-radius:12px;padding:20px;margin:24px 0;background:#fff;">
          {winner_label}
          <h2 style="font-family:'Lora',serif;font-size:1.3em;margin:0 0 8px;color:#3a3a3a;">{section_heading}</h2>
          <div style="display:flex;gap:16px;align-items:flex-start;margin:12px 0;">
            {img_block}
            <div>
              <div style="font-size:0.9em;color:#b08080;margin-bottom:6px;">{_star_html(rating)} &middot; {review_count} reviews &middot; {price}</div>
              <p style="margin:0;color:#555;line-height:1.6;">{review_text}</p>
            </div>
          </div>
          <a href="{amazon_url}" target="_blank" rel="nofollow sponsored"
             style="display:inline-block;background:#D4A0A0;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none;font-weight:600;font-size:0.95em;margin-top:12px;">
            See it on Amazon &rarr;</a>
        </div>'''

    # Verdict
    verdict_html = ''
    verdict_text = article_data.get('verdict_text', '')
    if verdict_text:
        verdict_html = f'''
        <div style="border-left:3px solid #D4A0A0;padding:16px 20px;margin:28px 0;background:#fdf5f5;border-radius:0 8px 8px 0;">
          <p style="margin:0;font-family:'Lora',serif;font-style:italic;color:#3a3a3a;line-height:1.6;">{_esc(verdict_text)}</p>
        </div>'''

    # FAQ
    faq_html = ''
    for faq in faq_items:
        faq_html += f'''
        <div style="margin:16px 0;">
          <h3 style="font-family:'Lora',serif;font-size:1.05em;color:#3a3a3a;margin:0 0 6px;">{_esc(faq.get('q', ''))}</h3>
          <p style="color:#666;margin:0;line-height:1.6;">{_esc(faq.get('a', ''))}</p>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | The Beauty Shelf</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{_esc(site_config['base_url'])}/articles/{slug}.html">
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
{schemas}
{"<script async src='https://www.googletagmanager.com/gtag/js?id=" + ga_id + "'></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','" + ga_id + "')</script>" if ga_id else ''}
  <!-- AdSense -->
  <meta name="google-adsense-account" content="ca-pub-7018489366035978">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7018489366035978" crossorigin="anonymous"></script>
</head>
<body style="margin:0;padding:0;background:#FFF5F5;color:#3a3a3a;font-family:'Inter',sans-serif;line-height:1.7;">

<nav style="background:#fff;border-bottom:1px solid #f0e0e0;padding:14px 20px;">
  <div style="max-width:680px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;">
    <a href="../index.html" style="text-decoration:none;font-family:'Lora',serif;font-size:1.15em;color:#3a3a3a;font-weight:600;">The Beauty <span style="color:#D4A0A0;">Shelf</span></a>
    <a href="./" style="text-decoration:none;color:#b08080;font-size:0.9em;">All Articles</a>
  </div>
</nav>

<main style="max-width:680px;margin:0 auto;padding:32px 20px;">
  <p style="font-size:0.82em;color:#b08080;margin:0 0 8px;">{date_display}</p>
  <h1 style="font-family:'Lora',serif;font-size:1.8em;line-height:1.3;margin:0 0 20px;color:#3a3a3a;">{title}</h1>

  <img src="{hero_url}" alt="{title}" style="width:100%;border-radius:10px;margin:0 0 24px;" loading="lazy">

  {intro_html}

  {products_html}

  {verdict_html}

  {f'<h2 style="font-family:Lora,serif;margin:36px 0 16px;">FAQ</h2>' + faq_html if faq_html else ''}

  {_cross_promo_section('beauty')}
</main>

<footer style="border-top:1px solid #f0e0e0;padding:24px 20px;text-align:center;color:#b08080;font-size:0.82em;">
  <p>&copy; {year} The Beauty Shelf. Affiliate links may earn a commission.</p>
</footer>

</body>
</html>'''


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API — dispatcher
# ═══════════════════════════════════════════════════════════════════════════

def render_clean_article(brand_key, article_data, site_config, slug):
    """Render a complete article page using the brand-specific clean template.

    This is the main entry point. Dispatches to the correct brand builder.
    """
    renderers = {
        'deals': _render_deals_article,
        'fitness': _render_fitness_article,
        'menopause': _render_menopause_article,
        'pilottools': _render_pilottools_article,
        'homedecor': _render_homedecor_article,
        'beauty': _render_beauty_article,
    }
    renderer = renderers.get(brand_key, _render_deals_article)
    return renderer(article_data, site_config, slug)


# ═══════════════════════════════════════════════════════════════════════════
# LEGACY COMPATIBILITY — keep render_article_from_template working
# for any code that still calls it (article_templates.py, etc.)
# ═══════════════════════════════════════════════════════════════════════════

# Old BRAND_THEMES kept for any imports
BRAND_THEMES = {
    'fitness': {
        'heading_font': 'Space Grotesk', 'body_font': 'Inter',
        'font_import': 'Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700',
        'colors': {'bg': '#111', 'surface': '#1a1a1a', 'border': '#333',
                   'accent': '#E8C547', 'accent_light': '#1a1a0a', 'text': '#fff',
                   'muted': '#888', 'warm': '#1a1a0a'},
        'expert_name': 'Talhah Bilal', 'expert_initials': 'TB',
        'expert_credentials': 'ISSA-CPT', 'expert_bio': '',
        'site_tagline': 'Expert Verified', 'cta_text': 'See on Amazon',
    },
    'menopause': {
        'heading_font': 'DM Serif Display', 'body_font': 'Outfit',
        'font_import': 'DM+Serif+Display&family=Outfit:wght@400;500;600;700',
        'colors': {'bg': '#FAF7F0', 'surface': '#fff', 'border': '#e8dcc8',
                   'accent': '#6B705C', 'accent_light': '#f0ebe3', 'text': '#3a3a3a',
                   'muted': '#8B7355', 'warm': '#f5ede0'},
        'expert_name': 'The Menopause Planner Team', 'expert_initials': 'MP',
        'expert_credentials': 'Wellness Guide', 'expert_bio': '',
        'site_tagline': 'Wellness Guide', 'cta_text': 'See on Amazon',
    },
    'deals': {
        'heading_font': 'Lora', 'body_font': 'Inter',
        'font_import': 'Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@400;500;600;700',
        'colors': {'bg': '#FAFAFA', 'surface': '#fff', 'border': '#e5e7eb',
                   'accent': '#C47D8E', 'accent_light': '#fdf5f7', 'text': '#2D2D2D',
                   'muted': '#999', 'warm': '#fdf5f7'},
        'expert_name': 'Daily Deal Darling Team', 'expert_initials': 'DD',
        'expert_credentials': 'Product Tested', 'expert_bio': '',
        'site_tagline': 'Product Tested', 'cta_text': 'See it on Amazon',
    },
    'pilottools': {
        'heading_font': 'Space Grotesk', 'body_font': 'Inter',
        'font_import': 'Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700',
        'colors': {'bg': '#0f172a', 'surface': '#1e293b', 'border': '#334155',
                   'accent': '#0EA5E9', 'accent_light': '#0c2d48', 'text': '#f1f5f9',
                   'muted': '#64748b', 'warm': '#0c2d48'},
        'expert_name': 'PilotTools Team', 'expert_initials': 'PT',
        'expert_credentials': 'AI Tools Expert', 'expert_bio': '',
        'site_tagline': 'AI Tools Expert', 'cta_text': 'Try it',
    },
    'homedecor': {
        'heading_font': 'DM Serif Display', 'body_font': 'Outfit',
        'font_import': 'DM+Serif+Display&family=Outfit:wght@400;500;600;700',
        'colors': {'bg': '#FAF7F0', 'surface': '#fff', 'border': '#e8dcc8',
                   'accent': '#6B705C', 'accent_light': '#f5f0e8', 'text': '#3a3a3a',
                   'muted': '#8B7355', 'warm': '#f5ede0'},
        'expert_name': 'Home Decor Edit Team', 'expert_initials': 'HD',
        'expert_credentials': 'Design Tested', 'expert_bio': '',
        'site_tagline': 'Design Tested', 'cta_text': 'See it on Amazon',
    },
    'beauty': {
        'heading_font': 'Lora', 'body_font': 'Inter',
        'font_import': 'Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@400;500;600;700',
        'colors': {'bg': '#FFF5F5', 'surface': '#fff', 'border': '#f0e0e0',
                   'accent': '#D4A0A0', 'accent_light': '#fdf5f5', 'text': '#3a3a3a',
                   'muted': '#b08080', 'warm': '#fdf5f5'},
        'expert_name': 'The Beauty Shelf Team', 'expert_initials': 'BS',
        'expert_credentials': 'Product Tested', 'expert_bio': '',
        'site_tagline': 'Product Tested', 'cta_text': 'See it on Amazon',
    },
}

FALLBACK_FACES = {
    'fitness': [''] * 4, 'menopause': [''] * 4, 'deals': [''] * 4,
}
FALLBACK_PRODUCT_IMAGES = {
    'fitness': FALLBACK_HERO_IMAGES['fitness'],
    'menopause': FALLBACK_HERO_IMAGES['menopause'],
    'deals': FALLBACK_HERO_IMAGES['deals'],
    'default': FALLBACK_HERO_IMAGES['default'],
}


def render_article_from_template(brand_key, article_data, site_config, slug):
    """Legacy compatibility wrapper — routes to the new clean renderer."""
    return render_clean_article(brand_key, article_data, site_config, slug)
