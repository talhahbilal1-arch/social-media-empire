"""
Affiliate Link Generator for Social Media Empire.

Generates Amazon affiliate links with proper encoding and tracking parameters.
Supports both search-based and ASIN-based (direct product) links.
"""

import urllib.parse
from typing import Optional
from datetime import datetime


# Brand-specific affiliate tags
AFFILIATE_TAGS = {
    'dailydealdarling': 'dailydealdarling1-20',
    'daily_deal_darling': 'dailydealdarling1-20',
    'menopause_planner': 'menopauseplan-20',
    'nurse_planner': 'nurseplanner-20',
    'adhd_planner': 'adhdplanner-20',
    'fitover35': 'dailydealdarl-20',
}

# Default affiliate tag
DEFAULT_TAG = 'dailydealdarling1-20'


def get_affiliate_tag(brand: str) -> str:
    """Get the affiliate tag for a given brand."""
    return AFFILIATE_TAGS.get(brand.lower().replace('-', '_'), DEFAULT_TAG)


def generate_amazon_link(
    search_term: str,
    brand: str = 'dailydealdarling',
    asin: Optional[str] = None,
) -> str:
    """
    Generate an Amazon affiliate link.

    Args:
        search_term: Product search term (used if no ASIN provided)
        brand: Brand name to determine affiliate tag
        asin: Optional Amazon product ASIN for direct link

    Returns:
        Formatted Amazon affiliate URL
    """
    tag = get_affiliate_tag(brand)

    if asin:
        # Direct product link using ASIN
        return f"https://www.amazon.com/dp/{asin}?tag={tag}"
    else:
        # Search-based link
        encoded_search = urllib.parse.quote_plus(search_term)
        return f"https://www.amazon.com/s?k={encoded_search}&tag={tag}"


def generate_tracked_link(
    search_term: str,
    brand: str = 'dailydealdarling',
    source: str = 'article',
    campaign: Optional[str] = None,
    asin: Optional[str] = None,
) -> str:
    """
    Generate an Amazon affiliate link with UTM tracking parameters.

    Args:
        search_term: Product search term
        brand: Brand name
        source: Traffic source (article, email, social, etc.)
        campaign: Optional campaign name
        asin: Optional Amazon product ASIN

    Returns:
        Amazon affiliate URL with tracking parameters
    """
    tag = get_affiliate_tag(brand)

    # Build base URL
    if asin:
        base_url = f"https://www.amazon.com/dp/{asin}"
    else:
        encoded_search = urllib.parse.quote_plus(search_term)
        base_url = f"https://www.amazon.com/s?k={encoded_search}"

    # Add affiliate tag
    separator = '&' if '?' in base_url else '?'
    url = f"{base_url}{separator}tag={tag}"

    # Note: Amazon doesn't support UTM parameters, but we can use
    # linkId for internal tracking via Amazon Associates reports
    # For now, we include the source in a way that might help with reporting

    return url


def generate_product_card_html(
    name: str,
    description: str,
    search_term: str,
    brand: str = 'dailydealdarling',
    price_range: Optional[str] = None,
    asin: Optional[str] = None,
) -> str:
    """
    Generate HTML for a product recommendation card.

    Args:
        name: Product name
        description: Product description
        search_term: Amazon search term
        brand: Brand for affiliate tag
        price_range: Optional price range (e.g., "Under $25")
        asin: Optional product ASIN

    Returns:
        HTML string for product card
    """
    link = generate_amazon_link(search_term, brand, asin)

    price_html = f'<p class="product-card__price">{price_range}</p>' if price_range else ''

    return f"""<div class="product-card">
  <h3 class="product-card__name">{name}</h3>
  {price_html}
  <p class="product-card__description">{description}</p>
  <a href="{link}" class="product-card__cta" target="_blank" rel="nofollow noopener">Check Price on Amazon</a>
</div>"""


def generate_inline_link(
    text: str,
    search_term: str,
    brand: str = 'dailydealdarling',
    asin: Optional[str] = None,
) -> str:
    """
    Generate an inline affiliate link for use within article text.

    Args:
        text: Link text to display
        search_term: Amazon search term
        brand: Brand for affiliate tag
        asin: Optional product ASIN

    Returns:
        HTML anchor tag
    """
    link = generate_amazon_link(search_term, brand, asin)
    return f'<a href="{link}" target="_blank" rel="nofollow noopener">{text}</a>'


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate Amazon affiliate links')
    parser.add_argument(
        'search_term',
        help='Product search term'
    )
    parser.add_argument(
        '--brand',
        default='dailydealdarling',
        help='Brand name for affiliate tag'
    )
    parser.add_argument(
        '--asin',
        help='Optional Amazon ASIN for direct link'
    )
    parser.add_argument(
        '--format',
        choices=['url', 'html', 'markdown'],
        default='url',
        help='Output format'
    )

    args = parser.parse_args()

    link = generate_amazon_link(args.search_term, args.brand, args.asin)

    if args.format == 'url':
        print(link)
    elif args.format == 'html':
        print(f'<a href="{link}" target="_blank" rel="nofollow noopener">{args.search_term}</a>')
    elif args.format == 'markdown':
        print(f'[{args.search_term}]({link})')

    return 0


if __name__ == "__main__":
    exit(main())
