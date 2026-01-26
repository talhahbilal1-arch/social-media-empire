"""
Lead Magnet PDF Generator - Premium Edition

Generates "The Smart Shopper's Ultimate Guide"
A comprehensive 30+ page guide with shopping strategies, seasonal calendars,
budget planning tools, product recommendations, and insider secrets.

This is designed to provide REAL value that helps readers save hundreds of dollars.
"""

import os
from datetime import datetime
from pathlib import Path

# Try to import ReportLab
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, ListFlowable, ListItem, KeepTogether, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not installed. Run: pip install reportlab")


# =============================================================================
# BRAND COLORS
# =============================================================================
if REPORTLAB_AVAILABLE:
    PRIMARY = colors.HexColor("#E85A4F")      # Coral/salmon
    SECONDARY = colors.HexColor("#2C3E50")    # Dark blue-gray
    ACCENT = colors.HexColor("#FF9900")       # Amazon orange
    SUCCESS = colors.HexColor("#27AE60")      # Green for savings
    LIGHT_BG = colors.HexColor("#FDF8F5")     # Cream background
    DARK_TEXT = colors.HexColor("#333333")    # Body text
    MUTED = colors.HexColor("#7F8C8D")        # Gray text


# =============================================================================
# COMPREHENSIVE CONTENT
# =============================================================================

INTRODUCTION = """
Welcome to the Smart Shopper's Ultimate Guide! Whether you're looking to stretch your budget,
find hidden deals, or simply make smarter purchasing decisions, this guide is your comprehensive
resource for saving money without sacrificing quality.

Inside these pages, you'll discover:
• 50+ proven strategies to save 30-70% on everyday purchases
• The psychology behind pricing (and how stores trick you)
• A month-by-month shopping calendar for the best prices
• Budget tracking templates and goal-setting worksheets
• 30 hand-picked product recommendations with honest reviews
• Insider tips that most shoppers never learn

This isn't just another list of "money-saving tips." This is a complete system for
transforming how you shop — backed by research, real data, and years of deal-hunting expertise.

Ready to start saving? Let's dive in.
"""

# Part 1: Understanding Retail Psychology
PSYCHOLOGY_SECTION = {
    "title": "The Psychology of Pricing: What Stores Don't Want You to Know",
    "intro": """Before we get into specific tips, it's crucial to understand HOW stores
manipulate your purchasing decisions. Once you see these tactics, you'll never shop
the same way again.""",
    "tactics": [
        {
            "name": "The Decoy Effect",
            "explanation": """Stores often place a clearly inferior option next to what they
want you to buy. Example: A $50 product seems reasonable when placed next to a $200
"premium" version that offers almost nothing extra.""",
            "defense": "Always compare products based on YOUR needs, not relative to other options on the shelf."
        },
        {
            "name": "Artificial Urgency",
            "explanation": """'Only 3 left!' 'Sale ends tonight!' These messages trigger
fear of missing out (FOMO). In reality, most sales repeat regularly, and stock
messages are often fabricated or refreshed.""",
            "defense": "Never make a purchase decision based on urgency alone. If it's a good deal today, a similar deal will come again."
        },
        {
            "name": "Charm Pricing",
            "explanation": """$19.99 vs $20.00 — we perceive the first as significantly
cheaper even though it's just a penny less. Our brains process left-to-right,
anchoring on the first digit.""",
            "defense": "Round up all prices mentally. $19.99 is $20. This small shift changes your perception entirely."
        },
        {
            "name": "The Anchor Price",
            "explanation": """When you see 'Was $100, Now $60!' your brain anchors to
$100 as the 'real' value. But that anchor price may be inflated or rarely
charged. Some retailers raise prices before sales just to show bigger discounts.""",
            "defense": "Use price tracking tools (covered later) to see ACTUAL historical prices, not manufactured 'original' prices."
        },
        {
            "name": "Bundle Confusion",
            "explanation": """Buy 3 for $15 sounds like a deal, but is it? If one item
is $5.50 normally, you're actually paying MORE for the bundle. Stores count on
you not doing the math.""",
            "defense": "Always calculate the per-unit price. Most stores are required to display this — look for it!"
        },
        {
            "name": "Strategic Store Layout",
            "explanation": """Essential items (milk, bread, toiletries) are placed at the
back of the store, forcing you to walk past tempting impulse items. End caps
and eye-level shelves feature higher-margin products, not the best deals.""",
            "defense": "Make a list and stick to it. Shop the perimeter first. Look high and low on shelves — the best values are often not at eye level."
        }
    ]
}

# Part 2: The 50 Strategies
STRATEGIES = [
    {
        "category": "Before You Buy: Research Phase",
        "icon": "🔍",
        "strategies": [
            {
                "title": "The 24-Hour Rule",
                "description": "For any non-essential purchase over $30, wait 24 hours before buying. This simple pause eliminates 70%+ of impulse purchases and lets you research better deals.",
                "savings": "$500-2,000/year"
            },
            {
                "title": "Price History is Everything",
                "description": "Install CamelCamelCamel (Amazon) or Keepa browser extensions. They show you the REAL price history of any product, revealing if that 'sale' is actually a good deal or if the price was lower last month.",
                "savings": "15-40% per purchase"
            },
            {
                "title": "The Review Deep-Dive",
                "description": "Don't just check the star rating. Sort reviews by 'Most Recent' to catch quality changes. Read 3-star reviews — they're often the most balanced and honest. Look for reviews with photos.",
                "savings": "Avoid costly mistakes"
            },
            {
                "title": "Find the Real Best-Seller",
                "description": "Amazon's 'Best Seller' badge can be bought through promotions. Instead, use Jungle Scout's free estimator or check Fakespot.com to verify review authenticity before trusting rankings.",
                "savings": "Avoid overpriced items"
            },
            {
                "title": "Compare Across Platforms",
                "description": "Don't assume Amazon has the best price. Check Google Shopping, Walmart, Target, and the manufacturer's own website. Many brands offer better deals direct or exclusive coupon codes.",
                "savings": "10-30% per purchase"
            },
            {
                "title": "Read the Negative Reviews First",
                "description": "5-star reviews are often incentivized. 1-star reviews reveal deal-breakers: quality issues, sizing problems, or misleading descriptions that might affect you.",
                "savings": "Avoid returns/regret"
            }
        ]
    },
    {
        "category": "Amazon Mastery",
        "icon": "📦",
        "strategies": [
            {
                "title": "Subscribe & Save Stacking",
                "description": "Subscribe & Save gives 5-15% off recurring items. Stack this with: digital coupons, promotions, and getting 5+ items in one delivery (extra 15% off). Cancel after first delivery if needed.",
                "savings": "20-35% on household items"
            },
            {
                "title": "Amazon Warehouse Secrets",
                "description": "Amazon Warehouse sells returns and open-box items at 20-50% off. Items marked 'Like New' are often untouched returns. Filter any category by 'Amazon Warehouse' in the seller options.",
                "savings": "20-50% off retail"
            },
            {
                "title": "Price Drop Refunds",
                "description": "Amazon doesn't advertise this: if an item drops in price within 7 days of delivery, contact support for a refund of the difference. Works for most products.",
                "savings": "Variable, often $10-50"
            },
            {
                "title": "The Coupon Page",
                "description": "Visit amazon.com/coupons daily. Digital coupons for products you actually need appear here. Clip before searching — many coupons don't show on product pages directly.",
                "savings": "5-50% per item"
            },
            {
                "title": "Lightning Deals Strategy",
                "description": "Lightning Deals are time-limited but not always the best price. Set CamelCamelCamel alerts on items you want — you'll know if the Lightning Deal is truly exceptional.",
                "savings": "Know when to skip"
            },
            {
                "title": "Prime Day Preparation",
                "description": "Start a wishlist 2-3 weeks before Prime Day. Watch prices leading up — some items are raised then 'discounted.' The best deals: Amazon devices, fashion, and select electronics.",
                "savings": "40-60% on Prime Day"
            },
            {
                "title": "Other Sellers Check",
                "description": "Below 'Add to Cart' is 'Other Sellers.' Third-party sellers often beat Amazon's price for the same new item. Check seller ratings (95%+ with 1000+ reviews is safe).",
                "savings": "10-25% difference"
            },
            {
                "title": "Amazon Outlet",
                "description": "amazon.com/outlet has overstock items at steep discounts. Categories include home, fashion, electronics, and more. Stock rotates frequently — check weekly.",
                "savings": "30-70% off"
            }
        ]
    },
    {
        "category": "Coupon Stacking & Cashback",
        "icon": "💰",
        "strategies": [
            {
                "title": "The Triple Stack",
                "description": "Combine: (1) store sale/promotion + (2) manufacturer coupon + (3) cashback app. Example: Target 20% off + $2 coupon + 5% Ibotta = 35%+ savings on a single item.",
                "savings": "30-50% regularly"
            },
            {
                "title": "Cashback App Arsenal",
                "description": "Use multiple apps: Rakuten (online), Ibotta (groceries), Fetch (any receipt), Shopkick (retail). These don't overlap — you can use ALL of them on the same purchases.",
                "savings": "$300-600/year"
            },
            {
                "title": "Credit Card Strategy",
                "description": "Use category cards: 5% on groceries (Amex BCP), 5% on Amazon (Prime card), 3% on dining (various). Never carry a balance — interest destroys savings.",
                "savings": "$500-1,500/year"
            },
            {
                "title": "Browser Extensions That Work",
                "description": "Install: Honey (auto-applies coupons), Capital One Shopping (price comparison), RetailMeNot (additional codes). They run automatically — set and forget.",
                "savings": "$200-500/year"
            },
            {
                "title": "Manufacturer Rebates",
                "description": "Many brands offer mail-in or digital rebates on their websites. Check before buying: P&G, Unilever, and beauty brands regularly offer $5-15 rebates on purchases.",
                "savings": "$50-200/year"
            },
            {
                "title": "Store Loyalty Stacking",
                "description": "Join free loyalty programs at every store you shop. Combine member pricing + digital coupons + fuel points + birthday rewards. CVS ExtraCare and Target Circle are goldmines.",
                "savings": "15-25% at each store"
            }
        ]
    },
    {
        "category": "Beauty & Skincare Savings",
        "icon": "💄",
        "strategies": [
            {
                "title": "Samples Before Full-Size",
                "description": "Never buy full-size skincare without trying it. Request samples at Sephora/Ulta, buy sample sizes on Amazon, or use subscription boxes like Ipsy ($14/month) to test products.",
                "savings": "Avoid $30-100 mistakes"
            },
            {
                "title": "Ulta vs. Sephora Timing",
                "description": "Ulta: 21 Days of Beauty (March/Sept) offers 50% off prestige brands daily. Sephora: VIB Sales (April/Nov) give 15-20% off everything including luxury brands.",
                "savings": "30-50% on prestige"
            },
            {
                "title": "Drugstore Dupes Database",
                "description": "Use Temptalia.com or Reddit's r/MakeupAddiction for proven drugstore duplicates of high-end products. e.l.f., NYX, and ColourPop routinely match $40+ products.",
                "savings": "70-80% vs. high-end"
            },
            {
                "title": "The Ordinary Strategy",
                "description": "The Ordinary offers clinical-grade skincare at 70-80% less than competitors. Their Niacinamide ($6) rivals products costing $50+. Buy direct for best pricing.",
                "savings": "$200-500/year"
            },
            {
                "title": "Return Policy Leverage",
                "description": "Sephora and Ulta have generous return policies. If a product breaks you out or doesn't work, return it (with receipt) within 30-60 days. Don't suffer through bad products.",
                "savings": "Get your money back"
            },
            {
                "title": "GWP (Gift With Purchase) Hunting",
                "description": "Department stores and Sephora regularly offer gift-with-purchase deals worth $50-150 in samples. Time your restocks around these promotions.",
                "savings": "$100-300/year in free products"
            }
        ]
    },
    {
        "category": "Home & Decor Strategies",
        "icon": "🏠",
        "strategies": [
            {
                "title": "The Furniture Cycle",
                "description": "Furniture is cheapest in January (post-holiday clearance) and August (new inventory arriving). Presidents Day and Labor Day sales are legitimate 30-50% off events.",
                "savings": "30-50% on furniture"
            },
            {
                "title": "Floor Model Negotiation",
                "description": "Always ask about floor models and open-box items. Negotiate 15-25% off for minor wear. This works at: West Elm, Pottery Barn, furniture stores, and even Best Buy.",
                "savings": "15-30% off"
            },
            {
                "title": "Target Clearance Endcaps",
                "description": "Target clearance goes: 30% → 50% → 70% off. Check endcaps weekly for home items. The Target app shows clearance percentages — use it in-store.",
                "savings": "50-70% off decor"
            },
            {
                "title": "HomeGoods/TJ Maxx Timing",
                "description": "New inventory arrives Tuesday-Thursday at most locations. Shop mid-week for best selection. Check back weekly — inventory rotates constantly.",
                "savings": "40-60% vs. retail"
            },
            {
                "title": "Wayfair Way Day",
                "description": "Wayfair's biggest sale (April/October) offers 60-80% off. Sign up for emails beforehand — they send early access links. Open-box deals go up to 70% off year-round.",
                "savings": "50-80% during sales"
            },
            {
                "title": "Facebook Marketplace Staging",
                "description": "Home stagers and interior designers resell gently-used staging furniture at 50-80% off retail. Filter by 'new' or 'like new' condition. Many items were used for photos only.",
                "savings": "50-80% off retail"
            }
        ]
    },
    {
        "category": "Grocery & Household Essentials",
        "icon": "🛒",
        "strategies": [
            {
                "title": "Loss Leader Strategy",
                "description": "Stores advertise items at or below cost to get you in the door. Buy ONLY the loss leaders from each store's weekly ad. Don't buy other items — that's how they profit.",
                "savings": "$50-100/month"
            },
            {
                "title": "Unit Price Dominance",
                "description": "Always compare unit prices (per oz, per count). Bigger isn't always cheaper. Store brands are often 30-50% less than name brands for identical quality.",
                "savings": "25-40% on groceries"
            },
            {
                "title": "The Freezer Strategy",
                "description": "When items hit rock-bottom prices, buy extra and freeze. Meat, bread, butter, cheese, and many vegetables freeze well for months. Stock up during sales.",
                "savings": "$100-200/month"
            },
            {
                "title": "Imperfect Produce Services",
                "description": "Companies like Misfits Market and Imperfect Foods sell 'ugly' produce at 30-50% off. Quality is identical — just cosmetically imperfect.",
                "savings": "30-50% on produce"
            },
            {
                "title": "Costco Math",
                "description": "Costco isn't always cheapest. Great buys: rotisserie chicken, organic eggs, Kirkland products, diapers, toilet paper. Skip: produce (spoilage), snacks (overeating).",
                "savings": "20-40% on select items"
            },
            {
                "title": "Digital Coupon Preloading",
                "description": "Load digital coupons to your store loyalty card BEFORE shopping. Kroger, Safeway, and CVS apps have dozens of coupons that apply automatically at checkout.",
                "savings": "$20-50/trip"
            }
        ]
    },
    {
        "category": "Seasonal & Holiday Shopping",
        "icon": "🎄",
        "strategies": [
            {
                "title": "Black Friday Reality Check",
                "description": "Many 'Black Friday' deals are on inferior models made cheaply for the sale. Focus on: Amazon devices, TVs from major brands, and doorbuster toys. Skip: clothing, kitchen gadgets.",
                "savings": "Avoid bad 'deals'"
            },
            {
                "title": "After-Holiday Goldmine",
                "description": "December 26-31: holiday decor goes 50-75% off. January: winter clothing clearance hits 70-80%. Buy next year's gifts and wardrobe at maximum discount.",
                "savings": "50-80% on seasonal"
            },
            {
                "title": "Summer Clearance Windows",
                "description": "July-August: outdoor furniture, grills, and summer items go 50-70% off. Buy for next year. Air conditioners and fans are cheapest in September-October.",
                "savings": "50-70% on outdoor"
            },
            {
                "title": "Back-to-School for Adults",
                "description": "August back-to-school sales include: laptops, electronics, organization, and office supplies. These deals rival Black Friday for computers and tablets.",
                "savings": "20-40% on electronics"
            },
            {
                "title": "Valentine's Day Aftermath",
                "description": "February 15: chocolate, candy, and Valentine's decor goes 50-90% off. Stock up on premium chocolate for months. Heart-shaped items work for any occasion.",
                "savings": "50-90% on sweets"
            },
            {
                "title": "The Quiet Months",
                "description": "March, September, and October are retail's slowest months. Stores offer promotions to drive traffic. Sign up for emails — you'll get exclusive 20-30% off codes.",
                "savings": "20-30% during lulls"
            }
        ]
    },
    {
        "category": "Advanced Money-Saving Techniques",
        "icon": "🧠",
        "strategies": [
            {
                "title": "Price Adjustment Requests",
                "description": "Most stores honor price adjustments 7-14 days after purchase. If something goes on sale, bring your receipt for a refund of the difference. Works at: Target, Nordstrom, Kohl's, most department stores.",
                "savings": "Get sale prices retroactively"
            },
            {
                "title": "Birthday Month Maximization",
                "description": "Sign up for loyalty programs before your birthday. Many offer significant rewards: Sephora ($10-20), Ulta ($10 + 2x points), Panera (free pastry), Starbucks (free drink), DSW ($5).",
                "savings": "$50-100 in birthday freebies"
            },
            {
                "title": "The Abandoned Cart Trick",
                "description": "Add items to your cart at smaller retailers, then leave. Many will email you a 10-15% discount within 24-48 hours to complete your purchase.",
                "savings": "10-15% off"
            },
            {
                "title": "Student/Teacher/Military Discounts",
                "description": "Many retailers offer 10-20% off for students, teachers, nurses, military, and first responders. Always ask at checkout. Verify through ID.me for online discounts.",
                "savings": "10-20% off always"
            },
            {
                "title": "Chat Support Haggling",
                "description": "If you find a lower price elsewhere, use chat support to ask for a price match. Many retailers (Best Buy, Target, Walmart) will match competitors. Be polite and have proof ready.",
                "savings": "Match lowest prices"
            },
            {
                "title": "Email List Optimization",
                "description": "Create a dedicated email for shopping signups. Most brands offer 10-20% off your first purchase for subscribing. Some (Anthropologie, J.Crew) offer 15% regularly.",
                "savings": "10-20% on first orders"
            }
        ]
    }
]

# Part 3: Monthly Shopping Calendar
SHOPPING_CALENDAR = {
    "January": {
        "best_buys": ["Winter clothing (70-80% off)", "Fitness equipment", "Bedding & linens", "Holiday decor (90% off)"],
        "avoid": ["Spring clothing (full price)", "Valentine's items (markup)"],
        "events": "White sales at department stores, New Year's resolution sales"
    },
    "February": {
        "best_buys": ["Winter clothing (final clearance)", "TVs (Super Bowl)", "Chocolate/candy (after 14th)"],
        "avoid": ["Jewelry (Valentine's markup)", "Roses and flowers"],
        "events": "Presidents Day sales (mattresses, furniture, appliances)"
    },
    "March": {
        "best_buys": ["Frozen foods (Frozen Food Month)", "Luggage", "Winter sports gear (end of season)"],
        "avoid": ["Spring break travel items", "Easter candy (full price)"],
        "events": "Ulta 21 Days of Beauty (50% off daily deals)"
    },
    "April": {
        "best_buys": ["Spring cleaning supplies", "Easter candy (after holiday)", "Tax software"],
        "avoid": ["Lawn equipment (wait)", "Spring decor (full price)"],
        "events": "Wayfair Way Day, Sephora Spring Sale"
    },
    "May": {
        "best_buys": ["Mattresses (Memorial Day)", "Appliances", "Spring clothing (clearance)"],
        "avoid": ["Summer items (full price)", "Flowers (Mother's Day markup)"],
        "events": "Memorial Day sales across most retailers"
    },
    "June": {
        "best_buys": ["Tools (Father's Day deals)", "Gym memberships", "Lingerie (semi-annual sales)"],
        "avoid": ["Outdoor furniture (peak)", "Swimwear (full price)"],
        "events": "Nordstrom Half-Yearly Sale, Victoria's Secret Semi-Annual"
    },
    "July": {
        "best_buys": ["Summer clothing (clearance)", "Furniture (floor models)", "Home items (Prime Day)"],
        "avoid": ["Back-to-school items (wait)", "New fall items (full price)"],
        "events": "Amazon Prime Day (mid-July), competing retailer sales"
    },
    "August": {
        "best_buys": ["Outdoor furniture (70% off)", "Grills (clearance)", "Laptops/computers (back-to-school)"],
        "avoid": ["Fall clothing (full price)", "Halloween items (markup)"],
        "events": "Back-to-school sales everywhere"
    },
    "September": {
        "best_buys": ["Lawn equipment (end of season)", "Cars (new model year)", "Summer items (90% off)"],
        "avoid": ["New tech (wait for holiday sales)", "Fall decor (full price)"],
        "events": "Labor Day sales, Ulta 21 Days of Beauty"
    },
    "October": {
        "best_buys": ["Denim (Columbus Day)", "Outdoor paint", "Early Halloween costumes"],
        "avoid": ["Candy (after Halloween is better)", "New holiday items"],
        "events": "Wayfair Way Day, Columbus Day sales"
    },
    "November": {
        "best_buys": ["Almost everything (Black Friday/Cyber Monday)", "TVs", "Toys (best selection)"],
        "avoid": ["Gift cards (no discount)", "Winter clothing (wait for post-holiday)"],
        "events": "Black Friday, Cyber Monday, Sephora VIB Sale"
    },
    "December": {
        "best_buys": ["Last-minute gift deals", "Holiday decor (late month)", "Gift cards (bonus offers)"],
        "avoid": ["Most items (wait for post-holiday)", "Shipping (delays)"],
        "events": "Green Monday (2nd Monday), post-Christmas clearance starts 12/26"
    }
}

# Part 4: Product Recommendations
PRODUCT_RECOMMENDATIONS = {
    "Beauty Essentials That Actually Work": [
        {
            "name": "CeraVe Moisturizing Cream (16 oz)",
            "price": "$15.99",
            "stars": "4.7/5",
            "reviews": "127,000+",
            "why": "Dermatologist-developed with ceramides and hyaluronic acid. Works for face AND body, all skin types. The rare product that lives up to the hype.",
            "best_for": "Daily moisturizer for everyone",
            "asin": "B00TTD9BRC"
        },
        {
            "name": "The Ordinary Niacinamide 10% + Zinc 1%",
            "price": "$5.80",
            "stars": "4.4/5",
            "reviews": "75,000+",
            "why": "Clinical-strength formula rivals serums costing $50+. Reduces pore appearance, controls oil, and helps with acne. Best budget skincare investment.",
            "best_for": "Oily/combination skin, acne-prone",
            "asin": "B07Q1XFGVJ"
        },
        {
            "name": "Laneige Lip Sleeping Mask",
            "price": "$24.00",
            "stars": "4.6/5",
            "reviews": "45,000+",
            "why": "TikTok-famous for a reason. One jar lasts 6+ months. Apply before bed, wake up with baby-soft lips. The Berry scent is the original bestseller.",
            "best_for": "Dry, chapped lips",
            "asin": "B07XXPHQZK"
        },
        {
            "name": "Neutrogena Hydro Boost Gel-Cream",
            "price": "$19.97",
            "stars": "4.6/5",
            "reviews": "55,000+",
            "why": "Oil-free, lightweight, layers beautifully under makeup. The hyaluronic acid formula provides 48-hour hydration without feeling heavy.",
            "best_for": "Oily skin, makeup wearers",
            "asin": "B00NR1YQHM"
        },
        {
            "name": "e.l.f. Poreless Putty Primer",
            "price": "$10.00",
            "stars": "4.4/5",
            "reviews": "48,000+",
            "why": "A near-perfect dupe for Tatcha Silk Canvas ($52). Same bouncy, pore-blurring texture. Makes makeup last all day.",
            "best_for": "Makeup prep, large pores",
            "asin": "B07KM1RFY5"
        },
        {
            "name": "Thayers Witch Hazel Toner",
            "price": "$10.95",
            "stars": "4.6/5",
            "reviews": "110,000+",
            "why": "Alcohol-free, gentle, and effective. The Rose Petal scent is cult-favorite. Tightens pores, soothes skin, and removes residual cleanser.",
            "best_for": "All skin types, especially sensitive",
            "asin": "B00016XJ4M"
        },
        {
            "name": "Real Techniques Makeup Brush Set",
            "price": "$18.99",
            "stars": "4.7/5",
            "reviews": "85,000+",
            "why": "Professional-quality brushes at a drugstore price. Soft, doesn't shed, and the Everyday Essentials set covers all bases.",
            "best_for": "Beginners and pros alike",
            "asin": "B004TSFBNK"
        },
        {
            "name": "Maybelline Lash Sensational Mascara",
            "price": "$8.98",
            "stars": "4.4/5",
            "reviews": "95,000+",
            "why": "The fanned-out lash effect rivals high-end mascaras. Buildable, doesn't clump, and removes easily. The drugstore mascara experts swear by.",
            "best_for": "Natural to dramatic lashes",
            "asin": "B00PFCS8YU"
        },
        {
            "name": "Bioderma Sensibio Micellar Water",
            "price": "$14.99",
            "stars": "4.7/5",
            "reviews": "28,000+",
            "why": "The original micellar water, loved by French women and makeup artists worldwide. Removes makeup gently without rinsing.",
            "best_for": "Makeup removal, sensitive skin",
            "asin": "B002XZLAWM"
        },
        {
            "name": "Paula's Choice 2% BHA Exfoliant",
            "price": "$29.50",
            "stars": "4.6/5",
            "reviews": "12,000+",
            "why": "The gold standard for chemical exfoliation. Unclogs pores, smooths texture, and fades dark spots. Worth every penny.",
            "best_for": "Blackheads, texture, anti-aging",
            "asin": "B00949CTQQ"
        }
    ],
    "Home Organization Game-Changers": [
        {
            "name": "SimpleHouseware Stackable Can Rack Organizer",
            "price": "$19.87",
            "stars": "4.5/5",
            "reviews": "22,000+",
            "why": "Instantly transforms a chaotic pantry. Holds 36 cans, FIFO design means older cans come out first. The 'before and after' photos don't lie.",
            "best_for": "Pantry organization",
            "asin": "B01CSPWQJ4"
        },
        {
            "name": "SONGMICS Closet Organizer System",
            "price": "$26.99",
            "stars": "4.6/5",
            "reviews": "18,000+",
            "why": "Doubles your closet space without renovation. Adjustable shelves and hanging rod fit any closet. Takes 15 minutes to install.",
            "best_for": "Small closets, apartments",
            "asin": "B01LYHV8VY"
        },
        {
            "name": "mDesign Clear Plastic Storage Bins (Set of 4)",
            "price": "$24.99",
            "stars": "4.6/5",
            "reviews": "12,000+",
            "why": "See-through design means no more forgotten items. Perfect for fridge, pantry, or under-sink organization. Stackable and durable.",
            "best_for": "Fridge, pantry, bathroom",
            "asin": "B076B3R3QF"
        },
        {
            "name": "IRIS USA Plastic Drawer Tower (4 Drawers)",
            "price": "$28.49",
            "stars": "4.7/5",
            "reviews": "35,000+",
            "why": "Craft room favorite for a reason. Clear drawers show contents, smooth gliding, stackable. Works anywhere: closet, office, bathroom.",
            "best_for": "Craft supplies, office, anywhere",
            "asin": "B005X1FCOK"
        },
        {
            "name": "Command Picture Hanging Strips",
            "price": "$13.19",
            "stars": "4.7/5",
            "reviews": "95,000+",
            "why": "No holes, no damage, holds up to 16 lbs. Essential for renters. Gallery walls made easy. Removes cleanly when you move.",
            "best_for": "Renters, wall decor",
            "asin": "B073XR4X72"
        },
        {
            "name": "Honey-Can-Do 3-Tier Rolling Cart",
            "price": "$29.99",
            "stars": "4.5/5",
            "reviews": "15,000+",
            "why": "Versatile storage that moves where you need it. Works in bathroom (toiletries), kitchen (produce), craft room (supplies), or office.",
            "best_for": "Multi-purpose mobile storage",
            "asin": "B002OEBMLU"
        },
        {
            "name": "Joseph Joseph DrawerStore Organizer",
            "price": "$14.99",
            "stars": "4.5/5",
            "reviews": "8,000+",
            "why": "Tiered design means you see everything in the drawer at once. Expandable to fit different drawer sizes. Kitchen drawer essential.",
            "best_for": "Kitchen utensil drawers",
            "asin": "B00EAYZDDC"
        },
        {
            "name": "Criusia Fabric Storage Cubes (8-Pack)",
            "price": "$25.99",
            "stars": "4.5/5",
            "reviews": "15,000+",
            "why": "Fit standard cube shelves perfectly. Foldable when not in use, reinforced handles, tons of color options. The best value in storage cubes.",
            "best_for": "Cube shelves, closets, toys",
            "asin": "B09QMF91LK"
        },
        {
            "name": "DecoBros Stackable Kitchen Cabinet Organizer",
            "price": "$22.97",
            "stars": "4.6/5",
            "reviews": "25,000+",
            "why": "Creates extra shelf space inside cabinets. No more stacking dishes or losing spices in the back. Expandable width.",
            "best_for": "Kitchen cabinets, pantry",
            "asin": "B00COCGVIQ"
        },
        {
            "name": "Amazon Basics Velvet Hangers (50-Pack)",
            "price": "$24.99",
            "stars": "4.8/5",
            "reviews": "200,000+",
            "why": "Non-slip velvet coating keeps clothes in place. Slim profile fits 2x more in your closet. The closet upgrade with the biggest impact.",
            "best_for": "Closet maximization",
            "asin": "B0758C7J39"
        }
    ],
    "Decor That Looks 3x the Price": [
        {
            "name": "KIVIK Linen Throw Pillow Covers (Set of 4)",
            "price": "$13.99",
            "stars": "4.5/5",
            "reviews": "18,000+",
            "why": "High-end linen look for under $4/pillow. Machine washable, hidden zipper, neutral colors that match everything. Instant room upgrade.",
            "best_for": "Living room, bedroom refresh",
            "asin": "B08HYF4J6N"
        },
        {
            "name": "Mkono Macrame Plant Hangers (Set of 3)",
            "price": "$13.99",
            "stars": "4.7/5",
            "reviews": "22,000+",
            "why": "Boho-chic style on a budget. Handmade look, sturdy cotton rope, three different lengths. Adds dimension and greenery to any room.",
            "best_for": "Plants, boho decor",
            "asin": "B071ZMPF6R"
        },
        {
            "name": "NICETOWN Blackout Curtains",
            "price": "$23.95",
            "stars": "4.6/5",
            "reviews": "130,000+",
            "why": "Room-darkening, thermal-insulated, and available in 50+ colors. Looks custom. Saves on heating/cooling costs too.",
            "best_for": "Bedrooms, living room, energy savings",
            "asin": "B01CSRQGFQ"
        },
        {
            "name": "Artificial Eucalyptus Garland",
            "price": "$12.99",
            "stars": "4.5/5",
            "reviews": "28,000+",
            "why": "Drape over mirrors, mantels, or table centerpieces. Incredibly realistic — guests will think it's real. Zero maintenance.",
            "best_for": "Mantels, weddings, everyday decor",
            "asin": "B07F72RCCY"
        },
        {
            "name": "Mercury Glass Votive Candle Holders (Set of 12)",
            "price": "$15.99",
            "stars": "4.6/5",
            "reviews": "8,000+",
            "why": "That expensive 'antiqued glass' look for $1.33 each. Perfect for tablescapes, mantels, or bathroom decor. Wedding planner favorite.",
            "best_for": "Ambiance, centerpieces, events",
            "asin": "B01N6V4FAE"
        },
        {
            "name": "Adeco Decorative Round Metal Wall Mirror",
            "price": "$29.99",
            "stars": "4.6/5",
            "reviews": "3,500+",
            "why": "That trendy circular mirror look for a fraction of the designer price. Opens up small spaces, adds light and dimension.",
            "best_for": "Entryway, bathroom, small rooms",
            "asin": "B08QHQN2SX"
        },
        {
            "name": "Ceramic White Vases (Set of 3)",
            "price": "$22.99",
            "stars": "4.6/5",
            "reviews": "5,000+",
            "why": "Minimalist white ceramic that works with any style. Different heights create visual interest. Display flowers or stand alone.",
            "best_for": "Mantel styling, minimalist decor",
            "asin": "B08G8H7Y3K"
        },
        {
            "name": "LED Flameless Candles with Timer (Set of 6)",
            "price": "$19.99",
            "stars": "4.5/5",
            "reviews": "35,000+",
            "why": "Realistic flickering, auto on/off timer, safe around kids and pets. Real wax exterior feels authentic. No more melted wax cleanup.",
            "best_for": "Ambiance without fire risk",
            "asin": "B07L3K5QYD"
        },
        {
            "name": "Woven Seagrass Basket Set",
            "price": "$26.99",
            "stars": "4.6/5",
            "reviews": "4,500+",
            "why": "That expensive coastal/boho look for cheap. Use as plant covers, storage, or blanket baskets. Natural texture adds warmth.",
            "best_for": "Plants, storage, texture",
            "asin": "B08QRJ3XWD"
        },
        {
            "name": "Umbra Trigg Wall Planters (Set of 2)",
            "price": "$24.00",
            "stars": "4.5/5",
            "reviews": "7,000+",
            "why": "Modern geometric design makes any wall Instagram-worthy. Ceramic vessels in brass or copper wire frames. Easy to hang.",
            "best_for": "Modern plant display, small spaces",
            "asin": "B017DPXMR0"
        }
    ]
}

# Bonus Section: Budget Tracker
BUDGET_WORKSHEET = """
MONTHLY SHOPPING BUDGET TRACKER

Category             | Budget | Spent | Saved | Notes
--------------------|--------|-------|-------|------------------
Groceries           | $      | $     | $     |
Beauty & Personal   | $      | $     | $     |
Clothing            | $      | $     | $     |
Home & Decor        | $      | $     | $     |
Entertainment       | $      | $     | $     |
Gifts               | $      | $     | $     |
Miscellaneous       | $      | $     | $     |
--------------------|--------|-------|-------|------------------
TOTAL               | $      | $     | $     |

SAVINGS GOAL THIS MONTH: $________

DEALS WAITING FOR:
1. _________________________________
2. _________________________________
3. _________________________________

UPCOMING SALES TO WATCH:
□ _________________________________
□ _________________________________
□ _________________________________
"""


def create_styles():
    """Create custom paragraph styles."""
    styles = getSampleStyleSheet()

    custom_styles = {
        'CoverTitle': ParagraphStyle(
            'CoverTitle',
            parent=styles['Title'],
            fontSize=36,
            textColor=PRIMARY,
            alignment=TA_CENTER,
            spaceAfter=12,
            leading=42
        ),
        'CoverSubtitle': ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontSize=18,
            textColor=SECONDARY,
            alignment=TA_CENTER,
            spaceAfter=8
        ),
        'ChapterTitle': ParagraphStyle(
            'ChapterTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=PRIMARY,
            spaceBefore=30,
            spaceAfter=16,
            alignment=TA_LEFT
        ),
        'SectionTitle': ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=SECONDARY,
            spaceBefore=20,
            spaceAfter=12
        ),
        'SubsectionTitle': ParagraphStyle(
            'SubsectionTitle',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=PRIMARY,
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ),
        'BodyText': ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontSize=11,
            textColor=DARK_TEXT,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=16
        ),
        'Quote': ParagraphStyle(
            'Quote',
            parent=styles['Normal'],
            fontSize=12,
            textColor=SECONDARY,
            leftIndent=20,
            rightIndent=20,
            spaceBefore=10,
            spaceAfter=10,
            fontName='Helvetica-Oblique'
        ),
        'TipBox': ParagraphStyle(
            'TipBox',
            parent=styles['Normal'],
            fontSize=10,
            textColor=DARK_TEXT,
            leftIndent=15,
            spaceAfter=6,
            leading=14
        ),
        'Savings': ParagraphStyle(
            'Savings',
            parent=styles['Normal'],
            fontSize=10,
            textColor=SUCCESS,
            fontName='Helvetica-Bold'
        ),
        'ProductName': ParagraphStyle(
            'ProductName',
            parent=styles['Normal'],
            fontSize=12,
            textColor=SECONDARY,
            fontName='Helvetica-Bold',
            spaceAfter=4
        ),
        'ProductDetails': ParagraphStyle(
            'ProductDetails',
            parent=styles['Normal'],
            fontSize=10,
            textColor=DARK_TEXT,
            spaceAfter=4
        ),
        'ProductLink': ParagraphStyle(
            'ProductLink',
            parent=styles['Normal'],
            fontSize=9,
            textColor=ACCENT,
            spaceAfter=12
        ),
        'Footer': ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=MUTED,
            alignment=TA_CENTER
        ),
        'TOCItem': ParagraphStyle(
            'TOCItem',
            parent=styles['Normal'],
            fontSize=12,
            textColor=SECONDARY,
            spaceBefore=6,
            leftIndent=20
        ),
        'MonthTitle': ParagraphStyle(
            'MonthTitle',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=PRIMARY,
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ),
        'CalendarText': ParagraphStyle(
            'CalendarText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=DARK_TEXT,
            leftIndent=10,
            spaceAfter=3
        )
    }

    return custom_styles


def generate_pdf(output_path: str = "smart_shopper_guide.pdf"):
    """Generate the comprehensive lead magnet PDF."""

    if not REPORTLAB_AVAILABLE:
        print("ReportLab is required. Install it with: pip install reportlab")
        return generate_text_version(output_path.replace('.pdf', '.txt'))

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.7*inch,
        leftMargin=0.7*inch,
        topMargin=0.6*inch,
        bottomMargin=0.6*inch
    )

    styles = create_styles()
    elements = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("💝", ParagraphStyle('Emoji', fontSize=48, alignment=TA_CENTER)))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("THE SMART SHOPPER'S", styles['CoverTitle']))
    elements.append(Paragraph("ULTIMATE GUIDE", styles['CoverTitle']))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        "50+ Money-Saving Strategies for Beauty, Home & Decor",
        styles['CoverSubtitle']
    ))
    elements.append(Paragraph(
        "Plus 30 Hand-Picked Products Under $30",
        styles['CoverSubtitle']
    ))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(HRFlowable(width="40%", thickness=2, color=PRIMARY, spaceAfter=20))
    elements.append(Paragraph(
        "Save hundreds on your next shopping trip with insider secrets,<br/>"
        "the psychology behind pricing, and a month-by-month guide<br/>"
        "to the best sales of the year.",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph(
        f"© {datetime.now().year} Daily Deal Darling",
        styles['Footer']
    ))
    elements.append(Paragraph(
        "dailydealdarling.com",
        styles['Footer']
    ))
    elements.append(PageBreak())

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    elements.append(Paragraph("What's Inside", styles['ChapterTitle']))
    elements.append(Spacer(1, 0.2*inch))

    toc_items = [
        "Introduction: How to Use This Guide",
        "Chapter 1: The Psychology of Pricing (What Stores Don't Tell You)",
        "Chapter 2: 50+ Proven Money-Saving Strategies",
        "   • Before You Buy: Research Phase",
        "   • Amazon Mastery",
        "   • Coupon Stacking & Cashback",
        "   • Beauty & Skincare Savings",
        "   • Home & Decor Strategies",
        "   • Grocery & Household Essentials",
        "   • Seasonal & Holiday Shopping",
        "   • Advanced Techniques",
        "Chapter 3: The Month-by-Month Shopping Calendar",
        "Chapter 4: 30 Editor-Approved Products Under $30",
        "   • Beauty Essentials",
        "   • Home Organization",
        "   • Decor Finds",
        "Bonus: Monthly Budget Tracker Worksheet",
        "Thank You + What's Next"
    ]

    for item in toc_items:
        elements.append(Paragraph(item, styles['TOCItem']))

    elements.append(PageBreak())

    # =========================================================================
    # INTRODUCTION
    # =========================================================================
    elements.append(Paragraph("Introduction", styles['ChapterTitle']))
    elements.append(Paragraph("How to Use This Guide", styles['SectionTitle']))

    for paragraph in INTRODUCTION.strip().split('\n\n'):
        if paragraph.strip().startswith('•'):
            # It's a bullet list
            items = [p.strip()[2:] for p in paragraph.strip().split('\n') if p.strip()]
            for item in items:
                elements.append(Paragraph(f"• {item}", styles['BodyText']))
        else:
            elements.append(Paragraph(paragraph.strip(), styles['BodyText']))

    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(
        "💡 <b>Pro Tip:</b> Don't try to implement everything at once. Pick 3-5 strategies "
        "to start with, master them, then add more. Small changes compound into big savings.",
        styles['Quote']
    ))
    elements.append(PageBreak())

    # =========================================================================
    # CHAPTER 1: PSYCHOLOGY OF PRICING
    # =========================================================================
    elements.append(Paragraph("Chapter 1", styles['CoverSubtitle']))
    elements.append(Paragraph(PSYCHOLOGY_SECTION['title'], styles['ChapterTitle']))
    elements.append(Paragraph(PSYCHOLOGY_SECTION['intro'], styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))

    for i, tactic in enumerate(PSYCHOLOGY_SECTION['tactics'], 1):
        elements.append(Paragraph(f"{i}. {tactic['name']}", styles['SubsectionTitle']))
        elements.append(Paragraph(tactic['explanation'], styles['BodyText']))
        elements.append(Paragraph(
            f"🛡️ <b>Your Defense:</b> {tactic['defense']}",
            styles['TipBox']
        ))
        elements.append(Spacer(1, 0.1*inch))

    elements.append(PageBreak())

    # =========================================================================
    # CHAPTER 2: 50+ STRATEGIES
    # =========================================================================
    elements.append(Paragraph("Chapter 2", styles['CoverSubtitle']))
    elements.append(Paragraph("50+ Proven Money-Saving Strategies", styles['ChapterTitle']))
    elements.append(Paragraph(
        "These strategies are organized by category. Each one includes the estimated "
        "savings potential to help you prioritize what to try first.",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 0.2*inch))

    strategy_num = 1
    for category_data in STRATEGIES:
        elements.append(Paragraph(
            f"{category_data['icon']} {category_data['category']}",
            styles['SectionTitle']
        ))

        for strategy in category_data['strategies']:
            elements.append(Paragraph(
                f"<b>{strategy_num}. {strategy['title']}</b>",
                styles['SubsectionTitle']
            ))
            elements.append(Paragraph(strategy['description'], styles['BodyText']))
            elements.append(Paragraph(
                f"💰 Potential Savings: {strategy['savings']}",
                styles['Savings']
            ))
            elements.append(Spacer(1, 0.1*inch))
            strategy_num += 1

        elements.append(Spacer(1, 0.15*inch))

    elements.append(PageBreak())

    # =========================================================================
    # CHAPTER 3: SHOPPING CALENDAR
    # =========================================================================
    elements.append(Paragraph("Chapter 3", styles['CoverSubtitle']))
    elements.append(Paragraph("The Month-by-Month Shopping Calendar", styles['ChapterTitle']))
    elements.append(Paragraph(
        "Timing is everything in retail. This calendar shows you exactly when to buy "
        "(and when to wait) for the best prices throughout the year.",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 0.2*inch))

    for month, data in SHOPPING_CALENDAR.items():
        elements.append(Paragraph(f"📅 {month}", styles['MonthTitle']))

        elements.append(Paragraph("<b>✅ Best Time to Buy:</b>", styles['CalendarText']))
        for item in data['best_buys']:
            elements.append(Paragraph(f"   • {item}", styles['CalendarText']))

        elements.append(Paragraph("<b>❌ Wait on These:</b>", styles['CalendarText']))
        for item in data['avoid']:
            elements.append(Paragraph(f"   • {item}", styles['CalendarText']))

        elements.append(Paragraph(
            f"<b>🎯 Key Events:</b> {data['events']}",
            styles['CalendarText']
        ))
        elements.append(Spacer(1, 0.1*inch))

    elements.append(PageBreak())

    # =========================================================================
    # CHAPTER 4: PRODUCT RECOMMENDATIONS
    # =========================================================================
    elements.append(Paragraph("Chapter 4", styles['CoverSubtitle']))
    elements.append(Paragraph("30 Editor-Approved Products Under $30", styles['ChapterTitle']))
    elements.append(Paragraph(
        "Every product here has been vetted for quality, value, and genuine reviews. "
        "We only recommend items we'd buy ourselves — no sponsored placements.",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 0.2*inch))

    product_num = 1
    for category, products in PRODUCT_RECOMMENDATIONS.items():
        elements.append(Paragraph(f"✨ {category}", styles['SectionTitle']))

        for product in products:
            elements.append(KeepTogether([
                Paragraph(f"{product_num}. {product['name']}", styles['ProductName']),
                Paragraph(
                    f"💰 {product['price']}  |  ⭐ {product['stars']} ({product['reviews']} reviews)",
                    styles['ProductDetails']
                ),
                Paragraph(f"<b>Why we love it:</b> {product['why']}", styles['ProductDetails']),
                Paragraph(f"<b>Best for:</b> {product['best_for']}", styles['ProductDetails']),
                Paragraph(
                    f"🔗 amazon.com/dp/{product['asin']}?tag=dailydealdarling1-20",
                    styles['ProductLink']
                ),
            ]))
            product_num += 1

    elements.append(PageBreak())

    # =========================================================================
    # BONUS: BUDGET TRACKER
    # =========================================================================
    elements.append(Paragraph("Bonus", styles['CoverSubtitle']))
    elements.append(Paragraph("Monthly Budget Tracker Worksheet", styles['ChapterTitle']))
    elements.append(Paragraph(
        "Print this page and use it to track your spending each month. "
        "Awareness is the first step to saving more.",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 0.3*inch))

    # Create a budget tracker table
    budget_data = [
        ['Category', 'Budget', 'Spent', 'Saved', 'Notes'],
        ['Groceries', '$_____', '$_____', '$_____', ''],
        ['Beauty & Personal Care', '$_____', '$_____', '$_____', ''],
        ['Clothing & Accessories', '$_____', '$_____', '$_____', ''],
        ['Home & Decor', '$_____', '$_____', '$_____', ''],
        ['Entertainment', '$_____', '$_____', '$_____', ''],
        ['Gifts', '$_____', '$_____', '$_____', ''],
        ['Miscellaneous', '$_____', '$_____', '$_____', ''],
        ['TOTAL', '$_____', '$_____', '$_____', ''],
    ]

    budget_table = Table(budget_data, colWidths=[1.8*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1.5*inch])
    budget_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-2, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (0, -1), (-1, -1), LIGHT_BG),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(budget_table)

    elements.append(Spacer(1, 0.4*inch))
    elements.append(Paragraph("<b>This Month's Savings Goal:</b> $__________", styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph("<b>Deals I'm Waiting For:</b>", styles['BodyText']))
    for i in range(1, 4):
        elements.append(Paragraph(f"{i}. _______________________________________________", styles['BodyText']))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("<b>Upcoming Sales to Watch:</b>", styles['BodyText']))
    for i in range(3):
        elements.append(Paragraph("□ _______________________________________________", styles['BodyText']))

    elements.append(PageBreak())

    # =========================================================================
    # THANK YOU PAGE
    # =========================================================================
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph("Thank You!", styles['CoverTitle']))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(
        "You now have everything you need to become a smarter shopper and "
        "save hundreds (even thousands) of dollars this year.",
        styles['BodyText']
    ))
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        "<b>Here's what to do next:</b>",
        styles['BodyText']
    ))
    elements.append(Paragraph("1. Pick 3 strategies from Chapter 2 to implement this week", styles['BodyText']))
    elements.append(Paragraph("2. Bookmark the Shopping Calendar for your next purchase", styles['BodyText']))
    elements.append(Paragraph("3. Print the Budget Tracker and start using it", styles['BodyText']))
    elements.append(Paragraph("4. Check your inbox every Tuesday for our curated deals", styles['BodyText']))

    elements.append(Spacer(1, 0.4*inch))
    elements.append(HRFlowable(width="60%", thickness=1, color=PRIMARY, spaceAfter=20))

    elements.append(Paragraph(
        "💝 <b>Happy Shopping!</b><br/>The Daily Deal Darling Team",
        ParagraphStyle('Signature', fontSize=14, textColor=SECONDARY, alignment=TA_CENTER)
    ))

    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        "<b>Stay Connected:</b><br/>"
        "🌐 dailydealdarling.com<br/>"
        "📧 Weekly deals in your inbox every Tuesday<br/>"
        "📌 Follow us on Pinterest: @dailydealdarling",
        styles['Footer']
    ))

    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        "<i>Affiliate Disclosure: Some links in this guide are affiliate links. "
        "This means we may earn a small commission if you make a purchase — at no "
        "extra cost to you. We only recommend products we truly believe in.</i>",
        ParagraphStyle('Disclosure', fontSize=8, textColor=MUTED, alignment=TA_CENTER)
    ))

    # Build the PDF
    doc.build(elements)
    print(f"\n✅ PDF generated successfully: {output_path}")
    print(f"   File size: {Path(output_path).stat().st_size / 1024:.1f} KB")

    return output_path


def generate_text_version(output_path: str):
    """Generate a plain text version if ReportLab is not available."""

    content = []
    content.append("=" * 70)
    content.append("THE SMART SHOPPER'S ULTIMATE GUIDE")
    content.append("50+ Money-Saving Strategies for Beauty, Home & Decor")
    content.append("Plus 30 Hand-Picked Products Under $30")
    content.append("=" * 70)
    content.append("")
    content.append("© " + str(datetime.now().year) + " Daily Deal Darling | dailydealdarling.com")
    content.append("")
    content.append("-" * 70)

    # Introduction
    content.append("\nINTRODUCTION")
    content.append("-" * 40)
    content.append(INTRODUCTION.strip())
    content.append("")

    # Psychology Section
    content.append("\nCHAPTER 1: " + PSYCHOLOGY_SECTION['title'].upper())
    content.append("-" * 40)
    content.append(PSYCHOLOGY_SECTION['intro'])
    content.append("")

    for i, tactic in enumerate(PSYCHOLOGY_SECTION['tactics'], 1):
        content.append(f"\n{i}. {tactic['name']}")
        content.append(tactic['explanation'])
        content.append(f"   🛡️ Your Defense: {tactic['defense']}")

    content.append("")

    # Strategies
    content.append("\nCHAPTER 2: 50+ PROVEN MONEY-SAVING STRATEGIES")
    content.append("-" * 40)

    strategy_num = 1
    for category_data in STRATEGIES:
        content.append(f"\n{category_data['icon']} {category_data['category']}")
        content.append("")

        for strategy in category_data['strategies']:
            content.append(f"{strategy_num}. {strategy['title']}")
            content.append(f"   {strategy['description']}")
            content.append(f"   💰 Potential Savings: {strategy['savings']}")
            content.append("")
            strategy_num += 1

    # Shopping Calendar
    content.append("\nCHAPTER 3: MONTH-BY-MONTH SHOPPING CALENDAR")
    content.append("-" * 40)

    for month, data in SHOPPING_CALENDAR.items():
        content.append(f"\n📅 {month}")
        content.append("   Best Time to Buy:")
        for item in data['best_buys']:
            content.append(f"      • {item}")
        content.append("   Wait on These:")
        for item in data['avoid']:
            content.append(f"      • {item}")
        content.append(f"   Key Events: {data['events']}")

    content.append("")

    # Products
    content.append("\nCHAPTER 4: 30 EDITOR-APPROVED PRODUCTS UNDER $30")
    content.append("-" * 40)

    product_num = 1
    for category, products in PRODUCT_RECOMMENDATIONS.items():
        content.append(f"\n✨ {category}")
        content.append("")

        for product in products:
            content.append(f"{product_num}. {product['name']}")
            content.append(f"   Price: {product['price']} | Rating: {product['stars']} ({product['reviews']} reviews)")
            content.append(f"   Why we love it: {product['why']}")
            content.append(f"   Best for: {product['best_for']}")
            content.append(f"   Link: amazon.com/dp/{product['asin']}?tag=dailydealdarling1-20")
            content.append("")
            product_num += 1

    # Budget Tracker
    content.append("\nBONUS: MONTHLY BUDGET TRACKER")
    content.append("-" * 40)
    content.append(BUDGET_WORKSHEET)

    # Thank You
    content.append("\n" + "=" * 70)
    content.append("THANK YOU FOR READING!")
    content.append("=" * 70)
    content.append("")
    content.append("You're now armed with 50+ strategies to save on every purchase.")
    content.append("Check your inbox every Tuesday for our curated weekly deals!")
    content.append("")
    content.append("💝 Happy Shopping!")
    content.append("The Daily Deal Darling Team")
    content.append("")
    content.append("Visit: dailydealdarling.com")
    content.append("=" * 70)

    Path(output_path).write_text("\n".join(content))
    print(f"✅ Text version generated: {output_path}")
    return output_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate the Smart Shopper Guide PDF')
    parser.add_argument(
        '--output',
        default='smart_shopper_guide.pdf',
        help='Output file path'
    )

    args = parser.parse_args()

    # Ensure output directory exists
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    generate_pdf(str(output_path))


if __name__ == "__main__":
    main()
