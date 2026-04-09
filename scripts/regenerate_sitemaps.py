#!/usr/bin/env python3
"""Regenerate sitemaps for all brand websites with all articles included."""

import os
import re
from pathlib import Path
from datetime import datetime

# Brand sitemap configuration
BRAND_SITEMAPS = {
    'fitness': {
        'domain': 'https://fitover35.com',
        'articles_dir': 'outputs/fitover35-website/articles',
        'sitemap_path': 'outputs/fitover35-website/sitemap.xml',
        'main_pages': [
            ('', 1.0, 'daily'),
            ('supplements.html', 0.9, 'weekly'),
            ('workouts.html', 0.9, 'weekly'),
            ('nutrition.html', 0.9, 'weekly'),
            ('gear.html', 0.9, 'weekly'),
            ('12-week-program.html', 0.8, 'monthly'),
            ('privacy.html', 0.3, 'yearly'),
            ('terms.html', 0.3, 'yearly'),
            ('disclaimer.html', 0.3, 'yearly'),
        ],
    },
    'deals': {
        'domain': 'https://dailydealdarling.com',
        'articles_dir': 'outputs/dailydealdarling-website/articles',
        'sitemap_path': 'outputs/dailydealdarling-website/sitemap.xml',
        'main_pages': [
            ('', 1.0, 'daily'),
            ('kitchen.html', 0.9, 'weekly'),
            ('home.html', 0.9, 'weekly'),
            ('beauty.html', 0.9, 'weekly'),
            ('mom.html', 0.9, 'weekly'),
            ('about', 0.6, 'monthly'),
        ],
    },
    'menopause': {
        'domain': 'https://menopause-planner-website.vercel.app',
        'articles_dir': 'outputs/menopause-planner-website/articles',
        'sitemap_path': 'outputs/menopause-planner-website/sitemap.xml',
        'main_pages': [
            ('', 1.0, 'daily'),
            ('supplements.html', 0.9, 'weekly'),
            ('sleep.html', 0.9, 'weekly'),
            ('wellness.html', 0.9, 'weekly'),
            ('about.html', 0.8, 'monthly'),
            ('blog.html', 0.8, 'weekly'),
            ('thank-you.html', 0.5, 'weekly'),
            ('wellness-planner.html', 0.8, 'monthly'),
            ('privacy.html', 0.3, 'yearly'),
            ('terms.html', 0.3, 'yearly'),
        ],
    },
}

LASTMOD_DATE = '2026-04-07'


def get_article_filenames(articles_dir):
    """Get list of article filenames (HTML files only)."""
    if not os.path.exists(articles_dir):
        return []
    articles = []
    for f in sorted(Path(articles_dir).glob('*.html')):
        articles.append(f.name)
    return articles


def build_sitemap_xml(brand_config):
    """Build complete sitemap XML with main pages and all articles."""
    domain = brand_config['domain']
    articles_dir = brand_config['articles_dir']
    main_pages = brand_config['main_pages']

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    # Add main pages
    for page_path, priority, changefreq in main_pages:
        if page_path:
            url = f"{domain}/{page_path}" if not page_path.startswith('/') else f"{domain}{page_path}"
        else:
            url = domain

        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{url}</loc>')
        xml_lines.append(f'    <lastmod>{LASTMOD_DATE}</lastmod>')
        xml_lines.append(f'    <changefreq>{changefreq}</changefreq>')
        xml_lines.append(f'    <priority>{priority}</priority>')
        xml_lines.append('  </url>')

    # Add all articles
    article_files = get_article_filenames(articles_dir)
    for article_file in article_files:
        # Remove .html extension and construct URL
        article_slug = article_file.replace('.html', '')
        url = f"{domain}/articles/{article_file}"

        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{url}</loc>')
        xml_lines.append(f'    <lastmod>{LASTMOD_DATE}</lastmod>')
        xml_lines.append('    <changefreq>weekly</changefreq>')
        xml_lines.append('    <priority>0.8</priority>')
        xml_lines.append('  </url>')

    xml_lines.append('</urlset>')
    return '\n'.join(xml_lines)


def write_sitemap(brand_name, brand_config):
    """Write sitemap XML to file."""
    sitemap_path = brand_config['sitemap_path']
    articles_dir = brand_config['articles_dir']

    # Check if articles directory exists
    if not os.path.exists(articles_dir):
        print(f"  Warning: Articles directory not found: {articles_dir}")
        article_count = 0
    else:
        article_count = len(get_article_filenames(articles_dir))

    # Build and write sitemap
    sitemap_xml = build_sitemap_xml(brand_config)

    try:
        Path(sitemap_path).write_text(sitemap_xml, encoding='utf-8')
        print(f"  OK Wrote sitemap with {article_count} articles ({len(brand_config['main_pages'])} main pages)")
        return True
    except Exception as e:
        print(f"  ERROR writing sitemap: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Regenerate sitemaps for all brand websites')
    parser.add_argument(
        '--brand',
        choices=['fitness', 'deals', 'menopause', 'all'],
        default='all',
        help='Regenerate sitemap for specific brand or all brands'
    )
    args = parser.parse_args()

    brands_to_process = BRAND_SITEMAPS if args.brand == 'all' else {args.brand: BRAND_SITEMAPS[args.brand]}

    print(f"Regenerating sitemaps with lastmod={LASTMOD_DATE}...\n")

    total_articles = 0
    for brand, config in brands_to_process.items():
        print(f"{brand.capitalize()}:")
        if write_sitemap(brand, config):
            articles = get_article_filenames(config['articles_dir'])
            total_articles += len(articles)

    print(f"\nTotal articles indexed: {total_articles}")


if __name__ == '__main__':
    main()
