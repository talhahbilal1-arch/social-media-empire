"""
Agent 8: Blog Factory
======================
Runs daily at 7:00 AM after Content Brain

Creates full SEO-optimized blog articles:
- 1000-2000 words
- Proper heading structure (H1, H2, H3)
- Affiliate product recommendations
- Internal links to other posts
- CTA to quiz/lead magnet

Publishes to Netlify and creates social content linking to blogs.
"""
import os
import sys
import json
import re
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient
from core.claude_client import ClaudeClient
from core.netlify_client import NetlifyClient
from core.notifications import send_alert


class BlogFactory:
    """Creates and publishes SEO-optimized blog articles."""

    # Brand-specific blog configuration
    BRAND_CONFIG = {
        'daily_deal_darling': {
            'blog_frequency': 3,  # Articles per week
            'word_count_target': 1500,
            'primary_cta': 'Take our quiz to find your perfect products!',
            'cta_link': 'https://dailydealdarling.com/quiz',
            'topic_categories': [
                'skincare routines',
                'home organization hacks',
                'self-care rituals',
                'amazon finds reviews',
                'beauty product comparisons',
                'lifestyle tips',
                'seasonal decor',
                'gift guides'
            ],
            'seo_focus': ['amazon finds', 'product reviews', 'self care', 'home organization']
        },
        'menopause_planner': {
            'blog_frequency': 2,  # Articles per week
            'word_count_target': 1800,
            'primary_cta': 'Download our free symptom tracker!',
            'cta_link': 'https://themenopauseplanner.com/free-tracker',
            'topic_categories': [
                'menopause symptom management',
                'perimenopause signs',
                'hormone health tips',
                'sleep strategies',
                'nutrition for menopause',
                'exercise for midlife',
                'stress management',
                'supplement reviews'
            ],
            'seo_focus': ['menopause', 'perimenopause', 'hormone health', 'midlife wellness']
        }
    }

    def __init__(self):
        self.db = SupabaseClient()
        self.claude = ClaudeClient()

        # Netlify is optional - can work without publishing
        try:
            self.netlify = NetlifyClient()
            self.can_publish = True
        except ValueError:
            print("Netlify not configured - articles will be saved but not published")
            self.netlify = None
            self.can_publish = False

    def run(self) -> Dict:
        """Main entry point - create blog articles for all brands."""
        run_id = self.db.start_agent_run('blog_factory', os.environ.get('GITHUB_RUN_ID'))

        results = {
            'total_created': 0,
            'total_published': 0,
            'by_brand': {},
            'errors': []
        }

        try:
            brands = self.db.get_active_brands()
            print(f"Creating blog articles for {len(brands)} brands...")

            for brand in brands:
                brand_name = brand['name']
                if brand_name not in self.BRAND_CONFIG:
                    print(f"No blog config for brand: {brand_name}, skipping")
                    continue

                print(f"\n{'='*50}")
                print(f"Processing: {brand['display_name']}")
                print(f"{'='*50}")

                brand_results = self._create_for_brand(brand)
                results['by_brand'][brand_name] = brand_results
                results['total_created'] += brand_results.get('created', 0)
                results['total_published'] += brand_results.get('published', 0)
                results['errors'].extend(brand_results.get('errors', []))

            self.db.complete_agent_run(
                run_id,
                status='completed',
                items_processed=len(brands),
                items_created=results['total_created'],
                items_failed=len(results['errors'])
            )

            print(f"\n{'='*50}")
            print(f"BLOG FACTORY COMPLETE")
            print(f"Created: {results['total_created']}, Published: {results['total_published']}")
            print(f"{'='*50}")

        except Exception as e:
            results['errors'].append(str(e))
            self.db.complete_agent_run(run_id, status='failed', error_log=[str(e)])
            send_alert(
                "Blog Factory Failed",
                f"Blog creation failed with error: {str(e)}",
                severity="error"
            )
            raise

        return results

    def _create_for_brand(self, brand: Dict) -> Dict:
        """Create blog articles for a single brand."""
        brand_id = brand['id']
        brand_name = brand['name']
        config = self.BRAND_CONFIG[brand_name]

        results = {'created': 0, 'published': 0, 'social_created': 0, 'errors': []}

        # Check how many articles we should create today
        # (For daily runs, we create 1 article if it's a publish day)
        articles_to_create = self._get_daily_article_count(config['blog_frequency'])

        if articles_to_create == 0:
            print(f"  No articles scheduled for today (frequency: {config['blog_frequency']}/week)")
            return results

        print(f"  Creating {articles_to_create} article(s)...")

        # Get trends and existing blogs for context
        trends = self.db.get_unused_trends(brand_id, limit=10)
        existing_blogs = self.db.get_recent_blogs(brand_id, limit=10)
        patterns = self.db.get_winning_patterns(brand_id)

        print(f"  Found {len(trends)} trends, {len(existing_blogs)} existing blogs")

        # Generate article topics
        topics = self._generate_topics(brand, config, trends, articles_to_create)
        print(f"  Generated {len(topics)} topics")

        for topic in topics:
            try:
                print(f"\n  Writing: {topic['title'][:50]}...")

                # Generate the article
                article_data = self._generate_article(
                    brand=brand,
                    config=config,
                    topic=topic,
                    trends=trends,
                    existing_blogs=existing_blogs
                )

                if not article_data:
                    results['errors'].append(f"Failed to generate: {topic['title']}")
                    continue

                # Save to database
                article_record = {
                    'brand_id': brand_id,
                    'title': article_data['title'],
                    'slug': article_data['slug'],
                    'meta_description': article_data['meta_description'],
                    'content_markdown': article_data['content_markdown'],
                    'content_html': self._markdown_to_html(article_data['content_markdown']),
                    'featured_image_prompt': article_data.get('featured_image_prompt'),
                    'affiliate_products': article_data.get('affiliate_products', []),
                    'seo_keywords': article_data.get('seo_keywords', []),
                    'word_count': len(article_data['content_markdown'].split()),
                    'reading_time_minutes': max(1, len(article_data['content_markdown'].split()) // 200),
                    'status': 'ready'
                }

                # Add trend reference if used
                if topic.get('trend_id'):
                    article_record['trend_id'] = topic['trend_id']

                saved_article = self.db.save_blog_article(article_record)
                results['created'] += 1
                print(f"    Saved article: {saved_article['id']}")

                # Publish to Netlify if configured
                if self.can_publish:
                    print(f"    Publishing to Netlify...")
                    publish_result = self._publish_article(saved_article, brand)

                    if publish_result.get('success'):
                        self.db.update_blog_status(
                            saved_article['id'],
                            'published',
                            published_url=publish_result['published_url'],
                            netlify_deploy_id=publish_result.get('deploy_id'),
                            published_at=datetime.utcnow().isoformat()
                        )
                        saved_article['published_url'] = publish_result['published_url']
                        results['published'] += 1
                        print(f"    Published: {publish_result['published_url']}")
                    else:
                        results['errors'].append(f"Publish failed: {publish_result.get('error')}")
                        print(f"    Publish failed: {publish_result.get('error')}")

                # Create social content to promote the blog
                social_content = self._create_social_promotion(brand, saved_article, config)
                if social_content:
                    self.db.save_content_batch(social_content)
                    results['social_created'] += len(social_content)
                    print(f"    Created {len(social_content)} social posts to promote blog")

                    # Link social content to blog
                    for content in social_content:
                        if content.get('id'):
                            self.db.link_blog_to_social(saved_article['id'], content['id'])

            except Exception as e:
                results['errors'].append(f"Error with {topic.get('title', 'unknown')}: {str(e)}")
                print(f"    Error: {e}")

        return results

    def _get_daily_article_count(self, weekly_frequency: int) -> int:
        """Determine how many articles to create today based on weekly frequency."""
        # Map day of week (0=Mon, 6=Sun) to publish days
        day = datetime.utcnow().weekday()

        # Spread articles across the week
        if weekly_frequency >= 7:
            return 1  # Publish every day
        elif weekly_frequency >= 5:
            return 1 if day < 5 else 0  # Weekdays only
        elif weekly_frequency >= 3:
            return 1 if day in [0, 2, 4] else 0  # Mon, Wed, Fri
        elif weekly_frequency >= 2:
            return 1 if day in [1, 4] else 0  # Tue, Fri
        elif weekly_frequency >= 1:
            return 1 if day == 2 else 0  # Wednesday only
        return 0

    def _generate_topics(self,
                         brand: Dict,
                         config: Dict,
                         trends: List[Dict],
                         count: int) -> List[Dict]:
        """Generate article topics using Claude."""

        system_prompt = f"""You are an SEO content strategist for {brand['display_name']}.
Your job is to suggest blog article topics that will:
1. Rank well in search engines
2. Provide value to the target audience
3. Naturally incorporate affiliate product recommendations
4. Drive traffic and conversions

TARGET AUDIENCE: {brand['target_audience']}
NICHE: {brand['niche']}
SEO FOCUS KEYWORDS: {', '.join(config['seo_focus'])}"""

        trends_text = "\n".join([
            f"- {t['title']}: {t.get('description', '')[:80]} (ID: {t['id']})"
            for t in trends[:8]
        ]) if trends else "No current trends"

        user_prompt = f"""Generate {count} blog article topic(s).

TRENDING TOPICS TO CONSIDER:
{trends_text}

TOPIC CATEGORIES TO CHOOSE FROM:
{', '.join(config['topic_categories'])}

For each topic, return:
{{
    "title": "SEO-optimized article title",
    "angle": "The unique angle or hook for this article",
    "target_keyword": "Primary keyword to rank for",
    "trend_id": "UUID of trend if using one, null otherwise",
    "products_to_feature": ["product types to recommend"]
}}

Return a JSON array of {count} topic(s)."""

        try:
            topics = self.claude.generate_json(system_prompt, user_prompt)
            return topics if isinstance(topics, list) else [topics]
        except Exception as e:
            print(f"  Topic generation error: {e}")
            # Fallback to basic topic from category
            return [{
                'title': f"Essential Guide to {config['topic_categories'][0].title()}",
                'angle': 'Comprehensive guide for beginners',
                'target_keyword': config['seo_focus'][0],
                'trend_id': None,
                'products_to_feature': []
            }]

    def _generate_article(self,
                          brand: Dict,
                          config: Dict,
                          topic: Dict,
                          trends: List[Dict],
                          existing_blogs: List[Dict]) -> Optional[Dict]:
        """Generate a full blog article using Claude."""

        system_prompt = f"""You are an expert SEO blog writer for {brand['display_name']}.

BRAND VOICE: Friendly, helpful, and knowledgeable. Like a trusted friend sharing advice.
TARGET AUDIENCE: {brand['target_audience']}
WORD COUNT TARGET: {config['word_count_target']} words

Write articles that:
1. Have a compelling, SEO-optimized title (50-60 characters)
2. Use proper heading hierarchy (H2, H3)
3. Are scannable with bullet points and short paragraphs
4. Include natural affiliate product recommendations
5. Have a clear CTA at the end
6. Link to related content when relevant

AFFILIATE TAG: {brand.get('affiliate_tag', 'N/A')}
CTA: {config['primary_cta']}
CTA LINK: {config['cta_link']}"""

        existing_posts = "\n".join([
            f"- {b['title']} ({b['slug']})"
            for b in existing_blogs[:5]
        ]) if existing_blogs else "None yet"

        user_prompt = f"""Write a complete blog article about:
TOPIC: {topic['title']}
ANGLE: {topic.get('angle', 'Comprehensive guide')}
TARGET KEYWORD: {topic.get('target_keyword', topic['title'])}
PRODUCTS TO FEATURE: {', '.join(topic.get('products_to_feature', ['relevant products']))}

EXISTING POSTS TO LINK TO:
{existing_posts}

Return a JSON object with:
{{
    "title": "SEO title (50-60 chars)",
    "slug": "url-friendly-slug",
    "meta_description": "Compelling meta description (150-160 chars)",
    "seo_keywords": ["primary", "secondary", "keywords"],
    "content_markdown": "FULL article in markdown (aim for {config['word_count_target']} words)",
    "featured_image_prompt": "Detailed prompt for hero image",
    "affiliate_products": [
        {{"name": "Product Name", "asin": "if known", "context": "how it's mentioned"}}
    ]
}}

The content_markdown should be a complete, publish-ready article with:
- Engaging introduction with hook
- Multiple H2 sections with H3 subsections
- Bullet points for lists
- Product recommendations with placeholder links
- Internal links to existing posts
- Conclusion with CTA"""

        try:
            return self.claude.generate_json(
                system_prompt,
                user_prompt,
                max_tokens=8000,
                temperature=0.7
            )
        except Exception as e:
            print(f"    Article generation error: {e}")
            return None

    def _publish_article(self, article: Dict, brand: Dict) -> Dict:
        """Publish article to Netlify."""
        if not self.netlify:
            return {'success': False, 'error': 'Netlify not configured'}

        try:
            return self.netlify.publish_article(article, brand)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _create_social_promotion(self,
                                  brand: Dict,
                                  article: Dict,
                                  config: Dict) -> List[Dict]:
        """Create social media content to promote the blog article."""

        # Generate social posts using Claude
        try:
            social_content = self.claude.generate_social_for_blog(
                brand=brand,
                blog=article,
                platforms=['pinterest', 'tiktok', 'instagram']
            )
        except Exception as e:
            print(f"    Social generation error: {e}")
            return []

        # Process and prepare for database
        processed = []
        for item in social_content:
            content = {
                'brand_id': brand['id'],
                'content_type': item.get('content_type', 'pin'),
                'title': item.get('title', article['title'])[:200],
                'description': item.get('description', article['meta_description'])[:500],
                'hashtags': item.get('hashtags', [])[:15],
                'video_script': item.get('video_script'),
                'image_prompt': item.get('image_prompt'),
                'cta_text': item.get('cta_text', 'Read more on the blog!'),
                'destination_link': article.get('published_url', f"/{article['slug']}"),
                'status': 'pending',
                'metadata': {
                    'blog_article_id': article['id'],
                    'generated_at': datetime.utcnow().isoformat()
                }
            }
            processed.append(content)

        return processed

    def _markdown_to_html(self, markdown: str) -> str:
        """Convert markdown to HTML with proper structure."""
        # Use the Netlify client's converter
        try:
            return NetlifyClient._markdown_to_html(None, markdown)
        except:
            # Fallback to simple conversion
            import re
            html = markdown
            html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
            html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
            html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
            html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
            return html


def main():
    """Entry point for GitHub Actions."""
    print(f"Starting Blog Factory at {datetime.utcnow().isoformat()}")

    factory = BlogFactory()
    results = factory.run()

    print(f"\nResults: {json.dumps(results, indent=2)}")
    return results


if __name__ == '__main__':
    main()
