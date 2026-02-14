"""ConvertKit automation and management utilities."""

import logging
from typing import Optional
from dataclasses import dataclass
import requests

from utils.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConvertKitManager:
    """Manages ConvertKit forms, tags, sequences, and subscribers."""

    api_key: str = ""
    api_secret: str = ""
    base_url: str = "https://api.convertkit.com/v3"

    def __post_init__(self):
        config = get_config()
        if not self.api_key:
            self.api_key = config.convertkit_api_key
        if not self.api_secret:
            self.api_secret = config.convertkit_api_secret

    # ==================== Forms ====================

    def list_forms(self) -> list[dict]:
        """Get all forms."""
        response = requests.get(
            f"{self.base_url}/forms",
            params={"api_key": self.api_key}
        )
        response.raise_for_status()
        return response.json().get("forms", [])

    def add_subscriber_to_form(
        self,
        form_id: str,
        email: str,
        first_name: Optional[str] = None,
        fields: Optional[dict] = None,
        tags: Optional[list[int]] = None
    ) -> dict:
        """Add subscriber to a form."""
        data = {
            "api_key": self.api_key,
            "email": email
        }
        if first_name:
            data["first_name"] = first_name
        if fields:
            data["fields"] = fields
        if tags:
            data["tags"] = tags

        response = requests.post(
            f"{self.base_url}/forms/{form_id}/subscribe",
            json=data
        )
        response.raise_for_status()
        return response.json()

    # ==================== Tags ====================

    def list_tags(self) -> list[dict]:
        """Get all tags."""
        response = requests.get(
            f"{self.base_url}/tags",
            params={"api_key": self.api_key}
        )
        response.raise_for_status()
        return response.json().get("tags", [])

    def create_tag(self, name: str) -> dict:
        """Create a new tag."""
        response = requests.post(
            f"{self.base_url}/tags",
            json={
                "api_key": self.api_key,
                "tag": {"name": name}
            }
        )
        response.raise_for_status()
        return response.json()

    def tag_subscriber(self, tag_id: str, email: str) -> dict:
        """Add a tag to a subscriber."""
        response = requests.post(
            f"{self.base_url}/tags/{tag_id}/subscribe",
            json={
                "api_key": self.api_key,
                "email": email
            }
        )
        response.raise_for_status()
        return response.json()

    def remove_tag_from_subscriber(self, tag_id: str, subscriber_id: str) -> bool:
        """Remove a tag from a subscriber."""
        response = requests.delete(
            f"{self.base_url}/subscribers/{subscriber_id}/tags/{tag_id}",
            params={"api_secret": self.api_secret}
        )
        return response.status_code == 204

    # ==================== Subscribers ====================

    def get_subscriber(self, subscriber_id: str) -> dict:
        """Get subscriber by ID."""
        response = requests.get(
            f"{self.base_url}/subscribers/{subscriber_id}",
            params={"api_secret": self.api_secret}
        )
        response.raise_for_status()
        return response.json().get("subscriber", {})

    def find_subscriber_by_email(self, email: str) -> Optional[dict]:
        """Find subscriber by email address."""
        response = requests.get(
            f"{self.base_url}/subscribers",
            params={
                "api_secret": self.api_secret,
                "email_address": email
            }
        )
        response.raise_for_status()
        subscribers = response.json().get("subscribers", [])
        return subscribers[0] if subscribers else None

    def update_subscriber(
        self,
        subscriber_id: str,
        first_name: Optional[str] = None,
        fields: Optional[dict] = None
    ) -> dict:
        """Update subscriber details."""
        data = {"api_secret": self.api_secret}
        if first_name:
            data["first_name"] = first_name
        if fields:
            data["fields"] = fields

        response = requests.put(
            f"{self.base_url}/subscribers/{subscriber_id}",
            json=data
        )
        response.raise_for_status()
        return response.json()

    def unsubscribe(self, email: str) -> dict:
        """Unsubscribe an email address."""
        response = requests.put(
            f"{self.base_url}/unsubscribe",
            json={
                "api_secret": self.api_secret,
                "email": email
            }
        )
        response.raise_for_status()
        return response.json()

    def list_subscribers(
        self,
        page: int = 1,
        sort_field: str = "created_at",
        sort_order: str = "desc"
    ) -> dict:
        """List all subscribers with pagination."""
        response = requests.get(
            f"{self.base_url}/subscribers",
            params={
                "api_secret": self.api_secret,
                "page": page,
                "sort_field": sort_field,
                "sort_order": sort_order
            }
        )
        response.raise_for_status()
        return response.json()

    # ==================== Sequences ====================

    def list_sequences(self) -> list[dict]:
        """Get all sequences."""
        response = requests.get(
            f"{self.base_url}/sequences",
            params={"api_key": self.api_key}
        )
        response.raise_for_status()
        return response.json().get("courses", [])

    def add_subscriber_to_sequence(
        self,
        sequence_id: str,
        email: str,
        first_name: Optional[str] = None,
        fields: Optional[dict] = None
    ) -> dict:
        """Add subscriber to a sequence."""
        data = {
            "api_key": self.api_key,
            "email": email
        }
        if first_name:
            data["first_name"] = first_name
        if fields:
            data["fields"] = fields

        response = requests.post(
            f"{self.base_url}/sequences/{sequence_id}/subscribe",
            json=data
        )
        response.raise_for_status()
        return response.json()

    # ==================== Broadcasts ====================

    def list_broadcasts(self, page: int = 1) -> dict:
        """Get all broadcasts."""
        response = requests.get(
            f"{self.base_url}/broadcasts",
            params={
                "api_secret": self.api_secret,
                "page": page
            }
        )
        response.raise_for_status()
        return response.json()

    def create_broadcast(
        self,
        subject: str,
        content: str,
        description: Optional[str] = None,
        public: bool = True,
        published_at: Optional[str] = None,
        send_at: Optional[str] = None,
        email_layout_template: Optional[str] = None,
        thumbnail_alt: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        preview_text: Optional[str] = None,
    ) -> dict:
        """Create a new broadcast (email to all subscribers).

        Args:
            subject: Email subject line
            content: HTML content of the email
            description: Internal description (not shown to subscribers)
            public: Whether to show on public profile (default True)
            published_at: ISO 8601 date for published date
            send_at: ISO 8601 date to schedule sending
            email_layout_template: ConvertKit email template to use
            thumbnail_alt: Alt text for thumbnail
            thumbnail_url: URL for thumbnail image
            preview_text: Email preview text
        """
        data = {
            "api_secret": self.api_secret,
            "subject": subject,
            "content": content,
        }
        if description:
            data["description"] = description
        if published_at:
            data["published_at"] = published_at
        if send_at:
            data["send_at"] = send_at
        if email_layout_template:
            data["email_layout_template"] = email_layout_template
        if thumbnail_alt:
            data["thumbnail_alt"] = thumbnail_alt
        if thumbnail_url:
            data["thumbnail_url"] = thumbnail_url
        if preview_text:
            data["preview_text"] = preview_text
        data["public"] = public

        response = requests.post(
            f"{self.base_url}/broadcasts",
            json=data
        )
        response.raise_for_status()
        logger.info(f"Created broadcast: {subject}")
        return response.json()

    def get_broadcast_stats(self, broadcast_id: str) -> dict:
        """Get statistics for a broadcast."""
        response = requests.get(
            f"{self.base_url}/broadcasts/{broadcast_id}/stats",
            params={"api_secret": self.api_secret}
        )
        response.raise_for_status()
        return response.json()

    # ==================== Custom Fields ====================

    def list_custom_fields(self) -> list[dict]:
        """Get all custom fields."""
        response = requests.get(
            f"{self.base_url}/custom_fields",
            params={"api_key": self.api_key}
        )
        response.raise_for_status()
        return response.json().get("custom_fields", [])

    def create_custom_field(self, label: str) -> dict:
        """Create a custom field."""
        response = requests.post(
            f"{self.base_url}/custom_fields",
            json={
                "api_secret": self.api_secret,
                "label": label
            }
        )
        response.raise_for_status()
        return response.json()

    # ==================== Utility Methods ====================

    def setup_brand_infrastructure(self, brand: str) -> dict:
        """Set up tags and infrastructure for a brand."""
        tags_to_create = [
            f"brand-{brand}",
            f"{brand}-welcome-started",
            f"{brand}-welcome-completed",
            f"{brand}-newsletter-active",
            f"{brand}-highly-engaged"
        ]

        created_tags = []
        for tag_name in tags_to_create:
            try:
                result = self.create_tag(tag_name)
                created_tags.append(result)
                logger.info(f"Created tag: {tag_name}")
            except Exception as e:
                logger.warning(f"Could not create tag {tag_name}: {e}")

        return {
            "brand": brand,
            "tags_created": len(created_tags),
            "tags": created_tags
        }

    def get_engagement_stats(self) -> dict:
        """Get overall engagement statistics."""
        subscribers = self.list_subscribers()

        total = subscribers.get("total_subscribers", 0)

        # Get tag counts
        tags = self.list_tags()
        tag_counts = {}
        for tag in tags:
            if "engagement" in tag.get("name", "").lower():
                tag_counts[tag["name"]] = tag.get("subscriber_count", 0)

        return {
            "total_subscribers": total,
            "engagement_breakdown": tag_counts
        }

    def sync_subscriber_to_supabase(self, email: str) -> dict:
        """Sync subscriber data to Supabase."""
        from database.supabase_client import get_supabase_client

        subscriber = self.find_subscriber_by_email(email)
        if not subscriber:
            return {"success": False, "error": "Subscriber not found"}

        db = get_supabase_client()

        # Determine brand from tags
        tags = subscriber.get("tags", [])
        brand = "unknown"
        for tag in tags:
            if tag.get("name", "").startswith("brand-"):
                brand = tag["name"].replace("brand-", "")
                break

        result = db.add_subscriber(
            email=email,
            brand=brand,
            source="convertkit_sync"
        )

        return {
            "success": True,
            "subscriber": result
        }


def setup_all_brands():
    """Set up ConvertKit infrastructure for all brands."""
    config = get_config()
    manager = ConvertKitManager()

    results = []
    for brand in config.brands:
        result = manager.setup_brand_infrastructure(brand)
        results.append(result)
        logger.info(f"Set up brand: {brand}")

    return results


if __name__ == "__main__":
    # Run setup when script is executed directly
    results = setup_all_brands()
    for result in results:
        print(f"Brand: {result['brand']} - {result['tags_created']} tags created")
