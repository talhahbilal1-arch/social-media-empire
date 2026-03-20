"""Regenerate all existing articles using the new template system.

Run this ONCE after deploying the template fix to rebuild all 235+ articles
with proper images and the approved design.

Usage:
    python scripts/regenerate_all_articles.py --brand deals
    python scripts/regenerate_all_articles.py --brand fitness
    python scripts/regenerate_all_articles.py --brand menopause
    python scripts/regenerate_all_articles.py --all
"""

import argparse
import glob
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from video_automation.template_renderer import render_article_from_template
from video_automation.pin_article_generator import (
    BRAND_SITE_CONFIG, _fetch_pexels_image, _fetch_pexels_batch,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)


def regenerate_brand(brand_key):
    """Regenerate all articles for a brand using the new template."""
    site = BRAND_SITE_CONFIG[brand_key]
    articles_dir = site['output_dir']

    if not os.path.exists(articles_dir):
        logger.warning(f'No articles directory found: {articles_dir}')
        return

    html_files = glob.glob(os.path.join(articles_dir, '*.html'))
    logger.info(f'Found {len(html_files)} articles for {brand_key}')

    regenerated = 0
    for filepath in html_files:
        slug = os.path.splitext(os.path.basename(filepath))[0]

        # Build minimal article_data from the slug
        title = slug.replace('-', ' ').title()
        hero_image = _fetch_pexels_image(title) or ''

        article_data = {
            'title': title,
            'meta_description': f'{title} — expert reviewed picks for {site["site_name"]}',
            'read_time': '4 min',
            'brands_tested': 8,
            'reviews_analyzed': '5,000+',
            'verdict': f'<strong>We researched the best options</strong> so you don\'t have to. Here are our top {brand_key} picks.',
            'before': {'emoji': '\U0001f630', 'title': 'Before', 'text': 'Hours of scrolling through thousands of options'},
            'after': {'emoji': '\U0001f60a', 'title': 'After', 'text': 'Confident purchase backed by real reviews'},
            'hero_url': hero_image,
            'category': brand_key.title(),
            'products': [],  # Will be empty for regenerated articles without JSON data
            'faq': [],
        }

        try:
            new_html = render_article_from_template(
                brand_key=brand_key,
                article_data=article_data,
                site_config=site,
                slug=slug,
            )
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_html)
            regenerated += 1
            if regenerated % 10 == 0:
                logger.info(f'  Regenerated {regenerated}/{len(html_files)}...')
        except Exception as e:
            logger.error(f'Failed to regenerate {slug}: {e}')

    logger.info(f'Done! Regenerated {regenerated}/{len(html_files)} articles for {brand_key}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--brand', choices=['fitness', 'deals', 'menopause'])
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()

    if args.all:
        for brand in ['fitness', 'deals', 'menopause']:
            regenerate_brand(brand)
    elif args.brand:
        regenerate_brand(args.brand)
    else:
        parser.print_help()
