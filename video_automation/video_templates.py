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

# Brand-specific Creatomate template configurations
BRAND_TEMPLATES = {
    "daily_deal_darling": {
        "template_id": CREATOMATE_TEMPLATE_ID,  # Storytelling Video template
        "colors": {
            "primary": "#E91E63",  # Pink
            "secondary": "#FFC107",  # Gold
            "text": "#FFFFFF",
            "background": "#1A1A1A"
        },
        "fonts": {
            "heading": "Montserrat Bold",
            "body": "Open Sans"
        },
        "logo_url": "https://dailydealdarling.com/logo.png"
    },
    "menopause_planner": {
        "template_id": CREATOMATE_TEMPLATE_ID,
        "colors": {
            "primary": "#9C27B0",  # Purple
            "secondary": "#E1BEE7",  # Light purple
            "text": "#FFFFFF",
            "background": "#2E1A47"
        },
        "fonts": {
            "heading": "Playfair Display Bold",
            "body": "Lato"
        },
        "logo_url": None
    },
    "nurse_planner": {
        "template_id": CREATOMATE_TEMPLATE_ID,
        "colors": {
            "primary": "#00BCD4",  # Teal
            "secondary": "#B2EBF2",  # Light teal
            "text": "#FFFFFF",
            "background": "#004D40"
        },
        "fonts": {
            "heading": "Roboto Bold",
            "body": "Roboto"
        },
        "logo_url": None
    },
    "adhd_planner": {
        "template_id": CREATOMATE_TEMPLATE_ID,
        "colors": {
            "primary": "#FF9800",  # Orange
            "secondary": "#FFE0B2",  # Light orange
            "text": "#212121",
            "background": "#FFF8E1"
        },
        "fonts": {
            "heading": "Nunito Bold",
            "body": "Nunito"
        },
        "logo_url": None
    }
}


# Template types available
TEMPLATE_TYPES = {
    "tips": {
        "description": "3-point tips format with text overlays",
        "duration": 30,
        "segments": ["hook", "tip1", "tip2", "tip3", "cta"]
    },
    "product_showcase": {
        "description": "Product highlight with benefits",
        "duration": 30,
        "segments": ["hook", "product", "benefit1", "benefit2", "cta"]
    },
    "deal_alert": {
        "description": "Time-sensitive deal announcement",
        "duration": 15,
        "segments": ["alert", "deal", "price", "cta"]
    },
    "story": {
        "description": "Personal story/testimonial format",
        "duration": 45,
        "segments": ["hook", "story1", "story2", "lesson", "cta"]
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
        return BRAND_TEMPLATES.get(brand, BRAND_TEMPLATES["daily_deal_darling"])

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
        """Create Creatomate modifications from content.

        Maps content to Creatomate Storytelling Video template elements:
        - Text-1: Hook/opening text
        - Text-2: Body point 1
        - Text-3: Body point 2
        - Text-4: CTA/closing text
        """
        brand_config = self.get_brand_config(brand)
        body_points = content.get("body_points", [])

        # Map content to Creatomate template element names
        modifications = {
            # Text elements (matching Creatomate Storytelling Video template)
            "Text-1": content.get("hook", ""),
            "Text-2": body_points[0] if len(body_points) > 0 else "",
            "Text-3": body_points[1] if len(body_points) > 1 else "",
            "Text-4": content.get("cta", "Follow for more!"),
        }

        # Add background if provided (applies to all background elements)
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
        """Render a video using Creatomate."""
        if not self.creatomate_client:
            raise ValueError("Creatomate client not configured")

        brand_config = self.get_brand_config(brand)
        modifications = self.create_modifications(brand, content, background_url)

        # Start render
        render_result = self.creatomate_client.create_render(
            template_id=brand_config["template_id"],
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
        """Generate a thumbnail image using Creatomate."""
        if not self.creatomate_client:
            raise ValueError("Creatomate client not configured")

        brand_config = self.get_brand_config(brand)

        modifications = {
            "Primary-Color": brand_config["colors"]["primary"],
            "Text-Color": brand_config["colors"]["text"],
            "Hook-Text": hook_text,
        }

        if background_url:
            modifications["Background"] = background_url

        render_result = self.creatomate_client.create_render(
            template_id=f"{brand_config['template_id']}-thumbnail",
            modifications=modifications,
            output_format="jpg"
        )

        return render_result
