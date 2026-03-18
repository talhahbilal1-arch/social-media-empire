"""Brand-specific bridge page templates for high-converting Amazon affiliate articles.

Three mobile-first templates optimized for Pinterest traffic and Google Search:
- 'The Iron Standard' (fitness) — Dark, gritty, data-heavy
- 'The Wellness Whisper' (menopause) — Clean, empathetic, editorial
- 'The Aesthetic Edit' (deals) — Minimalist, boutique, magazine-style

All use Tailwind CSS (CDN), Schema.org JSON-LD (Article + Product + FAQPage),
expert reviewer bios, geo-SEO, product cards, comparison tables,
and mobile-first sticky CTAs.
"""

import json
import re
from datetime import datetime, timezone


# ── Template configuration per brand ───────────────────────────────────────

TEMPLATE_CONFIG = {
    'fitness': {
        'name': 'The Iron Standard',
        'tagline': 'Expert Verified',
        'font_import': 'family=Oswald:wght@400;500;600;700&family=Inter:wght@400;500;600;700',
        'heading_font': 'Oswald',
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
        'font_import': 'family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@400;500;600;700',
        'heading_font': 'Lora',
        'body_font': 'Inter',
        'colors': {
            'bg': '#FDF5E6', 'surface': '#FFFFFF', 'border': '#D2B48C',
            'accent': '#6B8E23', 'text': '#4A4A4A', 'muted': '#8B7355',
        },
        'expert': {
            'name': 'Editorial Team',
            'credentials': 'The Menopause Planner',
            'bio': ("Reviewed by our editorial team in consultation with certified "
                    "women's health practitioners and menopause specialists."),
            'initials': 'MP',
            'bg': '#6B8E23',
            'text_color': '#FFFFFF',
        },
        'cta_text': "View Today's Amazon Deal",
        'cta_bg': '#6B8E23',
        'cta_text_color': '#FFFFFF',
    },
    'deals': {
        'name': 'The Aesthetic Edit',
        'tagline': 'Trending on Pinterest',
        'font_import': 'family=Playfair+Display:wght@400;500;600;700&family=Inter:wght@400;500;600;700',
        'heading_font': 'Playfair Display',
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
    'fitness': 'Free: Home Gym Setup Checklist (PDF)',
    'deals': 'Free: Weekly Top 10 Deals Newsletter',
    'menopause': 'Free: Menopause Symptom Tracker (Printable PDF)',
}

# Brand affiliate tags
_BRAND_TAGS = {
    'fitness': 'fitover35-20',
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
    """
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
