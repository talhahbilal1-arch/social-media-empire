"""
Article generator using Google Gemini AI.

Generates SEO-optimized articles with:
- Meta tags and descriptions
- Proper heading structure (H1, H2, H3)
- Product recommendations with affiliate links
- FAQ section with schema markup
- Internal linking to other articles
"""

import os
import re
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import google.generativeai as genai

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Article templates and prompts
OUTLINE_PROMPT = """Create an SEO-optimized article outline for the keyword: "{keyword}"

The article should:
1. Target users searching for buying advice
2. Include 4-6 main sections (H2 headings)
3. Have a compelling introduction
4. Include product recommendations where relevant
5. End with a FAQ section (3-4 questions)

Return the outline in this JSON format:
{{
    "title": "SEO-optimized title (60 chars max)",
    "meta_description": "Compelling description (155 chars max)",
    "intro_hook": "Opening sentence to grab attention",
    "sections": [
        {{
            "heading": "H2 heading text",
            "subheadings": ["H3 if needed"],
            "key_points": ["Main points to cover"],
            "products_to_mention": 0-2
        }}
    ],
    "faq": [
        {{
            "question": "Common question?",
            "answer_points": ["Key points for answer"]
        }}
    ],
    "internal_links": ["Related topics to link to"]
}}
"""

SECTION_PROMPT = """Write the content for this article section:

Article topic: {keyword}
Section heading: {heading}
Key points to cover: {key_points}

Write 150-250 words that:
- Are helpful and informative
- Use natural language (avoid keyword stuffing)
- Include specific details and examples
- Mention product recommendations naturally if relevant

Return just the paragraph content, no headings.
"""

FAQ_PROMPT = """Write an FAQ answer for:

Question: {question}
Key points: {answer_points}
Article topic: {keyword}

Write a concise 50-100 word answer that:
- Directly answers the question
- Is helpful and accurate
- Mentions relevant products if appropriate

Return just the answer text.
"""


class ArticleGenerator:
    """Generate SEO articles using Gemini AI."""

    AFFILIATE_TAG = "dailydealdarl-20"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Gemini API key."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def _call_gemini(self, prompt: str) -> str:
        """Make a Gemini API call."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    def generate_outline(self, keyword: str) -> dict:
        """Generate article outline."""
        logger.info(f"Generating outline for: {keyword}")

        prompt = OUTLINE_PROMPT.format(keyword=keyword)
        response = self._call_gemini(prompt)

        # Extract JSON from response
        try:
            # Find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in response")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse outline JSON: {e}")
            logger.debug(f"Response was: {response}")
            raise

    def generate_section(self, keyword: str, heading: str, key_points: list) -> str:
        """Generate content for a section."""
        logger.info(f"Generating section: {heading}")

        prompt = SECTION_PROMPT.format(
            keyword=keyword,
            heading=heading,
            key_points=", ".join(key_points)
        )
        return self._call_gemini(prompt)

    def generate_faq_answer(self, keyword: str, question: str, answer_points: list) -> str:
        """Generate FAQ answer."""
        prompt = FAQ_PROMPT.format(
            keyword=keyword,
            question=question,
            answer_points=", ".join(answer_points)
        )
        return self._call_gemini(prompt)

    def generate_full_article(self, keyword: str, category: str) -> dict:
        """
        Generate a complete article.

        Args:
            keyword: Target keyword
            category: Article category

        Returns:
            Dict with all article components
        """
        logger.info(f"Generating full article for: {keyword}")

        # Generate outline
        outline = self.generate_outline(keyword)

        # Generate intro
        intro = self._call_gemini(
            f"Write a 100-150 word introduction for an article about '{keyword}'. "
            f"Start with: {outline.get('intro_hook', '')} "
            "Make it engaging and establish credibility."
        )

        # Generate each section
        sections = []
        for section in outline.get('sections', []):
            content = self.generate_section(
                keyword=keyword,
                heading=section['heading'],
                key_points=section.get('key_points', [])
            )
            sections.append({
                'heading': section['heading'],
                'content': content,
                'subheadings': section.get('subheadings', []),
            })

        # Generate FAQ
        faq_items = []
        for faq in outline.get('faq', []):
            answer = self.generate_faq_answer(
                keyword=keyword,
                question=faq['question'],
                answer_points=faq.get('answer_points', [])
            )
            faq_items.append({
                'question': faq['question'],
                'answer': answer,
            })

        return {
            'keyword': keyword,
            'category': category,
            'title': outline.get('title', keyword.title()),
            'meta_description': outline.get('meta_description', ''),
            'intro': intro,
            'sections': sections,
            'faq': faq_items,
            'internal_links': outline.get('internal_links', []),
            'generated_at': datetime.now(timezone.utc).isoformat(),
        }


def generate_html(article_data: dict, template_path: Optional[str] = None) -> str:
    """
    Convert article data to HTML.

    Args:
        article_data: Output from ArticleGenerator.generate_full_article()
        template_path: Optional path to custom template

    Returns:
        Complete HTML string
    """
    title = article_data['title']
    meta_desc = article_data['meta_description']
    category = article_data['category']
    intro = article_data['intro']
    sections = article_data['sections']
    faq = article_data['faq']

    # Calculate read time (average 200 words per minute)
    total_words = len(intro.split())
    for section in sections:
        total_words += len(section['content'].split())
    read_time = max(3, total_words // 200)

    # Generate sections HTML
    sections_html = ""
    for section in sections:
        sections_html += f"""
      <section class="article-section">
        <h2>{section['heading']}</h2>
        <p>{section['content']}</p>
      </section>
"""

    # Generate FAQ HTML with schema
    faq_html = ""
    faq_schema_items = []
    if faq:
        faq_html = """
      <section class="article-section faq-section">
        <h2>Frequently Asked Questions</h2>
"""
        for item in faq:
            faq_html += f"""
        <div class="faq-item">
          <h3>{item['question']}</h3>
          <p>{item['answer']}</p>
        </div>
"""
            faq_schema_items.append({
                "@type": "Question",
                "name": item['question'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item['answer']
                }
            })
        faq_html += "      </section>"

    # Build schema JSON-LD
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": meta_desc,
        "datePublished": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "dateModified": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "author": {
            "@type": "Organization",
            "name": "Daily Deal Darling"
        }
    }

    faq_schema = ""
    if faq_schema_items:
        faq_schema_obj = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_schema_items
        }
        faq_schema = f"""
  <script type="application/ld+json">
  {json.dumps(faq_schema_obj, indent=2)}
  </script>"""

    # Build full HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{meta_desc}">
  <title>{title} | Daily Deal Darling</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:wght@600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/styles.css">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>💝</text></svg>">
  <script type="application/ld+json">
  {json.dumps(schema, indent=2)}
  </script>{faq_schema}
</head>
<body>
  <header class="header">
    <div class="container">
      <nav class="nav">
        <a href="../index.html" class="logo">💝 Daily Deal Darling</a>
        <ul class="nav-menu">
          <li><a href="../index.html#categories" class="nav-link">Categories</a></li>
          <li><a href="../index.html#bestsellers" class="nav-link">Best Sellers</a></li>
          <li><a href="../index.html#deals" class="nav-link">Today's Deals</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main>
    <article class="article-container">
      <div class="article-hero">
        <div class="breadcrumbs">
          <a href="../index.html">Home</a> / <a href="../index.html#categories">{category.title()}</a> / <span>{title}</span>
        </div>
        <h1>{title}</h1>
        <div class="article-meta">
          <span>Updated {datetime.now(timezone.utc).strftime("%B %d, %Y")}</span>
          <span>{read_time} min read</span>
        </div>
      </div>

      <div class="article-body">
        <div class="article-intro">
          <p>{intro}</p>
        </div>
{sections_html}
{faq_html}
        <div class="article-cta">
          <p><strong>Found this helpful?</strong> Check out our other buying guides for more recommendations.</p>
          <a href="../index.html#categories" class="btn btn-primary">Browse All Categories →</a>
        </div>
      </div>
    </article>
  </main>

  <footer class="footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-brand">
          <a href="../index.html" class="logo">💝 Daily Deal Darling</a>
          <p>Expert-curated product recommendations with honest reviews.</p>
        </div>
      </div>
      <div class="footer-bottom">
        <p class="footer-disclosure">
          <strong>Affiliate Disclosure:</strong> Daily Deal Darling is a participant in the Amazon Services LLC Associates Program. When you click links and make purchases, we may earn a commission at no extra cost to you.
        </p>
        <p>&copy; {datetime.now(timezone.utc).year} Daily Deal Darling. All rights reserved.</p>
      </div>
    </div>
  </footer>
</body>
</html>"""

    return html


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate SEO article')
    parser.add_argument(
        '--keyword',
        required=True,
        help='Target keyword for the article'
    )
    parser.add_argument(
        '--category',
        default='general',
        help='Article category'
    )
    parser.add_argument(
        '--output',
        help='Output HTML file path'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate outline only, skip full content'
    )

    args = parser.parse_args()

    generator = ArticleGenerator()

    if args.dry_run:
        # Just generate outline
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
        slug = args.keyword.lower().replace(' ', '-').replace('?', '')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')[:50]
        output_path = Path(f"dailydealdarling_website/articles/{slug}.html")

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    output_path.write_text(html, encoding='utf-8')
    logger.info(f"Article written to: {output_path}")

    print(f"\n{'='*60}")
    print(f"ARTICLE GENERATED: {article_data['title']}")
    print(f"{'='*60}")
    print(f"Output: {output_path}")
    print(f"Word count: ~{len(html.split())}")
    print(f"Sections: {len(article_data['sections'])}")
    print(f"FAQ items: {len(article_data['faq'])}")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    exit(main())
