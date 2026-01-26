"""
Generate HTML for the deals section from fetched deal data.

This script:
1. Reads deal data from JSON (output of fetch_deals.py)
2. Generates product card HTML for each deal
3. Updates the index.html deals section
4. Preserves the rest of the page structure
"""

import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Badge colors for different discount tiers
BADGE_COLORS = {
    'high': '#E74C3C',    # 40%+ - Red
    'medium': '#E67E22',  # 25-39% - Orange
    'low': '#27AE60',     # 15-24% - Green
}


def get_badge_color(discount: float) -> str:
    """Get badge color based on discount percentage."""
    if discount >= 40:
        return BADGE_COLORS['high']
    elif discount >= 25:
        return BADGE_COLORS['medium']
    else:
        return BADGE_COLORS['low']


def generate_deal_card(deal: dict) -> str:
    """
    Generate HTML for a single deal card.

    Args:
        deal: Deal dictionary from deals_data.json

    Returns:
        HTML string for the product card
    """
    asin = deal['asin']
    title = deal['title']
    deal_price = deal['deal_price']
    original_price = deal['original_price']
    discount = deal['discount_percentage']
    image_url = deal.get('image_url', '')
    affiliate_url = deal['affiliate_url']

    # Infer category from title
    title_lower = title.lower()
    if any(kw in title_lower for kw in ['beauty', 'skin', 'cream', 'lip', 'makeup']):
        category = 'Beauty'
    elif any(kw in title_lower for kw in ['kitchen', 'cook', 'chef', 'blender', 'pan']):
        category = 'Kitchen'
    elif any(kw in title_lower for kw in ['fitness', 'yoga', 'workout', 'gym', 'exercise']):
        category = 'Fitness'
    elif any(kw in title_lower for kw in ['home', 'storage', 'organiz', 'furniture']):
        category = 'Home'
    elif any(kw in title_lower for kw in ['tech', 'charger', 'power', 'electronic', 'phone']):
        category = 'Tech'
    elif any(kw in title_lower for kw in ['wellness', 'massage', 'health', 'theragun']):
        category = 'Wellness'
    else:
        category = 'Deals'

    badge_color = get_badge_color(discount)

    # Truncate title if too long
    display_title = title if len(title) <= 40 else title[:37] + '...'

    return f'''          <div class="product-card">
            <span class="product-badge" style="background: {badge_color};">{discount:.0f}% OFF</span>
            <div class="product-image" style="background: #f8f8f8; padding: 10px;">
              <img src="{image_url}" alt="{title}" style="object-fit: contain;">
            </div>
            <div class="product-content">
              <span class="product-category">{category}</span>
              <h4 class="product-title">{display_title}</h4>
              <div class="product-rating">
                <div class="stars">★★★★★</div>
                <span class="rating-count">Verified Deal</span>
              </div>
              <div class="product-price">
                <span class="price-current">${deal_price:.2f}</span>
                <span class="price-original">${original_price:.2f}</span>
              </div>
              <a href="{affiliate_url}" class="btn btn-amazon product-cta" target="_blank" rel="noopener sponsored">Grab This Deal →</a>
            </div>
          </div>'''


def generate_deals_section(deals: list[dict]) -> str:
    """
    Generate the complete deals section HTML.

    Args:
        deals: List of deal dictionaries

    Returns:
        HTML string for the entire deals section
    """
    if not deals:
        return ""

    cards_html = '\n'.join(generate_deal_card(deal) for deal in deals)

    return f'''    <!-- Today's Deals Section - Auto-generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} -->
    <section class="section" id="deals" style="background: var(--color-bg-alt);">
      <div class="container">
        <div class="section-header">
          <h2>⚡ Today's Best Deals</h2>
          <p>Real-time deals verified on Amazon • Updated every 4 hours</p>
        </div>
        <div class="grid grid-4">
{cards_html}
        </div>
      </div>
    </section>'''


def update_index_html(deals_html: str, index_path: str = "index.html") -> bool:
    """
    Update the deals section in index.html.

    Args:
        deals_html: New deals section HTML
        index_path: Path to index.html

    Returns:
        True if successful
    """
    index_file = Path(index_path)

    if not index_file.exists():
        logger.error(f"index.html not found at {index_path}")
        return False

    content = index_file.read_text(encoding='utf-8')

    # Pattern to match the deals section
    # Matches from the section with id="deals" to the closing </section>
    deals_pattern = r'(<!-- Today\'s (?:Best )?Deals Section.*?-->.*?<section[^>]*id="deals"[^>]*>.*?</section>)'

    # Alternative pattern for simpler matching
    alt_pattern = r'(<section[^>]*id="deals"[^>]*>.*?</section>)'

    # Try to find and replace the deals section
    if re.search(deals_pattern, content, re.DOTALL):
        new_content = re.sub(deals_pattern, deals_html, content, flags=re.DOTALL)
        logger.info("Updated deals section (full pattern match)")
    elif re.search(alt_pattern, content, re.DOTALL):
        new_content = re.sub(alt_pattern, deals_html, content, flags=re.DOTALL)
        logger.info("Updated deals section (alt pattern match)")
    else:
        logger.error("Could not find deals section in index.html")
        return False

    # Write updated content
    index_file.write_text(new_content, encoding='utf-8')
    logger.info(f"Updated {index_path}")

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate deals HTML')
    parser.add_argument(
        '--input',
        default='deals_data.json',
        help='Input deals JSON file (from fetch_deals.py)'
    )
    parser.add_argument(
        '--index',
        default='index.html',
        help='Path to index.html to update'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Preview HTML without updating index.html'
    )

    args = parser.parse_args()

    # Load deals data
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Deals data not found: {args.input}")
        logger.info("Run fetch_deals.py first to generate deals data")
        return 1

    deals_data = json.loads(input_path.read_text())
    deals = deals_data.get('deals', [])

    if not deals:
        logger.warning("No deals in input file")
        return 1

    logger.info(f"Loaded {len(deals)} deals from {args.input}")

    # Generate HTML
    deals_html = generate_deals_section(deals)

    if args.preview:
        print("\n" + "="*60)
        print("PREVIEW: Generated Deals HTML")
        print("="*60)
        print(deals_html)
        print("="*60)
        return 0

    # Update index.html
    if update_index_html(deals_html, args.index):
        logger.info("Successfully updated deals section")
        return 0
    else:
        logger.error("Failed to update deals section")
        return 1


if __name__ == "__main__":
    exit(main())
