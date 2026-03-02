#!/usr/bin/env python3
"""
Create professional product mockup images for Etsy/Gumroad listings.
Generates 4 mockup images per product:
1. Cover (main listing photo) — PDF cover with title
2. Contents preview — feature list on clean background
3. Sample page — shows actual content style
4. Who it's for — benefits summary
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

BASE = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE, "output", "mockups")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mockup canvas size (Etsy recommended 2000x2000)
W, H = 2000, 2000

PRODUCTS = [
    {
        "id": "product-1",
        "name": "AI Fitness Coach Vault",
        "subtitle": "Men Over 35 Edition",
        "tagline": "75 Prompts · 5 Programs · Discovery Call Script",
        "accent": (37, 99, 235),       # blue
        "accent_light": (219, 234, 254),
        "bg": (248, 250, 252),
        "badge": "DIGITAL PRODUCT",
        "features": [
            "75 Copy-Paste AI Prompts",
            "7 Categories: Workouts, Nutrition, Fat Loss,",
            "  Recovery, Hormones, Client Acquisition, Content",
            "5 Done-For-You Training Programs",
            "Complete Discovery Call Script",
            "Word-for-Word Objection Scripts",
            "PDF + Editable Google Doc",
            "Works with ChatGPT Free & Claude Free",
        ],
        "who": [
            "Online fitness coaches (men over 35 niche)",
            "Personal trainers who want to program faster",
            "Men over 35 using AI for their own fitness",
        ],
        "price": "$27",
    },
    {
        "id": "product-2",
        "name": "Pinterest Automation",
        "subtitle": "Blueprint",
        "tagline": "Post 15 Pins/Day on Autopilot · Real System · Not Theory",
        "accent": (220, 38, 38),        # red
        "accent_light": (254, 226, 226),
        "bg": (255, 251, 251),
        "badge": "AUTOMATION SYSTEM",
        "features": [
            "Full System Architecture Guide",
            "The Exact Claude AI Prompts (most valuable)",
            "45 Proven Pinterest Hook Frameworks",
            "Step-by-Step Make.com Setup Guide",
            "Pexels Image Selection System",
            "Content Strategy & Board SEO Guide",
            "Free Tech Stack (only cost: ~$20-40/mo Claude API)",
            "Running Live Across 3 Brands",
        ],
        "who": [
            "Pinterest marketers wanting to automate content",
            "Bloggers & affiliate marketers driving traffic",
            "Digital product sellers building Pinterest presence",
            "Developers comfortable with Python & GitHub",
        ],
        "price": "$47",
    },
    {
        "id": "product-3",
        "name": "Online Coach",
        "subtitle": "AI Client Machine",
        "tagline": "50 Prompts · Word-for-Word Scripts · Every Business Stage",
        "accent": (22, 163, 74),        # green
        "accent_light": (220, 252, 231),
        "bg": (250, 255, 252),
        "badge": "COACHING TOOLS",
        "features": [
            "50 Copy-Paste AI Prompts",
            "7 Stages: Discovery, Sales, Instagram, Email,",
            "  Onboarding, Retention, Operations",
            "Full DM → Discovery Call Sequence",
            "How to Say the Price Confidently",
            "5 Objection Scripts (word-for-word)",
            "Offboarding & Referral Scripts",
            "PDF + Editable Google Doc",
        ],
        "who": [
            "Online fitness, life & nutrition coaches",
            "Coaches making $2-10k/month who want to scale",
            "New coaches unsure what to say and when",
            "Anyone spending 2+ hours/day writing emails",
        ],
        "price": "$17",
    },
    {
        "id": "lead-magnet",
        "name": "FREE: 5 AI Prompts",
        "subtitle": "That Save Fitness Coaches 5 Hours a Week",
        "tagline": "Free Download · Instant Access · No Email Required",
        "accent": (147, 51, 234),       # purple
        "accent_light": (243, 232, 255),
        "bg": (253, 251, 255),
        "badge": "FREE DOWNLOAD",
        "features": [
            "Reply to Instagram DMs (sounds human, not scripted)",
            "Create a week of content in 10 minutes",
            "Build a 4-week client program from scratch",
            "Write check-in emails that get responses",
            "Turn any blog post into 3 Pinterest pin titles",
            "",
            "Taken from the full 75-prompt AI Fitness Coach Vault",
        ],
        "who": [
            "Fitness coaches wanting to try AI prompts free",
            "Personal trainers new to ChatGPT or Claude",
            "Anyone curious what good prompts look like",
        ],
        "price": "FREE",
    },
]


def load_font(size, bold=False):
    """Try to load a system font, fall back to default."""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=2):
    """Draw a rectangle with rounded corners."""
    x1, y1, x2, y2 = xy
    if fill:
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)
    else:
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, outline=outline, width=width)


def make_cover(product):
    """Mockup 1: Product cover — main listing photo."""
    img = Image.new("RGB", (W, H), product["bg"])
    draw = ImageDraw.Draw(img)

    accent = product["accent"]
    accent_light = product["accent_light"]

    # Background accent block (top 45%)
    draw.rectangle([0, 0, W, int(H * 0.45)], fill=accent)

    # Subtle dot pattern in accent block
    for x in range(0, W, 60):
        for y in range(0, int(H * 0.45), 60):
            draw.ellipse([x-3, y-3, x+3, y+3], fill=tuple(min(255, c+30) for c in accent))

    # White card in center
    card_margin = 100
    card_top = int(H * 0.15)
    card_bottom = int(H * 0.88)
    draw.rounded_rectangle(
        [card_margin, card_top, W - card_margin, card_bottom],
        radius=24, fill="white",
        outline=(229, 231, 235), width=2
    )

    # Badge pill
    badge_font = load_font(28)
    badge_text = product["badge"]
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    badge_w = bbox[2] - bbox[0] + 48
    badge_h = 52
    badge_x = W // 2 - badge_w // 2
    badge_y = card_top + 60
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=100, fill=accent_light
    )
    draw.text(
        (W // 2, badge_y + badge_h // 2),
        badge_text,
        font=badge_font,
        fill=accent,
        anchor="mm"
    )

    # Product name (big)
    name_font = load_font(88, bold=True)
    name_y = badge_y + badge_h + 55
    # Wrap long names
    name_lines = []
    words = product["name"].split()
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=name_font)
        if bbox[2] - bbox[0] > W - card_margin * 2 - 80:
            if line:
                name_lines.append(line)
            line = word
        else:
            line = test
    if line:
        name_lines.append(line)

    for i, ln in enumerate(name_lines):
        draw.text((W // 2, name_y + i * 100), ln, font=name_font, fill=(17, 24, 39), anchor="mt")

    # Subtitle
    sub_font = load_font(52)
    sub_y = name_y + len(name_lines) * 100 + 20
    draw.text((W // 2, sub_y), product["subtitle"], font=sub_font, fill=(107, 114, 128), anchor="mt")

    # Accent divider line
    div_y = sub_y + 80
    draw.rectangle([W // 2 - 50, div_y, W // 2 + 50, div_y + 6], fill=accent)

    # Tagline
    tag_font = load_font(38)
    tag_y = div_y + 50
    draw.text((W // 2, tag_y), product["tagline"], font=tag_font, fill=(75, 85, 99), anchor="mt")

    # Feature pills in the card middle
    feat_items = [f for f in product["features"] if f and not f.startswith("  ")][:4]
    pill_y = tag_y + 80
    for feat in feat_items:
        pill_font = load_font(30)
        fb = draw.textbbox((0, 0), feat, font=pill_font)
        pill_w = fb[2] - fb[0] + 48
        pill_h = 50
        pill_x = W // 2 - pill_w // 2
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=100, fill=accent_light, outline=accent, width=1)
        draw.text((W // 2, pill_y + pill_h // 2), feat, font=pill_font, fill=accent, anchor="mm")
        pill_y += 70

    # Price badge (bottom of card)
    price_font = load_font(64, bold=True)
    price_y = card_bottom - 120
    price_text = product["price"]
    price_bbox = draw.textbbox((0, 0), price_text, font=price_font)
    price_w = price_bbox[2] - price_bbox[0] + 80
    price_h = 90
    price_x = W // 2 - price_w // 2
    draw.rounded_rectangle(
        [price_x, price_y - 10, price_x + price_w, price_y - 10 + price_h],
        radius=12, fill=accent
    )
    draw.text((W // 2, price_y + price_h // 2 - 10), price_text, font=price_font, fill="white", anchor="mm")

    # Brand footer
    footer_font = load_font(32)
    draw.text((W // 2, card_bottom + 40), "fitover35.com · ISSA Certified Personal Trainer", font=footer_font, fill=(156, 163, 175), anchor="mt")

    return img


def make_features(product):
    """Mockup 2: Feature list — what's inside."""
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    accent = product["accent"]
    accent_light = product["accent_light"]

    # Left accent sidebar
    draw.rectangle([0, 0, 12, H], fill=accent)

    # Header section
    draw.rectangle([0, 0, W, 280], fill=accent)

    # "WHAT'S INSIDE" label
    label_font = load_font(32)
    draw.text((W // 2, 70), "WHAT'S INSIDE", font=label_font, fill=(255, 255, 255, 180), anchor="mt")

    name_font = load_font(72, bold=True)
    draw.text((W // 2, 120), product["name"], font=name_font, fill="white", anchor="mt")

    sub_font = load_font(42)
    draw.text((W // 2, 210), product["subtitle"], font=sub_font, fill=(255, 255, 255, 200), anchor="mt")

    # Features list
    feat_font = load_font(44)
    small_font = load_font(36)
    y = 340
    for feat in product["features"]:
        if feat == "":
            y += 30
            continue
        is_continuation = feat.startswith("  ")
        feat_clean = feat.strip()
        if not is_continuation:
            # Checkmark circle
            cx, cy = 80, y + 22
            draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=accent_light)
            draw.text((cx, cy), "✓", font=load_font(28), fill=accent, anchor="mm")
            draw.text((120, y), feat_clean, font=feat_font, fill=(17, 24, 39))
        else:
            draw.text((120, y), feat_clean, font=small_font, fill=(107, 114, 128))
        y += 72 if not is_continuation else 55

    # Bottom strip
    draw.rectangle([0, H - 120, W, H], fill=accent_light)
    footer_font = load_font(36)
    draw.text((W // 2, H - 60), f"PDF + Editable Google Doc · Works with ChatGPT & Claude", font=footer_font, fill=accent, anchor="mm")

    return img


def make_sample(product):
    """Mockup 3: Sample content preview."""
    img = Image.new("RGB", (W, H), (249, 250, 251))
    draw = ImageDraw.Draw(img)

    accent = product["accent"]
    accent_light = product["accent_light"]

    # Header
    draw.rectangle([0, 0, W, 200], fill=accent)
    hdr_font = load_font(52, bold=True)
    draw.text((W // 2, 100), "SAMPLE PROMPT FROM THE VAULT", font=hdr_font, fill="white", anchor="mm")

    # Prompt card
    card_top = 260
    card_bottom = H - 280
    draw.rounded_rectangle([80, card_top, W - 80, card_bottom], radius=20, fill="white", outline=(229, 231, 235), width=2)

    # Left accent border on card
    draw.rounded_rectangle([80, card_top, 92, card_bottom], radius=8, fill=accent)

    # Prompt label
    lbl_font = load_font(30)
    draw.text((130, card_top + 40), "COPY-PASTE PROMPT  ·  CLIENT PROGRAM BUILDER", font=lbl_font, fill=(107, 114, 128))

    # Divider
    draw.rectangle([130, card_top + 90, W - 130, card_top + 93], fill=(229, 231, 235))

    # Prompt text
    prompt_text = [
        'Design a 4-week training program for a [AGE]-year-old',
        'man with [INJURY/LIMITATION]. He trains [X] days/week,',
        'has [EQUIPMENT], and his main goal is [GOAL].',
        '',
        'Include:',
        '• Modifications for the injury/limitation',
        '• A note on deload timing for natural lifters his age',
        '• Realistic progression expectations',
        '• Exercise substitutions if needed',
        '',
        'Format: weekly table with sets, reps, rest, and notes.',
    ]

    p_font = load_font(38)
    py = card_top + 130
    for line in prompt_text:
        if line == "":
            py += 30
            continue
        draw.text((140, py), line, font=p_font, fill=(31, 41, 55))
        py += 58

    # "Copy this into" note
    note_font = load_font(34)
    draw.rounded_rectangle([130, py + 20, W - 130, py + 90], radius=10, fill=accent_light)
    draw.text((W // 2, py + 55), "Copy this into ChatGPT or Claude → get a full program in minutes", font=note_font, fill=accent, anchor="mm")

    # Footer
    footer_bg_y = H - 220
    draw.rectangle([0, footer_bg_y, W, H], fill=accent)
    f1_font = load_font(42, bold=True)
    f2_font = load_font(34)
    draw.text((W // 2, footer_bg_y + 60), product["name"], font=f1_font, fill="white", anchor="mt")
    draw.text((W // 2, footer_bg_y + 120), product["tagline"], font=f2_font, fill=(255, 255, 255), anchor="mt")

    return img


def make_who(product):
    """Mockup 4: Who it's for + social proof."""
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    accent = product["accent"]
    accent_light = product["accent_light"]

    # Top header
    draw.rounded_rectangle([0, 0, W, 240], radius=0, fill=accent)
    h_font = load_font(62, bold=True)
    draw.text((W // 2, 120), "WHO THIS IS FOR", font=h_font, fill="white", anchor="mm")

    # Divider strip
    draw.rectangle([0, 240, W, 258], fill=accent_light)

    # Who list
    who_y = 310
    for person in product["who"]:
        # Person icon circle
        cx, cy = 100, who_y + 34
        draw.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=accent)
        draw.text((cx, cy), "✓", font=load_font(34), fill="white", anchor="mm")

        # Text
        w_font = load_font(46)
        draw.text((170, who_y + 10), person, font=w_font, fill=(17, 24, 39))
        who_y += 110

    # Separator
    sep_y = who_y + 30
    draw.rectangle([80, sep_y, W - 80, sep_y + 3], fill=(229, 231, 235))

    # Compatibility section
    compat_y = sep_y + 60
    comp_title_font = load_font(40, bold=True)
    draw.text((W // 2, compat_y), "COMPATIBLE WITH", font=comp_title_font, fill=(107, 114, 128), anchor="mt")

    compat_items = ["ChatGPT (Free)", "ChatGPT Plus (GPT-4)", "Claude Free", "Claude Pro"]
    item_font = load_font(38)
    item_y = compat_y + 70
    item_x = 200
    for item in compat_items:
        draw.rounded_rectangle([item_x - 10, item_y - 8, item_x + 320, item_y + 52], radius=10, fill=accent_light)
        draw.text((item_x + 10, item_y + 22), item, font=item_font, fill=accent, anchor="lm")
        item_x += 380
        if item_x > W - 400:
            item_x = 200
            item_y += 90

    # Price + CTA at bottom
    cta_y = H - 300
    draw.rounded_rectangle([80, cta_y, W - 80, H - 60], radius=20, fill=accent)

    price_font = load_font(90, bold=True)
    draw.text((W // 2, cta_y + 60), product["price"], font=price_font, fill="white", anchor="mt")

    cta_font = load_font(42)
    draw.text((W // 2, cta_y + 170), "Instant PDF + Google Doc Download", font=cta_font, fill=(255, 255, 255), anchor="mt")
    draw.text((W // 2, cta_y + 220), "fitover35.com", font=cta_font, fill=(255, 255, 255), anchor="mt")

    return img


def build_product_mockups(product):
    print(f"\nBuilding mockups: {product['name']}")
    prefix = product["id"]

    imgs = [
        (make_cover(product), f"{prefix}-1-cover.png"),
        (make_features(product), f"{prefix}-2-features.png"),
        (make_sample(product), f"{prefix}-3-sample.png"),
        (make_who(product), f"{prefix}-4-who.png"),
    ]

    for img, filename in imgs:
        path = os.path.join(OUTPUT_DIR, filename)
        img.save(path, "PNG", optimize=True)
        size_kb = os.path.getsize(path) // 1024
        print(f"  ✓ {filename} ({size_kb}K)")


if __name__ == "__main__":
    print(f"Creating mockup images in prompt-packs/output/mockups/")
    for product in PRODUCTS:
        build_product_mockups(product)

    # Count total
    files = os.listdir(OUTPUT_DIR)
    print(f"\n{'='*50}")
    print(f"✅ Created {len(files)} mockup images")
    print(f"Location: prompt-packs/output/mockups/")
