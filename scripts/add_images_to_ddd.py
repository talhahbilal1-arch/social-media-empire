#!/usr/bin/env python3
"""
Image enhancer for dailydealdarling.com
1. Downloads Pexels lifestyle photos for every article card
2. Updates index.html + blog.html card thumbnails to use real images
3. Adds "Shop the Products" grid at the bottom of each article
   with live Amazon product images (m.media-amazon.com CDN)
"""

import os, re, json, time, sys
import requests
from pathlib import Path

PEXELS_KEY = "gk5p96fb8EeXzmAbUJa2oHA6NSHoNfT1pmNQmpojyIi6wSgPcALrGI0e"
SITE_DIR   = Path("outputs/dailydealdarling-website")
IMG_DIR    = SITE_DIR / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

# ── Pexels search terms per article slug ──────────────────────────────────────
ARTICLE_PEXELS = {
    # Kitchen
    "budget-kitchen-gadgets-under-20-that-save-time":              "kitchen gadgets tools cooking",
    "amazon-kitchen-finds-under-10-that-pros-are-loving-this-mont":"chef kitchen professional cooking",
    "viral-kitchen-gadgets-modern-must-haves-tiktok-finds":         "modern kitchen cooking tools",
    "kitchen-essentials-that-look-expensive-but-start-at-7":        "elegant kitchen counter styled",
    "kitchen-gadgets-under-15-for-healthy-eating-goals":            "healthy cooking vegetables meal prep",
    "the-8-kitchen-tool-replacing-expensive-appliances":            "food chopper manual kitchen",
    "8-kitchen-gadget-that-replaces-expensive-appliances":          "kitchen chopper vegetable prep",
    "timeless-kitchen-gadgets-that-never-go-out-of-style-grandma-": "vintage kitchen classic cooking tools",
    "non-plastic-kitchen-utensils-for-healthier-cooking":           "wooden kitchen utensils natural cooking",
    "kitchen-tools-were-replacing-in-2026-budget-friendly-upgrade": "new kitchen tools upgrade modern",
    "williams-sonoma-outlet-deals-premium-kitchen-finds-up-to-44-": "premium kitchen cookware luxury",
    # Home Organization
    "2026-home-organization-hacks-that-actually-work":              "home organization storage clean house",
    "8-storage-baskets-for-laundry-and-home-organization":          "storage baskets laundry organization",
    "bathroom-cabinet-organization-solutions":                      "bathroom organization cabinet storage",
    "kids-room-organization-that-actually-stays-organized":         "kids room organized toys storage",
    "label-makers-for-peak-home-organization":                      "label maker organization pantry",
    "spring-cleaning-organization-products-storage-deals":          "spring cleaning home organization",
    "spring-cleaning-prep-deals-organization-product-launches":     "spring cleaning supplies fresh home",
    "budget-walmart-storage-cabinets-for-home-organization-under-": "storage cabinet organizer home",
    # Beauty & Wellness
    "at-home-spa-night-essentials-and-setup":                       "spa night bath candles relax woman",
    "bath-products-that-feel-luxurious-under-20":                   "luxury bath products woman relaxing",
    "hair-tools-honest-review-and-comparison":                      "woman hair styling tools beauty",
    "skincare-routine-affordable-products-that-work":               "skincare routine woman beauty products",
    # Deals & Sales
    "wayfair-warehouse-clearance-up-to-60-off-furniture-storage":   "furniture living room home decor sale",
    "crate-barrel-clearance-home-deals-up-to-60-off":               "home decor elegant interior design",
    "presidents-day-mattress-furniture-sale-deals-2026":            "bedroom furniture mattress home",
    "tax-refund-smart-spending-best-home-upgrades-under-500":       "home upgrade improvement modern",
    "valentines-day-clearance-haul-deals-75-off":                   "valentines gifts pink hearts decor",
    "target-valentines-clearance-haul-75-percent-off":              "sale shopping clearance deals woman",
}

# ── Product labels per ASIN ───────────────────────────────────────────────────
# Used in the "Shop the Products" grid
ASIN_LABELS = {
    "B07FDJMC9Q": "Air Fryer",
    "B07TLZXRK2": "Knife Set",
    "B078RFVKNR": "Meal Prep Containers",
    "B07DFDS56B": "Organizer Bins",
    "B07P3SQCV3": "Silk Pillowcase",
    "B07D3KVL4Z": "LED Face Mask",
    "B0719RFLTQ": "Label Maker",
    "B073VB74FJ": "Drawer Dividers",
    "B000BD0RT0": "Magnesium Glycinate",
    "B004O2I9JO": "Fish Oil",
    "B001ARYU58": "Adjustable Dumbbells",
    "B003J9E5WO": "Kettlebell",
    "B07MHBJYRH": "Massage Gun",
    "B004164SRA": "Food Scale",
    "B01LZ2GH5O": "Protein Shaker",
    "B002DYIZEO": "Creatine Monohydrate",
    "B00GB85JR4": "Vitamin D3",
    "B078K18HYN": "Ashwagandha",
    "B000QSNYGI": "Protein Powder",
    "B00K6JUG40": "Collagen Peptides",
    "B01AVDVHTI": "Resistance Bands",
    "B001EJMS6K": "Pull-Up Bar",
    "B0040EKZDY": "Foam Roller",
}

def pexels_search(query, per_page=1, orientation="landscape"):
    """Fetch image URL from Pexels."""
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": per_page, "orientation": orientation,
                    "size": "medium"},
            timeout=15
        )
        r.raise_for_status()
        photos = r.json().get("photos", [])
        if photos:
            return photos[0]["src"]["large"]  # ~1200px wide
    except Exception as e:
        print(f"  Pexels error for '{query}': {e}")
    return None

def download_image(url, dest_path):
    """Download an image from URL to dest_path."""
    if dest_path.exists():
        print(f"  [skip] {dest_path.name} already exists")
        return True
    try:
        r = requests.get(url, timeout=20, stream=True)
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        print(f"  [ok]   downloaded {dest_path.name} ({dest_path.stat().st_size//1024}KB)")
        return True
    except Exception as e:
        print(f"  [err]  {dest_path.name}: {e}")
        return False

def fetch_all_images():
    """Download Pexels images for all articles + hero images."""
    print("\n── Downloading Pexels images ────────────────────────────────")
    # Category hero images for index page sections
    HEROES = {
        "hero":     "woman shopping happy smiling lifestyle",
        "kitchen":  "beautiful kitchen cooking woman",
        "home":     "organized home interior storage",
        "beauty":   "skincare beauty woman morning routine",
        "deals":    "woman shopping sale happy bags",
    }
    for name, query in HEROES.items():
        dest = IMG_DIR / f"hero-{name}.jpg"
        if dest.exists():
            print(f"  [skip] {dest.name}")
            continue
        url = pexels_search(query, per_page=3, orientation="landscape")
        if url:
            download_image(url, dest)
        time.sleep(0.3)

    # Per-article images
    for slug, query in ARTICLE_PEXELS.items():
        dest = IMG_DIR / f"{slug}.jpg"
        url = pexels_search(query)
        if url:
            download_image(url, dest)
        time.sleep(0.3)

    print(f"\n  Total images in /images/: {len(list(IMG_DIR.glob('*.jpg')))}")

# ── HTML patchers ─────────────────────────────────────────────────────────────

CARD_THUMB_RE = re.compile(
    r'(<div class="(?:blog-card|card)__thumb[^"]*"[^>]*>)\s*[^<]*\s*(</div>)',
    re.DOTALL
)

def make_thumb_style(slug):
    """Return inline background-image style if image exists."""
    img_path = IMG_DIR / f"{slug}.jpg"
    if img_path.exists():
        return f'../images/{slug}.jpg'
    return None

def patch_card_thumbs_in_file(html_path, slug_map):
    """
    Replace emoji content inside card thumbs with <img> tags.
    slug_map: { card_href_fragment: image_slug }
    """
    with open(html_path) as f:
        html = f.read()

    # Find all <a href="articles/SLUG" class="blog-card"> or card links
    # and replace the thumb div inside them
    def replace_card(m):
        full = m.group(0)
        # Find the href
        href_m = re.search(r'href="articles/([^"]+)"', full)
        if not href_m:
            return full
        slug = href_m.group(1)
        img_path = IMG_DIR / f"{slug}.jpg"
        if not img_path.exists():
            return full
        rel_path = f"images/{slug}.jpg"
        # Replace the thumb div content
        full = re.sub(
            r'(<div class="(?:blog-card|card)__thumb[^"]*")([^>]*)>\s*[^<]*\s*</div>',
            lambda tm: (
                f'{tm.group(1)}{tm.group(2)} style="background-image:url({rel_path});'
                'background-size:cover;background-position:center"></div>'
            ),
            full
        )
        return full

    # Match entire <a ...>...</a> blocks for cards
    card_re = re.compile(
        r'<a\s+href="articles/[^"]+"\s+class="(?:blog-card|card)"[^>]*>.*?</a>',
        re.DOTALL
    )
    html = card_re.sub(replace_card, html)

    with open(html_path, "w") as f:
        f.write(html)
    print(f"  [ok] patched thumbnails in {html_path.name}")

def patch_hero_image(html_path):
    """Add background-image to hero section."""
    hero_img = IMG_DIR / "hero-hero.jpg"
    if not hero_img.exists():
        return
    with open(html_path) as f:
        html = f.read()

    # Find hero section and inject background image
    html = html.replace(
        '<section class="hero">',
        '<section class="hero" style="background-image:url(images/hero-hero.jpg);'
        'background-size:cover;background-position:center 40%;">'
    )
    with open(html_path, "w") as f:
        f.write(html)
    print(f"  [ok] added hero image to {html_path.name}")

# ── Article: add "Shop the Products" section ─────────────────────────────────

SHOP_CSS = """
<style>
.shop-section { margin: 40px 0; padding: 28px; background: #FFF5F8; border-radius: 14px; border: 1px solid #FBCFE8; }
.shop-section h3 { font-size: 1.1rem; font-weight: 800; color: #1A1A2E; margin-bottom: 18px; }
.shop-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 14px; }
.shop-item { background: #fff; border-radius: 10px; overflow: hidden; border: 1px solid #E5E7EB; text-align: center; text-decoration: none; color: inherit; display: flex; flex-direction: column; transition: box-shadow 0.2s; }
.shop-item:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.1); }
.shop-item img { width: 100%; height: 130px; object-fit: contain; padding: 10px; background: #fff; }
.shop-item-label { padding: 8px 10px 10px; font-size: 0.75rem; font-weight: 600; color: #374151; line-height: 1.3; flex: 1; }
.shop-item-cta { display: block; padding: 7px; background: #E91E63; color: #fff !important; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.03em; }
</style>
"""

def extract_asins(html):
    """Extract all Amazon ASINs from affiliate links in an article."""
    asins = re.findall(r'amazon\.com/dp/([A-Z0-9]{10})', html)
    # Deduplicate preserving order
    seen = set()
    result = []
    for a in asins:
        if a not in seen:
            seen.add(a)
            result.append(a)
    return result

def build_shop_section(asins, affiliate_tag="dailydealdarl-20"):
    """Build HTML for the Shop the Products section."""
    if not asins:
        return ""
    items_html = ""
    for asin in asins:
        label = ASIN_LABELS.get(asin, "View Product")
        img_url = f"https://m.media-amazon.com/images/P/{asin}._SL300_.jpg"
        buy_url = f"https://www.amazon.com/dp/{asin}?tag={affiliate_tag}"
        items_html += f"""
        <a href="{buy_url}" class="shop-item" target="_blank" rel="nofollow sponsored">
          <img src="{img_url}" alt="{label}" loading="lazy">
          <span class="shop-item-label">{label}</span>
          <span class="shop-item-cta">Buy on Amazon →</span>
        </a>"""

    return f"""
{SHOP_CSS}
<div class="shop-section">
  <h3>🛒 Shop the Products in This Article</h3>
  <div class="shop-grid">{items_html}
  </div>
</div>
"""

def patch_article_shop_section(article_path):
    """Add a shop section to an article if it has Amazon links."""
    with open(article_path) as f:
        html = f.read()

    # Skip if already has shop section
    if 'class="shop-section"' in html:
        print(f"  [skip] {article_path.name} already has shop section")
        return

    asins = extract_asins(html)
    if not asins:
        print(f"  [skip] {article_path.name} — no Amazon links")
        return

    shop_html = build_shop_section(asins)

    # Insert before the affiliate disclosure paragraph
    disclosure_marker = '<p style="font-size:12px;color:#888'
    if disclosure_marker in html:
        html = html.replace(disclosure_marker, shop_html + disclosure_marker)
    else:
        # Insert before </article>
        html = html.replace("</article>", shop_html + "\n  </article>")

    with open(article_path, "w") as f:
        f.write(html)
    print(f"  [ok] {article_path.name} — added {len(asins)} product(s)")

def patch_article_hero_image(article_path):
    """Add a hero image to the top of an article if available."""
    slug = article_path.stem
    img_path = IMG_DIR / f"{slug}.jpg"
    if not img_path.exists():
        return

    with open(article_path) as f:
        html = f.read()

    # Skip if already has hero image
    if 'class="article-hero"' in html or 'article-hero-img' in html:
        return

    img_html = f"""
  <div style="width:100%;height:320px;overflow:hidden;border-radius:14px;margin-bottom:28px;">
    <img src="../images/{slug}.jpg" alt="" style="width:100%;height:100%;object-fit:cover;" loading="lazy">
  </div>"""

    # Insert after the article-meta line (date line)
    meta_re = re.compile(r'(<p class="article-meta"[^>]*>.*?</p>)', re.DOTALL)
    if meta_re.search(html):
        html = meta_re.sub(r'\1' + img_html, html, count=1)
        with open(article_path, "w") as f:
            f.write(html)
        print(f"  [ok] {article_path.name} — added hero image")
    else:
        print(f"  [skip] {article_path.name} — no meta line found")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Daily Deal Darling — Image Enhancer")
    print("=" * 60)

    # 1. Download Pexels images
    fetch_all_images()

    # 2. Patch card thumbnails on index + blog
    print("\n── Patching card thumbnails ─────────────────────────────────")
    patch_card_thumbs_in_file(SITE_DIR / "index.html", {})
    patch_hero_image(SITE_DIR / "index.html")
    patch_card_thumbs_in_file(SITE_DIR / "blog.html", {})

    # 3. Patch each article: hero image + shop section
    print("\n── Patching article pages ───────────────────────────────────")
    articles_dir = SITE_DIR / "articles"
    article_files = sorted(articles_dir.glob("*.html"))
    for article_path in article_files:
        patch_article_hero_image(article_path)
        patch_article_shop_section(article_path)

    print(f"\n✅  Done! Processed {len(article_files)} articles.")
    print(f"   Images folder: {IMG_DIR} ({len(list(IMG_DIR.glob('*.jpg')))} files)")

if __name__ == "__main__":
    main()
