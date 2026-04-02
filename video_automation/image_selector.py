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
            # Home / lifestyle (off-brand for fitness)
            "bedroom", "furniture", "decor", "fashion", "beauty", "makeup",
            "skincare", "menopause", "hot flash", "deal", "sale", "discount",
            "coupon", "baby", "wedding", "party", "christmas", "holiday",
            # Female-oriented (fitness brand is men-only)
            "woman", "women", "female", "girl", "feminine", "she", "her",
            "pink", "purse", "handbag", "nail polish", "lipstick",
            # Off-brand environments
            "nightclub", "casino", "bar", "cocktail", "wine",
            "cooking", "baking", "knitting", "sewing", "gardening",
            "office desk", "cubicle", "corporate"
        ],
        "fallback_query": "man fitness workout gym"
    },
    "deals": {
        "name": "Daily Deal Darling",
        "allowed_themes": [
            "amazon finds", "product flat lay", "organized shelf", "home organization",
            "kitchen gadgets", "skincare products", "beauty essentials",
            "bathroom organization", "desk accessories", "gift wrapping",
            "shopping haul", "product review", "clean aesthetic home",
            "modern kitchen", "closet organization", "laundry room",
            "pantry organization", "vanity setup", "cozy bedroom decor",
            "minimalist home"
        ],
        "blocked_terms": [
            # Fitness / workout imagery
            "gym", "weightlifting", "bodybuilding", "crossfit", "dumbbell",
            "barbell", "treadmill", "pushup", "squat", "deadlift", "bench press",
            "muscle", "bicep", "abs", "sixpack", "protein powder", "supplement",
            "pre workout", "creatine", "whey", "fitness", "workout", "exercise",
            "athlete", "marathon", "running shoes", "sports bra", "sweat",
            # Medical / health imagery
            "menopause", "hormone", "hot flash", "medical", "prescription",
            "hospital", "surgery", "doctor", "nurse", "stethoscope", "pill",
            "medication", "injection", "syringe", "x-ray", "blood test",
            # Industrial / construction
            "construction", "industrial", "factory", "warehouse", "building site",
            "hard hat", "concrete", "machinery", "welding", "scaffold",
            # Food service (not home kitchen)
            "chef", "cooking", "baking", "food prep", "restaurant",
            "commercial kitchen", "food truck",
            # Off-brand environments
            "christmas", "tree", "holiday", "snow", "winter",
            "dark moody", "black and white", "abandoned", "grunge",
            "nightclub", "bar", "casino", "tattoo", "motorcycle",
            "hunting", "fishing", "camping", "military", "weapon"
        ],
        "fallback_query": "clean organized home shelf products flat lay bright"
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
            # Fitness / intense exercise
            "gym", "bodybuilding", "heavy weights", "crossfit", "dumbbell",
            "barbell", "bench press", "deadlift", "muscle", "sixpack",
            "protein powder", "pre workout",
            # Youth / lifestyle (off-brand for midlife wellness)
            "fashion", "party", "nightclub", "young woman", "teen",
            "baby", "pregnancy", "college", "sorority", "prom",
            "bikini", "crop top", "miniskirt",
            # Commercial / deals
            "deal", "sale", "discount", "coupon", "unboxing",
            "shopping haul", "amazon",
            # Off-brand environments
            "casino", "bar", "cocktail", "tattoo", "motorcycle",
            "construction", "factory", "warehouse", "military"
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

    # Deals brand enforcement: ensure product/home-oriented imagery
    if brand == "deals":
        product_terms = {"product", "home", "kitchen", "organized", "shelf", "clean", "decor", "gift", "beauty", "skincare"}
        if not any(term in query_lower for term in product_terms):
            logger.info(f"Deals query '{query}' missing product terms. Appending 'product flat lay'.")
            query = f"{query} product flat lay"

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


def get_pexels_portrait_photos(brand, count=3):
    """Fetch portrait headshot photos from Pexels for testimonial sections.

    Args:
        brand: Brand key (fitness/deals/menopause)
        count: Number of unique photos to return

    Returns:
        List of image URL strings (may be shorter than count if API fails)
    """
    queries = {
        "fitness": "man portrait confident headshot",
        "deals": "woman portrait friendly headshot lifestyle",
        "menopause": "middle aged woman portrait warm headshot",
    }
    query = queries.get(brand, "person portrait headshot")

    api_key = os.environ.get('PEXELS_API_KEY', '')
    if not api_key:
        logger.info("No PEXELS_API_KEY — skipping portrait photo fetch")
        return []

    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={
                "query": query,
                "per_page": count * 3,
                "orientation": "portrait",
                "size": "small",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            photos = resp.json().get('photos', [])
            if photos:
                selected = random.sample(photos, min(count, len(photos)))
                urls = [p['src']['medium'] for p in selected]
                logger.info(f"Fetched {len(urls)} portrait photos for brand '{brand}'")
                return urls
            logger.warning(f"No Pexels portrait results for '{query}'")
        else:
            logger.warning(f"Pexels portrait API returned {resp.status_code}")
    except Exception as e:
        logger.warning(f"Pexels portrait fetch failed: {e}")
    return []
