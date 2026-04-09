"""
Phase 7: Meta Description Improvement Script

Scans all HTML articles across 3 brands and improves meta descriptions
using pattern-based templates (no AI API calls).
"""

import os
import re
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path

# Audience mapping by brand
AUDIENCE_MAP = {
    'fitness': 'men over 35',
    'deals': 'smart shoppers',
    'menopause': 'women 40+'
}

# CTA words to check for
CTA_WORDS = [
    'discover', 'find', 'learn', 'get', 'see', 'check', 'compare',
    'try', 'explore', 'shop', 'save', 'grab', 'unlock', 'rated', 'reviewed'
]

def extract_primary_keyword(title):
    """Extract primary keyword from title"""
    # Remove common filler words
    filler = ['the', 'best', 'top', 'a', 'an', 'for', 'in', 'on', 'at', 'to', 'of']
    words = title.lower().split()

    # Find the core phrase (usually 2-4 words after removing fillers)
    core_words = [w for w in words if w not in filler and len(w) > 2]

    # Return first 3-4 significant words as keyword
    if len(core_words) >= 3:
        return ' '.join(core_words[:3])
    return ' '.join(core_words)

def has_cta(description):
    """Check if description contains a CTA word"""
    desc_lower = description.lower()
    return any(cta in desc_lower for cta in CTA_WORDS)

def is_too_generic(description, title):
    """Check if description is just repeating the title"""
    # Normalize both strings
    desc_norm = re.sub(r'[^\w\s]', '', description.lower())
    title_norm = re.sub(r'[^\w\s]', '', title.lower())

    # Check if description is just title + minimal addition
    if title_norm in desc_norm and len(desc_norm) - len(title_norm) < 20:
        return True
    return False

def should_flag(description, title):
    """Determine if meta description should be flagged for improvement"""
    if not description:
        return True, "missing"

    length = len(description)
    if length < 120:
        return True, "too_short"
    if length > 160:
        return True, "too_long"
    if not has_cta(description):
        return True, "no_cta"
    if is_too_generic(description, title):
        return True, "too_generic"

    return False, None

def generate_improved_description(title, brand, date_published=None):
    """Generate improved meta description using templates"""
    keyword = extract_primary_keyword(title)
    audience = AUDIENCE_MAP.get(brand, 'readers')

    # Extract year from date or use current year
    year = "2026"
    month = datetime.now().strftime("%B")
    if date_published:
        try:
            date_obj = datetime.fromisoformat(date_published.replace('Z', '+00:00'))
            year = str(date_obj.year)
            month = date_obj.strftime("%B")
        except:
            pass

    # Detect article type from title
    title_lower = title.lower()

    # Review template
    if any(word in title_lower for word in ['review', 'rated', 'ranked', 'tested']):
        return f"{keyword.title()} — tested, rated & ranked for {year}. See the top picks that {audience} trust. Updated {month} {year}."

    # List template
    if re.search(r'\d+\s+(best|top)', title_lower):
        # Extract the number
        match = re.search(r'(\d+)\s+(?:best|top)', title_lower)
        num = match.group(1) if match else "top"
        return f"The {num} best {keyword} — compared & reviewed for {audience}. Expert picks backed by research. Updated {month} {year}."

    # Guide template
    if any(word in title_lower for word in ['guide', 'how to', 'tips', 'ways']):
        return f"Expert {keyword} guide for {audience}. Proven strategies and actionable tips. Find what works — backed by research."

    # Default template
    return f"Discover the best {keyword} for {audience}. Expert reviews, comparisons & recommendations. Updated {month} {year}."

def process_article(filepath, brand):
    """Process a single article HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Extract current meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    current_desc = meta_desc.get('content', '') if meta_desc else ''

    # Extract title
    title_tag = soup.find('title')
    title = title_tag.text if title_tag else ''

    # Extract date published
    date_published = None
    script_ld = soup.find('script', type='application/ld+json')
    if script_ld:
        import json
        try:
            ld_data = json.loads(script_ld.string)
            date_published = ld_data.get('datePublished')
        except:
            pass

    # Check if should be flagged
    should_improve, reason = should_flag(current_desc, title)

    if not should_improve:
        return None, None, None  # No improvement needed

    # Generate improved description
    new_desc = generate_improved_description(title, brand, date_published)

    # Truncate to 160 chars if needed
    if len(new_desc) > 160:
        new_desc = new_desc[:157] + '...'

    # Update all meta description tags
    updated = False

    # Update meta name="description"
    if meta_desc:
        meta_desc['content'] = new_desc
        updated = True
    else:
        # Create new meta tag
        new_meta = soup.new_tag('meta', attrs={'name': 'description', 'content': new_desc})
        if soup.head:
            soup.head.append(new_meta)
            updated = True

    # Update og:description
    og_desc = soup.find('meta', property='og:description')
    if og_desc:
        og_desc['content'] = new_desc
    else:
        new_og = soup.new_tag('meta', attrs={'property': 'og:description', 'content': new_desc})
        if soup.head:
            soup.head.append(new_og)

    # Update twitter:description
    twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
    if twitter_desc:
        twitter_desc['content'] = new_desc
    else:
        new_twitter = soup.new_tag('meta', attrs={'name': 'twitter:description', 'content': new_desc})
        if soup.head:
            soup.head.append(new_twitter)

    if updated:
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))

    return current_desc, new_desc, reason

def main():
    base_path = Path('C:/Users/talha/Desktop/social-media-empire/outputs')

    # Define article directories for each brand
    directories = {
        'fitness': base_path / 'fitover35-website/articles',
        'deals': base_path / 'dailydealdarling-website/articles',
        'menopause': base_path / 'menopause-planner-website/articles'
    }

    stats = {
        'total': 0,
        'flagged': 0,
        'improved': 0,
        'by_brand': {
            'fitness': {'total': 0, 'flagged': 0, 'improved': 0},
            'deals': {'total': 0, 'flagged': 0, 'improved': 0},
            'menopause': {'total': 0, 'flagged': 0, 'improved': 0}
        },
        'by_reason': {}
    }

    print("=" * 60)
    print("META DESCRIPTION IMPROVEMENT - PHASE 7")
    print("=" * 60)
    print()

    for brand, dir_path in directories.items():
        if not dir_path.exists():
            print(f"WARNING: Directory not found: {dir_path}")
            continue

        print(f"Scanning {brand.upper()} articles...")

        # Find all HTML files
        html_files = list(dir_path.glob('*.html'))

        for filepath in html_files:
            stats['total'] += 1
            stats['by_brand'][brand]['total'] += 1

            current, new, reason = process_article(filepath, brand)

            if new:  # Improvement was made
                stats['flagged'] += 1
                stats['improved'] += 1
                stats['by_brand'][brand]['flagged'] += 1
                stats['by_brand'][brand]['improved'] += 1

                # Track reason
                if reason:
                    stats['by_reason'][reason] = stats['by_reason'].get(reason, 0) + 1

                print(f"  IMPROVED: {filepath.name}")
                print(f"    Old: {current[:80]}...")
                print(f"    New: {new[:80]}...")
                print()

    # Print summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total articles scanned: {stats['total']}")
    print(f"Flagged for improvement: {stats['flagged']}")
    print(f"Successfully improved: {stats['improved']}")
    print()

    print("BY BRAND:")
    for brand, brand_stats in stats['by_brand'].items():
        print(f"  {brand.upper()}: {brand_stats['improved']}/{brand_stats['total']} improved")
    print()

    if stats['by_reason']:
        print("BY REASON:")
        for reason, count in stats['by_reason'].items():
            print(f"  {reason}: {count}")

    print()
    print("Meta description improvement complete!")

if __name__ == '__main__':
    main()
