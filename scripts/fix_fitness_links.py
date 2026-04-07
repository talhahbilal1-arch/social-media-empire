#!/usr/bin/env python3
"""
Replace Amazon search URLs with direct product URLs in fitness articles.
Ensures all links use correct affiliate tag: fitover3509-20
"""

import os
import re
from urllib.parse import unquote, quote_plus
from pathlib import Path

# Comprehensive ASIN mapping for fitness products
ASIN_MAP = {
    # Supplements
    "creatine": "B002DYIZEO",
    "creatine monohydrate": "B002DYIZEO",
    "nutricost creatine": "B00EIY7AXE",
    "vitamin d3": "B00GB85JR4",
    "vitamin d": "B00GB85JR4",
    "magnesium": "B000BD0RT0",
    "magnesium glycinate": "B000BD0RT0",
    "magnesium sleep": "B000BD0RT0",
    "fish oil": "B004O2I9JO",
    "omega 3": "B004O2I9JO",
    "omega-3": "B004O2I9JO",
    "ashwagandha": "B078K6DHN1",
    "ksm-66 ashwagandha": "B078K6DHN1",
    "protein powder": "B000QSNYGI",
    "whey protein": "B000QSNYGI",
    "optimum nutrition": "B000QSNYGI",
    "optimum nutrition gold standard": "B000QSNYGI",
    "optimum nutrition gold standard whey protein": "B000QSNYGI",
    "gold standard whey": "B000QSNYGI",
    "collagen": "B00K6JUG40",
    "collagen peptides": "B00K6JUG40",
    "vital proteins collagen": "B00K6JUG40",
    "zinc": "B003QB97MC",
    "zinc picolinate": "B001B4WQ1S",
    "thorne zinc": "B001B4WQ1S",
    "thorne zinc picolinate": "B001B4WQ1S",
    "bcaa": "B00E7GV65Q",
    "branched chain amino acids": "B00E7GV65Q",
    "pre workout": "B07DNRXWF7",
    "preworkout": "B07DNRXWF7",
    "c4 pre workout": "B07DNRXWF7",
    "c4 original": "B07DNRXWF7",
    "nutrabolt c4": "B07DNRXWF7",
    "multivitamin": "B000GG2I9O",
    "multivitamin men": "B000GG2I9O",
    "multivitamin for men over 35": "B000GG2I9O",
    "mens multivitamin": "B000GG2I9O",
    "probiotics": "B07K2GKZLM",
    "probiotic": "B07K2GKZLM",
    "turmeric": "B01K2JUMJQ",
    "curcumin": "B01K2JUMJQ",
    "melatonin": "B005DEK990",
    "testosterone booster": "B07DWR9BNJ",
    "test booster": "B07DWR9BNJ",
    "tongkat ali": "B084GJJT3N",
    "electrolyte": "B01IT9NLHW",
    "electrolyte powder": "B01IT9NLHW",
    "electrolytes": "B01IT9NLHW",

    # Equipment
    "resistance bands": "B01AVDVHTI",
    "resistance band": "B01AVDVHTI",
    "resistance bands set": "B01AVDVHTI",
    "adjustable dumbbells": "B001ARYU58",
    "adjustable dumbbell": "B001ARYU58",
    "bowflex dumbbells": "B001ARYU58",
    "bowflex selecttech": "B001ARYU58",
    "pull up bar": "B001EJMS6K",
    "pullup bar": "B001EJMS6K",
    "doorway pull up bar": "B001EJMS6K",
    "foam roller": "B0040EKZDY",
    "yoga mat": "B01LYBOA9L",
    "exercise mat": "B01LYBOA9L",
    "kettlebell": "B003J9E5WO",
    "massage gun": "B07MHBJYRH",
    "percussion massager": "B07MHBJYRH",
    "theragun": "B07MHBJYRH",
    "workout gloves": "B01MQGF4TQ",
    "lifting gloves": "B01MQGF4TQ",
    "weight bench": "B07DNHHNNN",
    "adjustable weight bench": "B07DNHHNNN",
    "workout bench": "B07DNHHNNN",
    "barbell": "B001K4OPY2",
    "olympic barbell": "B001K4OPY2",
    "power rack": "B01NBFIIIA",
    "squat rack": "B01NBFIIIA",
    "home gym rack": "B01NBFIIIA",
    "ab roller": "B010FN6I2C",
    "ab wheel": "B010FN6I2C",
    "jump rope": "B01ID497GU",
    "speed rope": "B01ID497GU",
    "agility ladder": "B00TXF7B5A",
    "weight plates": "B074DZ9GHM",
    "olympic weight plates": "B074DZ9GHM",
    "dip station": "B002Y2SUU4",
    "dip bars": "B002Y2SUU4",
    "gym bag": "B08CXC5W36",
    "workout bag": "B08CXC5W36",
    "lifting belt": "B019SSHDSW",
    "weightlifting belt": "B019SSHDSW",
    "lifting straps": "B00NQ1353K",
    "wrist straps": "B00NQ1353K",
    "wrist wraps": "B01N3RWL6B",
    "knee sleeves": "B019NSMQ9E",
    "knee sleeve": "B019NSMQ9E",
    "weighted vest": "B078Z3SRNG",
    "weight vest": "B078Z3SRNG",
    "battle ropes": "B00KFXIBXW",
    "battle rope": "B00KFXIBXW",
    "suspension trainer": "B002YIA5QE",
    "trx": "B002YIA5QE",
    "trx suspension": "B002YIA5QE",
    "stability ball": "B0074TWTMU",
    "exercise ball": "B0074TWTMU",
    "swiss ball": "B0074TWTMU",
    "hand gripper": "B07B1D47FB",
    "grip strengthener": "B07B1D47FB",
    "hand grip": "B07B1D47FB",
    "parallettes": "B07BRDZ2WY",
    "parallette bars": "B07BRDZ2WY",
    "push up handles": "B001QCZQCM",
    "pushup handles": "B001QCZQCM",
    "hex dumbbells": "B074DZ9GHM",
    "rubber hex dumbbells": "B074DZ9GHM",
    "dumbbell set": "B074DZ9GHM",

    # Nutrition & Kitchen
    "food scale": "B004164SRA",
    "kitchen scale": "B004164SRA",
    "meal prep containers": "B078RFVKNR",
    "meal prep container": "B078RFVKNR",
    "glass meal prep": "B078RFVKNR",
    "protein shaker": "B01LZ2GH5O",
    "shaker bottle": "B01LZ2GH5O",
    "blender bottle": "B01LZ2GH5O",
    "stretching strap": "B07YQ2BX91",
    "yoga strap": "B07YQ2BX91",

    # Recovery
    "lacrosse ball": "B06XK3DLVQ",
    "massage ball": "B06XK3DLVQ",
    "ice pack": "B01N926DGN",
    "compression sleeves": "B019NSMQ9E",
    "compression sleeve": "B019NSMQ9E",

    # Trackers & Tech
    "fitness tracker": "B0B5F5SG6P",
    "activity tracker": "B0B5F5SG6P",
    "apple watch": "B0CHX7C7WH",
    "garmin watch": "B09YVYW5QQ",
    "garmin fitness": "B09YVYW5QQ",
    "whoop band": "B09LVYY15K",
    "whoop": "B09LVYY15K",
    "heart rate monitor": "B0B5F5SG6P",
    "smart watch": "B0B5F5SG6P",
    "smartwatch": "B0B5F5SG6P",
    "body fat scale": "B09CL72LN7",
    "smart scale": "B09CL72LN7",
    "bathroom scale": "B09CL72LN7",
}

CORRECT_TAG = "fitover3509-20"

def normalize_query(query):
    """Normalize a search query for matching."""
    return query.lower().strip().replace("+", " ").replace("%20", " ").replace("-", " ")

def find_asin(search_query):
    """Try to find an ASIN for a search query using fuzzy matching."""
    normalized = normalize_query(search_query)

    # Direct match
    if normalized in ASIN_MAP:
        return ASIN_MAP[normalized]

    # Substring matching - try to find if any key is contained in the query
    for key, asin in ASIN_MAP.items():
        if key in normalized or normalized in key:
            return asin

    # Word matching - check if query contains key words
    query_words = set(normalized.split())
    for key, asin in ASIN_MAP.items():
        key_words = set(key.split())
        # If most key words are in the query, it's a match
        if len(key_words) > 0 and len(query_words.intersection(key_words)) >= len(key_words) * 0.7:
            return asin

    return None

def extract_search_urls(html_content):
    """Extract all Amazon search URLs from HTML content."""
    # Pattern matches both regular and HTML-encoded URLs
    pattern = r'https?://www\.amazon\.com/s\?k=([^"&\s]+)(?:&tag=[^"&\s]+)?'
    matches = re.findall(pattern, html_content)
    return [unquote(m) for m in matches]

def replace_amazon_urls(html_content):
    """Replace Amazon search URLs with direct product URLs where possible."""
    replacements = []

    # Find all Amazon URLs (search and direct)
    pattern = r'(https?://www\.amazon\.com/s\?k=([^"&\s]+)(?:&tag=([^"&\s]+))?)'

    def replace_url(match):
        full_url = match.group(1)
        search_query = unquote(match.group(2))
        existing_tag = match.group(3) if match.group(3) else None

        # Try to find ASIN
        asin = find_asin(search_query)

        if asin:
            # Replace with direct URL
            new_url = f'https://www.amazon.com/dp/{asin}?tag={CORRECT_TAG}'
            replacements.append({
                'type': 'direct',
                'query': search_query,
                'asin': asin,
                'old': full_url,
                'new': new_url
            })
            return new_url
        else:
            # Keep as search URL but ensure correct tag
            cleaned_query = quote_plus(search_query.lower().strip())
            new_url = f'https://www.amazon.com/s?k={cleaned_query}&tag={CORRECT_TAG}'
            replacements.append({
                'type': 'search',
                'query': search_query,
                'old': full_url,
                'new': new_url
            })
            return new_url

    new_content = re.sub(pattern, replace_url, html_content)
    return new_content, replacements

def process_article(file_path):
    """Process a single article file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content, replacements = replace_amazon_urls(content)

    if replacements:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return replacements

def main():
    # Get script directory and construct path relative to it
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    articles_dir = project_root / 'outputs' / 'fitover35-website' / 'articles'

    if not articles_dir.exists():
        print(f"Error: Directory not found: {articles_dir}")
        return

    html_files = list(articles_dir.glob('*.html'))
    print(f"Found {len(html_files)} HTML files to process\n")

    total_direct = 0
    total_search = 0
    all_replacements = []

    for file_path in html_files:
        replacements = process_article(file_path)
        if replacements:
            direct_count = sum(1 for r in replacements if r['type'] == 'direct')
            search_count = sum(1 for r in replacements if r['type'] == 'search')
            total_direct += direct_count
            total_search += search_count
            all_replacements.extend(replacements)

            if replacements:
                print(f"[OK] {file_path.name}: {direct_count} direct URLs, {search_count} search URLs")

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total files processed: {len(html_files)}")
    print(f"Search URLs replaced with DIRECT URLs: {total_direct}")
    print(f"Search URLs kept (cleaned): {total_search}")
    print(f"\n[OK] All links now use correct affiliate tag: {CORRECT_TAG}")

    # Show unique direct product conversions
    unique_direct = {}
    for r in all_replacements:
        if r['type'] == 'direct' and r['query'] not in unique_direct:
            unique_direct[r['query']] = r['asin']

    if unique_direct:
        print(f"\nDirect product conversions ({len(unique_direct)} unique):")
        for query, asin in sorted(unique_direct.items())[:10]:
            print(f"  - {query} -> {asin}")
        if len(unique_direct) > 10:
            print(f"  ... and {len(unique_direct) - 10} more")

if __name__ == "__main__":
    main()
