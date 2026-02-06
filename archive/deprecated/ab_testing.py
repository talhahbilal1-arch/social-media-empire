"""A/B testing system for video hooks and content optimization."""

import logging
import random
from datetime import datetime, timezone, timedelta
from typing import Optional
from dataclasses import dataclass, field

from utils.config import get_config
from utils.api_clients import GeminiClient
from database.supabase_client import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Hook style templates for testing
HOOK_STYLES = {
    "curiosity": {
        "name": "Curiosity Gap",
        "templates": [
            "I can't believe {topic} actually works like this...",
            "Nobody talks about this {topic} secret",
            "The real reason {topic} is {outcome}",
            "What they don't tell you about {topic}"
        ]
    },
    "direct": {
        "name": "Direct Value",
        "templates": [
            "Here's how to {benefit} with {topic}",
            "{number} ways to improve your {topic}",
            "The best {topic} tip I've ever found",
            "Do this for better {topic} results"
        ]
    },
    "controversial": {
        "name": "Controversial Take",
        "templates": [
            "Unpopular opinion: {topic} is overrated",
            "Stop doing this with {topic} immediately",
            "Why I hate most {topic} advice",
            "The {topic} myth everyone believes"
        ]
    },
    "story": {
        "name": "Story Hook",
        "templates": [
            "I tried {topic} for 30 days and here's what happened",
            "How {topic} completely changed my life",
            "The moment I realized {topic} was the answer",
            "My {topic} journey: before and after"
        ]
    },
    "pov": {
        "name": "POV Format",
        "templates": [
            "POV: You just discovered {topic}",
            "POV: You finally figured out {topic}",
            "POV: Nobody told you about {topic}",
            "POV: Your life after mastering {topic}"
        ]
    },
    "question": {
        "name": "Question Hook",
        "templates": [
            "Why isn't anyone talking about {topic}?",
            "Did you know {topic} could do this?",
            "What if {topic} is actually {outcome}?",
            "Is {topic} actually worth it?"
        ]
    },
    "list": {
        "name": "List Format",
        "templates": [
            "{number} {topic} tips that actually work",
            "My top {number} {topic} secrets",
            "{number} things I wish I knew about {topic}",
            "{number} {topic} mistakes to avoid"
        ]
    },
    "relatable": {
        "name": "Relatable Struggle",
        "templates": [
            "If you struggle with {topic}, watch this",
            "For everyone who's tired of {topic} problems",
            "Finally - {topic} made simple",
            "This is for my {topic} girlies"
        ]
    }
}


@dataclass
class ABTestResult:
    """Results from an A/B test."""
    test_id: str
    style_a: str
    style_b: str
    winner: Optional[str]
    style_a_metrics: dict
    style_b_metrics: dict
    confidence: float
    created_at: str
    completed_at: Optional[str]


@dataclass
class ABTestingManager:
    """Manages A/B testing for video hooks."""

    gemini_client: GeminiClient = field(default=None)

    def __post_init__(self):
        config = get_config()
        if self.gemini_client is None:
            self.gemini_client = GeminiClient(api_key=config.gemini_api_key)
        self.db = get_supabase_client()

    def generate_hook_variants(self, topic: str, brand: str, count: int = 2) -> list[dict]:
        """Generate multiple hook variants for A/B testing."""
        # Select random styles to test
        styles = random.sample(list(HOOK_STYLES.keys()), min(count, len(HOOK_STYLES)))

        variants = []
        for style in styles:
            style_config = HOOK_STYLES[style]
            template = random.choice(style_config["templates"])

            # Fill template
            hook = template.format(
                topic=topic,
                benefit="succeed",
                number=random.choice(["3", "5", "7"]),
                outcome="different than you think"
            )

            variants.append({
                "style": style,
                "style_name": style_config["name"],
                "hook": hook,
                "template": template
            })

        return variants

    def generate_ai_hook_variants(self, topic: str, brand: str, count: int = 2) -> list[dict]:
        """Use AI to generate hook variants."""
        styles = random.sample(list(HOOK_STYLES.keys()), min(count, len(HOOK_STYLES)))

        variants = []
        for style in styles:
            style_config = HOOK_STYLES[style]

            prompt = f"""Create a viral video hook for this topic: {topic}

Style: {style_config["name"]}
Example templates: {', '.join(style_config["templates"][:2])}

Requirements:
- Must be under 15 words
- Must create curiosity or urgency
- Must feel natural and conversational
- Match the {style} style

Return ONLY the hook text, nothing else."""

            try:
                hook = self.gemini_client.generate_content(prompt, max_tokens=50)
                hook = hook.strip().strip('"').strip("'")

                variants.append({
                    "style": style,
                    "style_name": style_config["name"],
                    "hook": hook,
                    "ai_generated": True
                })
            except Exception as e:
                logger.warning(f"AI hook generation failed: {e}")
                # Fall back to template
                template = random.choice(style_config["templates"])
                hook = template.format(
                    topic=topic,
                    benefit="succeed",
                    number="5",
                    outcome="different"
                )
                variants.append({
                    "style": style,
                    "style_name": style_config["name"],
                    "hook": hook,
                    "ai_generated": False
                })

        return variants

    def create_test(self, brand: str, topic: str) -> dict:
        """Create a new A/B test."""
        variants = self.generate_ai_hook_variants(topic, brand, count=2)

        test_data = {
            "brand": brand,
            "topic": topic,
            "variant_a": variants[0],
            "variant_b": variants[1] if len(variants) > 1 else variants[0],
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metrics_a": {"views": 0, "likes": 0, "comments": 0, "shares": 0},
            "metrics_b": {"views": 0, "likes": 0, "comments": 0, "shares": 0}
        }

        # Log to database
        try:
            self.db.log_analytics_event(
                event_type="ab_test_created",
                brand=brand,
                platform="all",
                data=test_data
            )
        except Exception as e:
            logger.warning(f"Failed to log A/B test: {e}")

        return test_data

    def get_winning_style(self, brand: str, min_tests: int = 5) -> Optional[str]:
        """Analyze past tests to find the best performing hook style."""
        try:
            result = self.db.client.table("analytics_events").select("*").eq(
                "event_type", "ab_test_completed"
            ).eq(
                "brand", brand
            ).execute()

            tests = result.data if result.data else []

            if len(tests) < min_tests:
                return None

            # Count wins by style
            wins = {}
            for test in tests:
                data = test.get("data", {})
                winner = data.get("winner")
                if winner:
                    wins[winner] = wins.get(winner, 0) + 1

            if not wins:
                return None

            return max(wins.items(), key=lambda x: x[1])[0]

        except Exception as e:
            logger.warning(f"Error getting winning style: {e}")
            return None

    def record_metrics(self, test_id: str, variant: str, metrics: dict) -> None:
        """Record engagement metrics for a test variant."""
        try:
            self.db.log_analytics_event(
                event_type="ab_test_metrics",
                brand="",
                platform="all",
                data={
                    "test_id": test_id,
                    "variant": variant,
                    "metrics": metrics,
                    "recorded_at": datetime.now(timezone.utc).isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to record metrics: {e}")

    def analyze_test(self, test_id: str) -> dict:
        """Analyze a test and determine the winner."""
        try:
            result = self.db.client.table("analytics_events").select("*").eq(
                "event_type", "ab_test_metrics"
            ).execute()

            metrics_events = [e for e in (result.data or []) if e.get("data", {}).get("test_id") == test_id]

            if len(metrics_events) < 2:
                return {"status": "insufficient_data", "winner": None}

            # Calculate engagement scores
            variant_scores = {}
            for event in metrics_events:
                data = event.get("data", {})
                variant = data.get("variant")
                metrics = data.get("metrics", {})

                # Engagement score: likes + comments*2 + shares*3
                score = (
                    metrics.get("likes", 0) +
                    metrics.get("comments", 0) * 2 +
                    metrics.get("shares", 0) * 3
                )

                views = metrics.get("views", 1)
                engagement_rate = score / views if views > 0 else 0

                if variant not in variant_scores:
                    variant_scores[variant] = []
                variant_scores[variant].append(engagement_rate)

            # Calculate average scores
            avg_scores = {
                v: sum(scores) / len(scores)
                for v, scores in variant_scores.items()
            }

            if len(avg_scores) < 2:
                return {"status": "insufficient_data", "winner": None}

            winner = max(avg_scores.items(), key=lambda x: x[1])

            return {
                "status": "completed",
                "winner": winner[0],
                "scores": avg_scores,
                "confidence": min(abs(list(avg_scores.values())[0] - list(avg_scores.values())[1]) * 100, 100)
            }

        except Exception as e:
            logger.warning(f"Error analyzing test: {e}")
            return {"status": "error", "winner": None}

    def get_optimized_hook(self, brand: str, topic: str) -> str:
        """Get an optimized hook based on past test results."""
        # Check if we have a winning style
        winning_style = self.get_winning_style(brand)

        if winning_style and winning_style in HOOK_STYLES:
            style_config = HOOK_STYLES[winning_style]
            template = random.choice(style_config["templates"])

            return template.format(
                topic=topic,
                benefit="succeed",
                number=random.choice(["3", "5", "7"]),
                outcome="different than you think"
            )

        # Fall back to random style
        variants = self.generate_hook_variants(topic, brand, count=1)
        return variants[0]["hook"] if variants else f"The truth about {topic}"


def get_best_hook_style_report() -> dict:
    """Generate a report of best performing hook styles by brand."""
    manager = ABTestingManager()
    brands = ["daily_deal_darling", "menopause_planner", "nurse_planner", "adhd_planner"]

    report = {}
    for brand in brands:
        winning_style = manager.get_winning_style(brand, min_tests=3)
        report[brand] = {
            "winning_style": winning_style or "Not enough data",
            "style_name": HOOK_STYLES.get(winning_style, {}).get("name", "N/A") if winning_style else "N/A"
        }

    return report


if __name__ == "__main__":
    manager = ABTestingManager()

    # Demo: Generate hook variants for each brand
    for brand in ["daily_deal_darling", "menopause_planner", "nurse_planner", "adhd_planner"]:
        topic = "saving money" if brand == "daily_deal_darling" else \
                "hot flashes" if brand == "menopause_planner" else \
                "12-hour shifts" if brand == "nurse_planner" else "staying focused"

        print(f"\n{'='*50}")
        print(f"Hook Variants for {brand}")
        print(f"Topic: {topic}")
        print("="*50)

        variants = manager.generate_ai_hook_variants(topic, brand, count=3)
        for i, v in enumerate(variants, 1):
            print(f"\n{i}. [{v['style_name']}]")
            print(f"   {v['hook']}")
