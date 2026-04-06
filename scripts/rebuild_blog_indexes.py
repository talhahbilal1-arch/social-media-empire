#!/usr/bin/env python3
"""Rebuild blog index pages for all 3 brand sites.

Scans article HTML files, extracts metadata, and regenerates blog.html
for each brand while preserving each site's unique design.
"""

import os
import re
import json
import math
import html
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

BRANDS = {
    'fitness': {
        'site_dir': BASE_DIR / 'outputs' / 'fitover35-website',
        'title_suffix_patterns': [
            ' — FitOver35', ' | FitOver35', ' - FitOver35',
        ],
    },
    'deals': {
        'site_dir': BASE_DIR / 'outputs' / 'dailydealdarling-website',
        'title_suffix_patterns': [
            ' — Daily Deal Darling', ' | Daily Deal Darling', ' - Daily Deal Darling',
        ],
    },
    'menopause': {
        'site_dir': BASE_DIR / 'outputs' / 'menopause-planner-website',
        'title_suffix_patterns': [
            ' — The Menopause Planner', ' | The Menopause Planner', ' - The Menopause Planner',
            ' — Menopause Planner', ' | Menopause Planner', ' - Menopause Planner',
        ],
    },
}


def extract_article_metadata(filepath, title_suffix_patterns):
    """Extract metadata from an article HTML file."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"  WARNING: Could not read {filepath.name}: {e}")
        return None

    meta = {'filename': filepath.name}

    # Title from <title> tag
    m = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
    if m:
        title = html.unescape(m.group(1).strip())
        for suffix in title_suffix_patterns:
            if title.endswith(suffix):
                title = title[:-len(suffix)]
                break
        meta['title'] = title.strip()
    else:
        # Fallback: derive from filename
        meta['title'] = filepath.stem.replace('-', ' ').title()

    # Description from <meta name="description">
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content, re.IGNORECASE)
    if m:
        meta['description'] = html.unescape(m.group(1).strip())
    else:
        meta['description'] = ''

    # og:image
    m = re.search(r'<meta\s+property="og:image"\s+content="([^"]*)"', content, re.IGNORECASE)
    if m:
        meta['og_image'] = m.group(1).strip()
    else:
        meta['og_image'] = ''

    # datePublished from JSON-LD
    m = re.search(r'"datePublished"\s*:\s*"([^"]*)"', content)
    if m:
        meta['date_published'] = m.group(1).strip()
    else:
        meta['date_published'] = '2026-01-01'

    # Keywords from <meta name="keywords">
    m = re.search(r'<meta\s+name="keywords"\s+content="([^"]*)"', content, re.IGNORECASE)
    if m:
        keywords = m.group(1).strip()
        first_kw = keywords.split(',')[0].strip() if keywords else ''
        meta['first_keyword'] = first_kw.capitalize() if first_kw else ''
    else:
        meta['first_keyword'] = ''

    # Word count for read time (count words in <body>)
    body_match = re.search(r'<body[^>]*>(.*)</body>', content, re.DOTALL | re.IGNORECASE)
    if body_match:
        body_text = re.sub(r'<[^>]+>', ' ', body_match.group(1))
        body_text = re.sub(r'\s+', ' ', body_text).strip()
        word_count = len(body_text.split())
        meta['read_time'] = max(1, math.ceil(word_count / 250))
    else:
        meta['read_time'] = 5

    return meta


def scan_articles(brand_key):
    """Scan all .html articles for a brand and return sorted metadata list."""
    config = BRANDS[brand_key]
    articles_dir = config['site_dir'] / 'articles'
    if not articles_dir.exists():
        print(f"  WARNING: {articles_dir} does not exist")
        return []

    articles = []
    for f in sorted(articles_dir.glob('*.html')):
        meta = extract_article_metadata(f, config['title_suffix_patterns'])
        if meta:
            articles.append(meta)

    return articles


def rebuild_fitness_blog(articles):
    """Rebuild FitOver35 blog.html preserving its dark theme design."""
    blog_path = BRANDS['fitness']['site_dir'] / 'blog.html'
    content = blog_path.read_text(encoding='utf-8')

    # Sort alphabetically by title (matching existing pattern)
    articles.sort(key=lambda a: a['title'].lower())

    # Build article links
    lines = []
    for a in articles:
        safe_title = html.escape(a['title'])
        lines.append(f'    <a href="/articles/{a["filename"]}" class="blog-item">{safe_title}</a>')
    new_grid_content = '\n'.join(lines)

    # Replace content inside <div class="blog-grid" id="blogGrid">...</div>
    pattern = r'(<div class="blog-grid" id="blogGrid">)\s*.*?\s*(</div>\s*\n\s*<footer)'
    replacement = f'\\1\n{new_grid_content}\n\\2'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # Update article count in page header
    count = len(articles)
    new_content = re.sub(
        r'<p>\d+ in-depth guides',
        f'<p>{count} in-depth guides',
        new_content
    )

    blog_path.write_text(new_content, encoding='utf-8')
    print(f"  FitOver35: {count} articles written to blog.html")


def rebuild_deals_blog(articles):
    """Rebuild DailyDealDarling blog.html preserving its pink card layout."""
    blog_path = BRANDS['deals']['site_dir'] / 'blog.html'
    content = blog_path.read_text(encoding='utf-8')

    # Sort by date (newest first)
    articles.sort(key=lambda a: a['date_published'], reverse=True)

    # Build article cards
    cards = []
    for a in articles:
        safe_title = html.escape(a['title'])
        safe_desc = html.escape(a['description']) if a['description'] else ''
        og_img = a['og_image'] or 'https://images.pexels.com/photos/5632398/pexels-photo-5632398.jpeg?auto=compress&cs=tinysrgb&w=600'

        # Category from first keyword
        category = a['first_keyword'] if a['first_keyword'] else 'Deals'
        # Clean up generic keywords
        generic = ['2026', 'home', 'best', 'top', 'amazon', 'the', 'a', 'an', 'for', 'and', 'of', 'to', 'in', 'on', 'with']
        if category.lower() in generic:
            category = 'Deals'

        card = f"""        <article class="blog-item">
          <div class="blog-item__image">
            <img src="{og_img}" alt="{safe_title.lower()}" loading="lazy">
          </div>
          <div class="blog-item__content">
            <span class="blog-item__category">{html.escape(category)}</span>
            <h2 class="blog-item__title">
              <a href="articles/{a['filename']}">{safe_title}</a>
            </h2>
            <p class="blog-item__excerpt">{safe_desc}</p>
            <span class="blog-item__meta">{a['read_time']} min read</span>
          </div>
        </article>"""
        cards.append(card)

    new_cards_content = '\n\n'.join(cards)

    # Replace everything inside <div class="blog-list">...</div>
    pattern = r'(<div class="blog-list">)\s*.*?\s*(</div>\s*\n\s*</section>\s*\n\s*<!-- Newsletter)'
    replacement = f'\\1\n{new_cards_content}\n\n    \\2'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    blog_path.write_text(new_content, encoding='utf-8')
    print(f"  DailyDealDarling: {len(articles)} articles written to blog.html")


def rebuild_menopause_blog(articles):
    """Rebuild Menopause Planner blog.html preserving its purple grid design."""
    blog_path = BRANDS['menopause']['site_dir'] / 'blog.html'
    content = blog_path.read_text(encoding='utf-8')

    # Sort by date (newest first)
    articles.sort(key=lambda a: a['date_published'], reverse=True)

    # Build article cards
    cards = []
    for a in articles:
        safe_title = html.escape(a['title'])
        safe_desc = html.escape(a['description']) if a['description'] else ''
        og_img = a['og_image'] or ''

        if og_img:
            img_tag = f'<img class="article-image" src="{og_img}" alt="{safe_title}" loading="lazy" style="width:100%;height:200px;object-fit:cover;">'
        else:
            img_tag = '<div class="article-image" style="display:flex;align-items:center;justify-content:center;font-size:3rem;color:#7B1FA2;">📖</div>'

        card = f"""        <a href="articles/{a['filename']}" class="article-card" style="text-decoration:none;color:inherit;">
          {img_tag}
          <div class="article-content">
            <h3>{safe_title}</h3>
            <p>{safe_desc}</p>
          </div>
        </a>"""
        cards.append(card)

    new_cards_content = '\n\n'.join(cards)

    # Remove the placeholder card
    content = re.sub(
        r'\s*<!-- Placeholder -->\s*<div class="placeholder-card">.*?</div>\s*',
        '\n',
        content,
        flags=re.DOTALL
    )

    # Replace content inside <div id="article-list">...</div>
    pattern = r'(<div id="article-list">)\s*(</div>)'
    replacement = f'\\1\n{new_cards_content}\n        \\2'
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    blog_path.write_text(new_content, encoding='utf-8')
    print(f"  Menopause Planner: {len(articles)} articles written to blog.html")


def main():
    print("Rebuilding blog index pages...\n")

    # Fitness
    print("Scanning FitOver35 articles...")
    fitness_articles = scan_articles('fitness')
    if fitness_articles:
        rebuild_fitness_blog(fitness_articles)

    # Deals
    print("\nScanning DailyDealDarling articles...")
    deals_articles = scan_articles('deals')
    if deals_articles:
        rebuild_deals_blog(deals_articles)

    # Menopause
    print("\nScanning Menopause Planner articles...")
    menopause_articles = scan_articles('menopause')
    if menopause_articles:
        rebuild_menopause_blog(menopause_articles)

    print(f"\nDone! Total articles indexed: {len(fitness_articles) + len(deals_articles) + len(menopause_articles)}")


if __name__ == '__main__':
    main()
