"""
Keyword selector for Daily Deal Darling SEO article generation.

Selects low-competition, long-tail keywords targeting budget-conscious
women 25-45 interested in deals, beauty, home, and lifestyle products.
Tracks which keywords have already been used to avoid duplicates.
"""

import os
import json
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Seed keywords - low competition, informational + buyer intent phrases
# Format: (keyword, category, estimated_difficulty)
SEED_KEYWORDS = [
    # === SKINCARE ===
    ("best drugstore moisturizers for dry skin", "skincare", "low"),
    ("vitamin c serum amazon favorites", "skincare", "low"),
    ("best retinol products under 30 dollars", "skincare", "low"),
    ("korean skincare products amazon bestsellers", "skincare", "low"),
    ("best sunscreen for daily wear", "skincare", "low"),
    ("affordable anti aging skincare routine", "skincare", "low"),
    ("niacinamide serums that actually work", "skincare", "low"),
    ("best hyaluronic acid products on amazon", "skincare", "low"),
    ("skincare dupes for expensive brands", "skincare", "low"),
    ("best eye cream for dark circles under 25", "skincare", "low"),
    ("amazon skincare finds tiktok made me buy", "skincare", "low"),
    ("best face wash for combination skin", "skincare", "low"),
    ("affordable exfoliators for glowing skin", "skincare", "low"),
    ("best body lotion for soft skin all day", "skincare", "low"),
    ("lip care products for dry cracked lips", "skincare", "low"),
    ("best face masks on amazon under 20", "skincare", "low"),
    ("acne fighting products that work fast", "skincare", "low"),
    ("best toners for large pores", "skincare", "low"),
    ("overnight skincare products for busy women", "skincare", "low"),
    ("best cleansing balms on amazon", "skincare", "low"),

    # === KITCHEN ===
    ("best air fryer accessories worth buying", "kitchen", "low"),
    ("kitchen gadgets under 25 that save time", "kitchen", "low"),
    ("best meal prep containers on amazon", "kitchen", "low"),
    ("organization bins for pantry amazon finds", "kitchen", "low"),
    ("best blender for smoothies under 100", "kitchen", "low"),
    ("coffee maker accessories you need", "kitchen", "low"),
    ("best cutting boards for home cooks", "kitchen", "low"),
    ("kitchen tools every home cook needs", "kitchen", "low"),
    ("best non stick pan set on amazon", "kitchen", "low"),
    ("knife sharpener that actually works", "kitchen", "low"),
    ("space saving kitchen gadgets for small kitchens", "kitchen", "low"),
    ("best instant pot accessories", "kitchen", "low"),
    ("silicone baking mats worth buying", "kitchen", "low"),
    ("best food storage containers glass vs plastic", "kitchen", "low"),
    ("amazon kitchen finds under 15 dollars", "kitchen", "low"),

    # === HOME ORGANIZATION ===
    ("closet organization ideas on a budget", "organization", "low"),
    ("best storage bins for closet organization", "organization", "low"),
    ("drawer organizers that transform your space", "organization", "low"),
    ("bathroom organization products amazon", "organization", "low"),
    ("pantry organization ideas and products", "organization", "low"),
    ("under sink organizers that maximize space", "organization", "low"),
    ("best hangers for small closets", "organization", "low"),
    ("desk organization products for work from home", "organization", "low"),
    ("laundry room organization on a budget", "organization", "low"),
    ("garage organization ideas amazon finds", "organization", "low"),
    ("shoe storage solutions for small spaces", "organization", "low"),
    ("jewelry organizers that look aesthetic", "organization", "low"),
    ("medicine cabinet organization products", "organization", "low"),
    ("kids room organization ideas and bins", "organization", "low"),
    ("entryway organization products for families", "organization", "low"),

    # === BEAUTY ===
    ("best drugstore makeup dupes for high end", "beauty", "low"),
    ("makeup brushes worth buying on amazon", "beauty", "low"),
    ("best mascara on amazon under 15", "beauty", "low"),
    ("lip products that last all day", "beauty", "low"),
    ("best setting spray for oily skin", "beauty", "low"),
    ("eyeshadow palettes under 20 amazon", "beauty", "low"),
    ("best concealer for dark under eyes", "beauty", "low"),
    ("foundation for mature skin drugstore", "beauty", "low"),
    ("makeup sponges and tools worth buying", "beauty", "low"),
    ("best bronzer for natural glow", "beauty", "low"),
    ("lip liner that doesnt smudge", "beauty", "low"),
    ("brow products for natural looking brows", "beauty", "low"),
    ("best blush for long lasting color", "beauty", "low"),
    ("primer for smooth makeup application", "beauty", "low"),
    ("makeup organizers for vanity setup", "beauty", "low"),

    # === TECH ===
    ("best portable charger for travel", "tech", "low"),
    ("wireless earbuds under 50 that sound great", "tech", "low"),
    ("phone accessories you didnt know you needed", "tech", "low"),
    ("best ring light for video calls", "tech", "low"),
    ("laptop accessories for working from home", "tech", "low"),
    ("phone stand for desk that looks nice", "tech", "low"),
    ("cable organizers for clean desk setup", "tech", "low"),
    ("best tablet stand for kitchen recipes", "tech", "low"),
    ("smart home devices worth buying", "tech", "low"),
    ("travel tech accessories for your next trip", "tech", "low"),
    ("best bluetooth speaker under 30", "tech", "low"),
    ("webcam for zoom calls that looks professional", "tech", "low"),
    ("keyboard and mouse for home office", "tech", "low"),
    ("apple watch bands amazon favorites", "tech", "low"),
    ("iphone accessories from amazon", "tech", "low"),

    # === WELLNESS ===
    ("best massage gun under 100", "wellness", "low"),
    ("sleep products for better rest", "wellness", "low"),
    ("weighted blanket worth buying amazon", "wellness", "low"),
    ("essential oil diffuser amazon favorites", "wellness", "low"),
    ("yoga mat accessories for home practice", "wellness", "low"),
    ("relaxation products for stress relief", "wellness", "low"),
    ("best water bottle to stay hydrated", "wellness", "low"),
    ("foam roller for muscle recovery", "wellness", "low"),
    ("posture corrector that actually works", "wellness", "low"),
    ("blue light glasses for screen time", "wellness", "low"),

    # === BUDGET FINDS ===
    ("amazon finds under 10 dollars", "budget", "low"),
    ("best amazon products under 25", "budget", "low"),
    ("tiktok amazon finds that are worth it", "budget", "low"),
    ("amazon dupes for expensive products", "budget", "low"),
    ("hidden gems on amazon you need", "budget", "low"),
    ("amazon products that look expensive", "budget", "low"),
    ("viral amazon products worth buying", "budget", "low"),
    ("amazon finds that changed my life", "budget", "low"),
    ("impulse amazon buys that were worth it", "budget", "low"),
    ("amazon finds for apartment living", "budget", "low"),
    ("amazon products with best reviews", "budget", "low"),
    ("best rated amazon products under 20", "budget", "low"),
    ("amazon finds for college students", "budget", "low"),
    ("amazon finds for first apartment", "budget", "low"),
    ("amazon products that solve problems", "budget", "low"),

    # === SEASONAL ===
    ("best valentines day gifts from amazon", "seasonal", "low"),
    ("mothers day gift ideas under 50", "seasonal", "low"),
    ("back to school supplies amazon", "seasonal", "low"),
    ("summer essentials from amazon", "seasonal", "low"),
    ("holiday gift guide amazon finds", "seasonal", "low"),
    ("fall home decor amazon favorites", "seasonal", "low"),
    ("spring cleaning products worth buying", "seasonal", "low"),
    ("new year organization products", "seasonal", "low"),
    ("gifts for her under 25 amazon", "seasonal", "low"),
    ("cozy winter products amazon finds", "seasonal", "low"),

    # === HAIR CARE ===
    ("best hair tools on amazon under 50", "haircare", "low"),
    ("hair products for damaged hair repair", "haircare", "low"),
    ("best shampoo and conditioner duos", "haircare", "low"),
    ("hair accessories that look expensive", "haircare", "low"),
    ("heat protectant sprays that work", "haircare", "low"),
    ("best hair masks for deep conditioning", "haircare", "low"),
    ("curling iron and wand amazon favorites", "haircare", "low"),
    ("dry shampoo that actually works", "haircare", "low"),
    ("hair growth products amazon bestsellers", "haircare", "low"),
    ("best detangling brush for all hair types", "haircare", "low"),
]


def load_used_keywords(state_file: str = "dailydealdarling_keyword_state.json") -> set:
    """Load keywords that have already been used."""
    state_path = Path(state_file)
    if state_path.exists():
        data = json.loads(state_path.read_text())
        return set(data.get('used_keywords', []))
    return set()


def save_used_keyword(keyword: str, state_file: str = "dailydealdarling_keyword_state.json"):
    """Mark a keyword as used."""
    state_path = Path(state_file)

    if state_path.exists():
        data = json.loads(state_path.read_text())
    else:
        data = {'used_keywords': [], 'last_updated': None}

    if keyword not in data['used_keywords']:
        data['used_keywords'].append(keyword)
        data['last_updated'] = datetime.utcnow().isoformat()

    state_path.write_text(json.dumps(data, indent=2))


def select_keyword(
    category: Optional[str] = None,
    difficulty: str = "low",
    state_file: str = "dailydealdarling_keyword_state.json"
) -> Optional[dict]:
    """
    Select a keyword for article generation.

    Args:
        category: Optional category filter (skincare, kitchen, organization,
                  beauty, tech, wellness, budget, seasonal, haircare)
        difficulty: Preferred difficulty level ("low", "medium")
        state_file: Path to state file tracking used keywords

    Returns:
        Dict with keyword info or None if all used
    """
    used = load_used_keywords(state_file)

    # Filter available keywords
    available = [
        kw for kw in SEED_KEYWORDS
        if kw[0] not in used
        and (category is None or kw[1] == category)
        and kw[2] == difficulty
    ]

    # If no low difficulty available, try medium
    if not available and difficulty == "low":
        available = [
            kw for kw in SEED_KEYWORDS
            if kw[0] not in used
            and (category is None or kw[1] == category)
        ]

    # If specific category exhausted, try any category
    if not available and category is not None:
        available = [
            kw for kw in SEED_KEYWORDS
            if kw[0] not in used
        ]

    if not available:
        logger.warning("All keywords have been used! Resetting state.")
        # Reset and try again
        Path(state_file).unlink(missing_ok=True)
        available = list(SEED_KEYWORDS)

    # Random selection for variety
    selected = random.choice(available)

    return {
        'keyword': selected[0],
        'category': selected[1],
        'difficulty': selected[2],
        'slug': generate_slug(selected[0]),
    }


def generate_slug(keyword: str) -> str:
    """Generate a URL-friendly slug from a keyword."""
    slug = keyword.lower().replace(' ', '-').replace('?', '').replace("'", '')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    # Remove consecutive hyphens
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug[:60].rstrip('-')


def generate_article_filename(keyword_info: dict) -> str:
    """Generate a filename for the article."""
    return f"{keyword_info['slug']}.html"


def get_stats(state_file: str = "dailydealdarling_keyword_state.json") -> dict:
    """Get keyword usage statistics."""
    used = load_used_keywords(state_file)
    total = len(SEED_KEYWORDS)
    used_count = len(used)

    categories = {}
    for kw in SEED_KEYWORDS:
        cat = kw[1]
        if cat not in categories:
            categories[cat] = {'total': 0, 'used': 0}
        categories[cat]['total'] += 1
        if kw[0] in used:
            categories[cat]['used'] += 1

    return {
        'total_keywords': total,
        'used_keywords': used_count,
        'remaining_keywords': total - used_count,
        'categories': categories,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Select keyword for Daily Deal Darling article')
    parser.add_argument(
        '--category',
        choices=[
            'skincare', 'kitchen', 'organization', 'beauty',
            'tech', 'wellness', 'budget', 'seasonal', 'haircare'
        ],
        help='Filter by category'
    )
    parser.add_argument(
        '--mark-used',
        action='store_true',
        help='Mark the selected keyword as used'
    )
    parser.add_argument(
        '--list-used',
        action='store_true',
        help='List all used keywords'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show keyword usage statistics'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset used keywords state'
    )
    parser.add_argument(
        '--state-file',
        default='dailydealdarling_keyword_state.json',
        help='Path to keyword state file'
    )

    args = parser.parse_args()

    state_file = args.state_file

    if args.reset:
        Path(state_file).unlink(missing_ok=True)
        print("Reset keyword state")
        return 0

    if args.list_used:
        used = load_used_keywords(state_file)
        print(f"Used keywords ({len(used)}):")
        for kw in sorted(used):
            print(f"  - {kw}")
        return 0

    if args.stats:
        stats = get_stats(state_file)
        print(f"Total keywords: {stats['total_keywords']}")
        print(f"Used: {stats['used_keywords']}")
        print(f"Remaining: {stats['remaining_keywords']}")
        print(f"\nBy category:")
        for cat, info in sorted(stats['categories'].items()):
            print(f"  {cat}: {info['used']}/{info['total']} used")
        return 0

    # Select keyword
    keyword_info = select_keyword(
        category=args.category,
        state_file=state_file
    )

    if not keyword_info:
        print("No available keywords!")
        return 1

    print(f"Selected keyword: {keyword_info['keyword']}")
    print(f"Category: {keyword_info['category']}")
    print(f"Difficulty: {keyword_info['difficulty']}")
    print(f"Filename: {generate_article_filename(keyword_info)}")

    if args.mark_used:
        save_used_keyword(keyword_info['keyword'], state_file)
        print("Marked as used")

    # Output for GitHub Actions
    github_output = os.environ.get('GITHUB_OUTPUT', '')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"keyword={keyword_info['keyword']}\n")
            f.write(f"category={keyword_info['category']}\n")
            f.write(f"filename={generate_article_filename(keyword_info)}\n")
            f.write(f"slug={keyword_info['slug']}\n")
    else:
        # Fallback for local testing
        print(f"\nkeyword={keyword_info['keyword']}")
        print(f"category={keyword_info['category']}")
        print(f"filename={generate_article_filename(keyword_info)}")
        print(f"slug={keyword_info['slug']}")

    return 0


if __name__ == "__main__":
    exit(main())
