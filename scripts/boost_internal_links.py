"""Phase 5: Internal linking boost across all 3 brands.

Adds 'Related Articles' section and contextual inline links to each article.
"""

import os
import re
from collections import defaultdict

BRANDS = {
    'fitness': {
        'dir': 'outputs/fitover35-website/articles',
        'hub_dir': 'outputs/fitover35-website',
        'hubs': ['supplements.html', 'workouts.html', 'nutrition.html', 'gear.html'],
    },
    'deals': {
        'dir': 'outputs/dailydealdarling-website/articles',
        'hub_dir': 'outputs/dailydealdarling-website',
        'hubs': ['kitchen.html', 'home.html', 'beauty.html', 'mom.html'],
    },
    'menopause': {
        'dir': 'outputs/menopause-planner-website/articles',
        'hub_dir': 'outputs/menopause-planner-website',
        'hubs': ['supplements.html', 'sleep.html', 'wellness.html'],
    },
}

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(title):
    """Extract meaningful keywords from article title."""
    stop_words = {
        'the', 'a', 'an', 'for', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
        'of', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
        'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
        'might', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'with',
        'this', 'that', 'these', 'those', 'it', 'its', 'my', 'your', 'our',
        'their', 'his', 'her', 'we', 'they', 'you', 'i', 'me', 'us', 'him',
        'them', 'who', 'what', 'which', 'when', 'where', 'why', 'how', 'all',
        'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
        'just', 'because', 'as', 'until', 'while', 'about', 'between', 'through',
        'during', 'before', 'after', 'above', 'below', 'from', 'up', 'down',
        'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
        'men', 'women', 'best', 'top', 'guide', 'review', 'complete', 'ultimate',
        '2024', '2025', '2026', 'over', '35', '40', '45', '50',
    }
    words = re.findall(r'[a-z]+', title.lower())
    return set(w for w in words if w not in stop_words and len(w) > 2)


def get_article_info(filepath):
    """Extract title and meta description from an article."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(3000)  # Only need the head section
    except Exception:
        return None, None

    title_match = re.search(r'<title>(.*?)</title>', content)
    title = title_match.group(1) if title_match else ''
    # Strip brand suffix
    for suffix in [' — FitOver35', ' | FitOver35', ' — Daily Deal Darling',
                   ' | Daily Deal Darling', ' — The Menopause Planner',
                   ' | The Menopause Planner']:
        title = title.replace(suffix, '')

    desc_match = re.search(r'<meta name="description" content="(.*?)"', content)
    desc = desc_match.group(1) if desc_match else ''

    return title, desc


def find_related_articles(target_file, target_keywords, all_articles, max_related=5):
    """Find related articles by keyword overlap."""
    scores = []
    for filepath, (title, desc, keywords) in all_articles.items():
        if filepath == target_file:
            continue
        overlap = len(target_keywords & keywords)
        if overlap >= 2:
            scores.append((overlap, filepath, title))

    scores.sort(reverse=True)
    return scores[:max_related]


def build_related_section(related, brand_key):
    """Build the Related Articles HTML section."""
    if not related:
        return ''

    items = ''
    for _, filepath, title in related:
        filename = os.path.basename(filepath)
        items += (
            f'<li style="padding:6px 0">'
            f'<a href="{filename}" style="color:var(--accent);text-decoration:none;'
            f'font-size:.88rem">{title}</a></li>\n'
        )

    return (
        f'\n<div style="background:var(--surface);border:1px solid var(--border);'
        f'border-radius:12px;padding:20px;margin:24px 0">'
        f'<h3 style="font-family:\'Instrument Serif\',serif;font-size:1.05rem;'
        f'margin-bottom:12px">Related Articles</h3>'
        f'<ul style="list-style:none;padding:0;margin:0">\n{items}</ul></div>\n'
    )


def count_existing_internal_links(content, articles_dir):
    """Count how many internal article links already exist."""
    files = set(os.path.basename(f) for f in os.listdir(articles_dir) if f.endswith('.html'))
    count = 0
    for f in files:
        if f in content:
            count += 1
    return count


def process_brand(brand_key, config):
    """Process all articles for a brand."""
    articles_dir = os.path.join(WORKSPACE, config['dir'])
    if not os.path.isdir(articles_dir):
        print(f"  Directory not found: {articles_dir}")
        return 0

    # Build article index
    all_articles = {}
    for fname in sorted(os.listdir(articles_dir)):
        if not fname.endswith('.html'):
            continue
        filepath = os.path.join(articles_dir, fname)
        title, desc = get_article_info(filepath)
        if title:
            keywords = extract_keywords(title)
            if desc:
                keywords |= extract_keywords(desc)
            all_articles[filepath] = (title, desc, keywords)

    print(f"  Indexed {len(all_articles)} articles")

    total_links_added = 0

    for filepath, (title, desc, keywords) in all_articles.items():
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception:
            continue

        # Skip if already has a Related Articles section
        if 'Related Articles</h3>' in content:
            continue

        existing_count = count_existing_internal_links(content, articles_dir)
        if existing_count >= 8:
            continue  # Max 8 internal links

        related = find_related_articles(filepath, keywords, all_articles, max_related=5)
        if not related:
            continue

        # Limit to not exceed 8 total links
        max_new = min(len(related), 8 - existing_count)
        related = related[:max_new]

        related_html = build_related_section(related, brand_key)
        if not related_html:
            continue

        # Insert before the final email signup form or footer
        # Look for the final-cta div or footer
        insert_patterns = [
            '<div class="final-cta">',
            '<div class="footer">',
            '</body>',
        ]

        inserted = False
        for pattern in insert_patterns:
            idx = content.rfind(pattern)
            if idx > 0:
                content = content[:idx] + related_html + content[idx:]
                inserted = True
                break

        if inserted:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            total_links_added += len(related)

    return total_links_added


def main():
    print("=" * 60)
    print("PHASE 5: Internal Linking Boost")
    print("=" * 60)

    total = 0
    for brand_key, config in BRANDS.items():
        print(f"\n--- {brand_key.upper()} ---")
        count = process_brand(brand_key, config)
        print(f"  Links added: {count}")
        total += count

    print(f"\n{'=' * 60}")
    print(f"TOTAL internal links added: {total}")
    print("=" * 60)


if __name__ == '__main__':
    main()
