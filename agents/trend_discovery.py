"""
Agent 7: Trend Discovery Engine
================================
Runs daily at 5:00 AM before Content Brain

Discovers trending topics, products, and news relevant to each brand.
Sources:
- Amazon Best Sellers & Movers and Shakers
- Google Trends
- Pinterest Trends
- Reddit (relevant subreddits)
- News APIs

Saves discoveries to Supabase for Content Brain to use.
"""
import os
import sys
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import feedparser

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient
from core.claude_client import ClaudeClient
from core.notifications import send_alert


class TrendDiscoveryEngine:
    """Discovers trending content for each brand."""

    # Brand-specific configuration
    BRAND_CONFIG = {
        'daily_deal_darling': {
            'amazon_categories': [
                'beauty',
                'home-garden',
                'health-personal-care',
                'kitchen',
                'handmade'
            ],
            'subreddits': [
                'SkincareAddiction',
                'MakeupAddiction',
                'HomeDecorating',
                'organization',
                'selfcare',
                'Frugal',
                'deals'
            ],
            'google_trends_keywords': [
                'skincare routine',
                'home organization',
                'self care products',
                'amazon finds',
                'beauty hacks'
            ],
            'news_topics': ['beauty', 'lifestyle', 'wellness', 'home decor']
        },
        'menopause_planner': {
            'amazon_categories': [
                'health-personal-care',
                'books',
                'sports-outdoors'
            ],
            'subreddits': [
                'Menopause',
                'WomensHealth',
                'Perimenopause',
                'HealthyAging',
                'selfcare'
            ],
            'google_trends_keywords': [
                'menopause symptoms',
                'perimenopause',
                'hormone health',
                'menopause supplements',
                'hot flashes relief'
            ],
            'news_topics': ['menopause', 'women health', 'hormone therapy', 'aging wellness']
        }
    }

    def __init__(self):
        self.db = SupabaseClient()
        self.claude = ClaudeClient()
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def run(self) -> Dict:
        """Main entry point - discover trends for all brands."""
        run_id = self.db.start_agent_run('trend_discovery', os.environ.get('GITHUB_RUN_ID'))

        results = {
            'total_discovered': 0,
            'by_brand': {},
            'by_source': {},
            'errors': []
        }

        try:
            brands = self.db.get_active_brands()
            print(f"Discovering trends for {len(brands)} brands...")

            for brand in brands:
                brand_name = brand['name']
                if brand_name not in self.BRAND_CONFIG:
                    print(f"No config for brand: {brand_name}, skipping")
                    continue

                print(f"\n{'='*50}")
                print(f"Processing brand: {brand['display_name']}")
                print(f"{'='*50}")

                brand_results = await self._discover_for_brand(brand)
                results['by_brand'][brand_name] = brand_results

                # Aggregate by source
                for source, count in brand_results.get('by_source', {}).items():
                    results['by_source'][source] = results['by_source'].get(source, 0) + count

                results['total_discovered'] += brand_results.get('total', 0)
                results['errors'].extend(brand_results.get('errors', []))

            # Cleanup old trends
            cleaned = self.db.cleanup_expired_trends()
            print(f"\nCleaned up {cleaned} expired trends")

            self.db.complete_agent_run(
                run_id,
                status='completed',
                items_processed=len(brands),
                items_created=results['total_discovered'],
                items_failed=len(results['errors'])
            )

            print(f"\n{'='*50}")
            print(f"TREND DISCOVERY COMPLETE")
            print(f"Total discovered: {results['total_discovered']}")
            print(f"{'='*50}")

        except Exception as e:
            results['errors'].append(str(e))
            self.db.complete_agent_run(run_id, status='failed', error_log=[str(e)])
            send_alert(
                "Trend Discovery Failed",
                f"The trend discovery agent failed with error: {str(e)}",
                severity="error"
            )
            raise

        return results

    async def _discover_for_brand(self, brand: Dict) -> Dict:
        """Discover trends for a single brand."""
        brand_id = brand['id']
        brand_name = brand['name']
        config = self.BRAND_CONFIG[brand_name]

        results = {'total': 0, 'by_source': {}, 'errors': []}
        all_discoveries = []

        # Run all discovery sources concurrently
        tasks = [
            self._discover_amazon(brand_id, config['amazon_categories']),
            self._discover_reddit(brand_id, config['subreddits']),
            self._discover_news(brand_id, config['news_topics']),
            self._discover_google_trends(brand_id, config['google_trends_keywords']),
        ]

        source_results = await asyncio.gather(*tasks, return_exceptions=True)

        sources = ['amazon', 'reddit', 'news', 'google_trends']
        for source, result in zip(sources, source_results):
            if isinstance(result, Exception):
                results['errors'].append(f"{source}: {str(result)}")
                print(f"  Error in {source}: {result}")
            else:
                all_discoveries.extend(result)
                results['by_source'][source] = len(result)
                print(f"  {source}: {len(result)} discoveries")

        # Deduplicate by title similarity
        unique_discoveries = self._deduplicate(all_discoveries)
        print(f"  Deduplicated: {len(all_discoveries)} -> {len(unique_discoveries)}")

        # Score relevance using Claude
        if unique_discoveries:
            scored = await self._score_relevance(brand, unique_discoveries)
            unique_discoveries = scored

        # Save to database
        if unique_discoveries:
            saved = self.db.save_trends_batch(unique_discoveries)
            results['total'] = len(saved)

        return results

    async def _discover_amazon(self, brand_id: str, categories: List[str]) -> List[Dict]:
        """Discover trending products from Amazon Best Sellers."""
        discoveries = []

        for category in categories[:3]:  # Limit to avoid rate limiting
            try:
                # Using Amazon's Best Sellers RSS feeds (public)
                url = f"https://www.amazon.com/gp/rss/bestsellers/{category}"
                async with self.session.get(url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)

                        for entry in feed.entries[:5]:  # Top 5 per category
                            discoveries.append({
                                'brand_id': brand_id,
                                'discovery_type': 'product',
                                'title': entry.get('title', '')[:200],
                                'description': self._clean_html(entry.get('summary', ''))[:500],
                                'source': 'amazon',
                                'source_url': entry.get('link', ''),
                                'source_data': {
                                    'category': category,
                                    'asin': self._extract_asin(entry.get('link', ''))
                                },
                                'relevance_score': 0.7,
                                'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat()
                            })
            except Exception as e:
                print(f"    Amazon {category} error: {e}")

        return discoveries

    async def _discover_reddit(self, brand_id: str, subreddits: List[str]) -> List[Dict]:
        """Discover trending topics from Reddit."""
        discoveries = []

        for subreddit in subreddits[:5]:  # Limit subreddits
            try:
                # Use Reddit's public JSON API (no auth needed for read)
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
                async with self.session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = data.get('data', {}).get('children', [])

                        for post in posts[:5]:
                            post_data = post.get('data', {})
                            # Skip stickied/pinned posts
                            if post_data.get('stickied'):
                                continue

                            score = post_data.get('score', 0)
                            # Only include posts with decent engagement
                            if score < 50:
                                continue

                            discoveries.append({
                                'brand_id': brand_id,
                                'discovery_type': 'topic',
                                'title': post_data.get('title', '')[:200],
                                'description': post_data.get('selftext', '')[:500] or 'Discussion thread',
                                'source': 'reddit',
                                'source_url': f"https://reddit.com{post_data.get('permalink', '')}",
                                'source_data': {
                                    'subreddit': subreddit,
                                    'score': score,
                                    'num_comments': post_data.get('num_comments', 0)
                                },
                                'relevance_score': min(0.9, 0.5 + (score / 1000)),
                                'expires_at': (datetime.utcnow() + timedelta(days=3)).isoformat()
                            })

                # Be nice to Reddit's API
                await asyncio.sleep(1)

            except Exception as e:
                print(f"    Reddit r/{subreddit} error: {e}")

        return discoveries

    async def _discover_news(self, brand_id: str, topics: List[str]) -> List[Dict]:
        """Discover trending news using Google News RSS."""
        discoveries = []

        for topic in topics[:3]:
            try:
                # Google News RSS (public, no API key needed)
                url = f"https://news.google.com/rss/search?q={topic}&hl=en-US&gl=US&ceid=US:en"
                async with self.session.get(url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)

                        for entry in feed.entries[:3]:  # Top 3 per topic
                            discoveries.append({
                                'brand_id': brand_id,
                                'discovery_type': 'news',
                                'title': entry.get('title', '')[:200],
                                'description': self._clean_html(entry.get('summary', ''))[:500],
                                'source': 'news',
                                'source_url': entry.get('link', ''),
                                'source_data': {
                                    'topic': topic,
                                    'published': entry.get('published', '')
                                },
                                'relevance_score': 0.6,
                                'expires_at': (datetime.utcnow() + timedelta(days=2)).isoformat()
                            })
            except Exception as e:
                print(f"    News {topic} error: {e}")

        return discoveries

    async def _discover_google_trends(self, brand_id: str, keywords: List[str]) -> List[Dict]:
        """
        Discover Google Trends data.

        Note: Google Trends doesn't have a public API. We use the trending searches
        RSS feed and infer relevance from our keywords.
        """
        discoveries = []

        try:
            # Google Trends Daily Trending Searches
            url = "https://trends.google.com/trending/rss?geo=US"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)

                    for entry in feed.entries[:10]:
                        title = entry.get('title', '')
                        # Check if any of our keywords are related
                        title_lower = title.lower()
                        is_relevant = any(kw.lower() in title_lower for kw in keywords)

                        if is_relevant:
                            discoveries.append({
                                'brand_id': brand_id,
                                'discovery_type': 'search_term',
                                'title': title[:200],
                                'description': entry.get('summary', '')[:500],
                                'source': 'google_trends',
                                'source_url': entry.get('link', ''),
                                'source_data': {
                                    'traffic': entry.get('ht_approx_traffic', 'N/A')
                                },
                                'relevance_score': 0.8,
                                'expires_at': (datetime.utcnow() + timedelta(days=1)).isoformat()
                            })
        except Exception as e:
            print(f"    Google Trends error: {e}")

        # Also create trend entries from our keywords for Content Brain to use
        for keyword in keywords[:3]:
            discoveries.append({
                'brand_id': brand_id,
                'discovery_type': 'search_term',
                'title': keyword,
                'description': f"Evergreen keyword for content generation: {keyword}",
                'source': 'google_trends',
                'source_url': f"https://trends.google.com/trends/explore?q={keyword.replace(' ', '%20')}",
                'source_data': {'type': 'evergreen_keyword'},
                'relevance_score': 0.5,
                'expires_at': (datetime.utcnow() + timedelta(days=14)).isoformat()
            })

        return discoveries

    async def _score_relevance(self, brand: Dict, discoveries: List[Dict]) -> List[Dict]:
        """Use Claude to score relevance of discoveries."""
        try:
            # Batch discoveries for efficiency
            discovery_texts = [
                f"- {d['title']}: {d.get('description', '')[:100]} (source: {d['source']})"
                for d in discoveries[:30]  # Limit to avoid token limits
            ]

            prompt = f"""Score these discoveries for relevance to the brand.

BRAND: {brand['display_name']}
NICHE: {brand['niche']}
TARGET AUDIENCE: {brand['target_audience']}

DISCOVERIES:
{chr(10).join(discovery_texts)}

Return a JSON array with the same order, each item having:
{{"index": 0, "score": 0.8, "reason": "why relevant or not"}}

Score from 0.0 (not relevant) to 1.0 (highly relevant).
Only return the JSON array, nothing else."""

            system = "You are a content relevance scoring system. Return only valid JSON."
            scores = self.claude.generate_json(system, prompt)

            # Apply scores
            for score_item in scores:
                idx = score_item.get('index', 0)
                if idx < len(discoveries):
                    discoveries[idx]['relevance_score'] = score_item.get('score', 0.5)

        except Exception as e:
            print(f"  Relevance scoring error: {e}")

        return discoveries

    def _deduplicate(self, discoveries: List[Dict]) -> List[Dict]:
        """Remove duplicate discoveries based on title similarity."""
        seen_titles = set()
        unique = []

        for d in discoveries:
            # Normalize title for comparison
            title_key = d['title'].lower().strip()[:50]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique.append(d)

        return unique

    def _clean_html(self, html: str) -> str:
        """Remove HTML tags from string."""
        if not html:
            return ''
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator=' ', strip=True)

    def _extract_asin(self, url: str) -> Optional[str]:
        """Extract Amazon ASIN from URL."""
        if not url:
            return None
        # Amazon URLs contain ASIN after /dp/ or /gp/product/
        import re
        match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url)
        return match.group(1) if match else None


async def main():
    """Entry point for GitHub Actions."""
    print(f"Starting Trend Discovery at {datetime.utcnow().isoformat()}")

    async with TrendDiscoveryEngine() as engine:
        results = await engine.run()

    print(f"\nResults: {json.dumps(results, indent=2)}")
    return results


if __name__ == '__main__':
    asyncio.run(main())
