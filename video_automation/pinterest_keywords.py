"""Pinterest Keyword Research — High-volume search terms mapped to each brand.

This module provides keyword data for pin descriptions, article titles, and board
names to maximize Pinterest SEO. Keywords are grouped by brand and topic cluster.

Used by:
- content_brain.py (pin description generation)
- pin_article_generator.py (article SEO optimization)
- seo_content_machine.py (content calendar planning)

Usage:
    from video_automation.pinterest_keywords import get_keywords, get_description_keywords

    keywords = get_keywords("fitness", "strength")
    desc_keywords = get_description_keywords("fitness")
"""


# ═══════════════════════════════════════════════════════════════
# FITNESS BRAND — fitover35.com
# ═══════════════════════════════════════════════════════════════

FITNESS_KEYWORDS = {
    "strength": {
        "primary": [
            "strength training over 35",
            "build muscle after 35",
            "men's workout plan",
            "compound exercises for men",
            "full body workout routine",
        ],
        "secondary": [
            "deadlift form tips",
            "squat variations",
            "bench press guide",
            "progressive overload",
            "muscle building tips",
            "home gym workout",
            "dumbbell workout plan",
        ],
        "long_tail": [
            "how to build muscle after 35 for men",
            "best strength training program for beginners over 35",
            "3 day full body workout plan for men",
            "compound lifts every man should do",
            "home gym workout routine no equipment",
        ],
    },
    "fat_loss": {
        "primary": [
            "lose belly fat men",
            "fat loss over 35",
            "HIIT workout for men",
            "metabolic training",
            "burn fat build muscle",
        ],
        "secondary": [
            "lose weight after 40",
            "body recomposition",
            "cutting diet plan",
            "intermittent fasting men",
            "cardio vs weights fat loss",
            "calorie deficit diet",
        ],
        "long_tail": [
            "how to lose belly fat after 40 for men",
            "best HIIT workout for fat loss at home",
            "body recomposition diet plan for men over 35",
            "how to lose weight without losing muscle after 35",
        ],
    },
    "nutrition": {
        "primary": [
            "high protein meals",
            "meal prep for men",
            "protein guide",
            "muscle building diet",
            "healthy meal plan",
        ],
        "secondary": [
            "macro counting",
            "best protein powder",
            "protein rich foods",
            "pre workout meal",
            "post workout nutrition",
            "creatine benefits",
            "testosterone foods",
        ],
        "long_tail": [
            "high protein meal prep ideas for the week",
            "best protein powder for men over 35",
            "how much protein do men over 35 need",
            "7 day muscle building meal plan",
            "foods that naturally boost testosterone",
        ],
    },
    "recovery": {
        "primary": [
            "muscle recovery tips",
            "foam rolling routine",
            "stretching for men",
            "mobility exercises",
            "sleep and muscle growth",
        ],
        "secondary": [
            "post workout recovery",
            "joint health supplements",
            "yoga for men",
            "massage gun benefits",
            "ice bath recovery",
        ],
        "long_tail": [
            "best recovery routine after heavy lifting",
            "mobility exercises for men over 35",
            "how to recover faster from workouts",
            "joint friendly exercises for older lifters",
        ],
    },
    "gear": {
        "primary": [
            "best home gym equipment",
            "adjustable dumbbells review",
            "home gym setup",
            "fitness gear for men",
            "best workout equipment",
        ],
        "secondary": [
            "resistance bands workout",
            "power rack home gym",
            "gym shoes for lifting",
            "fitness tracker review",
            "protein shaker bottle",
        ],
        "long_tail": [
            "best home gym equipment under 500 dollars",
            "adjustable dumbbells vs regular dumbbells",
            "complete home gym setup guide for beginners",
            "best fitness gifts for men over 35",
        ],
    },
    "hormones": {
        "primary": [
            "boost testosterone naturally",
            "testosterone after 35",
            "men's hormone health",
            "low testosterone symptoms",
            "natural testosterone boosters",
        ],
        "secondary": [
            "testosterone and sleep",
            "zinc testosterone",
            "vitamin D testosterone",
            "cortisol and muscle loss",
            "hormone optimization",
        ],
        "long_tail": [
            "how to boost testosterone naturally after 35",
            "signs of low testosterone in men over 35",
            "natural ways to increase testosterone without TRT",
            "best supplements for testosterone over 35",
        ],
    },
}

# ═══════════════════════════════════════════════════════════════
# DEALS BRAND — dailydealdarling.com
# ═══════════════════════════════════════════════════════════════

DEALS_KEYWORDS = {
    "skincare": {
        "primary": [
            "best skincare products",
            "skincare routine",
            "affordable skincare",
            "best moisturizer",
            "skincare products 2026",
        ],
        "secondary": [
            "CeraVe review",
            "drugstore skincare",
            "anti aging skincare",
            "vitamin C serum",
            "retinol for beginners",
            "sunscreen recommendations",
        ],
        "long_tail": [
            "best affordable skincare routine for beginners",
            "top rated skincare products on amazon",
            "best drugstore moisturizer for dry skin",
            "skincare products dermatologists recommend",
        ],
    },
    "home": {
        "primary": [
            "home organization ideas",
            "amazon home finds",
            "home decor on a budget",
            "closet organization",
            "kitchen organization",
        ],
        "secondary": [
            "bathroom organization",
            "pantry organization",
            "storage solutions",
            "declutter tips",
            "small space organization",
            "home office setup",
        ],
        "long_tail": [
            "best home organization products on amazon",
            "how to organize a small closet on a budget",
            "kitchen organization ideas that actually work",
            "amazon home finds under 25 dollars",
        ],
    },
    "kitchen": {
        "primary": [
            "best kitchen gadgets",
            "amazon kitchen finds",
            "kitchen organization",
            "best air fryer",
            "cooking gadgets",
        ],
        "secondary": [
            "meal prep containers",
            "cast iron skillet",
            "kitchen tools",
            "coffee maker review",
            "instant pot recipes",
            "blender review",
        ],
        "long_tail": [
            "best kitchen gadgets on amazon 2026",
            "kitchen gadgets that are actually worth it",
            "best air fryer for a family of 4",
            "kitchen organization ideas for small kitchens",
        ],
    },
    "self_care": {
        "primary": [
            "self care products",
            "self care routine",
            "relaxation products",
            "spa at home",
            "wellness products",
        ],
        "secondary": [
            "bath bombs",
            "aromatherapy",
            "massage gun",
            "weighted blanket",
            "meditation tools",
            "essential oils",
        ],
        "long_tail": [
            "best self care products on amazon",
            "at home spa day products",
            "self care gift ideas for women",
            "relaxation products that actually work",
        ],
    },
    "budget": {
        "primary": [
            "amazon finds under 25",
            "budget friendly products",
            "cheap amazon finds",
            "best deals amazon",
            "money saving tips",
        ],
        "secondary": [
            "amazon must haves",
            "tiktok amazon finds",
            "amazon favorites",
            "amazon hidden gems",
            "prime day deals",
        ],
        "long_tail": [
            "best amazon finds under 25 dollars 2026",
            "amazon products that are actually worth it",
            "hidden gem amazon products with great reviews",
            "budget friendly amazon finds for your home",
        ],
    },
}

# ═══════════════════════════════════════════════════════════════
# MENOPAUSE BRAND
# ═══════════════════════════════════════════════════════════════

MENOPAUSE_KEYWORDS = {
    "symptoms": {
        "primary": [
            "menopause symptoms",
            "perimenopause symptoms",
            "hot flashes relief",
            "menopause weight gain",
            "menopause sleep problems",
        ],
        "secondary": [
            "night sweats menopause",
            "brain fog menopause",
            "mood swings menopause",
            "menopause joint pain",
            "menopause fatigue",
        ],
        "long_tail": [
            "how to manage menopause symptoms naturally",
            "best remedies for hot flashes during menopause",
            "perimenopause symptoms every woman should know",
            "menopause weight gain around the middle",
        ],
    },
    "wellness": {
        "primary": [
            "menopause wellness",
            "menopause supplements",
            "menopause diet",
            "menopause exercise",
            "hormone balance naturally",
        ],
        "secondary": [
            "menopause self care",
            "menopause nutrition",
            "menopause yoga",
            "menopause meditation",
            "menopause support",
        ],
        "long_tail": [
            "best supplements for menopause symptoms",
            "menopause diet plan for weight loss",
            "exercise routine for women going through menopause",
            "natural ways to balance hormones during menopause",
        ],
    },
    "lifestyle": {
        "primary": [
            "life after menopause",
            "menopause skincare",
            "menopause fashion",
            "menopause relationships",
            "thriving during menopause",
        ],
        "secondary": [
            "menopause confidence",
            "menopause community",
            "postmenopause health",
            "menopause and aging",
        ],
        "long_tail": [
            "how to thrive during menopause",
            "best skincare routine for menopausal skin",
            "staying confident during menopause",
            "menopause support groups and communities",
        ],
    },
}


# ═══════════════════════════════════════════════════════════════
# KEYWORD LOOKUP API
# ═══════════════════════════════════════════════════════════════

BRAND_KEYWORDS = {
    "fitness": FITNESS_KEYWORDS,
    "deals": DEALS_KEYWORDS,
    "menopause": MENOPAUSE_KEYWORDS,
}


def get_keywords(brand, topic=None):
    """Get keywords for a brand, optionally filtered by topic.

    Args:
        brand: Brand key (fitness, deals, menopause)
        topic: Optional topic cluster key

    Returns:
        dict of keyword lists, or flat list if topic specified
    """
    brand_data = BRAND_KEYWORDS.get(brand, {})

    if topic:
        topic_data = brand_data.get(topic, {})
        # Return all keywords flat
        all_kws = []
        all_kws.extend(topic_data.get("primary", []))
        all_kws.extend(topic_data.get("secondary", []))
        all_kws.extend(topic_data.get("long_tail", []))
        return all_kws

    return brand_data


def get_description_keywords(brand, count=5):
    """Get a mix of high-value keywords for pin descriptions.

    Args:
        brand: Brand key
        count: Number of keywords to return

    Returns:
        list of keyword strings
    """
    brand_data = BRAND_KEYWORDS.get(brand, {})
    all_primary = []

    for topic_data in brand_data.values():
        all_primary.extend(topic_data.get("primary", []))

    # Return a rotating selection
    import random
    random.shuffle(all_primary)
    return all_primary[:count]


def get_all_keywords_flat(brand):
    """Get all keywords for a brand as a single flat list (deduped).

    Args:
        brand: Brand key

    Returns:
        list of unique keyword strings
    """
    brand_data = BRAND_KEYWORDS.get(brand, {})
    all_kws = set()

    for topic_data in brand_data.values():
        for tier in ["primary", "secondary", "long_tail"]:
            all_kws.update(topic_data.get(tier, []))

    return sorted(all_kws)


if __name__ == "__main__":
    # Print keyword summary
    for brand_key, brand_data in BRAND_KEYWORDS.items():
        total = sum(
            len(t.get("primary", [])) + len(t.get("secondary", [])) + len(t.get("long_tail", []))
            for t in brand_data.values()
        )
        topics = list(brand_data.keys())
        print(f"[{brand_key.upper()}] {total} keywords across {len(topics)} topics: {', '.join(topics)}")
