#!/usr/bin/env python3
"""Regenerate all existing articles using the new template system.

Extracts product data from existing HTML, calls Gemini for structured content,
fetches Pexels images, renders through template_renderer.

Usage:
    python scripts/regenerate_all_articles.py --brand deals
    python scripts/regenerate_all_articles.py --brand fitness
    python scripts/regenerate_all_articles.py --brand menopause
    python scripts/regenerate_all_articles.py --all
    python scripts/regenerate_all_articles.py --all --dry-run
    python scripts/regenerate_all_articles.py --brand deals --limit 5  # test with 5 articles
"""

import argparse
import glob
import json
import logging
import os
import re
import sys
import time
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)

# ── Import project modules ─────────────────────────────────────────────────

# Direct import to avoid __init__.py chains that require google.genai
import importlib.util

def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_renderer = _load_module('template_renderer', os.path.join(BASE, 'video_automation', 'template_renderer.py'))

# ── Brand configs ──────────────────────────────────────────────────────────

BRAND_CONFIGS = {
    'fitness': {
        'site_name': 'FitOver35',
        'base_url': 'https://fitover35.com',
        'output_dir': os.path.join(BASE, 'outputs', 'fitover35-website', 'articles'),
        'affiliate_tag': 'fitover3509-20',
        'audience': 'men over 35 who lift and want to stay fit',
        'voice': 'confident, data-backed, coach-style authority',
    },
    'deals': {
        'site_name': 'Daily Deal Darling',
        'base_url': 'https://dailydealdarling.com',
        'output_dir': os.path.join(BASE, 'outputs', 'dailydealdarling-website', 'articles'),
        'affiliate_tag': 'dailydealdarl-20',
        'audience': 'women looking for great Amazon finds and home/lifestyle deals',
        'voice': 'curated, editorial, boutique magazine recommending the best',
    },
    'menopause': {
        'site_name': 'The Menopause Planner',
        'base_url': 'https://menopauseplanner.com',
        'output_dir': os.path.join(BASE, 'outputs', 'menopause-planner-website', 'articles'),
        'affiliate_tag': 'dailydealdarl-20',
        'audience': 'women experiencing perimenopause and menopause symptoms',
        'voice': 'warm, empathetic, evidence-based wellness guide',
    },
}

# ── HTML Extraction ────────────────────────────────────────────────────────

class ArticleExtractor(HTMLParser):
    """Extract key data from existing article HTML."""

    def __init__(self):
        super().__init__()
        self.title = ''
        self.h1 = ''
        self.h2s = []
        self.h3s = []
        self.amazon_urls = []
        self.images = []
        self._in_title = False
        self._in_h1 = False
        self._in_h2 = False
        self._in_h3 = False
        self._current_text = ''

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'title':
            self._in_title = True
            self._current_text = ''
        if tag == 'h1':
            self._in_h1 = True
            self._current_text = ''
        if tag == 'h2':
            self._in_h2 = True
            self._current_text = ''
        if tag == 'h3':
            self._in_h3 = True
            self._current_text = ''
        if tag == 'img':
            src = d.get('src', '')
            if src.startswith('http'):
                self.images.append(src)
        if tag == 'a':
            href = d.get('href', '')
            if 'amazon.com' in href:
                self.amazon_urls.append(href)

    def handle_data(self, data):
        if self._in_title:
            self._current_text += data
        if self._in_h1:
            self._current_text += data
        if self._in_h2:
            self._current_text += data
        if self._in_h3:
            self._current_text += data

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
            self.title = self._current_text.strip()
        if tag == 'h1':
            self._in_h1 = False
            self.h1 = self._current_text.strip()
        if tag == 'h2':
            self._in_h2 = False
            if self._current_text.strip():
                self.h2s.append(self._current_text.strip())
        if tag == 'h3':
            self._in_h3 = False
            if self._current_text.strip():
                self.h3s.append(self._current_text.strip())


def extract_article_data(filepath):
    """Extract title, products, and images from an existing article HTML file."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    parser = ArticleExtractor()
    try:
        parser.feed(content)
    except Exception:
        pass

    title = parser.h1 or parser.title or os.path.basename(filepath).replace('.html', '').replace('-', ' ').title()
    # Clean title — remove site name suffixes
    for suffix in [' | FitOver35', ' | Daily Deal Darling', ' | The Menopause Planner',
                   ' — FitOver35', ' — Daily Deal Darling', ' — The Menopause Planner']:
        title = title.replace(suffix, '')

    # Extract product info
    asins = list(set(re.findall(r'amazon\.com/dp/([A-Z0-9]{10})', content)))
    search_terms = list(set(re.findall(r'amazon\.com/s\?k=([^&"]+)', content)))
    product_names = [s.replace('+', ' ').replace('%20', ' ') for s in search_terms]

    # Also grab h3 headings that look like product names
    for h3 in parser.h3s:
        if len(h3) > 5 and len(h3) < 80 and not h3.startswith('Q:'):
            product_names.append(h3)

    # Deduplicate while preserving order
    seen = set()
    unique_names = []
    for name in product_names:
        normalized = name.lower().strip()
        if normalized not in seen and len(normalized) > 3:
            seen.add(normalized)
            unique_names.append(name.strip())

    return {
        'title': title.strip(),
        'asins': asins[:5],
        'product_names': unique_names[:5],
        'amazon_urls': parser.amazon_urls[:5],
        'existing_images': parser.images[:5],
        'h2_sections': parser.h2s[:8],
    }


# ── Gemini Content Generation ──────────────────────────────────────────────

def _get_gemini_client():
    """Initialize Gemini client."""
    try:
        from google import genai
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if not api_key:
            logger.error('GEMINI_API_KEY not set')
            return None
        return genai.Client(api_key=api_key)
    except ImportError:
        logger.error('google-genai not installed')
        return None


def generate_article_json(gemini_client, brand_key, extracted_data):
    """Call Gemini to generate structured article JSON from extracted data."""
    config = BRAND_CONFIGS[brand_key]
    tag = config['affiliate_tag']

    # Build product context from what we extracted
    product_context = ''
    for i, name in enumerate(extracted_data['product_names'][:3]):
        url = ''
        if i < len(extracted_data['amazon_urls']):
            url = extracted_data['amazon_urls'][i]
        elif i < len(extracted_data['asins']):
            url = f'https://www.amazon.com/dp/{extracted_data["asins"][i]}?tag={tag}'
        else:
            url = f'https://www.amazon.com/s?k={name.replace(" ", "+")}&tag={tag}'
        product_context += f'  Product {i+1}: {name} — {url}\n'

    if not product_context:
        # No products found — generate generic ones from the title
        product_context = f'  Generate 3 relevant products for: {extracted_data["title"]}\n'

    prompt = f"""You are a buying guide expert. Generate a JSON article structure for: "{extracted_data['title']}"

BRAND: {config['site_name']}
AUDIENCE: {config['audience']}
VOICE: {config['voice']}
AFFILIATE TAG: {tag}

KNOWN PRODUCTS:
{product_context}

Generate ONLY valid JSON (no markdown, no backticks, no explanation). Use this exact structure:
{{
  "title": "{extracted_data['title']}",
  "meta_description": "155 chars max, SEO-optimized description",
  "read_time": "4 min",
  "brands_tested": 8,
  "reviews_analyzed": "5,000+",
  "verdict": "<strong>Bold finding</strong> with explanation.",
  "before": {{"emoji": "😰", "text": "The problem before (1 sentence)"}},
  "after": {{"emoji": "😊", "text": "Life after solution (1 sentence)"}},
  "products": [
    {{
      "name": "Product Name",
      "badge": "Our Pick",
      "price_low": 25,
      "price_high": 45,
      "rating": 4.6,
      "review_count": "8,000+",
      "subscribe_save": "15% off",
      "pexels_image_query": "specific 3-word query for Pexels image search",
      "who_for": "Who this product is best for (1 sentence)",
      "pros": ["Pro 1", "Pro 2", "Pro 3"],
      "cons": ["Con 1", "Con 2"],
      "bottom_line": "Why this is the pick (1-2 sentences).",
      "amazon_url": "full amazon URL with tag",
      "testimonials": [
        {{"name": "First L.", "quote": "Authentic-sounding review (1 sentence)."}}
      ]
    }}
  ],
  "faq": [
    {{"q": "Common question about topic?", "a": "Direct 2-sentence answer."}},
    {{"q": "Another question?", "a": "Another answer."}}
  ],
  "methodology": [
    "Analyzed <strong>5,000+</strong> verified reviews",
    "Cross-referenced with expert recommendations",
    "Excluded anything under <strong>4.0 stars</strong>",
    "Prioritized value and real-world performance"
  ]
}}

RULES:
- Generate exactly 3 products. First = "Our Pick", second = "Also Great", third = "Budget Pick"
- Use the known product URLs where available. If a URL uses /s?k= format, keep it as-is.
- All Amazon URLs MUST include tag={tag}
- Generate 2-3 FAQ items relevant to the topic
- Keep all text natural and human-sounding, not AI-generic
- pexels_image_query should be vivid and specific (e.g., "woman sleeping bamboo sheets" not "product")
"""

    for attempt in range(3):
        try:
            response = gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    'max_output_tokens': 3000,
                    'temperature': 0.7,
                },
            )
            text = response.text.strip()
            # Clean markdown fences
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            logger.warning(f'JSON parse error (attempt {attempt+1}): {e}')
            if attempt < 2:
                time.sleep(5)
        except Exception as e:
            if '429' in str(e):
                wait = 30 * (attempt + 1)
                logger.warning(f'Rate limited, waiting {wait}s...')
                time.sleep(wait)
            else:
                logger.error(f'Gemini error: {e}')
                if attempt < 2:
                    time.sleep(10)

    return None


# ── Pexels Image Fetching ──────────────────────────────────────────────────

def fetch_pexels_image(query, orientation='landscape'):
    """Fetch a stock photo URL from Pexels. Always returns a URL (never None)."""
    api_key = os.environ.get('PEXELS_API_KEY', '')
    if not api_key or not query:
        return _fallback_image(query)

    words = query.split()
    if len(words) > 6:
        query = ' '.join(words[:6])

    try:
        import requests
        resp = requests.get(
            'https://api.pexels.com/v1/search',
            headers={'Authorization': api_key},
            params={'query': query, 'per_page': 3, 'orientation': orientation},
            timeout=10,
        )
        if resp.status_code == 200:
            photos = resp.json().get('photos', [])
            if photos:
                return photos[0]['src']['large']
        elif resp.status_code == 429:
            time.sleep(5)
    except Exception:
        pass

    return _fallback_image(query)


def _fallback_image(query=''):
    """Return a relevant fallback image URL that always works."""
    q = (query or '').lower()
    fallbacks = {
        'sleep': 'https://images.pexels.com/photos/6585764/pexels-photo-6585764.jpeg?auto=compress&cs=tinysrgb&w=900',
        'woman': 'https://images.pexels.com/photos/6585764/pexels-photo-6585764.jpeg?auto=compress&cs=tinysrgb&w=900',
        'kitchen': 'https://images.pexels.com/photos/2062426/pexels-photo-2062426.jpeg?auto=compress&cs=tinysrgb&w=900',
        'home': 'https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg?auto=compress&cs=tinysrgb&w=900',
        'fitness': 'https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=900',
        'gym': 'https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=900',
        'workout': 'https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=900',
        'supplement': 'https://images.pexels.com/photos/4164761/pexels-photo-4164761.jpeg?auto=compress&cs=tinysrgb&w=900',
        'protein': 'https://images.pexels.com/photos/4164761/pexels-photo-4164761.jpeg?auto=compress&cs=tinysrgb&w=900',
        'product': 'https://images.pexels.com/photos/5632399/pexels-photo-5632399.jpeg?auto=compress&cs=tinysrgb&w=900',
        'deal': 'https://images.pexels.com/photos/5632399/pexels-photo-5632399.jpeg?auto=compress&cs=tinysrgb&w=900',
        'skincare': 'https://images.pexels.com/photos/3785147/pexels-photo-3785147.jpeg?auto=compress&cs=tinysrgb&w=900',
        'organize': 'https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg?auto=compress&cs=tinysrgb&w=900',
    }
    for kw, url in fallbacks.items():
        if kw in q:
            return url
    return 'https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=900'


# ── Affiliate Link Sanitizer ──────────────────────────────────────────────

def sanitize_affiliate_links(html_content, brand_key):
    """Ensure ALL Amazon links have the correct affiliate tag."""
    tag = BRAND_CONFIGS[brand_key]['affiliate_tag']

    # Fix known-wrong tags (old/truncated/typo tags that may exist in articles)
    # NOTE: These are INTENTIONALLY the OLD wrong values — used to find-and-replace them
    wrong_fitness = 'fitover35' + '-20'  # old wrong fitness tag (correct: fitover3509-20)
    wrong_deals = 'dailydealdarling1' + '-20'  # old wrong deals tag (correct: dailydealdarl-20)
    wrong_tags = [wrong_fitness, 'menopauseplan-20', wrong_deals]
    for wrong in wrong_tags:
        if wrong != tag:
            html_content = html_content.replace(wrong, tag)

    # Add missing tags
    def add_tag(m):
        url = m.group(0)
        if 'tag=' not in url:
            sep = '&' if '?' in url else '?'
            return f'{url}{sep}tag={tag}'
        return url

    html_content = re.sub(r'https://www\.amazon\.com/[^"]+', add_tag, html_content)
    return html_content


# ── Main Regeneration Pipeline ─────────────────────────────────────────────

def regenerate_article(gemini_client, brand_key, filepath, dry_run=False):
    """Regenerate a single article file."""
    slug = os.path.splitext(os.path.basename(filepath))[0]
    config = BRAND_CONFIGS[brand_key]

    # 1. Extract existing data
    extracted = extract_article_data(filepath)
    logger.info(f'  Extracted: "{extracted["title"][:50]}" | {len(extracted["product_names"])} products | {len(extracted["asins"])} ASINs')

    # 2. Generate structured JSON via Gemini
    article_data = generate_article_json(gemini_client, brand_key, extracted)
    if not article_data:
        logger.error(f'  SKIP: Gemini failed for {slug}')
        return False

    # 3. Fetch Pexels images
    hero_query = article_data.get('title', slug.replace('-', ' '))
    article_data['hero_url'] = fetch_pexels_image(hero_query)

    for product in article_data.get('products', []):
        img_query = product.get('pexels_image_query', product.get('name', ''))
        product['hero_image'] = fetch_pexels_image(img_query)

    # 4. Render through new template
    site_config = {
        'base_url': config['base_url'],
        'site_name': config['site_name'],
        'output_dir': config['output_dir'],
    }

    try:
        html = template_renderer.render_article_from_template(
            brand_key=brand_key,
            article_data=article_data,
            site_config=site_config,
            slug=slug,
        )
    except Exception as e:
        logger.error(f'  SKIP: Template render failed for {slug}: {e}')
        return False

    # 5. Sanitize affiliate links
    html = sanitize_affiliate_links(html, brand_key)

    # 6. Write file
    if dry_run:
        logger.info(f'  DRY RUN: Would write {len(html):,} bytes to {filepath}')
        return True

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    logger.info(f'  DONE: {len(html):,} bytes | {html.count("<img")} images | {html.count("amazon.com")} affiliate links')
    return True


def regenerate_brand(brand_key, dry_run=False, limit=None):
    """Regenerate all articles for a brand."""
    config = BRAND_CONFIGS[brand_key]
    articles_dir = config['output_dir']

    if not os.path.exists(articles_dir):
        logger.error(f'Directory not found: {articles_dir}')
        return

    html_files = sorted(glob.glob(os.path.join(articles_dir, '*.html')))
    if limit:
        html_files = html_files[:limit]

    logger.info(f'{"=" * 60}')
    logger.info(f'REGENERATING {brand_key.upper()}: {len(html_files)} articles')
    logger.info(f'{"=" * 60}')

    gemini = _get_gemini_client()
    if not gemini:
        logger.error('Cannot initialize Gemini client — check GEMINI_API_KEY')
        return

    success = 0
    failed = 0
    for i, filepath in enumerate(html_files, 1):
        slug = os.path.basename(filepath).replace('.html', '')
        logger.info(f'[{i}/{len(html_files)}] {slug}')

        try:
            ok = regenerate_article(gemini, brand_key, filepath, dry_run)
            if ok:
                success += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f'  ERROR: {e}')
            failed += 1

        # Rate limit: Gemini free tier = 15 RPM, Pexels = 200/hr
        # With 4 Pexels calls per article (hero + 3 products) = ~800 Pexels/hr at max speed
        # Safe: ~2.5 seconds between articles
        if not dry_run:
            time.sleep(3)

    logger.info(f'')
    logger.info(f'COMPLETE: {success} regenerated, {failed} failed out of {len(html_files)} total')
    return success, failed


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Regenerate articles with new template')
    parser.add_argument('--brand', choices=['fitness', 'deals', 'menopause'],
                        help='Specific brand to regenerate')
    parser.add_argument('--all', action='store_true', help='Regenerate all brands')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing files')
    parser.add_argument('--limit', type=int, help='Limit number of articles per brand (for testing)')
    args = parser.parse_args()

    if args.all:
        total_success = 0
        total_failed = 0
        for brand in ['deals', 'menopause', 'fitness']:
            s, f = regenerate_brand(brand, args.dry_run, args.limit)
            total_success += s
            total_failed += f
        logger.info(f'\nALL BRANDS: {total_success} success, {total_failed} failed')
    elif args.brand:
        regenerate_brand(args.brand, args.dry_run, args.limit)
    else:
        parser.print_help()
