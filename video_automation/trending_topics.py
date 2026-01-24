"""Trending topics discovery for content optimization."""

import logging
import random
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass

from utils.config import get_config
from utils.api_clients import GeminiClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Evergreen topics by brand (always relevant)
EVERGREEN_TOPICS = {
    "daily_deal_darling": [
        "Amazon hidden deals section",
        "Target Circle secrets",
        "Costco vs Sam's Club comparison",
        "Dollar store hacks",
        "Subscribe & Save strategy",
        "Cashback app stacking",
        "Clearance shopping tips",
        "Price matching secrets",
        "Coupon organization",
        "Budget meal planning deals"
    ],
    "menopause_planner": [
        "Hot flash triggers to avoid",
        "Best foods for hormone balance",
        "Sleep strategies for menopause",
        "Managing brain fog",
        "Natural supplements that help",
        "Exercise during menopause",
        "Mood swing management",
        "Perimenopause early signs",
        "HRT myths vs facts",
        "Weight gain prevention"
    ],
    "nurse_planner": [
        "12-hour shift survival tips",
        "Night shift sleep schedule",
        "Nurse foot care essentials",
        "Meal prep for nurses",
        "Burnout prevention",
        "Documentation shortcuts",
        "Work-life balance tips",
        "Self-care on shift",
        "Time management hacks",
        "Difficult patient strategies"
    ],
    "adhd_planner": [
        "Morning routine hacks",
        "Task initiation strategies",
        "Time blindness solutions",
        "Focus techniques that work",
        "ADHD-friendly organization",
        "Habit building for ADHD",
        "Dealing with overwhelm",
        "Working memory tips",
        "Rejection sensitivity coping",
        "Body doubling benefits"
    ]
}

# Seasonal/timely topics
SEASONAL_TOPICS = {
    "daily_deal_darling": {
        1: ["New Year organization deals", "January white sales", "Fitness gear deals"],
        2: ["Valentine's Day gifts on budget", "Presidents Day sales"],
        3: ["Spring cleaning deals", "St. Patrick's Day finds"],
        4: ["Easter basket deals", "Spring organization"],
        5: ["Memorial Day sales", "Summer prep deals"],
        6: ["Amazon Prime Day prep", "Summer travel deals"],
        7: ["Prime Day deals", "Back to school prep"],
        8: ["Back to school deals", "Dorm room essentials"],
        9: ["Labor Day sales", "Fall organization"],
        10: ["Halloween deals", "Early holiday shopping"],
        11: ["Black Friday strategy", "Cyber Monday prep", "Holiday gift guides"],
        12: ["Last-minute gift deals", "After Christmas sales"]
    },
    "menopause_planner": {
        1: ["New Year health goals", "Winter self-care"],
        2: ["Heart health awareness", "Self-love month"],
        3: ["Spring wellness reset", "Women's History Month"],
        4: ["Stress awareness month"],
        5: ["Mental health awareness", "Mother's Day self-care"],
        6: ["Summer cooling strategies"],
        7: ["Beat the summer heat"],
        8: ["Back to routine wellness"],
        9: ["Fall wellness prep", "Menopause awareness month"],
        10: ["Breast cancer awareness", "Menopause awareness"],
        11: ["Gratitude practice", "Holiday stress management"],
        12: ["Year-end reflection", "Holiday boundaries"]
    },
    "nurse_planner": {
        1: ["New Year career goals", "Winter wellness for nurses"],
        2: ["Heart month awareness", "Self-care reset"],
        3: ["March nursing events", "Spring shift prep"],
        4: ["Stress awareness for healthcare", "Spring cleaning lockers"],
        5: ["Nurses Week celebration", "Mental health awareness"],
        6: ["Summer shift survival"],
        7: ["Beat nurse burnout"],
        8: ["Back to school nursing", "Fall schedule prep"],
        9: ["Suicide prevention awareness"],
        10: ["Breast cancer awareness nursing"],
        11: ["Gratitude in nursing", "Holiday shift survival"],
        12: ["Year-end reflection", "Holiday nursing"]
    },
    "adhd_planner": {
        1: ["New Year ADHD-friendly goals", "Fresh start strategies"],
        2: ["ADHD and relationships", "Valentine's Day planning"],
        3: ["Spring reset for ADHD", "Daylight saving adjustment"],
        4: ["Tax season ADHD survival", "Spring cleaning with ADHD"],
        5: ["ADHD mental health month"],
        6: ["Summer ADHD challenges", "Routine-free survival"],
        7: ["Mid-year reset ADHD style"],
        8: ["Back to school ADHD prep"],
        9: ["Fall routine building", "ADHD awareness month"],
        10: ["ADHD awareness month content", "Holiday prep start"],
        11: ["ADHD holiday survival", "Black Friday impulse control"],
        12: ["Holiday overwhelm management", "Year reflection"]
    }
}

# Trending format types
TRENDING_FORMATS = [
    "3 things nobody tells you about {topic}",
    "Stop doing this one thing for {topic}",
    "The truth about {topic}",
    "Why {topic} is actually {outcome}",
    "{number} hacks for {topic} that actually work",
    "I tried {topic} for 30 days - here's what happened",
    "Unpopular opinion: {topic}",
    "Signs you need to {action} for {topic}",
    "What I wish I knew about {topic}",
    "POV: You just discovered {topic}"
]


@dataclass
class TrendingTopicsManager:
    """Manages trending and timely topic discovery."""

    gemini_client: GeminiClient = None

    def __post_init__(self):
        config = get_config()
        if self.gemini_client is None:
            self.gemini_client = GeminiClient(api_key=config.gemini_api_key)

    def get_topic_for_brand(self, brand: str, use_seasonal: bool = True) -> str:
        """Get a relevant topic for a brand, considering seasonality."""
        topics = []

        # Always include evergreen topics
        topics.extend(EVERGREEN_TOPICS.get(brand, []))

        # Add seasonal topics if enabled
        if use_seasonal:
            month = datetime.now().month
            seasonal = SEASONAL_TOPICS.get(brand, {}).get(month, [])
            # Weight seasonal topics higher
            topics.extend(seasonal * 2)

        return random.choice(topics) if topics else "general tips"

    def generate_trending_hook(self, brand: str, topic: str) -> str:
        """Generate a trending-style hook for a topic."""
        format_template = random.choice(TRENDING_FORMATS)

        # Fill in template
        hook = format_template.format(
            topic=topic,
            outcome="different than you think",
            number=random.choice(["3", "5", "7"]),
            action="start"
        )

        return hook

    def get_ai_trending_topic(self, brand: str) -> str:
        """Use AI to generate a trending topic."""
        brand_context = {
            "daily_deal_darling": "budget shopping, deals, Amazon finds, saving money",
            "menopause_planner": "menopause, perimenopause, hormone health, women's wellness",
            "nurse_planner": "nursing, healthcare workers, shift work, nurse life",
            "adhd_planner": "ADHD, focus, productivity, executive function, neurodivergent"
        }

        context = brand_context.get(brand, "lifestyle")

        prompt = f"""Generate ONE specific, engaging video topic about {context}.

Requirements:
- Must be specific and actionable
- Should feel timely and relevant
- Works for a 30-second vertical video
- Appeals to the target audience

Return ONLY the topic as a single line, no explanation or punctuation at the end."""

        try:
            topic = self.gemini_client.generate_content(prompt, max_tokens=100)
            return topic.strip().strip('"').strip("'")
        except Exception as e:
            logger.warning(f"AI topic generation failed: {e}")
            return self.get_topic_for_brand(brand)

    def get_content_calendar(self, brand: str, days: int = 7) -> list[dict]:
        """Generate a content calendar for upcoming days."""
        calendar = []
        current_date = datetime.now(timezone.utc)

        for day in range(days):
            date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            date = date.replace(day=date.day + day)

            # Mix of evergreen and seasonal
            use_seasonal = day % 3 == 0  # Every 3rd day use seasonal

            topic = self.get_topic_for_brand(brand, use_seasonal=use_seasonal)
            hook = self.generate_trending_hook(brand, topic)

            calendar.append({
                "date": date.strftime("%Y-%m-%d"),
                "day_of_week": date.strftime("%A"),
                "topic": topic,
                "suggested_hook": hook,
                "is_seasonal": use_seasonal
            })

        return calendar

    def get_hashtag_trends(self, brand: str) -> list[str]:
        """Get trending hashtags for a brand."""
        base_hashtags = {
            "daily_deal_darling": ["#deals", "#amazonfinds", "#budgettips", "#savingmoney", "#dealalert"],
            "menopause_planner": ["#menopause", "#perimenopause", "#midlife", "#hormonehealth", "#over50"],
            "nurse_planner": ["#nurselife", "#nursesoftiktok", "#healthcare", "#rn", "#nursetips"],
            "adhd_planner": ["#adhd", "#adhdtiktok", "#adultadhd", "#neurodivergent", "#adhdhacks"]
        }

        trending_additions = {
            "daily_deal_darling": ["#tiktokshop", "#amazonmusthaves", "#budgetfriendly"],
            "menopause_planner": ["#menopauseawareness", "#hotflashes", "#womenover40"],
            "nurse_planner": ["#nursesweek", "#healthcareworkers", "#nursehumor"],
            "adhd_planner": ["#adhdbrain", "#adhdsupport", "#executivefunction"]
        }

        hashtags = base_hashtags.get(brand, [])
        hashtags.extend(trending_additions.get(brand, []))

        # Randomize order but always include base tags
        random.shuffle(hashtags)
        return hashtags[:8]  # Return top 8


def get_daily_topics(brand: str, count: int = 3) -> list[str]:
    """Get multiple topics for daily content."""
    manager = TrendingTopicsManager()

    topics = []
    used_topics = set()

    while len(topics) < count:
        topic = manager.get_topic_for_brand(brand)
        if topic not in used_topics:
            topics.append(topic)
            used_topics.add(topic)

    return topics


if __name__ == "__main__":
    manager = TrendingTopicsManager()

    for brand in ["daily_deal_darling", "menopause_planner", "nurse_planner", "adhd_planner"]:
        print(f"\n{'='*50}")
        print(f"Content Calendar for {brand}")
        print("="*50)

        calendar = manager.get_content_calendar(brand, days=7)
        for day in calendar:
            print(f"\n{day['date']} ({day['day_of_week']})")
            print(f"  Topic: {day['topic']}")
            print(f"  Hook: {day['suggested_hook']}")

        print(f"\nHashtags: {' '.join(manager.get_hashtag_trends(brand))}")
