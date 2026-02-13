"""
Blog index updater for FitOver35 and Daily Deal Darling.

Automatically updates the blog listing page (blog.html) when a new article
is published. Adds the new article entry to the TOP of the blog list
(newest first) with proper HTML structure matching each brand's template.

Usage:
    python update_blog_index.py \\
        --brand fitover35 \\
        --article-path articles/my-new-article.html \\
        --title "My New Article Title" \\
        --category "Strength Training" \\
        --excerpt "Brief description of the article content." \\
        --read-time 8 \\
        --image-url "https://images.pexels.com/photos/123/photo.jpeg"
"""

import os
import re
import logging
import argparse
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Brand configurations
BRANDS = {
    "fitover35": {
        "blog_path": "outputs/fitover35-website/blog.html",
        "insert_marker": '<div class="blog-list">',
        "template": "fitover35",
    },
    "dailydealdarling": {
        "blog_path": "dailydealdarling_website/blog.html",
        "insert_marker": '<div class="blog-list">',
        "template": "dailydealdarling",
    },
}


def generate_fitover35_blog_item(
    article_path: str,
    title: str,
    category: str,
    excerpt: str,
    read_time: int,
    image_url: str,
) -> str:
    """Generate a blog-item card matching FitOver35 blog.html structure."""
    alt_text = title.lower()
    return f"""
        <!-- Article: {title} -->
        <article class="blog-item">
          <div class="blog-item__image">
            <img src="{image_url}" alt="{alt_text}" loading="lazy">
          </div>
          <div class="blog-item__content">
            <span class="blog-item__category">{category}</span>
            <h2 class="blog-item__title">
              <a href="{article_path}">{title}</a>
            </h2>
            <p class="blog-item__excerpt">{excerpt}</p>
            <span class="blog-item__meta">{read_time} min read</span>
          </div>
        </article>
"""


def generate_dailydealdarling_blog_item(
    article_path: str,
    title: str,
    category: str,
    excerpt: str,
    read_time: int,
    image_url: str,
) -> str:
    """Generate a blog-item card for Daily Deal Darling blog listing."""
    alt_text = title.lower()
    return f"""
        <!-- Article: {title} -->
        <article class="blog-item">
          <div class="blog-item__image">
            <img src="{image_url}" alt="{alt_text}" loading="lazy">
          </div>
          <div class="blog-item__content">
            <span class="blog-item__category">{category}</span>
            <h2 class="blog-item__title">
              <a href="{article_path}">{title}</a>
            </h2>
            <p class="blog-item__excerpt">{excerpt}</p>
            <span class="blog-item__meta">{read_time} min read</span>
          </div>
        </article>
"""


def check_duplicate(blog_html: str, title: str, article_path: str) -> bool:
    """Check if an article already exists in the blog listing."""
    if title in blog_html:
        return True
    if article_path in blog_html:
        return True
    return False


def update_blog_html(
    blog_path: str,
    article_path: str,
    title: str,
    category: str,
    excerpt: str,
    read_time: int,
    image_url: str,
    brand: str = "fitover35",
) -> bool:
    """
    Update the blog listing page with a new article entry.

    Inserts the new article at the TOP of the blog list (after the
    <div class="blog-list"> opening tag) so newest articles appear first.

    Args:
        blog_path: Path to the blog.html file
        article_path: Relative path to the article (e.g., "articles/my-article.html")
        title: Article title
        category: Display category name
        excerpt: Short description/excerpt
        read_time: Estimated read time in minutes
        image_url: URL for the article thumbnail/hero image
        brand: Brand identifier ("fitover35" or "dailydealdarling")

    Returns:
        True if update was successful, False otherwise
    """
    blog_file = Path(blog_path)

    if not blog_file.exists():
        logger.error(f"Blog file not found: {blog_path}")
        return False

    # Read current content
    content = blog_file.read_text(encoding='utf-8')

    # Check for duplicates
    if check_duplicate(content, title, article_path):
        logger.warning(f"Article already exists in blog listing: {title}")
        return False

    # Generate the new blog item HTML
    if brand == "fitover35":
        new_item = generate_fitover35_blog_item(
            article_path, title, category, excerpt, read_time, image_url
        )
    elif brand == "dailydealdarling":
        new_item = generate_dailydealdarling_blog_item(
            article_path, title, category, excerpt, read_time, image_url
        )
    else:
        logger.error(f"Unknown brand: {brand}")
        return False

    # Find the insertion point: right after <div class="blog-list">
    insert_marker = '<div class="blog-list">'
    marker_pos = content.find(insert_marker)

    if marker_pos == -1:
        logger.error(f"Could not find blog list marker '{insert_marker}' in {blog_path}")
        return False

    # Insert after the marker tag
    insert_pos = marker_pos + len(insert_marker)
    updated_content = content[:insert_pos] + new_item + content[insert_pos:]

    # Write updated content
    blog_file.write_text(updated_content, encoding='utf-8')
    logger.info(f"Updated blog listing: {blog_path}")
    logger.info(f"Added article: {title}")

    return True


def resolve_blog_path(brand: str, base_dir: str = ".") -> str:
    """Resolve the blog.html path for a given brand."""
    brand_config = BRANDS.get(brand)
    if not brand_config:
        raise ValueError(f"Unknown brand: {brand}. Available: {list(BRANDS.keys())}")

    return os.path.join(base_dir, brand_config["blog_path"])


def main():
    parser = argparse.ArgumentParser(
        description='Update blog listing page with new article'
    )
    parser.add_argument(
        '--brand',
        required=True,
        choices=['fitover35', 'dailydealdarling'],
        help='Brand to update'
    )
    parser.add_argument(
        '--article-path',
        required=True,
        help='Relative path to the article HTML file (e.g., articles/my-article.html)'
    )
    parser.add_argument(
        '--title',
        required=True,
        help='Article title'
    )
    parser.add_argument(
        '--category',
        required=True,
        help='Article category display name'
    )
    parser.add_argument(
        '--excerpt',
        required=True,
        help='Article excerpt/description'
    )
    parser.add_argument(
        '--read-time',
        required=True,
        type=int,
        help='Estimated read time in minutes'
    )
    parser.add_argument(
        '--image-url',
        required=True,
        help='URL for the article hero/thumbnail image'
    )
    parser.add_argument(
        '--blog-path',
        help='Override: explicit path to blog.html (instead of auto-resolving from brand)'
    )
    parser.add_argument(
        '--base-dir',
        default='.',
        help='Base directory of the repository'
    )

    args = parser.parse_args()

    # Resolve blog path
    if args.blog_path:
        blog_path = args.blog_path
    else:
        blog_path = resolve_blog_path(args.brand, args.base_dir)

    logger.info(f"Updating blog listing for brand: {args.brand}")
    logger.info(f"Blog path: {blog_path}")
    logger.info(f"New article: {args.title}")

    success = update_blog_html(
        blog_path=blog_path,
        article_path=args.article_path,
        title=args.title,
        category=args.category,
        excerpt=args.excerpt,
        read_time=args.read_time,
        image_url=args.image_url,
        brand=args.brand,
    )

    if success:
        print(f"Successfully updated blog listing with: {args.title}")

        # Output for GitHub Actions
        github_output = os.environ.get('GITHUB_OUTPUT', '')
        if github_output:
            with open(github_output, 'a') as f:
                f.write(f"blog_updated=true\n")
                f.write(f"blog_path={blog_path}\n")

        return 0
    else:
        print(f"Failed to update blog listing")
        return 1


if __name__ == "__main__":
    exit(main())
