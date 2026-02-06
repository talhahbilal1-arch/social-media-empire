"""Email sending functionality using Resend and ConvertKit."""

import logging
from typing import Optional
from dataclasses import dataclass, field
import requests
import resend

from utils.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Brand email configurations
BRAND_EMAIL_CONFIG = {
    "fitnessmadeasy": {
        "from_name": "FitOver35",
        "from_email": "hello@fitover35.com",
        "reply_to": "hello@fitover35.com",
        "footer": "You're receiving this because you signed up for FitOver35 fitness tips. Unsubscribe anytime."
    },
    "daily_deal_darling": {
        "from_name": "Daily Deal Darling",
        "from_email": "hello@dailydealdarling.com",
        "reply_to": "hello@dailydealdarling.com",
        "footer": "You're receiving this because you signed up for Daily Deal Darling updates."
    },
    "menopause_planner": {
        "from_name": "Menopause Planner",
        "from_email": "support@menopauseplanner.com",
        "reply_to": "support@menopauseplanner.com",
        "footer": "You're receiving this because you signed up for menopause wellness tips."
    },
    "nurse_planner": {
        "from_name": "Nurse Planner",
        "from_email": "hello@nurseplanner.com",
        "reply_to": "hello@nurseplanner.com",
        "footer": "You're receiving this because you signed up for nurse life tips."
    },
    "adhd_planner": {
        "from_name": "ADHD Planner",
        "from_email": "support@adhdplanner.com",
        "reply_to": "support@adhdplanner.com",
        "footer": "You're receiving this because you signed up for ADHD productivity tips."
    }
}


@dataclass
class EmailSender:
    """Handles email sending via Resend and ConvertKit integration."""

    resend_api_key: str = ""
    convertkit_api_key: str = ""
    convertkit_api_secret: str = ""

    def __post_init__(self):
        config = get_config()
        if not self.resend_api_key:
            self.resend_api_key = config.resend_api_key
        if not self.convertkit_api_key:
            self.convertkit_api_key = config.convertkit_api_key
        if not self.convertkit_api_secret:
            self.convertkit_api_secret = config.convertkit_api_secret

        if self.resend_api_key:
            resend.api_key = self.resend_api_key

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        brand: str,
        text_content: Optional[str] = None
    ) -> dict:
        """Send a single email via Resend.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML body content
            brand: Brand identifier for sender info
            text_content: Optional plain text version

        Returns:
            Result dict with success status
        """
        brand_config = BRAND_EMAIL_CONFIG.get(
            brand, BRAND_EMAIL_CONFIG["daily_deal_darling"]
        )

        try:
            params = {
                "from": f"{brand_config['from_name']} <{brand_config['from_email']}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "reply_to": brand_config["reply_to"]
            }

            if text_content:
                params["text"] = text_content

            response = resend.Emails.send(params)

            logger.info(f"Email sent to {to_email}: {subject}")
            return {
                "success": True,
                "id": response.get("id"),
                "to": to_email
            }

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def send_bulk_email(
        self,
        recipients: list[str],
        subject: str,
        html_content: str,
        brand: str
    ) -> dict:
        """Send email to multiple recipients.

        Args:
            recipients: List of email addresses
            subject: Email subject
            html_content: HTML body content
            brand: Brand identifier

        Returns:
            Summary of send results
        """
        results = {
            "total": len(recipients),
            "success": 0,
            "failed": 0,
            "errors": []
        }

        for email in recipients:
            result = self.send_email(email, subject, html_content, brand)
            if result.get("success"):
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "email": email,
                    "error": result.get("error")
                })

        return results

    def add_subscriber_to_convertkit(
        self,
        email: str,
        form_id: str,
        first_name: Optional[str] = None,
        tags: Optional[list[str]] = None,
        fields: Optional[dict] = None
    ) -> dict:
        """Add subscriber to ConvertKit form.

        Args:
            email: Subscriber email
            form_id: ConvertKit form ID
            first_name: Optional first name
            tags: Optional list of tag IDs
            fields: Optional custom fields

        Returns:
            Result dict with subscriber info
        """
        if not self.convertkit_api_key:
            return {"success": False, "error": "ConvertKit API key not configured"}

        url = f"https://api.convertkit.com/v3/forms/{form_id}/subscribe"

        data = {
            "api_key": self.convertkit_api_key,
            "email": email
        }

        if first_name:
            data["first_name"] = first_name
        if tags:
            data["tags"] = tags
        if fields:
            data["fields"] = fields

        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()

            result = response.json()
            logger.info(f"Subscriber added to ConvertKit: {email}")

            return {
                "success": True,
                "subscriber_id": result.get("subscription", {}).get("subscriber", {}).get("id"),
                "email": email
            }

        except Exception as e:
            logger.error(f"Failed to add subscriber to ConvertKit: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tag_subscriber(
        self,
        email: str,
        tag_id: str
    ) -> dict:
        """Add a tag to a ConvertKit subscriber.

        Args:
            email: Subscriber email
            tag_id: ConvertKit tag ID

        Returns:
            Result dict
        """
        if not self.convertkit_api_key:
            return {"success": False, "error": "ConvertKit API key not configured"}

        url = f"https://api.convertkit.com/v3/tags/{tag_id}/subscribe"

        data = {
            "api_key": self.convertkit_api_key,
            "email": email
        }

        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()

            logger.info(f"Tag {tag_id} added to subscriber: {email}")
            return {"success": True}

        except Exception as e:
            logger.error(f"Failed to tag subscriber: {e}")
            return {"success": False, "error": str(e)}

    def get_subscriber_info(self, email: str) -> dict:
        """Get subscriber information from ConvertKit.

        Args:
            email: Subscriber email

        Returns:
            Subscriber data dict
        """
        if not self.convertkit_api_secret:
            return {"success": False, "error": "ConvertKit API secret not configured"}

        url = f"https://api.convertkit.com/v3/subscribers"

        params = {
            "api_secret": self.convertkit_api_secret,
            "email_address": email
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            subscribers = data.get("subscribers", [])

            if subscribers:
                return {
                    "success": True,
                    "subscriber": subscribers[0]
                }
            return {
                "success": False,
                "error": "Subscriber not found"
            }

        except Exception as e:
            logger.error(f"Failed to get subscriber info: {e}")
            return {"success": False, "error": str(e)}

    def send_sequence_email(
        self,
        to_email: str,
        sequence_name: str,
        email_number: int,
        brand: str,
        personalization: Optional[dict] = None
    ) -> dict:
        """Send a specific email from a sequence.

        Args:
            to_email: Recipient email
            sequence_name: Name of the email sequence
            email_number: Email number in sequence (1-indexed)
            brand: Brand identifier
            personalization: Optional dict for template variables

        Returns:
            Result dict
        """
        # Load sequence template
        template = self._load_sequence_template(brand, sequence_name, email_number)

        if not template:
            return {
                "success": False,
                "error": f"Template not found: {sequence_name} #{email_number}"
            }

        # Apply personalization
        html_content = template["html"]
        subject = template["subject"]

        if personalization:
            for key, value in personalization.items():
                html_content = html_content.replace(f"{{{{{key}}}}}", str(value))
                subject = subject.replace(f"{{{{{key}}}}}", str(value))

        return self.send_email(to_email, subject, html_content, brand)

    def _load_sequence_template(
        self,
        brand: str,
        sequence_name: str,
        email_number: int
    ) -> Optional[dict]:
        """Load an email template from the sequences directory."""
        # This would typically load from a file or database
        # For now, return a basic template structure
        templates = {
            "welcome": {
                1: {
                    "subject": "Welcome to {brand_name}! 🎉",
                    "html": """
                    <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h1>Welcome, {{first_name}}!</h1>
                        <p>We're so excited to have you here.</p>
                        <p>Check your inbox soon for your free download!</p>
                    </body>
                    </html>
                    """
                }
            }
        }

        sequence = templates.get(sequence_name, {})
        return sequence.get(email_number)

    def is_configured(self) -> dict:
        """Check which email services are configured."""
        return {
            "resend": bool(self.resend_api_key),
            "convertkit": bool(self.convertkit_api_key),
            "convertkit_full": bool(self.convertkit_api_secret)
        }


_email_sender: Optional[EmailSender] = None


def get_email_sender() -> EmailSender:
    """Get or create the global EmailSender instance."""
    global _email_sender
    if _email_sender is None:
        _email_sender = EmailSender()
    return _email_sender
