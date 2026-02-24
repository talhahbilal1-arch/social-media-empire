"""ConvertKit automation and management utilities."""

import logging
from typing import Optional
from dataclasses import dataclass
import requests

from utils.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== Interest & Engagement Tags ====================

INTEREST_TAGS = {
    'fitness': {
        'interest_workouts': 'Clicked workout content',
        'interest_nutrition': 'Clicked nutrition content',
        'interest_supplements': 'Clicked supplement content',
        'interest_recovery': 'Clicked recovery content',
        'interest_equipment': 'Clicked equipment content',
    },
    'deals': {
        'interest_beauty': 'Clicked beauty products',
        'interest_kitchen': 'Clicked kitchen products',
        'interest_home': 'Clicked home organization',
        'interest_selfcare': 'Clicked self care products',
    },
    'menopause': {
        'interest_symptoms': 'Clicked symptom relief content',
        'interest_nutrition': 'Clicked nutrition content',
        'interest_sleep': 'Clicked sleep content',
        'interest_wellness': 'Clicked wellness content',
    }
}

ENGAGEMENT_TAGS = {
    'highly_engaged': 'Opens 80%+ of emails',
    'moderate_engaged': 'Opens 40-80% of emails',
    'at_risk': 'Opens less than 20% of emails',
    'purchaser': 'Clicked affiliate link and likely purchased',
}

# Brand-to-interest-group mapping
BRAND_INTEREST_MAP = {
    'fitover35': 'fitness',
    'daily_deal_darling': 'deals',
    'menopause_planner': 'menopause',
}


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

    def list_forms(self) -> list:
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
        tags: Optional[list] = None
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

    def list_tags(self) -> list:
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

    def list_sequences(self) -> list:
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

    def get_broadcast_stats(self, broadcast_id: str) -> dict:
        """Get statistics for a broadcast."""
        response = requests.get(
            f"{self.base_url}/broadcasts/{broadcast_id}/stats",
            params={"api_secret": self.api_secret}
        )
        response.raise_for_status()
        return response.json()

    def create_broadcast(
        self,
        subject: str,
        content: str,
        description: str = "",
        preview_text: str = "",
        public: bool = True,
    ) -> dict:
        """Create and send a broadcast email.

        Args:
            subject: Email subject line.
            content: HTML content of the email.
            description: Internal description for the broadcast.
            preview_text: Preview text shown in inbox.
            public: Whether the broadcast is publicly visible.

        Returns:
            ConvertKit broadcast response with broadcast ID.
        """
        data = {
            "api_secret": self.api_secret,
            "subject": subject,
            "content": content,
            "public": public,
        }
        if description:
            data["description"] = description
        if preview_text:
            data["email_layout_template"] = preview_text

        response = requests.post(
            f"{self.base_url}/broadcasts",
            json=data
        )
        response.raise_for_status()
        return response.json()

    # ==================== Custom Fields ====================

    def list_custom_fields(self) -> list:
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

    # ==================== Interest Tagging ====================

    def ensure_tags_exist(self) -> dict:
        """Create all interest and engagement tags if they don't already exist.

        Checks existing tags in ConvertKit and creates any that are missing
        from INTEREST_TAGS and ENGAGEMENT_TAGS definitions.

        Returns:
            Dict with created tags, existing tags, and any errors.
        """
        existing_tags = self.list_tags()
        existing_tag_names = {tag["name"] for tag in existing_tags}

        results = {
            "created": [],
            "already_exists": [],
            "errors": []
        }

        # Collect all tag names we need to ensure exist
        all_needed_tags = {}

        # Interest tags (per brand group)
        for brand_group, tags in INTEREST_TAGS.items():
            for tag_name, description in tags.items():
                all_needed_tags[tag_name] = description

        # Engagement tags
        for tag_name, description in ENGAGEMENT_TAGS.items():
            all_needed_tags[tag_name] = description

        # Create missing tags
        for tag_name, description in all_needed_tags.items():
            if tag_name in existing_tag_names:
                results["already_exists"].append(tag_name)
                logger.debug(f"Tag already exists: {tag_name}")
            else:
                try:
                    result = self.create_tag(tag_name)
                    results["created"].append({
                        "name": tag_name,
                        "description": description,
                        "id": result.get("id")
                    })
                    logger.info(f"Created tag: {tag_name} ({description})")
                except Exception as e:
                    results["errors"].append({
                        "name": tag_name,
                        "error": str(e)
                    })
                    logger.warning(f"Could not create tag {tag_name}: {e}")

        logger.info(
            f"Tag sync complete: {len(results['created'])} created, "
            f"{len(results['already_exists'])} existing, "
            f"{len(results['errors'])} errors"
        )

        return results

    def tag_subscriber_interest(
        self,
        email: str,
        brand: str,
        interest: str
    ) -> dict:
        """Tag a subscriber with an interest-based tag.

        Looks up the appropriate interest tag for the brand and applies it
        to the subscriber.

        Args:
            email: Subscriber email address.
            brand: Brand identifier (e.g., 'fitover35', 'daily_deal_darling').
            interest: Interest key (e.g., 'interest_workouts', 'interest_beauty').

        Returns:
            Dict with success status and tag details.
        """
        # Determine the interest group for this brand
        interest_group = BRAND_INTEREST_MAP.get(brand)
        if not interest_group:
            return {
                "success": False,
                "error": f"Unknown brand: {brand}. Known brands: {list(BRAND_INTEREST_MAP.keys())}"
            }

        # Validate the interest exists for this brand group
        brand_interests = INTEREST_TAGS.get(interest_group, {})
        if interest not in brand_interests:
            return {
                "success": False,
                "error": (
                    f"Unknown interest '{interest}' for brand '{brand}' "
                    f"(group: {interest_group}). "
                    f"Valid interests: {list(brand_interests.keys())}"
                )
            }

        # Find the tag ID by name
        existing_tags = self.list_tags()
        tag_id = None
        for tag in existing_tags:
            if tag["name"] == interest:
                tag_id = tag["id"]
                break

        if not tag_id:
            # Tag doesn't exist yet, create it
            try:
                result = self.create_tag(interest)
                tag_id = result.get("id")
                logger.info(f"Created missing tag: {interest}")
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Could not create tag '{interest}': {e}"
                }

        # Apply the tag
        try:
            result = self.tag_subscriber(str(tag_id), email)
            logger.info(
                f"Tagged {email} with '{interest}' "
                f"(brand: {brand}, description: {brand_interests[interest]})"
            )
            return {
                "success": True,
                "tag_name": interest,
                "tag_id": tag_id,
                "description": brand_interests[interest],
                "email": email,
                "brand": brand
            }
        except Exception as e:
            logger.error(f"Failed to tag subscriber {email} with {interest}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def tag_subscriber_engagement(self, email: str, engagement_level: str) -> dict:
        """Tag a subscriber with an engagement level.

        Args:
            email: Subscriber email address.
            engagement_level: One of 'highly_engaged', 'moderate_engaged',
                            'at_risk', or 'purchaser'.

        Returns:
            Dict with success status.
        """
        if engagement_level not in ENGAGEMENT_TAGS:
            return {
                "success": False,
                "error": (
                    f"Unknown engagement level: {engagement_level}. "
                    f"Valid levels: {list(ENGAGEMENT_TAGS.keys())}"
                )
            }

        # Find tag ID
        existing_tags = self.list_tags()
        tag_id = None
        for tag in existing_tags:
            if tag["name"] == engagement_level:
                tag_id = tag["id"]
                break

        if not tag_id:
            try:
                result = self.create_tag(engagement_level)
                tag_id = result.get("id")
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Could not create engagement tag: {e}"
                }

        # Remove conflicting engagement tags (subscriber should only
        # have one level at a time, except 'purchaser')
        if engagement_level != "purchaser":
            subscriber = self.find_subscriber_by_email(email)
            if subscriber:
                subscriber_id = str(subscriber.get("id", ""))
                for other_level in ENGAGEMENT_TAGS:
                    if other_level != engagement_level and other_level != "purchaser":
                        for tag in existing_tags:
                            if tag["name"] == other_level:
                                try:
                                    self.remove_tag_from_subscriber(
                                        str(tag["id"]),
                                        subscriber_id
                                    )
                                except Exception:
                                    pass  # Tag might not be on subscriber

        # Apply the engagement tag
        try:
            self.tag_subscriber(str(tag_id), email)
            logger.info(
                f"Tagged {email} as '{engagement_level}' "
                f"({ENGAGEMENT_TAGS[engagement_level]})"
            )
            return {
                "success": True,
                "tag_name": engagement_level,
                "description": ENGAGEMENT_TAGS[engagement_level]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_subscriber_interests(self, email: str) -> dict:
        """Get all interest tags for a subscriber.

        Args:
            email: Subscriber email address.

        Returns:
            Dict with subscriber's interest tags grouped by brand.
        """
        subscriber = self.find_subscriber_by_email(email)
        if not subscriber:
            return {"success": False, "error": "Subscriber not found"}

        subscriber_id = subscriber.get("id")
        response = requests.get(
            f"{self.base_url}/subscribers/{subscriber_id}/tags",
            params={"api_key": self.api_key}
        )
        response.raise_for_status()
        subscriber_tags = response.json().get("tags", [])

        # Build all interest tag names for lookup
        all_interest_tag_names = set()
        for brand_group_tags in INTEREST_TAGS.values():
            all_interest_tag_names.update(brand_group_tags.keys())

        # Filter to interest tags only
        interests = {}
        for tag in subscriber_tags:
            tag_name = tag.get("name", "")
            if tag_name in all_interest_tag_names:
                for group_name, group_tags in INTEREST_TAGS.items():
                    if tag_name in group_tags:
                        if group_name not in interests:
                            interests[group_name] = []
                        interests[group_name].append({
                            "tag": tag_name,
                            "description": group_tags[tag_name]
                        })

        return {
            "success": True,
            "email": email,
            "interests": interests,
            "total_interest_tags": sum(len(v) for v in interests.values())
        }

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

    # Also ensure all interest and engagement tags exist
    tag_results = manager.ensure_tags_exist()
    results.append({
        "brand": "_interest_tags",
        "tags_created": len(tag_results["created"]),
        "tags": tag_results
    })

    return results


if __name__ == "__main__":
    # Run setup when script is executed directly
    results = setup_all_brands()
    for result in results:
        print(f"Brand: {result['brand']} - {result['tags_created']} tags created")
