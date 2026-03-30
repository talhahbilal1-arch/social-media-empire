"""Content Distribution Script — Generate ready-to-post content for Reddit and Twitter/X.

Reads the latest articles from each brand's site directory, then generates
platform-specific content (Reddit posts, Twitter hooks) and saves them to
~/tall-command-center/distribution/ for manual or automated posting.

Usage:
    python distribution/auto_distribute.py
    python distribution/auto_distribute.py --brand fitness
    python distribution/auto_distribute.py --brand deals
"""

import os
import re
import json
import glob
import argparse
from datetime import datetime, timezone
from pathlib import Path


# ═══════════════════════════════════════════════════════════════
# SUBREDDIT MAPPING PER BRAND
# ═══════════════════════════════════════════════════════════════

SUBREDDIT_MAP = {
    "fitness": {
        "subreddits": [
            {"name": "r/fitness", "rules": "No self-promo. Share as advice/discussion.", "flair": "Discussion"},
            {"name": "r/over30", "rules": "Community-focused. Frame as personal experience.", "flair": None},
            {"name": "r/weightlifting", "rules": "Technical focus. Emphasize form and programming.", "flair": None},
            {"name": "r/supplements", "rules": "Evidence-based only. Cite studies when possible.", "flair": None},
            {"name": "r/homegym", "rules": "Product recs OK if genuine. Include personal experience.", "flair": None},
            {"name": "r/fitness30plus", "rules": "Age-specific. Frame around recovery and longevity.", "flair": None},
            {"name": "r/GettingShredded", "rules": "Progress and advice posts. Visual results help.", "flair": None},
            {"name": "r/naturalbodybuilding", "rules": "No gear discussion. Focus on training and diet.", "flair": None},
        ],
        "site_url": "https://fitover35.com",
        "articles_dir": None,  # Set dynamically
        "tone": "Direct, research-backed, no-BS. Speak as a fellow guy over 35 who trains.",
    },
    "deals": {
        "subreddits": [
            {"name": "r/deals", "rules": "Must be actual deals. Include price and discount %.", "flair": "Amazon"},
            {"name": "r/frugal", "rules": "Frame as money-saving tip, not product push.", "flair": None},
            {"name": "r/amazondeals", "rules": "Amazon links OK. Include product details.", "flair": None},
            {"name": "r/homedecorating", "rules": "Visual focus. Share as inspiration with product recs.", "flair": None},
            {"name": "r/BuyItForLife", "rules": "Quality focus. Emphasize durability and long-term value.", "flair": None},
            {"name": "r/AmazonTopRated", "rules": "Product recs with ratings. Include review count.", "flair": None},
            {"name": "r/budgetfood", "rules": "Kitchen gadgets and food deals. Practical focus.", "flair": None},
            {"name": "r/SkincareAddiction", "rules": "Evidence-based skincare only. Routine format preferred.", "flair": None},
        ],
        "site_url": "https://dailydealdarling.com",
        "articles_dir": None,  # Set dynamically
        "tone": "Friendly, helpful, genuine shopper sharing finds. Not salesy.",
    },
    "menopause": {
        "subreddits": [
            {"name": "r/Menopause", "rules": "Supportive community. Share as personal experience or research.", "flair": None},
            {"name": "r/WomensHealth", "rules": "Health-focused. Cite sources when possible.", "flair": None},
            {"name": "r/TwoXChromosomes", "rules": "Supportive, empowering. Frame as shared experience.", "flair": None},
            {"name": "r/AskWomenOver30", "rules": "Discussion format. Ask for experiences.", "flair": None},
        ],
        "site_url": "https://menopause-planner-website.vercel.app",
        "articles_dir": None,  # Set dynamically
        "tone": "Warm, empathetic, supportive. Share as helpful resource, not promotion.",
    },
}


# ═══════════════════════════════════════════════════════════════
# ARTICLE PARSER
# ═══════════════════════════════════════════════════════════════

def extract_article_info(html_path):
    """Extract title, description, and key content from an HTML article file."""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return None

    # Extract title
    title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else Path(html_path).stem.replace("-", " ").title()

    # Extract meta description
    desc_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"', content, re.IGNORECASE)
    description = desc_match.group(1).strip() if desc_match else ""

    # Extract H1
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.IGNORECASE | re.DOTALL)
    h1 = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip() if h1_match else title

    # Extract H2 headings for content structure
    h2_matches = re.findall(r"<h2[^>]*>(.*?)</h2>", content, re.IGNORECASE | re.DOTALL)
    h2_list = [re.sub(r"<[^>]+>", "", h).strip() for h in h2_matches[:6]]

    # Get slug for URL
    slug = Path(html_path).stem

    return {
        "title": title,
        "h1": h1,
        "description": description,
        "headings": h2_list,
        "slug": slug,
        "file_path": str(html_path),
    }


def get_latest_articles(articles_dir, count=5):
    """Get the most recent articles from a directory, sorted by modification time."""
    if not articles_dir or not os.path.isdir(articles_dir):
        return []

    html_files = glob.glob(os.path.join(articles_dir, "*.html"))
    html_files.sort(key=os.path.getmtime, reverse=True)

    articles = []
    for fpath in html_files[:count]:
        info = extract_article_info(fpath)
        if info:
            articles.append(info)

    return articles


# ═══════════════════════════════════════════════════════════════
# CONTENT GENERATORS
# ═══════════════════════════════════════════════════════════════

def generate_reddit_post(article, brand_config, subreddit):
    """Generate a Reddit-style post for a specific subreddit."""
    title = article["h1"]
    description = article["description"]
    headings = article["headings"]
    url = f"{brand_config['site_url']}/articles/{article['slug']}.html"

    # Build body text
    body_parts = []

    if description:
        body_parts.append(description)

    if headings:
        body_parts.append("\n**Key points covered:**")
        for h in headings[:5]:
            body_parts.append(f"- {h}")

    body_parts.append(f"\nFull guide: {url}")
    body_parts.append(f"\n*{brand_config['tone']}*")

    return {
        "platform": "reddit",
        "subreddit": subreddit["name"],
        "title": title,
        "body": "\n".join(body_parts),
        "flair": subreddit.get("flair"),
        "rules_reminder": subreddit["rules"],
        "url": url,
    }


def generate_twitter_post(article, brand_config):
    """Generate a Twitter/X post with hook + link."""
    title = article["h1"]
    url = f"{brand_config['site_url']}/articles/{article['slug']}.html"

    # Generate different hook styles
    hooks = [
        f"{title}\n\n{article['description'][:100]}...\n\n{url}",
        f"New guide: {title}\n\nRead the full breakdown: {url}",
    ]

    # Add heading-based thread if there are enough headings
    if len(article["headings"]) >= 3:
        thread_parts = [f"{title}\n\nA thread:"]
        for i, h in enumerate(article["headings"][:5], 1):
            thread_parts.append(f"{i}. {h}")
        thread_parts.append(f"\nFull guide with details: {url}")
        hooks.append("\n\n".join(thread_parts))

    return {
        "platform": "twitter",
        "posts": hooks,
        "url": url,
    }


# ═══════════════════════════════════════════════════════════════
# OUTPUT WRITER
# ═══════════════════════════════════════════════════════════════

def write_distribution_output(brand_key, reddit_posts, twitter_posts, output_dir):
    """Write distribution content to output files."""
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Reddit output
    reddit_file = os.path.join(output_dir, f"{brand_key}_reddit_{timestamp}.md")
    with open(reddit_file, "w", encoding="utf-8") as f:
        f.write(f"# Reddit Distribution — {brand_key.title()} Brand\n")
        f.write(f"# Generated: {timestamp}\n\n")
        f.write("---\n\n")

        for post in reddit_posts:
            f.write(f"## {post['subreddit']}\n")
            if post["flair"]:
                f.write(f"**Flair:** {post['flair']}\n")
            f.write(f"**Rules:** {post['rules_reminder']}\n\n")
            f.write(f"### Title:\n{post['title']}\n\n")
            f.write(f"### Body:\n{post['body']}\n\n")
            f.write("---\n\n")

    # Twitter output
    twitter_file = os.path.join(output_dir, f"{brand_key}_twitter_{timestamp}.md")
    with open(twitter_file, "w", encoding="utf-8") as f:
        f.write(f"# Twitter/X Distribution — {brand_key.title()} Brand\n")
        f.write(f"# Generated: {timestamp}\n\n")
        f.write("---\n\n")

        for i, post in enumerate(twitter_posts, 1):
            f.write(f"## Article {i}\n")
            f.write(f"**URL:** {post['url']}\n\n")
            for j, tweet in enumerate(post["posts"], 1):
                f.write(f"### Option {j}:\n```\n{tweet}\n```\n\n")
            f.write("---\n\n")

    return reddit_file, twitter_file


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def run_distribution(brand_key=None):
    """Run content distribution for one or all brands."""
    # Resolve paths based on platform
    home = os.path.expanduser("~")
    desktop = os.path.join(home, "Desktop")

    # Set article directories
    SUBREDDIT_MAP["fitness"]["articles_dir"] = os.path.join(desktop, "fitover35", "articles")
    SUBREDDIT_MAP["deals"]["articles_dir"] = os.path.join(desktop, "dailydealdarling.com", "articles")
    # menopause articles are generated in the social-media-empire outputs
    menopause_articles = os.path.join(desktop, "social-media-empire", "outputs", "menopause-planner-site", "articles")
    if os.path.isdir(menopause_articles):
        SUBREDDIT_MAP["menopause"]["articles_dir"] = menopause_articles

    output_dir = os.path.join(home, "tall-command-center", "distribution")
    os.makedirs(output_dir, exist_ok=True)

    brands_to_process = [brand_key] if brand_key else list(SUBREDDIT_MAP.keys())

    summary = []

    for brand in brands_to_process:
        if brand not in SUBREDDIT_MAP:
            print(f"[SKIP] Unknown brand: {brand}")
            continue

        config = SUBREDDIT_MAP[brand]
        articles = get_latest_articles(config["articles_dir"], count=5)

        if not articles:
            print(f"[SKIP] No articles found for {brand}")
            continue

        print(f"[{brand.upper()}] Found {len(articles)} articles")

        reddit_posts = []
        twitter_posts = []

        for article in articles:
            # Generate Reddit posts for each relevant subreddit
            for sub in config["subreddits"][:4]:  # Top 4 subreddits per article
                reddit_posts.append(generate_reddit_post(article, config, sub))

            # Generate Twitter posts
            twitter_posts.append(generate_twitter_post(article, config))

        reddit_file, twitter_file = write_distribution_output(brand, reddit_posts, twitter_posts, output_dir)

        summary.append({
            "brand": brand,
            "articles_processed": len(articles),
            "reddit_posts": len(reddit_posts),
            "twitter_posts": len(twitter_posts),
            "reddit_file": reddit_file,
            "twitter_file": twitter_file,
        })

        print(f"  Reddit: {len(reddit_posts)} posts -> {reddit_file}")
        print(f"  Twitter: {len(twitter_posts)} posts -> {twitter_file}")

    # Write summary JSON
    summary_file = os.path.join(output_dir, "distribution_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "brands": summary,
        }, f, indent=2)

    print(f"\nDistribution summary: {summary_file}")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate distribution content for Reddit and Twitter/X")
    parser.add_argument("--brand", choices=["fitness", "deals", "menopause"], help="Process a single brand")
    args = parser.parse_args()

    run_distribution(brand_key=args.brand)
