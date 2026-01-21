"""Video template management for Creatomate rendering."""

import json
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path

from utils.config import get_config
from utils.api_clients import CreatomateClient


# Brand-specific Creatomate template configurations
BRAND_TEMPLATES = {
    "daily_deal_darling": {
        "template_id": "deal-darling-vertical",  # Replace with actual Creatomate template ID
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
        "template_id": "menopause-vertical",
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
        "template_id": "nurse-vertical",
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
        "template_id": "adhd-vertical",
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
        """Create Creatomate modifications from content."""
        brand_config = self.get_brand_config(brand)

        modifications = {
            # Colors
            "Primary-Color": brand_config["colors"]["primary"],
            "Secondary-Color": brand_config["colors"]["secondary"],
            "Text-Color": brand_config["colors"]["text"],

            # Hook text
            "Hook-Text": content.get("hook", ""),

            # Body points
            "Body-1": content.get("body_points", [""])[0] if content.get("body_points") else "",
            "Body-2": content.get("body_points", ["", ""])[1] if len(content.get("body_points", [])) > 1 else "",
            "Body-3": content.get("body_points", ["", "", ""])[2] if len(content.get("body_points", [])) > 2 else "",

            # CTA
            "CTA-Text": content.get("cta", "Follow for more!"),

            # Hashtags
            "Hashtags": " ".join(content.get("hashtags", [])),
        }

        # Add background if provided
        if background_url:
            modifications["Background-Video"] = background_url

        # Add logo if available
        if brand_config.get("logo_url"):
            modifications["Logo"] = brand_config["logo_url"]

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
