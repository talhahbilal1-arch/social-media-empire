"""AI-powered content generation for video scripts using Gemini."""

import json
import random
from typing import Optional
from dataclasses import dataclass, field

from utils.config import get_config
from utils.api_clients import GeminiClient, PexelsClient


# Brand-specific content configurations (optimized for conversions)
BRAND_CONFIG = {
    "daily_deal_darling": {
        "name": "Daily Deal Darling",
        "niche": "beauty tips, fashion finds, home decor ideas for women",
        "tone": "friendly, excited, relatable, feminine, urgent",
        "audience": "women 25-45 interested in beauty, fashion, and home decor",
        "hashtags": ["#beautytips", "#fashionfinds", "#homedecor", "#amazonfind", "#tiktokshop", "#amazonmusthaves", "#dealsoftheday"],
        "lead_magnet": "FREE guide: 50 Hidden Gems Under $25",
        "cta_styles": [
            "🔗 Link in bio for the full list + my FREE $25 finds guide!",
            "Get my FREE deals guide - link in bio! 🎁",
            "Want more? Grab my free guide in bio! 📥",
            "Comment 'DEALS' for the link + free shopping guide!",
            "Follow + tap the link for exclusive deals sent to your inbox!",
            "💌 Free guide in bio - my secret Amazon finds list!"
        ],
        "urgency_hooks": [
            "🚨 Price just DROPPED on this viral find...",
            "This $__ product is going viral and here's why...",
            "STOP scrolling - this deal ends TODAY...",
            "I almost didn't share this because it keeps selling out...",
            "POV: You find out this cult favorite is now under $__...",
            "This Amazon find has 50,000+ 5-star reviews and costs less than lunch..."
        ],
        "email_hooks": [
            "I share deals like this every week in my free email - link in bio!",
            "My email subscribers got this first - join them (free) link in bio!",
            "This was in last week's deals email. Get on the list - bio link!"
        ]
    },
    "fitnessmadeasy": {
        "name": "Fitness Made Easy",
        "niche": "fat loss, muscle building, workout routines, supplements, nutrition for men over 35",
        "tone": "motivational, practical, no-nonsense, masculine, results-focused",
        "audience": "men 35+ looking to lose belly fat, build muscle, and get fit",
        "hashtags": ["#fitover35", "#mensfitness", "#over35fitness", "#fatloss", "#musclebuilding", "#homeworkout", "#mealprep"],
        "lead_magnet": "FREE 7-Day Fat Loss Kickstart Guide",
        "cta_styles": [
            "🔗 Free 7-Day Fat Loss Kickstart in bio - start today!",
            "Get the FREE fat loss guide at fitover35.com 💪",
            "Want the complete plan? Free at fitover35.com!",
            "Link in bio for the full workout + FREE kickstart guide!",
            "Follow + get the free 7-day plan at fitover35.com!"
        ],
        "urgency_hooks": [
            "If you're over 35 and not doing THIS, you're leaving gains on the table...",
            "Why most men over 35 FAIL at fat loss (and the simple fix)...",
            "This exercise burns more fat than 30 min of cardio...",
            "I wish I knew this at 35 - would've saved me years...",
            "The #1 mistake keeping you from seeing results after 35...",
            "Stop doing crunches. This is what actually burns belly fat after 35...",
            "3 foods killing your progress after 35 (most men eat these daily)...",
            "This 20-minute workout changed everything for men over 35..."
        ],
        "email_hooks": [
            "Free 7-Day Fat Loss guide at fitover35.com - start today!",
            "I send new workouts every week - join free at fitover35.com!",
            "This is from my email newsletter - sign up free at fitover35.com!"
        ],
        "destination_url": "https://fitover35.com",
        "product_url": "https://fitover35.com/products.html"
    },
    "menopause_planner": {
        "name": "Menopause Planner",
        "niche": "menopause wellness, hormone health, midlife thriving",
        "tone": "supportive, knowledgeable, empowering, understanding",
        "audience": "women 45-60 experiencing perimenopause/menopause",
        "hashtags": ["#menopause", "#perimenopause", "#midlifewellness", "#hormonehealth", "#over50", "#menopausesupport", "#hotflashhelp"],
        "lead_magnet": "FREE Menopause Symptom Tracker + Relief Guide",
        "cta_styles": [
            "🔗 Link in bio for the FREE symptom tracker!",
            "Get my FREE menopause relief guide - link in bio!",
            "Comment 'RELIEF' for the free guide!",
            "Free symptom tracker in bio - it's a game changer!",
            "Follow + grab your free guide - link in bio!"
        ],
        "urgency_hooks": [
            "This symptom trick worked when NOTHING else did...",
            "If hot flashes are ruining your sleep, try THIS tonight...",
            "The supplement my doctor FINALLY agreed actually works...",
            "Why this midlife symptom is actually a warning sign...",
            "3 foods making your menopause symptoms WORSE..."
        ],
        "email_hooks": [
            "I share tips like this in my weekly email - free to join, link in bio!",
            "My email subscribers got this tip first - join them free!",
            "More relief tips in my free newsletter - bio link!"
        ]
    },
    "nurse_planner": {
        "name": "Nurse Planner",
        "niche": "nurse lifestyle, healthcare organization, self-care for nurses",
        "tone": "understanding, practical, encouraging, relatable",
        "audience": "nurses and healthcare workers",
        "hashtags": ["#nurselife", "#nursesofinstagram", "#healthcareworker", "#nursetips", "#rn", "#nurseproblems", "#shiftworker"],
        "lead_magnet": "FREE Shift Survival Planner + Self-Care Checklist",
        "cta_styles": [
            "🔗 Link in bio for the FREE shift planner!",
            "Get my FREE nurse survival guide - link in bio!",
            "Comment 'NURSE' for the free planner!",
            "Free shift planner in bio - made for us by us!",
            "Tag a nurse who NEEDS this + follow for more!"
        ],
        "urgency_hooks": [
            "If 12-hour shifts are burning you out, you need THIS...",
            "The boundary I set that saved my nursing career...",
            "Why this simple habit made my shifts 10x easier...",
            "Things I wish I knew my first year as a nurse...",
            "The self-care hack every nurse should know..."
        ],
        "email_hooks": [
            "More nurse life tips in my free weekly email - bio link!",
            "I send shift survival tips every week - join free in bio!",
            "This was in last week's nurse newsletter. Get on the list!"
        ]
    },
    "adhd_planner": {
        "name": "ADHD Planner",
        "niche": "ADHD management, productivity, executive function support",
        "tone": "understanding, non-judgmental, practical, encouraging",
        "audience": "adults with ADHD seeking organization strategies",
        "hashtags": ["#adhd", "#adhdtips", "#adultadhd", "#adhdbrain", "#executivefunction", "#adhdhacks", "#adhdlife"],
        "lead_magnet": "FREE ADHD-Friendly Daily Planner + Focus Guide",
        "cta_styles": [
            "🔗 Link in bio for the FREE ADHD planner!",
            "Get my FREE focus guide - link in bio!",
            "Comment 'FOCUS' for the free planner!",
            "Free ADHD-friendly planner in bio - it actually works!",
            "Save this before you forget! + grab the free guide in bio!"
        ],
        "urgency_hooks": [
            "The ADHD hack that finally helps me actually START tasks...",
            "If your brain refuses to start, try this trick...",
            "Why traditional planners DON'T work for ADHD brains...",
            "This 2-minute trick breaks through ADHD paralysis...",
            "The focus method that actually works for ADHD..."
        ],
        "email_hooks": [
            "More ADHD hacks in my free weekly email - bio link!",
            "I send new productivity tips every week - join free!",
            "My email list gets these tips first - join free in bio!"
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
        # Get urgency hooks and email hooks for this brand
        urgency_hooks = brand_config.get('urgency_hooks', [])
        email_hooks = brand_config.get('email_hooks', [])
        lead_magnet = brand_config.get('lead_magnet', 'free guide')

        # Get destination URL if available (for Pinterest SEO)
        destination_url = brand_config.get('destination_url', '')
        product_url = brand_config.get('product_url', '')

        prompt = f"""Create a 30-second vertical video script for {brand_config['name']}.

Topic: {topic}
Tone: {brand_config['tone']}
Audience: {brand_config['audience']}
Lead Magnet to Promote: {lead_magnet}
Website: {destination_url}

IMPORTANT - This video should drive viewers to:
1. Visit {destination_url} for the free guide
2. Follow the account for more tips
3. Click the link in bio

Return JSON with:
{{
    "hook": "URGENT, scroll-stopping opening line that creates FOMO or curiosity (2-4 seconds). Start with a surprising fact, 'POV:', or a relatable problem. Make them NEED to watch.",
    "body": ["Point 1 - the main actionable tip (short, punchy)", "Point 2 - why it works or 'the best part is...'", "Point 3 - result or proof ('studies show...' or 'I lost X pounds doing this')"],
    "cta": "Strong call to action mentioning {destination_url} and the FREE guide. Create urgency.",
    "email_hook": "Brief mention of the free guide at {destination_url}",
    "pin_title": "A Pinterest-SEO-optimized title under 100 characters with keywords like 'men over 35', 'fat loss', 'workout', 'muscle building'",
    "pin_description": "A keyword-rich Pinterest description (2-3 sentences) that includes relevant search terms. Mention the free guide at {destination_url}",
    "hashtags": ["#fitover35", "#mensfitness", "#tag3", "#tag4", "#tag5", "#tag6", "#tag7"],
    "music_mood": "upbeat/calm/motivational/energetic"
}}

EXAMPLE HOOKS THAT CONVERT:
- "{urgency_hooks[0] if urgency_hooks else 'This changed everything...'}"
- "Stop doing crunches. Here's what actually works after 35..."
- "I lost 20 lbs after 35 by doing this ONE thing differently..."

Make it conversational, engaging, and valuable. The hook must stop the scroll IMMEDIATELY.
The CTA should mention fitover35.com and the FREE guide.
The pin_title and pin_description must be optimized for Pinterest search (include keywords people search for).
"""

        response = self.gemini_client.generate_content(prompt, max_tokens=500)

        try:
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            result = json.loads(response.strip())
            # Ensure email_hook exists
            if 'email_hook' not in result:
                result['email_hook'] = random.choice(brand_config.get('email_hooks', ['Join free in bio!']))
            return result
        except json.JSONDecodeError:
            # Fallback script with conversion focus
            lead_magnet = brand_config.get('lead_magnet', 'free guide')
            return {
                "hook": f"Stop scrolling if you've been struggling with {topic}...",
                "body": [
                    f"Here's what nobody tells you about {topic}",
                    "This simple trick changed everything for me",
                    "Thousands of people are already doing this"
                ],
                "cta": f"Get my {lead_magnet} - link in bio! 🔗",
                "email_hook": random.choice(brand_config.get('email_hooks', ['More tips in my free email - bio!'])),
                "hashtags": brand_config["hashtags"][:7],
                "music_mood": "upbeat"
            }

    def _create_text_overlays(self, script: dict) -> list[dict]:
        """Create text overlay configurations for video with conversion focus."""
        overlays = []

        # Hook overlay (0-4 seconds) - MUST stop the scroll
        overlays.append({
            "text": script.get("hook", ""),
            "start_time": 0,
            "end_time": 4,
            "position": "center",
            "style": "hook",
            "animation": "zoom_in"
        })

        # Body points (4-22 seconds, ~6 seconds each)
        body_points = script.get("body", [])
        for i, point in enumerate(body_points[:3]):
            overlays.append({
                "text": point,
                "start_time": 4 + (i * 6),
                "end_time": 10 + (i * 6),
                "position": "center",
                "style": "body"
            })

        # CTA overlay with email hook (22-26 seconds)
        overlays.append({
            "text": script.get("cta", "Follow for more!"),
            "start_time": 22,
            "end_time": 26,
            "position": "center",
            "style": "cta",
            "animation": "bounce"
        })

        # Email hook / Follow reminder (26-30 seconds)
        email_hook = script.get("email_hook", "Free guide in bio! 🔗")
        overlays.append({
            "text": f"👆 {email_hook}",
            "start_time": 26,
            "end_time": 30,
            "position": "bottom",
            "style": "email_cta",
            "animation": "pulse"
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
