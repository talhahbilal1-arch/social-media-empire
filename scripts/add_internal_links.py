#!/usr/bin/env python3
"""Add contextual internal links between articles within each brand site.

Scans all HTML articles per brand, builds a keyword-to-article relevance map,
then inserts 3-5 inline links per article using descriptive anchor text.
Uses relative paths (same /articles/ directory). Skips existing links.
"""

import os
import re
import argparse
from pathlib import Path
from collections import Counter

BRANDS = {
    'fitness': 'outputs/fitover35-website/articles',
    'deals': 'outputs/dailydealdarling-website/articles',
    'menopause': 'outputs/menopause-planner-website/articles',
}

# Stop words to exclude from keyword extraction
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'shall', 'can', 'need', 'dare',
    'that', 'this', 'these', 'those', 'i', 'me', 'my', 'we', 'our', 'you',
    'your', 'he', 'him', 'his', 'she', 'her', 'it', 'its', 'they', 'them',
    'their', 'what', 'which', 'who', 'whom', 'when', 'where', 'why', 'how',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
    'just', 'because', 'as', 'if', 'then', 'else', 'about', 'up', 'out',
    'into', 'over', 'after', 'before', 'between', 'under', 'again', 'here',
    'there', 'once', 'during', 'while', 'also', 'still', 'new', 'old',
    'best', 'top', 'good', 'great', 'really', 'actually', 'vs', 'guide',
    'tips', 'ways', 'things', 'men', 'women', '2024', '2025', '2026',
}


def extract_keywords_from_title(title):
    """Extract meaningful keywords from an article title."""
    # Remove brand suffixes
    title = re.sub(r'\s*[—\-|]\s*(FitOver35|Daily Deal Darling|The Menopause Planner).*$', '', title, flags=re.IGNORECASE)
    # Split into words, lowercase, remove non-alpha
    words = re.findall(r'[a-z]+', title.lower())
    # Filter stop words and short words
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def extract_keywords_from_filename(filename):
    """Extract keywords from the filename (slug)."""
    name = filename.replace('.html', '').replace('.md', '')
    words = name.split('-')
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def get_article_data(articles_dir):
    """Read all HTML files, extract titles and keywords."""
    articles = {}
    for f in sorted(Path(articles_dir).glob('*.html')):
        try:
            content = f.read_text(encoding='utf-8', errors='ignore')
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if title_match:
                raw_title = title_match.group(1).strip()
                # Clean title: remove brand suffix for display
                clean_title = re.sub(
                    r'\s*[—\-|]\s*(FitOver35|Daily Deal Darling|The Menopause Planner).*$',
                    '', raw_title, flags=re.IGNORECASE
                ).strip()
                keywords = set(extract_keywords_from_title(raw_title) +
                              extract_keywords_from_filename(f.name))
                articles[f.name] = {
                    'title': clean_title,
                    'keywords': keywords,
                    'path': str(f),
                }
        except Exception as e:
            print(f"  Warning: Could not read {f.name}: {e}")
    return articles


def score_relevance(article_keywords, candidate_keywords):
    """Score how related two articles are based on keyword overlap."""
    if not article_keywords or not candidate_keywords:
        return 0
    overlap = article_keywords & candidate_keywords
    # Score = number of shared keywords, weighted by specificity
    return len(overlap)


def find_related_articles(current_filename, current_keywords, all_articles, max_results=8):
    """Find the most contextually related articles for a given article."""
    scores = []
    for filename, data in all_articles.items():
        if filename == current_filename:
            continue
        score = score_relevance(current_keywords, data['keywords'])
        if score > 0:
            scores.append((filename, score, data))

    # Sort by relevance score (descending), then alphabetically for stability
    scores.sort(key=lambda x: (-x[1], x[0]))
    return scores[:max_results]


def get_body_content(html):
    """Extract body content from HTML, avoiding head/script/style."""
    body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.IGNORECASE | re.DOTALL)
    if body_match:
        return body_match.group(1)
    return html


def find_safe_insertion_points(body_html):
    """Find <p> tags, .verdict p, .bottom-line, .faq-a, .ba-text, and other
    text-containing elements that are safe for link insertion.
    Returns list of (start, end, text) for text nodes inside safe elements."""
    # Match text content inside paragraph-like elements
    # We target: <p ...>text</p>, <div class="...text...">text</div>
    # But we need to be careful not to touch attributes, scripts, etc.
    points = []

    # Find all <p> tags with content (the primary target)
    for m in re.finditer(r'(<p[^>]*>)(.*?)(</p>)', body_html, re.DOTALL | re.IGNORECASE):
        tag_open = m.group(1)
        inner = m.group(2)
        tag_close = m.group(3)
        # Skip if it's a very short snippet or already contains many links
        if len(inner.strip()) < 40:
            continue
        existing_links = len(re.findall(r'<a\s', inner, re.IGNORECASE))
        if existing_links >= 2:
            continue
        points.append({
            'full_start': m.start(),
            'full_end': m.end(),
            'inner_start': m.start(2),
            'inner_end': m.end(2),
            'inner': inner,
            'tag_open': tag_open,
            'tag_close': tag_close,
        })

    # Also target verdict paragraphs and bottom-line divs
    for m in re.finditer(r'(<div\s+class="(?:bottom-line|ba-text|faq-a)"[^>]*>)(.*?)(</div>)',
                         body_html, re.DOTALL | re.IGNORECASE):
        inner = m.group(2)
        if len(inner.strip()) < 40:
            continue
        existing_links = len(re.findall(r'<a\s', inner, re.IGNORECASE))
        if existing_links >= 2:
            continue
        points.append({
            'full_start': m.start(),
            'full_end': m.end(),
            'inner_start': m.start(2),
            'inner_end': m.end(2),
            'inner': inner,
            'tag_open': m.group(1),
            'tag_close': m.group(3),
        })

    return points


def insert_link_in_text(text, anchor_text, href, title):
    """Insert a link near a contextually relevant spot in the text.
    Returns (modified_text, success_bool)."""
    # Don't insert if this href is already in the text
    if href in text:
        return text, False

    # Don't insert inside existing <a> tags
    # Find a good insertion point: end of a sentence in plain text
    # We look for text nodes (not inside tags) where we can append a contextual link

    # Strategy: find the last period-ending sentence in plain text and append the link after it
    # This reads naturally: "...some statement. Read more about [anchor text] here."

    # First, get only the plain text portions (outside of HTML tags)
    # Find sentence boundaries in the text
    sentences = list(re.finditer(r'([^<>]*?[.!?])\s*(?=(?:[A-Z<]|$))', text))

    if not sentences:
        # No sentence boundaries found; try inserting before the last closing tag
        # Find the last chunk of plain text
        plain_chunks = list(re.finditer(r'>([^<]{20,})', text))
        if plain_chunks:
            chunk = plain_chunks[-1]
            insert_pos = chunk.end()
            link_html = f' For more, see <a href="{href}" title="{title}">{anchor_text}</a>.'
            return text[:insert_pos] + link_html + text[insert_pos:], True
        return text, False

    # Pick a sentence in the middle-to-end of the text for natural placement
    target_idx = max(0, len(sentences) // 2)
    # But prefer later sentences for more natural reading flow
    if len(sentences) > 2:
        target_idx = len(sentences) - 2  # Second to last sentence

    target = sentences[target_idx]
    insert_pos = target.end()

    # Make sure we're not inside an HTML tag
    # Count open < and > before insert_pos
    before_text = text[:insert_pos]
    open_tags = before_text.count('<') - before_text.count('>')
    if open_tags > 0:
        # We're inside a tag, skip to after the next >
        next_close = text.find('>', insert_pos)
        if next_close >= 0:
            insert_pos = next_close + 1
        else:
            return text, False

    # Check we're not inserting inside an <a> tag
    # Find the last <a before insert_pos and see if there's a matching </a>
    last_a_open = before_text.rfind('<a ')
    if last_a_open >= 0:
        last_a_close = before_text.rfind('</a>', last_a_open)
        if last_a_close < last_a_open:
            # We're inside an unclosed <a> tag, don't insert here
            return text, False

    link_html = f' You may also like <a href="{href}" title="{title}">{anchor_text}</a>.'
    return text[:insert_pos] + link_html + text[insert_pos:], True


def add_links_to_article(filepath, all_articles, max_links=5):
    """Add contextual internal links to an article. Returns count of links added."""
    try:
        content = Path(filepath).read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        print(f"  Error reading {filepath}: {e}")
        return 0

    current_filename = Path(filepath).name
    current_data = all_articles.get(current_filename)
    if not current_data:
        return 0

    # Count existing internal links (to other articles in same directory)
    existing_internal_links = len(re.findall(r'<a\s+href="[^"]*\.html"', content, re.IGNORECASE))
    if existing_internal_links >= max_links:
        return 0

    links_remaining = max_links - existing_internal_links

    # Find related articles ranked by relevance
    related = find_related_articles(
        current_filename, current_data['keywords'], all_articles, max_results=10
    )

    if not related:
        return 0

    # Filter out articles already linked in this page
    candidates = []
    for filename, score, data in related:
        if filename not in content:  # Not already linked anywhere
            candidates.append((filename, score, data))

    if not candidates:
        return 0

    # Get body section to work with
    body_match = re.search(r'(<body[^>]*>)(.*?)(</body>)', content, re.IGNORECASE | re.DOTALL)
    if not body_match:
        return 0

    body_before = content[:body_match.start(2)]
    body_html = body_match.group(2)
    body_after = content[body_match.end(2):]

    # Find safe insertion points (paragraphs and text containers)
    insertion_points = find_safe_insertion_points(body_html)

    if not insertion_points:
        return 0

    links_added = 0
    used_points = set()  # Track which insertion points we've used

    for filename, score, data in candidates:
        if links_added >= links_remaining:
            break

        title = data['title']
        href = filename  # Relative path -- all in same /articles/ directory

        # Escape title for HTML attribute
        safe_title = title.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        safe_anchor = title  # Use full article title as anchor text

        # Try each available insertion point
        for i, point in enumerate(insertion_points):
            if i in used_points:
                continue

            inner = point['inner']

            # Check this href isn't already in this element
            if href in inner:
                continue

            modified_inner, success = insert_link_in_text(inner, safe_anchor, href, safe_title)

            if success:
                # Replace the inner content in body_html
                # We need to rebuild using offsets -- but since we're modifying body_html
                # in-place multiple times, use string replacement on the specific inner text
                old_full = point['tag_open'] + inner + point['tag_close']
                new_full = point['tag_open'] + modified_inner + point['tag_close']

                if old_full in body_html:
                    body_html = body_html.replace(old_full, new_full, 1)
                    used_points.add(i)
                    links_added += 1
                    break

    if links_added > 0:
        new_content = body_before + body_html + body_after
        try:
            Path(filepath).write_text(new_content, encoding='utf-8')
        except Exception as e:
            print(f"  Error writing {filepath}: {e}")
            return 0

    return links_added


def update_sitemap(sitemap_path, articles_dir, base_url):
    """Regenerate sitemap with all articles and fresh lastmod dates."""
    from datetime import date
    today = date.today().isoformat()

    if not os.path.exists(sitemap_path):
        print(f"  Sitemap not found: {sitemap_path}")
        return

    # Read existing sitemap to preserve non-article URLs
    existing = Path(sitemap_path).read_text(encoding='utf-8', errors='ignore')

    # Extract non-article URLs (homepage, pages, etc.)
    non_article_urls = []
    for m in re.finditer(
        r'<url>\s*<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>\s*<changefreq>(.*?)</changefreq>\s*<priority>(.*?)</priority>\s*</url>',
        existing, re.DOTALL
    ):
        loc = m.group(1)
        if '/articles/' not in loc:
            non_article_urls.append({
                'loc': loc,
                'lastmod': m.group(2),
                'changefreq': m.group(3),
                'priority': m.group(4),
            })

    # Build new sitemap
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    # Add non-article pages first (update lastmod to today)
    for page in non_article_urls:
        lines.append('  <url>')
        lines.append(f'    <loc>{page["loc"]}</loc>')
        lines.append(f'    <lastmod>{today}</lastmod>')
        lines.append(f'    <changefreq>{page["changefreq"]}</changefreq>')
        lines.append(f'    <priority>{page["priority"]}</priority>')
        lines.append('  </url>')

    # Add all HTML articles
    article_count = 0
    for f in sorted(Path(articles_dir).glob('*.html')):
        article_count += 1
        loc = f"{base_url}/articles/{f.name}"
        lines.append('  <url>')
        lines.append(f'    <loc>{loc}</loc>')
        lines.append(f'    <lastmod>{today}</lastmod>')
        lines.append(f'    <changefreq>weekly</changefreq>')
        lines.append(f'    <priority>0.7</priority>')
        lines.append('  </url>')

    lines.append('</urlset>')

    Path(sitemap_path).write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"  Sitemap updated: {article_count} articles, lastmod={today}")


def main():
    parser = argparse.ArgumentParser(description='Add contextual internal links between brand articles')
    parser.add_argument(
        '--brand',
        choices=['fitness', 'deals', 'menopause', 'all'],
        default='all',
        help='Process specific brand or all brands'
    )
    parser.add_argument(
        '--max-links',
        type=int,
        default=5,
        help='Maximum internal links per article (default: 5)'
    )
    parser.add_argument(
        '--update-sitemaps',
        action='store_true',
        help='Also update sitemaps with fresh lastmod dates'
    )
    args = parser.parse_args()

    brands_to_process = BRANDS if args.brand == 'all' else {args.brand: BRANDS[args.brand]}

    SITEMAP_CONFIG = {
        'fitness': {
            'sitemap': 'outputs/fitover35-website/sitemap.xml',
            'base_url': 'https://fitover35.com',
        },
        'deals': {
            'sitemap': 'outputs/dailydealdarling-website/sitemap.xml',
            'base_url': 'https://dailydealdarling.com',
        },
        'menopause': {
            'sitemap': 'outputs/menopause-planner-website/sitemap.xml',
            'base_url': 'https://menopause-planner-website.vercel.app',
        },
    }

    grand_total = 0
    for brand, articles_dir in brands_to_process.items():
        if not os.path.exists(articles_dir):
            print(f"Skipping {brand}: directory {articles_dir} not found")
            continue

        print(f"\n{'='*60}")
        print(f"Processing {brand} ({articles_dir})")
        print(f"{'='*60}")

        # Build article index for this brand
        all_articles = get_article_data(articles_dir)
        print(f"  Indexed {len(all_articles)} articles")

        if len(all_articles) < 2:
            print(f"  Not enough articles to link")
            continue

        # Process each article
        total_links = 0
        articles_modified = 0
        for filepath in sorted(Path(articles_dir).glob('*.html')):
            links = add_links_to_article(filepath, all_articles, max_links=args.max_links)
            if links > 0:
                print(f"  +{links} links: {filepath.name}")
                total_links += links
                articles_modified += 1

        print(f"\n  Summary for {brand}:")
        print(f"    Articles processed: {len(all_articles)}")
        print(f"    Articles modified:  {articles_modified}")
        print(f"    Total links added:  {total_links}")
        grand_total += total_links

        # Update sitemap if requested
        if args.update_sitemaps and brand in SITEMAP_CONFIG:
            cfg = SITEMAP_CONFIG[brand]
            update_sitemap(cfg['sitemap'], articles_dir, cfg['base_url'])

    print(f"\n{'='*60}")
    print(f"GRAND TOTAL: {grand_total} internal links added across all brands")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
