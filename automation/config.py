"""
Central configuration for affiliate tags and site paths.
Single source of truth — all automation scripts import from here.
"""

# Amazon Associates affiliate tags
AFFILIATE_TAGS = {
    "fitover35": "fitover3509-20",
    "dailydealdarling": "dailydealdarl-20",
}

# Website root directories (local paths)
SITE_PATHS = {
    "fitover35": r"C:\Users\talha\Desktop\fitover35",
    "dailydealdarling": r"C:\Users\talha\Desktop\social-media-empire\dailydealdarling_website",
}

# Live URLs
SITE_URLS = {
    "fitover35": "https://fitover35.com",
    "dailydealdarling": "https://dailydealdarling.com",
}


def get_tag(site: str) -> str:
    """Return the affiliate tag for a site. Raises KeyError if unknown."""
    return AFFILIATE_TAGS[site]


def validate_tag(tag: str) -> bool:
    """Return True if the tag is one of our known-good tags."""
    return tag in AFFILIATE_TAGS.values()
