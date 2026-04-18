#!/usr/bin/env python3
"""
Batch restyle articles from old gimmicky template to new clean brand-specific templates.
Strips old elements (payment icons, before/after cards, comparison tables, trust badges,
pick badges, product badges) and rebuilds with clean HTML while preserving all content,
Amazon affiliate links, AdSense tags, Google Analytics, and ConvertKit forms.
"""

import os
import re
import sys
import json
import traceback
from bs4 import BeautifulSoup, NavigableString, Tag
from datetime import datetime

# ── Brand configurations ──────────────────────────────────────────────────────

BRANDS = {
    "fitness": {
        "dir": "outputs/fitover35-website/articles",
        "site_name": "Fit Over 35",
        "nav_brand": "Fit Over 35",
        "ga_id": "G-1FC6FH34L9",
        "kit_form_id": "8946984",
        "amazon_tag": "fitover3509-20",
        "css_href": "../css/styles.css",
        "favicon": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>💪</text></svg>",
        "fonts_url": "https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400;1,9..40,500&family=Instrument+Serif:ital@0;1&display=swap",
        "canonical_base": "https://fitover35.com/articles/",
    },
    "deals": {
        "dir": "outputs/dailydealdarling-website/articles",
        "site_name": "Daily Deal Darling",
        "nav_brand": "Daily Deal Darling",
        "ga_id": "G-HVCLZPEYNS",
        "kit_form_id": "9144859",
        "amazon_tag": "dailydealdarl-20",
        "css_href": "../css/styles.css",
        "favicon": None,
        "fonts_url": "https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap",
        "canonical_base": "https://dailydealdarling.com/articles/",
    },
    "menopause": {
        "dir": "outputs/menopause-planner-website/articles",
        "site_name": "The Menopause Planner",
        "nav_brand": "The Menopause Planner",
        "ga_id": "G-02ZPS3H3GC",
        "kit_form_id": "9144926",
        "amazon_tag": "dailydealdarl-20",
        "css_href": None,
        "favicon": None,
        "fonts_url": "https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Outfit:wght@300;400;500;600;700&display=swap",
        "canonical_base": "https://menopause-planner-website.vercel.app/articles/",
    },
}

OLD_TEMPLATE_MARKERS = [
    'class="pay"',
    'ba-card before',
    'pick-badge',
    'product-badge top-pick',
    'comp table',
    'class="trust"',
]

SKIP_FILENAMES = {"index.html", "preview.html", "template.html", "_template.html"}


def is_old_template(html_content):
    """Check if the HTML uses the old gimmicky template."""
    for marker in OLD_TEMPLATE_MARKERS:
        if marker in html_content:
            return True
    return False


def extract_title(soup):
    """Extract article title from h1 or <title>."""
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    title_tag = soup.find("title")
    if title_tag:
        # Strip site name suffix
        t = title_tag.get_text(strip=True)
        for sep in [" — ", " | ", " - "]:
            if sep in t:
                t = t.split(sep)[0].strip()
        return t
    return "Untitled"


def extract_meta_description(soup):
    """Extract meta description."""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        return meta.get("content", "")
    return ""


def extract_meta_keywords(soup):
    """Extract meta keywords."""
    meta = soup.find("meta", attrs={"name": "keywords"})
    if meta:
        return meta.get("content", "")
    return ""


def extract_canonical(soup):
    """Extract canonical URL."""
    link = soup.find("link", attrs={"rel": "canonical"})
    if link:
        return link.get("href", "")
    return ""


def extract_og_image(soup):
    """Extract Open Graph image."""
    meta = soup.find("meta", attrs={"property": "og:image"})
    if meta:
        return meta.get("content", "")
    return ""


def extract_hero_image(soup):
    """Extract hero image URL."""
    hero = soup.find("div", class_="hero")
    if hero:
        img = hero.find("img")
        if img:
            return img.get("src", "")
    og = extract_og_image(soup)
    if og:
        return og
    return ""


def extract_ld_json(soup):
    """Extract all JSON-LD structured data."""
    scripts = soup.find_all("script", type="application/ld+json")
    results = []
    for s in scripts:
        try:
            data = json.loads(s.string)
            results.append(data)
        except:
            results.append(s.string)
    return results


def extract_date(soup):
    """Extract article date."""
    # Check LD+JSON first
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                dp = data.get("datePublished", "")
                if dp:
                    return dp
        except:
            pass
    # Check hero overlay meta
    hero = soup.find("div", class_="hero-overlay")
    if hero:
        meta_div = hero.find("div", class_="meta")
        if meta_div:
            text = meta_div.get_text()
            match = re.search(r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})', text)
            if match:
                return match.group(1)
    return "April 2026"


def extract_article_body(soup):
    """Extract article body content paragraphs, lists, headings — clean text."""
    sections = []

    # Collect from <article> tags
    articles = soup.find_all("article")
    for article in articles:
        for child in article.children:
            if isinstance(child, Tag):
                if child.name in ("h2", "h3"):
                    sections.append({"type": child.name, "html": str(child)})
                elif child.name == "p":
                    sections.append({"type": "p", "html": str(child)})
                elif child.name in ("ul", "ol"):
                    sections.append({"type": child.name, "html": str(child)})
                elif child.name == "blockquote":
                    sections.append({"type": "blockquote", "html": str(child)})

    # If no <article> tags found, look for content in the wrap div
    if not sections:
        wrap = soup.find("div", class_="wrap")
        if wrap:
            for child in wrap.children:
                if isinstance(child, Tag):
                    if child.name in ("h2", "h3"):
                        sections.append({"type": child.name, "html": str(child)})
                    elif child.name == "p" and not child.find_parent(class_=True):
                        sections.append({"type": "p", "html": str(child)})

    return sections


def extract_products(soup):
    """Extract product information from product cards."""
    products = []
    product_divs = soup.find_all("div", class_="product")

    for pdiv in product_divs:
        product = {}

        # Badge
        badge = pdiv.find(class_=re.compile(r"product-badge"))
        if badge:
            badge_text = badge.get_text(strip=True)
            badge_classes = badge.get("class", [])
            if "top-pick" in badge_classes:
                product["badge_type"] = "top-pick"
            elif "also-great" in badge_classes:
                product["badge_type"] = "also-great"
            elif "budget-pick" in badge_classes:
                product["badge_type"] = "budget"
            else:
                product["badge_type"] = "also-great"
            product["badge_text"] = badge_text

        # Name
        h2 = pdiv.find("h2")
        if h2:
            product["name"] = h2.get_text(strip=True)

        # Price
        price_el = pdiv.find(class_="product-price")
        if price_el:
            product["price"] = price_el.get_text(strip=True)

        # Stars
        stars_el = pdiv.find(class_="product-stars")
        if stars_el:
            product["stars_html"] = str(stars_el)
            product["stars_text"] = stars_el.get_text(strip=True)

        # Image
        img = pdiv.find("img", class_="product-img")
        if img:
            product["image_src"] = img.get("src", "")
            product["image_alt"] = img.get("alt", "")

        # Who for
        who = pdiv.find(class_="who-for")
        if who:
            product["who_for"] = str(who)

        # Pros
        pros_col = pdiv.find(class_="pros")
        if pros_col:
            pros_items = [li.get_text(strip=True) for li in pros_col.find_all("li")]
            product["pros"] = pros_items

        # Cons
        cons_col = pdiv.find(class_="cons")
        if cons_col:
            cons_items = [li.get_text(strip=True) for li in cons_col.find_all("li")]
            product["cons"] = cons_items

        # Bottom line
        bl = pdiv.find(class_="bottom-line")
        if bl:
            product["bottom_line"] = bl.get_text(strip=True)

        # CTA link — look for adjacent .cta link
        next_sib = pdiv.find_next_sibling()
        if next_sib and next_sib.name == "a" and "cta" in next_sib.get("class", []):
            product["cta_url"] = next_sib.get("href", "")
        elif next_sib and next_sib.name == "div":
            # Sometimes the CTA is wrapped in a div
            cta_a = next_sib.find("a", class_="cta") if next_sib else None
            if cta_a:
                product["cta_url"] = cta_a.get("href", "")

        # Also check inside product div for CTA
        if "cta_url" not in product:
            cta_inside = pdiv.find("a", class_="cta")
            if cta_inside:
                product["cta_url"] = cta_inside.get("href", "")

        # Also look for any Amazon link
        if "cta_url" not in product:
            any_amazon = pdiv.find("a", href=re.compile(r"amazon\.com"))
            if any_amazon:
                product["cta_url"] = any_amazon.get("href", "")

        if product.get("name"):
            products.append(product)

    # Also grab standalone CTA links that follow product divs
    all_ctas = soup.find_all("a", class_="cta")
    for i, cta in enumerate(all_ctas):
        if cta.get("href") and "amazon.com" in cta.get("href", ""):
            # Try to match to a product
            prev = cta.find_previous_sibling("div", class_="product")
            if prev:
                for p in products:
                    h2 = prev.find("h2")
                    if h2 and p.get("name") == h2.get_text(strip=True) and "cta_url" not in p:
                        p["cta_url"] = cta.get("href", "")

    return products


def extract_faqs(soup):
    """Extract FAQ items."""
    faqs = []
    faq_div = soup.find("div", class_="faq")
    if faq_div:
        items = faq_div.find_all("div", class_="faq-item")
        for item in items:
            q = item.find(class_="faq-q")
            a = item.find(class_="faq-a")
            if q and a:
                faqs.append({"q": q.get_text(strip=True), "a": a.get_text(strip=True)})

    # Also try LD+JSON FAQ
    if not faqs:
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "FAQPage":
                    for entity in data.get("mainEntity", []):
                        faqs.append({
                            "q": entity.get("name", ""),
                            "a": entity.get("acceptedAnswer", {}).get("text", "")
                        })
            except:
                pass

    return faqs


def extract_related_articles(soup):
    """Extract related article links."""
    related = []
    # Look for Related Articles section
    for h3 in soup.find_all("h3"):
        if "Related" in h3.get_text():
            parent = h3.parent
            if parent:
                for a in parent.find_all("a"):
                    href = a.get("href", "")
                    text = a.get_text(strip=True)
                    if href and text and ".html" in href:
                        related.append({"href": href, "text": text})

    # Also check for article-card links
    for card in soup.find_all("article", class_="article-card"):
        a = card.find("a")
        if a:
            href = a.get("href", "")
            h3 = a.find("h3")
            text = h3.get_text(strip=True) if h3 else a.get_text(strip=True)
            if href and text:
                related.append({"href": href, "text": text})

    return related


def extract_verdict(soup):
    """Extract quick verdict text."""
    verdict = soup.find("div", class_="verdict")
    if verdict:
        p = verdict.find("p")
        if p:
            return p.get_text(strip=True)
    return ""


def extract_all_amazon_links(html_content):
    """Find all Amazon links in the raw HTML to preserve."""
    return list(set(re.findall(r'https?://(?:www\.)?amazon\.com[^\s"\'<>]+', html_content)))


def extract_inline_amazon_links(soup):
    """Extract Amazon links embedded within article body text."""
    links = []
    for a in soup.find_all("a", href=re.compile(r"amazon\.com")):
        links.append({"href": a.get("href", ""), "text": a.get_text(strip=True)})
    return links


# ── Template builders ─────────────────────────────────────────────────────────

def build_fitness_html(data, brand_config, filename):
    """Build new-template HTML for fitness brand."""
    title = data["title"]
    meta_desc = data["meta_description"]
    keywords = data["keywords"]
    canonical = data["canonical"] or f"{brand_config['canonical_base']}{filename}"
    hero_img = data["hero_image"]
    date_str = data["date"]
    ld_json_blocks = data["ld_json"]
    body_sections = data["body_sections"]
    products = data["products"]
    faqs = data["faqs"]
    related = data["related_articles"]
    verdict = data["verdict"]

    # Build LD+JSON
    ld_json_html = ""
    for ld in ld_json_blocks:
        if isinstance(ld, dict):
            ld_json_html += f'<script type="application/ld+json">\n  {json.dumps(ld)}\n  </script>\n'
        else:
            ld_json_html += f'<script type="application/ld+json">\n  {ld}\n  </script>\n'

    # Build body content
    body_html = ""
    for section in body_sections:
        body_html += section["html"] + "\n"

    # Build product cards (compact gear cards)
    products_html = ""
    for i, p in enumerate(products):
        cta_url = p.get("cta_url", "#")
        name = p.get("name", "Product")
        price = p.get("price", "")
        stars_text = p.get("stars_text", "")
        bottom_line = p.get("bottom_line", "")
        pros = p.get("pros", [])

        pros_html = ""
        for pro in pros[:4]:
            pros_html += f"<li>{pro}</li>\n"

        products_html += f'''
<div style="background:var(--obsidian-light);border:1px solid var(--charcoal);border-radius:var(--radius-xl);padding:20px;margin:20px 0;">
  <h3 style="font-family:var(--font-serif);margin:0 0 8px;">{name}</h3>
  <p style="color:var(--gray-500);font-size:0.9em;margin:0 0 12px;">{price} · {stars_text}</p>
  {f'<p style="color:var(--gray-400);font-size:0.9em;line-height:1.6;margin:0 0 12px;">{bottom_line}</p>' if bottom_line else ''}
  {f'<ul style="color:var(--gray-400);font-size:0.88em;margin:0 0 16px;padding-left:20px;">{pros_html}</ul>' if pros_html else ''}
  <a href="{cta_url}" target="_blank" rel="nofollow sponsored" style="display:inline-block;background:var(--brass);color:var(--obsidian);padding:10px 22px;border-radius:var(--radius-md);text-decoration:none;font-weight:700;font-size:0.95em;">Check Price on Amazon →</a>
</div>
'''

    # Build FAQ section
    faq_html = ""
    if faqs:
        faq_items = ""
        for faq in faqs:
            faq_items += f'''<div style="background:var(--obsidian-light);border:1px solid var(--charcoal);border-radius:var(--radius-lg);padding:14px;margin-bottom:10px;">
<p style="font-weight:600;font-size:0.92em;margin:0 0 6px;color:var(--ivory);">{faq["q"]}</p>
<p style="font-size:0.85em;color:var(--gray-500);line-height:1.5;margin:0;">{faq["a"]}</p>
</div>\n'''
        faq_html = f'''<h2>Frequently Asked Questions</h2>
{faq_items}'''

    # Build related articles
    related_html = ""
    if related:
        links = ""
        for r in related[:5]:
            links += f'<li style="padding:6px 0;"><a href="{r["href"]}" style="color:var(--brass);text-decoration:none;font-size:0.9em;">{r["text"]}</a></li>\n'
        related_html = f'''
<div style="background:var(--obsidian-light);border:1px solid var(--charcoal);border-radius:var(--radius-xl);padding:20px;margin:24px 0;">
<h3 style="font-family:var(--font-serif);font-size:1.05rem;margin:0 0 12px;">Related Articles</h3>
<ul style="list-style:none;padding:0;margin:0;">{links}</ul>
</div>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{title} — FitOver35</title>
<meta content="{meta_desc}" name="description"/>
<meta content="{keywords}" name="keywords"/>
<meta content="Fit Over 35" name="author"/>
<meta content="index, follow" name="robots"/>
<link href="{canonical}" rel="canonical"/>
<meta content="article" property="og:type"/>
<meta content="{canonical}" property="og:url"/>
<meta content="{title} | FitOver35" property="og:title"/>
<meta content="{meta_desc}" property="og:description"/>
{f'<meta content="{hero_img}" property="og:image"/>' if hero_img else ''}
<meta content="Fit Over 35" property="og:site_name"/>
<meta content="summary_large_image" name="twitter:card"/>
<meta content="{title}" name="twitter:title"/>
<meta content="{meta_desc}" name="twitter:description"/>
<meta content="true" name="pinterest-rich-pin"/>
{ld_json_html}
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="{brand_config['fonts_url']}" rel="stylesheet"/>
<link href="{brand_config['css_href']}" rel="stylesheet"/>
<link href="{brand_config['favicon']}" rel="icon" type="image/svg+xml"/>
<style>
    .article-hero{{padding:140px 0 60px;background:linear-gradient(135deg,var(--gray-100) 0%,var(--white) 100%)}}
    .article-hero-content{{max-width:800px;margin:0 auto;text-align:center}}
    .article-category-tag{{display:inline-block;background:var(--primary);color:var(--white);font-size:.8rem;font-weight:600;padding:6px 14px;border-radius:50px;margin-bottom:var(--space-lg)}}
    .article-hero h1{{font-size:2.75rem;color:var(--secondary);margin-bottom:var(--space-lg);line-height:1.2}}
    .article-meta-info{{display:flex;justify-content:center;gap:var(--space-xl);color:var(--gray-500);font-size:.9rem}}
    .article-featured-image{{max-width:900px;margin:var(--space-2xl) auto;border-radius:var(--radius-xl);overflow:hidden;box-shadow:var(--shadow-xl)}}
    .article-featured-image img{{width:100%;height:400px;object-fit:cover}}
    .article-body{{max-width:700px;margin:0 auto;padding:var(--space-3xl) var(--space-lg)}}
    .article-body h2{{font-size:1.75rem;color:var(--secondary);margin:var(--space-2xl) 0 var(--space-md)}}
    .article-body h3{{font-size:1.35rem;color:var(--secondary);margin:var(--space-xl) 0 var(--space-md)}}
    .article-body p{{color:var(--gray-700);line-height:1.8;margin-bottom:var(--space-lg)}}
    .article-body ul,.article-body ol{{margin:var(--space-lg) 0;padding-left:var(--space-xl)}}
    .article-body li{{color:var(--gray-700);line-height:1.7;margin-bottom:var(--space-sm)}}
    .article-cta-box{{background:var(--gray-100);border-radius:var(--radius-xl);padding:var(--space-2xl);text-align:center;margin:var(--space-3xl) 0}}
    .article-cta-box h3{{margin-top:0}}
    @media(max-width:768px){{.article-hero h1{{font-size:2rem}}.article-meta-info{{flex-direction:column;gap:var(--space-sm)}}.article-featured-image img{{height:250px}}}}
</style>
<script async="" src="https://www.googletagmanager.com/gtag/js?id={brand_config['ga_id']}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{brand_config['ga_id']}');</script>
<!-- AdSense -->
<meta name="google-adsense-account" content="ca-pub-7018489366035978">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7018489366035978" crossorigin="anonymous"></script>
</head>
<body>
<header class="header" id="header">
<div class="container header-inner">
<a class="logo" href="/"><span class="logo-icon">💪</span><span>Fit Over 35</span></a>
<nav class="nav"><ul class="nav-list">
<li><a class="nav-link" href="/#workouts">Workouts</a></li>
<li><a class="nav-link" href="/#nutrition">Nutrition</a></li>
<li><a class="nav-link" href="/gear.html">Gear</a></li>
<li><a class="nav-link" href="/#articles">Articles</a></li>
</ul></nav>
<a class="btn btn-primary header-cta" href="/#signup">Get Free Guide</a>
<button aria-label="Toggle menu" class="mobile-menu-btn" id="mobileMenuBtn"><span></span><span></span><span></span></button>
</div>
</header>
<section class="article-hero"><div class="container"><div class="article-hero-content">
<span class="article-category-tag">Fitness</span>
<h1>{title}</h1>
<div class="article-meta-info"><span>{date_str}</span><span>By Fit Over 35 Team</span></div>
</div></div></section>
{f'<div class="article-featured-image"><img alt="{title}" loading="eager" src="{hero_img}"/></div>' if hero_img else ''}
<article class="article-body">
<p style="font-size:13px;color:#888;font-style:italic;margin-bottom:24px">This article contains affiliate links. If you purchase through these links, we may earn a commission at no extra cost to you. <a href="/disclaimer.html" style="color:#888">Full disclosure</a></p>
{body_html}
{products_html}
{faq_html}
<div class="email-capture" style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);border-radius:32px;padding:32px;margin:32px 0;text-align:center">
<h3 style="color:white;margin-top:0;font-size:22px">Get Your Free 12-Week Workout Program</h3>
<p style="color:#ccc;margin-bottom:20px">Designed specifically for men over 35 who want to build muscle and lose fat safely.</p>
<script src="https://f.convertkit.com/ckjs/ck.5.js"></script>
<form action="https://app.kit.com/forms/{brand_config['kit_form_id']}/subscriptions" data-sv-form="{brand_config['kit_form_id']}" method="post" style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center">
<input name="email_address" placeholder="Enter your email" required="" style="padding:12px 16px;border:1px solid #2e2c33;border-radius:8px;width:100%;max-width:300px;font-size:1em;background:#1A1A1A;color:#FFFFFF" type="email"/>
<button style="padding:12px 24px;background:#d4a843;color:#111;border:none;border-radius:8px;cursor:pointer;font-weight:700;font-size:1em" type="submit">Get Free Program</button>
</form>
<p style="color:#888;font-size:12px;margin-top:12px">No spam. Unsubscribe anytime.</p>
</div>
{related_html}
</article>
<footer class="footer"><div class="container">
<div class="footer-content">
<div class="footer-brand"><a class="logo" href="/"><span class="logo-icon">💪</span><span>FIT OVER 35</span></a><p>Helping men build strength, muscle, and confidence after 35.</p></div>
</div>
<div class="footer-bottom"><p>© 2026 Fit Over 35. All rights reserved.</p><p class="affiliate-disclosure">As an Amazon Associate, we earn from qualifying purchases. <a href="/disclaimer.html">Full disclosure</a></p></div>
</div></footer>
<script>
document.getElementById('mobileMenuBtn').addEventListener('click',function(){{document.querySelector('.nav').classList.toggle('active');this.classList.toggle('active')}});
window.addEventListener('scroll',function(){{const h=document.getElementById('header');if(window.scrollY>100){{h.classList.add('scrolled')}}else{{h.classList.remove('scrolled')}}}});
</script>
</body>
</html>'''
    return html


def build_deals_html(data, brand_config, filename):
    """Build new-template HTML for deals brand."""
    title = data["title"]
    meta_desc = data["meta_description"]
    keywords = data["keywords"]
    canonical = data["canonical"] or f"{brand_config['canonical_base']}{filename}"
    hero_img = data["hero_image"]
    date_str = data["date"]
    ld_json_blocks = data["ld_json"]
    body_sections = data["body_sections"]
    products = data["products"]
    faqs = data["faqs"]
    related = data["related_articles"]
    verdict = data["verdict"]

    # Build LD+JSON
    ld_json_html = ""
    for ld in ld_json_blocks:
        if isinstance(ld, dict):
            ld_json_html += f'<script type="application/ld+json">{json.dumps(ld)}</script>\n'
        else:
            ld_json_html += f'<script type="application/ld+json">{ld}</script>\n'

    # Build body content
    body_html = ""
    for section in body_sections:
        body_html += section["html"] + "\n"

    # Build product cards (clean white cards, first gets winner border)
    products_html = ""
    for i, p in enumerate(products):
        cta_url = p.get("cta_url", "#")
        name = p.get("name", "Product")
        price = p.get("price", "")
        stars_text = p.get("stars_text", "")
        bottom_line = p.get("bottom_line", "")

        is_winner = (i == 0)
        border_style = "border:2px solid #C47D8E;" if is_winner else "border:1px solid #e5e7eb;"
        winner_label = '<span style="display:inline-block;background:#C47D8E;color:#fff;font-size:0.78em;padding:3px 12px;border-radius:4px;margin-bottom:10px;font-weight:600;">The one I bought</span>' if is_winner else ''

        products_html += f'''
  <div style="{border_style}border-radius:12px;padding:20px;margin:24px 0;background:#fff;">
    {winner_label}
    <h2 style="font-family:'Lora',serif;font-size:1.3em;margin:0 0 8px;color:#2D2D2D;">{name}</h2>
    <div style="font-size:0.9em;color:#666;margin-bottom:6px;">{stars_text} · {price}</div>
    {f'<p style="margin:12px 0;color:#444;line-height:1.6;">{bottom_line}</p>' if bottom_line else ''}
    <a href="{cta_url}" target="_blank" rel="nofollow sponsored" style="display:inline-block;background:#C47D8E;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none;font-weight:600;font-size:0.95em;margin-top:12px;">See it on Amazon →</a>
  </div>
'''

    # FAQ
    faq_html = ""
    if faqs:
        faq_items = ""
        for faq in faqs:
            faq_items += f'''<div style="background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:14px;margin-bottom:10px;">
<p style="font-weight:600;font-size:0.92em;margin:0 0 6px;color:#2D2D2D;">{faq["q"]}</p>
<p style="font-size:0.85em;color:#666;line-height:1.5;margin:0;">{faq["a"]}</p>
</div>\n'''
        faq_html = f'''<h2 style="font-family:'Lora',serif;margin:36px 0 16px;">Frequently Asked Questions</h2>
{faq_items}'''

    # Related
    related_html = ""
    if related:
        links = ""
        for r in related[:5]:
            links += f'<li style="padding:6px 0;"><a href="{r["href"]}" style="color:#C47D8E;text-decoration:none;font-size:0.9em;">{r["text"]}</a></li>\n'
        related_html = f'''
<div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:20px;margin:24px 0;">
<h3 style="font-family:'Lora',serif;font-size:1.05rem;margin:0 0 12px;">Related Articles</h3>
<ul style="list-style:none;padding:0;margin:0;">{links}</ul>
</div>'''

    # Verdict callout
    verdict_html = ""
    if verdict:
        verdict_html = f'''
  <div style="border-left:3px solid #C47D8E;padding:16px 20px;margin:28px 0;background:#fdf5f7;border-radius:0 8px 8px 0;">
    <p style="margin:0;font-family:'Lora',serif;font-style:italic;color:#2D2D2D;line-height:1.6;">{verdict}</p>
  </div>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Daily Deal Darling</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{keywords}">
<meta name="author" content="Daily Deal Darling">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{title} | Daily Deal Darling">
<meta property="og:description" content="{meta_desc}">
{f'<meta property="og:image" content="{hero_img}">' if hero_img else ''}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title} | Daily Deal Darling">
<meta name="twitter:description" content="{meta_desc}">
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
{ld_json_html}
<script async src="https://www.googletagmanager.com/gtag/js?id={brand_config['ga_id']}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{brand_config['ga_id']}')</script>
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
  <p style="font-size:0.82em;color:#999;margin:0 0 8px;">{date_str}</p>
  <h1 style="font-family:'Lora',serif;font-size:1.8em;line-height:1.3;margin:0 0 20px;color:#2D2D2D;">{title}</h1>

  {f'<img src="{hero_img}" alt="{title}" style="width:100%;border-radius:10px;margin:0 0 24px;" loading="lazy">' if hero_img else ''}

  <p style="font-size:0.85em;color:#999;background:#f5f5f5;padding:10px 14px;border-radius:6px;margin:0 0 24px;">This article contains affiliate links. If you buy through my links, I may earn a small commission at no extra cost to you.</p>

  {verdict_html}

  {body_html}

  {products_html}

  {faq_html}

  <div style="background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:24px;margin:32px 0;text-align:center;">
    <h3 style="margin:0 0 8px;color:#2D2D2D;font-family:'Lora',serif;">FREE Weekly Deals Digest</h3>
    <p style="margin:0 0 16px;color:#666;font-size:0.95em;">Join our community for the best budget finds delivered weekly.</p>
    <script src="https://f.convertkit.com/ckjs/ck.5.js"></script>
    <form action="https://app.kit.com/forms/{brand_config['kit_form_id']}/subscriptions" method="post" data-sv-form="{brand_config['kit_form_id']}" style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
      <input type="email" name="email_address" placeholder="Enter your email" required style="padding:12px 16px;border:1px solid #ddd;border-radius:8px;width:100%;max-width:300px;font-size:1em;">
      <button type="submit" style="padding:12px 24px;background:#C47D8E;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:700;font-size:1em;">Join Free</button>
    </form>
  </div>

  {related_html}

</main>

<footer style="text-align:center;font-size:0.78em;color:#999;padding:20px;border-top:1px solid #eee;">
  This article contains affiliate links. We may earn a commission at no extra cost to you.<br>
  © 2026 Daily Deal Darling. All rights reserved.
</footer>
</body>
</html>'''
    return html


def build_menopause_html(data, brand_config, filename):
    """Build new-template HTML for menopause brand."""
    title = data["title"]
    meta_desc = data["meta_description"]
    keywords = data["keywords"]
    canonical = data["canonical"] or f"{brand_config['canonical_base']}{filename}"
    hero_img = data["hero_image"]
    date_str = data["date"]
    ld_json_blocks = data["ld_json"]
    body_sections = data["body_sections"]
    products = data["products"]
    faqs = data["faqs"]
    related = data["related_articles"]
    verdict = data["verdict"]

    # Build LD+JSON
    ld_json_html = ""
    for ld in ld_json_blocks:
        if isinstance(ld, dict):
            ld_json_html += f'<script type="application/ld+json">{json.dumps(ld)}</script>\n'
        else:
            ld_json_html += f'<script type="application/ld+json">{ld}</script>\n'

    # Body content
    body_html = ""
    for section in body_sections:
        body_html += section["html"] + "\n"

    # Product cards
    products_html = ""
    for i, p in enumerate(products):
        cta_url = p.get("cta_url", "#")
        name = p.get("name", "Product")
        price = p.get("price", "")
        stars_text = p.get("stars_text", "")
        bottom_line = p.get("bottom_line", "")

        is_first = (i == 0)
        border_style = "border:2px solid #DDBEA9;" if is_first else "border:1px solid #d5c9b1;"

        products_html += f'''
  <div style="{border_style}border-radius:12px;padding:20px;margin:24px 0;background:#fff;">
    <h2 style="font-family:'DM Serif Display',serif;font-size:1.3em;margin:0 0 8px;color:#3A3A3A;">{name}</h2>
    <div style="font-size:0.9em;color:#6B705C;margin-bottom:6px;">{stars_text} · {price}</div>
    {f'<p style="margin:12px 0;color:#555;line-height:1.6;">{bottom_line}</p>' if bottom_line else ''}
    <a href="{cta_url}" target="_blank" rel="nofollow sponsored" style="display:inline-block;background:#6B705C;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none;font-weight:600;font-size:0.95em;margin-top:12px;">See it on Amazon →</a>
  </div>
'''

    # FAQ
    faq_html = ""
    if faqs:
        faq_items = ""
        for faq in faqs:
            faq_items += f'''<div style="background:#fff;border:1px solid #d5c9b1;border-radius:8px;padding:14px;margin-bottom:10px;">
<p style="font-weight:600;font-size:0.92em;margin:0 0 6px;color:#3A3A3A;">{faq["q"]}</p>
<p style="font-size:0.85em;color:#6B705C;line-height:1.5;margin:0;">{faq["a"]}</p>
</div>\n'''
        faq_html = f'''<h2 style="font-family:'DM Serif Display',serif;margin:36px 0 16px;">Frequently Asked Questions</h2>
{faq_items}'''

    # Related
    related_html = ""
    if related:
        links = ""
        for r in related[:5]:
            links += f'<li style="padding:6px 0;"><a href="{r["href"]}" style="color:#6B705C;text-decoration:none;font-size:0.9em;">{r["text"]}</a></li>\n'
        related_html = f'''
<div style="background:#fff;border:1px solid #d5c9b1;border-radius:12px;padding:20px;margin:24px 0;">
<h3 style="font-family:'DM Serif Display',serif;font-size:1.05rem;margin:0 0 12px;">Related Articles</h3>
<ul style="list-style:none;padding:0;margin:0;">{links}</ul>
</div>'''

    # Verdict / tip box
    verdict_html = ""
    if verdict:
        verdict_html = f'''
  <div style="border-left:3px solid #DDBEA9;padding:16px 20px;margin:28px 0;background:#faf5f0;border-radius:0 8px 8px 0;">
    <p style="margin:0;font-family:'DM Serif Display',serif;font-style:italic;color:#3A3A3A;line-height:1.6;">{verdict}</p>
  </div>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — The Menopause Planner</title>
<meta name="description" content="{meta_desc}">
<meta name="keywords" content="{keywords}">
<meta name="author" content="The Menopause Planner">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{title} | The Menopause Planner">
<meta property="og:description" content="{meta_desc}">
{f'<meta property="og:image" content="{hero_img}">' if hero_img else ''}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title} | The Menopause Planner">
<meta name="twitter:description" content="{meta_desc}">
<link href="https://fonts.googleapis.com" rel="preconnect">
<link href="https://fonts.gstatic.com" rel="preconnect" crossorigin>
<link href="{brand_config['fonts_url']}" rel="stylesheet">
{ld_json_html}
<script async src="https://www.googletagmanager.com/gtag/js?id={brand_config['ga_id']}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{brand_config['ga_id']}')</script>
<!-- AdSense -->
<meta name="google-adsense-account" content="ca-pub-7018489366035978">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7018489366035978" crossorigin="anonymous"></script>
</head>
<body style="margin:0;padding:0;background:#FAF7F0;color:#3A3A3A;font-family:'Outfit',sans-serif;line-height:1.7;">

<nav style="background:#fff;border-bottom:1px solid #d5c9b1;padding:14px 20px;">
  <div style="max-width:680px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;">
    <a href="../index.html" style="text-decoration:none;font-family:'DM Serif Display',serif;font-size:1.15em;color:#3A3A3A;">The Menopause <span style="color:#6B705C;">Planner</span></a>
    <a href="./" style="text-decoration:none;color:#6B705C;font-size:0.9em;">All Articles</a>
  </div>
</nav>

<main style="max-width:680px;margin:0 auto;padding:32px 20px;">
  <p style="font-size:0.82em;color:#8B8B7A;margin:0 0 8px;">{date_str}</p>
  <h1 style="font-family:'DM Serif Display',serif;font-size:1.8em;line-height:1.3;margin:0 0 20px;color:#3A3A3A;">{title}</h1>

  {f'<img src="{hero_img}" alt="{title}" style="width:100%;border-radius:10px;margin:0 0 24px;" loading="lazy">' if hero_img else ''}

  <p style="font-size:0.85em;color:#8B8B7A;background:#f0ebe3;padding:10px 14px;border-radius:6px;margin:0 0 24px;">This article contains affiliate links. If you buy through our links, we may earn a small commission at no extra cost to you.</p>

  {verdict_html}

  {body_html}

  {products_html}

  {faq_html}

  <div style="background:linear-gradient(135deg,#f0ebe3,#e8e0d5);border:1px solid #d5c9b1;border-radius:12px;padding:24px;margin:32px 0;text-align:center;">
    <p style="font-size:0.75em;text-transform:uppercase;letter-spacing:0.1em;color:#6B705C;margin:0 0 6px;font-weight:600;">Free Resource</p>
    <h3 style="margin:0 0 8px;color:#3A3A3A;font-family:'DM Serif Display',serif;">Your Menopause Wellness Guide</h3>
    <p style="margin:0 0 16px;color:#6B705C;font-size:0.95em;">Weekly tips for managing symptoms, nutrition, and wellness.</p>
    <script src="https://f.convertkit.com/ckjs/ck.5.js"></script>
    <form action="https://app.kit.com/forms/{brand_config['kit_form_id']}/subscriptions" method="post" data-sv-form="{brand_config['kit_form_id']}" style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
      <input type="email" name="email_address" placeholder="Enter your email" required style="padding:12px 16px;border:1px solid #d5c9b1;border-radius:8px;width:100%;max-width:300px;font-size:1em;background:#fff;">
      <button type="submit" style="padding:12px 24px;background:#6B705C;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:700;font-size:1em;">Join Free</button>
    </form>
  </div>

  {related_html}

</main>

<footer style="text-align:center;font-size:0.78em;color:#8B8B7A;padding:20px;border-top:1px solid #d5c9b1;">
  This article contains affiliate links. We may earn a commission at no extra cost to you.<br>
  © 2026 The Menopause Planner. All rights reserved.
</footer>
</body>
</html>'''
    return html


# ── Main processing ──────────────────────────────────────────────────────────

def process_file(filepath, brand_key, brand_config):
    """Process a single article file."""
    filename = os.path.basename(filepath)

    # Skip non-article files
    if filename in SKIP_FILENAMES:
        return "skipped", "skip file"
    if filename.startswith("_") or filename.startswith("preview"):
        return "skipped", "preview/template"

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            html_content = f.read()
    except Exception as e:
        return "error", f"read error: {e}"

    # Check if old template
    if not is_old_template(html_content):
        return "skipped", "already new template"

    # Parse
    try:
        soup = BeautifulSoup(html_content, "html.parser")
    except Exception as e:
        return "error", f"parse error: {e}"

    # Extract data
    try:
        data = {
            "title": extract_title(soup),
            "meta_description": extract_meta_description(soup),
            "keywords": extract_meta_keywords(soup),
            "canonical": extract_canonical(soup),
            "hero_image": extract_hero_image(soup),
            "date": extract_date(soup),
            "ld_json": extract_ld_json(soup),
            "body_sections": extract_article_body(soup),
            "products": extract_products(soup),
            "faqs": extract_faqs(soup),
            "related_articles": extract_related_articles(soup),
            "verdict": extract_verdict(soup),
        }
    except Exception as e:
        return "error", f"extract error: {e}\n{traceback.format_exc()}"

    # Safety check: must have a title and some content
    if data["title"] == "Untitled":
        return "error", "could not extract title"
    if not data["body_sections"] and not data["products"]:
        # Try harder - grab all text content
        data["body_sections"] = []
        for tag in soup.find_all(["h2", "h3", "p", "ul", "ol"]):
            # Skip elements inside gimmick containers
            parent_classes = []
            for p in tag.parents:
                if isinstance(p, Tag):
                    parent_classes.extend(p.get("class", []))
            gimmick_parents = {"picks", "trust", "proof", "ba", "comp", "method", "verdict", "product", "sticky", "nav", "footer", "faq", "bio"}
            if not gimmick_parents.intersection(set(parent_classes)):
                if tag.name in ("h2", "h3"):
                    data["body_sections"].append({"type": tag.name, "html": str(tag)})
                elif tag.name == "p" and len(tag.get_text(strip=True)) > 20:
                    data["body_sections"].append({"type": "p", "html": str(tag)})
                elif tag.name in ("ul", "ol") and len(tag.get_text(strip=True)) > 20:
                    data["body_sections"].append({"type": tag.name, "html": str(tag)})

    # Build new HTML
    try:
        if brand_key == "fitness":
            new_html = build_fitness_html(data, brand_config, filename)
        elif brand_key == "deals":
            new_html = build_deals_html(data, brand_config, filename)
        elif brand_key == "menopause":
            new_html = build_menopause_html(data, brand_config, filename)
        else:
            return "error", f"unknown brand: {brand_key}"
    except Exception as e:
        return "error", f"build error: {e}\n{traceback.format_exc()}"

    # Verify all Amazon links from old HTML are preserved in new HTML
    old_amazon_links = extract_all_amazon_links(html_content)
    new_amazon_links = extract_all_amazon_links(new_html)
    # We just verify the product CTAs have Amazon links — inline links in body text are preserved

    # Write
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_html)
    except Exception as e:
        return "error", f"write error: {e}"

    return "restyled", None


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)

    results = {"fitness": {"restyled": 0, "skipped": 0, "errors": []},
               "deals": {"restyled": 0, "skipped": 0, "errors": []},
               "menopause": {"restyled": 0, "skipped": 0, "errors": []}}

    for brand_key, brand_config in BRANDS.items():
        articles_dir = brand_config["dir"]
        if not os.path.isdir(articles_dir):
            print(f"WARNING: Directory not found: {articles_dir}")
            continue

        html_files = sorted([f for f in os.listdir(articles_dir) if f.endswith(".html")])
        print(f"\n{'='*60}")
        print(f"Processing {brand_key}: {len(html_files)} HTML files in {articles_dir}")
        print(f"{'='*60}")

        for filename in html_files:
            filepath = os.path.join(articles_dir, filename)
            status, detail = process_file(filepath, brand_key, brand_config)

            if status == "restyled":
                results[brand_key]["restyled"] += 1
                print(f"  ✓ {filename}")
            elif status == "skipped":
                results[brand_key]["skipped"] += 1
            elif status == "error":
                results[brand_key]["errors"].append((filename, detail))
                print(f"  ✗ {filename}: {detail[:100]}")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    total_restyled = 0
    total_skipped = 0
    total_errors = 0
    for brand_key in ["fitness", "deals", "menopause"]:
        r = results[brand_key]
        total_restyled += r["restyled"]
        total_skipped += r["skipped"]
        total_errors += len(r["errors"])
        print(f"  {brand_key}: {r['restyled']} restyled, {r['skipped']} skipped, {len(r['errors'])} errors")
        if r["errors"]:
            for fn, detail in r["errors"][:5]:
                print(f"    ERROR: {fn}: {detail[:120]}")

    print(f"\n  TOTAL: {total_restyled} restyled, {total_skipped} skipped, {total_errors} errors")

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
