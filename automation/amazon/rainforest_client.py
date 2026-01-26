"""
Rainforest API client for fetching Amazon product data.

This client provides methods to:
- Fetch product details (price, availability, images, ratings)
- Get active deals and discounts
- Track price history for calculating real discount percentages

Requires RAINFOREST_API_KEY environment variable.
API Documentation: https://www.rainforestapi.com/docs
"""

import os
import time
import logging
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class Product:
    """Amazon product data."""
    asin: str
    title: str
    price: Optional[float]
    list_price: Optional[float]
    currency: str
    availability: str
    rating: Optional[float]
    review_count: Optional[int]
    image_url: Optional[str]
    brand: Optional[str]
    category: Optional[str]
    is_prime: bool
    affiliate_url: str
    fetched_at: datetime

    @property
    def discount_percentage(self) -> Optional[float]:
        """Calculate discount percentage if list price available."""
        if self.price and self.list_price and self.list_price > self.price:
            return round((1 - self.price / self.list_price) * 100, 1)
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            'asin': self.asin,
            'title': self.title,
            'price': self.price,
            'list_price': self.list_price,
            'currency': self.currency,
            'availability': self.availability,
            'rating': self.rating,
            'review_count': self.review_count,
            'image_url': self.image_url,
            'brand': self.brand,
            'category': self.category,
            'is_prime': self.is_prime,
            'affiliate_url': self.affiliate_url,
            'discount_percentage': self.discount_percentage,
            'fetched_at': self.fetched_at.isoformat(),
        }


@dataclass
class Deal:
    """Amazon deal data."""
    asin: str
    title: str
    deal_price: float
    original_price: float
    discount_percentage: float
    deal_type: str  # 'lightning', 'best_deal', 'deal_of_day'
    image_url: Optional[str]
    end_time: Optional[datetime]
    affiliate_url: str

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            'asin': self.asin,
            'title': self.title,
            'deal_price': self.deal_price,
            'original_price': self.original_price,
            'discount_percentage': self.discount_percentage,
            'deal_type': self.deal_type,
            'image_url': self.image_url,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'affiliate_url': self.affiliate_url,
        }


class RainforestClient:
    """Client for Rainforest API to fetch Amazon product data."""

    BASE_URL = "https://api.rainforestapi.com/request"
    AFFILIATE_TAG = "dailydealdarling1-20"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Rainforest API client.

        Args:
            api_key: Rainforest API key. If not provided, reads from RAINFOREST_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("RAINFOREST_API_KEY")
        if not self.api_key:
            raise ValueError("RAINFOREST_API_KEY not set. Get one at https://www.rainforestapi.com")

        # Set up session with retry logic
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.6  # ~100 requests per minute

    def _rate_limit(self):
        """Ensure we don't exceed rate limits."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def _make_request(self, params: dict) -> dict:
        """Make API request with error handling."""
        self._rate_limit()

        params['api_key'] = self.api_key
        params['amazon_domain'] = 'amazon.com'

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Rainforest API error: {e}")
            raise

    def get_product(self, asin: str) -> Optional[Product]:
        """
        Fetch product details by ASIN.

        Args:
            asin: Amazon Standard Identification Number

        Returns:
            Product object or None if not found
        """
        logger.info(f"Fetching product {asin}")

        params = {
            'type': 'product',
            'asin': asin,
        }

        try:
            data = self._make_request(params)
            product_data = data.get('product', {})

            if not product_data:
                logger.warning(f"Product {asin} not found")
                return None

            # Extract price information
            price_info = product_data.get('buybox_winner', {})
            price = price_info.get('price', {}).get('value')

            # Get list price (RRP)
            list_price = None
            if 'rrp' in price_info:
                list_price = price_info['rrp'].get('value')

            # Build affiliate URL
            affiliate_url = f"https://www.amazon.com/dp/{asin}?tag={self.AFFILIATE_TAG}"

            return Product(
                asin=asin,
                title=product_data.get('title', ''),
                price=price,
                list_price=list_price,
                currency=price_info.get('price', {}).get('currency', 'USD'),
                availability=product_data.get('availability', {}).get('raw', 'Unknown'),
                rating=product_data.get('rating'),
                review_count=product_data.get('ratings_total'),
                image_url=product_data.get('main_image', {}).get('link'),
                brand=product_data.get('brand'),
                category=product_data.get('categories', [{}])[0].get('name') if product_data.get('categories') else None,
                is_prime=price_info.get('is_prime', False),
                affiliate_url=affiliate_url,
                fetched_at=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"Error fetching product {asin}: {e}")
            return None

    def get_deals(self, category: str = "deals", max_results: int = 20) -> list[Deal]:
        """
        Fetch current Amazon deals.

        Args:
            category: Deal category filter
            max_results: Maximum number of deals to return

        Returns:
            List of Deal objects
        """
        logger.info(f"Fetching deals for category: {category}")

        params = {
            'type': 'deals',
            'category': category,
        }

        try:
            data = self._make_request(params)
            deals_data = data.get('deals', [])[:max_results]

            deals = []
            for deal_item in deals_data:
                # Extract deal information
                asin = deal_item.get('asin')
                if not asin:
                    continue

                price_info = deal_item.get('deal_price', {})
                original_info = deal_item.get('list_price', {})

                deal_price = price_info.get('value', 0)
                original_price = original_info.get('value', deal_price)

                # Calculate discount
                if original_price > 0 and deal_price < original_price:
                    discount = round((1 - deal_price / original_price) * 100, 1)
                else:
                    discount = 0

                # Skip deals with less than 15% discount
                if discount < 15:
                    continue

                affiliate_url = f"https://www.amazon.com/dp/{asin}?tag={self.AFFILIATE_TAG}"

                deals.append(Deal(
                    asin=asin,
                    title=deal_item.get('title', ''),
                    deal_price=deal_price,
                    original_price=original_price,
                    discount_percentage=discount,
                    deal_type=deal_item.get('deal_type', 'deal'),
                    image_url=deal_item.get('image'),
                    end_time=None,  # Parse end time if available
                    affiliate_url=affiliate_url,
                ))

            logger.info(f"Found {len(deals)} deals with 15%+ discount")
            return deals

        except Exception as e:
            logger.error(f"Error fetching deals: {e}")
            return []

    def verify_asin(self, asin: str) -> dict:
        """
        Verify an ASIN exists and get basic info.

        Args:
            asin: Amazon Standard Identification Number

        Returns:
            Dict with verification result: {'valid': bool, 'title': str, 'error': str}
        """
        product = self.get_product(asin)

        if product:
            return {
                'valid': True,
                'asin': asin,
                'title': product.title,
                'price': product.price,
                'availability': product.availability,
                'error': None,
            }
        else:
            return {
                'valid': False,
                'asin': asin,
                'title': None,
                'price': None,
                'availability': None,
                'error': 'Product not found or unavailable',
            }

    def get_price_history(self, asin: str, days: int = 90) -> list[dict]:
        """
        Get price history for a product (if available in API plan).

        Note: Price history requires Rainforest API Growth plan or higher.

        Args:
            asin: Amazon Standard Identification Number
            days: Number of days of history to fetch

        Returns:
            List of price points: [{'date': str, 'price': float}, ...]
        """
        logger.info(f"Fetching {days}-day price history for {asin}")

        # Note: This endpoint may require higher API tier
        params = {
            'type': 'product',
            'asin': asin,
            'include_price_history': 'true',
        }

        try:
            data = self._make_request(params)
            history = data.get('product', {}).get('price_history', [])

            return [
                {'date': point.get('date'), 'price': point.get('price', {}).get('value')}
                for point in history
                if point.get('price', {}).get('value')
            ]

        except Exception as e:
            logger.error(f"Error fetching price history for {asin}: {e}")
            return []


# Convenience function for quick product lookup
def get_product_info(asin: str) -> Optional[dict]:
    """Quick lookup of product info by ASIN."""
    try:
        client = RainforestClient()
        product = client.get_product(asin)
        return product.to_dict() if product else None
    except Exception as e:
        logger.error(f"Error in quick product lookup: {e}")
        return None


if __name__ == "__main__":
    # Test the client
    import json

    logging.basicConfig(level=logging.INFO)

    # Test product lookup
    client = RainforestClient()

    test_asins = [
        "B00TTD9BRC",  # CeraVe
        "B07XXPHQZK",  # Laneige
        "B07HBTY3Z2",  # Anker PowerCore
    ]

    print("Testing product lookups:")
    for asin in test_asins:
        product = client.get_product(asin)
        if product:
            print(f"\n{asin}: {product.title}")
            print(f"  Price: ${product.price}")
            print(f"  Rating: {product.rating} ({product.review_count} reviews)")
            print(f"  Discount: {product.discount_percentage}%")
        else:
            print(f"\n{asin}: NOT FOUND")

    # Test deals
    print("\n\nTesting deals fetch:")
    deals = client.get_deals(max_results=5)
    for deal in deals:
        print(f"\n{deal.asin}: {deal.title[:50]}...")
        print(f"  Deal: ${deal.deal_price} (was ${deal.original_price}) - {deal.discount_percentage}% off")
