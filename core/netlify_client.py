"""
Netlify Client - Blog publishing for dailydealdarling.com
"""
import os
import json
import hashlib
import requests
from datetime import datetime
from typing import Dict, Optional


class NetlifyClient:
    """
    Publishes blog articles to Netlify.

    Two publishing methods:
    1. Direct Deploy API - For sites with simple static content
    2. Git-based - Push to repo and trigger Netlify build

    This implementation uses the Deploy API for simplicity.
    You'll need a Netlify Personal Access Token.
    """

    def __init__(self):
        self.api_token = os.environ.get('NETLIFY_API_TOKEN')
        self.site_id = os.environ.get('NETLIFY_SITE_ID')  # From Netlify dashboard
        self.base_url = "https://api.netlify.com/api/v1"

        if not self.api_token:
            raise ValueError("NETLIFY_API_TOKEN environment variable required")

    def _headers(self) -> Dict:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def publish_article(self, article: Dict, brand_config: Dict) -> Dict:
        """
        Publish a blog article to Netlify.

        For sites using a static site generator (Hugo, Jekyll, etc.),
        this creates the markdown file and triggers a deploy.

        For simple HTML sites, this deploys the rendered HTML directly.

        Returns deployment info including the published URL.
        """
        slug = article['slug']
        content_html = article.get('content_html') or self._markdown_to_html(article['content_markdown'])

        # Build the full HTML page
        page_html = self._build_blog_page(
            title=article['title'],
            meta_description=article['meta_description'],
            content=content_html,
            featured_image=article.get('featured_image_url'),
            brand_config=brand_config
        )

        # Calculate file hash for Netlify
        file_content = page_html.encode('utf-8')
        file_hash = hashlib.sha1(file_content).hexdigest()

        # Deploy to Netlify
        try:
            # First, get the current site
            site_response = requests.get(
                f"{self.base_url}/sites/{self.site_id}",
                headers=self._headers()
            )
            site_response.raise_for_status()
            site_data = site_response.json()

            # Create a new deploy
            deploy_data = {
                "files": {
                    f"/blog/{slug}/index.html": file_hash
                }
            }

            deploy_response = requests.post(
                f"{self.base_url}/sites/{self.site_id}/deploys",
                headers=self._headers(),
                json=deploy_data
            )
            deploy_response.raise_for_status()
            deploy = deploy_response.json()
            deploy_id = deploy['id']

            # Upload the file
            upload_response = requests.put(
                f"{self.base_url}/deploys/{deploy_id}/files/blog/{slug}/index.html",
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/octet-stream"
                },
                data=file_content
            )
            upload_response.raise_for_status()

            # Get the published URL
            site_url = site_data.get('ssl_url') or site_data.get('url')
            published_url = f"{site_url}/blog/{slug}/"

            return {
                'success': True,
                'deploy_id': deploy_id,
                'published_url': published_url,
                'published_at': datetime.utcnow().isoformat()
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _build_blog_page(self,
                         title: str,
                         meta_description: str,
                         content: str,
                         featured_image: Optional[str],
                         brand_config: Dict) -> str:
        """Build a complete HTML page for the blog article."""

        # This is a simple template - replace with your actual site template
        template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {brand_config.get('display_name', 'Blog')}</title>
    <meta name="description" content="{meta_description}">

    <!-- Open Graph -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_description}">
    {f'<meta property="og:image" content="{featured_image}">' if featured_image else ''}
    <meta property="og:type" content="article">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{meta_description}">

    <style>
        :root {{
            --primary: #e91e63;
            --text: #333;
            --bg: #fff;
            --accent: #f8f9fa;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.7;
            color: var(--text);
            background: var(--bg);
        }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem; }}
        header {{ text-align: center; margin-bottom: 3rem; }}
        h1 {{ font-size: 2.5rem; margin-bottom: 1rem; color: var(--primary); }}
        .meta {{ color: #666; font-size: 0.9rem; }}
        .featured-image {{ width: 100%; max-height: 400px; object-fit: cover; border-radius: 8px; margin-bottom: 2rem; }}
        article {{ font-size: 1.1rem; }}
        article h2 {{ margin: 2rem 0 1rem; color: var(--primary); }}
        article h3 {{ margin: 1.5rem 0 0.75rem; }}
        article p {{ margin-bottom: 1.25rem; }}
        article ul, article ol {{ margin-bottom: 1.25rem; padding-left: 2rem; }}
        article li {{ margin-bottom: 0.5rem; }}
        article a {{ color: var(--primary); }}
        .product-box {{
            background: var(--accent);
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1.5rem 0;
        }}
        .product-box h4 {{ color: var(--primary); margin-bottom: 0.5rem; }}
        .product-box a.button {{
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            text-decoration: none;
            margin-top: 1rem;
        }}
        .cta-box {{
            background: var(--primary);
            color: white;
            padding: 2rem;
            border-radius: 8px;
            text-align: center;
            margin: 2rem 0;
        }}
        .cta-box a {{ color: white; font-weight: bold; }}
        footer {{ text-align: center; margin-top: 3rem; padding: 2rem; color: #666; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <a href="/">{brand_config.get('display_name', 'Home')}</a>
        </header>

        <article>
            <h1>{title}</h1>
            <p class="meta">Published {datetime.utcnow().strftime('%B %d, %Y')}</p>

            {f'<img src="{featured_image}" alt="{title}" class="featured-image">' if featured_image else ''}

            {content}

            <div class="cta-box">
                <h3>Find Your Perfect Products!</h3>
                <p>Take our quick quiz to get personalized recommendations.</p>
                <a href="{brand_config.get('website_url', '/')}">Take the Quiz</a>
            </div>
        </article>

        <footer>
            <p>&copy; {datetime.utcnow().year} {brand_config.get('display_name', '')}. All rights reserved.</p>
            <p><a href="/privacy">Privacy Policy</a> | <a href="/affiliate-disclosure">Affiliate Disclosure</a></p>
        </footer>
    </div>
</body>
</html>"""

        return template

    def _markdown_to_html(self, markdown: str) -> str:
        """
        Convert markdown to HTML.

        For production, consider using a proper markdown library like markdown2.
        This is a simple conversion for basic formatting.
        """
        import re

        html = markdown

        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold and italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

        # Lists (simple)
        html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # Paragraphs
        paragraphs = html.split('\n\n')
        processed = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<h') and not p.startswith('<li'):
                if '<li>' in p:
                    p = f'<ul>{p}</ul>'
                else:
                    p = f'<p>{p}</p>'
            processed.append(p)
        html = '\n'.join(processed)

        return html
