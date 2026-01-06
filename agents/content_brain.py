"""
Agent 1: Content Brain
=======================
Runs daily at 6:00 AM after Trend Discovery

Uses Claude to generate 10-20 content pieces per day per brand based on:
- Trending discoveries from Agent 7
- Winning patterns from historical performance
- Brand-specific guidelines and prompts

Outputs to content_bank table for Video Factory and Multi-Platform Poster.
"""
import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient
from core.claude_client import ClaudeClient
from core.notifications import send_alert


class ContentBrain:
    """AI-powered content generation engine."""

    # Brand-specific content guidelines
    BRAND_GUIDELINES = {
        'daily_deal_darling': {
            'voice': 'Friendly, relatable, deal-savvy. Like a best friend sharing her favorite finds.',
            'content_mix': {
                'pin': 0.40,      # 40% Pinterest pins
                'video': 0.25,   # 25% video content
                'reel': 0.15,    # 15% Reels/TikTok
                'short': 0.10,   # 10% YouTube Shorts
                'blog_promo': 0.10  # 10% blog promotions
            },
            'hooks': [
                "This $X product changed my routine...",
                "Amazon finds you NEED right now",
                "Why didn't I buy this sooner?!",
                "The viral product that actually works",
                "Self-care Sunday essentials"
            ],
            'ctas': [
                "Link in bio!",
                "Save for later!",
                "Take our quiz to find your perfect products",
                "Shop the look",
                "Found on Amazon - link below"
            ],
            'hashtag_pools': {
                'pinterest': ['amazonfinds', 'beautyfinds', 'homedecor', 'selfcare', 'organization', 'skincare', 'lifestyle', 'homeorganization'],
                'tiktok': ['amazonfinds', 'tiktokmademebuyit', 'selfcare', 'grwm', 'beauty', 'lifestyle', 'amazonmusthaves'],
                'instagram': ['amazonfinds', 'selfcare', 'homedecor', 'beautytips', 'organization', 'lifestylecontent']
            }
        },
        'menopause_planner': {
            'voice': 'Supportive, understanding, empowering. A knowledgeable friend who gets what you are going through.',
            'content_mix': {
                'pin': 0.50,      # 50% Pinterest pins (primary platform)
                'video': 0.20,   # 20% video content
                'reel': 0.15,    # 15% Reels
                'short': 0.05,   # 5% YouTube Shorts
                'blog_promo': 0.10  # 10% blog promotions
            },
            'hooks': [
                "If you are in perimenopause, you need to know this...",
                "The symptom tracker that changed everything",
                "What I wish I knew before menopause",
                "This is your sign to prioritize yourself",
                "Menopause doesn't have to be a struggle"
            ],
            'ctas': [
                "Download our free tracker",
                "Save this for later",
                "Check out our Etsy shop",
                "You are not alone in this journey",
                "Get your planner today"
            ],
            'hashtag_pools': {
                'pinterest': ['menopause', 'perimenopause', 'womenshealth', 'selfcare', 'planner', 'tracker', 'wellness', 'over40'],
                'tiktok': ['menopause', 'perimenopause', 'over40', 'womenshealth', 'midlife', 'hormones'],
                'instagram': ['menopause', 'perimenopause', 'womenshealth', 'menopausesupport', 'midlifewoman', 'hormonehealth']
            }
        }
    }

    def __init__(self):
        self.db = SupabaseClient()
        self.claude = ClaudeClient()

    def run(self) -> Dict:
        """Main entry point - generate content for all brands."""
        run_id = self.db.start_agent_run('content_brain', os.environ.get('GITHUB_RUN_ID'))

        results = {
            'total_generated': 0,
            'by_brand': {},
            'errors': []
        }

        try:
            brands = self.db.get_active_brands()
            print(f"Generating content for {len(brands)} brands...")

            for brand in brands:
                brand_name = brand['name']
                if brand_name not in self.BRAND_GUIDELINES:
                    print(f"No guidelines for brand: {brand_name}, skipping")
                    continue

                print(f"\n{'='*50}")
                print(f"Generating for: {brand['display_name']}")
                print(f"{'='*50}")

                brand_results = self._generate_for_brand(brand)
                results['by_brand'][brand_name] = brand_results
                results['total_generated'] += brand_results.get('total', 0)
                results['errors'].extend(brand_results.get('errors', []))

            self.db.complete_agent_run(
                run_id,
                status='completed',
                items_processed=len(brands),
                items_created=results['total_generated'],
                items_failed=len(results['errors'])
            )

            print(f"\n{'='*50}")
            print(f"CONTENT BRAIN COMPLETE")
            print(f"Total generated: {results['total_generated']}")
            print(f"{'='*50}")

        except Exception as e:
            results['errors'].append(str(e))
            self.db.complete_agent_run(run_id, status='failed', error_log=[str(e)])
            send_alert(
                "Content Brain Failed",
                f"Content generation failed with error: {str(e)}",
                severity="error"
            )
            raise

        return results

    def _generate_for_brand(self, brand: Dict) -> Dict:
        """Generate content for a single brand."""
        brand_id = brand['id']
        brand_name = brand['name']
        guidelines = self.BRAND_GUIDELINES[brand_name]

        results = {'total': 0, 'by_type': {}, 'errors': []}

        # Get configuration
        config = self.db.get_config(brand_id, 'content_generation') or {
            'daily_pieces': 10,
            'video_ratio': 0.3
        }
        target_pieces = config.get('daily_pieces', 10)

        # Get fresh trends
        trends = self.db.get_unused_trends(brand_id, limit=15)
        print(f"  Found {len(trends)} unused trends")

        # Get winning patterns
        patterns = self.db.get_winning_patterns(brand_id)
        print(f"  Found {len(patterns)} winning patterns")

        # Calculate content mix based on guidelines
        content_mix = self._calculate_content_mix(target_pieces, guidelines['content_mix'])
        print(f"  Target content mix: {content_mix}")

        # Generate content in batches by type
        all_content = []

        for content_type, count in content_mix.items():
            if count == 0:
                continue

            try:
                print(f"  Generating {count} {content_type}s...")
                content_pieces = self._generate_content_batch(
                    brand=brand,
                    guidelines=guidelines,
                    trends=trends,
                    patterns=patterns,
                    content_type=content_type,
                    count=count
                )
                all_content.extend(content_pieces)
                results['by_type'][content_type] = len(content_pieces)
                print(f"    Created {len(content_pieces)} {content_type}s")

            except Exception as e:
                results['errors'].append(f"{content_type}: {str(e)}")
                print(f"    Error generating {content_type}: {e}")

        # Save all content to database
        if all_content:
            saved = self.db.save_content_batch(all_content)
            results['total'] = len(saved)

            # Mark used trends
            used_trend_ids = set(c.get('trend_id') for c in all_content if c.get('trend_id'))
            for trend_id in used_trend_ids:
                self.db.mark_trend_used(trend_id)
            print(f"  Marked {len(used_trend_ids)} trends as used")

        return results

    def _calculate_content_mix(self, total: int, mix_ratios: Dict[str, float]) -> Dict[str, int]:
        """Calculate actual piece counts from ratios."""
        content_mix = {}
        allocated = 0

        # Sort by ratio descending to allocate larger buckets first
        sorted_types = sorted(mix_ratios.items(), key=lambda x: x[1], reverse=True)

        for content_type, ratio in sorted_types[:-1]:
            count = round(total * ratio)
            content_mix[content_type] = count
            allocated += count

        # Last type gets remainder
        last_type = sorted_types[-1][0]
        content_mix[last_type] = max(0, total - allocated)

        return content_mix

    def _generate_content_batch(self,
                                 brand: Dict,
                                 guidelines: Dict,
                                 trends: List[Dict],
                                 patterns: List[Dict],
                                 content_type: str,
                                 count: int) -> List[Dict]:
        """Generate a batch of content of a specific type."""

        # Build the system prompt
        system_prompt = self._build_system_prompt(brand, guidelines, content_type)

        # Build user prompt with trends and patterns
        user_prompt = self._build_user_prompt(
            brand=brand,
            guidelines=guidelines,
            trends=trends,
            patterns=patterns,
            content_type=content_type,
            count=count
        )

        # Generate with Claude
        try:
            content_array = self.claude.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=4096,
                temperature=0.8  # Higher creativity for content
            )
        except Exception as e:
            print(f"      Claude generation error: {e}")
            return []

        # Process and validate generated content
        processed = []
        for item in content_array:
            try:
                content = self._process_content_item(brand, guidelines, item, content_type)
                if content:
                    processed.append(content)
            except Exception as e:
                print(f"      Error processing item: {e}")

        return processed

    def _build_system_prompt(self, brand: Dict, guidelines: Dict, content_type: str) -> str:
        """Build the system prompt for Claude."""
        type_instructions = {
            'pin': """
Create Pinterest pins that:
- Have compelling, keyword-rich titles (max 100 chars)
- Include descriptive, searchable descriptions
- Use relevant hashtags for discovery
- Include a clear image prompt for visual creation
- Drive clicks to the destination link""",
            'video': """
Create short-form video scripts (15-60 seconds) that:
- Hook viewers in the first 2 seconds
- Deliver value quickly
- End with a clear call-to-action
- Work for TikTok, Reels, and YouTube Shorts
- Include specific visual directions""",
            'reel': """
Create Instagram Reels scripts (15-30 seconds) that:
- Start with a pattern interrupt hook
- Are visually engaging
- End with engagement prompt (save, share, comment)
- Use trending audio suggestions when relevant""",
            'short': """
Create YouTube Shorts scripts (under 60 seconds) that:
- Open with curiosity or value promise
- Deliver quick, actionable tips
- Encourage subscription
- Work well with vertical video format""",
            'blog_promo': """
Create social posts that promote blog articles:
- Tease the value without giving everything away
- Create curiosity to click through
- Highlight key takeaways
- Drive traffic to the blog"""
        }

        return f"""You are an expert social media content creator for affiliate marketing.

BRAND: {brand['display_name']}
NICHE: {brand['niche']}
TARGET AUDIENCE: {brand['target_audience']}
WEBSITE: {brand.get('website_url', 'N/A')}
AFFILIATE TAG: {brand.get('affiliate_tag', 'N/A')}

BRAND VOICE: {guidelines['voice']}

CONTENT TYPE: {content_type.upper()}
{type_instructions.get(content_type, '')}

EXAMPLE HOOKS: {', '.join(guidelines['hooks'][:3])}
EXAMPLE CTAs: {', '.join(guidelines['ctas'][:3])}

Your content should:
1. Match the brand voice perfectly
2. Appeal to the target audience
3. Incorporate trending topics when relevant
4. Include clear affiliate product opportunities
5. Be authentic and helpful, not salesy

Return ONLY valid JSON array, no markdown or explanation."""

    def _build_user_prompt(self,
                           brand: Dict,
                           guidelines: Dict,
                           trends: List[Dict],
                           patterns: List[Dict],
                           content_type: str,
                           count: int) -> str:
        """Build the user prompt with trends and patterns."""

        # Format trends
        trends_text = "\n".join([
            f"- [{t['discovery_type']}] {t['title']}: {t.get('description', '')[:100]} (ID: {t['id']})"
            for t in trends[:10]
        ]) if trends else "No specific trends - create evergreen content"

        # Format winning patterns
        patterns_text = "\n".join([
            f"- {p['pattern_type']}: {p['pattern_value']} (engagement: {p['avg_engagement']:.2f})"
            for p in patterns[:8]
        ]) if patterns else "No established patterns - use best practices"

        # Get platform-specific hashtags
        platform_map = {
            'pin': 'pinterest',
            'video': 'tiktok',
            'reel': 'instagram',
            'short': 'tiktok',  # Shorts use similar hashtags
            'blog_promo': 'pinterest'
        }
        platform = platform_map.get(content_type, 'pinterest')
        hashtag_pool = guidelines['hashtag_pools'].get(platform, [])

        return f"""Generate {count} unique {content_type} content pieces.

CURRENT TRENDS TO INCORPORATE:
{trends_text}

WINNING PATTERNS TO USE:
{patterns_text}

HASHTAG POOL TO USE: {', '.join(hashtag_pool)}

For each piece, return this exact JSON structure:
{{
    "title": "Attention-grabbing title (max 100 chars)",
    "description": "Engaging description with hashtags (max 500 chars)",
    "hashtags": ["array", "of", "hashtags"],
    "video_script": "Full script if video/reel/short, null for pins",
    "image_prompt": "Detailed prompt for AI image generation",
    "cta_text": "Call to action",
    "trend_id": "UUID of trend used or null",
    "affiliate_products": [
        {{"name": "Product Name", "asin": "if known or null", "reason": "why recommended"}}
    ]
}}

Return a JSON array of exactly {count} items. Each must be unique and engaging."""

    def _process_content_item(self,
                               brand: Dict,
                               guidelines: Dict,
                               item: Dict,
                               content_type: str) -> Optional[Dict]:
        """Process and validate a generated content item."""

        # Validate required fields
        if not item.get('title'):
            return None

        # Build the content record
        content = {
            'brand_id': brand['id'],
            'content_type': content_type,
            'title': item['title'][:200],
            'description': item.get('description', '')[:500],
            'hashtags': item.get('hashtags', [])[:15],
            'video_script': item.get('video_script'),
            'image_prompt': item.get('image_prompt'),
            'cta_text': item.get('cta_text', guidelines['ctas'][0]),
            'destination_link': brand.get('website_url', ''),
            'affiliate_products': item.get('affiliate_products', []),
            'status': 'pending',
            'performance_score': 0,
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'generator': 'content_brain_v1'
            }
        }

        # Link to trend if used
        trend_id = item.get('trend_id')
        if trend_id and self._is_valid_uuid(trend_id):
            content['trend_id'] = trend_id

        # Add Amazon affiliate links if products specified
        if brand.get('affiliate_tag') and content['affiliate_products']:
            for product in content['affiliate_products']:
                if product.get('asin'):
                    product['affiliate_link'] = f"https://www.amazon.com/dp/{product['asin']}?tag={brand['affiliate_tag']}"

        return content

    def _is_valid_uuid(self, value: str) -> bool:
        """Check if string is a valid UUID."""
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
        return bool(uuid_pattern.match(str(value)))


def main():
    """Entry point for GitHub Actions."""
    print(f"Starting Content Brain at {datetime.utcnow().isoformat()}")

    brain = ContentBrain()
    results = brain.run()

    print(f"\nResults: {json.dumps(results, indent=2)}")
    return results


if __name__ == '__main__':
    main()
