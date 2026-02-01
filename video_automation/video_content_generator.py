"""AI-powered content generation for video scripts using Gemini."""

import json
import random
from typing import Optional
from dataclasses import dataclass, field

from utils.config import get_config
from utils.api_clients import GeminiClient, PexelsClient


# Brand-specific content configurations
BRAND_CONFIG = {
    "daily_deal_darling": {
        "name": "Daily Deal Darling",
        "niche": "beauty tips, fashion finds, home decor ideas for women",
        "tone": "friendly, excited, relatable, feminine",
        "audience": "women 25-45 interested in beauty, fashion, and home decor",
        "hashtags": ["#beautytips", "#fashionfinds", "#homedecor", "#womenslifestyle", "#beautydeals"],
        "cta_styles": [
            "Link in bio for all my favorite finds!",
            "Follow for daily beauty and fashion tips!",
            "Save this for later!",
            "Comment LINK and I'll send it to you!"
        ]
    },
    "fitnessmadeasy": {
        "name": "Fitness Made Easy",
        "niche": "fitness tips, health hacks, workout routines for men over 35",
        "tone": "motivational, practical, no-nonsense, masculine",
        "audience": "men 35+ looking to improve fitness and health",
        "hashtags": ["#mensfitness", "#over35fitness", "#healthylifestyle", "#workoutmotivation", "#fitover40"],
        "cta_styles": [
            "Follow for more fitness tips that actually work!",
            "Save this for your next workout!",
            "Link in bio for the full routine!",
            "Drop a 💪 if you're trying this!"
        ]
    },
    "menopause_planner": {
        "name": "Menopause Planner",
        "niche": "menopause wellness, hormone health, midlife thriving",
        "tone": "supportive, knowledgeable, empowering",
        "audience": "women 45-60 experiencing perimenopause/menopause",
        "hashtags": ["#menopause", "#perimenopause", "#midlifewellness", "#hormonehealth", "#over50"],
        "cta_styles": [
            "Get your free menopause symptom tracker - link in bio!",
            "Follow for more menopause tips that actually work!",
            "Save this for your next hot flash!",
            "Share with someone who needs this!"
        ]
    },
    "nurse_planner": {
        "name": "Nurse Planner",
        "niche": "nurse lifestyle, healthcare organization, self-care for nurses",
        "tone": "understanding, practical, encouraging",
        "audience": "nurses and healthcare workers",
        "hashtags": ["#nurselife", "#nursesofinstagram", "#healthcareworker", "#nursetips", "#rn"],
        "cta_styles": [
            "Grab your free shift planner - link in bio!",
            "Follow for more nurse life hacks!",
            "Tag a nurse friend who needs this!",
            "Save for your next shift!"
        ]
    },
    "adhd_planner": {
        "name": "ADHD Planner",
        "niche": "ADHD management, productivity, executive function support",
        "tone": "understanding, non-judgmental, practical",
        "audience": "adults with ADHD seeking organization strategies",
        "hashtags": ["#adhd", "#adhdtips", "#adultadhd", "#adhdbrain", "#executivefunction"],
        "cta_styles": [
            "Get your free ADHD-friendly planner - link in bio!",
            "Follow for more ADHD hacks that actually work!",
            "Save this before you forget!",
            "Share with your ADHD bestie!"
        ]
    }
}


@dataclass
class VideoContent:
    """Generated video content structure."""
    brand: str
    topic: str
    hook: str
    body_points: list[str]
    cta: str
    hashtags: list[str]
    music_mood: str
    background_query: str  # For Pexels search
    text_overlays: list[dict]
    duration_seconds: int = 30


@dataclass
class VideoContentGenerator:
    """Generates video content using AI and stock media."""

    gemini_client: GeminiClient = field(default=None)
    pexels_client: PexelsClient = field(default=None)

    def __post_init__(self):
        config = get_config()
        if self.gemini_client is None:
            self.gemini_client = GeminiClient(api_key=config.gemini_api_key)
        if self.pexels_client is None:
            self.pexels_client = PexelsClient(api_key=config.pexels_api_key)

    def generate_content(
        self,
        brand: str,
        topic: Optional[str] = None,
        content_type: str = "tips"
    ) -> VideoContent:
        """Generate complete video content for a brand."""
        brand_config = BRAND_CONFIG.get(brand, BRAND_CONFIG["daily_deal_darling"])

        # Generate topic if not provided
        if not topic:
            topic = self._generate_topic(brand, content_type)

        # Generate script using Gemini
        script = self._generate_script(brand, brand_config, topic, content_type)

        # Create text overlays from script
        overlays = self._create_text_overlays(script)

        # Determine background search query
        bg_query = self._get_background_query(brand, topic)

        return VideoContent(
            brand=brand,
            topic=topic,
            hook=script.get("hook", ""),
            body_points=script.get("body", []),
            cta=script.get("cta", random.choice(brand_config["cta_styles"])),
            hashtags=script.get("hashtags", brand_config["hashtags"][:5]),
            music_mood=script.get("music_mood", "upbeat"),
            background_query=bg_query,
            text_overlays=overlays,
            duration_seconds=30
        )

    def _generate_topic(self, brand: str, content_type: str) -> str:
        """Generate a topic using AI based on brand and content type."""
        brand_config = BRAND_CONFIG.get(brand, BRAND_CONFIG["daily_deal_darling"])

        prompt = f"""Generate ONE specific, engaging video topic for {brand_config['name']}.
Niche: {brand_config['niche']}
Audience: {brand_config['audience']}
Content type: {content_type}

Return ONLY the topic as a single line, no explanation."""

        topic = self.gemini_client.generate_content(prompt, max_tokens=100)
        return topic.strip().strip('"').strip("'")

    def _generate_script(
        self,
        brand: str,
        brand_config: dict,
        topic: str,
        content_type: str
    ) -> dict:
        """Generate a video script using Gemini."""
        prompt = f"""Create a 30-second vertical video script for {brand_config['name']}.

Topic: {topic}
Tone: {brand_config['tone']}
Audience: {brand_config['audience']}

Return JSON with:
{{
    "hook": "Attention-grabbing opening line (must stop the scroll, 2-4 seconds to read)",
    "body": ["Point 1 (short)", "Point 2 (short)", "Point 3 (short)"],
    "cta": "Call to action",
    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
    "music_mood": "upbeat/calm/motivational/energetic"
}}

Make it conversational, engaging, and valuable. The hook must create curiosity or urgency.
"""

        response = self.gemini_client.generate_content(prompt, max_tokens=500)

        try:
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # Fallback script
            return {
                "hook": f"You need to know this about {topic}!",
                "body": [
                    f"Here's the truth about {topic}",
                    "Most people don't realize this",
                    "Try this instead"
                ],
                "cta": random.choice(brand_config["cta_styles"]),
                "hashtags": brand_config["hashtags"][:5],
                "music_mood": "upbeat"
            }

    def _create_text_overlays(self, script: dict) -> list[dict]:
        """Create text overlay configurations for video."""
        overlays = []

        # Hook overlay (0-4 seconds)
        overlays.append({
            "text": script.get("hook", ""),
            "start_time": 0,
            "end_time": 4,
            "position": "center",
            "style": "hook"
        })

        # Body points (4-24 seconds, ~6 seconds each)
        body_points = script.get("body", [])
        for i, point in enumerate(body_points[:3]):
            overlays.append({
                "text": point,
                "start_time": 4 + (i * 6),
                "end_time": 10 + (i * 6),
                "position": "center",
                "style": "body"
            })

        # CTA overlay (24-30 seconds)
        overlays.append({
            "text": script.get("cta", "Follow for more!"),
            "start_time": 24,
            "end_time": 30,
            "position": "center",
            "style": "cta"
        })

        return overlays

    def _get_background_query(self, brand: str, topic: str) -> str:
        """Determine the best Pexels search query for background."""
        # Brand-specific background preferences
        brand_backgrounds = {
            "daily_deal_darling": ["beauty aesthetic", "fashion flatlay", "home decor", "feminine lifestyle"],
            "fitnessmadeasy": ["gym workout", "man exercising", "fitness motivation", "healthy lifestyle man"],
            "menopause_planner": ["calm wellness", "mature woman", "self care", "peaceful nature"],
            "nurse_planner": ["healthcare", "hospital", "medical professional", "coffee break"],
            "adhd_planner": ["organized desk", "planner", "productivity", "colorful workspace"]
        }

        backgrounds = brand_backgrounds.get(brand, ["lifestyle", "aesthetic"])
        return random.choice(backgrounds)

    def get_background_media(
        self,
        query: str,
        media_type: str = "video",
        count: int = 3,
        max_retries: int = 3
    ) -> list[dict]:
        """Get background media from Pexels with retry logic for rate limiting."""
        import time

        for attempt in range(max_retries):
            try:
                if media_type == "video":
                    results = self.pexels_client.search_videos(query, per_page=count)
                    return [
                        {
                            "url": self.pexels_client.get_video_url(v),
                            "id": v.get("id"),
                            "duration": v.get("duration")
                        }
                        for v in results
                    ]
                else:
                    results = self.pexels_client.search_photos(query, per_page=count)
                    return [
                        {
                            "url": self.pexels_client.get_photo_url(p),
                            "id": p.get("id")
                        }
                        for p in results
                    ]
            except Exception as e:
                if "401" in str(e) and attempt < max_retries - 1:
                    # Rate limited - wait with exponential backoff
                    wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
                    time.sleep(wait_time)
                    continue
                raise
        return []

    def generate_batch_content(
        self,
        brands: list[str],
        content_per_brand: int = 1
    ) -> list[VideoContent]:
        """Generate content for multiple brands."""
        all_content = []
        for brand in brands:
            for _ in range(content_per_brand):
                content = self.generate_content(brand)
                all_content.append(content)
        return all_content
