"""Brand-specific bridge page templates for high-converting Amazon affiliate articles.

Three mobile-first templates optimized for Pinterest traffic and Google Search:
- 'The Iron Standard' (fitness) — Dark, gritty, data-heavy
- 'The Wellness Whisper' (menopause) — Clean, empathetic, editorial
- 'The Aesthetic Edit' (deals) — Minimalist, boutique, magazine-style

All use Tailwind CSS (CDN), Schema.org JSON-LD (Article + Product + FAQPage),
expert reviewer bios, geo-SEO, product cards, comparison tables,
and mobile-first sticky CTAs.

V3 Template System: Structured article data rendering with 22-section layout.
"""

import json
import re
from datetime import datetime, timezone


# ── Template configuration per brand ───────────────────────────────────────

TEMPLATE_CONFIG = {
    'fitness': {
        'name': 'The Iron Standard',
        'tagline': 'Expert Verified',
        'font_import': 'family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=Oswald:wght@400;500;600;700&family=Inter:wght@400;500;600;700',
        'heading_font': 'Fraunces',
        'body_font': 'Inter',
        'colors': {
            'bg': '#0A0A0A', 'surface': '#111111', 'border': '#2A2A2A',
            'accent': '#CCFF00', 'text': '#FFFFFF', 'muted': '#999999',
        },
        'expert': {
            'name': 'Talhah Bilal',
            'credentials': 'NASM-CPT &middot; Kinesiology Degree',
            'bio': ('Reviewed by Talhah Bilal, a Kinesiology degree holder, '
                    'NASM-certified personal trainer, and competitive bodybuilder '
                    'with over a decade of experience in physique transformation.'),
            'initials': 'TB',
            'bg': '#CCFF00',
            'text_color': '#000000',
        },
        'cta_text': 'Check Current Price on Amazon',
        'cta_bg': '#CCFF00',
        'cta_text_color': '#000000',
    },
    'menopause': {
        'name': 'The Wellness Whisper',
        'tagline': 'Wellness Guide',
        'font_import': 'family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@400;500;600;700',
        'heading_font': 'Fraunces',
        'body_font': 'Inter',
        'colors': {
            'bg': '#FDFBF7', 'surface': '#FFFFFF', 'border': '#D2C4A8',
            'accent': '#3D6B4F', 'text': '#4A4A4A', 'muted': '#8B7355',
        },
        'expert': {
            'name': 'Editorial Team',
            'credentials': 'The Menopause Planner',
            'bio': ("Reviewed by our editorial team in consultation with certified "
                    "women's health practitioners and menopause specialists."),
            'initials': 'MP',
            'bg': '#3D6B4F',
            'text_color': '#FFFFFF',
        },
        'cta_text': "View Today's Amazon Deal",
        'cta_bg': '#3D6B4F',
        'cta_text_color': '#FFFFFF',
    },
    'deals': {
        'name': 'The Aesthetic Edit',
        'tagline': 'Trending on Pinterest',
        'font_import': 'family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@400;500;600;700',
        'heading_font': 'Fraunces',
        'body_font': 'Inter',
        'colors': {
            'bg': '#FAF9F6', 'surface': '#FFFFFF', 'border': '#E5E5E5',
            'accent': '#D4AF37', 'text': '#1A1A1A', 'muted': '#6B6B6B',
        },
        'expert': {
            'name': 'Deal Curators',
            'credentials': 'Daily Deal Darling',
            'bio': ('Curated by the Daily Deal Darling editorial team — we test, '
                    'compare, and only recommend products that deliver real value.'),
            'initials': 'DD',
            'bg': '#D4AF37',
            'text_color': '#000000',
        },
        'cta_text': 'Buy on Amazon',
        'cta_bg': '#D4AF37',
        'cta_text_color': '#000000',
    },
}

# Brand-specific lead magnet overrides for signup forms
LEAD_MAGNET_OVERRIDES = {
    'fitness': 'Free: 7-Day Fat Burn Kickstart Plan (PDF)',
    'deals': "Free: This Week's Top 10 Deals (Newsletter)",
    'menopause': 'Free: Night Sweat Symptom Tracker (Printable PDF)',
}

# Brand affiliate tags
_BRAND_TAGS = {
    'fitness': 'dailydealdarling1-20',
    'deals': 'dailydealdarling1-20',
    'menopause': 'dailydealdarling1-20',
}


# ── Shared helpers ─────────────────────────────────────────────────────────

def _get_brand_tag(brand_key):
    """Get Amazon affiliate tag for a brand."""
    return _BRAND_TAGS.get(brand_key, 'dailydealdarling1-20')


def _find_first_amazon_url(body_html):
    """Extract first Amazon affiliate URL from body HTML."""
    m = re.search(r'href="(https://www\.amazon\.com[^"]*)"', body_html)
    return m.group(1) if m else None


def _build_article_schema(title, meta_desc, slug, site_config, expert_name):
    """Build Article Schema.org JSON-LD."""
    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    url = site_config['base_url'] + '/articles/' + slug + '.html'
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "datePublished": date_str,
        "dateModified": date_str,
        "url": url,
        "author": {"@type": "Person", "name": expert_name},
        "publisher": {"@type": "Organization", "name": site_config['site_name']},
        "description": meta_desc,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }, indent=2)


def _build_product_schema(title, amazon_url):
    """Build Product Schema.org JSON-LD."""
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": title,
        "offers": {
            "@type": "Offer",
            "url": amazon_url,
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
        },
    }, indent=2)


GEO_SCRIPT = (
    '<script>(function(){var e=document.getElementById("geo-loc");'
    'if(!e)return;fetch("https://ipapi.co/json/")'
    '.then(function(r){return r.json()})'
    '.then(function(d){if(d.city)e.textContent=d.city+", "+(d.region||d.country_name)})'
    '.catch(function(){})})()</script>'
)

ETSY_CTA_HTML = (
    '<div style="background:linear-gradient(135deg,#f3e8ff,#ede0f7);border:2px solid #c084fc;'
    'border-radius:14px;padding:28px;margin:36px 0;text-align:center;">'
    '<p style="font-size:0.8em;font-weight:700;letter-spacing:0.08em;color:#7B1FA2;'
    'text-transform:uppercase;margin:0 0 8px">The Menopause Planner &mdash; Digital Download</p>'
    '<h3 style="margin:0 0 10px;font-size:1.3em;color:#111">Track Every Symptom. Reclaim Your Sleep.</h3>'
    '<p style="margin:0 0 18px;color:#444;font-size:0.97em">A printable digital planner built '
    'specifically for women navigating menopause &mdash; track symptoms, sleep patterns, supplements, '
    'and mood in one place.</p>'
    '<a href="https://www.etsy.com/listing/4435219468/menopause-wellness-planner-bundle'
    '?utm_source=Pinterest&amp;utm_medium=organic" target="_blank" rel="noopener" '
    'style="display:inline-block;background:#7B1FA2;color:#fff;padding:12px 28px;border-radius:8px;'
    'text-decoration:none;font-weight:700;font-size:1em">Get the Planner on Etsy &rarr;</a>'
    '<p style="margin:12px 0 0;font-size:0.82em;color:#777">Instant download &bull; Print at home '
    '&bull; One-time purchase</p></div>'
)


# ── Product card parsing and rendering ────────────────────────────────────

def _replace_product_cards(body_html, tpl):
    """Parse <!--PRODUCT_CARD: ...--> comments and replace with styled HTML cards.

    Returns (modified_body_html, list_of_card_dicts).
    """
    cards = []
    pattern = (
        r'(?:<p>\s*)?'
        r'<!--PRODUCT_CARD:\s*'
        r'name="([^"]*?)"\s*\|\s*'
        r'url="([^"]*?)"\s*\|\s*'
        r'rating="([^"]*?)"\s*\|\s*'
        r'reviews="([^"]*?)"\s*\|\s*'
        r'price_range="([^"]*?)"\s*\|\s*'
        r'badge="([^"]*?)"\s*'
        r'-->'
        r'(?:\s*</p>)?'
    )

    def _replacer(m):
        card = {
            'name': m.group(1),
            'url': m.group(2),
            'rating': m.group(3),
            'reviews': m.group(4),
            'price_range': m.group(5),
            'badge': m.group(6),
        }
        cards.append(card)
        return _render_product_card_html(card, tpl)

    body_html = re.sub(pattern, _replacer, body_html)
    return body_html, cards


def _render_product_card_html(card, tpl):
    """Render a single product card as styled HTML."""
    c = tpl['colors']
    return (
        f'<div class="product-card" style="border:2px solid {c["accent"]};border-radius:12px;'
        f'padding:20px;margin:24px 0;background:{c["surface"]};">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">'
        f'<span style="background:{c["accent"]};color:{tpl["cta_text_color"]};padding:4px 12px;'
        f'border-radius:20px;font-size:0.8em;font-weight:700;">{card["badge"]}</span>'
        f'<span style="color:{c["muted"]};font-size:0.85em;">'
        f'\u2b50 {card["rating"]} ({card["reviews"]} reviews)</span></div>'
        f'<h3 style="margin:0 0 8px;font-size:1.3em;">{card["name"]}</h3>'
        f'<p style="color:{c["muted"]};margin:0 0 16px;font-size:0.9em;">'
        f'Typical price: {card["price_range"]}</p>'
        f'<a href="{card["url"]}" target="_blank" rel="nofollow sponsored noopener" '
        f'style="display:block;text-align:center;background:{tpl["cta_bg"]};'
        f'color:{tpl["cta_text_color"]};padding:14px 24px;border-radius:8px;'
        f'text-decoration:none;font-weight:700;font-size:1.05em;">'
        f'Check Current Price on Amazon \u2192</a></div>'
    )


def _render_quick_picks_box(cards, tpl):
    """Render a summary box with the first 3 product picks."""
    if not cards:
        return ''
    c = tpl['colors']
    picks_html = ''
    for card in cards[:3]:
        picks_html += (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:10px 0;border-bottom:1px solid {c["border"]};">'
            f'<div><span style="font-weight:700;font-size:0.85em;margin-right:8px;">'
            f'{card["badge"]}</span>'
            f'<span style="font-size:0.95em;">{card["name"]}</span></div>'
            f'<a href="{card["url"]}" target="_blank" rel="nofollow sponsored noopener" '
            f'style="background:{tpl["cta_bg"]};color:{tpl["cta_text_color"]};'
            f'padding:6px 14px;border-radius:6px;text-decoration:none;font-weight:600;'
            f'font-size:0.85em;white-space:nowrap;">Check Price</a></div>'
        )
    return (
        f'<div style="border:2px solid {c["accent"]};border-radius:12px;padding:20px;'
        f'margin:24px 0;background:{c["surface"]};">'
        f'<h3 style="margin:0 0 12px;font-size:1.1em;">\U0001f3af Quick Picks</h3>'
        f'{picks_html}</div>'
    )


# ── FAQ parsing and schema ────────────────────────────────────────────────

def _parse_faq_pairs(body_html):
    """Extract Q&A pairs from HTML body.

    Expects format: <p><strong>Q: question?</strong></p> followed by <p>A: answer</p>
    """
    pairs = []
    pattern = r'<p><strong>Q:\s*(.+?)</strong></p>\s*<p>A:\s*(.+?)</p>'
    for m in re.finditer(pattern, body_html):
        question = m.group(1).strip().rstrip('?') + '?'
        answer = re.sub(r'<[^>]+>', '', m.group(2).strip())  # strip inner HTML tags
        pairs.append((question, answer))
    return pairs


def _build_faq_schema(faq_pairs):
    """Build FAQPage Schema.org JSON-LD."""
    if not faq_pairs:
        return ''
    entries = []
    for q, a in faq_pairs:
        entries.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {
                "@type": "Answer",
                "text": a,
            },
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entries,
    }
    return f'<script type="application/ld+json">{json.dumps(schema, indent=2)}</script>'


# ── Mobile sticky CTA ────────────────────────────────────────────────────

def _render_mobile_sticky_cta(top_pick, tpl):
    """Build mobile-only sticky bottom CTA bar for the top-pick product."""
    if not top_pick:
        return ''
    c = tpl['colors']
    return (
        f'<style>.sticky-cta{{display:none}}'
        f'@media(max-width:768px){{.sticky-cta{{display:flex}}}}</style>'
        f'<div class="sticky-cta" style="position:fixed;bottom:0;left:0;right:0;'
        f'background:{c["surface"]};border-top:2px solid {c["accent"]};padding:12px 16px;'
        f'z-index:1000;align-items:center;justify-content:space-between;">'
        f'<div><strong style="font-size:0.9em;">{top_pick["name"]}</strong>'
        f'<span style="color:{c["muted"]};font-size:0.8em;display:block;">'
        f'{top_pick["price_range"]}</span></div>'
        f'<a href="{top_pick["url"]}" target="_blank" rel="nofollow sponsored noopener" '
        f'style="background:{tpl["cta_bg"]};color:{tpl["cta_text_color"]};'
        f'padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:700;'
        f'font-size:0.9em;white-space:nowrap;">Check Price \u2192</a></div>'
    )


def _fallback_sticky_cta(tpl, cta_url):
    """Build generic sticky bottom CTA bar (fallback when no product cards)."""
    return (
        f'<div style="position:fixed;bottom:0;left:0;right:0;background:{tpl["cta_bg"]};'
        f'z-index:50;box-shadow:0 -2px 10px rgba(0,0,0,0.15)">'
        f'<a href="{cta_url}" target="_blank" rel="nofollow sponsored" '
        f'style="display:block;text-align:center;color:{tpl["cta_text_color"]};'
        f'font-weight:700;font-size:1.05em;padding:14px 16px;text-decoration:none">'
        f'{tpl["cta_text"]} &rarr;</a></div>'
    )


# ── Signup form ───────────────────────────────────────────────────────────

def _signup_form(site_config, tpl, brand_key='deals'):
    """Build email signup form matching brand template."""
    c = tpl['colors']
    lead_magnet = LEAD_MAGNET_OVERRIDES.get(brand_key, site_config['lead_magnet'])
    return (
        '<div style="background:{bg};border:1px solid {border};border-radius:12px;'
        'padding:24px;margin:32px 0;text-align:center">'
        '<h3 style="margin:0 0 8px;color:{heading}">{lead}</h3>'
        '<p style="margin:0 0 16px;color:{muted};font-size:0.95em">'
        'Join our community for weekly tips and guides.</p>'
        '<script src="https://f.convertkit.com/ckjs/ck.5.js"></script>'
        '<form action="https://app.kit.com/forms/{form_id}/subscriptions" method="post" '
        'data-sv-form="{form_id}" style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center">'
        '<input type="email" name="email_address" placeholder="Enter your email" required '
        'style="padding:12px 16px;border:1px solid {border};border-radius:8px;'
        'width:100%;max-width:300px;font-size:1em;background:{input_bg};color:{input_text}">'
        '<button type="submit" style="padding:12px 24px;background:{accent};color:{btn_text};'
        'border:none;border-radius:8px;cursor:pointer;font-weight:700;font-size:1em">'
        '{btn}</button></form></div>'
    ).format(
        bg=c['surface'], border=c['border'], heading=c.get('text', '#111'),
        muted=c['muted'], accent=c['accent'], lead=lead_magnet,
        form_id=site_config['signup_form_id'], btn=site_config['signup_button_text'],
        btn_text=tpl['cta_text_color'],
        input_bg='#1A1A1A' if c['bg'] == '#0A0A0A' else '#FFFFFF',
        input_text=c['text'],
    )


# ── Main dispatcher ────────────────────────────────────────────────────────

def render_article_page(brand_key, title, meta_desc, body_html, hero_url,
                        site_config, slug, pin_data=None):
    """Render a complete bridge-page HTML for the given brand.

    Replaces the old article_to_html page wrapper. body_html should already
    have inline product cards injected and inline formatting applied. The
    <!-- email-signup-placeholder --> will be replaced with a brand-styled form.
    <!--PRODUCT_CARD: ...--> comments will be replaced with visual product cards.

    Routes to v3 template if structured article data is available in pin_data.
    """
    # Route to v3 template if structured data available
    article_data = (pin_data or {}).get('_article_data')
    if article_data:
        return _render_v3_page(brand_key, article_data, site_config, slug)

    # Fallback: use v2 markdown-based templates
    tpl = TEMPLATE_CONFIG.get(brand_key, TEMPLATE_CONFIG['deals'])

    # Parse and render PRODUCT_CARD comments into styled HTML cards
    body_html, product_cards = _replace_product_cards(body_html, tpl)

    # Insert quick picks summary box before first <h2>
    if product_cards:
        quick_picks = _render_quick_picks_box(product_cards[:3], tpl)
        first_h2_pos = body_html.find('<h2')
        if first_h2_pos != -1:
            body_html = body_html[:first_h2_pos] + quick_picks + body_html[first_h2_pos:]
        else:
            # No <h2> found — insert after first closing paragraph
            first_p_end = body_html.find('</p>')
            if first_p_end != -1:
                body_html = body_html[:first_p_end + 4] + quick_picks + body_html[first_p_end + 4:]

    # Parse FAQ pairs and build schema
    faq_pairs = _parse_faq_pairs(body_html)
    faq_schema_tag = _build_faq_schema(faq_pairs)

    first_amazon = _find_first_amazon_url(body_html)
    article_schema = _build_article_schema(
        title, meta_desc, slug, site_config, tpl['expert']['name'])
    product_schema_tag = ''
    if first_amazon:
        product_schema_tag = (
            '<script type="application/ld+json">'
            + _build_product_schema(title, first_amazon)
            + '</script>'
        )

    date_str = datetime.now(timezone.utc).strftime('%B %d, %Y')
    article_url = site_config['base_url'] + '/articles/' + slug + '.html'
    affiliate_tag = _get_brand_tag(brand_key)
    cta_url = first_amazon or (
        'https://www.amazon.com/s?k=' + slug.replace('-', '+')
        + '&tag=' + affiliate_tag
    )

    # Replace email signup placeholder with brand-styled form
    form_html = _signup_form(site_config, tpl, brand_key)
    body_html = body_html.replace('<!-- email-signup-placeholder -->', form_html)

    # Append Etsy CTA for menopause brand
    if brand_key == 'menopause':
        body_html += ETSY_CTA_HTML

    # Build mobile sticky CTA for top-pick product
    top_pick = product_cards[0] if product_cards else None
    mobile_sticky_html = _render_mobile_sticky_cta(top_pick, tpl)

    # Dispatch to brand template
    ctx = dict(
        tpl=tpl, title=title, meta_desc=meta_desc, body_html=body_html,
        hero_url=hero_url, site_config=site_config, slug=slug,
        date_str=date_str, article_url=article_url, cta_url=cta_url,
        article_schema=article_schema, product_schema_tag=product_schema_tag,
        faq_schema_tag=faq_schema_tag, mobile_sticky_html=mobile_sticky_html,
    )
    if brand_key == 'fitness':
        return _render_iron_standard(**ctx)
    elif brand_key == 'menopause':
        return _render_wellness_whisper(**ctx)
    return _render_aesthetic_edit(**ctx)


# ── Shared page parts ──────────────────────────────────────────────────────

def _head(tpl, title, meta_desc, article_url, site_config, article_schema,
          product_schema_tag, article_css, faq_schema_tag=''):
    """Build <head> section shared across all templates."""
    c = tpl['colors']
    tw_config = json.dumps({
        "theme": {"extend": {"colors": {
            "brand": c['accent'], "surface": c['surface'], "dark": c['bg'],
        }}}
    })
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '  <meta charset="UTF-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'  <meta name="description" content="{_esc(meta_desc)}">\n'
        f'  <meta name="author" content="{_esc(site_config["site_name"])}">\n'
        '  <meta name="robots" content="index, follow">\n'
        '  <meta property="og:type" content="article">\n'
        f'  <meta property="og:url" content="{article_url}">\n'
        f'  <meta property="og:title" content="{_esc(title)}">\n'
        f'  <meta property="og:description" content="{_esc(meta_desc[:160])}">\n'
        f'  <title>{_esc(title)} | {site_config["site_name"]} '
        '&mdash; Best of 2026, Expert Verified</title>\n'
        '  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'  <link href="https://fonts.googleapis.com/css2?{tpl["font_import"]}'
        '&display=swap" rel="stylesheet">\n'
        '  <script src="https://cdn.tailwindcss.com"></script>\n'
        f'  <script>tailwind.config = {tw_config}</script>\n'
        '  <!-- Google Analytics: Replace G-XXXXXXX with your tracking ID -->\n'
        '  <!-- <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX">'
        '</script> -->\n'
        '  <!-- Facebook Pixel: Replace XXXXXXX with your Pixel ID -->\n'
        '  <!-- <noscript><img height="1" width="1" style="display:none" '
        'src="https://www.facebook.com/tr?id=XXXXXXX&ev=PageView&noscript=1"/>'
        '</noscript> -->\n'
        f'  <script type="application/ld+json">{article_schema}</script>\n'
        f'  {product_schema_tag}\n'
        f'  {faq_schema_tag}\n'
        f'  <style>{article_css}</style>\n'
        '</head>\n'
    )


def _esc(text):
    """Escape HTML special characters in attribute values."""
    return (text or '').replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')


def _nav(tpl, site_config, dark=False):
    """Build navigation bar."""
    c = tpl['colors']
    link_color = c['muted'] if dark else '#555'
    hover = 'white' if dark else c['accent']
    links = ''.join(
        f'<a href="{url}" class="text-sm transition hover:opacity-80" '
        f'style="color:{link_color}">{label}</a>'
        for label, url in site_config['nav_links']
    )
    bg_style = f'background:{c["bg"]};border-bottom:1px solid {c["border"]}'
    return (
        f'<header style="{bg_style}">'
        '<div class="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">'
        f'<a href="../index.html" class="text-xl font-bold no-underline" '
        f'style="font-family:{tpl["heading_font"]},sans-serif;color:{c["text"]}">'
        f'{site_config["logo_html"]}</a>'
        f'<nav class="flex gap-4">{links}</nav>'
        '</div></header>'
    )


def _expert_card(tpl):
    """Build expert reviewer card."""
    c = tpl['colors']
    e = tpl['expert']
    return (
        f'<div style="border:1px solid {c["border"]};border-radius:12px;padding:24px;'
        f'margin-top:40px;background:{c["surface"]}">'
        '<div style="display:flex;align-items:center;gap:16px">'
        f'<div style="width:48px;height:48px;border-radius:50%;background:{e["bg"]};'
        f'color:{e["text_color"]};display:flex;align-items:center;justify-content:center;'
        f'font-weight:700;font-size:1.1em;flex-shrink:0">{e["initials"]}</div>'
        f'<div><p style="font-weight:700;margin:0;color:{c["text"]}">{e["name"]}</p>'
        f'<p style="font-size:0.85em;margin:0;color:{c["muted"]}">'
        f'{e["credentials"]}</p></div></div>'
        f'<p style="margin:16px 0 0;font-size:0.9em;line-height:1.6;color:{c["muted"]}">'
        f'{e["bio"]}</p></div>'
    )


def _geo_badge(tpl):
    """Build geo-SEO verification badge."""
    c = tpl['colors']
    return (
        f'<div style="display:flex;align-items:center;gap:8px;font-size:0.85em;'
        f'color:{c["muted"]};margin-bottom:24px">'
        '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">'
        '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" '
        'd="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
        '<span>Verified for fast Prime delivery to '
        '<span id="geo-loc">the Greater San Francisco Bay Area</span></span></div>'
    )


def _disclosure(tpl):
    """Affiliate disclosure text."""
    c = tpl['colors']
    return (
        f'<p style="font-size:0.75em;color:{c["muted"]};margin-top:40px;padding-top:16px;'
        f'border-top:1px solid {c["border"]}"><em>This article contains affiliate links. '
        'If you purchase through these links, we may earn a small commission at no extra '
        'cost to you. This helps us continue creating free content.</em></p>'
    )


def _table_css(tpl):
    """CSS rules for styled comparison tables."""
    c = tpl['colors']
    return (
        f'.article-body table {{ width:100%;border-collapse:collapse;margin:24px 0;font-size:0.9em }}'
        f'.article-body thead th {{ background:{c["accent"]};color:{tpl["cta_text_color"]};'
        f'padding:12px;text-align:left;font-weight:600;white-space:nowrap }}'
        f'.article-body td {{ padding:10px 12px;border-bottom:1px solid {c["border"]} }}'
        f'.article-body tr:nth-child(even) td {{ background:{c["surface"]} }}'
    )


# ── Template 1: The Iron Standard (Fitness) ────────────────────────────────

def _render_iron_standard(tpl, title, meta_desc, body_html, hero_url, site_config,
                          slug, date_str, article_url, cta_url,
                          article_schema, product_schema_tag,
                          faq_schema_tag='', mobile_sticky_html=''):
    c = tpl['colors']
    article_css = (
        f'.article-body h1 {{ font-family:{tpl["heading_font"]},sans-serif; '
        f'font-size:2.2em; font-weight:700; color:#fff; margin:32px 0 16px; line-height:1.2 }}'
        f'.article-body h2 {{ font-family:{tpl["heading_font"]},sans-serif; '
        f'font-size:1.5em; font-weight:600; color:{c["accent"]}; margin:28px 0 12px; line-height:1.3 }}'
        f'.article-body h3 {{ font-family:{tpl["heading_font"]},sans-serif; '
        f'font-size:1.2em; font-weight:600; color:#fff; margin:24px 0 10px }}'
        f'.article-body p {{ color:#ccc; margin:0 0 16px; line-height:1.8 }}'
        f'.article-body ul {{ margin:0 0 16px; padding-left:24px }}'
        f'.article-body li {{ color:#ccc; margin-bottom:8px; line-height:1.7 }}'
        f'.article-body a {{ color:{c["accent"]}; text-decoration:underline }}'
        f'.article-body strong {{ color:#fff }}'
        f'.article-body blockquote {{ border-left:4px solid {c["accent"]}; '
        f'padding:16px 20px; margin:24px 0; background:{c["surface"]}; '
        f'border-radius:0 8px 8px 0 }}'
        f'body {{ font-family:{tpl["body_font"]},sans-serif; padding-bottom:60px }}'
        + _table_css(tpl)
    )

    head = _head(tpl, title, meta_desc, article_url, site_config,
                 article_schema, product_schema_tag, article_css, faq_schema_tag)
    nav = _nav(tpl, site_config, dark=True)

    # Hero — full bleed with dark overlay
    if hero_url:
        hero = (
            f'<div style="position:relative;width:100%;min-height:350px;overflow:hidden">'
            f'<img src="{hero_url}" alt="{_esc(title)}" '
            f'style="width:100%;height:50vh;min-height:350px;object-fit:cover;opacity:0.45" loading="eager">'
            f'<div style="position:absolute;inset:0;background:linear-gradient(to top,{c["bg"]},transparent)"></div>'
            f'<div style="position:absolute;bottom:0;left:0;right:0;padding:24px">'
            f'<div style="max-width:768px;margin:0 auto">'
            f'<span style="display:inline-block;background:{c["accent"]};color:#000;'
            f'padding:4px 12px;font-size:0.75em;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.1em;border-radius:4px">{tpl["tagline"]}</span>'
            f'<h1 style="font-family:{tpl["heading_font"]},sans-serif;font-size:2.2em;'
            f'font-weight:700;color:#fff;margin:12px 0 0;line-height:1.2">{title}</h1>'
            f'<p style="font-size:0.85em;color:{c["muted"]};margin:8px 0 0">'
            f'{date_str} &middot; {tpl["expert"]["name"]}, {tpl["expert"]["credentials"]}</p>'
            f'</div></div></div>'
        )
    else:
        hero = (
            f'<div style="max-width:768px;margin:0 auto;padding:40px 16px 24px">'
            f'<span style="display:inline-block;background:{c["accent"]};color:#000;'
            f'padding:4px 12px;font-size:0.75em;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.1em;border-radius:4px">{tpl["tagline"]}</span>'
            f'<h1 style="font-family:{tpl["heading_font"]},sans-serif;font-size:2.2em;'
            f'font-weight:700;color:#fff;margin:12px 0 0;line-height:1.2">{title}</h1>'
            f'<p style="font-size:0.85em;color:{c["muted"]};margin:8px 0 0">'
            f'{date_str} &middot; {tpl["expert"]["name"]}, {tpl["expert"]["credentials"]}</p>'
            f'</div>'
        )

    sticky = mobile_sticky_html if mobile_sticky_html else _fallback_sticky_cta(tpl, cta_url)

    return (
        head
        + f'<body style="background:{c["bg"]};color:{c["text"]}">\n'
        + nav + '\n' + hero + '\n'
        + f'<main style="max-width:768px;margin:0 auto;padding:32px 16px">\n'
        + _geo_badge(tpl) + '\n'
        + f'<div class="article-body">\n{body_html}\n</div>\n'
        + _expert_card(tpl) + '\n'
        + _disclosure(tpl) + '\n'
        + _prompt_pack_cta(tpl) + '\n'
        + f'<div style="background:{c["accent"]};border-radius:12px;padding:24px;'
        f'margin-top:32px;text-align:center">'
        f'<p style="margin:0 0 8px;color:#000;font-weight:700;font-size:1.1em">'
        f'Want more tips like this?</p>'
        f'<a href="{site_config["base_url"]}" '
        f'style="display:inline-block;background:#000;color:{c["accent"]};'
        f'padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:700">'
        f'Visit {site_config["site_name"]} &rarr;</a></div>\n'
        + '</main>\n'
        + sticky + '\n'
        + GEO_SCRIPT + '\n'
        + '</body>\n</html>'
    )


# ── Template 2: The Wellness Whisper (Menopause) ──────────────────────────

def _render_wellness_whisper(tpl, title, meta_desc, body_html, hero_url, site_config,
                             slug, date_str, article_url, cta_url,
                             article_schema, product_schema_tag,
                             faq_schema_tag='', mobile_sticky_html=''):
    c = tpl['colors']
    article_css = (
        f'.article-body h1 {{ font-family:{tpl["heading_font"]},serif; '
        f'font-size:2em; font-weight:600; color:#2D2D2D; margin:32px 0 16px; line-height:1.3 }}'
        f'.article-body h2 {{ font-family:{tpl["heading_font"]},serif; '
        f'font-size:1.4em; font-weight:600; color:{c["accent"]}; margin:28px 0 12px; line-height:1.4 }}'
        f'.article-body h3 {{ font-family:{tpl["heading_font"]},serif; '
        f'font-size:1.15em; font-weight:600; color:#333; margin:24px 0 10px }}'
        f'.article-body p {{ color:{c["text"]}; margin:0 0 16px; line-height:1.8 }}'
        f'.article-body ul {{ margin:0 0 16px; padding-left:24px }}'
        f'.article-body li {{ color:{c["text"]}; margin-bottom:8px; line-height:1.7 }}'
        f'.article-body a {{ color:{c["accent"]}; text-decoration:underline }}'
        f'.article-body strong {{ color:#222 }}'
        f'.article-body blockquote {{ border-left:4px solid {c["accent"]}; '
        f'padding:16px 20px; margin:24px 0; background:#fff; '
        f'border-radius:0 12px 12px 0; font-style:italic }}'
        f'body {{ font-family:{tpl["body_font"]},sans-serif; padding-bottom:60px }}'
        + _table_css(tpl)
    )

    head = _head(tpl, title, meta_desc, article_url, site_config,
                 article_schema, product_schema_tag, article_css, faq_schema_tag)
    nav = _nav(tpl, site_config, dark=False)

    # Hero — centered editorial with soft image
    hero_img = ''
    if hero_url:
        hero_img = (
            f'<img src="{hero_url}" alt="{_esc(title)}" '
            f'style="width:100%;max-height:400px;object-fit:cover;border-radius:16px;'
            f'margin-bottom:32px" loading="eager">'
        )

    hero = (
        f'<div style="max-width:672px;margin:0 auto;padding:40px 16px 0;text-align:center">'
        f'<span style="display:inline-block;color:{c["accent"]};font-size:0.8em;'
        f'text-transform:uppercase;letter-spacing:0.15em;font-weight:600">'
        f'{tpl["tagline"]}</span>'
        f'<h1 style="font-family:{tpl["heading_font"]},serif;font-size:2em;'
        f'font-weight:600;color:#2D2D2D;margin:12px 0 8px;line-height:1.3">{title}</h1>'
        f'<p style="font-size:0.85em;color:{c["muted"]};margin:0 0 24px">'
        f'Managing {tpl["tagline"]} &middot; {date_str}</p>'
        f'{hero_img}</div>'
    )

    sticky = mobile_sticky_html if mobile_sticky_html else _fallback_sticky_cta(tpl, cta_url)

    return (
        head
        + f'<body style="background:{c["bg"]};color:{c["text"]}">\n'
        + nav + '\n' + hero + '\n'
        + f'<main style="max-width:672px;margin:0 auto;padding:0 16px 48px">\n'
        + _geo_badge(tpl) + '\n'
        + f'<div class="article-body">\n{body_html}\n</div>\n'
        + _expert_card(tpl) + '\n'
        + _disclosure(tpl) + '\n'
        + f'<div style="background:{c["accent"]};border-radius:12px;padding:24px;'
        f'margin-top:32px;text-align:center">'
        f'<p style="margin:0 0 8px;color:#fff;font-weight:700;font-size:1.1em">'
        f'Want more wellness tips?</p>'
        f'<a href="{site_config["base_url"]}" '
        f'style="display:inline-block;background:#fff;color:{c["accent"]};'
        f'padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:700">'
        f'Visit {site_config["site_name"]} &rarr;</a></div>\n'
        + '</main>\n'
        + sticky + '\n'
        + GEO_SCRIPT + '\n'
        + '</body>\n</html>'
    )


# ── Template 3: The Aesthetic Edit (Deals) ─────────────────────────────────

def _render_aesthetic_edit(tpl, title, meta_desc, body_html, hero_url, site_config,
                           slug, date_str, article_url, cta_url,
                           article_schema, product_schema_tag,
                           faq_schema_tag='', mobile_sticky_html=''):
    c = tpl['colors']
    article_css = (
        f'.article-body h1 {{ font-family:{tpl["heading_font"]},serif; '
        f'font-size:2em; font-weight:700; color:#000; margin:32px 0 16px; line-height:1.2 }}'
        f'.article-body h2 {{ font-family:{tpl["heading_font"]},serif; '
        f'font-size:1.4em; font-weight:600; color:#111; margin:28px 0 12px; line-height:1.3; '
        f'border-bottom:2px solid {c["accent"]}; padding-bottom:8px }}'
        f'.article-body h3 {{ font-family:{tpl["heading_font"]},serif; '
        f'font-size:1.15em; font-weight:600; color:#222; margin:24px 0 10px }}'
        f'.article-body p {{ color:{c["text"]}; margin:0 0 16px; line-height:1.8 }}'
        f'.article-body ul {{ margin:0 0 16px; padding-left:24px }}'
        f'.article-body li {{ color:{c["text"]}; margin-bottom:8px; line-height:1.7 }}'
        f'.article-body a {{ color:{c["accent"]}; text-decoration:underline }}'
        f'.article-body strong {{ color:#000 }}'
        f'.article-body blockquote {{ border-left:3px solid {c["accent"]}; '
        f'padding:16px 20px; margin:24px 0; background:#fff; border-radius:0 8px 8px 0 }}'
        f'body {{ font-family:{tpl["body_font"]},sans-serif; padding-bottom:60px }}'
        + _table_css(tpl)
    )

    head = _head(tpl, title, meta_desc, article_url, site_config,
                 article_schema, product_schema_tag, article_css, faq_schema_tag)
    nav = _nav(tpl, site_config, dark=False)

    # Hero — vertical Pinterest-style image
    year = datetime.now(timezone.utc).year
    hero_img = ''
    if hero_url:
        hero_img = (
            f'<div style="max-width:320px;margin:0 auto 32px;aspect-ratio:9/16;'
            f'overflow:hidden;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,0.08)">'
            f'<img src="{hero_url}" alt="{_esc(title)}" '
            f'style="width:100%;height:100%;object-fit:cover" loading="eager">'
            f'</div>'
        )

    hero = (
        f'<div style="max-width:672px;margin:0 auto;padding:40px 16px 0;text-align:center">'
        f'<span style="display:inline-block;color:{c["accent"]};font-size:0.8em;'
        f'text-transform:uppercase;letter-spacing:0.2em;font-weight:600">'
        f'{tpl["tagline"]}</span>'
        f'<h1 style="font-family:{tpl["heading_font"]},serif;font-size:2.2em;'
        f'font-weight:700;color:#000;margin:12px 0 8px;line-height:1.2">{title}</h1>'
        f'<p style="font-size:0.85em;color:{c["muted"]};margin:0 0 24px">'
        f'The {year} Edit &middot; {date_str}</p>'
        f'{hero_img}</div>'
    )

    sticky = mobile_sticky_html if mobile_sticky_html else _fallback_sticky_cta(tpl, cta_url)

    return (
        head
        + f'<body style="background:{c["bg"]};color:{c["text"]}">\n'
        + nav + '\n' + hero + '\n'
        + f'<main style="max-width:672px;margin:0 auto;padding:0 16px 48px">\n'
        + _geo_badge(tpl) + '\n'
        + f'<div class="article-body">\n{body_html}\n</div>\n'
        + _expert_card(tpl) + '\n'
        + _disclosure(tpl) + '\n'
        + f'<div style="background:{c["accent"]};border-radius:12px;padding:24px;'
        f'margin-top:32px;text-align:center">'
        f'<p style="margin:0 0 8px;color:#000;font-weight:700;font-size:1.1em">'
        f'More curated finds</p>'
        f'<a href="{site_config["base_url"]}" '
        f'style="display:inline-block;background:#000;color:{c["accent"]};'
        f'padding:10px 24px;border-radius:8px;text-decoration:none;font-weight:700">'
        f'Visit {site_config["site_name"]} &rarr;</a></div>\n'
        + '</main>\n'
        + sticky + '\n'
        + GEO_SCRIPT + '\n'
        + '</body>\n</html>'
    )


# ── V3 Template System ──────────────────────────────────────────────────────

def _render_v3_page(brand_key, article_data, site_config, slug):
    """Render complete v3 article page with 22 sections.

    article_data structure:
    {
        'title': str,
        'meta_description': str,
        'read_time': str,
        'brands_tested': int,
        'reviews_analyzed': str,
        'verdict': str,
        'before': {'emoji': str, 'title': str, 'text': str},
        'after': {'emoji': str, 'title': str, 'text': str},
        'urgency_text': str,
        'hero_url': str,
        'video_url': str or None,
        'category': str,
        'products': [...],
        'comparison_extra_rows': [...],
        'methodology': [str],
        'faq': [{'q': str, 'a': str}],
        'related_products': [...],
    }
    """
    tpl = TEMPLATE_CONFIG.get(brand_key, TEMPLATE_CONFIG['deals'])
    c = tpl['colors']

    title = article_data.get('title', 'Untitled')
    meta_desc = article_data.get('meta_description', '')
    article_url = site_config['base_url'] + '/articles/' + slug + '.html'

    # Build schemas
    article_schema = _build_article_schema(
        title, meta_desc, slug, site_config, tpl['expert']['name'])

    products = article_data.get('products', [])
    first_product_amazon = products[0].get('amazon_url', '') if products else ''
    product_schema_tag = ''
    if first_product_amazon:
        product_schema_tag = (
            '<script type="application/ld+json">'
            + _build_product_schema(title, first_product_amazon)
            + '</script>'
        )

    # Build FAQ schema
    faq_pairs = [(q['q'], q['a']) for q in article_data.get('faq', [])]
    faq_schema_tag = _build_faq_schema(faq_pairs)

    # Build styles
    v3_css = _build_v3_css(tpl)

    # Build head
    head = _head(tpl, title, meta_desc, article_url, site_config,
                 article_schema, product_schema_tag, v3_css, faq_schema_tag)

    # Build all 22 sections
    sections = []
    sections.append(_v3_sticky_nav(tpl, site_config, article_url))
    sections.append(_v3_breadcrumbs(tpl, article_data.get('category', '')))
    sections.append(_v3_social_proof(tpl, article_data.get('reviews_analyzed', '0')))
    sections.append(_v3_hero(tpl, article_data, slug))
    sections.append(_v3_before_after(tpl, article_data))
    sections.append(_v3_quick_verdict(tpl, article_data.get('verdict', '')))
    sections.append(_v3_urgency_banner(tpl, article_data.get('urgency_text', '')))
    sections.append(_v3_quick_picks(tpl, products))
    sections.append(_v3_trust_bar(tpl))
    sections.append(_v3_as_seen_in(tpl))
    sections.append(_v3_email_signup(site_config, tpl, brand_key))
    sections.extend(_v3_product_sections(tpl, products))
    sections.append(_v3_comparison_table(tpl, products, article_data.get('comparison_extra_rows', [])))
    sections.append(_v3_how_we_chose(tpl, article_data.get('methodology', [])))
    sections.append(_v3_price_drop_alert(site_config, tpl, brand_key))
    if brand_key == 'menopause':
        sections.append(ETSY_CTA_HTML)
    sections.append(_v3_faq_section(tpl, article_data.get('faq', [])))
    sections.append(_v3_related_products(tpl, article_data.get('related_products', [])))
    sections.append(_v3_share_bar(tpl, article_url, title))
    sections.append(_v3_expert_bio(tpl))
    sections.append(_v3_final_cta_box(tpl, products))
    sections.append(_v3_footer(tpl, site_config))

    body_html = '\n'.join(sections)

    # Mobile sticky CTA
    mobile_sticky = ''
    if products:
        top_pick = products[0]
        mobile_sticky = _v3_mobile_sticky_cta(tpl, top_pick)

    return (
        head
        + f'<body style="background:{c["bg"]};color:{c["text"]}">\n'
        + body_html
        + mobile_sticky
        + '\n' + GEO_SCRIPT + '\n'
        + '</body>\n</html>'
    )


def _build_v3_css(tpl):
    """Build CSS for v3 template."""
    c = tpl['colors']
    return (
        f'* {{ box-sizing: border-box; }}'
        f'body {{ font-family: {tpl["body_font"]}, sans-serif; margin: 0; padding: 0; }}'
        f'h1, h2, h3, h4, h5, h6 {{ font-family: {tpl["heading_font"]}, sans-serif; }}'
        f'a {{ color: {c["accent"]}; text-decoration: none; }}'
        f'a:hover {{ opacity: 0.85; }}'
        f'.container {{ max-width: 900px; margin: 0 auto; padding: 0 16px; }}'
        f'@media (max-width: 768px) {{ .hide-mobile {{ display: none; }} }}'
        f'.sticky-nav {{ position: fixed; top: 0; left: 0; right: 0; z-index: 1000; }}'
        f'.product-card {{ border: 1px solid {c["border"]}; border-radius: 12px; padding: 20px; margin: 20px 0; }}'
        f'button, .btn {{ cursor: pointer; padding: 12px 24px; border: none; border-radius: 8px; }}'
        f'.btn-primary {{ background: {c["accent"]}; color: {tpl["cta_text_color"]}; font-weight: 700; }}'
        f'.star {{ color: #FFD700; }}'
    )


def _v3_sticky_nav(tpl, site_config, article_url):
    """Section 1: Sticky navigation bar."""
    c = tpl['colors']
    return (
        f'<nav class="sticky-nav" style="background: {c["bg"]}; border-bottom: 1px solid {c["border"]}; '
        f'padding: 12px 16px;">'
        f'<div class="container" style="display: flex; align-items: center; justify-content: space-between;">'
        f'<div style="font-weight: 700; font-size: 0.85em; background: {c["accent"]}; '
        f'color: {tpl["cta_text_color"]}; padding: 4px 12px; border-radius: 4px;">'
        f'EXPERT TESTED</div>'
        f'<a href="https://pinterest.com/pin/create/button/?url={_esc(article_url)}" '
        f'target="_blank" style="font-size: 0.9em; color: {c["accent"]};">Pin</a>'
        f'</div></nav>'
    )


def _v3_breadcrumbs(tpl, category):
    """Section 2: Breadcrumb navigation."""
    c = tpl['colors']
    cat_name = _esc(category) if category else 'Products'
    return (
        f'<div style="background: {c["surface"]}; padding: 12px 16px; border-bottom: 1px solid {c["border"]};">'
        f'<div class="container" style="font-size: 0.85em; color: {c["muted"]};">'
        f'<a href="../index.html" style="color: {c["accent"]};">Home</a> / '
        f'<span>{cat_name}</span></div></div>'
    )


def _v3_social_proof(tpl, reviews_analyzed):
    """Section 3: Social proof banner."""
    c = tpl['colors']
    return (
        f'<div style="background: {c["surface"]}; padding: 16px; margin: 0; text-align: center; '
        f'border-bottom: 1px solid {c["border"]};">'
        f'<p style="margin: 0; font-size: 0.9em; color: {c["text"]};">'
        f'Trusted by {_esc(reviews_analyzed)} verified buyers</p></div>'
    )


def _v3_hero(tpl, article_data, slug):
    """Section 4: Hero section with image or video."""
    c = tpl['colors']
    title = article_data.get('title', 'Untitled')
    hero_url = article_data.get('hero_url', '')
    video_url = article_data.get('video_url')
    read_time = article_data.get('read_time', '5 min')
    brands_tested = article_data.get('brands_tested', 0)
    reviews_analyzed = article_data.get('reviews_analyzed', '0')

    now = datetime.now(timezone.utc)
    month_year = now.strftime('%B %Y')

    media = ''
    if video_url:
        media = (
            f'<video autoplay muted loop playsinline poster="{_esc(hero_url)}" '
            f'style="width: 100%; height: 500px; object-fit: cover;">'
            f'<source src="{_esc(video_url)}" type="video/mp4"></video>'
        )
    elif hero_url:
        media = f'<img src="{_esc(hero_url)}" alt="{_esc(title)}" style="width: 100%; height: 500px; object-fit: cover;">'

    return (
        f'<div style="position: relative; background: {c["bg"]}; color: {c["text"]}; '
        f'padding: 60px 16px; text-align: center;">'
        f'{media}'
        f'<div style="position: absolute; bottom: 0; left: 0; right: 0; '
        f'background: linear-gradient(to top, {c["bg"]}, transparent); padding: 40px 16px;">'
        f'<div class="container">'
        f'<div style="font-size: 0.85em; color: {c["muted"]}; margin-bottom: 12px;">'
        f'UPDATED {month_year.upper()} &bull; {brands_tested} BRANDS TESTED</div>'
        f'<h1 style="margin: 0 0 12px; font-size: 2.5em; line-height: 1.2;">{_esc(title)}</h1>'
        f'<p style="margin: 0; font-size: 0.9em; color: {c["muted"]};">'
        f'By {tpl["expert"]["name"]} &bull; {read_time} read &bull; Based on {_esc(reviews_analyzed)} reviews</p>'
        f'</div></div></div>'
    )


def _v3_before_after(tpl, article_data):
    """Section 5: Before/After comparison cards."""
    c = tpl['colors']
    before = article_data.get('before', {})
    after = article_data.get('after', {})

    return (
        f'<div class="container" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; '
        f'padding: 40px 16px;">'
        f'<div style="background: rgba(255, 0, 0, 0.05); border: 1px solid #ffcccc; border-radius: 12px; '
        f'padding: 24px; text-align: center;">'
        f'<div style="font-size: 2em; margin-bottom: 8px;">{before.get("emoji", "")}</div>'
        f'<h3 style="margin: 0 0 8px; color: {c["text"]};">{_esc(before.get("title", ""))}</h3>'
        f'<p style="margin: 0; color: {c["muted"]};">{_esc(before.get("text", ""))}</p>'
        f'</div>'
        f'<div style="background: rgba(0, 255, 0, 0.05); border: 1px solid #ccffcc; border-radius: 12px; '
        f'padding: 24px; text-align: center;">'
        f'<div style="font-size: 2em; margin-bottom: 8px;">{after.get("emoji", "")}</div>'
        f'<h3 style="margin: 0 0 8px; color: {c["text"]};">{_esc(after.get("title", ""))}</h3>'
        f'<p style="margin: 0; color: {c["muted"]};">{_esc(after.get("text", ""))}</p>'
        f'</div>'
        f'</div>'
    )


def _v3_quick_verdict(tpl, verdict):
    """Section 6: Quick verdict box."""
    c = tpl['colors']
    first_sent = verdict.split('.')[0] + '.' if '.' in verdict else verdict
    rest = verdict[len(first_sent):].strip() if len(verdict) > len(first_sent) else ''

    return (
        f'<div class="container" style="padding: 40px 16px;">'
        f'<div style="background: {c["surface"]}; border-left: 4px solid {c["accent"]}; '
        f'padding: 24px; border-radius: 8px;">'
        f'<h2 style="margin: 0 0 12px; display: flex; align-items: center; gap: 8px;">'
        f'✓ Quick Verdict</h2>'
        f'<p style="margin: 0; line-height: 1.6;">'
        f'<strong>{first_sent}</strong> {_esc(rest)}</p>'
        f'</div></div>'
    )


def _v3_urgency_banner(tpl, urgency_text):
    """Section 7: Urgency banner."""
    if not urgency_text:
        return ''
    return (
        f'<div style="background: linear-gradient(135deg, #ff6b6b, #ff8787); color: white; '
        f'padding: 24px 16px; text-align: center; margin: 20px 0;">'
        f'<div class="container">'
        f'<p style="margin: 0; font-weight: 700;">DEAL: {_esc(urgency_text)}</p>'
        f'</div></div>'
    )


def _v3_quick_picks(tpl, products):
    """Section 8: Quick picks grid."""
    if not products:
        return ''
    c = tpl['colors']
    picks_html = ''
    for product in products[:3]:
        hero_img = product.get('hero_image', '')
        name = product.get('name', '')
        badge = product.get('badge', '')
        rating = product.get('rating', 0)
        amazon_url = product.get('amazon_url', '')

        stars = '⭐' * int(rating)

        picks_html += (
            f'<div style="background: {c["surface"]}; border: 1px solid {c["border"]}; '
            f'border-radius: 12px; padding: 16px; text-align: center;">'
            f'<img src="{_esc(hero_img)}" alt="{_esc(name)}" style="width: 100%; '
            f'height: 180px; object-fit: cover; border-radius: 8px; margin-bottom: 12px;" '
            f'loading="lazy">'
            f'<span style="background: {c["accent"]}; color: {tpl["cta_text_color"]}; '
            f'padding: 4px 8px; font-size: 0.75em; border-radius: 4px; display: inline-block; '
            f'margin-bottom: 8px;">{_esc(badge)}</span>'
            f'<h3 style="margin: 8px 0; font-size: 0.95em;">{_esc(name)}</h3>'
            f'<p style="margin: 0 0 12px; font-size: 0.85em;">{stars} {rating}</p>'
            f'<a href="{_esc(amazon_url)}" target="_blank" rel="nofollow sponsored noopener" '
            f'class="btn btn-primary">View →</a>'
            f'</div>'
        )

    return (
        f'<div class="container" style="padding: 40px 16px;">'
        f'<h2 style="text-align: center; margin: 0 0 24px;">Top Picks</h2>'
        f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); '
        f'gap: 20px;">{picks_html}</div></div>'
    )


def _v3_trust_bar(tpl):
    """Section 9: Trust badges."""
    c = tpl['colors']
    return (
        f'<div class="container" style="padding: 32px 16px; text-align: center;">'
        f'<div style="display: flex; justify-content: center; gap: 24px; flex-wrap: wrap;">'
        f'<div style="font-size: 0.85em;"><span style="color: {c["accent"]}; font-weight: 700;">✓</span> '
        f'Verified Reviews</div>'
        f'<div style="font-size: 0.85em;"><span style="color: {c["accent"]}; font-weight: 700;">✓</span> '
        f'30-Day Returns</div>'
        f'<div style="font-size: 0.85em;"><span style="color: {c["accent"]}; font-weight: 700;">✓</span> '
        f'Free Prime Shipping</div>'
        f'</div></div>'
    )


def _v3_as_seen_in(tpl):
    """Section 10: 'As Seen In' logos."""
    c = tpl['colors']
    return (
        f'<div class="container" style="padding: 32px 16px; text-align: center; '
        f'border-top: 1px solid {c["border"]}; border-bottom: 1px solid {c["border"]};">'
        f'<p style="margin: 0 0 16px; color: {c["muted"]}; font-size: 0.85em;">Referenced by</p>'
        f'<div style="display: flex; justify-content: center; gap: 32px; flex-wrap: wrap; '
        f'color: {c["muted"]}; font-size: 0.9em;">'
        f'Sleep Foundation &bull; Health.com &bull; Pinterest Trending'
        f'</div></div>'
    )


def _v3_email_signup(site_config, tpl, brand_key):
    """Section 11: Email signup form."""
    c = tpl['colors']
    lead_magnet = LEAD_MAGNET_OVERRIDES.get(brand_key, 'Free weekly tips')
    form_id = site_config.get('signup_form_id', '')

    return (
        f'<div class="container" style="padding: 40px 16px;">'
        f'<div style="background: {c["surface"]}; border: 1px solid {c["border"]}; '
        f'border-radius: 12px; padding: 32px; text-align: center;">'
        f'<h3 style="margin: 0 0 8px;">{_esc(lead_magnet)}</h3>'
        f'<p style="margin: 0 0 16px; color: {c["muted"]};">Join our community for exclusive tips.</p>'
        f'<script src="https://f.convertkit.com/ckjs/ck.5.js"></script>'
        f'<form action="https://app.kit.com/forms/{form_id}/subscriptions" method="post" '
        f'data-sv-form="{form_id}" style="display: flex; gap: 8px; justify-content: center; '
        f'flex-wrap: wrap;">'
        f'<input type="email" name="email_address" placeholder="Enter your email" required '
        f'style="padding: 12px 16px; border: 1px solid {c["border"]}; border-radius: 8px; '
        f'min-width: 250px;">'
        f'<button type="submit" class="btn btn-primary">Subscribe</button>'
        f'</form></div></div>'
    )


def _v3_product_sections(tpl, products):
    """Sections 12: Individual product detail sections."""
    sections = []
    c = tpl['colors']

    for product in products:
        name = product.get('name', '')
        badge = product.get('badge', '')
        hero_img = product.get('hero_image', '')
        thumb_images = product.get('thumb_images', [])
        rating = product.get('rating', 0)
        review_count = product.get('review_count', '0')
        price_low = product.get('price_low', 0)
        price_high = product.get('price_high', 0)
        subscribe_save = product.get('subscribe_save', '')
        amazon_url = product.get('amazon_url', '')
        benefit_icons = product.get('benefit_icons', [])
        benefit_img = product.get('benefit_image', '')
        benefit_headline = product.get('benefit_headline', '')
        benefit_desc = product.get('benefit_description', '')
        pros = product.get('pros', [])
        cons = product.get('cons', [])
        testimonials = product.get('testimonials', [])

        stars = '⭐' * int(rating)

        # Hero image
        section = f'<div class="container" style="padding: 40px 16px;">'
        section += f'<h2 style="margin: 0 0 24px;">{_esc(name)} — Best for {_esc(badge)}</h2>'

        # Full-width hero
        section += (
            f'<div style="position: relative; margin-bottom: 24px;">'
            f'<img src="{_esc(hero_img)}" alt="{_esc(name)}" '
            f'style="width: 100%; height: 400px; object-fit: cover; border-radius: 12px;" '
            f'loading="lazy">'
            f'<span style="position: absolute; top: 16px; left: 16px; background: {c["accent"]}; '
            f'color: {tpl["cta_text_color"]}; padding: 8px 16px; border-radius: 6px; '
            f'font-weight: 700; font-size: 0.85em;">{_esc(badge)}</span>'
            f'</div>'
        )

        # Thumbnail strip
        if thumb_images:
            thumb_html = ''
            for thumb in thumb_images[:4]:
                thumb_html += f'<img src="{_esc(thumb)}" alt="detail" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px; cursor: pointer;" loading="lazy">'
            section += f'<div style="display: flex; gap: 8px; margin-bottom: 24px;">{thumb_html}</div>'

        # Product info
        section += (
            f'<h3 style="margin: 0 0 8px;">{_esc(name)}</h3>'
            f'<p style="margin: 0 0 8px; color: {c["muted"]};">{stars} {rating} ({_esc(review_count)} reviews)</p>'
            f'<p style="margin: 0 0 16px; font-size: 1.2em; font-weight: 700;">'
            f'${price_low}–${price_high}</p>'
        )

        if subscribe_save:
            section += f'<p style="margin: 0 0 16px; color: {c["accent"]}; font-weight: 600;">Subscribe & Save: {_esc(subscribe_save)}</p>'

        # Benefit icons
        if benefit_icons:
            benefit_html = ''
            for icon in benefit_icons[:3]:
                benefit_html += f'<div style="text-align: center;"><div style="font-size: 2em; margin-bottom: 4px;">{icon.get("emoji", "")}</div><p style="margin: 0; font-size: 0.85em;">{_esc(icon.get("text", ""))}</p></div>'
            section += f'<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px;">{benefit_html}</div>'

        # Benefit section
        if benefit_img:
            section += (
                f'<div style="position: relative; margin-bottom: 24px;">'
                f'<img src="{_esc(benefit_img)}" alt="benefit" style="width: 100%; height: 300px; object-fit: cover; border-radius: 12px; opacity: 0.7;" loading="lazy">'
                f'<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); border-radius: 12px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; text-align: center;">'
                f'<h3 style="margin: 0; font-size: 1.5em;">{_esc(benefit_headline)}</h3>'
                f'<p style="margin: 12px 0 0;">{_esc(benefit_desc)}</p>'
                f'</div></div>'
            )

        # Pros/Cons
        if pros or cons:
            section += (
                f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px;">'
                f'<div>'
                f'<h4 style="margin: 0 0 12px; color: {c["accent"]};">Pros</h4>'
            )
            for pro in pros:
                section += f'<p style="margin: 0 0 8px;">✓ {_esc(pro)}</p>'
            section += f'</div><div><h4 style="margin: 0 0 12px; color: #d32f2f;">Cons</h4>'
            for con in cons:
                section += f'<p style="margin: 0 0 8px;">✗ {_esc(con)}</p>'
            section += '</div></div>'

        # Testimonials
        if testimonials:
            for testimonial in testimonials:
                section += (
                    f'<div style="background: {c["surface"]}; border: 1px solid {c["border"]}; '
                    f'border-radius: 12px; padding: 20px; margin-bottom: 16px;">'
                    f'<div style="display: flex; gap: 12px; margin-bottom: 12px;">'
                    f'<img src="{_esc(testimonial.get("photo", ""))}" alt="reviewer" '
                    f'style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" '
                    f'loading="lazy">'
                    f'<div>'
                    f'<p style="margin: 0; font-weight: 700;">{_esc(testimonial.get("name", ""))}</p>'
                    f'<p style="margin: 0; font-size: 0.85em; color: {c["muted"]};">Verified Amazon Purchase</p>'
                    f'</div></div>'
                    f'<p style="margin: 0 0 8px;">⭐⭐⭐⭐⭐</p>'
                    f'<p style="margin: 0; color: {c["muted"]};">"{_esc(testimonial.get("quote", ""))}"</p>'
                    f'</div>'
                )

        # Subscribe & Save callout
        if subscribe_save:
            section += (
                f'<div style="background: {c["accent"]}; color: {tpl["cta_text_color"]}; '
                f'padding: 16px; border-radius: 8px; margin-bottom: 24px; text-align: center;">'
                f'<p style="margin: 0; font-weight: 700;">Subscribe & Save: {_esc(subscribe_save)}</p>'
                f'</div>'
            )

        # CTA button
        section += (
            f'<a href="{_esc(amazon_url)}" target="_blank" rel="nofollow sponsored noopener" '
            f'class="btn btn-primary" style="display: block; text-align: center; width: 100%; '
            f'font-size: 1.05em; margin-bottom: 12px;">Check Today\'s Price on Amazon →</a>'
            f'<p style="margin: 0; text-align: center; font-size: 0.85em; color: {c["muted"]};">'
            f'Free returns • Prime eligible • 30-day guarantee</p>'
        )

        # Payment logos
        section += (
            f'<p style="margin: 24px 0 0; text-align: center; font-size: 0.85em; color: {c["muted"]};">'
            f'Visa • Mastercard • PayPal • Amazon Pay • Apple Pay</p>'
        )

        section += '</div>'
        sections.append(section)

    return sections


def _v3_comparison_table(tpl, products, extra_rows):
    """Section 13: Comparison table."""
    if not products:
        return ''

    c = tpl['colors']

    table = f'<div class="container" style="padding: 40px 16px;"><h2>Product Comparison</h2>'
    table += (
        f'<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">'
        f'<thead><tr style="background: {c["accent"]}; color: {tpl["cta_text_color"]};">'
        f'<th style="padding: 12px; text-align: left;">Product</th>'
        f'<th style="padding: 12px;">Price Range</th>'
        f'<th style="padding: 12px;">Rating</th>'
        f'<th style="padding: 12px;">Reviews</th>'
        f'<th style="padding: 12px;">Subscribe & Save</th>'
        f'<th style="padding: 12px;">Buy?</th>'
        f'</tr></thead><tbody>'
    )

    for i, product in enumerate(products):
        bg = c["surface"] if i % 2 == 0 else 'transparent'
        table += (
            f'<tr style="background: {bg}; border-bottom: 1px solid {c["border"]};">'
            f'<td style="padding: 12px;"><strong>{_esc(product.get("name", ""))}</strong> '
            f'<span style="background: {c["accent"]}; color: {tpl["cta_text_color"]}; padding: 2px 6px; '
            f'font-size: 0.75em; border-radius: 3px;">{_esc(product.get("badge", ""))}</span></td>'
            f'<td style="padding: 12px; text-align: center;">${product.get("price_low", 0)}–${product.get("price_high", 0)}</td>'
            f'<td style="padding: 12px; text-align: center;">⭐ {product.get("rating", 0)}</td>'
            f'<td style="padding: 12px; text-align: center;">{_esc(product.get("review_count", "0"))}</td>'
            f'<td style="padding: 12px; text-align: center;">{_esc(product.get("subscribe_save", "—"))}</td>'
            f'<td style="padding: 12px; text-align: center;">'
            f'<a href="{_esc(product.get("amazon_url", ""))}" target="_blank" rel="nofollow sponsored noopener" '
            f'class="btn btn-primary" style="font-size: 0.85em; padding: 6px 12px;">View</a></td>'
            f'</tr>'
        )

    for extra_row in extra_rows:
        label = extra_row.get('label', '')
        values = extra_row.get('values', [])
        table += f'<tr style="border-bottom: 1px solid {c["border"]};">'
        table += f'<td style="padding: 12px;"><strong>{_esc(label)}</strong></td>'
        for val in values:
            table += f'<td style="padding: 12px; text-align: center;">{_esc(val)}</td>'
        table += '</tr>'

    table += '</tbody></table></div>'
    return table


def _v3_how_we_chose(tpl, methodology):
    """Section 14: Methodology section."""
    if not methodology:
        return ''

    c = tpl['colors']
    method_html = ''
    for i, item in enumerate(methodology[:4], 1):
        method_html += (
            f'<div style="text-align: center;">'
            f'<div style="font-size: 2em; font-weight: 700; color: {c["accent"]}; margin-bottom: 8px;">'
            f'{i}</div>'
            f'<p style="margin: 0;">{_esc(item)}</p>'
            f'</div>'
        )

    return (
        f'<div class="container" style="padding: 40px 16px;">'
        f'<h2 style="text-align: center; margin-bottom: 32px;">How We Chose These Products</h2>'
        f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 24px;">'
        f'{method_html}</div></div>'
    )


def _v3_price_drop_alert(site_config, tpl, brand_key):
    """Section 15: Price drop alert signup."""
    c = tpl['colors']
    form_id = site_config.get('signup_form_id', '')

    return (
        f'<div class="container" style="padding: 40px 16px;">'
        f'<div style="background: {c["surface"]}; border: 1px solid {c["border"]}; '
        f'border-radius: 12px; padding: 24px; text-align: center;">'
        f'<h3 style="margin: 0 0 12px;">Price Drop Alert</h3>'
        f'<p style="margin: 0 0 16px; color: {c["muted"]};">Get notified if the price drops on these products.</p>'
        f'<script src="https://f.convertkit.com/ckjs/ck.5.js"></script>'
        f'<form action="https://app.kit.com/forms/{form_id}/subscriptions" method="post" '
        f'data-sv-form="{form_id}" style="display: flex; gap: 8px; justify-content: center;">'
        f'<input type="email" name="email_address" placeholder="Enter your email" required '
        f'style="padding: 12px 16px; border: 1px solid {c["border"]}; border-radius: 8px; min-width: 250px;">'
        f'<button type="submit" class="btn btn-primary">Notify Me</button>'
        f'</form></div></div>'
    )


def _v3_faq_section(tpl, faq_items):
    """Section 17: FAQ section with expandable items."""
    if not faq_items:
        return ''

    c = tpl['colors']
    faq_html = ''
    for item in faq_items:
        q = item.get('q', '')
        a = item.get('a', '')
        faq_html += (
            f'<details style="margin-bottom: 12px; border: 1px solid {c["border"]}; '
            f'border-radius: 8px; padding: 16px;">'
            f'<summary style="cursor: pointer; font-weight: 700; color: {c["text"]};">{_esc(q)}</summary>'
            f'<p style="margin: 12px 0 0; color: {c["muted"]};">{_esc(a)}</p>'
            f'</details>'
        )

    return (
        f'<div class="container" style="padding: 40px 16px;">'
        f'<h2 style="margin-bottom: 24px;">Frequently Asked Questions</h2>'
        f'{faq_html}</div>'
    )


def _v3_related_products(tpl, related):
    """Section 18: Related products."""
    if not related:
        return ''

    c = tpl['colors']
    related_html = ''
    for prod in related[:3]:
        related_html += (
            f'<div style="background: {c["surface"]}; border: 1px solid {c["border"]}; '
            f'border-radius: 12px; padding: 16px; text-align: center;">'
            f'<img src="{_esc(prod.get("image", ""))}" alt="{_esc(prod.get("name", ""))}" '
            f'style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 12px;" '
            f'loading="lazy">'
            f'<h4 style="margin: 0 0 12px;">{_esc(prod.get("name", ""))}</h4>'
            f'<a href="{_esc(prod.get("amazon_url", ""))}" target="_blank" rel="nofollow sponsored noopener" '
            f'class="btn btn-primary">View on Amazon →</a>'
            f'</div>'
        )

    return (
        f'<div class="container" style="padding: 40px 16px;">'
        f'<h2 style="margin-bottom: 24px;">Also Bought</h2>'
        f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">'
        f'{related_html}</div></div>'
    )


def _v3_share_bar(tpl, article_url, title):
    """Section 19: Social share buttons."""
    c = tpl['colors']
    escaped_url = _esc(article_url)
    escaped_title = _esc(title)

    return (
        f'<div class="container" style="padding: 32px 16px; text-align: center; '
        f'border-top: 1px solid {c["border"]}; border-bottom: 1px solid {c["border"]};">'
        f'<p style="margin: 0 0 16px; color: {c["muted"]};">Share this article</p>'
        f'<div style="display: flex; justify-content: center; gap: 12px;">'
        f'<a href="https://pinterest.com/pin/create/button/?url={escaped_url}&description={escaped_title}" '
        f'target="_blank" style="padding: 8px 16px; background: {c["accent"]}; color: {tpl["cta_text_color"]}; '
        f'border-radius: 6px; font-size: 0.85em;">Pinterest</a>'
        f'<a href="https://www.facebook.com/sharer/sharer.php?u={escaped_url}" '
        f'target="_blank" style="padding: 8px 16px; background: {c["accent"]}; color: {tpl["cta_text_color"]}; '
        f'border-radius: 6px; font-size: 0.85em;">Facebook</a>'
        f'<a href="https://api.whatsapp.com/send?text={escaped_title}%20{escaped_url}" '
        f'target="_blank" style="padding: 8px 16px; background: {c["accent"]}; color: {tpl["cta_text_color"]}; '
        f'border-radius: 6px; font-size: 0.85em;">WhatsApp</a>'
        f'</div></div>'
    )


def _v3_expert_bio(tpl):
    """Section 20: Expert bio card."""
    e = tpl['expert']
    c = tpl['colors']

    return (
        f'<div class="container" style="padding: 40px 16px;">'
        f'<div style="background: {c["surface"]}; border: 1px solid {c["border"]}; '
        f'border-radius: 12px; padding: 24px; text-align: center;">'
        f'<div style="width: 60px; height: 60px; border-radius: 50%; background: {e["bg"]}; '
        f'color: {e["text_color"]}; display: flex; align-items: center; justify-content: center; '
        f'font-weight: 700; font-size: 1.3em; margin: 0 auto 12px;">{e["initials"]}</div>'
        f'<h3 style="margin: 0;">{e["name"]}</h3>'
        f'<p style="margin: 4px 0 12px; color: {c["muted"]}; font-size: 0.85em;">{e["credentials"]}</p>'
        f'<p style="margin: 0; color: {c["muted"]}; line-height: 1.6;">{e["bio"]}</p>'
        f'</div></div>'
    )


def _v3_final_cta_box(tpl, products):
    """Section 21: Final CTA box."""
    c = tpl['colors']

    if not products:
        return ''

    top = products[0]
    name = top.get('name', '')
    amazon_url = top.get('amazon_url', '')

    return (
        f'<div class="container" style="padding: 40px 16px;">'
        f'<div style="background: {c["accent"]}; color: {tpl["cta_text_color"]}; '
        f'border-radius: 12px; padding: 32px; text-align: center;">'
        f'<h2 style="margin: 0 0 12px; color: {tpl["cta_text_color"]};">{_esc(name)}</h2>'
        f'<a href="{_esc(amazon_url)}" target="_blank" rel="nofollow sponsored noopener" '
        f'class="btn" style="background: {tpl["cta_text_color"]}; color: {c["accent"]}; '
        f'display: inline-block; margin-bottom: 12px;">Check Today\'s Price on Amazon →</a>'
        f'<p style="margin: 0; font-size: 0.85em;">Visa • Mastercard • PayPal • Amazon Pay • Apple Pay</p>'
        f'</div></div>'
    )


def _v3_footer(tpl, site_config):
    """Section 22: Footer."""
    c = tpl['colors']
    year = datetime.now(timezone.utc).year

    return (
        f'<footer style="background: {c["bg"]}; border-top: 1px solid {c["border"]}; '
        f'padding: 40px 16px; margin-top: 60px;">'
        f'<div class="container">'
        f'<p style="margin: 0 0 12px; font-size: 0.75em; color: {c["muted"]};">'
        f'This article contains affiliate links. If you purchase through these links, we may earn a '
        f'small commission at no extra cost to you. This helps us continue creating free content.</p>'
        f'<p style="margin: 0; font-size: 0.75em; color: {c["muted"]};">'
        f'© {year} {site_config["site_name"]}. All rights reserved.</p>'
        f'</div></footer>'
    )


def _v3_mobile_sticky_cta(tpl, top_product):
    """Mobile sticky CTA for v3 template."""
    c = tpl['colors']
    name = top_product.get('name', '')
    price_low = top_product.get('price_low', 0)
    price_high = top_product.get('price_high', 0)
    amazon_url = top_product.get('amazon_url', '')

    return (
        f'<style>@media (max-width: 768px) {{ .v3-mobile-sticky {{ display: flex !important; }} }}</style>'
        f'<div class="v3-mobile-sticky" style="display: none; position: fixed; bottom: 0; left: 0; right: 0; '
        f'background: {c["surface"]}; border-top: 2px solid {c["accent"]}; padding: 12px 16px; '
        f'z-index: 1000; align-items: center; justify-content: space-between;">'
        f'<div><p style="margin: 0; font-weight: 700; font-size: 0.9em;">{_esc(name)}</p>'
        f'<p style="margin: 0; color: {c["muted"]}; font-size: 0.8em;">${price_low}–${price_high}</p></div>'
        f'<a href="{_esc(amazon_url)}" target="_blank" rel="nofollow sponsored noopener" '
        f'style="background: {c["accent"]}; color: {tpl["cta_text_color"]}; padding: 10px 16px; '
        f'border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.9em;">Check Price →</a>'
        f'</div>'
    )
