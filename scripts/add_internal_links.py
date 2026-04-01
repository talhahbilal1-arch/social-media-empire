#!/usr/bin/env python3
"""Add internal links between articles within each brand site."""

import os
import re
from pathlib import Path

BRANDS = {
    'fitness': 'outputs/fitover35-website/articles',
    'deals': 'outputs/dailydealdarling-website/articles',
    'menopause': 'outputs/menopause-planner-website/articles',
}

# Common keywords to link between articles (brand-specific)
LINK_KEYWORDS = {
    'fitness': [
        'protein', 'workout', 'muscle', 'weight loss', 'supplements', 'exercise',
        'training', 'recovery', 'nutrition', 'strength', 'fat loss', 'testosterone',
        'creatine', 'gear', 'home gym', 'cardio', 'lifting', 'compound'
    ],
    'deals': [
        'amazon', 'deal', 'discount', 'sale', 'review', 'best', 'budget', 'save',
        'price', 'worth', 'kitchen', 'home', 'gadget', 'organizer', 'bedroom',
        'skincare', 'gift', 'trending'
    ],
    'menopause': [
        'symptoms', 'hot flashes', 'sleep', 'weight', 'hormone', 'wellness',
        'nutrition', 'exercise', 'stress', 'supplements', 'relief', 'night sweats',
        'mood', 'energy', 'natural'
    ],
}


def get_article_titles(articles_dir):
    """Read all HTML files and extract titles from <title> tags."""
    articles = {}
    try:
        for f in Path(articles_dir).glob('*.html'):
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                # Extract title from <title> tag
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                if title_match:
                    articles[f.name] = title_match.group(1)
            except Exception as e:
                print(f"  Warning: Could not read {f.name}: {e}")
    except Exception as e:
        print(f"  Error reading articles directory: {e}")
    return articles


def add_links_to_article(filepath, other_articles, brand, max_links=3):
    """Add internal links to related articles based on keyword matching."""
    try:
        content = Path(filepath).read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return 0

    links_added = 0
    current_filename = Path(filepath).name
    keywords_found = set()

    for filename, title in other_articles.items():
        if links_added >= max_links:
            break
        if filename == current_filename:
            continue
        if filename in content:  # Already linked
            continue

        # Check if article content mentions keywords from other articles
        title_words = title.lower().split()
        for keyword in LINK_KEYWORDS.get(brand, []):
            if links_added >= max_links:
                break
            if keyword in keywords_found:  # Skip if we already used this keyword
                continue
            # Case-insensitive search within text (avoid <head>, <script> sections)
            body_match = re.search(
                r'<body[^>]*>(.*?)</body>',
                content,
                re.IGNORECASE | re.DOTALL
            )
            if not body_match:
                body_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.IGNORECASE | re.DOTALL)

            search_text = body_match.group(1) if body_match else content.lower()

            # Find keyword in article body (word boundary search)
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, search_text, re.IGNORECASE):
                # Find the first occurrence in a paragraph and wrap it with a link
                match = re.search(
                    r'(?<=>)([^<]*?\b' + re.escape(keyword) + r'\b[^<]*?)(?=<)',
                    search_text,
                    re.IGNORECASE
                )
                if match:
                    # Build the replacement with anchor tag
                    original_text = match.group(1)
                    keyword_in_text = re.search(
                        r'\b(' + re.escape(keyword) + r')\b',
                        original_text,
                        re.IGNORECASE
                    )
                    if keyword_in_text:
                        before = original_text[:keyword_in_text.start(1)]
                        keyword_text = keyword_in_text.group(1)
                        after = original_text[keyword_in_text.end(1):]
                        link_html = (
                            f'{before}<a href="/articles/{filename}" '
                            f'title="{title}">{keyword_text}</a>{after}'
                        )
                        # Replace in the actual content
                        content = content[:match.start(1)] + link_html + content[match.end(1):]
                        keywords_found.add(keyword)
                        links_added += 1
                        break

    if links_added > 0:
        try:
            Path(filepath).write_text(content, encoding='utf-8')
        except Exception as e:
            print(f"  Error writing {filepath}: {e}")
            return 0

    return links_added


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Add internal links between brand articles')
    parser.add_argument(
        '--brand',
        choices=['fitness', 'deals', 'menopause', 'all'],
        default='all',
        help='Process specific brand or all brands'
    )
    args = parser.parse_args()

    brands_to_process = BRANDS if args.brand == 'all' else {args.brand: BRANDS[args.brand]}

    for brand, articles_dir in brands_to_process.items():
        if not os.path.exists(articles_dir):
            print(f"Skipping {brand}: directory {articles_dir} not found")
            continue

        print(f"\nProcessing {brand} ({articles_dir})...")
        articles = get_article_titles(articles_dir)
        print(f"  Found {len(articles)} articles")

        if len(articles) == 0:
            print(f"  No articles to process")
            continue

        total_links = 0
        for filepath in sorted(Path(articles_dir).glob('*.html')):
            links = add_links_to_article(filepath, articles, brand, max_links=3)
            total_links += links

        print(f"  Total links added for {brand}: {total_links}")


if __name__ == '__main__':
    main()
