"""
Weekly Deals Finder for Email Newsletter

Finds the top 10 deals in beauty, home, and decor categories
for the weekly Tuesday email to subscribers.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from automation.amazon.rainforest_client import RainforestClient, Deal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Target categories for women's newsletter (beauty, home, decor)
EMAIL_CATEGORIES = [
    {
        "name": "Beauty & Skincare",
        "search_terms": ["skincare", "beauty", "makeup", "hair care"],
        "min_deals": 3,
        "max_deals": 4,
    },
    {
        "name": "Home Organization",
        "search_terms": ["storage", "organization", "closet", "bathroom storage"],
        "min_deals": 3,
        "max_deals": 4,
    },
    {
        "name": "Home Decor",
        "search_terms": ["home decor", "throw pillows", "candles", "wall art"],
        "min_deals": 2,
        "max_deals": 3,
    },
]

# Filter criteria
MIN_DISCOUNT_PERCENT = 20  # Only show 20%+ off
MIN_RATING = 4.0  # Only show 4+ star items
MAX_PRICE = 50.00  # Keep it budget-friendly
MIN_REVIEWS = 500  # Must have social proof


@dataclass
class EmailDeal:
    """Deal formatted for email inclusion."""
    asin: str
    title: str
    category: str
    current_price: float
    original_price: float
    discount_percent: float
    rating: Optional[float]
    review_count: Optional[int]
    image_url: str
    affiliate_url: str
    why_buy: str  # One-liner reason to buy


def score_deal(deal: Deal, category_name: str) -> float:
    """
    Score a deal for email relevance.
    Higher score = better for email.
    """
    score = 0.0

    # Discount is most important (max 40 points)
    score += min(deal.discount_percentage, 40)

    # Price point matters (prefer $15-35 range, max 20 points)
    if 15 <= deal.deal_price <= 35:
        score += 20
    elif deal.deal_price < 15:
        score += 10
    elif deal.deal_price <= 50:
        score += 15

    # Bonus for Prime (10 points)
    # Note: Would need to check this via product API

    return score


def generate_why_buy(title: str, discount: float, category: str) -> str:
    """Generate a compelling one-liner for why to buy."""

    title_lower = title.lower()

    # Category-specific hooks
    if "skincare" in category.lower() or "beauty" in category.lower():
        if "serum" in title_lower:
            return f"Cult-favorite serum at {discount:.0f}% off!"
        elif "moisturizer" in title_lower or "cream" in title_lower:
            return f"Stock up on skincare essentials - {discount:.0f}% off"
        elif "lip" in title_lower:
            return f"TikTok-viral lip product now {discount:.0f}% off"
        else:
            return f"Beauty steal: {discount:.0f}% off today"

    elif "organization" in category.lower() or "storage" in category.lower():
        if "closet" in title_lower:
            return f"Closet organization goals at {discount:.0f}% off"
        elif "kitchen" in title_lower or "pantry" in title_lower:
            return f"Kitchen organization made easy - {discount:.0f}% off"
        else:
            return f"Declutter for less: {discount:.0f}% off"

    elif "decor" in category.lower():
        if "pillow" in title_lower:
            return f"Instant room refresh at {discount:.0f}% off"
        elif "candle" in title_lower:
            return f"Cozy vibes on sale: {discount:.0f}% off"
        else:
            return f"Home glow-up for {discount:.0f}% off"

    return f"Great deal: {discount:.0f}% off today only"


def find_weekly_deals(client: Optional[RainforestClient] = None) -> list[EmailDeal]:
    """
    Find the top 10 deals for the weekly email.

    Returns deals balanced across beauty, home, and decor categories.
    """
    if client is None:
        client = RainforestClient()

    all_deals = []

    for category in EMAIL_CATEGORIES:
        category_deals = []
        logger.info(f"Searching {category['name']}...")

        for search_term in category['search_terms']:
            try:
                # Fetch deals for this search term
                deals = client.get_deals(category=search_term, max_results=15)

                # Filter by criteria
                for deal in deals:
                    if deal.discount_percentage < MIN_DISCOUNT_PERCENT:
                        continue
                    if deal.deal_price > MAX_PRICE:
                        continue

                    # Score and add
                    score = score_deal(deal, category['name'])

                    category_deals.append({
                        'deal': deal,
                        'category': category['name'],
                        'score': score,
                    })

            except Exception as e:
                logger.error(f"Error fetching {search_term}: {e}")

        # Sort by score and take best ones
        category_deals.sort(key=lambda x: x['score'], reverse=True)

        # Take min_deals to max_deals from this category
        selected = category_deals[:category['max_deals']]
        all_deals.extend(selected)

        logger.info(f"Found {len(selected)} deals for {category['name']}")

    # Convert to EmailDeal format
    email_deals = []
    for item in all_deals[:10]:  # Cap at 10 total
        deal = item['deal']
        category = item['category']

        email_deals.append(EmailDeal(
            asin=deal.asin,
            title=deal.title,
            category=category,
            current_price=deal.deal_price,
            original_price=deal.original_price,
            discount_percent=deal.discount_percentage,
            rating=None,  # Would need product API call
            review_count=None,
            image_url=deal.image_url or "",
            affiliate_url=deal.affiliate_url,
            why_buy=generate_why_buy(deal.title, deal.discount_percentage, category)
        ))

    logger.info(f"Total deals for email: {len(email_deals)}")
    return email_deals


def save_deals_json(deals: list[EmailDeal], output_path: str = "weekly_deals.json"):
    """Save deals to JSON for email generation."""

    deals_data = {
        'generated_at': datetime.utcnow().isoformat(),
        'email_date': get_next_tuesday().isoformat(),
        'deal_count': len(deals),
        'deals': [
            {
                'asin': d.asin,
                'title': d.title,
                'category': d.category,
                'current_price': d.current_price,
                'original_price': d.original_price,
                'discount_percent': d.discount_percent,
                'rating': d.rating,
                'review_count': d.review_count,
                'image_url': d.image_url,
                'affiliate_url': d.affiliate_url,
                'why_buy': d.why_buy,
            }
            for d in deals
        ]
    }

    Path(output_path).write_text(json.dumps(deals_data, indent=2))
    logger.info(f"Saved {len(deals)} deals to {output_path}")


def get_next_tuesday() -> datetime:
    """Get the next Tuesday date."""
    from datetime import timedelta

    today = datetime.now()
    days_until_tuesday = (1 - today.weekday()) % 7
    if days_until_tuesday == 0:
        days_until_tuesday = 7  # If today is Tuesday, get next Tuesday

    return today + timedelta(days=days_until_tuesday)


def create_mock_deals() -> list[EmailDeal]:
    """Create mock deals for testing without API."""

    return [
        EmailDeal(
            asin="B00TTD9BRC",
            title="CeraVe Moisturizing Cream 16oz",
            category="Beauty & Skincare",
            current_price=12.99,
            original_price=18.99,
            discount_percent=32,
            rating=4.7,
            review_count=127000,
            image_url="https://m.media-amazon.com/images/I/61S7BrCBj7L._SL500_.jpg",
            affiliate_url="https://www.amazon.com/dp/B00TTD9BRC?tag=dailydealdarling1-20",
            why_buy="Stock up on skincare essentials - 32% off"
        ),
        EmailDeal(
            asin="B07XXPHQZK",
            title="Laneige Lip Sleeping Mask Berry",
            category="Beauty & Skincare",
            current_price=18.00,
            original_price=24.00,
            discount_percent=25,
            rating=4.6,
            review_count=45000,
            image_url="https://m.media-amazon.com/images/I/51k+hnqOuWL._SL500_.jpg",
            affiliate_url="https://www.amazon.com/dp/B07XXPHQZK?tag=dailydealdarling1-20",
            why_buy="TikTok-viral lip product now 25% off"
        ),
        EmailDeal(
            asin="B09QMF91LK",
            title="Criusia Storage Cubes 8-Pack",
            category="Home Organization",
            current_price=19.99,
            original_price=29.99,
            discount_percent=33,
            rating=4.5,
            review_count=15000,
            image_url="https://m.media-amazon.com/images/I/81yW0OBUTOL._AC_SL500_.jpg",
            affiliate_url="https://www.amazon.com/dp/B09QMF91LK?tag=dailydealdarling1-20",
            why_buy="Declutter for less: 33% off"
        ),
        EmailDeal(
            asin="B076B3R3QF",
            title="mDesign Plastic Storage Bins Set",
            category="Home Organization",
            current_price=18.99,
            original_price=24.99,
            discount_percent=24,
            rating=4.6,
            review_count=12000,
            image_url="https://m.media-amazon.com/images/I/71LdvqKBqjL._AC_SL500_.jpg",
            affiliate_url="https://www.amazon.com/dp/B076B3R3QF?tag=dailydealdarling1-20",
            why_buy="Kitchen organization made easy - 24% off"
        ),
        EmailDeal(
            asin="B08HYF4J6N",
            title="KIVIK Throw Pillow Covers 18x18",
            category="Home Decor",
            current_price=11.99,
            original_price=16.99,
            discount_percent=29,
            rating=4.5,
            review_count=18000,
            image_url="https://m.media-amazon.com/images/I/81CxV7OT1QL._AC_SL500_.jpg",
            affiliate_url="https://www.amazon.com/dp/B08HYF4J6N?tag=dailydealdarling1-20",
            why_buy="Instant room refresh at 29% off"
        ),
    ]


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Find weekly deals for email')
    parser.add_argument(
        '--output',
        default='weekly_deals.json',
        help='Output JSON file path'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Use mock data instead of API calls'
    )

    args = parser.parse_args()

    if args.dry_run:
        logger.info("DRY RUN - using mock deals")
        deals = create_mock_deals()
    else:
        deals = find_weekly_deals()

    if not deals:
        logger.warning("No deals found!")
        return 1

    save_deals_json(deals, args.output)

    # Print summary
    print(f"\n{'='*60}")
    print(f"WEEKLY DEALS FOUND: {len(deals)}")
    print(f"{'='*60}")

    for deal in deals:
        print(f"\n{deal.title[:50]}...")
        print(f"  ${deal.current_price:.2f} (was ${deal.original_price:.2f}) - {deal.discount_percent:.0f}% off")
        print(f"  Category: {deal.category}")
        print(f"  Hook: {deal.why_buy}")

    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    exit(main())
