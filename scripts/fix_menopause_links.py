#!/usr/bin/env python3
"""
Fix menopause article Amazon links: replace search URLs with direct product links.
Processes all HTML files in outputs/menopause-planner-website/articles/
"""

import os
import re
import urllib.parse
from pathlib import Path
from difflib import SequenceMatcher

# Comprehensive ASIN dictionary for menopause/wellness products
ASIN_MAP = {
    # Menopause Supplements
    "black cohosh": "B0019LTI86",
    "evening primrose oil": "B00DWCZWHK",
    "magnesium glycinate": "B000BD0RT0",
    "magnesium": "B000BD0RT0",
    "vitamin d3": "B00GB85JR4",
    "vitamin d": "B00GB85JR4",
    "calcium": "B001G7QUXW",
    "collagen": "B00K6JUG40",
    "collagen powder": "B00K6JUG40",
    "collagen peptides": "B00K6JUG40",
    "probiotics": "B07K2GKZLM",
    "omega 3": "B004O2I9JO",
    "fish oil": "B004O2I9JO",
    "maca root": "B007IM1XFM",
    "ashwagandha": "B078K18HYN",
    "turmeric": "B01K2JUMJQ",
    "iron supplement": "B0019GKIB4",
    "b12 vitamin": "B005DG6GK6",
    "vitamin b complex": "B005F24H30",
    "dong quai": "B000MRISUE",
    "red clover": "B000MRIVAG",
    "soy isoflavones": "B007U2GZIY",
    "dhea": "B000NRVXGS",
    "vitex": "B0019LSF8Q",
    "chasteberry": "B0019LSF8Q",
    "st johns wort": "B000GG567Q",
    "valerian root": "B0012AMVHW",
    "melatonin": "B005DEK990",
    "5 htp": "B005GFLNA6",
    "l theanine": "B000JKD7OC",
    "multivitamin women": "B00J36DNR8",

    # Sleep
    "cooling pillow": "B07C7FQBDT",
    "bamboo sheets": "B07QDFLQ7J",
    "cooling pajamas": "B07YC684QN",
    "weighted blanket": "B07H2DKQGJ",
    "silk pillowcase": "B07P3SQCV3",
    "white noise machine": "B00MY8V86O",
    "sleep mask": "B07KC5DWCC",
    "essential oils diffuser": "B07L4R62GQ",
    "diffuser": "B07L4R62GQ",
    "lavender oil": "B005V2WRZI",
    "blackout curtains": "B0725T8FD5",
    "cooling mattress pad": "B07X3BKDPH",
    "bed fan": "B07SRJ4C1B",
    "cooling blanket": "B092QNCL7Q",

    # Wellness/Self-Care
    "symptom tracker journal": "B0BW9GDRP7",
    "journal": "B0BW9GDRP7",
    "yoga mat": "B01LYBOA9L",
    "resistance bands": "B01AVDVHTI",
    "foam roller": "B0040EKZDY",
    "face roller": "B07WRFQ1Q5",
    "jade roller": "B07WRFQ1Q5",
    "gua sha": "B082FJSSV6",
    "dry brush": "B07F5B9HRN",
    "bath salts": "B01CUV6NMS",
    "epsom salt": "B004N7DQHA",
    "heating pad": "B00075M1T6",
    "hot water bottle": "B07DFPNZ4Y",
    "tens unit": "B00NCRE4GO",
    "acupressure mat": "B07BFGH97T",
    "meditation cushion": "B01MAU17HF",
    "eye mask heated": "B07KC5DWCC",

    # Clothing/Comfort
    "moisture wicking clothes": "B077GWLWTR",
    "cooling towel": "B07MWCDR79",
    "compression socks": "B077GWLWTR",
    "comfort bra": "B071KPRQKN",

    # Home
    "fan": "B07DCVY6YQ",
    "humidifier": "B013IJPTFK",
    "air purifier": "B07VVK39F7",
    "water filter": "B015QS4OG0",
    "tea set": "B073W6F8K9",
    "herbal tea": "B0009F3QL6",
}


def fuzzy_match(query, threshold=0.6):
    """Find best ASIN match for a query using fuzzy matching."""
    query_lower = query.lower().strip()

    # Exact match first
    if query_lower in ASIN_MAP:
        return ASIN_MAP[query_lower]

    # Fuzzy match
    best_match = None
    best_ratio = 0

    for key in ASIN_MAP.keys():
        ratio = SequenceMatcher(None, query_lower, key).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = key

    if best_ratio >= threshold:
        return ASIN_MAP[best_match]

    return None


def extract_search_query(url):
    """Extract search query from Amazon search URL."""
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)

        if 'k' in params:
            return params['k'][0]
        return None
    except Exception as e:
        print(f"Error parsing URL: {url} - {e}")
        return None


def process_file(filepath):
    """Process a single HTML file and replace search URLs."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    replaced_count = 0
    remaining_count = 0

    # Find all Amazon search URLs
    pattern = r'https://www\.amazon\.com/s\?k=([^&\s"\']+)(?:[^"\']*tag=([^&\s"\']+))?'

    def replace_url(match):
        nonlocal replaced_count, remaining_count

        full_url = match.group(0)
        search_query = urllib.parse.unquote_plus(match.group(1))
        existing_tag = match.group(2) if match.group(2) else "dailydealdarl-20"

        # Try to find ASIN
        asin = fuzzy_match(search_query)

        if asin:
            # Replace with direct product link
            new_url = f"https://www.amazon.com/dp/{asin}?tag=dailydealdarl-20"
            replaced_count += 1
            return new_url
        else:
            # Keep search URL but ensure correct tag
            remaining_count += 1
            if "tag=" not in full_url:
                return f"{full_url}&tag=dailydealdarl-20"
            return full_url

    content = re.sub(pattern, replace_url, content)

    # Write back if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return replaced_count, remaining_count


def main():
    articles_dir = Path("outputs/menopause-planner-website/articles")

    if not articles_dir.exists():
        print(f"Error: {articles_dir} does not exist")
        return

    html_files = list(articles_dir.glob("*.html"))
    print(f"Found {len(html_files)} HTML files\n")

    total_replaced = 0
    total_remaining = 0
    errors = 0

    for filepath in sorted(html_files):
        try:
            replaced, remaining = process_file(filepath)
            total_replaced += replaced
            total_remaining += remaining

            if replaced > 0 or remaining > 0:
                print(f"{filepath.name}: {replaced} replaced, {remaining} remaining")
        except Exception as e:
            print(f"ERROR in {filepath.name}: {e}")
            errors += 1

    print("\n" + "="*60)
    print(f"FINAL RESULTS:")
    print(f"  Total replaced: {total_replaced}")
    print(f"  Total remaining: {total_remaining}")
    print(f"  Total processed: {len(html_files)}")
    print(f"  Errors: {errors}")
    print("="*60)


if __name__ == "__main__":
    main()
