#!/usr/bin/env python3
"""Re-wrap all existing articles in brand output directories with bridge page templates.

Processes all .html files in:
- outputs/fitover35-website/articles/*.html (brand_key='fitness')
- outputs/dailydealdarling-website/articles/*.html (brand_key='deals')
- outputs/menopause-planner-website/articles/*.html (brand_key='menopause')

For each article:
1. Extract title, meta description, body HTML, and slug
2. Find hero image URL if present
3. Call render_article_page() from article_templates with extracted data
4. Overwrite the file with new HTML

Prints progress per brand.
"""

import os
import sys
import re
import glob
import time
from typing import Optional, Tuple

# Add repo root to path for imports
sys.path.insert(0, '/Users/homefolder/Desktop/social-media-empire')

from video_automation.article_templates import render_article_page
from video_automation.pin_article_generator import BRAND_SITE_CONFIG, _fetch_pexels_image


# Brand mappings: directory pattern -> brand_key
BRAND_DIRS = {
    'outputs/fitover35-website/articles': 'fitness',
    'outputs/dailydealdarling-website/articles': 'deals',
    'outputs/menopause-planner-website/articles': 'menopause',
}


def extract_title_from_html(html):
    """Extract title from <title> tag, stripping sitename suffix."""
    match = re.search(r'<title>([^<]+)</title>', html)
    if not match:
        return None
    title = match.group(1).strip()
    # Remove common suffixes like " - SiteName" or " | SiteName"
    title = re.sub(r'\s*[-|]\s+[^-|]*$', '', title)
    return title


def extract_meta_description(html):
    """Extract content from <meta name="description" content="...">"""
    match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    if match:
        return match.group(1).strip()
    return ""


def extract_hero_image_url(html):
    """Find hero image URL from <img src="..." after h1 or page header."""
    # Look for background-image in page-header section
    bg_match = re.search(r'style="background-image:\s*url\(\'?([^\'")]+)\'?\)"', html)
    if bg_match:
        return bg_match.group(1)
    # Fallback: find first <img> with src
    img_match = re.search(r'<img[^>]+src="([^"]+)"', html)
    if img_match:
        return img_match.group(1)
    return None


def extract_body_html(html):
    """Extract and clean article body HTML.

    Handles two structures:
    1. Old style: <article class="container"...>...</article> (fitness brand)
    2. New style: <div class="article-body">...</div> (menopause, deals brands)

    Removes:
    - Opening article-meta / date lines
    - Closing disclosure and "Want more tips" sections
    """
    # Try new bridge page structure first (div.article-body)
    article_match = re.search(
        r'<div\s+class="article-body"[^>]*>(.*?)</div>',
        html,
        re.DOTALL
    )

    # Fallback to old structure (article tag)
    if not article_match:
        article_match = re.search(
            r'<article[^>]*>(.*?)</article>',
            html,
            re.DOTALL
        )

    if not article_match:
        return ""

    body = article_match.group(1)

    # Remove opening meta info paragraph (old style)
    body = re.sub(
        r'<p[^>]*class="article-meta"[^>]*>.*?</p>',
        '',
        body,
        flags=re.DOTALL
    )

    # Remove container div wrapper if present (keep inner content)
    body = re.sub(
        r'<div\s+class="container[^"]*"[^>]*>(.*?)</div>(?=\s*$)',
        r'\1',
        body,
        flags=re.DOTALL
    )

    # Remove closing disclosure paragraphs (font-size:12px style)
    body = re.sub(
        r'<p[^>]*style="font-size:12px[^"]*"[^>]*>.*?</p>',
        '',
        body,
        flags=re.DOTALL
    )

    # Remove "Want more tips?" div and following content until next heading or end
    body = re.sub(
        r'<div[^>]*>.*?Want\s+more\s+tips.*?</div>',
        '',
        body,
        flags=re.DOTALL | re.IGNORECASE
    )

    return body.strip()


def slug_from_filename(filepath):
    """Extract slug from filename (strip .html extension)."""
    basename = os.path.basename(filepath)
    return basename[:-5] if basename.endswith('.html') else basename


def process_article(filepath, brand_key):
    """Process a single article file.

    Returns (success: bool, message: str)
    """
    try:
        # Read original HTML
        with open(filepath, 'r', encoding='utf-8') as f:
            original_html = f.read()

        # Extract components
        title = extract_title_from_html(original_html)
        if not title:
            return False, f"No title found"

        meta_desc = extract_meta_description(original_html)
        if not meta_desc:
            meta_desc = title[:155]  # Fallback

        body_html = extract_body_html(original_html)
        if not body_html:
            return False, f"No article body found"

        hero_url = extract_hero_image_url(original_html)
        slug = slug_from_filename(filepath)

        # Fetch Pexels hero image if none found in existing HTML
        if not hero_url and os.environ.get('PEXELS_API_KEY'):
            pexels_query = slug.replace('-', ' ')
            hero_url = _fetch_pexels_image(pexels_query)
            if hero_url:
                time.sleep(0.25)  # Rate-limit Pexels API (200 req/hr)

        # Get site config
        site_config = BRAND_SITE_CONFIG.get(brand_key)
        if not site_config:
            return False, f"Invalid brand_key: {brand_key}"

        # Render new HTML
        new_html = render_article_page(
            brand_key=brand_key,
            title=title,
            meta_desc=meta_desc,
            body_html=body_html,
            hero_url=hero_url,
            site_config=site_config,
            slug=slug,
            pin_data=None
        )

        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_html)

        return True, f"✓ {title[:50]}..."

    except Exception as e:
        return False, f"Error: {str(e)[:80]}"


def main():
    """Process all articles in all brand directories."""
    print("=" * 80)
    print("ARTICLE REGENERATION WITH BRIDGE PAGE TEMPLATES")
    print("=" * 80)
    if os.environ.get('PEXELS_API_KEY'):
        print("  Pexels API key detected — will fetch hero images for articles missing them")
    else:
        print("  No PEXELS_API_KEY — hero images will only be preserved from existing HTML")
    print()

    total_processed = 0
    total_skipped = 0
    total_failed = 0

    # Process each brand directory
    for dir_pattern, brand_key in BRAND_DIRS.items():
        print(f"\n[{brand_key.upper()}] Processing {dir_pattern}")
        print("-" * 80)

        # Find all .html files in directory
        full_pattern = os.path.join(
            '/Users/homefolder/Desktop/social-media-empire',
            dir_pattern,
            '*.html'
        )

        files = sorted(glob.glob(full_pattern))
        if not files:
            print(f"  No .html files found")
            continue

        print(f"  Found {len(files)} article(s)")

        processed = 0
        failed = 0

        for filepath in files:
            success, message = process_article(filepath, brand_key)

            if success:
                processed += 1
                print(f"    {message}")
            else:
                failed += 1
                print(f"    ✗ {os.path.basename(filepath)}: {message}")

        print(f"\n  Summary: {processed} processed, {failed} failed")

        total_processed += processed
        total_failed += failed

    # Final summary
    print()
    print("=" * 80)
    print(f"TOTAL: {total_processed} articles regenerated, {total_failed} failed")
    print("=" * 80)

    return 0 if total_failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
