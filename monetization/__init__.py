"""Monetization module for Social Media Empire."""

from .affiliate_setup import (
    AffiliateManager,
    AffiliateLink,
    AFFILIATE_PROGRAMS,
    BRAND_AFFILIATES,
    generate_affiliate_description,
    DISCLOSURE_TEMPLATES
)

__all__ = [
    "AffiliateManager",
    "AffiliateLink",
    "AFFILIATE_PROGRAMS",
    "BRAND_AFFILIATES",
    "generate_affiliate_description",
    "DISCLOSURE_TEMPLATES"
]
