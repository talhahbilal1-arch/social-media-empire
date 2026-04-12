"""Nano Banana — AI-generated Pinterest pin images via Gemini 2.5 Flash Image.

Design principles (2026 best practices):
- Gemini generates the BACKGROUND art only (no text in AI image — unreliable)
- PIL stamps all text overlays for pixel-perfect readability
- Brand-specific gradient tints, hex colors, and CTA copy
- 50+ headline templates per brand for maximum variety

Usage:
    from video_automation.nano_banana_generator import generate_pin_image, generate_pin_batch
    img_bytes = generate_pin_image('fitness', 'Best strength exercises for men over 35')
    pins = generate_pin_batch('deals', ['topic1', 'topic2'], count=5)
"""

import io
import logging
import os
import random
import time

logger = logging.getLogger(__name__)

# ── Font paths ───────────────────────────────────────────────────────────────
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_BOLD = os.path.join(_REPO_ROOT, "assets", "fonts", "Montserrat-Bold.ttf")
FONT_EXTRABOLD = os.path.join(_REPO_ROOT, "assets", "fonts", "Montserrat-ExtraBold.ttf")
FONT_MEDIUM = os.path.join(_REPO_ROOT, "assets", "fonts", "Montserrat-Medium.ttf")

# ── Gemini model ─────────────────────────────────────────────────────────────
IMAGE_MODEL = "gemini-2.5-flash-preview-image-generation"

# ── Pin canvas ───────────────────────────────────────────────────────────────
PIN_W, PIN_H = 1000, 1500

# ── Brand visual identity ────────────────────────────────────────────────────
BRAND_CONFIGS = {
    "fitness": {
        "name": "FitOver35",
        "url": "fitover35.com",
        "primary": (232, 85, 58),      # #E8553A deep orange
        "accent": (255, 107, 107),     # #FF6B6B coral
        "text": (255, 255, 255),       # white
        "gradient_tint": (232, 85, 58, 180),   # coral overlay RGBA
        "cta": "Save This Workout 💪",
        "audience": "men over 35 who train seriously",
        "image_style": (
            "A clean, bright gym or outdoor fitness background with NO TEXT. "
            "Dominant colors: warm coral (#FF6B6B), deep orange (#E8553A), charcoal black. "
            "Leave the top 30% and bottom 30% visually darker/clear for text overlays. "
            "Subject centered. Athletic, energetic, masculine sports-magazine aesthetic. "
            "Uncluttered composition, minimal background distractions. "
            "NO watermarks, NO logos, NO text, NO borders."
        ),
    },
    "deals": {
        "name": "DailyDealDarling",
        "url": "dailydealdarling.com",
        "primary": (46, 204, 113),     # #2ECC71 emerald
        "accent": (241, 196, 15),      # #F1C40F gold
        "text": (255, 255, 255),       # white
        "gradient_tint": (27, 120, 66, 180),   # deep green RGBA
        "cta": "Shop Now Before It's Gone! 🛒",
        "audience": "savvy home shoppers hunting Amazon deals",
        "image_style": (
            "A clean, bright lifestyle flat-lay or product photo with NO TEXT. "
            "Dominant colors: emerald green (#2ECC71), warm gold (#F1C40F), cream white. "
            "Leave the top 30% and bottom 30% visually darker/clear for text overlays. "
            "Products beautifully arranged, modern minimal aesthetic. "
            "Deal-tag energy: clean, appealing, aspirational. "
            "NO watermarks, NO logos, NO text, NO price tags, NO borders."
        ),
    },
    "menopause": {
        "name": "MenopausePlanner",
        "url": "menopause-planner-website.vercel.app",
        "primary": (155, 89, 182),     # #9B59B6 purple
        "accent": (26, 188, 156),      # #1ABC9C teal
        "text": (255, 255, 255),       # white
        "gradient_tint": (90, 50, 130, 170),   # deep purple RGBA
        "cta": "Save for Your Wellness Journey 🌿",
        "audience": "women navigating perimenopause and menopause",
        "image_style": (
            "A calm, soothing wellness scene with NO TEXT. "
            "Dominant colors: soft purple (#9B59B6), teal (#1ABC9C), lavender (#BB8FCE), warm cream. "
            "Leave the top 30% and bottom 30% visually darker/clear for text overlays. "
            "Natural light, botanical elements, calming wellness aesthetic. "
            "Could feature: herbal tea, candles, nature, a relaxed woman (no face required). "
            "NO watermarks, NO logos, NO text, NO borders."
        ),
    },
}

# ── Headline templates (50+ per brand) ──────────────────────────────────────
FITNESS_HEADLINES = [
    "5 Quick {topic} Moves for Men 35+",
    "At-Home {topic} (No Equipment Needed)",
    "Stop Doing {topic} Wrong — Here's How",
    "{topic} Tips That Actually Work After 35",
    "The Real Way to Master {topic}",
    "Build Strength With {topic} in 20 Min",
    "Why {topic} Changes After 35 (And What to Do)",
    "{topic}: The Over-35 Man's Guide",
    "Boost Your {topic} Without the Gym",
    "7 {topic} Mistakes Men Over 35 Make",
    "The {topic} Workout Men Swear By",
    "{topic} for Fat Loss After 35",
    "Get Stronger With {topic} Today",
    "No More Excuses — Do This {topic} Routine",
    "{topic}: Science-Backed Tips for Men",
    "Daily {topic} Habit That Transforms Your Body",
    "Fix Your {topic} Form Instantly",
    "The Lazy Man's Guide to {topic}",
    "How to Recover Faster After {topic}",
    "{topic} Without Hurting Your Joints",
    "Beginner's {topic} Plan That Actually Works",
    "The 10-Min {topic} You'll Actually Stick To",
    "Why Your {topic} Isn't Working (Fix This)",
    "{topic} Secrets Top Trainers Won't Tell You",
    "Double Your {topic} Results With These Hacks",
    "Men Over 35: Master {topic} This Week",
    "Simple {topic} Tweaks = Big Results",
    "Level Up Your {topic} Game Starting Now",
    "The Weekend Warrior's {topic} Blueprint",
    "Proven {topic} Methods for Busy Dads",
    "Build Muscle With {topic} After 40",
    "Drop 10 lbs With This {topic} Trick",
    "The {topic} Protocol That Works Fast",
    "What No One Tells You About {topic}",
    "3-Day {topic} Plan for Maximum Gains",
    "Morning {topic} Routine for All-Day Energy",
    "The Anti-Aging Power of {topic}",
    "Boost Testosterone Naturally With {topic}",
    "Smart {topic} Strategy for Men Over 35",
    "The {topic} Cheat Sheet for Beginners",
    "{topic} Guide: Week 1 Through Week 12",
    "How Elite Athletes Approach {topic}",
    "Low-Impact {topic} That Still Burns Fat",
    "The {topic} Reset Every Man Needs",
    "Crush {topic} With Less Time in the Gym",
    "5-Minute {topic} Fix You Can Do Anywhere",
    "This {topic} Routine Changed Everything",
    "The Truth About {topic} After 35",
    "Master {topic} in Just 30 Days",
    "The {topic} Blueprint for Real Results",
]

DEALS_HEADLINES = [
    "Amazon's Hidden {topic} Deal — Today Only!",
    "Up to 60% Off {topic} Right Now 🛍️",
    "The Best {topic} Under $30 on Amazon",
    "This {topic} Deal Won't Last Long",
    "Shoppers Are Obsessed With This {topic}",
    "I Found the Best {topic} Deal of the Week",
    "Save Big on {topic} Before It Sells Out",
    "Amazon's #1 {topic} Is on Sale Now",
    "Budget {topic} That Looks Expensive",
    "The {topic} Everyone Is Buying in 2026",
    "Score This {topic} at Half Price!",
    "The {topic} You Need for Your Home",
    "Viral {topic} on Amazon — And It's Cheap",
    "The Best-Reviewed {topic} Under $50",
    "Why Everyone Is Buying This {topic}",
    "Flash Sale: {topic} at 40% Off Today",
    "This {topic} Organizes Everything Instantly",
    "Amazon Deal Alert: {topic} at Rock-Bottom Price",
    "The {topic} That Sold Out Last Week Is Back",
    "Upgrade Your Home With This {topic} Deal",
    "The {topic} Hack That Saves You Money",
    "Today's Best {topic} Deal on Amazon",
    "Affordable {topic} That Doesn't Feel Cheap",
    "{topic}: The Smart Shopper's Find of the Week",
    "This {topic} Is Going Viral — And for Good Reason",
    "The {topic} Deal I Wish I Found Sooner",
    "Limited Stock: {topic} at This Price",
    "The {topic} That Makes Life So Much Easier",
    "Under $20: The {topic} You Didn't Know You Needed",
    "5-Star {topic} for Less Than You Think",
    "The {topic} Upgrade Your Home Deserves",
    "Amazon Prime Members: {topic} on Sale Now",
    "The {topic} Deal That Breaks the Internet",
    "Get This {topic} Before the Price Goes Back Up",
    "Home Edit Approved: This {topic} Is a Game-Changer",
    "The {topic} That Makes Cleaning Actually Fun",
    "Organize Everything With This {topic} Find",
    "The {topic} Every Homeowner Needs",
    "Your {topic} Budget Just Got Better",
    "The {topic} Mom Groups Won't Stop Talking About",
    "Amazon's Bestselling {topic} Now On Sale",
    "The {topic} Deal of the Season",
    "How to Get {topic} for Less This Week",
    "The Clever {topic} Find That Went Viral",
    "This {topic} Restores Order to Any Home",
    "Get Organized With This {topic} for Less",
    "Budget-Friendly {topic} That Looks Luxe",
    "The {topic} That Pays for Itself Instantly",
    "Deal of the Day: {topic} Marked Way Down",
    "The {topic} Thousands of Reviewers Love",
]

MENOPAUSE_HEADLINES = [
    "Natural Relief for {topic} — What Works",
    "5 Tips for Managing {topic} Naturally",
    "The {topic} Guide Every Woman Needs at 45+",
    "How to Ease {topic} Without Hormones",
    "Doctor-Approved Ways to Handle {topic}",
    "The {topic} Symptom No One Talks About",
    "Reclaim Your Life: Managing {topic} in Midlife",
    "Simple {topic} Fixes That Actually Help",
    "{topic} and Menopause: What You Need to Know",
    "The Hormone Hack for {topic} Relief",
    "Why {topic} Gets Worse in Perimenopause",
    "5 Women Share Their {topic} Success Stories",
    "The {topic} Routine That Changed Everything",
    "Your {topic} Symptom Checklist for 2026",
    "Science-Backed {topic} Relief You Can Start Today",
    "Beat {topic} With These Lifestyle Changes",
    "The {topic} Plan for Midlife Women",
    "How I Finally Beat {topic} Naturally",
    "3 Foods That Make {topic} Worse (Avoid These)",
    "{topic} and Sleep: What No One Tells You",
    "The Truth About {topic} During Perimenopause",
    "Gentle {topic} Solutions for Sensitive Women",
    "My {topic} Journey: What Finally Worked",
    "The {topic} Supplement That Actually Works",
    "Ease {topic} With This Morning Ritual",
    "The Midlife Woman's {topic} Survival Guide",
    "Finding Balance: {topic} Solutions That Last",
    "Holistic {topic} Remedies Backed by Research",
    "{topic} Myths Busted by Menopause Experts",
    "The {topic} Protocol Women Are Raving About",
    "Natural vs. Medical {topic} Treatment — The Truth",
    "Calm Your {topic} With These Daily Habits",
    "Why {topic} Is Different After 50",
    "The {topic} Reset for Menopausal Women",
    "Manage {topic} With This Wellness Routine",
    "The {topic} Conversation You Need to Have with Your Doctor",
    "From Overwhelmed to Thriving: {topic} Tips",
    "Build Your {topic} Support System Today",
    "The 7-Day {topic} Relief Challenge",
    "Empower Yourself: Understanding Your {topic}",
    "The {topic} Approach That Restored My Energy",
    "What Works (and What Doesn't) for {topic}",
    "The Midlife {topic} Blueprint for Women",
    "Live Better: Your {topic} Action Plan",
    "{topic} Relief Without Side Effects",
    "The {topic} Solution Your Doctor Hasn't Told You",
    "Thrive Through {topic} — Real Strategies That Help",
    "Why {topic} Spikes During Perimenopause",
    "The {topic} Journal That Changed My Symptoms",
    "Take Back Control: {topic} Tools That Work",
]

BRAND_HEADLINES = {
    "fitness": FITNESS_HEADLINES,
    "deals": DEALS_HEADLINES,
    "menopause": MENOPAUSE_HEADLINES,
}

# ── Pexels fallback ──────────────────────────────────────────────────────────
_PEXELS_FALLBACK = {
    "fitness": "man fitness workout gym strength",
    "deals": "home organisation modern minimal products",
    "menopause": "wellness calm nature woman relaxed",
}


# ── Gemini client ────────────────────────────────────────────────────────────

def _get_client():
    try:
        from video_automation.gemini_client import get_client
        return get_client()
    except Exception:
        from google import genai
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        return genai.Client(api_key=api_key)


# ── Prompt builder ───────────────────────────────────────────────────────────

def _build_prompt(brand: str, topic: str, variation: int = 0) -> str:
    """Brand-specific Gemini prompt — NO TEXT in the generated image."""
    cfg = BRAND_CONFIGS[brand]
    angle = ["straight-on", "slightly above", "close-up detail"][variation % 3]
    return (
        f"Create a professional Pinterest pin background image at portrait 2:3 ratio (1000x1500px). "
        f"Shot angle: {angle}. "
        f"Topic inspiration: {topic}. "
        f"{cfg['image_style']} "
        f"The image will have text overlaid by a separate tool — leave clear negative space "
        f"at the top 25% and bottom 30% of the image (darker, blurred, or plain background there). "
        f"Center the main visual subject in the middle 45% of the frame. "
        f"High resolution, photorealistic or high-quality digital art. "
        f"Vibrant but not oversaturated. Professional studio quality."
    )


# ── Headline generation ──────────────────────────────────────────────────────

def _pick_headline(brand: str, topic: str, used: set) -> str:
    """Pick an unused headline template and fill in {topic}."""
    templates = BRAND_HEADLINES.get(brand, FITNESS_HEADLINES)
    # Normalize topic to title case, max 3 words
    short_topic = " ".join(topic.split()[:4]).title()
    available = [t for t in templates if t not in used]
    if not available:
        available = templates  # reset if all used
    template = random.choice(available)
    used.add(template)
    headline = template.format(topic=short_topic)
    # Cap at 7 words
    words = headline.split()
    if len(words) > 7:
        headline = " ".join(words[:7])
    return headline


# ── PIL overlay ──────────────────────────────────────────────────────────────

def _load_font(path: str, size: int):
    """Load a TTF font, falling back to PIL default if missing."""
    from PIL import ImageFont
    if os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _add_gradient_overlay(img):
    """Add semi-transparent dark gradient at top 25% and bottom 30%."""
    from PIL import Image
    import struct

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    w, h = img.size
    pixels = overlay.load()

    top_zone = int(h * 0.28)
    bottom_start = int(h * 0.68)

    for y in range(h):
        if y <= top_zone:
            # Dark at top edge → transparent toward middle
            alpha = int(200 * (1 - y / top_zone))
            for x in range(w):
                pixels[x, y] = (0, 0, 0, alpha)
        elif y >= bottom_start:
            # Transparent at bottom_start → dark at bottom edge
            progress = (y - bottom_start) / (h - bottom_start)
            alpha = int(210 * progress)
            for x in range(w):
                pixels[x, y] = (0, 0, 0, alpha)

    return Image.alpha_composite(img.convert("RGBA"), overlay)


def _draw_cta_button(draw, cfg: dict, y_pos: int, width: int):
    """Draw a pill-shaped CTA button with brand accent color."""
    from PIL import ImageDraw

    cta_text = cfg["cta"]
    font = _load_font(FONT_BOLD, 26)
    # Measure text
    try:
        bbox = draw.textbbox((0, 0), cta_text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except AttributeError:
        tw, th = draw.textsize(cta_text, font=font)

    pad_x, pad_y = 36, 14
    btn_w = tw + pad_x * 2
    btn_h = th + pad_y * 2
    btn_x = (width - btn_w) // 2
    btn_y = y_pos

    r = btn_h // 2  # pill radius
    accent = cfg["accent"]
    draw.rounded_rectangle(
        [btn_x, btn_y, btn_x + btn_w, btn_y + btn_h],
        radius=r,
        fill=accent,
    )
    # White text centered
    text_x = btn_x + pad_x
    text_y = btn_y + pad_y
    draw.text((text_x, text_y), cta_text, font=font, fill=(255, 255, 255))
    return btn_y + btn_h


def add_text_overlay(image_bytes: bytes, brand: str, headline: str, subtext: str = "") -> bytes:
    """Stamp brand-specific text overlay onto the pin image.

    Args:
        image_bytes: Raw image bytes (JPEG or PNG)
        brand: Brand key
        headline: Main pin headline (max 7 words)
        subtext: Optional supporting tip/tagline

    Returns:
        PNG bytes with overlay applied
    """
    from PIL import Image, ImageDraw

    cfg = BRAND_CONFIGS[brand]
    img = Image.open(io.BytesIO(image_bytes)).resize((PIN_W, PIN_H), Image.LANCZOS)
    img = _add_gradient_overlay(img).convert("RGB")
    draw = ImageDraw.Draw(img)

    # ── Headline ─────────────────────────────────────────────────────────────
    headline_font = _load_font(FONT_EXTRABOLD, 72)
    # Word-wrap to 2 lines max
    words = headline.split()
    mid = len(words) // 2
    line1 = " ".join(words[:mid]) if mid else headline
    line2 = " ".join(words[mid:]) if mid else ""
    lines = [line1, line2] if line2 else [headline]

    # Position in upper third
    y = 80
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=headline_font)
            tw = bbox[2] - bbox[0]
        except AttributeError:
            tw, _ = draw.textsize(line, font=headline_font)
        x = (PIN_W - tw) // 2
        # Shadow
        draw.text((x + 3, y + 3), line, font=headline_font, fill=(0, 0, 0, 180))
        # Main text
        draw.text((x, y), line, font=headline_font, fill=cfg["text"])
        y += 88

    # ── Subtext ───────────────────────────────────────────────────────────────
    if subtext:
        sub_font = _load_font(FONT_MEDIUM, 32)
        sub = subtext[:60]  # cap length
        try:
            bbox = draw.textbbox((0, 0), sub, font=sub_font)
            tw = bbox[2] - bbox[0]
        except AttributeError:
            tw, _ = draw.textsize(sub, font=sub_font)
        x = (PIN_W - tw) // 2
        draw.text((x + 2, y + 2), sub, font=sub_font, fill=(0, 0, 0, 160))
        draw.text((x, y), sub, font=sub_font, fill=(220, 220, 220))

    # ── CTA button ───────────────────────────────────────────────────────────
    cta_y = PIN_H - 210
    _draw_cta_button(draw, cfg, cta_y, PIN_W)

    # ── Brand name + URL ─────────────────────────────────────────────────────
    brand_font = _load_font(FONT_BOLD, 20)
    brand_line = f"{cfg['name']}  •  {cfg['url']}"
    try:
        bbox = draw.textbbox((0, 0), brand_line, font=brand_font)
        tw = bbox[2] - bbox[0]
    except AttributeError:
        tw, _ = draw.textsize(brand_line, font=brand_font)
    bx = (PIN_W - tw) // 2
    draw.text((bx, PIN_H - 52), brand_line, font=brand_font, fill=(200, 200, 200))

    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


# ── Core generation ──────────────────────────────────────────────────────────

def generate_pin_image(brand: str, topic: str, style: str = "default",
                       variation: int = 0, headline: str = "") -> bytes:
    """Generate a Pinterest pin image: Gemini background + PIL text overlay.

    Args:
        brand: Brand key — 'fitness', 'deals', or 'menopause'
        topic: Pin topic
        style: Reserved for future use
        variation: 0-4 prompt variation for batch diversity
        headline: Pre-computed headline (generated if empty)

    Returns:
        PNG image bytes ready for Supabase Storage upload
    """
    from google.genai import types

    if brand not in BRAND_CONFIGS:
        brand = "fitness"

    used_headlines: set = set()
    if not headline:
        headline = _pick_headline(brand, topic, used_headlines)

    client = _get_client()
    prompt = _build_prompt(brand, topic, variation)
    last_error = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=IMAGE_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"]
                ),
            )
            for candidate in response.candidates or []:
                for part in candidate.content.parts or []:
                    if hasattr(part, "inline_data") and part.inline_data:
                        raw = part.inline_data.data
                        if isinstance(raw, str):
                            import base64
                            raw = base64.b64decode(raw)
                        if raw:
                            logger.info(f"[{brand}] Gemini background generated ({len(raw)} bytes)")
                            # Apply PIL text overlay
                            final = add_text_overlay(raw, brand, headline, "")
                            logger.info(f"[{brand}] PIL overlay applied → {len(final)} bytes")
                            return final
            raise RuntimeError("Gemini returned no image data")
        except Exception as e:
            last_error = e
            wait = 2 ** attempt
            logger.warning(f"[{brand}] Gemini attempt {attempt + 1}/3 failed: {e} — retry in {wait}s")
            if attempt < 2:
                time.sleep(wait)

    logger.warning(f"[{brand}] Gemini failed ({last_error}), falling back to Pexels")
    return _pexels_fallback_with_overlay(brand, topic, headline)


def _pexels_fallback_with_overlay(brand: str, topic: str, headline: str) -> bytes:
    """Fetch a Pexels image, apply PIL overlay, return PNG bytes."""
    import requests

    api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        raise RuntimeError(f"[{brand}] Gemini and Pexels both unavailable (no PEXELS_API_KEY)")

    query = _PEXELS_FALLBACK.get(brand, topic)
    resp = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": api_key},
        params={"query": query, "per_page": 10, "orientation": "portrait"},
        timeout=15,
    )
    resp.raise_for_status()
    photos = resp.json().get("photos", [])
    if not photos:
        raise RuntimeError(f"[{brand}] Pexels returned no photos for '{query}'")

    photo = random.choice(photos[:5])
    img_resp = requests.get(photo["src"]["large2x"], timeout=30)
    img_resp.raise_for_status()
    return add_text_overlay(img_resp.content, brand, headline, "")


def _generate_metadata(brand: str, topic: str) -> dict:
    """Generate Pinterest-optimized title and description via Gemini text."""
    try:
        from video_automation.gemini_client import generate_json
        import json

        cfg = BRAND_CONFIGS[brand]
        prompt = (
            f"Generate a Pinterest pin title and description.\n"
            f"Topic: {topic}\nBrand: {cfg['name']} ({cfg['audience']})\n"
            f"- Title: 50-80 chars, keyword-rich, compelling, no clickbait\n"
            f"- Description: 150-250 chars, 3-5 relevant hashtags at the end\n"
            f'Return ONLY valid JSON: {{"title": "...", "description": "..."}}'
        )
        data = json.loads(generate_json(prompt, max_tokens=300))
        return {"title": data.get("title", topic[:80]), "description": data.get("description", topic)}
    except Exception as e:
        logger.warning(f"[{brand}] Metadata generation failed: {e}")
        return {"title": topic[:80], "description": topic}


def generate_pin_batch(brand: str, topics: list, count: int = 5) -> list:
    """Generate a batch of Pinterest pins with AI backgrounds + PIL overlays.

    Args:
        brand: Brand key — 'fitness', 'deals', or 'menopause'
        topics: List of topic strings (cycled if fewer than count)
        count: Number of pins to generate

    Returns:
        List of dicts: image_bytes, topic, title, description, filename, headline
    """
    import datetime

    if not topics:
        topics = [brand]

    selected = [topics[i % len(topics)] for i in range(count)]
    results = []
    used_headlines: set = set()

    for i, topic in enumerate(selected):
        try:
            headline = _pick_headline(brand, topic, used_headlines)
            image_bytes = generate_pin_image(brand, topic, variation=i, headline=headline)
            metadata = _generate_metadata(brand, topic)
            timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            results.append({
                "image_bytes": image_bytes,
                "topic": topic,
                "headline": headline,
                "title": metadata["title"],
                "description": metadata["description"],
                "filename": f"{brand}_nb_{i}_{timestamp}.png",
            })
            logger.info(f"[{brand}] Pin {i + 1}/{count}: '{headline[:50]}'")
        except Exception as e:
            logger.error(f"[{brand}] Pin {i + 1} failed for '{topic}': {e}")

    return results


def save_samples(brand: str, topics: list, count: int = 3, out_dir: str = "samples") -> list:
    """Generate and save sample pins locally for quality review.

    Args:
        brand: Brand key
        topics: Topics to use
        count: How many samples to save
        out_dir: Output directory (created if absent)

    Returns:
        List of saved file paths
    """
    import datetime

    os.makedirs(out_dir, exist_ok=True)
    pins = generate_pin_batch(brand, topics, count=count)
    paths = []
    for pin in pins:
        ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        fname = f"{out_dir}/{brand}_{ts}_{len(paths)}.png"
        with open(fname, "wb") as f:
            f.write(pin["image_bytes"])
        logger.info(f"Sample saved: {fname}  headline='{pin['headline']}'")
        paths.append(fname)
    return paths
