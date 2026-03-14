"""
Brand constants — the single source of truth for all brand names.

Every workflow, script, and agent should import from here instead of
hardcoding brand strings.  The validator (monitoring/validators.py)
also reads from this module so there is exactly ONE place to update.

Usage:
    from core.brands import ACTIVE_BRANDS, get_brand_aliases, is_valid_brand
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BrandConfig:
    """Immutable brand definition."""
    canonical: str          # The name stored in the DB / used as primary key
    display_name: str       # Human-readable label
    aliases: tuple[str, ...] = ()   # Valid shorthand names (accepted everywhere)
    deprecated_aliases: tuple[str, ...] = ()  # Old names the validator should flag
    content_bank_file: Optional[str] = None
    active: bool = True


# ── Registry ────────────────────────────────────────────────
# Add / remove / rename brands HERE and only here.

BRAND_REGISTRY: dict[str, BrandConfig] = {
    "daily_deal_darling": BrandConfig(
        canonical="daily_deal_darling",
        display_name="Daily Deal Darling",
        aliases=("deals",),
        content_bank_file="deal_topics.json",
    ),
    "fitness": BrandConfig(
        canonical="fitness",
        display_name="Fitness Over 35",
        aliases=("fitness-made-easy",),
        deprecated_aliases=("fitover35",),  # Old name — flag if found in code
        content_bank_file="fitness_topics.json",
    ),
    "menopause_planner": BrandConfig(
        canonical="menopause_planner",
        display_name="Menopause Planner",
        aliases=("menopause",),
        content_bank_file="menopause_topics.json",
    ),
    "nurse_planner": BrandConfig(
        canonical="nurse_planner",
        display_name="Nurse Planner",
        active=False,
    ),
    "adhd_planner": BrandConfig(
        canonical="adhd_planner",
        display_name="ADHD Planner",
        active=False,
    ),
}

# ── Derived constants (auto-computed) ───────────────────────

ACTIVE_BRANDS: list[str] = [
    name for name, cfg in BRAND_REGISTRY.items() if cfg.active
]

ALL_BRANDS: list[str] = list(BRAND_REGISTRY.keys())

# alias → canonical mapping  (includes both valid and deprecated aliases)
ALIAS_MAP: dict[str, str] = {}
for _name, _cfg in BRAND_REGISTRY.items():
    for _alias in _cfg.aliases:
        ALIAS_MAP[_alias] = _name
    for _alias in _cfg.deprecated_aliases:
        ALIAS_MAP[_alias] = _name

# Only deprecated aliases — these are what the validator flags as errors
DEPRECATED_ALIAS_MAP: dict[str, str] = {}
for _name, _cfg in BRAND_REGISTRY.items():
    for _alias in _cfg.deprecated_aliases:
        DEPRECATED_ALIAS_MAP[_alias] = _name


# ── Helper functions ────────────────────────────────────────

def resolve_brand(name: str) -> str:
    """Return the canonical brand name for *name* (handles aliases).

    Raises ValueError if *name* is not a known brand or alias.
    """
    if name in BRAND_REGISTRY:
        return name
    if name in ALIAS_MAP:
        return ALIAS_MAP[name]
    raise ValueError(
        f"Unknown brand '{name}'. "
        f"Valid brands: {', '.join(ALL_BRANDS)}. "
        f"Valid aliases: {', '.join(ALIAS_MAP.keys())}."
    )


def is_valid_brand(name: str) -> bool:
    """Check if *name* is a known brand or alias."""
    return name in BRAND_REGISTRY or name in ALIAS_MAP


def get_brand_aliases(canonical: str) -> list[str]:
    """Return all names (canonical + aliases) that map to this brand."""
    cfg = BRAND_REGISTRY.get(canonical)
    if not cfg:
        return []
    return [canonical, *cfg.aliases]
