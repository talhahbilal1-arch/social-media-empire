"""
Claude Client - AI content generation for all agents
"""
import os
import json
from typing import Dict, List, Optional, Any
import anthropic


class ClaudeClient:
    """Wrapper for Claude API operations."""

    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"  # Good balance of quality and cost

    def generate(self,
                 system_prompt: str,
                 user_prompt: str,
                 max_tokens: int = 4096,
                 temperature: float = 0.7) -> str:
        """Generate text response from Claude."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return message.content[0].text

    def generate_json(self,
                      system_prompt: str,
                      user_prompt: str,
                      max_tokens: int = 4096,
                      temperature: float = 0.7) -> Dict:
        """Generate and parse JSON response from Claude."""
        # Add JSON instruction to system prompt
        json_system = f"""{system_prompt}

IMPORTANT: Your response must be valid JSON only. No markdown, no explanation, just the JSON object or array."""

        response = self.generate(json_system, user_prompt, max_tokens, temperature)

        # Clean up response in case Claude adds markdown
        clean_response = response.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:]
        if clean_response.startswith('```'):
            clean_response = clean_response[3:]
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3]

        return json.loads(clean_response.strip())

    def generate_content_ideas(self,
                               brand: Dict,
                               trends: List[Dict],
                               winning_patterns: List[Dict],
                               count: int = 10) -> List[Dict]:
        """Generate content ideas based on trends and patterns."""

        system_prompt = f"""You are an expert social media content strategist for affiliate marketing.

BRAND: {brand['display_name']}
NICHE: {brand['niche']}
TARGET AUDIENCE: {brand['target_audience']}
WEBSITE: {brand.get('website_url', 'N/A')}
AFFILIATE TAG: {brand.get('affiliate_tag', 'N/A')}

Your job is to create engaging social media content that:
1. Captures attention in the first 2 seconds
2. Provides value to the target audience
3. Naturally leads to affiliate product recommendations
4. Uses proven viral patterns and hooks

Generate content in JSON format."""

        trends_text = "\n".join([
            f"- {t['title']}: {t.get('description', '')} (Source: {t['source']}, Type: {t['discovery_type']})"
            for t in trends[:15]
        ]) if trends else "No current trends available"

        patterns_text = "\n".join([
            f"- {p['pattern_type']}: {p['pattern_value']} (Engagement: {p['avg_engagement']:.2f})"
            for p in winning_patterns[:10]
        ]) if winning_patterns else "No patterns established yet - use best practices"

        user_prompt = f"""Generate {count} unique content ideas.

CURRENT TRENDS TO USE:
{trends_text}

WINNING PATTERNS TO FOLLOW:
{patterns_text}

For each piece of content, provide:
{{
    "content_type": "pin" | "video" | "reel" | "short" | "blog_promo",
    "title": "Attention-grabbing title (max 100 chars)",
    "description": "Engaging description with hashtags for social (max 500 chars)",
    "hashtags": ["relevant", "hashtags", "array"],
    "video_script": "If video/reel/short: Full script with hook, body, CTA (null for pins)",
    "image_prompt": "Detailed prompt for AI image generation",
    "cta_text": "Call to action text",
    "trend_id": "ID of trend used if applicable, null otherwise",
    "affiliate_products": [
        {{"asin": "if known", "name": "Product name", "why": "Why this product fits"}}
    ]
}}

Return a JSON array of {count} content ideas."""

        return self.generate_json(system_prompt, user_prompt)

    def generate_blog_article(self,
                              brand: Dict,
                              topic: str,
                              trends: List[Dict],
                              existing_blogs: List[Dict],
                              affiliate_products: List[Dict] = None) -> Dict:
        """Generate a full SEO-optimized blog article."""

        system_prompt = f"""You are an expert SEO content writer for affiliate marketing blogs.

BRAND: {brand['display_name']}
NICHE: {brand['niche']}
TARGET AUDIENCE: {brand['target_audience']}
WEBSITE: {brand.get('website_url', 'N/A')}
AFFILIATE TAG: {brand.get('affiliate_tag', 'N/A')}

Write engaging, helpful articles that:
1. Rank well in search engines (proper H1, H2, H3 structure)
2. Provide genuine value to readers
3. Naturally incorporate affiliate product recommendations
4. Include clear calls-to-action
5. Are 1000-2000 words

Always use markdown format for the content."""

        existing_posts = "\n".join([
            f"- [{b['title']}]({b.get('published_url', b['slug'])})"
            for b in existing_blogs[:5]
        ]) if existing_blogs else "No existing posts yet"

        trends_context = "\n".join([
            f"- {t['title']}: {t.get('description', '')}"
            for t in trends[:5]
        ]) if trends else "Write evergreen content"

        products_context = "\n".join([
            f"- {p.get('name', p.get('asin', 'Product'))}: {p.get('why', 'Relevant to topic')}"
            for p in (affiliate_products or [])[:5]
        ]) if affiliate_products else "Recommend relevant products from Amazon"

        user_prompt = f"""Write a complete blog article about: {topic}

TRENDING CONTEXT:
{trends_context}

EXISTING POSTS TO LINK TO:
{existing_posts}

PRODUCTS TO FEATURE:
{products_context}

Return a JSON object with:
{{
    "title": "SEO-optimized title (50-60 chars)",
    "slug": "url-friendly-slug",
    "meta_description": "Compelling meta description (150-160 chars)",
    "seo_keywords": ["primary", "secondary", "keywords"],
    "content_markdown": "Full article in markdown format with proper headings",
    "featured_image_prompt": "Detailed prompt for hero image",
    "affiliate_products": [
        {{"asin": "B0...", "name": "Product Name", "context": "Where/how mentioned"}}
    ],
    "internal_links": ["slugs of posts to link to"],
    "word_count": 1500,
    "reading_time_minutes": 7
}}"""

        return self.generate_json(system_prompt, user_prompt, max_tokens=8000)

    def generate_social_for_blog(self,
                                 brand: Dict,
                                 blog: Dict,
                                 platforms: List[str]) -> List[Dict]:
        """Generate social media posts to promote a blog article."""

        system_prompt = f"""You are a social media expert creating promotional content for blog posts.

BRAND: {brand['display_name']}
TARGET AUDIENCE: {brand['target_audience']}

Create engaging social posts that drive traffic to the blog article.
Each platform has different requirements:
- Pinterest: Vertical images, keywords in description, save-worthy content
- TikTok/Reels/Shorts: Hook in first 2 seconds, value-packed, CTA at end
- Twitter: Concise, engaging, thread-worthy"""

        user_prompt = f"""Create promotional social content for this blog post:

TITLE: {blog['title']}
URL: {blog.get('published_url', f"/{blog['slug']}")}
SUMMARY: {blog.get('meta_description', 'See article')}
KEYWORDS: {', '.join(blog.get('seo_keywords', []))}

Create content for platforms: {', '.join(platforms)}

Return a JSON array with one object per platform:
[
    {{
        "content_type": "pin" | "video" | "reel" | "short",
        "platform": "pinterest" | "tiktok" | "instagram" | "youtube",
        "title": "Platform-appropriate title",
        "description": "Platform-appropriate description with hashtags",
        "hashtags": ["relevant", "hashtags"],
        "video_script": "Script if video content, null otherwise",
        "image_prompt": "Image prompt if static content",
        "cta_text": "Call to action",
        "destination_link": "{blog.get('published_url', f'/{blog["slug"]}')}"
    }}
]"""

        return self.generate_json(system_prompt, user_prompt)

    def analyze_performance(self,
                           analytics_data: List[Dict],
                           current_patterns: List[Dict]) -> Dict:
        """Analyze performance data and suggest optimizations."""

        system_prompt = """You are a data analyst specializing in social media performance optimization.

Analyze the provided analytics data and identify:
1. What content performs best
2. Optimal posting times
3. Best performing hashtags and topics
4. Underperforming content to retire
5. New patterns to test

Be specific and actionable in your recommendations."""

        user_prompt = f"""Analyze this performance data:

RECENT ANALYTICS:
{json.dumps(analytics_data[:50], indent=2)}

CURRENT WINNING PATTERNS:
{json.dumps(current_patterns, indent=2)}

Return a JSON object with:
{{
    "new_patterns": [
        {{"pattern_type": "topic|hashtag|posting_time|format|hook", "pattern_value": "value", "confidence": 0.8, "reason": "why"}}
    ],
    "retire_patterns": [
        {{"pattern_type": "type", "pattern_value": "value", "reason": "why"}}
    ],
    "schedule_changes": [
        {{"platform": "platform", "current_time": "HH:MM", "suggested_time": "HH:MM", "reason": "why"}}
    ],
    "content_recommendations": [
        {{"recommendation": "description", "priority": "high|medium|low", "expected_impact": "description"}}
    ],
    "summary": "Brief executive summary of findings"
}}"""

        return self.generate_json(system_prompt, user_prompt, max_tokens=4096)
