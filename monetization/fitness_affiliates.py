"""High-commission fitness affiliate product management.

Manages affiliate products from ShareASale, ClickBank, Amazon, and direct
brand programs. Products are rotated into video descriptions, website
articles, and email sequences.
"""

import random
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AffiliateProduct:
    """A single affiliate product with tracking info."""
    name: str
    category: str  # supplements, equipment, programs, apps
    affiliate_url: str
    commission_rate: float  # e.g. 0.30 for 30%
    price: float
    network: str  # amazon, shareasale, clickbank, direct
    description: str
    pitch: str  # Short pitch for video CTAs
    active: bool = True


# Fitness affiliate products - ordered by commission rate (highest first)
# TODO: Replace placeholder URLs with actual affiliate links after signup
FITNESS_AFFILIATE_PRODUCTS = [
    # === HIGH COMMISSION (30-75%) — ClickBank / Direct ===
    AffiliateProduct(
        name="Old School New Body Program",
        category="programs",
        affiliate_url="https://www.clickbank.com/placeholder/oldschoolnewbody",  # TODO: Replace with actual ClickBank hop link
        commission_rate=0.75,
        price=20.00,
        network="clickbank",
        description="F4X Training System - workout program designed for people over 35",
        pitch="This training system is designed specifically for people over 35 - link in bio"
    ),
    AffiliateProduct(
        name="Anabolic Running",
        category="programs",
        affiliate_url="https://www.clickbank.com/placeholder/anabolicrunning",  # TODO: Replace
        commission_rate=0.75,
        price=15.00,
        network="clickbank",
        description="16-minute running protocol designed to boost testosterone naturally",
        pitch="This 16-minute protocol changed my cardio game - check bio for the link"
    ),
    AffiliateProduct(
        name="Lean Body Hacks",
        category="programs",
        affiliate_url="https://www.clickbank.com/placeholder/leanbodyhacks",  # TODO: Replace
        commission_rate=0.75,
        price=37.00,
        network="clickbank",
        description="Fat loss program optimized for men with declining metabolism",
        pitch="If your metabolism has slowed down, this is the fix - link in bio"
    ),

    # === MEDIUM-HIGH COMMISSION (15-40%) — ShareASale / Direct ===
    AffiliateProduct(
        name="Transparent Labs Creatine HMB",
        category="supplements",
        affiliate_url="https://www.shareasale.com/placeholder/transparentlabs",  # TODO: Replace with ShareASale link
        commission_rate=0.25,
        price=49.99,
        network="shareasale",
        description="Research-backed creatine with HMB for muscle preservation",
        pitch="The only creatine I recommend for men over 35 - link in bio"
    ),
    AffiliateProduct(
        name="Legion Athletics Whey+",
        category="supplements",
        affiliate_url="https://www.shareasale.com/placeholder/legion",  # TODO: Replace
        commission_rate=0.20,
        price=44.99,
        network="shareasale",
        description="100% whey isolate, no artificial junk. Third-party tested.",
        pitch="Cleanest protein powder I've found - check the link in bio"
    ),
    AffiliateProduct(
        name="TRX Suspension Trainer",
        category="equipment",
        affiliate_url="https://www.shareasale.com/placeholder/trx",  # TODO: Replace
        commission_rate=0.15,
        price=149.95,
        network="shareasale",
        description="Portable full-body workout system. Perfect for home or travel.",
        pitch="Best home workout equipment under $150 - link in bio"
    ),
    AffiliateProduct(
        name="Rogue Fitness Bands",
        category="equipment",
        affiliate_url="https://www.shareasale.com/placeholder/rogue",  # TODO: Replace
        commission_rate=0.15,
        price=34.50,
        network="shareasale",
        description="Commercial-grade resistance bands for warm-ups, rehab, and strength work.",
        pitch="These bands replaced half my warm-up routine - link in bio"
    ),

    # === AMAZON (4-10%) — Lower commission but high trust/conversion ===
    AffiliateProduct(
        name="Bowflex SelectTech 552 Dumbbells",
        category="equipment",
        affiliate_url="https://www.amazon.com/dp/B001ARYU58?tag=fitover35-20",
        commission_rate=0.04,
        price=349.00,
        network="amazon",
        description="Adjustable dumbbells replacing 15 sets. Space-efficient home gym essential.",
        pitch="The only dumbbells you need for a home gym - link in bio"
    ),
    AffiliateProduct(
        name="Optimum Nutrition Creatine",
        category="supplements",
        affiliate_url="https://www.amazon.com/dp/B002DYIZEO?tag=fitover35-20",
        commission_rate=0.04,
        price=28.99,
        network="amazon",
        description="Micronized creatine monohydrate. Most researched supplement.",
        pitch="5 grams a day - the most proven supplement in fitness"
    ),
    AffiliateProduct(
        name="Optimum Nutrition Gold Standard Whey",
        category="supplements",
        affiliate_url="https://www.amazon.com/dp/B000QSNYGI?tag=fitover35-20",
        commission_rate=0.04,
        price=36.99,
        network="amazon",
        description="Industry standard whey protein. 24g protein per scoop.",
        pitch="Meeting your protein goal just got easier - link in bio"
    ),
    AffiliateProduct(
        name="TriggerPoint GRID Foam Roller",
        category="equipment",
        affiliate_url="https://www.amazon.com/dp/B0040EKZDY?tag=fitover35-20",
        commission_rate=0.04,
        price=34.99,
        network="amazon",
        description="Essential recovery tool for myofascial release.",
        pitch="Non-negotiable recovery tool if you're training over 35"
    ),
    AffiliateProduct(
        name="FITFORT Resistance Bands Set",
        category="equipment",
        affiliate_url="https://www.amazon.com/dp/B08N5J924L?tag=fitover35-20",
        commission_rate=0.04,
        price=29.99,
        network="amazon",
        description="5 resistance levels. Perfect for warm-ups, rehab, and travel workouts.",
        pitch="Under $30 for a complete resistance band set - link in bio"
    ),
]


def get_products_by_category(category: str) -> list[AffiliateProduct]:
    """Get active products in a category, sorted by commission rate (highest first)."""
    return sorted(
        [p for p in FITNESS_AFFILIATE_PRODUCTS if p.active and p.category == category],
        key=lambda p: p.commission_rate,
        reverse=True
    )


def get_random_product(category: str = None, prefer_high_commission: bool = True) -> AffiliateProduct:
    """Get a random product, optionally filtered by category.

    If prefer_high_commission is True, products with higher commission rates
    are weighted more heavily in the random selection.
    """
    products = [p for p in FITNESS_AFFILIATE_PRODUCTS if p.active]
    if category:
        products = [p for p in products if p.category == category]

    if not products:
        return FITNESS_AFFILIATE_PRODUCTS[0]  # Fallback

    if prefer_high_commission:
        # Weight by commission rate
        weights = [p.commission_rate for p in products]
        return random.choices(products, weights=weights, k=1)[0]

    return random.choice(products)


def get_product_for_article(article_topic: str) -> list[AffiliateProduct]:
    """Get relevant products based on article topic keywords.

    Returns up to 3 products, prioritizing high-commission items.
    """
    topic_lower = article_topic.lower()

    # Keyword to category mapping
    category_keywords = {
        "supplements": ["supplement", "creatine", "protein", "nutrition", "diet", "meal", "eat"],
        "equipment": ["equipment", "gym", "home gym", "dumbbell", "band", "roller", "foam", "gear"],
        "programs": ["program", "workout", "training", "plan", "routine", "exercise", "fat loss", "muscle"],
    }

    matched_categories = set()
    for category, keywords in category_keywords.items():
        if any(kw in topic_lower for kw in keywords):
            matched_categories.add(category)

    # If no match, return a mix
    if not matched_categories:
        matched_categories = {"supplements", "equipment", "programs"}

    results = []
    for cat in matched_categories:
        products = get_products_by_category(cat)
        if products:
            results.append(products[0])  # Highest commission in each category

    return results[:3]


def generate_affiliate_section_html(products: list[AffiliateProduct]) -> str:
    """Generate HTML for an affiliate product recommendation section.

    Used in auto-generated articles to embed product recommendations.
    """
    if not products:
        return ""

    html = '<div class="affiliate-recommendations" style="background: var(--color-off-white); padding: 2rem; border-radius: 8px; margin: 2rem 0;">\n'
    html += '<h3 style="margin-bottom: 1rem;">Recommended Products</h3>\n'
    html += '<p style="color: var(--color-slate-blue); margin-bottom: 1.5rem; font-size: 0.9rem;">These are products we use and recommend. Affiliate links support the site at no extra cost to you.</p>\n'

    for product in products:
        html += f'''<div style="display: flex; align-items: center; gap: 1rem; padding: 1rem 0; border-bottom: 1px solid var(--color-gray-100);">
  <div style="flex: 1;">
    <strong>{product.name}</strong>
    <p style="color: var(--color-slate-blue); margin: 0.25rem 0; font-size: 0.9rem;">{product.description}</p>
    <span style="color: var(--color-accent); font-weight: 600;">${product.price:.2f}</span>
  </div>
  <a href="{product.affiliate_url}" target="_blank" rel="noopener sponsored" style="background: var(--color-accent); color: white; padding: 0.5rem 1.25rem; border-radius: 4px; text-decoration: none; font-weight: 600; white-space: nowrap;">Check Price</a>
</div>\n'''

    html += '</div>\n'
    return html


def get_video_affiliate_pitch() -> dict:
    """Get a product pitch for video CTA usage.

    Returns a dict with product info suitable for embedding
    in video scripts and pin descriptions.
    """
    product = get_random_product(prefer_high_commission=True)
    return {
        "product_name": product.name,
        "pitch": product.pitch,
        "url": product.affiliate_url,
        "category": product.category,
        "price": product.price,
        "commission_rate": product.commission_rate,
    }
