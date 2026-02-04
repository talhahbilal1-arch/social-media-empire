"""
SEO-optimized blog article generator for Fit Over 35.
Generates articles using Gemini AI and publishes to GitHub Pages.
"""

import os
import json
import random
import re
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
import google.generativeai as genai
import requests


# Article topics organized by category
ARTICLE_TOPICS = {
    "strength_training": [
        "Best Dumbbell Exercises for Men Over 35",
        "How to Build a Bigger Chest After 40",
        "The Complete Guide to Deadlifts for Older Lifters",
        "Shoulder Workout That Won't Wreck Your Joints",
        "Building Bigger Arms After 35: Complete Guide",
        "The Best Back Exercises for Men Over 35",
        "Leg Day Workout for Maximum Muscle Growth",
        "How to Increase Your Bench Press After 40",
        "Core Exercises That Actually Work for Older Men",
        "Full Body Workout for Busy Professionals",
        "The Push Pull Legs Split for Men Over 35",
        "How to Build Muscle With Limited Equipment",
        "Barbell vs Dumbbell: Which Is Better After 35",
        "Progressive Overload for Older Lifters",
        "How to Prevent Injury While Building Muscle"
    ],
    "fat_loss": [
        "How to Lose Belly Fat After 35",
        "The Best Cardio for Fat Loss Without Losing Muscle",
        "HIIT vs Steady State Cardio for Men Over 35",
        "Intermittent Fasting for Men Over 35",
        "How to Get Lean Without Starving Yourself",
        "The Truth About Fat Burners After 40",
        "Metabolic Conditioning Workouts for Fat Loss",
        "How to Break Through a Weight Loss Plateau",
        "Walking for Fat Loss: The Underrated Exercise",
        "Body Recomposition: Build Muscle and Lose Fat"
    ],
    "nutrition": [
        "High Protein Breakfast Ideas for Muscle Building",
        "Best Post-Workout Meals for Recovery",
        "How to Meal Prep for the Week in 2 Hours",
        "The Best Protein Sources for Muscle Growth",
        "Nutrition Mistakes Men Over 35 Make",
        "How Much Water Should You Drink Daily",
        "The Truth About Carbs for Men Over 35",
        "Anti-Inflammatory Foods for Better Recovery",
        "Best Foods to Boost Testosterone Naturally",
        "Supplements Worth Taking After 35"
    ],
    "testosterone": [
        "Natural Ways to Boost Testosterone After 35",
        "Signs of Low Testosterone Every Man Should Know",
        "How Sleep Affects Testosterone Levels",
        "Foods That Kill Testosterone",
        "Exercise Types That Increase Testosterone",
        "Stress Management for Optimal Hormone Levels",
        "The Link Between Body Fat and Testosterone",
        "Vitamin D and Testosterone: The Connection",
        "How Alcohol Affects Your Testosterone",
        "Natural Testosterone vs TRT: What You Need to Know"
    ],
    "recovery": [
        "How to Improve Sleep Quality for Better Gains",
        "The Importance of Rest Days After 35",
        "Foam Rolling Guide for Muscle Recovery",
        "How to Reduce Muscle Soreness Fast",
        "Stretching Routine for Men Over 35",
        "Ice Bath vs Hot Shower for Recovery",
        "How Stress Affects Muscle Growth",
        "The Best Recovery Supplements That Actually Work",
        "Active Recovery Workouts for Rest Days",
        "How to Prevent Overtraining"
    ],
    "lifestyle": [
        "Morning Routine for Maximum Productivity",
        "How to Stay Fit With a Desk Job",
        "Building a Home Gym on a Budget",
        "Fitness Tips for Traveling Professionals",
        "How to Stay Motivated After 35",
        "Balancing Family Life and Fitness Goals",
        "The Mental Benefits of Lifting Weights",
        "How to Build Fitness Habits That Stick",
        "Common Excuses That Hold Men Back",
        "Setting Realistic Fitness Goals After 35"
    ]
}

# SEO keywords for each category
CATEGORY_KEYWORDS = {
    "strength_training": ["strength training", "build muscle", "muscle building", "weightlifting", "resistance training", "men over 35", "over 40 fitness"],
    "fat_loss": ["fat loss", "lose weight", "burn fat", "weight loss for men", "belly fat", "metabolism", "men over 35"],
    "nutrition": ["nutrition", "diet", "protein", "muscle building diet", "healthy eating", "meal prep", "men over 35"],
    "testosterone": ["testosterone", "hormone health", "boost testosterone", "low T", "natural testosterone", "men's health"],
    "recovery": ["recovery", "muscle recovery", "rest", "sleep", "injury prevention", "mobility", "stretching"],
    "lifestyle": ["fitness lifestyle", "healthy habits", "motivation", "work life balance", "home gym", "men over 35"]
}

# Pexels search queries for article images
PEXELS_QUERIES = {
    "strength_training": ["man weightlifting", "man dumbbell workout", "man gym training", "muscular man exercise"],
    "fat_loss": ["man running", "man cardio", "man fitness", "athletic man workout"],
    "nutrition": ["healthy food", "protein meal", "meal prep", "healthy breakfast"],
    "testosterone": ["man lifting weights", "strong man workout", "man exercise"],
    "recovery": ["man stretching", "foam roller", "man resting gym", "man yoga"],
    "lifestyle": ["home gym", "man morning routine", "fit man lifestyle", "man working out home"]
}


@dataclass
class Article:
    """Generated article structure."""
    title: str
    slug: str
    category: str
    meta_description: str
    keywords: list
    content: str
    featured_image: str
    read_time: int
    date: str


class FitOver35ArticleGenerator:
    """Generates SEO-optimized articles for Fit Over 35."""

    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.pexels_api_key = os.environ.get("PEXELS_API_KEY")
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.repo_owner = "talhahbilal1-arch"
        self.repo_name = "fitover35"

        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')

    def get_pexels_image(self, category: str) -> str:
        """Get a relevant image from Pexels."""
        if not self.pexels_api_key:
            return "https://images.pexels.com/photos/1431282/pexels-photo-1431282.jpeg?auto=compress&cs=tinysrgb&w=800"

        queries = PEXELS_QUERIES.get(category, ["man fitness"])
        query = random.choice(queries)

        headers = {"Authorization": self.pexels_api_key}
        params = {"query": query, "per_page": 15, "orientation": "landscape"}

        try:
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers=headers,
                params=params,
                timeout=10
            )
            if response.status_code == 200:
                photos = response.json().get("photos", [])
                if photos:
                    photo = random.choice(photos)
                    return photo["src"]["large"]
        except Exception as e:
            print(f"Pexels error: {e}")

        return "https://images.pexels.com/photos/1431282/pexels-photo-1431282.jpeg?auto=compress&cs=tinysrgb&w=800"

    def generate_article_content(self, topic: str, category: str) -> Optional[Article]:
        """Generate a full SEO-optimized article using Gemini."""

        keywords = CATEGORY_KEYWORDS.get(category, ["fitness", "men over 35"])

        prompt = f"""Write a comprehensive, SEO-optimized blog article for a men's fitness website targeting men over 35.

TOPIC: {topic}
CATEGORY: {category}
TARGET KEYWORDS: {', '.join(keywords)}

REQUIREMENTS:
1. Write 1500-2000 words
2. Use an authoritative but friendly tone
3. Include practical, actionable advice
4. Target men aged 35-55
5. Include scientific backing where relevant
6. Structure with clear H2 and H3 headings
7. Include a compelling introduction that hooks the reader
8. End with a strong call-to-action

FORMAT YOUR RESPONSE AS JSON:
{{
    "title": "SEO-optimized title (60 chars max)",
    "meta_description": "Compelling meta description (155 chars max)",
    "content": "Full article content in HTML format with proper heading tags (h2, h3), paragraphs, lists, and bold text for emphasis",
    "read_time": estimated_minutes_to_read
}}

IMPORTANT:
- Use <h2> for main sections, <h3> for subsections
- Use <p> for paragraphs
- Use <ul><li> for bullet lists
- Use <strong> for emphasis
- Do NOT include the title as an H1 in the content (it will be added separately)
- Make the content engaging and practical
- Include specific numbers, percentages, and examples where possible
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text

            # Clean up the response
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            data = json.loads(text)

            # Generate slug from title
            slug = self._create_slug(data["title"])

            # Get featured image
            featured_image = self.get_pexels_image(category)

            return Article(
                title=data["title"],
                slug=slug,
                category=category,
                meta_description=data["meta_description"],
                keywords=keywords,
                content=data["content"],
                featured_image=featured_image,
                read_time=data.get("read_time", 10),
                date=datetime.now().strftime("%B %d, %Y")
            )

        except Exception as e:
            print(f"Error generating article: {e}")
            return None

    def _create_slug(self, title: str) -> str:
        """Create URL-friendly slug from title."""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        return slug

    def generate_html_page(self, article: Article) -> str:
        """Generate full HTML page for the article."""

        category_display = article.category.replace("_", " ").title()

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- SEO Meta Tags -->
  <title>{article.title} | Fit Over 35</title>
  <meta name="description" content="{article.meta_description}">
  <meta name="keywords" content="{', '.join(article.keywords)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://fitover35.com/articles/{article.slug}.html">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://fitover35.com/articles/{article.slug}.html">
  <meta property="og:title" content="{article.title}">
  <meta property="og:description" content="{article.meta_description}">
  <meta property="og:image" content="{article.featured_image}">

  <!-- Twitter -->
  <meta property="twitter:card" content="summary_large_image">
  <meta property="twitter:title" content="{article.title}">
  <meta property="twitter:description" content="{article.meta_description}">
  <meta property="twitter:image" content="{article.featured_image}">

  <!-- Schema.org Article -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{article.title}",
    "description": "{article.meta_description}",
    "image": "{article.featured_image}",
    "author": {{
      "@type": "Organization",
      "name": "Fit Over 35"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "Fit Over 35",
      "logo": {{
        "@type": "ImageObject",
        "url": "https://fitover35.com/logo.png"
      }}
    }},
    "datePublished": "{datetime.now().strftime('%Y-%m-%d')}",
    "dateModified": "{datetime.now().strftime('%Y-%m-%d')}"
  }}
  </script>

  <!-- Favicon -->
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>💪</text></svg>">

  <!-- Fonts & Styles -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/styles.css">
</head>
<body>
  <!-- Header -->
  <header class="header" id="header">
    <div class="header-inner">
      <a href="/" class="logo">
        <span class="logo-icon">💪</span>
        <span>FIT OVER 35</span>
      </a>
      <nav class="nav">
        <ul class="nav-list">
          <li><a href="/#workouts" class="nav-link">Workouts</a></li>
          <li><a href="/#nutrition" class="nav-link">Nutrition</a></li>
          <li><a href="/#gear" class="nav-link">Gear</a></li>
          <li><a href="/#articles" class="nav-link">Articles</a></li>
        </ul>
      </nav>
      <a href="/#signup" class="header-cta">Get Free Guide</a>
      <button class="mobile-menu-btn" id="mobileMenuBtn" aria-label="Toggle menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>

  <!-- Article Hero -->
  <section class="article-hero">
    <div class="container">
      <div class="article-hero-content">
        <span class="section-badge">{category_display}</span>
        <h1>{article.title}</h1>
        <div class="article-meta-info">
          <span>{article.date}</span>
          <span>{article.read_time} min read</span>
          <span>By Fit Over 35 Team</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Featured Image -->
  <div class="article-featured-image">
    <img src="{article.featured_image}" alt="{article.title}" loading="eager">
  </div>

  <!-- Article Body -->
  <article class="article-body">
    {article.content}

    <!-- Article CTA -->
    <div class="article-cta-box">
      <h3>Ready to Transform Your Fitness?</h3>
      <p>Get our free 12-week workout program designed specifically for men over 35.</p>
      <a href="/#signup" class="btn btn-primary btn-lg">Download Free Program</a>
    </div>
  </article>

  <!-- Related Articles -->
  <section class="related-articles">
    <div class="container">
      <h2 style="text-align: center; margin-bottom: 2rem; color: var(--color-dark);">Related Articles</h2>
      <div class="related-grid">
        <a href="protein-guide-over-35.html" class="related-card">
          <img src="https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?auto=compress&cs=tinysrgb&w=600" alt="Protein Guide" loading="lazy">
          <div class="related-card-content">
            <h4>Complete Protein Guide for Men Over 35</h4>
            <span>10 min read</span>
          </div>
        </a>
        <a href="compound-lifts-guide.html" class="related-card">
          <img src="https://images.pexels.com/photos/1547248/pexels-photo-1547248.jpeg?auto=compress&cs=tinysrgb&w=600" alt="Compound Lifts" loading="lazy">
          <div class="related-card-content">
            <h4>The 5 Compound Lifts Every Man Should Master</h4>
            <span>8 min read</span>
          </div>
        </a>
        <a href="testosterone-boost-naturally.html" class="related-card">
          <img src="https://images.pexels.com/photos/3289711/pexels-photo-3289711.jpeg?auto=compress&cs=tinysrgb&w=600" alt="Testosterone" loading="lazy">
          <div class="related-card-content">
            <h4>10 Ways to Boost Testosterone Naturally</h4>
            <span>12 min read</span>
          </div>
        </a>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a href="/" class="logo">
            <span class="logo-icon">💪</span>
            <span>FIT OVER 35</span>
          </a>
          <p>Science-backed fitness for men who refuse to slow down.</p>
          <div class="footer-social">
            <a href="https://pinterest.com/fitover35" target="_blank" rel="noopener" aria-label="Pinterest">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738.098.119.112.224.083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/></svg>
            </a>
            <a href="https://instagram.com/fitover35" target="_blank" rel="noopener" aria-label="Instagram">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
            </a>
            <a href="https://youtube.com/@fitover35" target="_blank" rel="noopener" aria-label="YouTube">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
            </a>
          </div>
        </div>
        <div class="footer-links">
          <h4>Workouts</h4>
          <ul>
            <li><a href="compound-lifts-guide.html">Strength Training</a></li>
            <li><a href="hiit-for-fat-loss.html">HIIT Workouts</a></li>
            <li><a href="full-body-routine.html">Full Body Routines</a></li>
          </ul>
        </div>
        <div class="footer-links">
          <h4>Nutrition</h4>
          <ul>
            <li><a href="protein-guide-over-35.html">Protein Guide</a></li>
            <li><a href="meal-prep-guide.html">Meal Prep</a></li>
            <li><a href="supplements-guide.html">Supplements</a></li>
          </ul>
        </div>
        <div class="footer-links">
          <h4>Resources</h4>
          <ul>
            <li><a href="../gear.html">Recommended Gear</a></li>
            <li><a href="./">All Articles</a></li>
            <li><a href="/#signup">Free Workout Guide</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 Fit Over 35. All rights reserved.</p>
        <p class="footer-legal">
          <a href="../privacy.html">Privacy</a>
          <a href="../terms.html">Terms</a>
          <a href="../disclaimer.html">Affiliate Disclosure</a>
        </p>
      </div>
    </div>
  </footer>

  <script>
    // Header scroll effect
    const header = document.getElementById('header');
    window.addEventListener('scroll', () => {{
      if (window.pageYOffset > 100) {{
        header.style.boxShadow = '0 4px 20px rgba(0,0,0,0.3)';
      }} else {{
        header.style.boxShadow = 'none';
      }}
    }});

    // Mobile menu
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    mobileMenuBtn?.addEventListener('click', () => {{
      mobileMenuBtn.classList.toggle('active');
    }});
  </script>
</body>
</html>'''

        return html

    def publish_article(self, article: Article) -> bool:
        """Publish article to GitHub repository."""
        if not self.github_token:
            print("No GitHub token available")
            return False

        html_content = self.generate_html_page(article)
        file_path = f"articles/{article.slug}.html"

        # Check if file exists
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"

        try:
            # Check if file exists
            response = requests.get(url, headers=headers, timeout=10)
            sha = None
            if response.status_code == 200:
                sha = response.json().get("sha")

            # Create/Update file
            import base64
            content_b64 = base64.b64encode(html_content.encode()).decode()

            data = {
                "message": f"Add article: {article.title}",
                "content": content_b64,
                "branch": "main"
            }
            if sha:
                data["sha"] = sha

            response = requests.put(url, headers=headers, json=data, timeout=30)

            if response.status_code in [200, 201]:
                print(f"Published: {article.title}")
                return True
            else:
                print(f"Failed to publish: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error publishing article: {e}")
            return False

    def update_sitemap(self, new_articles: list[Article]) -> bool:
        """Update sitemap with new articles."""
        if not self.github_token:
            return False

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Get current sitemap
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/sitemap.xml"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return False

            import base64
            current_content = base64.b64decode(response.json()["content"]).decode()
            sha = response.json()["sha"]

            # Add new URLs before closing tag
            new_urls = ""
            for article in new_articles:
                new_urls += f'''  <url>
    <loc>https://fitover35.com/articles/{article.slug}.html</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
'''

            # Insert before </urlset>
            updated_content = current_content.replace("</urlset>", new_urls + "</urlset>")

            # Update file
            content_b64 = base64.b64encode(updated_content.encode()).decode()
            data = {
                "message": "Update sitemap with new articles",
                "content": content_b64,
                "sha": sha,
                "branch": "main"
            }

            response = requests.put(url, headers=headers, json=data, timeout=30)
            return response.status_code in [200, 201]

        except Exception as e:
            print(f"Error updating sitemap: {e}")
            return False

    def run_weekly_generation(self, num_articles: int = 5):
        """Generate and publish weekly articles."""
        print(f"Generating {num_articles} articles...")

        # Select random topics from different categories
        all_topics = []
        for category, topics in ARTICLE_TOPICS.items():
            for topic in topics:
                all_topics.append((topic, category))

        random.shuffle(all_topics)
        selected = all_topics[:num_articles]

        published_articles = []

        for topic, category in selected:
            print(f"\nGenerating: {topic}")
            article = self.generate_article_content(topic, category)

            if article:
                if self.publish_article(article):
                    published_articles.append(article)
                    print(f"  ✓ Published successfully")
                else:
                    print(f"  ✗ Failed to publish")
            else:
                print(f"  ✗ Failed to generate")

        # Update sitemap
        if published_articles:
            if self.update_sitemap(published_articles):
                print(f"\n✓ Sitemap updated with {len(published_articles)} new articles")
            else:
                print("\n✗ Failed to update sitemap")

        print(f"\nCompleted: {len(published_articles)}/{num_articles} articles published")
        return published_articles


if __name__ == "__main__":
    generator = FitOver35ArticleGenerator()
    generator.run_weekly_generation(5)
