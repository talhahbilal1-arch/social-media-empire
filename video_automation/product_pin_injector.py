"""Inject product promotion pins into the daily content-engine pipeline.

IMPORTANT: The fitness brand audience is men over 35 who want to GET FIT —
not run a coaching business. All promo pins must be strictly on-brand:
workouts, nutrition, supplements, recovery. No business/marketing content.

Injection is currently DISABLED because no fitness-safe product templates
exist yet. Re-enable by adding templates that pass FITNESS_CONTENT_BLOCKLIST.
"""

import random
from datetime import datetime, timezone

# Terms that must NEVER appear in fitness brand pin content.
# The fitness page is for men who want to get fit — not run a coaching business.
FITNESS_CONTENT_BLOCKLIST = [
    "coaching client",
    "online client",
    "coaching business",
    "client acquisition",
    "sales funnel",
    "lead generation",
    "email list",
    "course launch",
    "monetize",
    "freelance",
    "side hustle",
    "discovery call",
    "objection handling",
    "dm script",
    "sales script",
    "pinterestautomation",
    "digitalmarketing",
    "passiveincome",
    "coachingtools",
    "coachingbusiness",
    "onlinecoach",
    "personaltrainer",
    "fitnesscoach",
]


def is_fitness_safe(text: str) -> bool:
    """Return True if text contains no off-brand coaching/business keywords."""
    lower = text.lower()
    return not any(kw in lower for kw in FITNESS_CONTENT_BLOCKLIST)


# Product pin templates — ALL must pass is_fitness_safe() before being used.
# Add fitness-only promos here (e.g. workout guides, meal plans) when available.
# Current templates: none — promo injection is effectively disabled until
# on-brand products (workout programs, nutrition guides) are ready to promote.
PRODUCT_PIN_TEMPLATES = [
    # Example of a SAFE template (uncomment when product exists):
    # {
    #     "title": "Free 4-Week Home Workout Plan for Men Over 35",
    #     "description": "No gym needed. This 4-week plan is designed for men over 35 — compound movements, joint-friendly progressions, and 3 sessions per week. Download free. #fitover35 #homeworkout #strengthtraining #mensfitness",
    #     "image_query": "man over 40 home workout pushups determined morning",
    #     "destination_url": "https://talhahbilal.gumroad.com/l/dkschg",
    #     "board": "Workouts for Men Over 35",
    # },
]

# Filter to only safe templates (safety net in case someone adds an off-brand one)
SAFE_PRODUCT_PIN_TEMPLATES = [t for t in PRODUCT_PIN_TEMPLATES if is_fitness_safe(
    t.get("title", "") + " " + t.get("description", "")
)]

# Injection probability per content-engine run
INJECTION_PROBABILITY = 0.30


def should_inject_product_pin():
    """Return True only if safe templates exist AND random threshold is met."""
    return bool(SAFE_PRODUCT_PIN_TEMPLATES) and random.random() < INJECTION_PROBABILITY


def get_product_pin():
    """Return a product pin dict compatible with the content-engine pipeline.

    Selects based on the current hour to rotate through templates predictably.
    Raises RuntimeError if no safe templates are available (should not be
    called without checking should_inject_product_pin() first).
    """
    if not SAFE_PRODUCT_PIN_TEMPLATES:
        raise RuntimeError("No fitness-safe product pin templates available")

    hour = datetime.now(timezone.utc).hour
    idx = hour % len(SAFE_PRODUCT_PIN_TEMPLATES)
    template = SAFE_PRODUCT_PIN_TEMPLATES[idx]

    return {
        'brand': 'fitness',
        'title': template['title'],
        'description': template['description'],
        'image_search_query': template['image_query'],
        'graphic_title': template['title'][:60],
        'tips': [],
        'destination_url': template['destination_url'],
        'board': template['board'],
        'visual_style': 'gradient_overlay',
        'topic': 'product_promotion',
        'category': 'product_promotion',
        'angle_framework': 'product_promo',
        'description_opener': '',
        'is_product_pin': True,
    }
