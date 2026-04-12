"""Shared brand slug mapping — single source of truth for Make.com route filters.

Make.com route filters use hyphenated brand names. The Python pipeline uses short
keys internally. Import BRAND_SLUG from here; never hardcode slugs in other files.

Usage:
    from video_automation.brand_slugs import BRAND_SLUG
    slug = BRAND_SLUG['fitness']  # → 'fitness-made-easy'
"""

BRAND_SLUG = {
    'fitness': 'fitness-made-easy',
    'deals': 'daily-deal-darling',
    'menopause': 'menopause-planner',
}
