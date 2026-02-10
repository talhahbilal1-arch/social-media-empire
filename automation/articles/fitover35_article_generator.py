"""
FitOver35 article generator using Google Gemini AI.

Generates SEO-optimized fitness articles for men over 35 with:
- Meta tags, Open Graph, and Twitter Card tags
- Article schema JSON-LD + FAQ schema JSON-LD
- Proper heading hierarchy (H1, H2, H3)
- Product recommendations with Amazon affiliate links (tag: fitover35-20)
- FAQ section with schema markup
- Pexels hero image integration
- ConvertKit email signup integration
- Internal links to existing articles
- Matching FitOver35 website HTML template structure exactly
"""

import os
import re
import json
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import anthropic as _anthropic
except ImportError:
    _anthropic = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ── Constants ────────────────────────────────────────────────────────────────

AFFILIATE_TAG = "fitover35-20"
CONVERTKIT_FORM_ID = "8946984"
SITE_URL = "https://fitover35.com"
SITE_NAME = "FitOver35"

# Author credentials for E-E-A-T
AUTHOR_BIO = (
    "Bachelor's in Kinesiology, Master's in Education, "
    "15+ years of fitness experience, natural bodybuilder and coach"
)

# Existing articles for internal linking
EXISTING_ARTICLES = [
    {"slug": "time-efficient-training", "title": "The Time-Efficient Training System for Men Over 35", "category": "Training Systems"},
    {"slug": "discipline-beats-motivation", "title": "Why Discipline Beats Motivation Every Time", "category": "Mindset"},
    {"slug": "superset-guide", "title": "The Complete Superset Guide for Busy Professionals", "category": "Training Systems"},
    {"slug": "nutrition-fundamentals", "title": "Nutrition Fundamentals for Men with Slowing Metabolisms", "category": "Nutrition"},
    {"slug": "recovery-stretching", "title": "Recovery and Stretching: The Missing Piece for Men 35+", "category": "Recovery"},
    {"slug": "home-gym-setup", "title": "Home Gym Setup Guide: Everything You Need, Nothing You Don't", "category": "Equipment"},
    {"slug": "supplements-over-35", "title": "The Best Supplements for Men Over 35 (Evidence-Based)", "category": "Nutrition"},
    {"slug": "training-around-injuries", "title": "How to Train Around Injuries Without Losing Progress", "category": "Training Systems"},
    {"slug": "30-day-density-program", "title": "The 30-Day Density Training Program", "category": "Programs"},
    {"slug": "training-identity", "title": "Building a Training Identity: Who You Are vs What You Do", "category": "Mindset"},
]

# Category display names
CATEGORY_DISPLAY = {
    "strength_training": "Strength Training",
    "nutrition": "Nutrition",
    "recovery": "Recovery",
    "mindset": "Mindset",
    "equipment": "Equipment",
    "health": "Health",
    "programs": "Programs",
    "lifestyle": "Lifestyle",
}


# ── Prompts ──────────────────────────────────────────────────────────────────

OUTLINE_PROMPT = """You are an expert fitness content writer for FitOver35.com, a website targeting men over 35 who want to build or maintain a strong physique.

The site owner has a Bachelor's in Kinesiology, Master's in Education, 15+ years fitness experience, and is a natural bodybuilder/coach.

Create a detailed article outline for the keyword: "{keyword}"

The article should:
1. Be 1000-2000 words (plan sections accordingly)
2. Target men over 35 who are searching for practical, evidence-based fitness advice
3. Include 4-6 main sections (H2 headings) with logical flow
4. Have a compelling, authoritative introduction that hooks immediately
5. Include 2-3 places where product recommendations fit naturally
6. End with a FAQ section (3-5 questions that people actually search for)
7. Include practical, actionable advice -- not fluff
8. Reference scientific evidence where appropriate
9. Use a direct, no-BS tone (confident, evidence-based, practical)

Return ONLY valid JSON in this exact format:
{{
    "title": "SEO-optimized title (55-65 chars, include keyword naturally)",
    "meta_description": "Compelling description (145-155 chars, include keyword, actionable)",
    "intro_hook": "Opening sentence that immediately grabs a man over 35",
    "sections": [
        {{
            "heading": "H2 heading text",
            "subheadings": ["H3 heading if needed"],
            "key_points": ["Main points to cover in this section"],
            "include_product": false
        }}
    ],
    "product_recommendations": [
        {{
            "name": "Product name",
            "description": "Why this product helps (1-2 sentences)",
            "search_term": "amazon search term for this product"
        }}
    ],
    "faq": [
        {{
            "question": "Common search question related to keyword?",
            "answer_points": ["Key points for answer"]
        }}
    ],
    "internal_link_slugs": ["slugs from existing articles to link to"],
    "pexels_search": "best search query for pexels hero image"
}}
"""

ARTICLE_CONTENT_PROMPT = """You are the head writer for FitOver35.com. The site owner has a Bachelor's in Kinesiology, Master's in Education, 15+ years fitness experience, and is a natural bodybuilder/coach.

Write the FULL article content for: "{keyword}"
Title: {title}

Use this outline:
{outline_json}

WRITING GUIDELINES:
- Total length: 1000-2000 words
- Tone: Direct, authoritative, no-BS. Like a knowledgeable friend who happens to have credentials.
- Write for men over 35 who are busy professionals, dads, or both
- Use "you" language -- speak directly to the reader
- Include specific numbers, sets, reps, percentages when relevant
- Reference research/evidence naturally (don't be overly academic)
- Be practical -- every paragraph should have actionable value
- Avoid filler phrases like "in today's fast-paced world" or "it's important to note"
- Use short paragraphs (2-4 sentences max)
- Include relevant statistics or research findings where natural
- Don't use excessive exclamation marks or hype language

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

PRODUCT_SECTION_PROMPT = """Write product recommendation cards for a FitOver35 article about "{keyword}".

Products to recommend:
{products_json}

For each product, write a brief 1-2 sentence description that explains why it's useful for men over 35 training.

Return ONLY valid JSON array:
[
    {{
        "name": "Product Name",
        "description": "Why this product matters for the reader",
        "amazon_search": "search terms for amazon link"
    }}
]
"""

FAQ_PROMPT = """Write FAQ answers for a FitOver35 article about "{keyword}".

Questions and answer points:
{faq_json}

Write concise, authoritative answers (50-100 words each). Be direct and practical.
Reference the site owner's credentials naturally where appropriate (B.S. in Kinesiology, M.Ed., 15+ years experience, natural bodybuilder/coach).

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


# Fallback images by category - ALL VERIFIED MALE-ONLY IMAGES
FALLBACK_IMAGES = {
    "strength_training": "https://images.pexels.com/photos/4720788/pexels-photo-4720788.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Man lifting barbell
    "nutrition": "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Food/nutrition
    "recovery": "https://images.pexels.com/photos/6456300/pexels-photo-6456300.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Man with dumbbells
    "mindset": "https://images.pexels.com/photos/3837757/pexels-photo-3837757.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Man focused training
    "equipment": "https://images.pexels.com/photos/4164761/pexels-photo-4164761.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Home gym equipment
    "health": "https://images.pexels.com/photos/3622614/pexels-photo-3622614.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Supplements
    "programs": "https://images.pexels.com/photos/4720788/pexels-photo-4720788.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Man lifting barbell
    "lifestyle": "https://images.pexels.com/photos/6456300/pexels-photo-6456300.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",  # Man with dumbbells
}


# ── Article Generator ────────────────────────────────────────────────────────

class FitOver35ArticleGenerator:
    """Generate SEO-optimized fitness articles using Gemini AI."""

    def __init__(self, api_key: Optional[str] = None, pexels_key: Optional[str] = None):
        """Initialize with API keys. Falls back to Anthropic if Gemini unavailable."""
        self.pexels_key = pexels_key or os.getenv("PEXELS_API_KEY")
        gemini_key = api_key or os.getenv("GEMINI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if gemini_key and genai:
            genai.configure(api_key=gemini_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
            self.backend = 'gemini'
            logger.info("Using Gemini backend for article generation")
        elif anthropic_key and _anthropic:
            self._anthropic_client = _anthropic.Anthropic(api_key=anthropic_key)
            self.backend = 'anthropic'
            logger.info("GEMINI_API_KEY not set, using Anthropic backend")
        else:
            raise ValueError(
                "Neither GEMINI_API_KEY nor ANTHROPIC_API_KEY is set. "
                "At least one AI API key is required for article generation."
            )

    def _call_gemini(self, prompt: str, json_mode: bool = False) -> str:
        """Make an AI API call with retry. Dispatches to Gemini or Anthropic."""
        if self.backend == 'anthropic':
            return self._call_anthropic(prompt)
        generation_config = None
        if json_mode and genai:
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        for attempt in range(3):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                return response.text
            except Exception as e:
                logger.error(f"Gemini API error (attempt {attempt + 1}): {e}")
                if attempt == 2:
                    raise
                import time
                time.sleep(2 ** attempt)

    def _call_anthropic(self, prompt: str) -> str:
        """Make an Anthropic API call with retry."""
        for attempt in range(3):
            try:
                response = self._anthropic_client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            except Exception as e:
                logger.error(f"Anthropic API error (attempt {attempt + 1}): {e}")
                if attempt == 2:
                    raise
                import time
                time.sleep(2 ** attempt)

    def _repair_json(self, text: str) -> Optional[str]:
        """Attempt to repair common JSON issues from LLM responses."""
        # Fix trailing commas before } or ]
        repaired = re.sub(r',\s*([}\]])', r'\1', text)
        # Fix missing commas between values (cross-line)
        repaired = re.sub(r'(")\s*\n\s*(")', r'\1,\n\2', repaired)
        repaired = re.sub(r'(")\s*\n\s*(\{)', r'\1,\n\2', repaired)
        repaired = re.sub(r'(\})\s*\n\s*(\{)', r'\1,\n\2', repaired)
        repaired = re.sub(r'(\])\s*\n\s*(")', r'\1,\n\2', repaired)
        repaired = re.sub(r'(\})\s*\n\s*(")', r'\1,\n\2', repaired)
        # Fix missing commas within a line: "value" "key" or "value"  "key"
        repaired = re.sub(r'"\s+"(?=[a-zA-Z_])', '", "', repaired)
        # Fix: true/false/null/number followed by "key" without comma
        repaired = re.sub(r'(true|false|null|\d+)\s+"', r'\1, "', repaired)
        # Fix: "value" followed by { or [ without comma (within line)
        repaired = re.sub(r'"\s+(\{)', r'", \1', repaired)
        repaired = re.sub(r'"\s+(\[)', r'", \1', repaired)
        try:
            json.loads(repaired)
            return repaired
        except json.JSONDecodeError:
            pass
        # Try truncating to last valid closing brace (Gemini sometimes appends garbage)
        last_brace = repaired.rfind('}')
        if last_brace != -1:
            candidate = repaired[:last_brace + 1]
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass
        return None

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
                # Try repairing the extracted block
                repaired = self._repair_json(json_block.group(1))
                if repaired:
                    logger.info("JSON repair succeeded on ```json block")
                    return json.loads(repaired)

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
                repaired = self._repair_json(clean)
                if repaired:
                    logger.info("JSON repair succeeded after stripping markers")
                    return json.loads(repaired)

        # Third try: find the outermost JSON object or array
        for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
            json_match = re.search(pattern, text)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    repaired = self._repair_json(json_match.group())
                    if repaired:
                        logger.info("JSON repair succeeded on extracted object")
                        return json.loads(repaired)

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
                                repaired = self._repair_json(text[brace_start:i+1])
                                if repaired:
                                    logger.info("JSON repair succeeded on brace-matched block")
                                    return json.loads(repaired)
                                break

        raise ValueError(f"No valid JSON found in response: {text[:200]}...")

    def generate_outline(self, keyword: str) -> dict:
        """Generate article outline with retry on parse failure."""
        logger.info(f"Generating outline for: {keyword}")
        prompt = OUTLINE_PROMPT.format(keyword=keyword)
        last_error = None
        for attempt in range(3):
            response = self._call_gemini(prompt, json_mode=True)
            try:
                return self._parse_json(response)
            except ValueError as e:
                last_error = e
                logger.warning(f"Outline parse failed (attempt {attempt + 1}/3): {e}")
                import time
                time.sleep(2)
        raise last_error

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
        response = self._call_gemini(prompt, json_mode=True)
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
        response = self._call_gemini(prompt, json_mode=True)
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
                FALLBACK_IMAGES["strength_training"]
            )

        # Step 6: Calculate read time
        total_text = content_html
        for item in faq:
            total_text += " " + item.get("answer", "")
        word_count = len(total_text.split())
        read_time = max(5, word_count // 200)

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
            'faq': faq,
            'hero_image': hero_image,
            'read_time': read_time,
            'word_count': word_count,
            'internal_links': internal_links,
            'generated_at': datetime.now(timezone.utc).isoformat(),
        }


# ── HTML Generator ───────────────────────────────────────────────────────────

def generate_html(article_data: dict) -> str:
    """
    Convert article data to complete HTML matching FitOver35 website structure.

    Matches the exact HTML structure of existing articles at:
    outputs/fitover35-website/articles/

    Args:
        article_data: Output from FitOver35ArticleGenerator.generate_full_article()

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
    now = datetime.now(timezone.utc)
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

    # Build product recommendation cards
    products_html = ""
    if products:
        products_html = '\n      <h2>Recommended Tools</h2>\n\n      <div class="product-grid">\n'
        for product in products:
            name = product.get('name', 'Recommended Product')
            desc = product.get('description', '')
            search = product.get('amazon_search', product.get('search_term', name))
            amazon_url = f"https://www.amazon.com/s?k={requests.utils.quote(search)}&tag={AFFILIATE_TAG}"
            products_html += f"""        <div class="product-card">
          <h3 class="product-card__name">{name}</h3>
          <p class="product-card__description">{desc}</p>
          <a href="{amazon_url}" class="product-card__cta" target="_blank" rel="nofollow noopener">Check Price on Amazon</a>
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
            "@type": "Person",
            "name": "FitOver35",
            "description": AUTHOR_BIO,
        },
        "publisher": {
            "@type": "Organization",
            "name": "FitOver35",
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
        <p>Some links on this page are affiliate links. If you purchase through these links, we may earn a small commission at no extra cost to you. We only recommend products we genuinely believe in.</p>
      </div>"""

    # Build the full HTML matching existing FitOver35 article structure
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{_escape_attr(meta_desc)}">
  <meta name="keywords" content="{_escape_attr(article_data['keyword'])}, men over 35, fitness, strength training">
  <meta name="author" content="FitOver35">
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
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

  <!-- Styles -->
  <link rel="stylesheet" href="../css/styles.css">

  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>35</text></svg>">

  <!-- Article Schema -->
  <script type="application/ld+json">
  {json.dumps(article_schema, indent=2)}
  </script>{faq_schema_html}

  <style>
    .article-header {{
      background-color: var(--color-charcoal);
      color: var(--color-white);
      padding: var(--spacing-2xl) 0;
    }}
    .article-header__category {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--color-accent);
      font-weight: 600;
      margin-bottom: var(--spacing-sm);
    }}
    .article-header__title {{
      color: var(--color-white);
      font-size: 2.5rem;
      margin-bottom: var(--spacing-md);
      line-height: 1.2;
    }}
    .article-header__meta {{
      color: var(--color-gray-200);
      font-size: 0.95rem;
    }}
    .article-content {{
      padding: var(--spacing-2xl) 0;
    }}
    .article-content h2 {{
      margin-top: var(--spacing-xl);
      margin-bottom: var(--spacing-md);
    }}
    .article-content h3 {{
      margin-top: var(--spacing-lg);
      margin-bottom: var(--spacing-sm);
    }}
    .article-content p {{
      color: var(--color-slate-blue);
      font-size: 1.1rem;
      line-height: 1.8;
      margin-bottom: var(--spacing-md);
    }}
    .article-content ul, .article-content ol {{
      color: var(--color-slate-blue);
      font-size: 1.1rem;
      line-height: 1.8;
      margin-bottom: var(--spacing-md);
      padding-left: var(--spacing-lg);
    }}
    .article-content li {{
      margin-bottom: var(--spacing-xs);
    }}
    .article-content strong {{
      color: var(--color-charcoal);
    }}
    .key-takeaways {{
      background-color: var(--color-off-white);
      padding: var(--spacing-lg);
      border-radius: 8px;
      margin-top: var(--spacing-xl);
    }}
    .key-takeaways h2 {{
      margin-top: 0;
    }}
    .key-takeaways ol {{
      margin-bottom: 0;
    }}
  </style>
</head>
<body>
  <!-- Header -->
  <header class="header">
    <div class="container">
      <div class="header__inner">
        <a href="../index.html" class="logo">Fit<span>Over35</span></a>
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
  <section class="article-header article-header--bg" style="background-image: url('{hero_image}');">
    <div class="container container--narrow">
      <span class="article-header__category">{_escape_html(category_display)}</span>
      <h1 class="article-header__title">{_escape_html(title)}</h1>
      <p class="article-header__meta">{read_time} min read</p>
    </div>
  </section>

  <!-- Article Content -->
  <article class="article-content">
    <div class="container container--narrow">
      {content_html}

{products_html}
{faq_html}
{affiliate_html}
    </div>
  </article>

  <!-- Email Signup CTA -->
  <section class="section section--dark" id="signup">
    <div class="container">
      <div class="cta">
        <div class="cta__content">
          <h2 class="cta__title">The Weekly System</h2>
          <p class="cta__text">One email per week. No fluff. Just actionable insights on training, nutrition, and the psychology of building a body that lasts. Unsubscribe anytime.</p>
          <form class="signup-form" action="https://app.convertkit.com/forms/{CONVERTKIT_FORM_ID}/subscriptions" method="post" data-sv-form="{CONVERTKIT_FORM_ID}" data-ck-form="lead-magnet" data-uid="" data-format="inline" data-version="5">
            <input type="email" name="email_address" class="signup-form__input" placeholder="Enter your email" required>
            <button type="submit" class="btn btn--primary">Subscribe</button>
          </form>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <div class="footer__grid">
        <div class="footer__brand">
          <a href="../index.html" class="logo">Fit<span>Over35</span></a>
          <p>Evidence-based fitness systems for men who understand that consistency beats intensity. Building bodies and identities since 2010.</p>
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
          <h4 class="footer__title">Topics</h4>
          <ul class="footer__links">
            <li><a href="../blog.html">Training Systems</a></li>
            <li><a href="../blog.html">Nutrition</a></li>
            <li><a href="../blog.html">Recovery</a></li>
            <li><a href="../blog.html">Mindset</a></li>
          </ul>
        </div>
      </div>
      <div class="footer__bottom">
        <p>&copy; {now.year} FitOver35. All rights reserved.</p>
      </div>
    </div>
  </footer>


  <!-- Email Popup Modal -->
  <div class="popup-overlay" id="popupOverlay">
    <div class="popup-modal">
      <button class="popup-close" id="popupClose" aria-label="Close popup">&times;</button>
      <div class="popup-content">
        <h2>Get the 5-Day Density Training Starter Guide</h2>
        <p>Free PDF + weekly training insights for men over 35. No spam. Unsubscribe anytime.</p>
        <form class="signup-form" action="https://app.convertkit.com/forms/{CONVERTKIT_FORM_ID}/subscriptions" method="post" data-sv-form="{CONVERTKIT_FORM_ID}" data-ck-form="lead-magnet" data-uid="" data-format="inline" data-version="5">
          <input type="email" name="email_address" class="signup-form__input" placeholder="Enter your email" required>
          <button type="submit" class="btn btn--primary">Subscribe</button>
        </form>
      </div>
    </div>
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
    var popupShown = false;

    function showPopup() {{
      if (popupShown) return;
      if (sessionStorage.getItem('popupDismissed')) return;
      popupShown = true;
      popupOverlay.classList.add('active');
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

    setTimeout(showPopup, 30000);

    window.addEventListener('scroll', function() {{
      var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      var docHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      if (docHeight > 0 && (scrollTop / docHeight) >= 0.6) {{
        showPopup();
      }}
    }});

    if (window.matchMedia('(pointer: fine)').matches) {{
      document.addEventListener('mouseout', function(e) {{
        if (e.clientY <= 0) {{
          showPopup();
        }}
      }});
    }}
  }})();
  </script>

  <!-- ConvertKit -->
  <script async data-uid="" src="https://fitover35.ck.page/{CONVERTKIT_FORM_ID}/index.js"></script>

  <script src="../js/convertkit.js"></script>
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

    parser = argparse.ArgumentParser(description='Generate FitOver35 SEO article')
    parser.add_argument(
        '--keyword',
        required=True,
        help='Target keyword for the article'
    )
    parser.add_argument(
        '--category',
        default='strength_training',
        help='Article category'
    )
    parser.add_argument(
        '--output',
        help='Output HTML file path'
    )
    parser.add_argument(
        '--output-dir',
        default='outputs/fitover35-website/articles',
        help='Output directory for articles'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate outline only, skip full content'
    )

    args = parser.parse_args()

    generator = FitOver35ArticleGenerator()

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
            # Generate excerpt from meta description
            f.write(f"excerpt={article_data['meta_description']}\n")

    return 0


if __name__ == "__main__":
    exit(main())
