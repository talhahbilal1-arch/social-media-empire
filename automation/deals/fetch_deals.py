"""
Fetch real Amazon deals for the website.

This script:
1. Fetches active deals from Rainforest API
2. Filters for deals with 15%+ real discounts
3. Stores deals in Supabase for HTML generation
4. Logs deal history for analytics
"""

import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from automation.amazon.rainforest_client import RainforestClient, Deal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Categories to fetch deals from
DEAL_CATEGORIES = [
    'beauty',
    'kitchen',
    'home',
    'sports',
    'electronics',
]

# Minimum discount to show as a "deal"
MIN_DISCOUNT_PERCENT = 15

# Maximum deals to display on homepage
MAX_HOMEPAGE_DEALS = 4


def fetch_deals(client: Optional[RainforestClient] = None) -> list[Deal]:
    """
    Fetch deals from multiple categories.

    Args:
        client: Optional pre-configured RainforestClient

    Returns:
        List of Deal objects sorted by discount percentage
    """
    if client is None:
        client = RainforestClient()

    all_deals = []

    for category in DEAL_CATEGORIES:
        logger.info(f"Fetching deals for category: {category}")
        try:
            deals = client.get_deals(category=category, max_results=10)
            all_deals.extend(deals)
            logger.info(f"Found {len(deals)} deals in {category}")
        except Exception as e:
            logger.error(f"Error fetching {category} deals: {e}")

    # Filter by minimum discount
    filtered_deals = [
        d for d in all_deals
        if d.discount_percentage >= MIN_DISCOUNT_PERCENT
    ]

    # Sort by discount (highest first)
    filtered_deals.sort(key=lambda x: x.discount_percentage, reverse=True)

    logger.info(f"Total deals with {MIN_DISCOUNT_PERCENT}%+ discount: {len(filtered_deals)}")

    return filtered_deals


def save_deals_locally(deals: list[Deal], output_path: str = "deals_data.json"):
    """
    Save deals to local JSON file (for GitHub Actions workflow).

    Args:
        deals: List of Deal objects
        output_path: Output file path
    """
    deals_data = {
        'fetched_at': datetime.now(timezone.utc).isoformat(),
        'count': len(deals),
        'deals': [d.to_dict() for d in deals],
    }

    Path(output_path).write_text(json.dumps(deals_data, indent=2))
    logger.info(f"Saved {len(deals)} deals to {output_path}")


def save_deals_to_supabase(deals: list[Deal]):
    """
    Save deals to Supabase database.

    Requires SUPABASE_URL and SUPABASE_KEY environment variables.
    """
    try:
        from supabase import create_client, Client

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            logger.warning("Supabase credentials not set, skipping database save")
            return

        supabase: Client = create_client(url, key)

        # Upsert deals
        for deal in deals:
            deal_dict = deal.to_dict()
            deal_dict['updated_at'] = datetime.now(timezone.utc).isoformat()

            supabase.table('deals').upsert(
                deal_dict,
                on_conflict='asin'
            ).execute()

        logger.info(f"Saved {len(deals)} deals to Supabase")

    except ImportError:
        logger.warning("Supabase client not installed, skipping database save")
    except Exception as e:
        logger.error(f"Error saving to Supabase: {e}")


def get_homepage_deals(deals: list[Deal]) -> list[Deal]:
    """
    Select the best deals for homepage display.

    Criteria:
    - Highest discount percentage
    - Diverse categories
    - Available products

    Args:
        deals: Full list of deals

    Returns:
        Top deals for homepage (up to MAX_HOMEPAGE_DEALS)
    """
    if not deals:
        return []

    # Try to get variety of categories
    selected = []
    seen_categories = set()

    # First pass: one from each category
    for deal in deals:
        # Infer category from title keywords
        title_lower = deal.title.lower()
        category = 'other'

        if any(kw in title_lower for kw in ['beauty', 'skin', 'cream', 'lip']):
            category = 'beauty'
        elif any(kw in title_lower for kw in ['kitchen', 'cook', 'chef', 'pan', 'blender']):
            category = 'kitchen'
        elif any(kw in title_lower for kw in ['fitness', 'yoga', 'workout', 'gym']):
            category = 'fitness'
        elif any(kw in title_lower for kw in ['home', 'storage', 'organiz']):
            category = 'home'
        elif any(kw in title_lower for kw in ['tech', 'charger', 'power', 'electronic']):
            category = 'tech'

        if category not in seen_categories:
            selected.append(deal)
            seen_categories.add(category)

        if len(selected) >= MAX_HOMEPAGE_DEALS:
            break

    # If we need more, fill with highest discounts
    if len(selected) < MAX_HOMEPAGE_DEALS:
        for deal in deals:
            if deal not in selected:
                selected.append(deal)
            if len(selected) >= MAX_HOMEPAGE_DEALS:
                break

    return selected[:MAX_HOMEPAGE_DEALS]


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Fetch Amazon deals')
    parser.add_argument(
        '--output',
        default='deals_data.json',
        help='Output JSON file path'
    )
    parser.add_argument(
        '--save-db',
        action='store_true',
        help='Also save to Supabase database'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Skip API calls, use mock data'
    )

    args = parser.parse_args()

    if args.dry_run:
        logger.info("DRY RUN - using mock deal data")
        mock_deals = [
            Deal(
                asin='B00NGV4506',
                title='Ninja Professional Blender 1000W',
                deal_price=59.99,
                original_price=99.99,
                discount_percentage=40.0,
                deal_type='best_deal',
                image_url='https://m.media-amazon.com/images/I/616TLHB+3RL._AC_SL500_.jpg',
                end_time=None,
                affiliate_url='https://www.amazon.com/dp/B00NGV4506?tag=dailydealdarl-20',
            ),
            Deal(
                asin='B00TTD9BRC',
                title='CeraVe Moisturizing Cream 16oz',
                deal_price=12.99,
                original_price=18.99,
                discount_percentage=31.6,
                deal_type='deal',
                image_url='https://m.media-amazon.com/images/I/61S7BrCBj7L._SL500_.jpg',
                end_time=None,
                affiliate_url='https://www.amazon.com/dp/B00TTD9BRC?tag=dailydealdarl-20',
            ),
        ]
        deals = mock_deals
    else:
        # Fetch real deals
        deals = fetch_deals()

    if not deals:
        logger.warning("No deals found!")
        return 1

    # Get homepage deals
    homepage_deals = get_homepage_deals(deals)
    logger.info(f"Selected {len(homepage_deals)} deals for homepage")

    # Save locally
    save_deals_locally(homepage_deals, args.output)

    # Optionally save to database
    if args.save_db:
        save_deals_to_supabase(homepage_deals)

    # Print summary
    print(f"\n{'='*60}")
    print("DEALS FETCHED SUCCESSFULLY")
    print(f"{'='*60}")
    for deal in homepage_deals:
        print(f"\n{deal.title[:50]}...")
        print(f"  ASIN: {deal.asin}")
        print(f"  Price: ${deal.deal_price:.2f} (was ${deal.original_price:.2f})")
        print(f"  Discount: {deal.discount_percentage:.0f}% OFF")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    exit(main())
