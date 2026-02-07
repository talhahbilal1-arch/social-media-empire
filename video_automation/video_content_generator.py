"""AI-powered content generation for video scripts using Claude API."""

import json
import os
import random
from typing import Optional
from dataclasses import dataclass, field

import anthropic

from utils.config import get_config
from utils.api_clients import PexelsClient


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
            "Link in bio for the full list + my FREE $25 finds guide!",
            "Get my FREE deals guide - link in bio!",
            "Want more? Grab my free guide in bio!",
            "Comment 'DEALS' for the link + free shopping guide!",
            "Follow + tap the link for exclusive deals sent to your inbox!",
            "Free guide in bio - my secret Amazon finds list!"
        ],
        "urgency_hooks": [
            "Price just DROPPED on this viral find...",
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
        "niche": "fitness tips, health hacks, workout routines for men over 35",
        "tone": "motivational, practical, no-nonsense, masculine, results-focused",
        "audience": "men 35+ looking to improve fitness and health",
        "hashtags": ["#mensfitness", "#over35fitness", "#healthylifestyle", "#workoutmotivation", "#fitover40", "#fitover35", "#homeworkout"],
        "lead_magnet": "FREE 30-Day Workout Plan for Men 35+",
        "cta_styles": [
            "Link in bio for the full workout + FREE 30-day plan!",
            "Get my FREE workout plan - link in bio!",
            "Want the complete routine? Free guide in bio!",
            "Comment 'PLAN' and I'll send you the free workout!",
            "Follow + grab the free plan - link in bio!"
        ],
        "urgency_hooks": [
            "If you're over 35 and not doing THIS, you're leaving gains on the table...",
            "Why most men over 35 FAIL at fitness (and the simple fix)...",
            "This exercise burns more fat than 30 min of cardio...",
            "I wish I knew this at 35 - would've saved me years...",
            "The #1 mistake keeping you from seeing results after 35..."
        ],
        "email_hooks": [
            "Full workout plan in my free guide - link in bio!",
            "I send out new workouts every week - join free in bio!",
            "This is from my email newsletter - get on the list (free) link in bio!"
        ]
    },
    "menopause_planner": {
        "name": "Menopause Planner",
        "niche": "menopause wellness, hormone health, midlife thriving",
        "tone": "supportive, knowledgeable, empowering, understanding",
        "audience": "women 45-60 experiencing perimenopause/menopause",
        "hashtags": ["#menopause", "#perimenopause", "#midlifewellness", "#hormonehealth", "#over50", "#menopausesupport", "#hotflashhelp"],
        "lead_magnet": "FREE Menopause Symptom Tracker + Relief Guide",
        "cta_styles": [
            "Link in bio for the FREE symptom tracker!",
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
            "Link in bio for the FREE shift planner!",
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
            "Link in bio for the FREE ADHD planner!",
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
    duration_seconds: int = 15  # Pinterest optimal is 6-15s


@dataclass
class VideoContentGenerator:
    """Generates video content using Claude API and stock media."""

    claude_client: anthropic.Anthropic = field(default=None)
    pexels_client: PexelsClient = field(default=None)

    def __post_init__(self):
        config = get_config()
        if self.claude_client is None:
            self.claude_client = anthropic.Anthropic(
                api_key=os.environ.get('ANTHROPIC_API_KEY', config.anthropic_api_key if hasattr(config, 'anthropic_api_key') else '')
            )
        if self.pexels_client is None:
            self.pexels_client = PexelsClient(api_key=config.pexels_api_key)

    def _call_claude(self, prompt: str, max_tokens: int = 500) -> str:
        """Call Claude API and return text response."""
        response = self.claude_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

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

        # Generate script using Claude
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
            duration_seconds=15
        )

    def _generate_topic(self, brand: str, content_type: str) -> str:
        """Generate a topic using Claude based on brand and content type."""
        brand_config = BRAND_CONFIG.get(brand, BRAND_CONFIG["daily_deal_darling"])

        prompt = f"""Generate ONE specific, engaging video topic for {brand_config['name']}.
Niche: {brand_config['niche']}
Audience: {brand_config['audience']}
Content type: {content_type}

Return ONLY the topic as a single line, no explanation."""

        topic = self._call_claude(prompt, max_tokens=100)
        return topic.strip().strip('"').strip("'")

    def _generate_script(
        self,
        brand: str,
        brand_config: dict,
        topic: str,
        content_type: str
    ) -> dict:
        """Generate a video script using Claude API."""
        urgency_hooks = brand_config.get('urgency_hooks', [])
        email_hooks = brand_config.get('email_hooks', [])
        lead_magnet = brand_config.get('lead_magnet', 'free guide')

        prompt = f"""Create a 15-second vertical video script for Pinterest for {brand_config['name']}.
Structure: Hook (0-3s), 2 key points (3-11s), CTA (11-15s). Keep text SHORT — max 8 words per overlay. Pinterest users scroll fast.

Topic: {topic}
Tone: {brand_config['tone']}
Audience: {brand_config['audience']}
Lead Magnet to Promote: {lead_magnet}

IMPORTANT - This video should drive viewers to:
1. Follow the account
2. Click the link in bio
3. Sign up for the free guide/email list

Return JSON with:
{{
    "hook": "URGENT, scroll-stopping opening line (max 8 words, 0-3 seconds). Start with a surprising fact or create FOMO.",
    "body": ["Key point 1 (max 8 words)", "Key point 2 (max 8 words)"],
    "cta": "Short CTA mentioning FREE guide in bio (max 8 words, 11-15s)",
    "background_query": "Specific Pexels search query relevant to {brand_config['niche']} and this topic",
    "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
    "music_mood": "upbeat/calm/motivational/energetic"
}}

EXAMPLE HOOKS THAT CONVERT:
- "{urgency_hooks[0] if urgency_hooks else 'This changed everything...'}"
- "I almost didn't share this..."

Keep EVERYTHING short and punchy — this is a 15-second video. Max 8 words per text overlay.
The background_query MUST be specifically relevant to {brand_config['niche']} — no off-brand imagery.
"""

        response = self._call_claude(prompt, max_tokens=500)

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
                "hook": f"Stop scrolling — {topic[:30]}...",
                "body": [
                    f"Here's what works for {topic[:20]}",
                    "This simple trick changed everything"
                ],
                "cta": f"Free guide — link in bio!",
                "background_query": f"{brand_config['niche'].split(',')[0]} lifestyle",
                "email_hook": random.choice(brand_config.get('email_hooks', ['More tips in my free email - bio!'])),
                "hashtags": brand_config["hashtags"][:5],
                "music_mood": "upbeat"
            }

    def _create_text_overlays(self, script: dict) -> list[dict]:
        """Create text overlay configurations for 15-second Pinterest video."""
        overlays = []

        # Hook overlay (0-3s) - scroll stopper
        overlays.append({
            "text": script.get("hook", ""),
            "start_time": 0,
            "end_time": 3,
            "position": "center",
            "style": "bold_large",
            "animation": "fade_in"
        })

        # Body points (3-11s, ~4s each for 2 points)
        body_points = script.get("body", [])[:2]  # Max 2 points for 15s
        for i, point in enumerate(body_points):
            start = 3 + (i * 4)
            overlays.append({
                "text": point,
                "start_time": start,
                "end_time": start + 4,
                "position": "center",
                "style": "medium",
                "animation": "slide_up"
            })

        # CTA overlay (11-15s)
        overlays.append({
            "text": script.get("cta", "Learn more! Link in bio"),
            "start_time": 11,
            "end_time": 15,
            "position": "bottom",
            "style": "cta_bold",
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
