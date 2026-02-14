"""Affiliate link management and product database."""

from .link_generator import generate_amazon_link, generate_tracked_link
from .product_database import get_products_by_category, get_random_products

__all__ = [
    'generate_amazon_link',
    'generate_tracked_link',
    'get_products_by_category',
    'get_random_products',
]
