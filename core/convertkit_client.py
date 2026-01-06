"""
ConvertKit (Kit) Client - Email marketing API operations
"""
import os
import requests
from typing import Optional, List, Dict, Any


class ConvertKitClient:
    """Wrapper for ConvertKit/Kit API operations."""

    BASE_URL = "https://api.convertkit.com/v3"

    def __init__(self):
        self.api_key = os.environ.get('CONVERTKIT_API_KEY')
        self.api_secret = os.environ.get('CONVERTKIT_API_SECRET')
        self.form_id = os.environ.get('CONVERTKIT_FORM_ID')

        if not self.api_key:
            raise ValueError("CONVERTKIT_API_KEY environment variable required")

    # ==========================================
    # SUBSCRIBERS
    # ==========================================

    def add_subscriber_to_form(
        self,
        email: str,
        form_id: str = None,
        first_name: str = None,
        fields: Dict[str, str] = None,
        tags: List[int] = None
    ) -> Optional[Dict]:
        """
        Add a subscriber to a form.

        Args:
            email: Subscriber email address
            form_id: ConvertKit form ID (uses default if not provided)
            first_name: Subscriber's first name
            fields: Custom field values (e.g., {"quiz_type": "morning", "quiz_result": "early_bird"})
            tags: List of tag IDs to apply

        Returns:
            Subscriber data if successful, None otherwise
        """
        form_id = form_id or self.form_id
        if not form_id:
            raise ValueError("Form ID required - set CONVERTKIT_FORM_ID or pass form_id")

        url = f"{self.BASE_URL}/forms/{form_id}/subscribe"

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

        response = requests.post(url, json=data)

        if response.status_code == 200:
            return response.json().get("subscription")
        else:
            print(f"ConvertKit error: {response.status_code} - {response.text}")
            return None

    def tag_subscriber(self, email: str, tag_id: int) -> bool:
        """
        Add a tag to a subscriber.

        Args:
            email: Subscriber email
            tag_id: ConvertKit tag ID

        Returns:
            True if successful
        """
        url = f"{self.BASE_URL}/tags/{tag_id}/subscribe"

        data = {
            "api_key": self.api_key,
            "email": email
        }

        response = requests.post(url, json=data)
        return response.status_code == 200

    def get_subscriber(self, email: str) -> Optional[Dict]:
        """
        Get subscriber by email.

        Args:
            email: Subscriber email

        Returns:
            Subscriber data if found
        """
        url = f"{self.BASE_URL}/subscribers"

        params = {
            "api_secret": self.api_secret,
            "email_address": email
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            subscribers = response.json().get("subscribers", [])
            return subscribers[0] if subscribers else None
        return None

    # ==========================================
    # TAGS
    # ==========================================

    def get_tags(self) -> List[Dict]:
        """Get all tags in the account."""
        url = f"{self.BASE_URL}/tags"

        params = {"api_key": self.api_key}

        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json().get("tags", [])
        return []

    def create_tag(self, name: str) -> Optional[Dict]:
        """
        Create a new tag.

        Args:
            name: Tag name

        Returns:
            Tag data if successful
        """
        url = f"{self.BASE_URL}/tags"

        data = {
            "api_key": self.api_key,
            "tag": {"name": name}
        }

        response = requests.post(url, json=data)

        if response.status_code == 201:
            return response.json().get("tag")
        return None

    def get_or_create_tag(self, name: str) -> Optional[int]:
        """
        Get tag ID by name, creating it if it doesn't exist.

        Args:
            name: Tag name

        Returns:
            Tag ID
        """
        tags = self.get_tags()
        for tag in tags:
            if tag["name"].lower() == name.lower():
                return tag["id"]

        new_tag = self.create_tag(name)
        return new_tag["id"] if new_tag else None

    # ==========================================
    # FORMS
    # ==========================================

    def get_forms(self) -> List[Dict]:
        """Get all forms in the account."""
        url = f"{self.BASE_URL}/forms"

        params = {"api_key": self.api_key}

        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json().get("forms", [])
        return []

    # ==========================================
    # SEQUENCES
    # ==========================================

    def get_sequences(self) -> List[Dict]:
        """Get all sequences in the account."""
        url = f"{self.BASE_URL}/sequences"

        params = {"api_key": self.api_key}

        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json().get("courses", [])
        return []

    def add_subscriber_to_sequence(self, email: str, sequence_id: int) -> bool:
        """
        Add subscriber to an email sequence.

        Args:
            email: Subscriber email
            sequence_id: ConvertKit sequence ID

        Returns:
            True if successful
        """
        url = f"{self.BASE_URL}/sequences/{sequence_id}/subscribe"

        data = {
            "api_key": self.api_key,
            "email": email
        }

        response = requests.post(url, json=data)
        return response.status_code == 200


# ==========================================
# QUIZ EMAIL CAPTURE HELPER
# ==========================================

class QuizEmailCapture:
    """Helper class for capturing emails from quiz completions."""

    # Tag mappings - these IDs should be set after creating tags in ConvertKit
    QUIZ_TYPE_TAGS = {
        "morning": "quiz-morning",
        "organization": "quiz-organization",
        "selfcare": "quiz-selfcare",
        "beauty": "quiz-beauty",
        "lifestyle": "quiz-lifestyle"
    }

    BRAND_TAGS = {
        "daily-deal-darling": "daily-deal-darling",
        "menopause-planner": "menopause-planner"
    }

    # Etsy product mappings for Menopause Planner brand
    ETSY_PRODUCTS = {
        "symptom_tracker": {
            "name": "Menopause Symptom Tracker",
            "url": "https://www.etsy.com/shop/TheMenopausePlanner",
            "description": "Track your symptoms daily to identify patterns"
        },
        "hot_flash_journal": {
            "name": "Hot Flash Journal",
            "url": "https://www.etsy.com/shop/TheMenopausePlanner",
            "description": "Document triggers and find relief strategies"
        },
        "mood_tracker": {
            "name": "Menopause Mood Tracker",
            "url": "https://www.etsy.com/shop/TheMenopausePlanner",
            "description": "Understand your emotional patterns"
        },
        "sleep_log": {
            "name": "Sleep Quality Log",
            "url": "https://www.etsy.com/shop/TheMenopausePlanner",
            "description": "Improve your sleep during menopause"
        }
    }

    def __init__(self):
        self.client = ConvertKitClient()
        self._tag_cache = {}

    def capture_quiz_completion(
        self,
        email: str,
        quiz_type: str,
        quiz_result: str,
        brand: str,
        first_name: str = None
    ) -> Dict[str, Any]:
        """
        Capture email after quiz completion and tag appropriately.

        Args:
            email: User's email address
            quiz_type: Type of quiz taken (morning, organization, etc.)
            quiz_result: The quiz result/category
            brand: Brand name (daily-deal-darling or menopause-planner)
            first_name: Optional first name

        Returns:
            Dict with subscription status and recommendations
        """
        # Prepare custom fields
        fields = {
            "quiz_type": quiz_type,
            "quiz_result": quiz_result,
            "brand": brand
        }

        # Get tag IDs
        tags_to_apply = []

        # Quiz type tag
        quiz_tag_name = self.QUIZ_TYPE_TAGS.get(quiz_type.lower())
        if quiz_tag_name:
            tag_id = self._get_tag_id(quiz_tag_name)
            if tag_id:
                tags_to_apply.append(tag_id)

        # Brand tag
        brand_tag_name = self.BRAND_TAGS.get(brand.lower())
        if brand_tag_name:
            tag_id = self._get_tag_id(brand_tag_name)
            if tag_id:
                tags_to_apply.append(tag_id)

        # Subscribe to form
        subscription = self.client.add_subscriber_to_form(
            email=email,
            first_name=first_name,
            fields=fields,
            tags=tags_to_apply
        )

        # Get product recommendations
        recommendations = self._get_recommendations(quiz_type, quiz_result, brand)

        return {
            "subscribed": subscription is not None,
            "subscriber_id": subscription.get("id") if subscription else None,
            "tags_applied": tags_to_apply,
            "recommendations": recommendations
        }

    def _get_tag_id(self, tag_name: str) -> Optional[int]:
        """Get or create tag ID with caching."""
        if tag_name not in self._tag_cache:
            tag_id = self.client.get_or_create_tag(tag_name)
            self._tag_cache[tag_name] = tag_id
        return self._tag_cache.get(tag_name)

    def _get_recommendations(self, quiz_type: str, quiz_result: str, brand: str) -> List[Dict]:
        """Get product recommendations based on quiz results."""
        recommendations = []

        # For Menopause Planner brand, include Etsy products
        if brand.lower() == "menopause-planner":
            # Add relevant Etsy products based on quiz type
            if "symptom" in quiz_type.lower() or "track" in quiz_result.lower():
                recommendations.append(self.ETSY_PRODUCTS["symptom_tracker"])
            if "hot" in quiz_result.lower() or "flash" in quiz_result.lower():
                recommendations.append(self.ETSY_PRODUCTS["hot_flash_journal"])
            if "mood" in quiz_result.lower() or "emotion" in quiz_result.lower():
                recommendations.append(self.ETSY_PRODUCTS["mood_tracker"])
            if "sleep" in quiz_result.lower() or "insomnia" in quiz_result.lower():
                recommendations.append(self.ETSY_PRODUCTS["sleep_log"])

            # Default: add symptom tracker if no specific match
            if not recommendations:
                recommendations.append(self.ETSY_PRODUCTS["symptom_tracker"])

        return recommendations


# ==========================================
# STANDALONE FUNCTIONS FOR QUICK USE
# ==========================================

def capture_quiz_email(
    email: str,
    quiz_type: str,
    quiz_result: str,
    brand: str = "daily-deal-darling",
    first_name: str = None
) -> Dict[str, Any]:
    """
    Quick function to capture quiz completion email.

    Example usage:
        result = capture_quiz_email(
            email="user@example.com",
            quiz_type="morning",
            quiz_result="early_bird",
            brand="daily-deal-darling"
        )
    """
    capture = QuizEmailCapture()
    return capture.capture_quiz_completion(
        email=email,
        quiz_type=quiz_type,
        quiz_result=quiz_result,
        brand=brand,
        first_name=first_name
    )
