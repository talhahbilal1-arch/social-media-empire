#!/usr/bin/env python3
"""Fix duplicate affiliate tags in Amazon URLs across all brand articles.

Scans all HTML articles and:
1. Removes duplicate tag= parameters from Amazon URLs
2. Converts search URLs that are just ASINs to direct /dp/ links
3. Ensures correct brand-specific affiliate tag
"""

import os
import re
import html as htmlmod
from urllib.parse import urlparse, parse_qs, urlencode, unquote_plus

# Brand tag mapping
BRAND_TAGS = {
    "outputs/fitover35-website/articles": "fitover3509-20",
    "outputs/dailydealdarling-website/articles": "dailydealdarl-20",
    "outputs/menopause-planner-website/articles": "dailydealdarl-20",
}

# Wrong tags to replace
WRONG_TAGS = {"fitover35-20", "dailydealdarling1-20", "dailydealdarling-20"}

# ASIN pattern
ASIN_RE = re.compile(r'^[Bb][0-9A-Za-z]{9}$')


def fix_amazon_url(url_raw, correct_tag):
    """Fix a single Amazon URL: remove duplicate tags, fix wrong tags."""
    # Decode HTML entities
    url = htmlmod.unescape(url_raw)

    # Extract ASIN from /dp/ URLs
    dp_match = re.search(r'/dp/([A-Z0-9]{10})', url, re.IGNORECASE)

    # Check if it's a search URL where the query IS an ASIN
    search_asin = None
    if '/s?' in url or '/s%3F' in url:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'k' in params:
            query_val = params['k'][0].strip()
            if ASIN_RE.match(query_val):
                search_asin = query_val.upper()

    if dp_match:
        # Direct product URL — rebuild clean
        asin = dp_match.group(1).upper()
        return f"https://www.amazon.com/dp/{asin}?tag={correct_tag}"

    if search_asin:
        # Search URL with ASIN as query — convert to direct link
        return f"https://www.amazon.com/dp/{search_asin}?tag={correct_tag}"

    # For all other URLs (search, category, etc.): strip duplicate/wrong tags
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)

    # Remove all tag params and add exactly one correct tag
    if 'tag' in params:
        params['tag'] = [correct_tag]

    # Rebuild query string
    clean_params = []
    for key, values in params.items():
        for val in values:
            clean_params.append((key, val))

    new_query = urlencode(clean_params)
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if new_query:
        clean_url += f"?{new_query}"

    return clean_url


def process_file(filepath, correct_tag):
    """Process a single HTML file, fixing all Amazon URLs."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    fixes = {"duplicate_tags": 0, "wrong_tags": 0, "asin_search": 0, "dp_cleaned": 0}

    def replace_href(match):
        url_raw = match.group(1)

        # Only process amazon URLs
        decoded = htmlmod.unescape(url_raw)
        if 'amazon.com' not in decoded.lower():
            return match.group(0)

        tag_count = len(re.findall(r'tag=', decoded))
        has_wrong = any(wt in decoded for wt in WRONG_TAGS)

        # Check if it's a search-as-ASIN
        is_asin_search = False
        if '/s?' in decoded:
            parsed = urlparse(decoded)
            params = parse_qs(parsed.query)
            if 'k' in params and ASIN_RE.match(params['k'][0].strip()):
                is_asin_search = True

        # Only fix if there's actually a problem
        if tag_count <= 1 and not has_wrong and not is_asin_search:
            return match.group(0)

        fixed = fix_amazon_url(url_raw, correct_tag)

        if tag_count > 1:
            fixes["duplicate_tags"] += 1
        if has_wrong:
            fixes["wrong_tags"] += 1
        if is_asin_search:
            fixes["asin_search"] += 1
        if '/dp/' in decoded and tag_count > 1:
            fixes["dp_cleaned"] += 1

        return f'href="{fixed}"'

    # Fix href attributes
    content = re.sub(r'href="([^"]*amazon[^"]*?)"', replace_href, content)

    # Also fix URLs inside JSON-LD schema blocks
    def replace_schema_url(match):
        url_raw = match.group(1)
        if 'amazon.com' not in url_raw.lower():
            return match.group(0)
        decoded = htmlmod.unescape(url_raw)
        tag_count = len(re.findall(r'tag=', decoded))
        if tag_count <= 1:
            return match.group(0)
        fixed = fix_amazon_url(url_raw, correct_tag)
        return f'"url": "{fixed}"'

    content = re.sub(r'"url":\s*"([^"]*amazon[^"]*?)"', replace_schema_url, content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return fixes


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    total_fixes = {"duplicate_tags": 0, "wrong_tags": 0, "asin_search": 0, "dp_cleaned": 0}
    files_modified = 0

    for brand_dir, tag in BRAND_TAGS.items():
        full_dir = os.path.join(base, brand_dir)
        if not os.path.isdir(full_dir):
            print(f"SKIP: {brand_dir} (not found)")
            continue

        brand_fixes = {"duplicate_tags": 0, "wrong_tags": 0, "asin_search": 0, "dp_cleaned": 0}
        brand_files = 0

        for fn in sorted(os.listdir(full_dir)):
            if not fn.endswith('.html'):
                continue
            filepath = os.path.join(full_dir, fn)
            fixes = process_file(filepath, tag)
            if any(v > 0 for v in fixes.values()):
                brand_files += 1
                for k, v in fixes.items():
                    brand_fixes[k] += v

        print(f"\n{brand_dir}:")
        print(f"  Files modified: {brand_files}")
        print(f"  Duplicate tags fixed: {brand_fixes['duplicate_tags']}")
        print(f"  Wrong tags fixed: {brand_fixes['wrong_tags']}")
        print(f"  ASIN-as-search converted: {brand_fixes['asin_search']}")

        files_modified += brand_files
        for k, v in brand_fixes.items():
            total_fixes[k] += v

    print(f"\n=== TOTALS ===")
    print(f"Files modified: {files_modified}")
    print(f"Duplicate tags fixed: {total_fixes['duplicate_tags']}")
    print(f"Wrong tags fixed: {total_fixes['wrong_tags']}")
    print(f"ASIN-as-search converted: {total_fixes['asin_search']}")


if __name__ == "__main__":
    main()
