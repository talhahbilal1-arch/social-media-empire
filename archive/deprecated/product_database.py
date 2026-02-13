"""
Product Database for Daily Deal Darling and other brands.

Curated products by category with ASINs, prices, and descriptions
for use in article generation and recommendations.
"""

import random
from typing import List, Optional, Dict, Any


# ── Product Database ─────────────────────────────────────────────────────────

PRODUCTS = {
    "skincare": [
        {
            "name": "CeraVe Moisturizing Cream",
            "asin": "B00TTD9BRC",
            "search_term": "CeraVe Moisturizing Cream 16oz",
            "price_range": "Under $20",
            "description": "Dermatologist-recommended daily moisturizer with ceramides and hyaluronic acid. Perfect for dry to normal skin.",
            "rating": 4.7,
        },
        {
            "name": "La Roche-Posay Anthelios Sunscreen",
            "asin": "B002CML1VG",
            "search_term": "La Roche-Posay Anthelios Melt-In Sunscreen SPF 60",
            "price_range": "Under $35",
            "description": "Lightweight, fast-absorbing sunscreen that feels invisible on skin. Great for daily use under makeup.",
            "rating": 4.6,
        },
        {
            "name": "The Ordinary Niacinamide 10% + Zinc 1%",
            "asin": "B06VSQ2S75",
            "search_term": "The Ordinary Niacinamide 10% + Zinc 1%",
            "price_range": "Under $10",
            "description": "Cult-favorite serum that helps minimize pores and control oil. Amazing value for the results.",
            "rating": 4.5,
        },
        {
            "name": "Neutrogena Hydro Boost Gel Cream",
            "asin": "B00NR1YQHM",
            "search_term": "Neutrogena Hydro Boost Water Gel",
            "price_range": "Under $20",
            "description": "Lightweight gel moisturizer with hyaluronic acid. Absorbs quickly without feeling greasy.",
            "rating": 4.6,
        },
        {
            "name": "Paula's Choice 2% BHA Liquid Exfoliant",
            "asin": "B00949CTQQ",
            "search_term": "Paula's Choice 2% BHA Liquid Exfoliant",
            "price_range": "Under $35",
            "description": "Gentle yet effective salicylic acid exfoliant for smoother, clearer skin. Use 2-3 times per week.",
            "rating": 4.6,
        },
    ],

    "kitchen": [
        {
            "name": "Instant Pot Duo 7-in-1",
            "asin": "B00FLYWNYQ",
            "search_term": "Instant Pot Duo 7-in-1 6 Quart",
            "price_range": "Under $100",
            "description": "The kitchen appliance that does it all. Pressure cooker, slow cooker, rice cooker, and more.",
            "rating": 4.7,
        },
        {
            "name": "Ninja Professional Blender",
            "asin": "B00NGV4506",
            "search_term": "Ninja Professional Blender 1000W",
            "price_range": "Under $100",
            "description": "Powerful 1000-watt blender that crushes ice and blends smoothies perfectly every time.",
            "rating": 4.7,
        },
        {
            "name": "OXO Good Grips 3-Piece Cutting Board Set",
            "asin": "B00I0Z8W9K",
            "search_term": "OXO Good Grips Cutting Board Set",
            "price_range": "Under $30",
            "description": "Non-slip cutting boards in three sizes. Dishwasher safe and easy to store.",
            "rating": 4.7,
        },
        {
            "name": "Lodge Cast Iron Skillet",
            "asin": "B00006JSUB",
            "search_term": "Lodge 10.25 Inch Cast Iron Skillet",
            "price_range": "Under $25",
            "description": "Pre-seasoned cast iron that gets better with age. A kitchen essential that lasts forever.",
            "rating": 4.7,
        },
        {
            "name": "Rubbermaid Meal Prep Containers",
            "asin": "B01JCRXYXC",
            "search_term": "Rubbermaid Meal Prep Containers 7-Pack",
            "price_range": "Under $20",
            "description": "Stackable meal prep containers with divided compartments. Microwave and dishwasher safe.",
            "rating": 4.5,
        },
    ],

    "organization": [
        {
            "name": "SimpleHouseware Closet Organizer",
            "asin": "B072Q1FJN1",
            "search_term": "SimpleHouseware Hanging Closet Organizer",
            "price_range": "Under $15",
            "description": "6-shelf hanging organizer that maximizes vertical closet space. Perfect for sweaters and bags.",
            "rating": 4.6,
        },
        {
            "name": "mDesign Stackable Storage Bins",
            "asin": "B01GKJ0EJI",
            "search_term": "mDesign Stackable Plastic Storage Bins",
            "price_range": "Under $25",
            "description": "Clear stackable bins with handles. Great for pantry, bathroom, or closet organization.",
            "rating": 4.5,
        },
        {
            "name": "YouCopia SpiceStack Organizer",
            "asin": "B003L77WIO",
            "search_term": "YouCopia SpiceStack Spice Rack Organizer",
            "price_range": "Under $25",
            "description": "Drawer spice organizer with adjustable compartments. No more digging through cabinets!",
            "rating": 4.6,
        },
        {
            "name": "Bamboo Drawer Dividers",
            "asin": "B01F26KLMY",
            "search_term": "Bamboo Drawer Dividers Adjustable",
            "price_range": "Under $20",
            "description": "Spring-loaded bamboo dividers that fit any drawer. Eco-friendly and adjustable.",
            "rating": 4.5,
        },
        {
            "name": "Under Sink Organizer Shelf",
            "asin": "B089SVNV6Q",
            "search_term": "Under Sink Organizer 2-Tier",
            "price_range": "Under $25",
            "description": "Expandable under-sink shelf that works around pipes. Double your storage instantly.",
            "rating": 4.4,
        },
    ],

    "beauty": [
        {
            "name": "Revlon One-Step Hair Dryer",
            "asin": "B01LSUQSB0",
            "search_term": "Revlon One-Step Hair Dryer and Volumizer",
            "price_range": "Under $50",
            "description": "The viral hair tool that dries and styles at the same time. Salon blowout at home!",
            "rating": 4.5,
        },
        {
            "name": "Real Techniques Brush Set",
            "asin": "B004TSFBNK",
            "search_term": "Real Techniques Makeup Brush Set",
            "price_range": "Under $20",
            "description": "Professional-quality brushes at a fraction of the price. Soft, durable, and easy to clean.",
            "rating": 4.6,
        },
        {
            "name": "Maybelline Lash Sensational Mascara",
            "asin": "B00PFCTSD4",
            "search_term": "Maybelline Lash Sensational Mascara",
            "price_range": "Under $10",
            "description": "Fan-favorite mascara for full, fanned-out lashes. Buildable and doesn't clump.",
            "rating": 4.4,
        },
        {
            "name": "NYX Butter Gloss",
            "asin": "B00FYS9KC6",
            "search_term": "NYX Butter Gloss",
            "price_range": "Under $6",
            "description": "Buttery smooth lip gloss in tons of shades. Non-sticky formula that smells amazing.",
            "rating": 4.4,
        },
        {
            "name": "e.l.f. Poreless Putty Primer",
            "asin": "B07F6X5WW6",
            "search_term": "e.l.f. Poreless Putty Primer",
            "price_range": "Under $10",
            "description": "Silky primer that blurs pores and keeps makeup in place. Drugstore dupe for expensive primers.",
            "rating": 4.4,
        },
    ],

    "tech": [
        {
            "name": "Anker PowerCore Portable Charger",
            "asin": "B0194WDVHI",
            "search_term": "Anker PowerCore 10000 Portable Charger",
            "price_range": "Under $30",
            "description": "Compact portable charger that fits in your pocket. Charges iPhone 3+ times.",
            "rating": 4.7,
        },
        {
            "name": "Apple AirPods Pro",
            "asin": "B09JQMJHXY",
            "search_term": "Apple AirPods Pro 2nd Generation",
            "price_range": "Under $250",
            "description": "Premium wireless earbuds with active noise cancellation. Worth the investment.",
            "rating": 4.7,
        },
        {
            "name": "Logitech MX Anywhere 3",
            "asin": "B08BT4PYP1",
            "search_term": "Logitech MX Anywhere 3 Mouse",
            "price_range": "Under $80",
            "description": "Compact wireless mouse that works on any surface. Perfect for remote work.",
            "rating": 4.6,
        },
        {
            "name": "Ring Light with Phone Holder",
            "asin": "B08CVR6G6C",
            "search_term": "Ring Light 10 inch with Tripod Stand",
            "price_range": "Under $30",
            "description": "Adjustable ring light for video calls and content creation. Multiple brightness levels.",
            "rating": 4.5,
        },
        {
            "name": "Cable Management Box",
            "asin": "B07PRFDRD1",
            "search_term": "Cable Management Box Large",
            "price_range": "Under $20",
            "description": "Hide messy cables and power strips. Clean desk = clear mind.",
            "rating": 4.5,
        },
    ],

    "wellness": [
        {
            "name": "Theragun Mini Massage Gun",
            "asin": "B086BQMKZQ",
            "search_term": "Theragun Mini Massage Gun",
            "price_range": "Under $200",
            "description": "Compact percussion massager for on-the-go relief. Fits in your purse or gym bag.",
            "rating": 4.6,
        },
        {
            "name": "Gravity Weighted Blanket",
            "asin": "B073429DV2",
            "search_term": "Gravity Weighted Blanket 15 lb",
            "price_range": "Under $150",
            "description": "Premium weighted blanket for better sleep. Feels like a gentle hug all night.",
            "rating": 4.5,
        },
        {
            "name": "Vitruvi Stone Diffuser",
            "asin": "B072K7RNJX",
            "search_term": "Vitruvi Stone Diffuser",
            "price_range": "Under $120",
            "description": "Beautiful ceramic essential oil diffuser. Aesthetic and functional.",
            "rating": 4.6,
        },
        {
            "name": "Hydro Flask Water Bottle",
            "asin": "B01ACATW7E",
            "search_term": "Hydro Flask 32 oz Wide Mouth",
            "price_range": "Under $45",
            "description": "Keeps drinks cold for 24 hours. Durable and comes in beautiful colors.",
            "rating": 4.8,
        },
        {
            "name": "Jade Roller and Gua Sha Set",
            "asin": "B07GT23RH1",
            "search_term": "Jade Roller and Gua Sha Set",
            "price_range": "Under $15",
            "description": "Traditional face massage tools for lymphatic drainage and relaxation.",
            "rating": 4.5,
        },
    ],

    "budget": [
        {
            "name": "Silicone Baking Mats (Set of 3)",
            "asin": "B00629K4YK",
            "search_term": "Silicone Baking Mats Set of 3",
            "price_range": "Under $15",
            "description": "Reusable baking mats that replace parchment paper. Save money and the environment.",
            "rating": 4.7,
        },
        {
            "name": "Microfiber Cleaning Cloths (24 Pack)",
            "asin": "B00V24L91Y",
            "search_term": "Microfiber Cleaning Cloths 24 Pack",
            "price_range": "Under $15",
            "description": "Ultra-absorbent cloths for every cleaning task. Washable and reusable.",
            "rating": 4.6,
        },
        {
            "name": "Cord Organizer Clips",
            "asin": "B08JLFX23L",
            "search_term": "Cable Clips Cord Organizer 20 Pack",
            "price_range": "Under $10",
            "description": "Adhesive cord clips to keep cables tidy. Small but life-changing.",
            "rating": 4.4,
        },
        {
            "name": "Reusable Produce Bags",
            "asin": "B07PVMF6SD",
            "search_term": "Reusable Produce Bags Mesh Set",
            "price_range": "Under $15",
            "description": "Washable mesh bags for grocery shopping. Say goodbye to plastic bags.",
            "rating": 4.6,
        },
        {
            "name": "Collapsible Colander Set",
            "asin": "B01M8IYT2F",
            "search_term": "Collapsible Colander Set of 2",
            "price_range": "Under $15",
            "description": "Space-saving colanders that collapse flat. Perfect for small kitchens.",
            "rating": 4.5,
        },
    ],

    "haircare": [
        {
            "name": "Olaplex No. 3 Hair Perfector",
            "asin": "B00SNM5US4",
            "search_term": "Olaplex No. 3 Hair Perfector",
            "price_range": "Under $30",
            "description": "Weekly treatment that repairs damaged hair from the inside. Game-changer for color-treated hair.",
            "rating": 4.5,
        },
        {
            "name": "Wet Brush Original Detangler",
            "asin": "B00564Y4L0",
            "search_term": "Wet Brush Original Detangler",
            "price_range": "Under $10",
            "description": "Pain-free detangling brush for all hair types. Works on wet or dry hair.",
            "rating": 4.7,
        },
        {
            "name": "Chi Silk Infusion",
            "asin": "B000A0GQIK",
            "search_term": "Chi Silk Infusion",
            "price_range": "Under $15",
            "description": "Lightweight silk serum that adds shine without weighing hair down. A little goes a long way.",
            "rating": 4.6,
        },
        {
            "name": "Revlon Ceramic Flat Iron",
            "asin": "B003F2VY1Y",
            "search_term": "Revlon Ceramic Flat Iron 1 inch",
            "price_range": "Under $20",
            "description": "Affordable flat iron with ceramic plates. Heats up fast with adjustable temps.",
            "rating": 4.4,
        },
        {
            "name": "Batiste Dry Shampoo",
            "asin": "B003WN2TR2",
            "search_term": "Batiste Dry Shampoo Original",
            "price_range": "Under $10",
            "description": "Refreshes hair between washes. Absorbs oil and adds volume instantly.",
            "rating": 4.5,
        },
    ],

    "seasonal": [
        {
            "name": "Cozy Throw Blanket",
            "asin": "B07BKVR91Y",
            "search_term": "Fleece Throw Blanket Cozy",
            "price_range": "Under $25",
            "description": "Super soft throw blanket perfect for movie nights. Machine washable.",
            "rating": 4.7,
        },
        {
            "name": "Candle Gift Set",
            "asin": "B0888BXRWR",
            "search_term": "Scented Candle Gift Set",
            "price_range": "Under $25",
            "description": "Set of beautifully scented candles. Perfect for gifting or self-care.",
            "rating": 4.5,
        },
        {
            "name": "Desk Calendar 2026",
            "asin": "B09X4RN6RZ",
            "search_term": "Desk Calendar 2026",
            "price_range": "Under $15",
            "description": "Stylish desk calendar to keep organized all year. Great new year gift.",
            "rating": 4.4,
        },
    ],
}


def get_products_by_category(category: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get products for a specific category.

    Args:
        category: Product category
        limit: Optional maximum number of products to return

    Returns:
        List of product dictionaries
    """
    products = PRODUCTS.get(category.lower(), [])
    if limit:
        return products[:limit]
    return products


def get_random_products(category: Optional[str] = None, count: int = 3) -> List[Dict[str, Any]]:
    """
    Get random products, optionally filtered by category.

    Args:
        category: Optional category filter
        count: Number of products to return

    Returns:
        List of random product dictionaries
    """
    if category:
        pool = PRODUCTS.get(category.lower(), [])
    else:
        pool = [p for products in PRODUCTS.values() for p in products]

    if len(pool) <= count:
        return pool

    return random.sample(pool, count)


def get_all_categories() -> List[str]:
    """Get list of all available categories."""
    return list(PRODUCTS.keys())


def search_products(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search products by name or description.

    Args:
        query: Search query
        limit: Maximum results to return

    Returns:
        List of matching products
    """
    query_lower = query.lower()
    results = []

    for category, products in PRODUCTS.items():
        for product in products:
            if (query_lower in product['name'].lower() or
                query_lower in product['description'].lower() or
                query_lower in product['search_term'].lower()):
                results.append({**product, 'category': category})

    return results[:limit]


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Product database queries')
    parser.add_argument(
        '--category',
        help='Filter by category'
    )
    parser.add_argument(
        '--random',
        type=int,
        help='Get N random products'
    )
    parser.add_argument(
        '--search',
        help='Search products by keyword'
    )
    parser.add_argument(
        '--list-categories',
        action='store_true',
        help='List all categories'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    args = parser.parse_args()

    if args.list_categories:
        categories = get_all_categories()
        if args.json:
            print(json.dumps(categories, indent=2))
        else:
            print("Available categories:")
            for cat in categories:
                count = len(PRODUCTS[cat])
                print(f"  - {cat} ({count} products)")
        return 0

    if args.search:
        products = search_products(args.search)
    elif args.random:
        products = get_random_products(args.category, args.random)
    elif args.category:
        products = get_products_by_category(args.category)
    else:
        # Show all products
        products = [
            {**p, 'category': cat}
            for cat, prods in PRODUCTS.items()
            for p in prods
        ]

    if args.json:
        print(json.dumps(products, indent=2))
    else:
        for p in products:
            cat = p.get('category', 'unknown')
            print(f"\n[{cat}] {p['name']}")
            print(f"  Price: {p['price_range']}")
            print(f"  {p['description']}")
            if p.get('asin'):
                print(f"  ASIN: {p['asin']}")

    return 0


if __name__ == "__main__":
    exit(main())
