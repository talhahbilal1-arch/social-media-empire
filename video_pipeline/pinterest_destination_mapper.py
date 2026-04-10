"""
Pinterest destination URL resolver.

Replaces the previous behaviour (every pin linked to the homepage) with
topic-aware deep-linking plus UTM tracking. Pinterest CTR was measured at
0.09% when all pins landed on the homepage; users click a pin about
"creatine for older men" and land on a generic homepage with no matching
content, so they bounce. Deep-linking to the specific article is the single
highest-leverage change for fit-over-35 affiliate conversions.

Public API:
    resolve_destination(brand, script_data, board_name=None) -> str

Fallback: if no mapping is found (or the brand has no map), returns the
brand's site_url (current behaviour) so this change cannot make pin
posting fail — the worst case is the same homepage link we had before,
still with UTM params for attribution.
"""

from __future__ import annotations

import logging
import re
from typing import Iterable
from urllib.parse import urlencode

from .config import BrandConfig

logger = logging.getLogger(__name__)


# ── Brand topic → article slug maps ────────────────────────────────────────────
#
# Each entry is (keyword_tuple, article_path). The first entry whose ANY
# keyword appears as a substring of the normalised pin topic/title wins.
# Order matters: put more specific keywords before more generic ones
# (e.g. "protein powder" before "protein").

FITOVER35_TOPIC_MAP: list[tuple[tuple[str, ...], str]] = [
    # ── Equipment / home gym ──
    (("adjustable dumbbell", "dumbbells", "dumbbell"),          "articles/best-adjustable-dumbbells-2026"),
    (("home gym", "gym equipment", "gym setup", "garage gym"),  "articles/best-home-gym-equipment-under-500"),
    (("fitness tracker", "smartwatch", "wearable", "fitness watch"), "articles/best-fitness-tracker-weight-training"),
    (("resistance band",),                                       "articles/resistance-bands-for-strength-training-at-home"),

    # ── Supplements ──
    (("best protein powder", "protein powder", "whey protein", "casein"), "articles/best-protein-powder-for-men-over-50"),
    (("protein",),                                               "articles/protein-guide-over-35"),
    (("creatine monohydrate",),                                  "articles/creatine-monohydrate-for-older-men"),
    (("best creatine", "creatine"),                              "articles/best-creatine-for-men-over-40"),
    (("best pre-workout", "best pre workout", "pre-workout", "pre workout", "preworkout"), "articles/best-pre-workout-for-men-over-40"),
    (("testosterone booster", "test booster", "low testosterone", "low t"), "articles/best-testosterone-booster-for-men-over-40"),
    (("testosterone", "boost test", "boost t"),                  "articles/testosterone-boost-naturally"),

    # ── Training topics ──
    (("compound lift", "deadlift", "squat", "bench press", "overhead press", "barbell row"), "articles/compound-lifts-guide"),
    (("progressive overload",),                                  "articles/progressive-overload-for-beginners-over-35"),
    (("limited equipment", "bodyweight", "minimal equipment"),   "articles/build-muscle-after-35-limited-equipment-maximum-gains"),
    (("build muscle", "muscle building", "gain muscle", "mass gain", "muscle"), "articles/build-muscle-after-35-limited-equipment-maximum-gains"),
    (("strength training", "lifting", "strength"),              "articles/strength-training-men-over-35"),

    # ── Fat loss / nutrition ──
    (("belly fat", "lose belly", "visceral fat", "fat loss", "lose weight"), "articles/lose-belly-fat-after-40"),

    # ── Longevity / lifestyle ──
    (("alcohol",),                                               "articles/alcohol-testosterone-what-men-over-35-need-to-know"),
    (("longevity", "lifespan", "live longer"),                   "articles/invest-in-your-longevity"),
    (("metabolic", "metabolism"),                                "articles/muscle-active-metabolic-organ"),
    (("motivation", "consistency", "habit", "never miss"),       "articles/motivational-monday-stay-consistent"),
]

BRAND_TOPIC_MAPS: dict[str, list[tuple[tuple[str, ...], str]]] = {
    "fitover35": FITOVER35_TOPIC_MAP,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace to dashes (UTM-safe)."""
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[\s_]+", "-", text)[:50] or "pin"


def _match_topic(needle_sources: Iterable[str], topic_map: list[tuple[tuple[str, ...], str]]) -> str | None:
    """Return the first article slug whose keywords match any needle, or None."""
    haystack = " ".join(s.lower() for s in needle_sources if s)
    if not haystack:
        return None
    for keywords, slug in topic_map:
        for kw in keywords:
            if kw in haystack:
                return slug
    return None


def _normalise_site(site_url: str) -> str:
    return site_url.rstrip("/")


# ── Public API ────────────────────────────────────────────────────────────────

def resolve_destination(
    brand: BrandConfig,
    script_data: dict,
    board_name: str | None = None,
) -> str:
    """
    Resolve the best destination URL for a Pinterest pin.

    Precedence:
        1. script_data["article_url"] — explicit override from the content pipeline
        2. topic-keyword match against the brand's topic map
        3. brand.site_url — safe fallback (current behaviour)

    UTM parameters are always appended for attribution:
        utm_source=pinterest
        utm_medium=social
        utm_campaign=<board-slug>
        utm_content=<pin-slug>
    """
    site = _normalise_site(brand.site_url)

    # 1. Explicit override from pipeline
    explicit = script_data.get("article_url") or script_data.get("destination_url")
    if explicit:
        base = explicit if explicit.startswith("http") else f"{site}/{explicit.lstrip('/')}"
    else:
        # 2. Topic keyword match
        topic_map = BRAND_TOPIC_MAPS.get(brand.key, [])
        needles = [
            script_data.get("topic", ""),
            script_data.get("title", ""),
            script_data.get("hook", ""),
        ]
        match = _match_topic(needles, topic_map)
        if match:
            base = f"{site}/{match.lstrip('/')}"
        else:
            # 3. Fallback to homepage (same as old behaviour)
            base = site

    # 4. Append UTM params
    campaign = _slugify(board_name or "default")
    content = _slugify(script_data.get("title") or script_data.get("topic") or "pin")
    utm = urlencode({
        "utm_source": "pinterest",
        "utm_medium": "social",
        "utm_campaign": campaign,
        "utm_content": content,
    })
    sep = "&" if "?" in base else "?"
    url = f"{base}{sep}{utm}"

    logger.info(
        "Pin destination resolved: brand=%s topic=%r -> %s",
        brand.key,
        script_data.get("topic") or script_data.get("title") or "<unknown>",
        url,
    )
    return url
