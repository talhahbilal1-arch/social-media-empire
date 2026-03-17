"""Affiliate marketing integration for all brands."""

import re
from typing import Optional
from dataclasses import dataclass, field

from utils.config import get_config


# Affiliate program configurations
AFFILIATE_PROGRAMS = {
    "amazon": {
        "name": "Amazon Associates",
        "base_url": "https://www.amazon.com",
        "tag_param": "tag",
        "commission_rate": "1-10%",
        "cookie_duration": "24 hours",
        "signup_url": "https://affiliate-program.amazon.com/"
    },
    "shareasale": {
        "name": "ShareASale",
        "base_url": "https://www.shareasale.com",
        "commission_rate": "Varies by merchant",
        "cookie_duration": "Varies",
        "signup_url": "https://www.shareasale.com/info/affiliates/"
    },
    "impact": {
        "name": "Impact",
        "base_url": "https://impact.com",
        "commission_rate": "Varies by brand",
        "cookie_duration": "Varies",
        "signup_url": "https://impact.com/"
    },
    "cj": {
        "name": "CJ Affiliate",
        "base_url": "https://www.cj.com",
        "commission_rate": "Varies by merchant",
        "cookie_duration": "Varies",
        "signup_url": "https://www.cj.com/publisher"
    },
    "rakuten": {
        "name": "Rakuten Advertising",
        "base_url": "https://rakutenadvertising.com",
        "commission_rate": "Varies",
        "cookie_duration": "Varies",
        "signup_url": "https://rakutenadvertising.com/affiliate/"
    }
}

# Brand-specific affiliate configurations
BRAND_AFFILIATES = {
    "daily_deal_darling": {
        "amazon_tag": "dailydealdarl-20",
        "primary_categories": [
            "Home & Kitchen",
            "Beauty & Personal Care",
            "Organization & Storage",
            "Kitchen Gadgets",
            "Cleaning Supplies"
        ],
        "shareasale_merchants": [
            "Target",
            "Wayfair",
            "Bed Bath & Beyond",
            "Kohl's"
        ],
        "recommended_products": [
            {"name": "Organization bins", "asin": "B07DFDS8WB", "commission": "4%"},
            {"name": "Kitchen gadgets", "asin": "B09XQKL8V2", "commission": "4%"},
            {"name": "Cleaning supplies", "asin": "B07GBCRBDP", "commission": "3%"},
        ]
    },
    "menopause_planner": {
        "amazon_tag": "menopauseplan-20",
        "primary_categories": [
            "Health & Wellness",
            "Supplements",
            "Sleep Aids",
            "Cooling Products",
            "Self-Care"
        ],
        "shareasale_merchants": [
            "Vitacost",
            "iHerb",
            "GNC"
        ],
        "recommended_products": [
            {"name": "Cooling pillow", "asin": "B07Q3KLQVW", "commission": "4%"},
            {"name": "Menopause supplements", "asin": "B00FGWLDR6", "commission": "3%"},
            {"name": "Sleep mask", "asin": "B07KC5DWCC", "commission": "4%"},
        ]
    },
    "nurse_planner": {
        "amazon_tag": "nurseplanner-20",
        "primary_categories": [
            "Medical Supplies",
            "Comfortable Shoes",
            "Scrubs & Uniforms",
            "Self-Care",
            "Compression Socks"
        ],
        "shareasale_merchants": [
            "Uniform Advantage",
            "Shoes For Crews",
            "Scrubs & Beyond"
        ],
        "recommended_products": [
            {"name": "Compression socks", "asin": "B01N1UHLMA", "commission": "4%"},
            {"name": "Nurse watch", "asin": "B07D3FGQK9", "commission": "4%"},
            {"name": "Badge reel", "asin": "B07KXQNZ7M", "commission": "4%"},
        ]
    },
    "adhd_planner": {
        "amazon_tag": "adhdplanner-20",
        "primary_categories": [
            "Planners & Organizers",
            "Focus Tools",
            "Fidget Items",
            "Timer Tools",
            "Noise-Canceling Headphones"
        ],
        "shareasale_merchants": [
            "Clever Fox",
            "Erin Condren"
        ],
        "recommended_products": [
            {"name": "Visual timer", "asin": "B07V2FVBGQ", "commission": "4%"},
            {"name": "Fidget cube", "asin": "B01MAYGWNC", "commission": "4%"},
            {"name": "ADHD planner", "asin": "B09NVMYHY8", "commission": "4%"},
        ]
    }
}


@dataclass
class AffiliateLink:
    """Represents an affiliate link."""
    original_url: str
    affiliate_url: str
    product_name: str
    brand: str
    program: str
    expected_commission: str


@dataclass
class AffiliateManager:
    """Manages affiliate links and tracking."""

    def __post_init__(self):
        self.config = get_config()

    def create_amazon_link(self, asin: str, brand: str) -> str:
        """Create an Amazon affiliate link."""
        brand_config = BRAND_AFFILIATES.get(brand, BRAND_AFFILIATES["daily_deal_darling"])
        tag = brand_config["amazon_tag"]
        return f"https://www.amazon.com/dp/{asin}?tag={tag}"

    def create_amazon_search_link(self, query: str, brand: str) -> str:
        """Create an Amazon search affiliate link."""
        brand_config = BRAND_AFFILIATES.get(brand, BRAND_AFFILIATES["daily_deal_darling"])
        tag = brand_config["amazon_tag"]
        encoded_query = query.replace(" ", "+")
        return f"https://www.amazon.com/s?k={encoded_query}&tag={tag}"

    def convert_amazon_link(self, url: str, brand: str) -> str:
        """Convert a regular Amazon link to an affiliate link."""
        brand_config = BRAND_AFFILIATES.get(brand, BRAND_AFFILIATES["daily_deal_darling"])
        tag = brand_config["amazon_tag"]

        # Extract ASIN from URL
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if asin_match:
            asin = asin_match.group(1)
            return f"https://www.amazon.com/dp/{asin}?tag={tag}"

        # If no ASIN found, append tag to existing URL
        if "?" in url:
            return f"{url}&tag={tag}"
        return f"{url}?tag={tag}"

    def get_recommended_products(self, brand: str) -> list[dict]:
        """Get recommended affiliate products for a brand."""
        brand_config = BRAND_AFFILIATES.get(brand, BRAND_AFFILIATES["daily_deal_darling"])
        products = brand_config.get("recommended_products", [])

        return [
            {
                **product,
                "affiliate_url": self.create_amazon_link(product["asin"], brand)
            }
            for product in products
        ]

    def get_link_for_content(self, brand: str, topic: str) -> Optional[str]:
        """Get a relevant affiliate link based on content topic."""
        brand_config = BRAND_AFFILIATES.get(brand, BRAND_AFFILIATES["daily_deal_darling"])

        # Keywords to product mapping
        keyword_products = {
            "organization": "B07DFDS8WB",
            "storage": "B07DFDS8WB",
            "cleaning": "B07GBCRBDP",
            "kitchen": "B09XQKL8V2",
            "sleep": "B07Q3KLQVW",
            "hot flash": "B07Q3KLQVW",
            "cooling": "B07Q3KLQVW",
            "supplement": "B00FGWLDR6",
            "compression": "B01N1UHLMA",
            "scrubs": "B07KXQNZ7M",
            "planner": "B09NVMYHY8",
            "timer": "B07V2FVBGQ",
            "focus": "B07V2FVBGQ",
            "fidget": "B01MAYGWNC",
        }

        topic_lower = topic.lower()
        for keyword, asin in keyword_products.items():
            if keyword in topic_lower:
                return self.create_amazon_link(asin, brand)

        # Default: return search link for topic
        return self.create_amazon_search_link(topic, brand)

    def generate_bio_links(self, brand: str) -> dict:
        """Generate all affiliate links for a brand's bio/linktree."""
        brand_config = BRAND_AFFILIATES.get(brand, BRAND_AFFILIATES["daily_deal_darling"])

        links = {
            "amazon_storefront": f"https://www.amazon.com/shop/{brand_config['amazon_tag']}",
            "recommended_products": self.get_recommended_products(brand),
            "category_links": [
                {
                    "category": cat,
                    "url": self.create_amazon_search_link(cat, brand)
                }
                for cat in brand_config["primary_categories"]
            ]
        }

        return links

    def track_click(self, link_id: str, brand: str, platform: str) -> None:
        """Track affiliate link click (for analytics)."""
        # This would integrate with your analytics/database
        pass


def generate_affiliate_description(brand: str, topic: str, include_link: bool = True) -> str:
    """Generate a video description with affiliate links."""
    manager = AffiliateManager()
    brand_config = BRAND_AFFILIATES.get(brand, BRAND_AFFILIATES["daily_deal_darling"])

    description_parts = []

    if include_link:
        affiliate_link = manager.get_link_for_content(brand, topic)
        description_parts.append(f"Shop my favorite finds: {affiliate_link}")

    # Add disclosure (required by FTC)
    description_parts.append("\n#ad #affiliate")
    description_parts.append("(As an Amazon Associate, I earn from qualifying purchases)")

    return "\n".join(description_parts)


# Disclosure templates for different platforms
DISCLOSURE_TEMPLATES = {
    "youtube": """
DISCLOSURE: Some links in this description are affiliate links. If you purchase through these links, I may earn a small commission at no extra cost to you. Thank you for supporting this channel!
""",
    "instagram": """
#ad #affiliate | As an Amazon Associate I earn from qualifying purchases
""",
    "pinterest": """
This pin contains affiliate links. I may earn a commission if you make a purchase.
""",
    "tiktok": """
#amazonfinds #affiliate
"""
}
