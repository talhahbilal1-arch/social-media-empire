"""Video template management for Creatomate rendering."""

import json
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path

from utils.config import get_config
from utils.api_clients import CreatomateClient


# Creatomate Storytelling Video Template (9:16 vertical)
# This template has 4 text compositions with backgrounds
CREATOMATE_TEMPLATE_ID = "1be9bec1-93d3-40b4-811b-e9ba235112fb"

# Brand-specific video styling (applied as modifications to the base template)
BRAND_VIDEO_STYLES = {
    "fitness": {
        "template_id": CREATOMATE_TEMPLATE_ID,
        "colors": {
            "primary": "#1B5E20",      # Dark green - strength/health
            "secondary": "#4CAF50",    # Medium green
            "accent": "#FF6F00",       # Orange - energy/motivation
            "text_primary": "#FFFFFF",  # White text on dark
            "text_secondary": "#E8F5E9", # Light green text
            "background": "#0D1B0E"    # Near-black green
        },
        "fonts": {
            "heading": "Oswald",       # Bold, masculine
            "body": "Open Sans",
            "cta": "Oswald"
        },
        "logo_url": None,
        "watermark_text": "Fitness Made Easy",
        "style_preset": "bold_athletic"
    },
    "fitnessmadeasy": {
        "template_id": CREATOMATE_TEMPLATE_ID,
        "colors": {
            "primary": "#1B5E20",
            "secondary": "#4CAF50",
            "accent": "#FF6F00",
            "text_primary": "#FFFFFF",
            "text_secondary": "#E8F5E9",
            "background": "#0D1B0E"
        },
        "fonts": {
            "heading": "Oswald",
            "body": "Open Sans",
            "cta": "Oswald"
        },
        "logo_url": None,
        "watermark_text": "Fitness Made Easy",
        "style_preset": "bold_athletic"
    },
    "deals": {
        "template_id": CREATOMATE_TEMPLATE_ID,
        "colors": {
            "primary": "#E91E63",      # Pink - existing DDD brand
            "secondary": "#F48FB1",    # Light pink
            "accent": "#FFD700",       # Gold - deals/value
            "text_primary": "#FFFFFF",
            "text_secondary": "#FCE4EC",
            "background": "#1A0A10"    # Dark pink-black
        },
        "fonts": {
            "heading": "Playfair Display",  # Elegant, feminine
            "body": "Lato",
            "cta": "Montserrat"
        },
        "logo_url": None,
        "watermark_text": "Daily Deal Darling",
        "style_preset": "elegant_feminine"
    },
    "daily_deal_darling": {
        "template_id": CREATOMATE_TEMPLATE_ID,
        "colors": {
            "primary": "#E91E63",
            "secondary": "#F48FB1",
            "accent": "#FFD700",
            "text_primary": "#FFFFFF",
            "text_secondary": "#FCE4EC",
            "background": "#1A0A10"
        },
        "fonts": {
            "heading": "Playfair Display",
            "body": "Lato",
            "cta": "Montserrat"
        },
        "logo_url": None,
        "watermark_text": "Daily Deal Darling",
        "style_preset": "elegant_feminine"
    },
    "menopause": {
        "template_id": CREATOMATE_TEMPLATE_ID,
        "colors": {
            "primary": "#6A1B9A",      # Purple - wisdom/calm
            "secondary": "#CE93D8",    # Light purple
            "accent": "#00897B",       # Teal - health/wellness
            "text_primary": "#FFFFFF",
            "text_secondary": "#F3E5F5",
            "background": "#12061A"    # Dark purple-black
        },
        "fonts": {
            "heading": "Merriweather",  # Warm, trustworthy
            "body": "Source Sans Pro",
            "cta": "Merriweather"
        },
        "logo_url": None,
        "watermark_text": "The Menopause Planner",
        "style_preset": "warm_wellness"
    },
    "menopause_planner": {
        "template_id": CREATOMATE_TEMPLATE_ID,
        "colors": {
            "primary": "#6A1B9A",
            "secondary": "#CE93D8",
            "accent": "#00897B",
            "text_primary": "#FFFFFF",
            "text_secondary": "#F3E5F5",
            "background": "#12061A"
        },
        "fonts": {
            "heading": "Merriweather",
            "body": "Source Sans Pro",
            "cta": "Merriweather"
        },
        "logo_url": None,
        "watermark_text": "The Menopause Planner",
        "style_preset": "warm_wellness"
    },
    "nurse_planner": {
        "template_id": CREATOMATE_TEMPLATE_ID,
        "colors": {
            "primary": "#00BCD4",      # Teal
            "secondary": "#B2EBF2",    # Light teal
            "accent": "#FF7043",       # Warm coral
            "text_primary": "#FFFFFF",
            "text_secondary": "#E0F7FA",
            "background": "#004D40"    # Dark teal
        },
        "fonts": {
            "heading": "Roboto",
            "body": "Roboto",
            "cta": "Roboto"
        },
        "logo_url": None,
        "watermark_text": "Nurse Planner",
        "style_preset": "clean_professional"
    },
    "adhd_planner": {
        "template_id": CREATOMATE_TEMPLATE_ID,
        "colors": {
            "primary": "#FF9800",      # Orange
            "secondary": "#FFE0B2",    # Light orange
            "accent": "#7C4DFF",       # Purple accent
            "text_primary": "#212121",
            "text_secondary": "#FFF8E1",
            "background": "#FFF8E1"    # Light warm background
        },
        "fonts": {
            "heading": "Nunito",
            "body": "Nunito",
            "cta": "Nunito"
        },
        "logo_url": None,
        "watermark_text": "ADHD Planner",
        "style_preset": "warm_energetic"
    }
}

# Keep BRAND_TEMPLATES as alias for backward compatibility
BRAND_TEMPLATES = BRAND_VIDEO_STYLES


# Template types available
TEMPLATE_TYPES = {
    "tips": {
        "description": "3-point tips format with text overlays",
        "duration": 15,
        "segments": ["hook", "tip1", "tip2", "cta"]
    },
    "product_showcase": {
        "description": "Product highlight with benefits",
        "duration": 15,
        "segments": ["hook", "product", "benefit1", "cta"]
    },
    "deal_alert": {
        "description": "Time-sensitive deal announcement",
        "duration": 15,
        "segments": ["alert", "deal", "price", "cta"]
    },
    "story": {
        "description": "Personal story/testimonial format",
        "duration": 15,
        "segments": ["hook", "story1", "lesson", "cta"]
    }
}


@dataclass
class VideoTemplateManager:
    """Manages video templates and Creatomate rendering."""

    creatomate_client: CreatomateClient = field(default=None)
    templates_dir: Path = field(default_factory=lambda: Path(__file__).parent / "templates")

    def __post_init__(self):
        config = get_config()
        if self.creatomate_client is None and config.creatomate_api_key:
            self.creatomate_client = CreatomateClient(api_key=config.creatomate_api_key)

    def get_brand_config(self, brand: str) -> dict:
        """Get template configuration for a brand."""
        return BRAND_VIDEO_STYLES.get(brand, BRAND_VIDEO_STYLES["deals"])

    def load_template(self, template_name: str) -> dict:
        """Load a template configuration from JSON file."""
        template_path = self.templates_dir / f"{template_name}.json"
        if template_path.exists():
            with open(template_path, "r") as f:
                return json.load(f)
        return {}

    def create_modifications(
        self,
        brand: str,
        content: dict,
        background_url: Optional[str] = None
    ) -> dict:
        """Create Creatomate modifications from content with brand-specific styling.

        Maps content to Creatomate Storytelling Video template elements:
        - Text-1: Hook/opening text
        - Text-2: Body point 1
        - Text-3: Body point 2
        - Text-4: CTA/closing text

        Also applies brand-specific colors and fonts as template modifications.
        """
        style = self.get_brand_config(brand)
        body_points = content.get("body_points", [])
        colors = style["colors"]
        fonts = style["fonts"]

        # Map content to Creatomate template element names
        modifications = {
            # Text elements (matching Creatomate Storytelling Video template)
            "Text-1": content.get("hook", ""),
            "Text-2": body_points[0] if len(body_points) > 0 else "",
            "Text-3": body_points[1] if len(body_points) > 1 else "",
            "Text-4": content.get("cta", "Follow for more!"),

            # Brand-specific color modifications
            "Text-1.fill_color": colors["text_primary"],
            "Text-2.fill_color": colors["text_primary"],
            "Text-3.fill_color": colors["text_primary"],
            "Text-4.fill_color": colors["accent"],

            "Text-1.font_family": fonts["heading"],
            "Text-2.font_family": fonts["body"],
            "Text-3.font_family": fonts["body"],
            "Text-4.font_family": fonts["cta"],

            # Background color for all compositions
            "Composition-1.background_color": colors["background"],
            "Composition-2.background_color": colors["background"],
            "Composition-3.background_color": colors["background"],
            "Composition-4.background_color": colors["background"],
        }

        # Add background images if provided
        if background_url:
            modifications["Background-1"] = background_url
            modifications["Background-2"] = background_url
            modifications["Background-3"] = background_url
            modifications["Background-4"] = background_url

        return modifications

    def render_video(
        self,
        brand: str,
        content: dict,
        background_url: Optional[str] = None,
        template_type: str = "tips"
    ) -> dict:
        """Render a video using Creatomate with brand-specific styling."""
        if not self.creatomate_client:
            raise ValueError("Creatomate client not configured")

        style = self.get_brand_config(brand)
        modifications = self.create_modifications(brand, content, background_url)

        # Start render using brand-specific template
        render_result = self.creatomate_client.create_render(
            template_id=style["template_id"],
            modifications=modifications,
            output_format="mp4"
        )

        return render_result

    def render_video_and_wait(
        self,
        brand: str,
        content: dict,
        background_url: Optional[str] = None,
        timeout_seconds: int = 300
    ) -> dict:
        """Render a video and wait for completion."""
        render_result = self.render_video(brand, content, background_url)

        # Handle both single render and array response
        if isinstance(render_result, list):
            render_id = render_result[0].get("id")
        else:
            render_id = render_result.get("id")

        if not render_id:
            raise ValueError("No render ID returned from Creatomate")

        # Wait for completion
        completed = self.creatomate_client.wait_for_render(
            render_id,
            timeout_seconds=timeout_seconds
        )

        return completed

    def get_template_info(self, template_type: str) -> dict:
        """Get information about a template type."""
        return TEMPLATE_TYPES.get(template_type, TEMPLATE_TYPES["tips"])

    def generate_thumbnail(
        self,
        brand: str,
        hook_text: str,
        background_url: Optional[str] = None
    ) -> dict:
        """Generate a thumbnail image using Creatomate with brand styling."""
        if not self.creatomate_client:
            raise ValueError("Creatomate client not configured")

        style = self.get_brand_config(brand)
        colors = style["colors"]

        modifications = {
            "Primary-Color": colors["primary"],
            "Text-Color": colors["text_primary"],
            "Hook-Text": hook_text,
            "Background-Color": colors["background"],
        }

        if background_url:
            modifications["Background"] = background_url

        render_result = self.creatomate_client.create_render(
            template_id=f"{style['template_id']}-thumbnail",
            modifications=modifications,
            output_format="jpg"
        )

        return render_result
