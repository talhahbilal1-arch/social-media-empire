"""Unique image fetching for Pinterest pins.

Selects Pexels images that haven't been used by the brand recently,
ensuring visual variety across pins.
"""

import requests
import random
import os
import logging

logger = logging.getLogger(__name__)


def get_unique_pexels_image(search_query, brand, supabase_client):
    """Fetch a Pexels image that hasn't been used by this brand recently.

    Args:
        search_query: Detailed search query for Pexels
        brand: Brand key (fitness/deals/menopause)
        supabase_client: Supabase client instance

    Returns:
        Dict with id, url, photographer, alt
    """
    api_key = os.environ.get('PEXELS_API_KEY', '')
    if not api_key:
        raise ValueError("PEXELS_API_KEY not set")

    # Get recently used image IDs for this brand (last 50 pins)
    used_ids = set()
    try:
        recent = supabase_client.table('content_history') \
            .select('pexels_image_id') \
            .eq('brand', brand) \
            .order('created_at', desc=True) \
            .limit(50) \
            .execute()
        used_ids = {str(r['pexels_image_id']) for r in recent.data if r.get('pexels_image_id')}
    except Exception as e:
        logger.warning(f"Could not fetch recent images: {e}")

    # Search Pexels — use portrait orientation for Pinterest
    headers = {"Authorization": api_key}
    params = {
        "query": search_query,
        "per_page": 40,
        "orientation": "portrait",
        "size": "large"
    }

    response = requests.get(
        "https://api.pexels.com/v1/search",
        headers=headers,
        params=params,
        timeout=15
    )

    if response.status_code != 200:
        raise Exception(f"Pexels API error: {response.status_code} - {response.text[:200]}")

    photos = response.json().get('photos', [])

    # Filter out recently used images
    new_photos = [p for p in photos if str(p['id']) not in used_ids]

    if not new_photos:
        # Try broadening the search query
        simplified_query = ' '.join(search_query.split()[:3]) + " lifestyle"
        logger.info(f"All images used for '{search_query}', trying '{simplified_query}'")

        params['query'] = simplified_query
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params=params,
            timeout=15
        )
        if response.status_code == 200:
            new_photos = [
                p for p in response.json().get('photos', [])
                if str(p['id']) not in used_ids
            ]

    if not new_photos:
        # Last resort — use any photo but log a warning
        new_photos = photos
        logger.warning(f"All images exhausted for '{search_query}'. Reusing an older image.")

    if not new_photos:
        raise Exception(f"No Pexels images found for query: {search_query}")

    # Pick randomly from top results for variety
    chosen = random.choice(new_photos[:min(10, len(new_photos))])

    return {
        "id": str(chosen['id']),
        "url": chosen['src']['large2x'],
        "photographer": chosen['photographer'],
        "alt": chosen.get('alt', '')
    }
