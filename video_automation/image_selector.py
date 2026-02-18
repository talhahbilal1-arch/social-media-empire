"""Unique image fetching for Pinterest pins.

Selects Pexels images that haven't been used by the brand recently,
ensuring visual variety across pins. Includes brand-specific guardrails
to prevent off-brand imagery.
"""

import requests
import random
import os
import logging

logger = logging.getLogger(__name__)


# Brand-specific image validation rules
BRAND_IMAGE_RULES = {
    "fitness": {
        "name": "Fitness Made Easy",
        "allowed_themes": [
            "fitness", "gym", "workout", "exercise", "muscle", "protein",
            "healthy food", "meal prep", "running", "weightlifting", "stretching",
            "yoga", "active lifestyle", "sports nutrition", "home workout",
            "dumbbell", "resistance band", "athletic", "training", "cardio",
            "man", "male", "men", "guy", "masculine", "male athlete"
        ],
        "blocked_terms": [
            "bedroom", "furniture", "decor", "fashion", "beauty", "makeup",
            "skincare", "menopause", "hot flash", "deal", "sale", "discount",
            "coupon", "baby", "wedding", "party", "christmas", "holiday",
            "woman", "women", "female", "girl", "feminine", "she", "her"
        ],
        "fallback_query": "man fitness workout gym"
    },
    "deals": {
        "name": "Daily Deal Darling",
        "allowed_themes": [
            "beauty products", "skincare", "home organization", "kitchen gadgets",
            "self care", "cozy home", "lifestyle products", "women accessories",
            "home decor modern", "bath products", "candles", "planner",
            "desk organization", "gift ideas", "shopping", "unboxing"
        ],
        "blocked_terms": [
            "gym", "weightlifting", "bodybuilding", "menopause", "hormone",
            "hot flash", "supplement", "protein powder", "dumbbell",
            "barbell", "crossfit", "medical", "prescription"
        ],
        "fallback_query": "lifestyle products women aesthetic"
    },
    "menopause": {
        "name": "The Menopause Planner",
        "allowed_themes": [
            "wellness", "self care", "calm", "meditation", "herbal tea",
            "journaling", "planner", "midlife wellness", "women health",
            "relaxation", "sleep", "comfort", "natural remedies",
            "yoga mature women", "peaceful lifestyle", "wellness journal"
        ],
        "blocked_terms": [
            "gym", "bodybuilding", "heavy weights", "fashion", "party",
            "nightclub", "young woman", "teen", "baby", "pregnancy",
            "deal", "sale", "discount", "coupon", "unboxing"
        ],
        "fallback_query": "wellness self care calm lifestyle"
    }
}


def validate_image_query(query, brand):
    """Validate and sanitize image search query for brand relevance.

    Returns sanitized query or fallback if query is off-brand.
    """
    rules = BRAND_IMAGE_RULES.get(brand)
    if not rules:
        return query  # Unknown brand, pass through

    query_lower = query.lower()

    # Check for blocked terms
    for blocked in rules["blocked_terms"]:
        if blocked in query_lower:
            logger.warning(f"Blocked term '{blocked}' found in query '{query}' for brand '{brand}'. Using fallback.")
            return rules["fallback_query"]

    # Check if query has at least one allowed theme word
    has_relevant_term = any(theme in query_lower for theme in rules["allowed_themes"])

    if not has_relevant_term:
        logger.warning(f"Query '{query}' has no relevant terms for brand '{brand}'. Appending brand context.")
        context_word = random.choice(rules["allowed_themes"][:5])
        query = f"{query} {context_word}"

    # Fitness gender enforcement: ensure male-oriented imagery
    if brand == "fitness":
        male_terms = {"man", "male", "men", "guy", "masculine"}
        if not any(term in query_lower for term in male_terms):
            logger.info(f"Fitness query '{query}' missing male terms. Prepending 'man'.")
            query = f"man {query}"

    return query


def get_unique_pexels_image(search_query, brand, supabase_client):
    """Fetch a Pexels image that hasn't been used by this brand recently.

    Args:
        search_query: Detailed search query for Pexels
        brand: Brand key (fitness/deals/menopause)
        supabase_client: Supabase client instance

    Returns:
        Dict with id, url, photographer, alt
    """
    # Validate query against brand guardrails before making API call
    search_query = validate_image_query(search_query, brand)

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
        "url": chosen['src']['original'],
        "photographer": chosen['photographer'],
        "alt": chosen.get('alt', '')
    }
