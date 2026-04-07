#!/usr/bin/env python3
"""
Replace Amazon search URLs with direct product links in Daily Deal Darling articles.
Uses fuzzy matching to map search queries to ASINs.
"""

import re
import urllib.parse
from pathlib import Path
from difflib import get_close_matches

# Comprehensive ASIN dictionary for home/kitchen/beauty/deals products
ASIN_MAP = {
    # Kitchen - Air Fryers & Appliances
    "air fryer": "B07FDJMC9Q",
    "ninja air fryer": "B07FDJMC9Q",
    "instant pot": "B00FLYWNYQ",
    "coffee maker": "B083LNYLNJ",
    "electric kettle": "B07TZ5YHJN",
    "toaster": "B00CQLJEOC",
    "rice cooker": "B007WQ9YNO",
    "slow cooker": "B004P2NG0K",
    "blender": "B00VKUWMMG",
    "portable blender": "B07KJGP5KP",
    "food processor": "B01AXM4WOO",
    "stand mixer": "B00LEAWBQO",
    "ice cream maker": "B003KYSLMW",
    "waffle maker": "B00QHDR5L2",

    # Kitchen - Knives & Cutting
    "knife set": "B07TLZXRK2",
    "kitchen knife": "B07TLZXRK2",
    "chef knife": "B000IBVB8E",
    "cutting board": "B01J9AOF1G",
    "bamboo cutting board": "B01J9AOF1G",
    "plastic cutting board": "B07P3C2CP6",

    # Kitchen - Cookware
    "cast iron skillet": "B00006JSUA",
    "nonstick pan": "B00OEFBPIC",
    "dutch oven": "B000N501BK",
    "baking sheet": "B00BPXKFKM",

    # Kitchen - Tools & Utensils
    "mixing bowls": "B01L1UN7XO",
    "measuring cups": "B074XTSVJ7",
    "silicone spatula": "B07RLVHP5T",
    "silicone utensil set": "B091CFKWZJ",
    "cooking utensil set": "B091CFKWZJ",
    "microplane grater": "B00004S7V8",
    "thermometer": "B01IHHLB3W",
    "digital thermometer": "B01IHHLB3W",
    "can opener": "B001C2S0NO",
    "colander": "B002L6RTQK",
    "whisk": "B00GZI7VVG",
    "tongs": "B07MCLVV52",
    "avocado slicer": "B0088LR592",
    "vegetable chopper": "B0764HS4SL",

    # Kitchen - Storage & Organization
    "storage containers": "B0018AJFPY",
    "food storage containers": "B0018AJFPY",
    "glass food storage": "B078RFVKNR",
    "airtight containers": "B0018AJFPY",
    "drawer dividers": "B073VB74FJ",
    "bamboo drawer dividers": "B073VB74FJ",
    "drawer organizers": "B073VB74FJ",
    "spice rack": "B071LSRDJ6",
    "lazy susan": "B07WNRVMPH",
    "utensil holder": "B08R9QJRKL",

    # Home Organization
    "organizer bins": "B07DFDS56B",
    "storage bins": "B07DFDS56B",
    "stackable bins": "B07DFDS56B",
    "clear storage bins": "B07DFDS56B",
    "label maker": "B0719RFLTQ",
    "closet organizer": "B07N4KFMHZ",
    "shoe rack": "B079DJZTJH",
    "shoe organizer": "B079DJZTJH",
    "shelf organizer": "B07DFDS56B",
    "vacuum storage bags": "B07B6LGWJR",
    "hangers": "B0796P2FNM",
    "laundry basket": "B07YVHQSC2",
    "hamper": "B07YVHQSC2",
    "trash can": "B00BEXXVKE",
    "command hooks": "B00I62F5JW",
    "tension rod": "B001B1EJ08",
    "magazine holder": "B071LSRDJ6",
    "desk organizer": "B078HNYQWN",
    "cable organizer": "B06XNPGT71",
    "storage baskets": "B07DFDS56B",
    "under bed storage": "B07YVHQSC2",
    "garage hooks": "B07P6ZMBYX",

    # Beauty/Skincare
    "silk pillowcase": "B07P3SQCV3",
    "satin pillowcase": "B07P3SQCV3",
    "led face mask": "B07D3KVL4Z",
    "face roller": "B07WRFQ1Q5",
    "jade roller": "B07WRFQ1Q5",
    "gua sha": "B082FJSSV6",
    "retinol serum": "B01MSSDEPK",
    "vitamin c serum": "B01M4MCUAF",
    "hyaluronic acid": "B004FWZAAM",
    "sunscreen": "B00X1FWFG0",
    "moisturizer": "B00WJ3O9CQ",
    "face wash": "B003YMJJSK",
    "makeup organizer": "B01LYFSAEJ",
    "hair dryer": "B084DB3F9Z",
    "curling iron": "B00GQRK0M4",
    "hot air brush": "B01LSUQSB0",
    "flat iron": "B00BQIVONY",
    "hair brush": "B084LV2PPJ",
    "nail kit": "B07GQ3ZCLW",
    "dry shampoo": "B0B94CSHXZ",
    "face masks": "B08P414JH5",
    "setting spray": "B00TQZKFAE",

    # Home Decor
    "throw pillows": "B08RDSBWTK",
    "pillow covers": "B08RDSBWTK",
    "led candles": "B07P3SQCV3",
    "scented candles": "B079SCMFDC",
    "fairy lights": "B07BKY4XL2",
    "string lights": "B07BKY4XL2",
    "wall art": "B07SXHYV33",
    "area rug": "B076J4QSGY",
    "curtains": "B0725T8FD5",
    "throw blanket": "B0BYK2N6S3",
    "faux fur blanket": "B0BYK2N6S3",
    "picture frames": "B0177MTJLE",
    "diffuser": "B07L4R62GQ",
    "essential oils": "B07L4R62GQ",
    "plant pot": "B07BHJ5DQH",
    "planter": "B07BHJ5DQH",
    "door mat": "B07SXR8L2R",
    "mirror": "B0B5XPXPNW",
    "floating frames": "B0177MTJLE",
    "succulents": "B07QJCQD3R",
    "accent chair": "B07RDVFDK3",

    # Cleaning
    "robot vacuum": "B08G4V2J5D",
    "roomba": "B08G4V2J5D",
    "cordless vacuum": "B07FSFG1QQ",
    "steam mop": "B079ZQQP4M",
    "microfiber cloths": "B009FUF6DM",
    "cleaning supplies": "B09FGSKGBM",
    "laundry detergent": "B00J4S0PVQ",
    "dryer balls": "B00GA9P5OC",
    "dish brush": "B00004OCLJ",
    "bar keepers friend": "B000V72992",
    "degreaser": "B07MFWFXFD",

    # Tech/Gadgets
    "smart plug": "B07XJ8C8F5",
    "echo dot": "B09B8V1LZ3",
    "ring doorbell": "B08N5NQ69J",
    "fire stick": "B0C3M73TRS",
    "power bank": "B07QXV6N1B",
    "portable charger": "B07QXV6N1B",
    "wireless charger": "B07THHQMHM",
    "bluetooth speaker": "B01MTB55WH",
    "phone stand": "B07F8S18D5",
    "airtag": "B0933BVK6T",
    "led desk lamp": "B06XYDNQ68",
    "under cabinet lighting": "B07L4R62GQ",

    # Water Bottles & Tumblers
    "water bottle": "B09MKVLHZM",
    "hydro flask": "B084KJWNJK",
    "stanley tumbler": "B0BQY3KJ9D",
    "iron flask": "B079F73N7R",
    "tumbler": "B07YBT7BT7",

    # Bathroom
    "shower caddy": "B07HSCGBK2",
    "bathroom organizer": "B07DFDS56B",
    "over toilet storage": "B07HSCGBK2",
    "vanity tray": "B078HNYQWN",

    # Bedroom
    "bamboo sheets": "B089HHB9LR",
    "white noise machine": "B00E6D6LQY",
    "blackout curtains": "B0725T8FD5",

    # Misc
    "calendar": "B08L7VL8KR",
    "journal": "B082MYV7PB",
    "planner": "B082MYV7PB",
    "monitor stand": "B07DWM9WNM",
    "desk": "B082RQ9X3G",
    "board games": "B00000DMBD",
    "peel stick tile": "B07NQRKN95",
    "contact paper": "B07NQRKN95",
    "coasters": "B07CXVY6GG",
    "necklace": "B08R9QJRKL",
}

# Create normalized key map for faster fuzzy matching
NORMALIZED_KEYS = {key.lower().strip(): asin for key, asin in ASIN_MAP.items()}

def normalize_query(query: str) -> str:
    """Normalize search query for matching."""
    # Decode URL encoding
    query = urllib.parse.unquote_plus(query)
    # Remove common filler words
    filler_words = ['the', 'best', 'top', 'amazon', 'under', 'worth', 'buying',
                   'actually', 'that', 'and', 'or', 'for', 'with', 'from',
                   'rated', 'review', 'reviews', 'guide', 'comparison']
    words = query.lower().split()
    words = [w for w in words if w not in filler_words and not w.isdigit()]
    return ' '.join(words)

def find_asin(query: str) -> str | None:
    """Find ASIN for search query using fuzzy matching."""
    normalized = normalize_query(query)

    # Direct match
    if normalized in NORMALIZED_KEYS:
        return NORMALIZED_KEYS[normalized]

    # Try removing numbers and special chars
    clean_query = re.sub(r'[^a-z\s]', '', normalized)
    if clean_query in NORMALIZED_KEYS:
        return NORMALIZED_KEYS[clean_query]

    # Fuzzy match with high confidence threshold
    matches = get_close_matches(normalized, NORMALIZED_KEYS.keys(), n=1, cutoff=0.7)
    if matches:
        return NORMALIZED_KEYS[matches[0]]

    # Try partial matching (if query contains a known product)
    for key, asin in NORMALIZED_KEYS.items():
        if key in normalized or normalized in key:
            return asin

    return None

def process_html_file(file_path: Path) -> dict:
    """Process a single HTML file and replace Amazon search URLs."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = []
    updated_content = content

    # Find all Amazon search URLs
    pattern = r'https?://www\.amazon\.com/s\?k=([^&"]+)(?:&tag=([^"&]+))?'
    matches = re.finditer(pattern, content)

    for match in matches:
        old_url = match.group(0)
        query = match.group(1)
        existing_tag = match.group(2)

        # Decode the search query
        decoded_query = urllib.parse.unquote_plus(query)

        # Find matching ASIN
        asin = find_asin(query)

        if asin:
            # Replace with direct product link
            new_url = f"https://www.amazon.com/dp/{asin}?tag=dailydealdarl-20"
            updated_content = updated_content.replace(old_url, new_url)
            replacements.append({
                'query': decoded_query,
                'asin': asin,
                'old': old_url,
                'new': new_url
            })
        else:
            # No match found - just fix the affiliate tag if needed
            if existing_tag != 'dailydealdarl-20':
                new_url = f"https://www.amazon.com/s?k={query}&tag=dailydealdarl-20"
                updated_content = updated_content.replace(old_url, new_url)
                replacements.append({
                    'query': decoded_query,
                    'asin': None,
                    'old': old_url,
                    'new': new_url,
                    'action': 'tag_fix_only'
                })

    # Write updated content if changes were made
    if updated_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

    return {
        'file': file_path.name,
        'replacements': len(replacements),
        'details': replacements
    }

def main():
    """Process all HTML files in Daily Deal Darling articles directory."""
    articles_dir = Path(__file__).parent.parent / 'outputs' / 'dailydealdarling-website' / 'articles'

    if not articles_dir.exists():
        print(f"ERROR: Directory not found: {articles_dir}")
        return

    html_files = list(articles_dir.glob('*.html'))
    print(f"Found {len(html_files)} HTML files")
    print(f"Processing with {len(ASIN_MAP)} product ASINs...\n")

    total_replacements = 0
    total_asin_matches = 0
    files_modified = 0

    for file_path in sorted(html_files):
        result = process_html_file(file_path)

        if result['replacements'] > 0:
            files_modified += 1
            total_replacements += result['replacements']
            asin_matches = len([r for r in result['details'] if r['asin'] is not None])
            total_asin_matches += asin_matches

            print(f"OK: {result['file']}: {result['replacements']} replacements ({asin_matches} ASIN matches)")

            # Show details for ASIN matches
            for r in result['details']:
                if r['asin']:
                    print(f"   -> \"{r['query']}\" = ASIN {r['asin']}")

    print(f"\n" + "="*80)
    print(f"COMPLETE!")
    print(f"   Files modified: {files_modified}/{len(html_files)}")
    print(f"   Total replacements: {total_replacements}")
    print(f"   ASIN matches: {total_asin_matches}")
    print(f"   Tag-only fixes: {total_replacements - total_asin_matches}")
    print("="*80)

if __name__ == '__main__':
    main()
