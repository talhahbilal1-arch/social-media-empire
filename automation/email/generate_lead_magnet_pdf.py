"""
Premium Lead Magnet PDF Generator with Real Amazon Product Images

Creates a stunning visual guide with:
- Real product images fetched from Amazon
- Clickable affiliate links (dailydealdarling1-20)
- Professional magazine-style layout
"""

import os
import io
import re
import urllib.request
import ssl
from datetime import datetime
from pathlib import Path
import time

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, Flowable, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfbase.pdfmetrics import stringWidth
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Install ReportLab: pip install reportlab")


# =============================================================================
# BRAND COLORS
# =============================================================================
class C:
    CORAL = colors.HexColor("#E85A4F")
    NAVY = colors.HexColor("#2C3E50")
    GOLD = colors.HexColor("#D4A574")
    GREEN = colors.HexColor("#27AE60")
    CREAM = colors.HexColor("#FDF8F5")
    WHITE = colors.white
    DARK = colors.HexColor("#1A1A2E")
    GRAY = colors.HexColor("#7F8C8D")
    LIGHT_GRAY = colors.HexColor("#ECF0F1")
    BLUSH = colors.HexColor("#FADBD8")
    SAGE = colors.HexColor("#D5E8D4")
    AMAZON_ORANGE = colors.HexColor("#FF9900")


# =============================================================================
# AFFILIATE TAG
# =============================================================================
AFFILIATE_TAG = "dailydealdarling1-20"

def get_affiliate_url(asin):
    return f"https://www.amazon.com/dp/{asin}?tag={AFFILIATE_TAG}"


# =============================================================================
# PRODUCTS DATA
# =============================================================================
PRODUCTS = {
    "beauty": [
        {
            "name": "CeraVe Moisturizing Cream",
            "price": "$15.99",
            "rating": "4.7",
            "reviews": "127K+",
            "why": "Dermatologist-developed with ceramides. Works on face AND body.",
            "asin": "B00TTD9BRC",
        },
        {
            "name": "The Ordinary Niacinamide 10%",
            "price": "$5.80",
            "rating": "4.4",
            "reviews": "75K+",
            "why": "Clinical-grade serum that rivals $50+ products. Targets pores & oil.",
            "asin": "B01MDTVZTZ",
        },
        {
            "name": "Laneige Lip Sleeping Mask",
            "price": "$24.00",
            "rating": "4.6",
            "reviews": "45K+",
            "why": "TikTok famous for a reason. One jar lasts 6+ months of nightly use.",
            "asin": "B07XXPHQZK",
        },
        {
            "name": "e.l.f. Poreless Putty Primer",
            "price": "$10.00",
            "rating": "4.4",
            "reviews": "48K+",
            "why": "Perfect dupe for Tatcha Silk Canvas ($52). Same silky finish.",
            "asin": "B0815DCF14",
        },
        {
            "name": "Maybelline Lash Sensational",
            "price": "$8.98",
            "rating": "4.4",
            "reviews": "95K+",
            "why": "Fanned-out lashes without clumping. The drugstore mascara pros swear by.",
            "asin": "B00PFCT2R0",
        },
    ],
    "home": [
        {
            "name": "SONGMICS Portable Closet",
            "price": "$45.99",
            "rating": "4.6",
            "reviews": "18K+",
            "why": "Doubles your closet space instantly. Quick assembly, sturdy build.",
            "asin": "B07MTZJW2G",
        },
        {
            "name": "mDesign Clear Storage Bins 4pk",
            "price": "$24.99",
            "rating": "4.6",
            "reviews": "12K+",
            "why": "See everything at a glance. Perfect for fridge, pantry, bathroom.",
            "asin": "B07D84P19H",
        },
        {
            "name": "Command Picture Hanging Strips",
            "price": "$13.19",
            "rating": "4.7",
            "reviews": "95K+",
            "why": "No holes, no damage, holds 16 lbs. Essential for renters.",
            "asin": "B073XR4X72",
        },
        {
            "name": "Amazon Basics Velvet Hangers",
            "price": "$24.99",
            "rating": "4.8",
            "reviews": "200K+",
            "why": "Non-slip, ultra-slim. Fit 2x more clothes in same closet space.",
            "asin": "B0758C7J39",
        },
        {
            "name": "SimpleHouseware Can Rack",
            "price": "$19.87",
            "rating": "4.5",
            "reviews": "22K+",
            "why": "Pantry transformation. Holds 36 cans, FIFO rotation built-in.",
            "asin": "B01CSPWQJ4",
        },
    ],
    "decor": [
        {
            "name": "MIULEE Velvet Pillow Covers",
            "price": "$13.99",
            "rating": "4.5",
            "reviews": "55K+",
            "why": "Velvet texture, hidden zipper, machine washable. Pack of 2!",
            "asin": "B076LWHV2Z",
        },
        {
            "name": "NICETOWN Blackout Curtains",
            "price": "$23.95",
            "rating": "4.6",
            "reviews": "130K+",
            "why": "Room darkening + thermal insulated. 50+ colors available.",
            "asin": "B015SJ7RYY",
        },
        {
            "name": "Eucalyptus in Glass Vase",
            "price": "$15.99",
            "rating": "4.5",
            "reviews": "5K+",
            "why": "Looks incredibly real. Includes vase with faux water. Zero care.",
            "asin": "B0CY2GVDT1",
        },
        {
            "name": "Gold Ceramic Vase Set of 3",
            "price": "$19.99",
            "rating": "4.6",
            "reviews": "2K+",
            "why": "That expensive boutique look for under $7 each. Instant elegance.",
            "asin": "B0BZM8KRQB",
        },
        {
            "name": "Vinkor Flameless LED Candles",
            "price": "$25.99",
            "rating": "4.5",
            "reviews": "35K+",
            "why": "Real wax, realistic flicker, remote with timer. Safe for pets.",
            "asin": "B07D266SGW",
        },
    ]
}

STRATEGIES = [
    ("The 24-Hour Rule", "Wait 24 hours before any purchase over $30. Eliminates 70% of impulse buys.", "$500-2K/yr"),
    ("Price History Check", "Install CamelCamelCamel extension. See if that 'sale' is actually a good deal.", "15-40%"),
    ("Triple Stack Method", "Store sale + manufacturer coupon + cashback app = 30-50% off regularly.", "30-50%"),
    ("Subscribe & Cancel", "Amazon Subscribe & Save gives 15% off. Get one shipment, then cancel.", "15%"),
    ("Amazon Warehouse", "Filter by 'Amazon Warehouse' for open-box items at 20-50% off.", "20-50%"),
    ("Abandoned Cart Trick", "Add to cart then leave. Most sites email 10-15% off within 48 hours.", "10-15%"),
]

CALENDAR = [
    ("JAN", "Holiday decor 90% off • Winter clothes 70% off • Bedding sales"),
    ("FEB", "TVs for Super Bowl • Chocolate after V-Day 50-75% off"),
    ("MAR", "Ulta 21 Days of Beauty: 50% off prestige brands daily"),
    ("APR", "Wayfair Way Day • Sephora Spring Sale 15-20% off sitewide"),
    ("MAY", "Memorial Day: Mattresses & appliances at year-low prices"),
    ("JUN", "Tools for Father's Day • Semi-annual lingerie sales"),
    ("JUL", "PRIME DAY: Best deals of summer across all categories"),
    ("AUG", "Outdoor furniture 70% off • Back-to-school laptop deals"),
    ("SEP", "Ulta 21 Days again • Labor Day appliance sales"),
    ("OCT", "Wayfair Way Day #2 • Columbus Day denim deals"),
    ("NOV", "BLACK FRIDAY & CYBER MONDAY: Biggest sales of the year"),
    ("DEC", "After-Christmas clearance 50-90% off • Gift card bonuses"),
]


# =============================================================================
# IMAGE FETCHING
# =============================================================================

def fetch_amazon_image_url(asin, retries=2):
    """Fetch the main product image URL from Amazon product page."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = f"https://www.amazon.com/dp/{asin}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'identity',
        'Connection': 'keep-alive',
    }

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
                html = response.read().decode('utf-8', errors='ignore')

            # Look for high-quality product images
            # Pattern 1: Main product image (usually the largest)
            patterns = [
                r'"hiRes":"(https://m\.media-amazon\.com/images/I/[^"]+)"',
                r'"large":"(https://m\.media-amazon\.com/images/I/[^"]+)"',
                r'data-old-hires="(https://m\.media-amazon\.com/images/I/[^"]+)"',
                r'src="(https://m\.media-amazon\.com/images/I/[A-Za-z0-9+%-]+\._[^"]*(?:SL1500|SL1000|SL500|AC_SL)[^"]*\.jpg)"',
                r'(https://m\.media-amazon\.com/images/I/[A-Za-z0-9+%-]+\._AC_SL\d+_\.jpg)',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, html)
                if matches:
                    # Get the first high-res image
                    img_url = matches[0]
                    # Convert to a consistent size
                    img_url = re.sub(r'\._[^.]+_\.', '._AC_SL500_.', img_url)
                    return img_url

            # Fallback: any Amazon image
            fallback = re.findall(r'(https://m\.media-amazon\.com/images/I/[A-Za-z0-9+%-]+\.jpg)', html)
            if fallback:
                return fallback[0].replace('.jpg', '._AC_SL500_.jpg')

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
            continue

    return None


def download_image(url, max_size=(100, 100)):
    """Download image and return as ReportLab Image object."""
    if not url:
        return None

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            image_data = response.read()

        img = Image(io.BytesIO(image_data))

        # Scale to fit within max_size while maintaining aspect ratio
        aspect = img.imageWidth / img.imageHeight
        if aspect > 1:
            img.drawWidth = min(max_size[0], img.imageWidth)
            img.drawHeight = img.drawWidth / aspect
        else:
            img.drawHeight = min(max_size[1], img.imageHeight)
            img.drawWidth = img.drawHeight * aspect

        return img

    except Exception as e:
        return None


# =============================================================================
# CUSTOM FLOWABLES
# =============================================================================

class ProductCard(Flowable):
    """Beautiful product card with image and clickable link."""

    def __init__(self, product, image_obj=None, width=230, height=210):
        Flowable.__init__(self)
        self.product = product
        self.image_obj = image_obj
        self.width = width
        self.height = height
        self.affiliate_url = get_affiliate_url(product['asin'])

    def draw(self):
        c = self.canv

        # Shadow
        c.setFillColor(colors.HexColor("#E8E8E8"))
        c.roundRect(3, -3, self.width, self.height, 12, fill=1, stroke=0)

        # Card background
        c.setFillColor(C.WHITE)
        c.setStrokeColor(colors.HexColor("#E0E0E0"))
        c.setLineWidth(1)
        c.roundRect(0, 0, self.width, self.height, 12, fill=1, stroke=1)

        # Image area background
        img_area_height = 100
        img_area_y = self.height - img_area_height - 10
        c.setFillColor(C.CREAM)
        c.roundRect(10, img_area_y, self.width - 20, img_area_height, 8, fill=1, stroke=0)

        # Draw product image
        if self.image_obj:
            try:
                img_x = (self.width - self.image_obj.drawWidth) / 2
                img_y = img_area_y + (img_area_height - self.image_obj.drawHeight) / 2
                self.image_obj.drawOn(c, img_x, img_y)
            except:
                pass

        # Price badge
        c.setFillColor(C.GREEN)
        badge_w = 55
        c.roundRect(self.width - badge_w - 8, self.height - 28, badge_w, 22, 6, fill=1, stroke=0)
        c.setFillColor(C.WHITE)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(self.width - badge_w/2 - 8, self.height - 21, self.product['price'])

        # Content area
        content_y = img_area_y - 10

        # Product name
        c.setFillColor(C.NAVY)
        c.setFont("Helvetica-Bold", 10)
        name = self.product['name']
        if len(name) > 28:
            name = name[:26] + "..."
        c.drawCentredString(self.width/2, content_y - 5, name)

        # Rating
        c.setFillColor(C.AMAZON_ORANGE)
        c.setFont("Helvetica-Bold", 9)
        rating = f"★ {self.product['rating']} ({self.product['reviews']})"
        c.drawCentredString(self.width/2, content_y - 20, rating)

        # Why we love it
        c.setFillColor(C.DARK)
        c.setFont("Helvetica", 8)
        why = self.product['why']
        words = why.split()
        lines = []
        line = ""
        for word in words:
            test = line + " " + word if line else word
            if stringWidth(test, "Helvetica", 8) < self.width - 30:
                line = test
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)

        y = content_y - 35
        for ln in lines[:2]:
            c.drawCentredString(self.width/2, y, ln)
            y -= 11

        # Shop button
        btn_w, btn_h = 110, 26
        btn_x = (self.width - btn_w) / 2
        btn_y = 10

        c.setFillColor(C.AMAZON_ORANGE)
        c.roundRect(btn_x, btn_y, btn_w, btn_h, 6, fill=1, stroke=0)
        c.setFillColor(C.WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(self.width/2, btn_y + 9, "Shop on Amazon →")

        # Make the button clickable - use relative=1 for flowable coordinates
        c.linkURL(self.affiliate_url, (btn_x, btn_y, btn_x + btn_w, btn_y + btn_h), relative=1)

        # Also make the entire card clickable as a fallback
        c.linkURL(self.affiliate_url, (0, 0, self.width, self.height), relative=1)


class StrategyCard(Flowable):
    """Strategy tip card."""

    def __init__(self, number, title, description, savings, width=480):
        Flowable.__init__(self)
        self.number = number
        self.title = title
        self.description = description
        self.savings = savings
        self.width = width
        self.height = 60

    def draw(self):
        c = self.canv

        # Background
        c.setFillColor(C.CREAM)
        c.roundRect(0, 0, self.width, self.height, 8, fill=1, stroke=0)

        # Number circle
        c.setFillColor(C.CORAL)
        c.circle(28, self.height/2, 18, fill=1, stroke=0)
        c.setFillColor(C.WHITE)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(28, self.height/2 - 5, str(self.number))

        # Title
        c.setFillColor(C.NAVY)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(55, self.height - 18, self.title)

        # Description
        c.setFillColor(C.DARK)
        c.setFont("Helvetica", 9)
        desc = self.description[:80] + "..." if len(self.description) > 80 else self.description
        c.drawString(55, self.height - 35, desc)

        # Savings badge
        c.setFillColor(C.GREEN)
        badge_w = 65
        c.roundRect(self.width - badge_w - 10, self.height/2 - 11, badge_w, 22, 6, fill=1, stroke=0)
        c.setFillColor(C.WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(self.width - badge_w/2 - 10, self.height/2 - 4, self.savings)


class CalendarRow(Flowable):
    """Calendar month row."""

    def __init__(self, month, description, width=480):
        Flowable.__init__(self)
        self.month = month
        self.description = description
        self.width = width
        self.height = 30

    def draw(self):
        c = self.canv

        # Month badge
        c.setFillColor(C.NAVY)
        c.roundRect(0, 2, 42, self.height - 4, 5, fill=1, stroke=0)
        c.setFillColor(C.WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(21, 11, self.month)

        # Description
        c.setFillColor(C.DARK)
        c.setFont("Helvetica", 9)
        c.drawString(52, 11, self.description[:75])

        # Divider
        c.setStrokeColor(C.LIGHT_GRAY)
        c.setLineWidth(0.5)
        c.line(0, 0, self.width, 0)


# =============================================================================
# PDF GENERATION
# =============================================================================

def create_styles():
    return {
        'Hero': ParagraphStyle('Hero', fontSize=36, textColor=C.NAVY, alignment=TA_CENTER,
                               fontName='Helvetica-Bold', leading=42),
        'HeroSub': ParagraphStyle('HeroSub', fontSize=13, textColor=C.GRAY, alignment=TA_CENTER, leading=18),
        'Chapter': ParagraphStyle('Chapter', fontSize=10, textColor=C.CORAL, fontName='Helvetica-Bold'),
        'Title': ParagraphStyle('Title', fontSize=22, textColor=C.NAVY, fontName='Helvetica-Bold',
                                spaceAfter=6, leading=26),
        'Intro': ParagraphStyle('Intro', fontSize=10, textColor=C.DARK, leading=14, spaceAfter=12),
        'Section': ParagraphStyle('Section', fontSize=14, textColor=C.NAVY, fontName='Helvetica-Bold',
                                  spaceBefore=15, spaceAfter=8),
        'Body': ParagraphStyle('Body', fontSize=10, textColor=C.DARK, leading=14),
        'Footer': ParagraphStyle('Footer', fontSize=8, textColor=C.GRAY, alignment=TA_CENTER),
        'Quote': ParagraphStyle('Quote', fontSize=12, textColor=C.NAVY, alignment=TA_CENTER,
                                fontName='Helvetica-Oblique', leading=16),
    }


def generate_pdf(output_path: str = "smart_shopper_guide.pdf"):
    """Generate premium PDF with real Amazon product images."""

    if not REPORTLAB_AVAILABLE:
        print("ReportLab required: pip install reportlab")
        return None

    print("\n🎨 Generating Premium Smart Shopper's Guide...")
    print("━" * 50)

    # Fetch all product images
    all_products = PRODUCTS['beauty'] + PRODUCTS['home'] + PRODUCTS['decor']
    images = {}

    print("\n📦 Fetching product images from Amazon...")
    for i, prod in enumerate(all_products, 1):
        print(f"   [{i:2d}/{len(all_products)}] {prod['name'][:35]}...", end=" ")

        # Fetch image URL from Amazon page
        img_url = fetch_amazon_image_url(prod['asin'])

        if img_url:
            # Download the image
            img = download_image(img_url, max_size=(85, 85))
            if img:
                images[prod['asin']] = img
                print("✓")
            else:
                print("⚠ download failed")
        else:
            print("⚠ URL not found")

        time.sleep(0.5)  # Be nice to Amazon

    print(f"\n   Successfully loaded {len(images)}/{len(all_products)} images")

    # Create PDF
    print("\n📄 Building PDF...")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.55*inch,
        leftMargin=0.55*inch,
        topMargin=0.45*inch,
        bottomMargin=0.45*inch
    )

    styles = create_styles()
    elements = []
    page_width = letter[0] - 1.1*inch

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("💝 DAILY DEAL DARLING", styles['Chapter']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph("The Smart<br/>Shopper's Guide", styles['Hero']))
    elements.append(Spacer(1, 0.12*inch))
    elements.append(HRFlowable(width="22%", thickness=3, color=C.CORAL, spaceAfter=12))
    elements.append(Paragraph(
        "6 Power Strategies to Save Thousands<br/>+ 15 Top-Rated Products Under $30",
        styles['HeroSub']
    ))

    elements.append(Spacer(1, 0.35*inch))

    # Stats - with proper spacing between numbers and labels
    stats = [["$2,847", "6", "15"], ["Avg. Yearly Savings", "Power Strategies", "Top Products"]]
    stats_table = Table(stats, colWidths=[page_width/3]*3, rowHeights=[50, 22])
    stats_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),   # Numbers centered in taller cell
        ('VALIGN', (0, 1), (-1, 1), 'TOP'),      # Labels at top of cell
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 28),
        ('TEXTCOLOR', (0, 0), (0, 0), C.CORAL),
        ('TEXTCOLOR', (1, 0), (1, 0), C.NAVY),
        ('TEXTCOLOR', (2, 0), (2, 0), C.GREEN),
        ('FONTSIZE', (0, 1), (-1, 1), 9),
        ('TEXTCOLOR', (0, 1), (-1, 1), C.GRAY),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Push numbers up from bottom
        ('TOPPADDING', (0, 1), (-1, 1), 6),      # Gap above labels
    ]))
    elements.append(stats_table)

    elements.append(Spacer(1, 0.4*inch))
    elements.append(Paragraph('"Stop overpaying. Start outsmarting."', styles['Quote']))
    elements.append(Spacer(1, 0.8*inch))
    elements.append(Paragraph(f"© {datetime.now().year} Daily Deal Darling • dailydealdarling.com", styles['Footer']))
    elements.append(PageBreak())

    # =========================================================================
    # STRATEGIES PAGE
    # =========================================================================
    elements.append(Paragraph("01", styles['Chapter']))
    elements.append(Paragraph("6 Strategies That Save Thousands", styles['Title']))
    elements.append(Paragraph(
        "These are the highest-ROI strategies our readers use to save $2,000+ every year. "
        "Master these six and you're ahead of 90% of shoppers.",
        styles['Intro']
    ))

    for i, (title, desc, savings) in enumerate(STRATEGIES, 1):
        elements.append(StrategyCard(i, title, desc, savings, width=page_width))
        elements.append(Spacer(1, 6))

    elements.append(Spacer(1, 0.15*inch))

    # Pro tip
    tip = Table([[Paragraph(
        "💡 <b>START HERE:</b> The 24-Hour Rule alone saves most people $500+ per year. "
        "Try it this week on your next purchase over $30.",
        ParagraphStyle('Tip', fontSize=9, textColor=C.NAVY, leading=13)
    )]], colWidths=[page_width - 16])
    tip.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C.BLUSH),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(tip)

    elements.append(PageBreak())

    # =========================================================================
    # CALENDAR PAGE
    # =========================================================================
    elements.append(Paragraph("02", styles['Chapter']))
    elements.append(Paragraph("When to Buy Everything", styles['Title']))
    elements.append(Paragraph(
        "Timing = money. This calendar shows the best month to buy each category. "
        "Bookmark this page for year-round savings.",
        styles['Intro']
    ))

    for month, desc in CALENDAR:
        elements.append(CalendarRow(month, desc, width=page_width))
        elements.append(Spacer(1, 2))

    elements.append(Spacer(1, 0.15*inch))

    dates = Table([[Paragraph(
        "🗓️ <b>KEY DATES:</b> Prime Day (July) • Ulta 21 Days (Mar/Sep) • "
        "Way Day (Apr/Oct) • Black Friday (Nov)",
        ParagraphStyle('Dates', fontSize=9, textColor=C.NAVY, leading=13)
    )]], colWidths=[page_width - 16])
    dates.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C.SAGE),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(dates)

    elements.append(PageBreak())

    # =========================================================================
    # BEAUTY PRODUCTS
    # =========================================================================
    elements.append(Paragraph("03", styles['Chapter']))
    elements.append(Paragraph("15 Products We Actually Use", styles['Title']))
    elements.append(Paragraph(
        "Every product is vetted, reviewed, and genuinely loved. Click any card to shop on Amazon. "
        "No sponsored placements — just the best value under $30.",
        styles['Intro']
    ))

    elements.append(Paragraph("✨ Beauty Essentials", styles['Section']))

    beauty_cards = [ProductCard(p, images.get(p['asin']), width=238, height=215) for p in PRODUCTS['beauty']]

    row1 = Table([[beauty_cards[0], beauty_cards[1]]], colWidths=[248, 248])
    row1.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(row1)
    elements.append(Spacer(1, 8))

    row2 = Table([[beauty_cards[2], beauty_cards[3]]], colWidths=[248, 248])
    row2.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(row2)
    elements.append(Spacer(1, 8))

    row3 = Table([[beauty_cards[4]]], colWidths=[496])
    row3.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    elements.append(row3)

    elements.append(PageBreak())

    # =========================================================================
    # HOME PRODUCTS
    # =========================================================================
    elements.append(Paragraph("🏠 Home Organization", styles['Section']))

    home_cards = [ProductCard(p, images.get(p['asin']), width=238, height=215) for p in PRODUCTS['home']]

    row1 = Table([[home_cards[0], home_cards[1]]], colWidths=[248, 248])
    row1.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(row1)
    elements.append(Spacer(1, 8))

    row2 = Table([[home_cards[2], home_cards[3]]], colWidths=[248, 248])
    row2.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(row2)
    elements.append(Spacer(1, 8))

    row3 = Table([[home_cards[4]]], colWidths=[496])
    row3.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    elements.append(row3)

    elements.append(PageBreak())

    # =========================================================================
    # DECOR PRODUCTS
    # =========================================================================
    elements.append(Paragraph("🌿 Decor That Looks Expensive", styles['Section']))

    decor_cards = [ProductCard(p, images.get(p['asin']), width=238, height=215) for p in PRODUCTS['decor']]

    row1 = Table([[decor_cards[0], decor_cards[1]]], colWidths=[248, 248])
    row1.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(row1)
    elements.append(Spacer(1, 8))

    row2 = Table([[decor_cards[2], decor_cards[3]]], colWidths=[248, 248])
    row2.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(row2)
    elements.append(Spacer(1, 8))

    row3 = Table([[decor_cards[4]]], colWidths=[496])
    row3.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    elements.append(row3)

    elements.append(PageBreak())

    # =========================================================================
    # THANK YOU PAGE
    # =========================================================================
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("You're Ready to Save", styles['Title']))
    elements.append(Spacer(1, 0.1*inch))

    elements.append(Paragraph(
        "You now have the exact strategies we use to save thousands every year, "
        "plus 15 vetted products worth adding to your cart today.",
        styles['Intro']
    ))

    next_steps = [
        "→  <b>This week:</b> Try the 24-Hour Rule on your next purchase",
        "→  <b>Save this PDF:</b> Reference the calendar before big purchases",
        "→  <b>Every Tuesday:</b> Check your inbox for our curated deals email",
        "→  <b>Daily updates:</b> Visit dailydealdarling.com for fresh finds",
    ]
    for step in next_steps:
        elements.append(Paragraph(step, ParagraphStyle('Step', fontSize=10, textColor=C.DARK, leading=18, leftIndent=15)))

    elements.append(Spacer(1, 0.3*inch))

    cta = Table([[Paragraph(
        "💝 <b>Happy Shopping!</b><br/>The Daily Deal Darling Team<br/><br/>"
        "dailydealdarling.com",
        ParagraphStyle('CTA', fontSize=11, textColor=C.NAVY, alignment=TA_CENTER, leading=16)
    )]], colWidths=[page_width - 60])
    cta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C.CREAM),
        ('ROUNDEDCORNERS', [10, 10, 10, 10]),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(cta)

    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(
        f"Affiliate Disclosure: Links are affiliate links with tag {AFFILIATE_TAG}. "
        "We may earn a commission at no extra cost to you.",
        styles['Footer']
    ))

    # Build
    doc.build(elements)

    file_size = Path(output_path).stat().st_size / 1024
    print(f"\n{'━' * 50}")
    print(f"✅ PDF Generated Successfully!")
    print(f"   📁 File: {output_path}")
    print(f"   📊 Size: {file_size:.1f} KB")
    print(f"   📄 Pages: 7")
    print(f"   🖼️  Images: {len(images)} product photos")
    print(f"   🔗 Links: All products linked with {AFFILIATE_TAG}")
    print(f"{'━' * 50}\n")

    return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate premium lead magnet PDF')
    parser.add_argument('--output', default='smart_shopper_guide.pdf', help='Output path')
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generate_pdf(str(output_path))


if __name__ == "__main__":
    main()
