"""Email automation system with ConvertKit integration."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from dataclasses import dataclass, field

from utils.config import get_config
from database.supabase_client import get_supabase_client
from .sequences.welcome_sequences import EMAIL_SEQUENCES, get_sequence, get_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConvertKitAutomation:
    """Manages ConvertKit email automation."""

    api_key: str = field(default=None)
    api_secret: str = field(default=None)

    def __post_init__(self):
        config = get_config()
        if self.api_key is None:
            self.api_key = config.convertkit_api_key
        if self.api_secret is None:
            self.api_secret = config.convertkit_api_secret

    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make API request to ConvertKit."""
        import requests

        base_url = "https://api.convertkit.com/v3"
        url = f"{base_url}/{endpoint}"

        params = {"api_secret": self.api_secret}

        if method == "GET":
            response = requests.get(url, params=params, timeout=30)
        elif method == "POST":
            response = requests.post(url, params=params, json=data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, params=params, json=data, timeout=30)
        else:
            raise ValueError(f"Unknown method: {method}")

        response.raise_for_status()
        return response.json()

    def get_forms(self) -> list[dict]:
        """Get all ConvertKit forms."""
        result = self._make_request("GET", "forms")
        return result.get("forms", [])

    def get_sequences(self) -> list[dict]:
        """Get all ConvertKit sequences."""
        result = self._make_request("GET", "sequences")
        return result.get("courses", [])

    def create_sequence(self, name: str) -> dict:
        """Create a new sequence in ConvertKit."""
        data = {"name": name}
        return self._make_request("POST", "courses", data)

    def add_subscriber_to_sequence(self, sequence_id: str, email: str, first_name: str = "") -> dict:
        """Add a subscriber to a sequence."""
        data = {
            "email": email,
            "first_name": first_name
        }
        return self._make_request("POST", f"sequences/{sequence_id}/subscribe", data)

    def create_tag(self, name: str) -> dict:
        """Create a tag in ConvertKit."""
        data = {"tag": {"name": name}}
        return self._make_request("POST", "tags", data)

    def tag_subscriber(self, tag_id: str, email: str) -> dict:
        """Add a tag to a subscriber."""
        data = {"email": email}
        return self._make_request("POST", f"tags/{tag_id}/subscribe", data)

    def get_subscriber(self, email: str) -> Optional[dict]:
        """Get subscriber by email."""
        try:
            result = self._make_request("GET", f"subscribers?email_address={email}")
            subscribers = result.get("subscribers", [])
            return subscribers[0] if subscribers else None
        except Exception:
            return None

    def setup_brand_automation(self, brand: str) -> dict:
        """Set up ConvertKit automation for a brand."""
        sequence_config = get_sequence(brand)

        # Create main sequence
        sequence_name = f"{sequence_config['name']} - Welcome Sequence"

        results = {
            "brand": brand,
            "sequence_name": sequence_name,
            "forms_created": [],
            "tags_created": [],
            "sequences_created": []
        }

        try:
            # Create main welcome sequence
            seq_result = self.create_sequence(sequence_name)
            results["sequences_created"].append(seq_result)

            # Create brand tag
            tag_result = self.create_tag(f"brand:{brand}")
            results["tags_created"].append(tag_result)

            # Create lead magnet tag
            lead_magnet_tag = self.create_tag(f"lead_magnet:{sequence_config['lead_magnet']}")
            results["tags_created"].append(lead_magnet_tag)

            logger.info(f"Set up ConvertKit automation for {brand}")

        except Exception as e:
            logger.error(f"Error setting up ConvertKit for {brand}: {e}")
            results["error"] = str(e)

        return results


@dataclass
class EmailAutomationManager:
    """Manages email automation across all brands."""

    convertkit: ConvertKitAutomation = field(default=None)

    def __post_init__(self):
        if self.convertkit is None:
            self.convertkit = ConvertKitAutomation()

    def setup_all_brands(self) -> list[dict]:
        """Set up email automation for all brands."""
        results = []

        for brand in EMAIL_SEQUENCES.keys():
            result = self.convertkit.setup_brand_automation(brand)
            results.append(result)

        return results

    def process_new_subscriber(self, email: str, brand: str, lead_magnet_id: str, first_name: str = "") -> dict:
        """Process a new subscriber and add to appropriate sequence."""
        db = get_supabase_client()

        # Log subscriber
        subscriber_data = {
            "email": email,
            "first_name": first_name,
            "brand": brand,
            "lead_magnet": lead_magnet_id,
            "subscribed_at": datetime.now(timezone.utc).isoformat()
        }

        # Add to ConvertKit sequence
        sequence_config = get_sequence(brand)

        # Get existing sequences
        sequences = self.convertkit.get_sequences()
        sequence_name = f"{sequence_config['name']} - Welcome Sequence"

        matching_sequence = None
        for seq in sequences:
            if seq.get("name") == sequence_name:
                matching_sequence = seq
                break

        result = {"success": False, "subscriber": subscriber_data}

        if matching_sequence:
            try:
                self.convertkit.add_subscriber_to_sequence(
                    sequence_id=matching_sequence["id"],
                    email=email,
                    first_name=first_name
                )
                result["success"] = True
                result["sequence_id"] = matching_sequence["id"]
            except Exception as e:
                result["error"] = str(e)

        # Log to database
        try:
            db.log_analytics_event(
                event_type="email_subscriber",
                brand=brand,
                platform="email",
                data=subscriber_data
            )
        except Exception as e:
            logger.warning(f"Failed to log subscriber to database: {e}")

        return result

    def get_email_content(self, brand: str, day: int) -> Optional[dict]:
        """Get email content for a specific day in the sequence."""
        return get_email(brand, day)

    def preview_all_sequences(self) -> dict:
        """Preview all email sequences."""
        preview = {}

        for brand, config in EMAIL_SEQUENCES.items():
            preview[brand] = {
                "name": config["name"],
                "from": f"{config['from_name']} <{config['from_email']}>",
                "lead_magnet": config["lead_magnet"],
                "emails": [
                    {
                        "day": email["day"],
                        "subject": email["subject"],
                        "preview": email["preview"]
                    }
                    for email in config["sequence"]
                ]
            }

        return preview


# Form configurations for embedding
FORM_CONFIGS = {
    "daily_deal_darling": {
        "popup": {
            "title": "Want the BEST Deals?",
            "subtitle": "Get my FREE Deal Tracker + daily deal alerts!",
            "button_text": "Send Me Deals!",
            "placeholder": "Enter your email"
        },
        "inline": {
            "title": "Never Miss a Deal Again",
            "subtitle": "Download the FREE Ultimate Deal Tracker",
            "button_text": "Get Free Access",
            "placeholder": "Your best email"
        }
    },
    "menopause_planner": {
        "popup": {
            "title": "Free Symptom Tracker",
            "subtitle": "Track your symptoms & find patterns",
            "button_text": "Send It To Me!",
            "placeholder": "Enter your email"
        },
        "inline": {
            "title": "Start Understanding Your Body",
            "subtitle": "Get the FREE 30-Day Symptom Tracker",
            "button_text": "Download Free",
            "placeholder": "Your email address"
        }
    },
    "nurse_planner": {
        "popup": {
            "title": "Organize Your Shifts",
            "subtitle": "FREE Shift Planner for Nurses",
            "button_text": "Get My Planner!",
            "placeholder": "Enter your email"
        },
        "inline": {
            "title": "Thrive in Your Nursing Career",
            "subtitle": "Download the FREE Ultimate Shift Planner",
            "button_text": "Send It Free",
            "placeholder": "Your nurse email"
        }
    },
    "adhd_planner": {
        "popup": {
            "title": "Clear the Mental Clutter",
            "subtitle": "FREE ADHD Brain Dump Sheets",
            "button_text": "Get My Sheets!",
            "placeholder": "Enter your email"
        },
        "inline": {
            "title": "Get Out of Your Head",
            "subtitle": "Download FREE Brain Dump Worksheets",
            "button_text": "Send Them Free",
            "placeholder": "Your email"
        }
    }
}


def generate_form_html(brand: str, form_type: str = "inline") -> str:
    """Generate HTML for an email capture form."""
    config = FORM_CONFIGS.get(brand, FORM_CONFIGS["daily_deal_darling"])
    form_config = config.get(form_type, config["inline"])

    brand_colors = {
        "daily_deal_darling": {"primary": "#E91E63", "secondary": "#FFC107"},
        "menopause_planner": {"primary": "#9C27B0", "secondary": "#E1BEE7"},
        "nurse_planner": {"primary": "#00BCD4", "secondary": "#B2EBF2"},
        "adhd_planner": {"primary": "#FF9800", "secondary": "#FFE0B2"}
    }
    colors = brand_colors.get(brand, brand_colors["daily_deal_darling"])

    return f'''
<div class="email-form" style="background: {colors["secondary"]}; padding: 30px; border-radius: 10px; text-align: center; max-width: 400px; margin: 20px auto;">
    <h3 style="color: {colors["primary"]}; margin-bottom: 10px;">{form_config["title"]}</h3>
    <p style="color: #333; margin-bottom: 20px;">{form_config["subtitle"]}</p>
    <form action="{{{{convertkit_form_action}}}}" method="post">
        <input type="email" name="email" placeholder="{form_config["placeholder"]}"
               style="width: 100%; padding: 12px; border: 2px solid {colors["primary"]}; border-radius: 5px; margin-bottom: 10px; font-size: 16px;" required>
        <button type="submit"
                style="width: 100%; padding: 12px 24px; background: {colors["primary"]}; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; font-weight: bold;">
            {form_config["button_text"]}
        </button>
    </form>
    <p style="font-size: 12px; color: #666; margin-top: 10px;">We respect your privacy. Unsubscribe anytime.</p>
</div>
'''


if __name__ == "__main__":
    # Preview all sequences
    manager = EmailAutomationManager()
    preview = manager.preview_all_sequences()

    for brand, data in preview.items():
        print(f"\n{'='*60}")
        print(f"Brand: {data['name']}")
        print(f"From: {data['from']}")
        print(f"Lead Magnet: {data['lead_magnet']}")
        print(f"\nEmails:")
        for email in data['emails']:
            print(f"  Day {email['day']}: {email['subject']}")
