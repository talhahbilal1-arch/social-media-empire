"""
Lead Magnet PDF Generator

Generates "The Smart Shopper's Guide: 50 Ways to Save + Top Products Under $30"
A comprehensive guide with shopping tips and curated product recommendations.
"""

import os
from datetime import datetime
from pathlib import Path

# Try to import ReportLab, fall back to text-based generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, ListFlowable, ListItem, Image
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not installed. Will generate text version.")


# Brand colors
PRIMARY_COLOR = colors.HexColor("#E85A4F") if REPORTLAB_AVAILABLE else "#E85A4F"
SECONDARY_COLOR = colors.HexColor("#2C3E50") if REPORTLAB_AVAILABLE else "#2C3E50"
ACCENT_COLOR = colors.HexColor("#FF9900") if REPORTLAB_AVAILABLE else "#FF9900"


# Content for the guide
PART1_TIPS = [
    {
        "category": "Spotting Real Deals",
        "tips": [
            "Check the price history using CamelCamelCamel or Keepa browser extensions before buying",
            "Amazon 'List Price' isn't always the real original price - verify independently",
            "Lightning Deals have timers but aren't always the best price - compare first",
            "Subscribe & Save discounts stack with coupons for maximum savings",
            "Warehouse Deals offer like-new items at 20-30% off retail"
        ]
    },
    {
        "category": "Best Times to Buy",
        "tips": [
            "BEAUTY: January (post-holiday clearance) and Prime Day (July)",
            "HOME & DECOR: After-holiday sales (Jan, Nov) and Presidents Day",
            "ORGANIZATION: Back-to-school season (Aug) and New Year (Jan)",
            "ELECTRONICS: Black Friday, Prime Day, and after CES (January)",
            "Year-round: Check prices on Tuesdays - many retailers update then"
        ]
    },
    {
        "category": "Price Tracking Secrets",
        "tips": [
            "Set up CamelCamelCamel price alerts for items on your wishlist",
            "Use Honey or Capital One Shopping for automatic coupon application",
            "Check 'Other Sellers' on Amazon - sometimes cheaper options available",
            "Amazon Outlet has overstock items at significant discounts",
            "Bookmark items and check back on Prime Day and Black Friday"
        ]
    },
    {
        "category": "Coupon Stacking Strategies",
        "tips": [
            "Clip digital coupons on the product page before adding to cart",
            "Subscribe & Save + coupon + sale price = triple savings",
            "Look for 'Buy 2, Save X%' promotions on everyday items",
            "Check brand websites for manufacturer coupons that work on Amazon",
            "Use Amazon credit card for 5% back on all purchases"
        ]
    },
    {
        "category": "Smart Shopping Habits",
        "tips": [
            "Read reviews sorted by 'Most Recent' to catch quality changes",
            "Check the 'Frequently Bought Together' for bundle deals",
            "Compare price-per-unit on household items (it's displayed under the price)",
            "Use Amazon Smile to donate to charity while you shop",
            "Keep items in cart for a few days - sometimes prices drop or coupons appear"
        ]
    }
]

PART2_PRODUCTS = {
    "Beauty Steals Under $30": [
        {
            "name": "CeraVe Moisturizing Cream 16oz",
            "price": "$15.99",
            "rating": "4.7/5 (127,000+ reviews)",
            "why": "Dermatologist-recommended, fragrance-free, great for all skin types",
            "asin": "B00TTD9BRC"
        },
        {
            "name": "Laneige Lip Sleeping Mask",
            "price": "$24.00",
            "rating": "4.6/5 (45,000+ reviews)",
            "why": "Overnight treatment that actually works, multiple flavors",
            "asin": "B07XXPHQZK"
        },
        {
            "name": "The Ordinary Niacinamide 10% + Zinc 1%",
            "price": "$9.80",
            "rating": "4.4/5 (75,000+ reviews)",
            "why": "Targets pores and oil control, incredible value",
            "asin": "B07Q1XFGVJ"
        },
        {
            "name": "Maybelline Lash Sensational Mascara",
            "price": "$8.98",
            "rating": "4.4/5 (95,000+ reviews)",
            "why": "Full fan effect, doesn't clump, drugstore favorite",
            "asin": "B00PFCS8YU"
        },
        {
            "name": "e.l.f. Poreless Putty Primer",
            "price": "$10.00",
            "rating": "4.4/5 (48,000+ reviews)",
            "why": "Tatcha dupe at a fraction of the price",
            "asin": "B07KM1RFY5"
        },
        {
            "name": "NYX Butter Gloss Set",
            "price": "$12.00",
            "rating": "4.5/5 (32,000+ reviews)",
            "why": "Non-sticky formula, great color variety",
            "asin": "B07T7Q9P8Z"
        },
        {
            "name": "Neutrogena Hydro Boost Gel-Cream",
            "price": "$19.97",
            "rating": "4.6/5 (55,000+ reviews)",
            "why": "Lightweight hydration, oil-free formula",
            "asin": "B00NR1YQHM"
        },
        {
            "name": "Real Techniques Makeup Brush Set",
            "price": "$18.99",
            "rating": "4.7/5 (85,000+ reviews)",
            "why": "Professional quality at drugstore prices",
            "asin": "B004TSFBNK"
        },
        {
            "name": "Thayers Witch Hazel Toner",
            "price": "$10.95",
            "rating": "4.6/5 (110,000+ reviews)",
            "why": "Alcohol-free, gentle, cult favorite",
            "asin": "B00016XJ4M"
        },
        {
            "name": "Bioderma Sensibio Micellar Water",
            "price": "$14.99",
            "rating": "4.7/5 (28,000+ reviews)",
            "why": "Gentle makeup remover, French pharmacy staple",
            "asin": "B002XZLAWM"
        }
    ],
    "Home Organization Must-Haves": [
        {
            "name": "SimpleHouseware Stackable Can Rack",
            "price": "$19.87",
            "rating": "4.5/5 (22,000+ reviews)",
            "why": "Instantly organizes pantry, holds 36 cans",
            "asin": "B01CSPWQJ4"
        },
        {
            "name": "Criusia Storage Cubes 8-Pack",
            "price": "$25.99",
            "rating": "4.5/5 (15,000+ reviews)",
            "why": "Fit any cube shelf, foldable when not in use",
            "asin": "B09QMF91LK"
        },
        {
            "name": "SONGMICS Closet Organizer",
            "price": "$26.99",
            "rating": "4.6/5 (18,000+ reviews)",
            "why": "Double your closet space, sturdy construction",
            "asin": "B01LYHV8VY"
        },
        {
            "name": "mDesign Plastic Storage Bins",
            "price": "$24.99",
            "rating": "4.6/5 (12,000+ reviews)",
            "why": "Clear design, perfect for fridge or pantry",
            "asin": "B076B3R3QF"
        },
        {
            "name": "Command Picture Hanging Strips",
            "price": "$13.19",
            "rating": "4.7/5 (95,000+ reviews)",
            "why": "Damage-free hanging, holds up to 16 lbs",
            "asin": "B073XR4X72"
        },
        {
            "name": "IRIS USA Plastic Drawer System",
            "price": "$28.49",
            "rating": "4.7/5 (35,000+ reviews)",
            "why": "Stackable, see-through, perfect for craft supplies",
            "asin": "B005X1FCOK"
        },
        {
            "name": "Joseph Joseph DrawerStore Organizer",
            "price": "$14.99",
            "rating": "4.5/5 (8,000+ reviews)",
            "why": "Tiered design maximizes drawer space",
            "asin": "B00EAYZDDC"
        },
        {
            "name": "DecoBros Stackable Kitchen Cabinet",
            "price": "$22.97",
            "rating": "4.6/5 (25,000+ reviews)",
            "why": "Creates extra shelf space instantly",
            "asin": "B00COCGVIQ"
        },
        {
            "name": "Honey-Can-Do 3-Tier Cart",
            "price": "$29.99",
            "rating": "4.5/5 (15,000+ reviews)",
            "why": "Rolling storage for bathroom, kitchen, or office",
            "asin": "B002OEBMLU"
        },
        {
            "name": "S-hooks and Basket Combo",
            "price": "$18.99",
            "rating": "4.4/5 (5,000+ reviews)",
            "why": "Maximize vertical closet space",
            "asin": "B07DVFDRWY"
        }
    ],
    "Decor Finds That Look Expensive": [
        {
            "name": "KIVIK Throw Pillow Covers",
            "price": "$13.99",
            "rating": "4.5/5 (18,000+ reviews)",
            "why": "Linen look, machine washable, instant room upgrade",
            "asin": "B08HYF4J6N"
        },
        {
            "name": "Mkono Macrame Plant Hanger",
            "price": "$13.99",
            "rating": "4.7/5 (22,000+ reviews)",
            "why": "Boho vibes on a budget",
            "asin": "B071ZMPF6R"
        },
        {
            "name": "Mercury Glass Candle Holders",
            "price": "$15.99",
            "rating": "4.6/5 (8,000+ reviews)",
            "why": "Looks high-end, great as centerpieces",
            "asin": "B01N6V4FAE"
        },
        {
            "name": "Artificial Eucalyptus Garland",
            "price": "$12.99",
            "rating": "4.5/5 (28,000+ reviews)",
            "why": "Realistic look, no maintenance required",
            "asin": "B07F72RCCY"
        },
        {
            "name": "NICETOWN Blackout Curtains",
            "price": "$23.95",
            "rating": "4.6/5 (130,000+ reviews)",
            "why": "Thermal insulated, room darkening, many colors",
            "asin": "B01CSRQGFQ"
        }
    ]
}


def generate_pdf(output_path: str = "smart_shopper_guide.pdf"):
    """Generate the lead magnet PDF using ReportLab."""

    if not REPORTLAB_AVAILABLE:
        return generate_text_version(output_path.replace('.pdf', '.txt'))

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=PRIMARY_COLOR,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=SECONDARY_COLOR,
        alignment=TA_CENTER,
        spaceAfter=30
    )

    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=PRIMARY_COLOR,
        spaceBefore=20,
        spaceAfter=12
    )

    category_style = ParagraphStyle(
        'Category',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=SECONDARY_COLOR,
        spaceBefore=15,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=6,
        leading=14
    )

    product_name_style = ParagraphStyle(
        'ProductName',
        parent=styles['Normal'],
        fontSize=12,
        textColor=SECONDARY_COLOR,
        fontName='Helvetica-Bold'
    )

    elements = []

    # Cover Page
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("💝 Daily Deal Darling Presents", subtitle_style))
    elements.append(Paragraph("The Smart Shopper's Guide", title_style))
    elements.append(Paragraph("50 Ways to Save + Top Products Under $30", subtitle_style))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        "Your complete guide to saving money on beauty, home & decor<br/>"
        "— without sacrificing quality.",
        body_style
    ))
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph(
        f"© {datetime.now().year} Daily Deal Darling<br/>"
        "dailydealdarling.com",
        ParagraphStyle('Footer', parent=body_style, alignment=TA_CENTER, textColor=colors.gray)
    ))
    elements.append(PageBreak())

    # Part 1: Shopping Tips
    elements.append(Paragraph("PART 1", subtitle_style))
    elements.append(Paragraph("25 Money-Saving Tips & Hacks", section_style))
    elements.append(Paragraph(
        "Master these strategies to never overpay again.",
        body_style
    ))
    elements.append(Spacer(1, 0.2*inch))

    tip_number = 1
    for category_data in PART1_TIPS:
        elements.append(Paragraph(f"📌 {category_data['category']}", category_style))

        for tip in category_data['tips']:
            elements.append(Paragraph(
                f"<b>{tip_number}.</b> {tip}",
                body_style
            ))
            tip_number += 1

        elements.append(Spacer(1, 0.1*inch))

    elements.append(PageBreak())

    # Part 2: Product Picks
    elements.append(Paragraph("PART 2", subtitle_style))
    elements.append(Paragraph("25 Top Products Under $30", section_style))
    elements.append(Paragraph(
        "Our editors' favorite finds — all under $30 with stellar reviews.",
        body_style
    ))
    elements.append(Spacer(1, 0.2*inch))

    product_number = 1
    for category, products in PART2_PRODUCTS.items():
        elements.append(Paragraph(f"✨ {category}", category_style))

        for product in products:
            elements.append(Paragraph(
                f"<b>{product_number}. {product['name']}</b>",
                product_name_style
            ))
            elements.append(Paragraph(
                f"💰 {product['price']} | ⭐ {product['rating']}",
                body_style
            ))
            elements.append(Paragraph(
                f"Why we love it: {product['why']}",
                body_style
            ))
            elements.append(Paragraph(
                f"🔗 amazon.com/dp/{product['asin']}?tag=dailydealdarling1-20",
                ParagraphStyle('Link', parent=body_style, textColor=ACCENT_COLOR, fontSize=9)
            ))
            elements.append(Spacer(1, 0.15*inch))
            product_number += 1

    elements.append(PageBreak())

    # Final Page
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph("Thanks for Reading!", title_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(
        "Now you're armed with 50 ways to save on your next shopping trip!<br/><br/>"
        "Want more deals? We send our best finds every Tuesday.<br/>"
        "You're already on the list — check your inbox!",
        body_style
    ))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        "💝 Happy Shopping!<br/>"
        "The Daily Deal Darling Team",
        ParagraphStyle('Signature', parent=body_style, alignment=TA_CENTER, fontSize=12)
    ))
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph(
        "<b>Visit us:</b> dailydealdarling.com<br/>"
        "<b>Follow us:</b> @dailydealdarling on Pinterest",
        ParagraphStyle('Links', parent=body_style, alignment=TA_CENTER)
    ))

    # Build PDF
    doc.build(elements)
    print(f"PDF generated: {output_path}")
    return output_path


def generate_text_version(output_path: str):
    """Generate a text version if ReportLab is not available."""

    content = []
    content.append("=" * 60)
    content.append("THE SMART SHOPPER'S GUIDE")
    content.append("50 Ways to Save + Top Products Under $30")
    content.append("by Daily Deal Darling")
    content.append("=" * 60)
    content.append("")

    content.append("PART 1: 25 MONEY-SAVING TIPS & HACKS")
    content.append("-" * 40)

    tip_number = 1
    for category_data in PART1_TIPS:
        content.append(f"\n📌 {category_data['category']}")
        for tip in category_data['tips']:
            content.append(f"  {tip_number}. {tip}")
            tip_number += 1

    content.append("\n")
    content.append("PART 2: 25 TOP PRODUCTS UNDER $30")
    content.append("-" * 40)

    product_number = 1
    for category, products in PART2_PRODUCTS.items():
        content.append(f"\n✨ {category}")
        for product in products:
            content.append(f"\n  {product_number}. {product['name']}")
            content.append(f"     Price: {product['price']} | Rating: {product['rating']}")
            content.append(f"     Why: {product['why']}")
            content.append(f"     Link: amazon.com/dp/{product['asin']}?tag=dailydealdarling1-20")
            product_number += 1

    content.append("\n")
    content.append("=" * 60)
    content.append("Thanks for reading! Check your inbox for weekly deals.")
    content.append("Visit: dailydealdarling.com")
    content.append("=" * 60)

    Path(output_path).write_text("\n".join(content))
    print(f"Text version generated: {output_path}")
    return output_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate lead magnet PDF')
    parser.add_argument(
        '--output',
        default='lead_magnets/smart_shopper_guide.pdf',
        help='Output file path'
    )

    args = parser.parse_args()

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    generate_pdf(str(output_path))


if __name__ == "__main__":
    main()
