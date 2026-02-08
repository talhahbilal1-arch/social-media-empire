"""
Gemini AI content writer with Chain-of-Density prompting.

Handles:
1. Niche keyword brainstorming (low-competition, high-buyer-intent)
2. Chain-of-Density article generation → Gutenberg-compatible HTML
3. Comparison tables, FAQ Schema.org, CTA buttons, affiliate link injection
4. Featured image prompt generation
"""

import json
import logging
import re
import time
from typing import Optional

import google.generativeai as genai

from anti_gravity.core.config import settings

logger = logging.getLogger(__name__)

# Retry config for 429 rate-limit errors
MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 2


def _call_gemini(model, prompt: str, retries: int = MAX_RETRIES) -> str:
    """Call Gemini with exponential backoff on 429 errors."""
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            err = str(e).lower()
            if "429" in err or "resource_exhausted" in err or "rate" in err:
                wait = BASE_BACKOFF_SECONDS * (2 ** attempt)
                logger.warning(f"Rate limited (attempt {attempt + 1}/{retries}). Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"Gemini rate-limited after {retries} retries")


class Writer:
    """Gemini-powered content writer with intelligence layer."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        key = api_key or settings.GEMINI_API_KEY
        if not key:
            raise ValueError("GEMINI_API_KEY is required")
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(model_name=model_name or settings.GEMINI_MODEL)

    # ------------------------------------------------------------------
    # Step 1: Keyword brainstorming
    # ------------------------------------------------------------------

    def brainstorm_keywords(self, seed_niche: str, count: int = 5) -> list[dict]:
        """
        Ask Gemini to brainstorm low-competition, high-buyer-intent long-tail keywords.

        Returns list of dicts: [{"keyword": "...", "intent": "...", "difficulty": "low"}]
        """
        logger.info(f"Brainstorming {count} keywords for niche: {seed_niche}")

        prompt = f"""You are an expert SEO strategist specializing in affiliate marketing.

Given the seed niche: "{seed_niche}"

Brainstorm exactly {count} long-tail keywords that meet ALL of these criteria:
1. Low competition — not dominated by major authority sites
2. High buyer intent — the searcher is ready to purchase (uses words like "best", "review", "vs", "under $X", "for [specific audience]")
3. Commercially viable — products exist with affiliate programs paying 5%+ commissions
4. Search volume potential — real people search for these monthly

Return ONLY a JSON array. No markdown fences. Example format:
[
  {{"keyword": "best ergonomic chairs for home office under $200", "intent": "comparison-purchase", "difficulty": "low"}},
  {{"keyword": "top wireless earbuds for running 2026", "intent": "best-of-purchase", "difficulty": "low"}}
]"""

        raw = _call_gemini(self.model, prompt)

        # Strip markdown fences if present
        raw = re.sub(r"```json\s*", "", raw)
        raw = re.sub(r"```\s*$", "", raw)

        try:
            keywords = json.loads(raw.strip())
            logger.info(f"Brainstormed {len(keywords)} keywords")
            return keywords
        except json.JSONDecodeError:
            logger.error(f"Failed to parse keyword JSON: {raw[:300]}")
            # Fallback: extract lines that look like keywords
            return [{"keyword": seed_niche, "intent": "general", "difficulty": "unknown"}]

    # ------------------------------------------------------------------
    # Step 2: Chain-of-Density article generation
    # ------------------------------------------------------------------

    def write_article(
        self,
        keyword: str,
        affiliate_link: str = "[AFFILIATE_LINK]",
        min_words: int = 1500,
    ) -> dict:
        """
        Generate a full SEO article using Chain-of-Density prompting.

        Chain of Density:
        - Pass 1: Generate a comprehensive outline with entity-dense notes
        - Pass 2: Expand into full Gutenberg-compatible HTML with all required blocks

        Returns dict with keys: title, slug, html, meta_description, word_count, image_prompt
        """
        logger.info(f"Writing article for keyword: {keyword}")

        # --- Pass 1: Dense outline ---
        outline = self._chain_pass_outline(keyword, min_words)
        logger.info("Chain pass 1 (outline) complete")

        # --- Pass 2: Full HTML article ---
        article = self._chain_pass_article(keyword, outline, affiliate_link, min_words)
        logger.info(f"Chain pass 2 (article) complete — {article['word_count']} words")

        # --- Generate featured image prompt ---
        article["image_prompt"] = self._generate_image_prompt(keyword, article["title"])

        return article

    def _chain_pass_outline(self, keyword: str, min_words: int) -> str:
        """Chain-of-Density Pass 1: entity-dense outline."""
        prompt = f"""You are writing a {min_words}+ word buyer's guide targeting the keyword: "{keyword}"

Create a DETAILED outline that is entity-dense. For every section, list:
- The exact H2/H3 heading
- 3-5 specific entities, facts, or data points to include
- Any products to compare (with real names)

Sections MUST include:
1. Introduction (hook + why this matters now)
2. How We Evaluated (methodology gives authority)
3. Top Picks Comparison Table (3-5 products)
4. Individual Product Deep-Dives (H3 per product)
5. Buyer's Guide: What to Look For (decision factors)
6. FAQ (5+ real questions people ask)
7. Final Verdict + CTA

For the comparison table, identify 3-5 REAL products with:
- Product name
- Key differentiating spec
- Price range
- Best-for category

Return the outline as structured text. Be specific — no generic placeholders."""

        return _call_gemini(self.model, prompt)

    def _chain_pass_article(
        self,
        keyword: str,
        outline: str,
        affiliate_link: str,
        min_words: int,
    ) -> dict:
        """Chain-of-Density Pass 2: full Gutenberg HTML from the outline."""
        prompt = f"""You are a senior affiliate content writer. Using the outline below, write a complete
{min_words}+ word article targeting: "{keyword}"

OUTPUT FORMAT: Valid Gutenberg-compatible HTML blocks. Each block wrapped in WordPress comments:

<!-- wp:heading {{"level":2}} -->
<h2>Heading Text</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>Paragraph text here.</p>
<!-- /wp:paragraph -->

REQUIRED BLOCKS (you MUST include ALL of these):

1. **Comparison Table** — Use this exact structure:
<!-- wp:table {{"className":"is-style-stripes"}} -->
<figure class="wp-block-table is-style-stripes"><table><thead><tr>
<th>Product</th><th>Best For</th><th>Key Feature</th><th>Price</th><th>Rating</th>
</tr></thead><tbody>
<tr><td>Product Name</td><td>Category</td><td>Feature</td><td>$XX-$XX</td><td>X.X/5</td></tr>
</tbody></table></figure>
<!-- /wp:table -->

2. **FAQ Section with Schema.org** — Use this exact structure:
<!-- wp:heading {{"level":2}} -->
<h2>Frequently Asked Questions</h2>
<!-- /wp:heading -->
<div itemscope itemtype="https://schema.org/FAQPage">
<div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
<h3 itemprop="name">Question text here?</h3>
<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
<p itemprop="text">Answer text here.</p>
</div></div>
</div>

Include at least 5 FAQ items based on real questions people ask about "{keyword}".

3. **CTA Buttons** — Use this structure (place after introduction AND at the end):
<!-- wp:buttons {{"layout":{{"type":"flex","justifyContent":"center"}}}} -->
<div class="wp-block-buttons">
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="{affiliate_link}" target="_blank" rel="noopener nofollow sponsored">Check Latest Price &rarr;</a></div>
</div>
<!-- /wp:buttons -->

4. **Affiliate links** — Weave the link {affiliate_link} naturally into product names and recommendation text using:
<a href="{affiliate_link}" target="_blank" rel="noopener nofollow sponsored">anchor text</a>

WRITING RULES:
- Write like an authoritative expert who has personally tested these products
- Use specific numbers, measurements, and comparisons — never vague superlatives
- Vary sentence length. Mix short punchy sentences with detailed explanations.
- Address the reader directly with "you"
- NO AI clichés: "In today's world", "It's worth noting", "Look no further", "game-changer"
- Every paragraph must deliver value — zero filler

OUTLINE TO EXPAND:
{outline}

Return ONLY the HTML content. Start with the H1 title heading. No markdown. No explanations outside the HTML."""

        raw_html = _call_gemini(self.model, prompt)

        # Extract title from first H1
        title = self._extract_h1(raw_html, keyword)

        # Generate slug from title
        slug = self._slugify(title)

        # Count words (strip HTML tags)
        text_only = re.sub(r"<[^>]+>", " ", raw_html)
        text_only = re.sub(r"<!--[^>]+-->", " ", text_only)
        word_count = len(text_only.split())

        # Generate meta description
        meta = self._generate_meta(keyword, title)

        return {
            "title": title,
            "slug": slug,
            "html": raw_html,
            "meta_description": meta,
            "word_count": word_count,
        }

    # ------------------------------------------------------------------
    # Step 3: Featured image prompt
    # ------------------------------------------------------------------

    def _generate_image_prompt(self, keyword: str, title: str) -> str:
        """Generate a text-to-image prompt for the article's featured image."""
        prompt = f"""Create a single text-to-image prompt for a blog featured image.

Article title: "{title}"
Keyword: "{keyword}"

Requirements:
- Photorealistic style, clean and professional
- No text or watermarks in the image
- Bright, well-lit product/lifestyle photography aesthetic
- 16:9 aspect ratio composition
- Should convey trust and quality

Return ONLY the image generation prompt, nothing else. Keep it under 100 words."""

        return _call_gemini(self.model, prompt).strip()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_h1(self, html: str, fallback_keyword: str) -> str:
        """Extract title from the first <h1> tag."""
        match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
        if match:
            # Strip inner HTML tags
            return re.sub(r"<[^>]+>", "", match.group(1)).strip()
        return f"The Ultimate Guide to {fallback_keyword} ({time.strftime('%Y')})"

    def _slugify(self, title: str) -> str:
        """Convert a title to a URL-safe slug."""
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")[:200]

    def _generate_meta(self, keyword: str, title: str) -> str:
        """Generate an SEO meta description under 155 characters."""
        prompt = f"""Write a compelling SEO meta description for this article:
Title: {title}
Target keyword: {keyword}

Rules:
- Exactly 130-155 characters
- Include the keyword naturally
- Include a call-to-action
- No quotes around the text

Return ONLY the meta description text."""

        meta = _call_gemini(self.model, prompt).strip().strip('"')
        return meta[:155]

    # ------------------------------------------------------------------
    # Pin content generation
    # ------------------------------------------------------------------

    def generate_pin_variations(self, title: str, keyword: str, url: str) -> list[dict]:
        """
        Generate 3 distinct Pinterest pin variations for a blog post.

        Returns list of dicts: [{"title": "...", "description": "...", "link": url}]
        """
        logger.info(f"Generating 3 pin variations for: {title}")

        prompt = f"""Create 3 DISTINCT Pinterest pin variations for this blog post:

Title: "{title}"
Keyword: "{keyword}"
Link: {url}

For each variation, provide:
- pin_title: Catchy, different angle (max 100 chars). Use numbers, questions, or power words.
- pin_description: SEO-optimized (150-300 chars). Include the keyword, a benefit, and a CTA like "Read the full guide at the link!"

Make each variation appeal to a different audience segment or emotion:
1. Practical/helpful angle
2. Urgency/FOMO angle
3. Aspirational/lifestyle angle

Return ONLY a JSON array. No markdown fences:
[
  {{"pin_title": "...", "pin_description": "..."}},
  {{"pin_title": "...", "pin_description": "..."}},
  {{"pin_title": "...", "pin_description": "..."}}
]"""

        raw = _call_gemini(self.model, prompt)
        raw = re.sub(r"```json\s*", "", raw)
        raw = re.sub(r"```\s*$", "", raw)

        try:
            variations = json.loads(raw.strip())
        except json.JSONDecodeError:
            logger.error("Failed to parse pin variations, using fallback")
            variations = [
                {"pin_title": title, "pin_description": f"Discover {keyword}. Read the guide!"},
                {"pin_title": f"Best {keyword} Guide", "pin_description": f"Everything about {keyword}. Tap to read!"},
                {"pin_title": f"{keyword}: What You Need to Know", "pin_description": f"Expert picks for {keyword}. Full guide inside!"},
            ]

        # Attach the link to each variation
        for v in variations:
            v["link"] = url

        return variations[:3]
