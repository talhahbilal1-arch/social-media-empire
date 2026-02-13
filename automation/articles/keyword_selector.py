"""
Keyword selector for SEO article generation.

Selects low-competition, buyer-intent keywords for daily article generation.
Tracks which keywords have already been used to avoid duplicates.
"""

import os
import json
import random
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Seed keywords - low competition, buyer intent phrases
# Format: (keyword, category, estimated_difficulty)
SEED_KEYWORDS = [
    # Skincare
    ("best moisturizer for dry skin 2026", "skincare", "low"),
    ("affordable anti aging skincare routine", "skincare", "low"),
    ("best vitamin c serum under 30", "skincare", "low"),
    ("korean skincare products worth buying", "skincare", "medium"),
    ("best sunscreen for oily skin drugstore", "skincare", "low"),
    ("niacinamide vs hyaluronic acid which is better", "skincare", "low"),
    ("best retinol for beginners sensitive skin", "skincare", "low"),
    ("how to layer skincare products correctly", "skincare", "low"),

    # Kitchen
    ("best air fryer under 100 dollars", "kitchen", "medium"),
    ("instant pot vs air fryer which should i buy", "kitchen", "low"),
    ("best non stick pan that actually lasts", "kitchen", "low"),
    ("kitchen gadgets that save time", "kitchen", "low"),
    ("best blender for smoothies under 50", "kitchen", "low"),
    ("is ninja blender worth it review", "kitchen", "low"),
    ("best knife set for home cooks", "kitchen", "medium"),
    ("meal prep containers that dont leak", "kitchen", "low"),

    # Home Organization
    ("best closet organizers for small spaces", "organization", "low"),
    ("how to organize kitchen cabinets cheap", "organization", "low"),
    ("best storage bins for clothes", "organization", "low"),
    ("pantry organization ideas that work", "organization", "low"),
    ("desk organization products for work from home", "organization", "low"),
    ("bathroom storage ideas small space", "organization", "low"),
    ("garage organization on a budget", "organization", "low"),
    ("best drawer organizers kitchen", "organization", "low"),

    # Fitness
    ("best yoga mat for beginners thick", "fitness", "low"),
    ("home gym equipment under 200", "fitness", "low"),
    ("resistance bands vs weights which is better", "fitness", "low"),
    ("best running shoes for beginners wide feet", "fitness", "low"),
    ("foam roller benefits and how to use", "fitness", "low"),
    ("best workout equipment for small apartments", "fitness", "low"),
    ("fitness tracker vs smartwatch which to buy", "fitness", "medium"),
    ("best jump rope for beginners weighted", "fitness", "low"),

    # Self Care
    ("best massage gun under 100", "wellness", "medium"),
    ("relaxation gifts for stressed mom", "wellness", "low"),
    ("best essential oil diffuser for sleep", "wellness", "low"),
    ("weighted blanket worth it review", "wellness", "low"),
    ("best journal for mental health", "wellness", "low"),
    ("sleep products that actually work", "wellness", "low"),
    ("self care products under 25 dollars", "wellness", "low"),
    ("best bath bombs that dont stain tub", "wellness", "low"),

    # Tech Accessories
    ("best portable charger for travel", "tech", "medium"),
    ("wireless earbuds under 50 worth buying", "tech", "low"),
    ("best phone stand for desk adjustable", "tech", "low"),
    ("laptop accessories for work from home", "tech", "low"),
    ("best cable organizer for desk", "tech", "low"),
    ("ring light for video calls worth it", "tech", "low"),
    ("best keyboard for typing all day", "tech", "medium"),
    ("usb hub recommendations 2026", "tech", "low"),

    # Budget Finds
    ("amazon products under 10 dollars worth buying", "budget", "medium"),
    ("best amazon finds under 25", "budget", "medium"),
    ("cheap products that look expensive", "budget", "low"),
    ("amazon hidden gems 2026", "budget", "low"),
    ("best value products on amazon", "budget", "low"),
    ("dupes for expensive products amazon", "budget", "low"),
    ("tiktok amazon finds that work", "budget", "medium"),
    ("most useful amazon products 2026", "budget", "low"),
]


def load_used_keywords(state_file: str = "keyword_state.json") -> set:
    """Load keywords that have already been used."""
    state_path = Path(state_file)
    if state_path.exists():
        data = json.loads(state_path.read_text())
        return set(data.get('used_keywords', []))
    return set()


def save_used_keyword(keyword: str, state_file: str = "keyword_state.json"):
    """Mark a keyword as used."""
    state_path = Path(state_file)

    if state_path.exists():
        data = json.loads(state_path.read_text())
    else:
        data = {'used_keywords': [], 'last_updated': None}

    if keyword not in data['used_keywords']:
        data['used_keywords'].append(keyword)
        data['last_updated'] = datetime.now(timezone.utc).isoformat()

    state_path.write_text(json.dumps(data, indent=2))


def select_keyword(
    category: Optional[str] = None,
    difficulty: str = "low",
    state_file: str = "keyword_state.json"
) -> Optional[dict]:
    """
    Select a keyword for article generation.

    Args:
        category: Optional category filter
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

    if not available:
        logger.warning("All keywords have been used!")
        return None

    # Random selection for variety
    selected = random.choice(available)

    return {
        'keyword': selected[0],
        'category': selected[1],
        'difficulty': selected[2],
        'slug': selected[0].lower().replace(' ', '-').replace('?', ''),
    }


def generate_article_filename(keyword_info: dict) -> str:
    """Generate a filename for the article."""
    slug = keyword_info['slug']
    # Remove special characters and limit length
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    slug = slug[:50]  # Max length
    return f"{slug}.html"


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Select keyword for article')
    parser.add_argument(
        '--category',
        choices=['skincare', 'kitchen', 'organization', 'fitness', 'wellness', 'tech', 'budget'],
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
        '--reset',
        action='store_true',
        help='Reset used keywords state'
    )

    args = parser.parse_args()

    state_file = "keyword_state.json"

    if args.reset:
        Path(state_file).unlink(missing_ok=True)
        print("Reset keyword state")
        return 0

    if args.list_used:
        used = load_used_keywords(state_file)
        print(f"Used keywords ({len(used)}):")
        for kw in used:
            print(f"  - {kw}")
        return 0

    # Select keyword
    keyword_info = select_keyword(category=args.category, state_file=state_file)

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
    print(f"\n::set-output name=keyword::{keyword_info['keyword']}")
    print(f"::set-output name=category::{keyword_info['category']}")
    print(f"::set-output name=filename::{generate_article_filename(keyword_info)}")

    return 0


if __name__ == "__main__":
    exit(main())
