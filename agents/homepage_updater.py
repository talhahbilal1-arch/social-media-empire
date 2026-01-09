"""
Homepage Updater - Updates dailydealdarling.com homepage with articles section
================================================================================
Run this after Blog Factory to add new articles to the homepage.

Creates an articles section below the quiz grid with links to published blog posts.
"""
import os
import sys
import hashlib
import requests
from datetime import datetime
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient


class HomepageUpdater:
    """Updates the Daily Deal Darling homepage with articles section."""

    def __init__(self):
        self.db = SupabaseClient()
        self.netlify_token = os.environ.get('NETLIFY_API_TOKEN')
        self.netlify_site_id = os.environ.get('NETLIFY_SITE_ID')
        self.base_url = "https://api.netlify.com/api/v1"

        if not self.netlify_token:
            raise ValueError("NETLIFY_API_TOKEN environment variable required")

    def run(self) -> Dict:
        """Main entry point - update homepage with articles."""
        print(f"Starting Homepage Updater at {datetime.utcnow().isoformat()}")

        results = {
            'articles_found': 0,
            'deployed': False,
            'errors': []
        }

        try:
            # Get published articles for Daily Deal Darling
            articles = self._get_published_articles()
            results['articles_found'] = len(articles)
            print(f"Found {len(articles)} published articles")

            # Generate the updated homepage HTML
            homepage_html = self._generate_homepage(articles)
            print(f"Generated homepage HTML ({len(homepage_html)} bytes)")

            # Deploy to Netlify
            deploy_result = self._deploy_homepage(homepage_html)

            if deploy_result.get('success'):
                results['deployed'] = True
                results['deploy_id'] = deploy_result.get('deploy_id')
                print(f"Successfully deployed! Deploy ID: {deploy_result.get('deploy_id')}")
            else:
                results['errors'].append(deploy_result.get('error'))
                print(f"Deploy failed: {deploy_result.get('error')}")

        except Exception as e:
            results['errors'].append(str(e))
            print(f"Error: {e}")
            raise

        return results

    def _get_published_articles(self) -> List[Dict]:
        """Fetch published articles from Supabase."""
        try:
            # Get Daily Deal Darling brand ID
            brands = self.db.get_active_brands()
            ddd_brand = next((b for b in brands if b['name'] == 'daily_deal_darling'), None)

            if not ddd_brand:
                print("Daily Deal Darling brand not found")
                return []

            # Get published articles
            response = self.db.client.table('blog_articles').select('*').eq(
                'brand_id', ddd_brand['id']
            ).eq('status', 'published').order(
                'published_at', desc=True
            ).limit(6).execute()

            return response.data if response.data else []

        except Exception as e:
            print(f"Error fetching articles: {e}")
            return []

    def _generate_homepage(self, articles: List[Dict]) -> str:
        """Generate the complete homepage HTML with articles section."""

        # Generate article cards HTML
        articles_html = ""
        if articles:
            for i, article in enumerate(articles):
                delay = 0.9 + (i * 0.1)  # Staggered animation
                category = self._extract_category(article)
                excerpt = self._get_excerpt(article)
                thumbnail = article.get('featured_image_url') or self._get_placeholder_image(category)

                articles_html += f'''
            <a href="/blog/{article['slug']}/" class="article-card" style="animation-delay: {delay}s">
                <div class="article-image-container">
                    <img src="{thumbnail}" alt="{article['title']}" class="article-image" loading="lazy">
                </div>
                <div class="article-content">
                    <span class="article-category">{category}</span>
                    <h3>{article['title']}</h3>
                    <p>{excerpt}</p>
                    <span class="article-cta">Read More <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span>
                </div>
            </a>'''
        else:
            # Placeholder when no articles exist yet
            articles_html = '''
            <div class="no-articles">
                <p>Fresh articles coming soon! Check back for curated product guides and reviews.</p>
            </div>'''

        # Build the complete homepage
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Find Your Perfect Products | Daily Deal Darling</title>
    <meta name="description" content="Discover curated product recommendations tailored to your lifestyle. Take our quick quizzes and find your perfect matches in beauty, home, self-care, and more.">

    <!-- Open Graph -->
    <meta property="og:title" content="Daily Deal Darling - Curated Finds for Your Best Life">
    <meta property="og:description" content="Take our quick quizzes to find personalized product recommendations.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://dailydealdarling.com">

    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=Cormorant+Garamond:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --blush: #F5E6E0;
            --rose: #E8C4C4;
            --terracotta: #C68B77;
            --sage: #A8B5A0;
            --cream: #FDF8F5;
            --charcoal: #3D3D3D;
            --gold: #C9A962;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, var(--cream) 0%, var(--blush) 50%, var(--rose) 100%);
            min-height: 100vh;
            color: var(--charcoal);
            overflow-x: hidden;
        }}

        .grain-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            opacity: 0.03;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            position: relative;
            z-index: 1;
        }}

        header {{
            text-align: center;
            padding: 3rem 0 4rem;
            animation: fadeInDown 1s ease-out;
        }}

        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .logo {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 2.5rem;
            font-weight: 600;
            color: var(--terracotta);
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}

        .tagline {{
            font-size: 1rem;
            color: var(--charcoal);
            opacity: 0.7;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            font-weight: 300;
        }}

        /* Navigation */
        nav {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1.5rem;
        }}

        nav a {{
            color: var(--charcoal);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            opacity: 0.8;
            transition: all 0.3s ease;
            padding: 0.5rem 1rem;
            border-radius: 20px;
        }}

        nav a:hover {{
            opacity: 1;
            background: rgba(255,255,255,0.5);
            color: var(--terracotta);
        }}

        .hero {{
            text-align: center;
            margin-bottom: 4rem;
            animation: fadeIn 1.2s ease-out 0.3s both;
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}

        .hero h1 {{
            font-family: 'Cormorant Garamond', serif;
            font-size: clamp(2.5rem, 6vw, 4rem);
            font-weight: 400;
            line-height: 1.2;
            margin-bottom: 1.5rem;
            color: var(--charcoal);
        }}

        .hero h1 em {{
            font-style: italic;
            color: var(--terracotta);
        }}

        .hero p {{
            font-size: 1.15rem;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.7;
            opacity: 0.85;
        }}

        .quiz-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }}

        .quiz-card {{
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 2.5rem;
            text-decoration: none;
            color: var(--charcoal);
            border: 1px solid rgba(255, 255, 255, 0.5);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.8s ease-out both;
        }}

        .quiz-card:nth-child(1) {{ animation-delay: 0.4s; }}
        .quiz-card:nth-child(2) {{ animation-delay: 0.5s; }}
        .quiz-card:nth-child(3) {{ animation-delay: 0.6s; }}
        .quiz-card:nth-child(4) {{ animation-delay: 0.7s; }}
        .quiz-card:nth-child(5) {{ animation-delay: 0.8s; }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(40px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .quiz-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--terracotta), var(--gold));
            transform: scaleX(0);
            transition: transform 0.4s ease;
        }}

        .quiz-card:hover::before {{
            transform: scaleX(1);
        }}

        .quiz-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 25px 50px rgba(198, 139, 119, 0.2);
            background: rgba(255, 255, 255, 0.9);
        }}

        .quiz-icon {{
            width: 70px;
            height: 70px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin-bottom: 1.5rem;
            transition: transform 0.3s ease;
        }}

        .quiz-card:hover .quiz-icon {{
            transform: scale(1.1) rotate(5deg);
        }}

        .quiz-card.morning .quiz-icon {{ background: linear-gradient(135deg, #FFE5B4, #FFD89B); }}
        .quiz-card.organization .quiz-icon {{ background: linear-gradient(135deg, #B8E0D2, #95D5B2); }}
        .quiz-card.selfcare .quiz-icon {{ background: linear-gradient(135deg, #E8D5E3, #DEC9E5); }}
        .quiz-card.beauty .quiz-icon {{ background: linear-gradient(135deg, #F5CAC3, #F2B5B1); }}
        .quiz-card.lifestyle .quiz-icon {{ background: linear-gradient(135deg, #BDE0FE, #A2D2FF); }}

        .quiz-card h2 {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.6rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }}

        .quiz-card p {{
            font-size: 0.95rem;
            line-height: 1.6;
            opacity: 0.8;
            margin-bottom: 1.5rem;
        }}

        .quiz-cta {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 500;
            color: var(--terracotta);
            font-size: 0.9rem;
        }}

        .quiz-cta svg {{
            transition: transform 0.3s ease;
        }}

        .quiz-card:hover .quiz-cta svg {{
            transform: translateX(5px);
        }}

        .time-badge {{
            display: inline-block;
            background: var(--cream);
            padding: 0.3rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            color: var(--charcoal);
            opacity: 0.7;
            margin-bottom: 1rem;
        }}

        /* Articles Section */
        .articles-section {{
            margin-top: 5rem;
            padding-top: 3rem;
            border-top: 1px solid rgba(198, 139, 119, 0.2);
        }}

        .section-title {{
            font-family: 'Cormorant Garamond', serif;
            font-size: clamp(2rem, 4vw, 2.8rem);
            font-weight: 400;
            text-align: center;
            margin-bottom: 0.75rem;
            color: var(--charcoal);
        }}

        .section-subtitle {{
            text-align: center;
            font-size: 1.1rem;
            opacity: 0.75;
            margin-bottom: 3rem;
        }}

        .articles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 2rem;
        }}

        .article-card {{
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            text-decoration: none;
            color: var(--charcoal);
            border: 1px solid rgba(255, 255, 255, 0.5);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
            animation: fadeInUp 0.8s ease-out both;
        }}

        .article-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 25px 50px rgba(198, 139, 119, 0.2);
            background: rgba(255, 255, 255, 0.9);
        }}

        .article-image-container {{
            width: 100%;
            aspect-ratio: 16/9;
            overflow: hidden;
        }}

        .article-image {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.4s ease;
        }}

        .article-card:hover .article-image {{
            transform: scale(1.05);
        }}

        .article-content {{
            padding: 1.5rem;
        }}

        .article-category {{
            display: inline-block;
            background: linear-gradient(135deg, var(--terracotta), var(--gold));
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.7rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.75rem;
        }}

        .article-content h3 {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            line-height: 1.3;
        }}

        .article-content p {{
            font-size: 0.9rem;
            line-height: 1.6;
            opacity: 0.8;
            margin-bottom: 1rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .article-cta {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 500;
            color: var(--terracotta);
            font-size: 0.85rem;
        }}

        .article-cta svg {{
            transition: transform 0.3s ease;
        }}

        .article-card:hover .article-cta svg {{
            transform: translateX(5px);
        }}

        .no-articles {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 3rem;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 20px;
        }}

        .no-articles p {{
            font-size: 1.1rem;
            opacity: 0.7;
        }}

        footer {{
            text-align: center;
            padding: 4rem 2rem 2rem;
            font-size: 0.85rem;
            opacity: 0.6;
        }}

        footer a {{
            color: var(--terracotta);
            text-decoration: none;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}
            header {{
                padding: 2rem 0 3rem;
            }}
            .logo {{
                font-size: 2rem;
            }}
            nav {{
                gap: 1rem;
            }}
            nav a {{
                font-size: 0.8rem;
                padding: 0.4rem 0.8rem;
            }}
            .quiz-grid,
            .articles-grid {{
                grid-template-columns: 1fr;
            }}
            .quiz-card {{
                padding: 2rem;
            }}
            .articles-section {{
                margin-top: 3rem;
                padding-top: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="grain-overlay"></div>

    <div class="container">
        <header>
            <h1 class="logo">Daily Deal Darling</h1>
            <p class="tagline">Curated Finds for Your Best Life</p>
            <nav>
                <a href="#quizzes">Quizzes</a>
                <a href="#articles">Articles</a>
                <a href="/blog/">All Posts</a>
            </nav>
        </header>

        <section class="hero">
            <h1>Discover Products <em>Made for You</em></h1>
            <p>Take our quick quizzes to find personalized recommendations that match your unique lifestyle, preferences, and goals. It only takes 2 minutes!</p>
        </section>

        <div class="quiz-grid" id="quizzes">
            <a href="/quiz-morning" class="quiz-card morning">
                <span class="time-badge">2 min</span>
                <div class="quiz-icon">🌅</div>
                <h2>Morning Routine Quiz</h2>
                <p>Wake up refreshed and energized. Find products that transform your mornings from chaotic to calm.</p>
                <span class="quiz-cta">Start Quiz <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span>
            </a>

            <a href="/quiz-organization" class="quiz-card organization">
                <span class="time-badge">2 min</span>
                <div class="quiz-icon">🏠</div>
                <h2>Home Organization Quiz</h2>
                <p>Declutter your space, declutter your mind. Discover storage solutions that actually work for you.</p>
                <span class="quiz-cta">Start Quiz <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span>
            </a>

            <a href="/quiz-selfcare" class="quiz-card selfcare">
                <span class="time-badge">2 min</span>
                <div class="quiz-icon">🧘‍</div>
                <h2>Self-Care Quiz</h2>
                <p>You deserve to feel your best. Find relaxation and wellness products tailored to your stress-relief style.</p>
                <span class="quiz-cta">Start Quiz <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span>
            </a>

            <a href="/quiz-beauty" class="quiz-card beauty">
                <span class="time-badge">2 min</span>
                <div class="quiz-icon">✨</div>
                <h2>Beauty Match Quiz</h2>
                <p>Unlock your glow with skincare and beauty products perfectly matched to your skin type and goals.</p>
                <span class="quiz-cta">Start Quiz <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span>
            </a>

            <a href="/quiz-lifestyle" class="quiz-card lifestyle">
                <span class="time-badge">2 min</span>
                <div class="quiz-icon">💫</div>
                <h2>Lifestyle Upgrade Quiz</h2>
                <p>Elevate your everyday with products that boost productivity, wellness, and happiness.</p>
                <span class="quiz-cta">Start Quiz <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg></span>
            </a>
        </div>

        <section class="articles-section" id="articles">
            <h2 class="section-title">Latest Finds & Guides</h2>
            <p class="section-subtitle">Curated articles with our top product picks</p>

            <div class="articles-grid">
{articles_html}
            </div>
        </section>
    </div>

    <footer>
        <p>&copy; {datetime.utcnow().year} Daily Deal Darling &middot; <a href="https://dailydealdarling.com">dailydealdarling.com</a></p>
        <p>As an Amazon Associate, we earn from qualifying purchases.</p>
    </footer>
</body>
</html>'''

        return html

    def _extract_category(self, article: Dict) -> str:
        """Extract category from article keywords or title."""
        keywords = article.get('seo_keywords', []) or []
        title = article.get('title', '').lower()

        categories = {
            'Beauty': ['beauty', 'skincare', 'makeup', 'skin', 'glow'],
            'Home': ['home', 'organization', 'storage', 'decor', 'house'],
            'Self-Care': ['self-care', 'selfcare', 'wellness', 'relax', 'stress'],
            'Lifestyle': ['lifestyle', 'productivity', 'daily', 'routine'],
            'Deals': ['deal', 'amazon', 'finds', 'best', 'top']
        }

        for category, terms in categories.items():
            for term in terms:
                if any(term in kw.lower() for kw in keywords) or term in title:
                    return category

        return 'Lifestyle'

    def _get_excerpt(self, article: Dict) -> str:
        """Get article excerpt from meta description or content."""
        if article.get('meta_description'):
            return article['meta_description'][:150]

        content = article.get('content_markdown', '') or article.get('content_html', '')
        # Strip HTML/markdown and get first 150 chars
        import re
        text = re.sub(r'<[^>]+>', '', content)
        text = re.sub(r'[#*_\[\]()]', '', text)
        text = ' '.join(text.split())
        return text[:150] + '...' if len(text) > 150 else text

    def _get_placeholder_image(self, category: str) -> str:
        """Get placeholder image URL for category."""
        # Use Unsplash source for category-appropriate placeholders
        category_images = {
            'Beauty': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=600&h=338&fit=crop',
            'Home': 'https://images.unsplash.com/photo-1484101403633-562f891dc89a?w=600&h=338&fit=crop',
            'Self-Care': 'https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=600&h=338&fit=crop',
            'Lifestyle': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=600&h=338&fit=crop',
            'Deals': 'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=600&h=338&fit=crop'
        }
        return category_images.get(category, category_images['Lifestyle'])

    def _deploy_homepage(self, html_content: str) -> Dict:
        """Deploy the homepage to Netlify."""
        headers = {
            "Authorization": f"Bearer {self.netlify_token}",
            "Content-Type": "application/json"
        }

        try:
            # Get current site info and existing files
            site_response = requests.get(
                f"{self.base_url}/sites/{self.netlify_site_id}",
                headers=headers
            )
            site_response.raise_for_status()
            site_data = site_response.json()

            # Get current deploy to preserve existing files
            current_deploy_id = site_data.get('published_deploy', {}).get('id')
            existing_files = {}

            if current_deploy_id:
                files_response = requests.get(
                    f"{self.base_url}/deploys/{current_deploy_id}/files",
                    headers=headers
                )
                if files_response.status_code == 200:
                    for f in files_response.json():
                        existing_files[f['path']] = f['sha']

            # Calculate hash for new index.html
            file_content = html_content.encode('utf-8')
            file_hash = hashlib.sha1(file_content).hexdigest()

            # Update index.html in the files map
            existing_files['/index.html'] = file_hash

            # Create new deploy
            deploy_response = requests.post(
                f"{self.base_url}/sites/{self.netlify_site_id}/deploys",
                headers=headers,
                json={"files": existing_files}
            )
            deploy_response.raise_for_status()
            deploy = deploy_response.json()
            deploy_id = deploy['id']

            # Upload the file if needed
            required_files = deploy.get('required', [])
            if file_hash in required_files:
                upload_response = requests.put(
                    f"{self.base_url}/deploys/{deploy_id}/files/index.html",
                    headers={
                        "Authorization": f"Bearer {self.netlify_token}",
                        "Content-Type": "application/octet-stream"
                    },
                    data=file_content
                )
                upload_response.raise_for_status()

            return {
                'success': True,
                'deploy_id': deploy_id
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Netlify API error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }


def main():
    """Entry point for GitHub Actions."""
    updater = HomepageUpdater()
    results = updater.run()

    import json
    print(f"\nResults: {json.dumps(results, indent=2)}")

    if results.get('errors'):
        sys.exit(1)

    return results


if __name__ == '__main__':
    main()
