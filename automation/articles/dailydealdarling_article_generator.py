"""
Daily Deal Darling article generator using Google Gemini AI.

Generates SEO-optimized lifestyle/deals articles for budget-conscious women 25-45 with:
- Meta tags, Open Graph, and Twitter Card tags
- Article schema JSON-LD + FAQ schema JSON-LD
- Proper heading hierarchy (H1, H2, H3)
- Product recommendations with Amazon affiliate links (tag: dailydealdarling1-20)
- FAQ section with schema markup
- Pexels hero image integration
- ConvertKit email signup integration
- Internal links to existing articles
- Matching Daily Deal Darling website HTML template structure
"""

import os
import re
import json
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional

import google.generativeai as genai

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ── Constants ────────────────────────────────────────────────────────────────

AFFILIATE_TAG = "dailydealdarling1-20"
CONVERTKIT_FORM_ID = os.getenv("CONVERTKIT_DDD_FORM_ID", "5641382")
SITE_URL = "https://dailydealdarling.com"
SITE_NAME = "Daily Deal Darling"

# Brand voice description
BRAND_VOICE = (
    "Your helpful best friend who always knows the best deals. "
    "Friendly, approachable, and genuinely excited to share savings."
)

# Lead magnet for email signups
LEAD_MAGNET = {
    "name": "50 Hidden Gems Under $25",
    "description": "My secret list of amazing Amazon finds most people don't know about",
    "value": "FREE guide",
}

# Urgency/scarcity triggers
URGENCY_PHRASES = [
    "Prices checked today",
    "Deal alert",
    "Limited stock",
    "Best price we've seen",
    "Popular pick",
    "Selling fast",
]

# Social proof stats
SOCIAL_PROOF = {
    "subscribers": "15,000+",
    "products_tested": "500+",
    "happy_readers": "50,000+",
}

# Existing articles for internal linking
EXISTING_ARTICLES = [
    {"slug": "best-amazon-products-2026", "title": "Best Amazon Products 2026", "category": "Budget"},
    {"slug": "best-skincare-products-2026", "title": "Best Skincare Products 2026", "category": "Skincare"},
    {"slug": "best-kitchen-gadgets-2026", "title": "Best Kitchen Gadgets 2026", "category": "Kitchen"},
    {"slug": "best-home-organization-2026", "title": "Best Home Organization 2026", "category": "Organization"},
    {"slug": "best-fitness-gear-2026", "title": "Best Fitness Gear 2026", "category": "Wellness"},
    {"slug": "best-self-care-products-2026", "title": "Best Self-Care Products 2026", "category": "Wellness"},
    {"slug": "amazon-finds-under-25", "title": "Amazon Finds Under $25", "category": "Budget"},
    {"slug": "morning-routine-products", "title": "Morning Routine Products", "category": "Beauty"},
]

# Category display names
CATEGORY_DISPLAY = {
    "skincare": "Skincare",
    "kitchen": "Kitchen",
    "organization": "Home Organization",
    "beauty": "Beauty",
    "tech": "Tech",
    "wellness": "Wellness",
    "budget": "Budget Finds",
    "seasonal": "Seasonal",
    "haircare": "Hair Care",
}


# ── Prompts ──────────────────────────────────────────────────────────────────

OUTLINE_PROMPT = """You are an expert lifestyle content writer for DailyDealDarling.com, a website helping budget-conscious women find the best Amazon products and deals.

The site has a friendly, helpful, "best friend who always knows the deals" vibe. We help women 25-45 discover products that make their lives easier without breaking the bank.

Create a detailed article outline for the keyword: "{keyword}"

The article should:
1. Be 1500-2500 words (plan sections accordingly)
2. Target women looking for honest product recommendations and deals
3. Start with a "Quick Picks" summary (top 3 products for readers in a hurry)
4. Include 5-7 main sections (H2 headings) with logical flow
5. Have an engaging introduction with urgency ("If you've been putting this off...")
6. Include 4-6 product recommendations with SPECIFIC benefits and star ratings
7. End with a FAQ section (4-6 questions shoppers actually ask)
8. Include practical, honest advice -- not salesy language
9. Mention price points, value, and LIMITED TIME elements where relevant
10. Use a warm, conversational tone (like texting a friend about a great find)
11. Include comparison elements ("This vs That")
12. Add social proof (reviews, ratings, "bestseller" status)

Return ONLY valid JSON in this exact format:
{{
    "title": "SEO-optimized title (55-65 chars, include keyword naturally)",
    "meta_description": "Compelling description (145-155 chars, include keyword, action-oriented)",
    "intro_hook": "Opening sentence with urgency that immediately connects with a busy woman looking for solutions",
    "quick_picks": [
        {{
            "position": "Best Overall",
            "name": "Product name",
            "why": "One sentence why"
        }},
        {{
            "position": "Best Budget",
            "name": "Product name",
            "why": "One sentence why"
        }},
        {{
            "position": "Best Premium",
            "name": "Product name",
            "why": "One sentence why"
        }}
    ],
    "sections": [
        {{
            "heading": "H2 heading text",
            "subheadings": ["H3 heading if needed"],
            "key_points": ["Main points to cover in this section"],
            "include_product": false,
            "include_email_cta": false
        }}
    ],
    "product_recommendations": [
        {{
            "name": "Product name",
            "description": "Why this product is a great find (2-3 sentences with specific benefits)",
            "price_range": "under $X",
            "search_term": "amazon search term for this product",
            "rating": "4.7",
            "review_count": "25,000+",
            "badge": "Best Seller OR Editor's Pick OR Best Value OR Trending",
            "pros": ["Pro 1", "Pro 2", "Pro 3"],
            "cons": ["Con 1"]
        }}
    ],
    "faq": [
        {{
            "question": "Common shopping question related to keyword?",
            "answer_points": ["Key points for answer"]
        }}
    ],
    "internal_link_slugs": ["slugs from existing articles to link to"],
    "pexels_search": "best search query for pexels hero image (lifestyle/product focused)"
}}
"""

ARTICLE_CONTENT_PROMPT = """You are the lead writer for DailyDealDarling.com. The site helps budget-conscious women 25-45 discover amazing Amazon products that make life easier.

Write the FULL article content for: "{keyword}"
Title: {title}

Use this outline:
{outline_json}

WRITING GUIDELINES:
- Total length: 1500-2500 words
- Tone: Warm, friendly, conversational -- like texting a friend about a great find
- Write for busy women who want honest recommendations without the fluff
- Use "you" language -- speak directly to the reader
- Include specific price points and value mentions
- Be honest about pros/cons -- readers trust authenticity
- Avoid overly salesy language or hype
- Use short paragraphs (2-4 sentences max)
- Include personal touches ("I've been using this for months")
- Mention who products are best for ("Perfect if you...")

CONVERSION ELEMENTS TO INCLUDE:
- Add urgency where appropriate ("I just checked and prices are still...")
- Include social proof ("Over 25,000 5-star reviews", "Bestseller for 3 years")
- Add FOMO triggers ("This sold out last month", "Price just dropped")
- Mention Amazon Prime benefits where relevant
- Include comparison statements ("Unlike cheaper alternatives...")
- Add trust builders ("Dermatologist recommended", "Award winning")

CALLS TO ACTION to weave in naturally (2-3 throughout the article):
- "Want my complete list of hidden gems? I share my best finds in my free weekly email."
- "I put together a free guide with 50 more finds like this - grab it below!"
- "Join 15,000+ savvy shoppers who get my deals email every week."

INTERNAL LINKS TO INCLUDE (use these existing article URLs where relevant):
{internal_links}

FORMAT YOUR RESPONSE AS HTML CONTENT ONLY (no <html>, <head>, or <body> tags).
Use these HTML elements:
- <p> for paragraphs
- <h2> for main sections
- <h3> for subsections
- <ul>/<ol> and <li> for lists
- <strong> for emphasis
- <a href="..."> for internal links (use relative paths like "articles/slug.html")
- Do NOT include the title (H1) -- that's handled separately

Write the complete article now.
"""

PRODUCT_SECTION_PROMPT = """Write product recommendation cards for a Daily Deal Darling article about "{keyword}".

Products to recommend:
{products_json}

For each product, write a COMPELLING description (2-3 sentences) that:
- Explains the key benefit (what problem it solves)
- Mentions social proof (ratings, reviews, bestseller status)
- Creates urgency or FOMO when appropriate
- Mentions Prime shipping if relevant
- Includes who it's perfect for

Return ONLY valid JSON array:
[
    {{
        "name": "Product Name",
        "description": "Compelling description with benefits and social proof",
        "price_range": "under $X",
        "amazon_search": "search terms for amazon link",
        "rating": "4.X",
        "review_count": "XX,000+",
        "badge": "Best Seller OR Editor's Pick OR Best Value OR Trending OR Popular Pick",
        "urgency_note": "Optional urgency message like 'Price just dropped!' or 'Often sells out'",
        "pros": ["Pro 1", "Pro 2", "Pro 3"],
        "cons": ["Minor con for authenticity"]
    }}
]
"""

FAQ_PROMPT = """Write FAQ answers for a Daily Deal Darling article about "{keyword}".

Questions and answer points:
{faq_json}

Write concise, helpful answers (50-100 words each). Be friendly and practical.
Think about what a helpful friend would say when answering these questions.

Return ONLY valid JSON array:
[
    {{
        "question": "The question exactly as given",
        "answer": "Complete answer text"
    }}
]
"""


# ── Pexels Integration ───────────────────────────────────────────────────────

def fetch_pexels_image(query: str, api_key: Optional[str] = None) -> Optional[str]:
    """Fetch a relevant hero image from Pexels API."""
    api_key = api_key or os.getenv("PEXELS_API_KEY")
    if not api_key:
        logger.warning("PEXELS_API_KEY not set, using fallback image")
        return None

    try:
        headers = {"Authorization": api_key}
        params = {
            "query": query,
            "orientation": "landscape",
            "size": "large",
            "per_page": 5,
        }
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get("photos"):
            # Pick the first result
            photo = data["photos"][0]
            # Use the large2x size for hero images
            image_url = photo["src"].get("large2x") or photo["src"].get("large")
            logger.info(f"Pexels image found: {image_url}")
            return image_url

    except Exception as e:
        logger.warning(f"Pexels API error: {e}")

    return None


# Fallback images by category
FALLBACK_IMAGES = {
    "skincare": "https://images.pexels.com/photos/3785147/pexels-photo-3785147.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "kitchen": "https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "organization": "https://images.pexels.com/photos/6044266/pexels-photo-6044266.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "beauty": "https://images.pexels.com/photos/2587370/pexels-photo-2587370.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "tech": "https://images.pexels.com/photos/3183198/pexels-photo-3183198.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "wellness": "https://images.pexels.com/photos/3757942/pexels-photo-3757942.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "budget": "https://images.pexels.com/photos/5632398/pexels-photo-5632398.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "seasonal": "https://images.pexels.com/photos/5632379/pexels-photo-5632379.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "haircare": "https://images.pexels.com/photos/3993449/pexels-photo-3993449.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
}


# ── Article Generator ────────────────────────────────────────────────────────

class DailyDealDarlingArticleGenerator:
    """Generate SEO-optimized deals/lifestyle articles using Gemini AI."""

    def __init__(self, api_key: Optional[str] = None, pexels_key: Optional[str] = None):
        """Initialize with API keys."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.pexels_key = pexels_key or os.getenv("PEXELS_API_KEY")

    def _call_gemini(self, prompt: str) -> str:
        """Make a Gemini API call with retry."""
        for attempt in range(3):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                logger.error(f"Gemini API error (attempt {attempt + 1}): {e}")
                if attempt == 2:
                    raise
                import time
                time.sleep(2 ** attempt)

    def _parse_json(self, text: str) -> dict:
        """Extract and parse JSON from Gemini response."""
        # Clean the text first
        text = text.strip()

        # First try: look for ```json blocks (greedy match)
        json_block = re.search(r'```json\s*([\s\S]+?)\s*```', text)
        if json_block:
            try:
                return json.loads(json_block.group(1))
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error in ```json block: {e}")

        # Second try: if the whole text starts with ```json, strip the markers
        if text.startswith('```json'):
            clean = text[7:]  # Remove ```json
            if clean.endswith('```'):
                clean = clean[:-3]
            clean = clean.strip()
            try:
                return json.loads(clean)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error after stripping markers: {e}")

        # Third try: find the outermost JSON object or array
        for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
            json_match = re.search(pattern, text)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    continue

        # Fourth try: maybe Gemini didn't add the closing ```
        if '```json' in text:
            start = text.find('```json') + 7
            # Find the first { after ```json
            brace_start = text.find('{', start)
            if brace_start != -1:
                # Find matching closing brace
                depth = 0
                for i, c in enumerate(text[brace_start:], brace_start):
                    if c == '{':
                        depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0:
                            try:
                                return json.loads(text[brace_start:i+1])
                            except json.JSONDecodeError:
                                break

        raise ValueError(f"No valid JSON found in response: {text[:200]}...")

    def generate_outline(self, keyword: str) -> dict:
        """Generate article outline."""
        logger.info(f"Generating outline for: {keyword}")
        prompt = OUTLINE_PROMPT.format(keyword=keyword)
        response = self._call_gemini(prompt)
        return self._parse_json(response)

    def generate_article_content(self, keyword: str, title: str, outline: dict) -> str:
        """Generate the full article HTML content."""
        logger.info(f"Generating article content for: {keyword}")

        # Build internal links reference
        internal_links = ""
        link_slugs = outline.get("internal_link_slugs", [])
        for article in EXISTING_ARTICLES:
            if article["slug"] in link_slugs or not link_slugs:
                internal_links += f'- {article["title"]}: articles/{article["slug"]}.html\n'

        prompt = ARTICLE_CONTENT_PROMPT.format(
            keyword=keyword,
            title=title,
            outline_json=json.dumps(outline, indent=2),
            internal_links=internal_links
        )
        return self._call_gemini(prompt)

    def generate_product_recommendations(self, keyword: str, products: list) -> list:
        """Generate product recommendation content."""
        if not products:
            return []

        logger.info(f"Generating {len(products)} product recommendations")
        prompt = PRODUCT_SECTION_PROMPT.format(
            keyword=keyword,
            products_json=json.dumps(products, indent=2)
        )
        response = self._call_gemini(prompt)
        try:
            return self._parse_json(response)
        except (ValueError, json.JSONDecodeError):
            logger.warning("Failed to parse product recommendations, using outline data")
            return products

    def generate_faq(self, keyword: str, faq_items: list) -> list:
        """Generate FAQ answers."""
        if not faq_items:
            return []

        logger.info(f"Generating {len(faq_items)} FAQ answers")
        prompt = FAQ_PROMPT.format(
            keyword=keyword,
            faq_json=json.dumps(faq_items, indent=2)
        )
        response = self._call_gemini(prompt)
        try:
            return self._parse_json(response)
        except (ValueError, json.JSONDecodeError):
            logger.warning("Failed to parse FAQ, generating simple answers")
            return [
                {"question": item["question"], "answer": ". ".join(item.get("answer_points", ["See article above for details."]))}
                for item in faq_items
            ]

    def generate_full_article(self, keyword: str, category: str) -> dict:
        """
        Generate a complete article with all components.

        Args:
            keyword: Target keyword
            category: Article category

        Returns:
            Dict with all article components needed for HTML generation
        """
        logger.info(f"{'='*60}")
        logger.info(f"Generating full article for: {keyword}")
        logger.info(f"Category: {category}")
        logger.info(f"{'='*60}")

        # Step 1: Generate outline
        outline = self.generate_outline(keyword)
        title = outline.get('title', keyword.title())
        meta_description = outline.get('meta_description', '')

        # Step 2: Generate article content
        content_html = self.generate_article_content(keyword, title, outline)

        # Step 3: Generate product recommendations
        products = self.generate_product_recommendations(
            keyword,
            outline.get('product_recommendations', [])
        )

        # Step 4: Generate FAQ
        faq = self.generate_faq(keyword, outline.get('faq', []))

        # Step 5: Fetch hero image
        pexels_query = outline.get('pexels_search', keyword)
        hero_image = fetch_pexels_image(pexels_query, self.pexels_key)
        if not hero_image:
            hero_image = FALLBACK_IMAGES.get(
                category,
                FALLBACK_IMAGES["budget"]
            )

        # Step 6: Calculate read time
        total_text = content_html
        for item in faq:
            total_text += " " + item.get("answer", "")
        word_count = len(total_text.split())
        read_time = max(4, word_count // 200)

        # Step 7: Determine internal links
        internal_link_slugs = outline.get('internal_link_slugs', [])
        internal_links = [
            a for a in EXISTING_ARTICLES
            if a["slug"] in internal_link_slugs
        ]
        # If none matched, pick 2-3 related ones
        if not internal_links:
            internal_links = EXISTING_ARTICLES[:3]

        return {
            'keyword': keyword,
            'category': category,
            'category_display': CATEGORY_DISPLAY.get(category, category.replace('_', ' ').title()),
            'title': title,
            'meta_description': meta_description,
            'content_html': content_html,
            'products': products,
            'quick_picks': outline.get('quick_picks', []),
            'faq': faq,
            'hero_image': hero_image,
            'read_time': read_time,
            'word_count': word_count,
            'internal_links': internal_links,
            'generated_at': datetime.utcnow().isoformat(),
        }


# ── HTML Generator ───────────────────────────────────────────────────────────

def generate_html(article_data: dict) -> str:
    """
    Convert article data to complete HTML matching Daily Deal Darling website structure.

    Args:
        article_data: Output from DailyDealDarlingArticleGenerator.generate_full_article()

    Returns:
        Complete HTML string
    """
    title = article_data['title']
    meta_desc = article_data['meta_description']
    category_display = article_data['category_display']
    content_html = article_data['content_html']
    products = article_data.get('products', [])
    faq = article_data.get('faq', [])
    hero_image = article_data['hero_image']
    read_time = article_data['read_time']
    now = datetime.utcnow()
    date_str = now.strftime("%B %d, %Y")
    date_iso = now.strftime("%Y-%m-%d")
    slug = article_data['keyword'].lower().replace(' ', '-').replace('?', '').replace("'", '')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')[:60]

    # Clean up content HTML -- strip any wrapping tags Gemini might add
    content_html = content_html.strip()
    if content_html.startswith('```html'):
        content_html = content_html[7:]
    if content_html.startswith('```'):
        content_html = content_html[3:]
    if content_html.endswith('```'):
        content_html = content_html[:-3]
    content_html = content_html.strip()

    # Build Quick Picks summary section
    quick_picks_html = ""
    quick_picks = article_data.get('quick_picks', [])
    if quick_picks:
        quick_picks_html = """
      <div class="quick-picks">
        <div class="quick-picks__header">
          <span class="quick-picks__badge">⚡ Quick Picks</span>
          <h2>In a Hurry? Here Are Our Top 3</h2>
        </div>
        <div class="quick-picks__grid">
"""
        for pick in quick_picks[:3]:
            position = pick.get('position', 'Top Pick')
            name = pick.get('name', '')
            why = pick.get('why', '')
            search = name.replace(' ', '+')
            amazon_url = f"https://www.amazon.com/s?k={requests.utils.quote(name)}&tag={AFFILIATE_TAG}"
            quick_picks_html += f"""          <a href="{amazon_url}" class="quick-pick" target="_blank" rel="nofollow noopener">
            <span class="quick-pick__position">{position}</span>
            <span class="quick-pick__name">{name}</span>
            <span class="quick-pick__why">{why}</span>
            <span class="quick-pick__cta">Check Price →</span>
          </a>
"""
        quick_picks_html += """        </div>
      </div>
"""

    # Build product recommendation cards with enhanced conversion elements
    products_html = ""
    if products:
        products_html = '\n      <h2>Our Top Recommendations</h2>\n      <p class="section-subtitle">Personally tested and reader-approved picks</p>\n\n      <div class="product-grid">\n'
        for i, product in enumerate(products):
            name = product.get('name', 'Recommended Product')
            desc = product.get('description', '')
            price_range = product.get('price_range', '')
            search = product.get('amazon_search', product.get('search_term', name))
            amazon_url = f"https://www.amazon.com/s?k={requests.utils.quote(search)}&tag={AFFILIATE_TAG}"
            rating = product.get('rating', '4.5')
            review_count = product.get('review_count', '10,000+')
            badge = product.get('badge', '')
            urgency = product.get('urgency_note', '')
            pros = product.get('pros', [])
            cons = product.get('cons', [])

            badge_html = f'<span class="product-badge product-badge--{badge.lower().replace(" ", "-")}">{badge}</span>' if badge else ''
            urgency_html = f'<span class="product-urgency">🔥 {urgency}</span>' if urgency else ''

            # Build pros/cons HTML
            pros_cons_html = ""
            if pros or cons:
                pros_cons_html = '<div class="product-pros-cons">'
                if pros:
                    pros_cons_html += '<div class="pros"><strong>✓ Pros:</strong><ul>'
                    for pro in pros[:3]:
                        pros_cons_html += f'<li>{pro}</li>'
                    pros_cons_html += '</ul></div>'
                if cons:
                    pros_cons_html += '<div class="cons"><strong>✗ Cons:</strong><ul>'
                    for con in cons[:1]:
                        pros_cons_html += f'<li>{con}</li>'
                    pros_cons_html += '</ul></div>'
                pros_cons_html += '</div>'

            products_html += f"""        <div class="product-card">
          {badge_html}
          <h3 class="product-card__name">{name}</h3>
          <div class="product-card__rating">
            <span class="stars">{'★' * int(float(rating))}{'☆' * (5 - int(float(rating)))}</span>
            <span class="rating-text">{rating} ({review_count} reviews)</span>
          </div>
          <p class="product-card__price">{price_range}</p>
          {urgency_html}
          <p class="product-card__description">{desc}</p>
          {pros_cons_html}
          <a href="{amazon_url}" class="product-card__cta" target="_blank" rel="nofollow noopener">
            <span>Check Price on Amazon</span>
            <span class="prime-badge">✓ Prime</span>
          </a>
        </div>
"""
        products_html += '      </div>\n'

    # Build FAQ HTML with proper formatting
    faq_html = ""
    faq_schema_items = []
    if faq:
        faq_html = '\n      <h2>Frequently Asked Questions</h2>\n\n'
        for item in faq:
            question = item.get('question', '')
            answer = item.get('answer', '')
            faq_html += f"""      <h3>{question}</h3>
      <p>{answer}</p>

"""
            faq_schema_items.append({
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer
                }
            })

    # Article schema JSON-LD
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": meta_desc,
        "image": hero_image,
        "datePublished": date_iso,
        "dateModified": date_iso,
        "author": {
            "@type": "Organization",
            "name": "Daily Deal Darling",
        },
        "publisher": {
            "@type": "Organization",
            "name": "Daily Deal Darling",
            "url": SITE_URL,
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"{SITE_URL}/articles/{slug}.html"
        }
    }

    # FAQ schema JSON-LD
    faq_schema_html = ""
    if faq_schema_items:
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_schema_items
        }
        faq_schema_html = f"""
  <script type="application/ld+json">
  {json.dumps(faq_schema, indent=2)}
  </script>"""

    # Affiliate disclosure
    affiliate_html = """
      <div class="affiliate-disclosure">
        <p><strong>Affiliate Disclosure:</strong> This post contains affiliate links. If you purchase through these links, we may earn a small commission at no extra cost to you. We only recommend products we genuinely love!</p>
      </div>"""

    # Build the full HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{_escape_attr(meta_desc)}">
  <meta name="keywords" content="{_escape_attr(article_data['keyword'])}, amazon finds, best products, deals">
  <meta name="author" content="Daily Deal Darling">
  <meta name="robots" content="index, follow">

  <!-- Open Graph / Social -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="{SITE_URL}/articles/{slug}.html">
  <meta property="og:title" content="{_escape_attr(title)} | {SITE_NAME}">
  <meta property="og:description" content="{_escape_attr(meta_desc)}">
  <meta property="og:image" content="{hero_image}">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{_escape_attr(title)} | {SITE_NAME}">
  <meta name="twitter:description" content="{_escape_attr(meta_desc)}">

  <title>{_escape_html(title)} | {SITE_NAME}</title>

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:wght@600;700&display=swap" rel="stylesheet">

  <!-- Styles -->
  <link rel="stylesheet" href="../css/styles.css">

  <!-- Article Schema -->
  <script type="application/ld+json">
  {json.dumps(article_schema, indent=2)}
  </script>{faq_schema_html}

  <style>
    .article-header {{
      background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
      color: white;
      padding: var(--spacing-2xl) 0;
      text-align: center;
    }}
    .article-header__category {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      opacity: 0.9;
      font-weight: 600;
      margin-bottom: var(--spacing-sm);
    }}
    .article-header__title {{
      color: white;
      font-size: 2.25rem;
      margin-bottom: var(--spacing-md);
      line-height: 1.2;
      font-family: 'Fraunces', serif;
    }}
    .article-header__meta {{
      opacity: 0.9;
      font-size: 0.95rem;
    }}
    .article-content {{
      padding: var(--spacing-2xl) 0;
      max-width: 800px;
      margin: 0 auto;
    }}
    .article-content h2 {{
      margin-top: var(--spacing-xl);
      margin-bottom: var(--spacing-md);
      color: var(--color-charcoal);
      font-family: 'Fraunces', serif;
    }}
    .article-content h3 {{
      margin-top: var(--spacing-lg);
      margin-bottom: var(--spacing-sm);
      color: var(--color-charcoal);
    }}
    .article-content p {{
      color: var(--color-text);
      font-size: 1.1rem;
      line-height: 1.8;
      margin-bottom: var(--spacing-md);
    }}
    .article-content ul, .article-content ol {{
      color: var(--color-text);
      font-size: 1.1rem;
      line-height: 1.8;
      margin-bottom: var(--spacing-md);
      padding-left: var(--spacing-lg);
    }}
    .article-content li {{
      margin-bottom: var(--spacing-xs);
    }}
    .product-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: var(--spacing-lg);
      margin: var(--spacing-lg) 0;
    }}
    .product-card {{
      background: var(--color-off-white);
      border-radius: 12px;
      padding: var(--spacing-lg);
      text-align: center;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .product-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }}
    .product-card__name {{
      font-size: 1.1rem;
      margin-bottom: var(--spacing-xs);
      color: var(--color-charcoal);
    }}
    .product-card__price {{
      color: var(--color-primary);
      font-weight: 600;
      margin-bottom: var(--spacing-sm);
    }}
    .product-card__description {{
      font-size: 0.95rem;
      color: var(--color-text);
      margin-bottom: var(--spacing-md);
    }}
    .product-card__cta {{
      display: inline-block;
      background: var(--color-primary);
      color: white;
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 600;
      transition: background 0.2s;
    }}
    .product-card__cta:hover {{
      background: var(--color-primary-dark);
    }}
    .affiliate-disclosure {{
      background: #fef3c7;
      border-left: 4px solid var(--color-accent);
      padding: var(--spacing-md);
      margin-top: var(--spacing-xl);
      border-radius: 0 8px 8px 0;
      font-size: 0.9rem;
    }}
    /* Trust Bar */
    .trust-bar {{
      display: flex;
      justify-content: center;
      gap: var(--spacing-lg);
      flex-wrap: wrap;
      padding: var(--spacing-md);
      background: #f8fafc;
      border-radius: 8px;
      margin-bottom: var(--spacing-xl);
      font-size: 0.9rem;
      color: var(--color-text);
    }}
    .trust-bar .trust-item {{
      display: flex;
      align-items: center;
      gap: 4px;
    }}

    /* Quick Picks Section */
    .quick-picks {{
      background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
      border-radius: 12px;
      padding: var(--spacing-lg);
      margin-bottom: var(--spacing-xl);
    }}
    .quick-picks__header {{
      text-align: center;
      margin-bottom: var(--spacing-md);
    }}
    .quick-picks__badge {{
      background: #f59e0b;
      color: white;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 700;
      display: inline-block;
      margin-bottom: var(--spacing-sm);
    }}
    .quick-picks__header h2 {{
      margin: 0;
      font-size: 1.25rem;
    }}
    .quick-picks__grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: var(--spacing-md);
    }}
    .quick-pick {{
      background: white;
      border-radius: 8px;
      padding: var(--spacing-md);
      text-decoration: none;
      display: flex;
      flex-direction: column;
      gap: 4px;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .quick-pick:hover {{
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .quick-pick__position {{
      font-size: 0.7rem;
      text-transform: uppercase;
      color: var(--color-primary);
      font-weight: 700;
    }}
    .quick-pick__name {{
      font-weight: 600;
      color: var(--color-charcoal);
    }}
    .quick-pick__why {{
      font-size: 0.85rem;
      color: var(--color-text);
    }}
    .quick-pick__cta {{
      color: var(--color-primary);
      font-weight: 600;
      font-size: 0.85rem;
      margin-top: auto;
    }}

    /* Enhanced Product Cards */
    .section-subtitle {{
      text-align: center;
      color: var(--color-text);
      margin-bottom: var(--spacing-lg);
    }}
    .product-badge {{
      position: absolute;
      top: var(--spacing-sm);
      left: var(--spacing-sm);
      padding: 4px 10px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .product-badge--best-seller {{ background: #ef4444; color: white; }}
    .product-badge--editor's-pick {{ background: #8b5cf6; color: white; }}
    .product-badge--best-value {{ background: #10b981; color: white; }}
    .product-badge--trending {{ background: #f59e0b; color: white; }}
    .product-badge--popular-pick {{ background: #3b82f6; color: white; }}
    .product-card {{
      position: relative;
    }}
    .product-card__rating {{
      display: flex;
      align-items: center;
      gap: var(--spacing-xs);
      margin-bottom: var(--spacing-sm);
    }}
    .product-card__rating .stars {{
      color: #f59e0b;
    }}
    .product-card__rating .rating-text {{
      font-size: 0.85rem;
      color: var(--color-text);
    }}
    .product-urgency {{
      display: inline-block;
      background: #fef3c7;
      color: #92400e;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 0.8rem;
      font-weight: 600;
      margin-bottom: var(--spacing-sm);
    }}
    .product-pros-cons {{
      margin: var(--spacing-md) 0;
      font-size: 0.9rem;
    }}
    .product-pros-cons ul {{
      margin: var(--spacing-xs) 0;
      padding-left: var(--spacing-md);
    }}
    .product-pros-cons .pros {{ color: #059669; }}
    .product-pros-cons .cons {{ color: #6b7280; }}
    .product-card__cta {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: var(--spacing-sm);
    }}
    .prime-badge {{
      background: #232f3e;
      color: white;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 600;
    }}

    /* Comparison Callout */
    .comparison-callout {{
      background: #eff6ff;
      border-left: 4px solid #3b82f6;
      padding: var(--spacing-md);
      margin: var(--spacing-xl) 0;
      border-radius: 0 8px 8px 0;
    }}
    .comparison-callout h3 {{
      margin: 0 0 var(--spacing-xs) 0;
      font-size: 1rem;
    }}
    .comparison-callout p {{
      margin: 0;
      font-size: 0.95rem;
    }}

    /* Enhanced Email Signup */
    .email-signup-inline {{
      background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
      color: white;
      padding: var(--spacing-xl);
      border-radius: 12px;
      text-align: center;
      margin: var(--spacing-xl) 0;
    }}
    .email-signup-inline--mid {{
      background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
    }}
    .email-signup-inline--bottom {{
      background: linear-gradient(135deg, #059669 0%, #10b981 100%);
    }}
    .email-signup-badge {{
      display: inline-block;
      background: rgba(255,255,255,0.2);
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 700;
      margin-bottom: var(--spacing-sm);
    }}
    .email-signup-inline h3 {{
      color: white;
      margin-bottom: var(--spacing-sm);
      font-size: 1.5rem;
    }}
    .email-signup-inline p {{
      color: rgba(255,255,255,0.9);
      margin-bottom: var(--spacing-md);
    }}
    .signup-form-inline {{
      display: flex;
      gap: var(--spacing-sm);
      max-width: 450px;
      margin: 0 auto;
    }}
    .signup-form-inline input {{
      flex: 1;
      padding: 0.875rem 1rem;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
    }}
    .signup-form-inline button {{
      background: var(--color-charcoal);
      color: white;
      border: none;
      padding: 0.875rem 1.5rem;
      border-radius: 8px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
      transition: transform 0.2s;
    }}
    .signup-form-inline button:hover {{
      transform: scale(1.02);
    }}
    .signup-privacy {{
      font-size: 0.85rem;
      opacity: 0.8;
      margin-top: var(--spacing-sm);
    }}
    .signup-benefits {{
      display: flex;
      justify-content: center;
      gap: var(--spacing-md);
      flex-wrap: wrap;
      margin-top: var(--spacing-md);
      font-size: 0.9rem;
    }}

    /* CTA Section Enhancements */
    .cta__badge {{
      display: inline-block;
      background: rgba(255,255,255,0.2);
      padding: 6px 16px;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: var(--spacing-md);
    }}
    .cta__perks {{
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);
      margin-top: var(--spacing-md);
      font-size: 0.9rem;
    }}

    /* Popup Enhancements */
    .popup-badge {{
      display: inline-block;
      background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
      color: white;
      padding: 6px 16px;
      border-radius: 20px;
      font-size: 0.8rem;
      font-weight: 700;
      margin-bottom: var(--spacing-md);
    }}
    .popup-subtitle {{
      font-size: 1rem;
      margin-bottom: var(--spacing-md);
    }}
    .popup-benefits {{
      text-align: left;
      list-style: none;
      padding: 0;
      margin: 0 0 var(--spacing-md) 0;
    }}
    .popup-benefits li {{
      padding: var(--spacing-xs) 0;
      font-size: 0.95rem;
    }}
    .popup-form {{
      flex-direction: column;
    }}
    .popup-form input {{
      width: 100%;
      margin-bottom: var(--spacing-sm);
    }}
    .btn--large {{
      padding: 1rem 2rem;
      font-size: 1.1rem;
    }}
    .popup-privacy {{
      font-size: 0.85rem;
      color: var(--color-text);
      margin-top: var(--spacing-sm);
    }}

    /* Mobile Sticky Bar */
    .mobile-sticky-bar {{
      display: none;
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
      padding: 12px 16px;
      z-index: 999;
      box-shadow: 0 -4px 20px rgba(0,0,0,0.15);
    }}
    .mobile-sticky-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .mobile-sticky-text {{
      color: white;
      font-weight: 600;
      font-size: 0.9rem;
    }}
    .mobile-sticky-btn {{
      background: white;
      color: var(--color-primary);
      border: none;
      padding: 10px 20px;
      border-radius: 50px;
      font-weight: 700;
      font-size: 0.9rem;
      cursor: pointer;
    }}
    @media (min-width: 769px) {{
      .mobile-sticky-bar {{ display: none !important; }}
    }}
    @media (max-width: 768px) {{
      body {{ padding-bottom: 70px; }}
      .signup-form-inline {{ flex-direction: column; }}
      .quick-picks__grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <!-- Header -->
  <header class="header">
    <div class="container">
      <div class="header__inner">
        <a href="../index.html" class="logo">Daily Deal <span>Darling</span></a>
        <nav class="nav" id="nav">
          <a href="../index.html" class="nav__link">Home</a>
          <a href="../blog.html" class="nav__link nav__link--active">Articles</a>
          <a href="../about.html" class="nav__link">About</a>
          <a href="../contact.html" class="nav__link">Contact</a>
        </nav>
        <button class="nav__toggle" id="navToggle" aria-label="Toggle navigation">
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </div>
  </header>

  <!-- Article Header -->
  <section class="article-header">
    <div class="container">
      <span class="article-header__category">{_escape_html(category_display)}</span>
      <h1 class="article-header__title">{_escape_html(title)}</h1>
      <p class="article-header__meta">{read_time} min read</p>
    </div>
  </section>

  <!-- Article Content -->
  <article class="article-content">
    <div class="container">
      <!-- Trust Bar -->
      <div class="trust-bar">
        <span class="trust-item">✓ {SOCIAL_PROOF['products_tested']} Products Tested</span>
        <span class="trust-item">✓ {SOCIAL_PROOF['subscribers']} Newsletter Subscribers</span>
        <span class="trust-item">✓ Updated {date_str}</span>
      </div>

{quick_picks_html}

      {content_html}

      <!-- Mid-Article Email Signup with Lead Magnet -->
      <div class="email-signup-inline email-signup-inline--mid">
        <div class="email-signup-badge">🎁 FREE GUIDE</div>
        <h3>Want 50 More Hidden Gems Like These?</h3>
        <p>Get my exclusive list of Amazon finds under $25 that most people don't know about - plus weekly deal alerts!</p>
        <form action="https://app.convertkit.com/forms/{CONVERTKIT_FORM_ID}/subscriptions" method="post" class="signup-form-inline">
          <input type="email" name="email_address" placeholder="Enter your best email" required>
          <button type="submit">Send Me the Free Guide →</button>
        </form>
        <p class="signup-privacy">Join {SOCIAL_PROOF['subscribers']} readers. Unsubscribe anytime. No spam, ever.</p>
      </div>

{products_html}

      <!-- Comparison Callout -->
      <div class="comparison-callout">
        <h3>💡 Pro Tip: Before You Buy</h3>
        <p>Prices on Amazon change constantly. I recommend checking the current price and reading the most recent reviews before purchasing. Look for the "Verified Purchase" badge!</p>
      </div>

{faq_html}

      <!-- Pre-Footer Email Signup -->
      <div class="email-signup-inline email-signup-inline--bottom">
        <h3>Never Miss a Deal Again!</h3>
        <p>I find amazing deals every week and share them with my email subscribers first. Join us!</p>
        <form action="https://app.convertkit.com/forms/{CONVERTKIT_FORM_ID}/subscriptions" method="post" class="signup-form-inline">
          <input type="email" name="email_address" placeholder="Your email address" required>
          <button type="submit">Get Weekly Deals</button>
        </form>
        <div class="signup-benefits">
          <span>✓ Weekly deal roundups</span>
          <span>✓ Early sale alerts</span>
          <span>✓ Exclusive finds</span>
        </div>
      </div>

{affiliate_html}
    </div>
  </article>

  <!-- Footer Email Signup with Strong CTA -->
  <section class="section section--coral" id="signup">
    <div class="container">
      <div class="cta">
        <div class="cta__content">
          <div class="cta__badge">🔥 {SOCIAL_PROOF['subscribers']} Smart Shoppers Can't Be Wrong</div>
          <h2 class="cta__title">Get the Best Deals Before Everyone Else</h2>
          <p class="cta__text">Every week I scour Amazon for the best deals and hidden gems. Join my free email list and I'll send them straight to your inbox - before they sell out!</p>
          <form class="signup-form" action="https://app.convertkit.com/forms/{CONVERTKIT_FORM_ID}/subscriptions" method="post">
            <input type="email" name="email_address" class="signup-form__input" placeholder="Enter your best email" required>
            <button type="submit" class="btn btn--primary">Yes, Send Me Deals! →</button>
          </form>
          <div class="cta__perks">
            <span>🎁 Free guide: 50 Hidden Gems Under $25</span>
            <span>📧 Weekly deal alerts</span>
            <span>🚫 Zero spam, unsubscribe anytime</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <div class="footer__grid">
        <div class="footer__brand">
          <a href="../index.html" class="logo">Daily Deal <span>Darling</span></a>
          <p>Your trusted source for the best Amazon finds, deals, and honest product recommendations.</p>
        </div>
        <div class="footer__nav">
          <h4 class="footer__title">Navigate</h4>
          <ul class="footer__links">
            <li><a href="../index.html">Home</a></li>
            <li><a href="../blog.html">Articles</a></li>
            <li><a href="../about.html">About</a></li>
            <li><a href="../contact.html">Contact</a></li>
          </ul>
        </div>
        <div class="footer__nav">
          <h4 class="footer__title">Categories</h4>
          <ul class="footer__links">
            <li><a href="../blog.html">Skincare</a></li>
            <li><a href="../blog.html">Kitchen</a></li>
            <li><a href="../blog.html">Home Organization</a></li>
            <li><a href="../blog.html">Budget Finds</a></li>
          </ul>
        </div>
      </div>
      <div class="footer__bottom">
        <p>&copy; {now.year} Daily Deal Darling. All rights reserved.</p>
        <p><a href="../disclosure.html">Affiliate Disclosure</a> | <a href="../privacy.html">Privacy Policy</a></p>
      </div>
    </div>
  </footer>

  <!-- Email Popup Modal (Exit Intent) -->
  <div class="popup-overlay" id="popupOverlay">
    <div class="popup-modal">
      <button class="popup-close" id="popupClose" aria-label="Close popup">&times;</button>
      <div class="popup-content">
        <div class="popup-badge">🎁 FREE GIFT</div>
        <h2>Wait! Grab This Before You Go...</h2>
        <p class="popup-subtitle">Get my <strong>50 Hidden Gems Under $25</strong> guide FREE - the secret finds I don't share anywhere else!</p>
        <ul class="popup-benefits">
          <li>✓ 50 amazing products under $25</li>
          <li>✓ Weekly deal alerts (before they sell out)</li>
          <li>✓ Early access to flash sales</li>
        </ul>
        <form class="signup-form popup-form" action="https://app.convertkit.com/forms/{CONVERTKIT_FORM_ID}/subscriptions" method="post">
          <input type="email" name="email_address" class="signup-form__input" placeholder="Your best email" required>
          <button type="submit" class="btn btn--primary btn--large">Send My Free Guide →</button>
        </form>
        <p class="popup-privacy">Join {SOCIAL_PROOF['subscribers']} smart shoppers. No spam, ever.</p>
      </div>
    </div>
  </div>

  <!-- Mobile Sticky Bar -->
  <div class="mobile-sticky-bar" id="mobileSticky">
    <span class="mobile-sticky-text">🔥 Get my free deals guide!</span>
    <button class="mobile-sticky-btn" id="mobileStickyBtn">Free Guide →</button>
  </div>

  <!-- Mobile Nav Script -->
  <script>
    document.getElementById('navToggle').addEventListener('click', function() {{
      document.getElementById('nav').classList.toggle('nav--open');
    }});
  </script>

  <!-- Popup Script -->
  <script>
  (function() {{
    var popupOverlay = document.getElementById('popupOverlay');
    var popupClose = document.getElementById('popupClose');
    var mobileStickyBtn = document.getElementById('mobileStickyBtn');
    var mobileSticky = document.getElementById('mobileSticky');
    var popupShown = false;

    function showPopup() {{
      if (sessionStorage.getItem('emailSubscribed')) return;
      popupOverlay.classList.add('active');
      popupShown = true;
    }}

    function closePopup() {{
      popupOverlay.classList.remove('active');
      sessionStorage.setItem('popupDismissed', 'true');
    }}

    popupClose.addEventListener('click', closePopup);

    popupOverlay.addEventListener('click', function(e) {{
      if (e.target === popupOverlay) closePopup();
    }});

    document.addEventListener('keydown', function(e) {{
      if (e.key === 'Escape') closePopup();
    }});

    // Mobile sticky bar shows popup
    if (mobileStickyBtn) {{
      mobileStickyBtn.addEventListener('click', function() {{
        showPopup();
      }});
    }}

    // Show mobile sticky bar after scrolling 400px
    window.addEventListener('scroll', function() {{
      if (mobileSticky) {{
        if (window.scrollY > 400) {{
          mobileSticky.style.display = 'flex';
        }} else {{
          mobileSticky.style.display = 'none';
        }}
      }}
    }});

    // Auto-show popup triggers (only if not dismissed)
    if (!sessionStorage.getItem('popupDismissed')) {{
      // Show after 45 seconds
      setTimeout(function() {{
        if (!popupShown) showPopup();
      }}, 45000);

      // Show at 70% scroll
      window.addEventListener('scroll', function() {{
        if (popupShown) return;
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        var docHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        if (docHeight > 0 && (scrollTop / docHeight) >= 0.7) {{
          showPopup();
        }}
      }});

      // Exit intent (desktop only)
      if (window.matchMedia('(pointer: fine)').matches) {{
        document.addEventListener('mouseout', function(e) {{
          if (!popupShown && e.clientY <= 0) {{
            showPopup();
          }}
        }});
      }}
    }}

    // Track form submissions
    document.querySelectorAll('form').forEach(function(form) {{
      form.addEventListener('submit', function() {{
        sessionStorage.setItem('emailSubscribed', 'true');
        if (mobileSticky) mobileSticky.style.display = 'none';
      }});
    }});
  }})();
  </script>
</body>
</html>"""

    return html


def _escape_html(text: str) -> str:
    """Escape HTML special characters in text."""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def _escape_attr(text: str) -> str:
    """Escape HTML attribute value."""
    return (text
            .replace('&', '&amp;')
            .replace('"', '&quot;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


# ── Main CLI ─────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate Daily Deal Darling SEO article')
    parser.add_argument(
        '--keyword',
        required=True,
        help='Target keyword for the article'
    )
    parser.add_argument(
        '--category',
        default='budget',
        help='Article category'
    )
    parser.add_argument(
        '--output',
        help='Output HTML file path'
    )
    parser.add_argument(
        '--output-dir',
        default='dailydealdarling_website/articles',
        help='Output directory for articles'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate outline only, skip full content'
    )

    args = parser.parse_args()

    generator = DailyDealDarlingArticleGenerator()

    if args.dry_run:
        outline = generator.generate_outline(args.keyword)
        print(json.dumps(outline, indent=2))
        return 0

    # Generate full article
    article_data = generator.generate_full_article(args.keyword, args.category)

    # Convert to HTML
    html = generate_html(article_data)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        slug = article_data['keyword'].lower().replace(' ', '-').replace('?', '').replace("'", '')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')[:60]
        output_path = Path(args.output_dir) / f"{slug}.html"

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    output_path.write_text(html, encoding='utf-8')
    logger.info(f"Article written to: {output_path}")

    # Output summary
    print(f"\n{'='*60}")
    print(f"ARTICLE GENERATED: {article_data['title']}")
    print(f"{'='*60}")
    print(f"Output: {output_path}")
    print(f"Word count: ~{article_data['word_count']}")
    print(f"Read time: {article_data['read_time']} min")
    print(f"Products: {len(article_data['products'])}")
    print(f"FAQ items: {len(article_data['faq'])}")
    print(f"Hero image: {article_data['hero_image']}")
    print(f"{'='*60}")

    # Output for GitHub Actions
    github_output = os.environ.get('GITHUB_OUTPUT', '')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"article_path={output_path}\n")
            f.write(f"title={article_data['title']}\n")
            f.write(f"category={article_data['category_display']}\n")
            f.write(f"read_time={article_data['read_time']}\n")
            f.write(f"hero_image={article_data['hero_image']}\n")
            f.write(f"word_count={article_data['word_count']}\n")
            f.write(f"excerpt={article_data['meta_description']}\n")

    return 0


if __name__ == "__main__":
    exit(main())
