"""
Test script to publish existing ready articles to Netlify.
This bypasses day-of-week scheduling to test the API token.
"""
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import SupabaseClient
from core.netlify_client import NetlifyClient


def main():
    print("Testing Netlify publishing...")

    db = SupabaseClient()

    # Get brands
    brands = db.get_active_brands()
    print(f"Found {len(brands)} brands")

    # Try to initialize Netlify
    try:
        netlify = NetlifyClient()
        print("Netlify client initialized successfully")
    except ValueError as e:
        print(f"Netlify not configured: {e}")
        return

    # Get ready articles
    for brand in brands:
        print(f"\nChecking {brand['display_name']}...")
        articles = db.get_pending_blogs(brand['id'], limit=2)
        print(f"  Found {len(articles)} ready articles")

        for article in articles[:1]:  # Just test with 1 per brand
            print(f"  Publishing: {article['title'][:50]}...")

            result = netlify.publish_article(article, brand)

            if result.get('success'):
                print(f"    SUCCESS! URL: {result.get('published_url')}")

                # Update database
                db.update_blog_status(
                    article['id'],
                    'published',
                    published_url=result.get('published_url'),
                    published_at=result.get('published_at')
                )
                print(f"    Database updated")
            else:
                print(f"    FAILED: {result.get('error')}")


if __name__ == '__main__':
    main()
