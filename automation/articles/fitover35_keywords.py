"""
Keyword selector for FitOver35 SEO article generation.

Selects low-competition, long-tail keywords targeting men over 35
interested in fitness, strength training, nutrition, and health.
Tracks which keywords have already been used to avoid duplicates.
"""

import os
import json
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Seed keywords - low competition, informational + buyer intent phrases
# Format: (keyword, category, estimated_difficulty)
SEED_KEYWORDS = [
    # === STRENGTH TRAINING ===
    ("best compound exercises for men over 35", "strength_training", "low"),
    ("progressive overload for beginners over 35", "strength_training", "low"),
    ("how to build muscle after 35 naturally", "strength_training", "low"),
    ("density training workout for busy professionals", "strength_training", "low"),
    ("superset workout plan for men over 35", "strength_training", "low"),
    ("how often should men over 35 lift weights", "strength_training", "low"),
    ("best rep range for muscle growth over 35", "strength_training", "low"),
    ("barbell vs dumbbell training for older lifters", "strength_training", "low"),
    ("full body workout vs split for men over 35", "strength_training", "low"),
    ("how to increase bench press after 35", "strength_training", "low"),
    ("deadlift form tips for older lifters", "strength_training", "low"),
    ("squat variations for bad knees over 35", "strength_training", "low"),
    ("training volume for natural lifters over 35", "strength_training", "low"),
    ("strength training frequency for men over 40", "strength_training", "low"),
    ("best exercises for aging athletes", "strength_training", "low"),
    ("how to maintain muscle mass after 40", "strength_training", "low"),
    ("drop sets vs supersets for muscle building", "strength_training", "low"),
    ("time under tension training for hypertrophy", "strength_training", "low"),

    # === NUTRITION ===
    ("how much protein do men over 35 need", "nutrition", "low"),
    ("meal prep for busy dads who lift", "nutrition", "low"),
    ("best high protein meals for muscle building", "nutrition", "low"),
    ("macro counting guide for men over 35", "nutrition", "medium"),
    ("pre workout meal ideas for morning training", "nutrition", "low"),
    ("post workout nutrition for muscle recovery", "nutrition", "low"),
    ("best protein powder for men over 35", "nutrition", "medium"),
    ("creatine benefits for men over 35", "nutrition", "low"),
    ("how to eat enough protein without supplements", "nutrition", "low"),
    ("cutting diet plan for men over 35", "nutrition", "low"),
    ("lean bulk diet for men over 35", "nutrition", "low"),
    ("nutrition mistakes men over 35 make", "nutrition", "low"),
    ("anti inflammatory foods for lifters", "nutrition", "low"),
    ("best carbs for muscle building and recovery", "nutrition", "low"),
    ("intermittent fasting and muscle building over 35", "nutrition", "low"),
    ("hydration guide for strength training", "nutrition", "low"),

    # === RECOVERY ===
    ("best stretching routine for men over 35", "recovery", "low"),
    ("mobility exercises for desk workers who lift", "recovery", "low"),
    ("foam rolling benefits and techniques for lifters", "recovery", "low"),
    ("deload week guide for men over 35", "recovery", "low"),
    ("how to improve sleep for better recovery", "recovery", "low"),
    ("active recovery day ideas for lifters", "recovery", "low"),
    ("hip mobility exercises for squats over 35", "recovery", "low"),
    ("shoulder mobility routine for bench press", "recovery", "low"),
    ("how to prevent injuries in the gym over 35", "recovery", "low"),
    ("cold plunge vs hot bath for recovery", "recovery", "low"),
    ("best recovery tools for home gym", "recovery", "low"),
    ("signs of overtraining for men over 35", "recovery", "low"),
    ("thoracic spine mobility for better posture", "recovery", "low"),
    ("ankle mobility exercises for better squats", "recovery", "low"),

    # === MINDSET ===
    ("building discipline for consistent training", "mindset", "low"),
    ("how to stay consistent with gym over 35", "mindset", "low"),
    ("fitness motivation for busy professionals", "mindset", "low"),
    ("building a training identity after 35", "mindset", "low"),
    ("habit stacking for fitness consistency", "mindset", "low"),
    ("overcoming gym intimidation at any age", "mindset", "low"),
    ("long term mindset for sustainable fitness", "mindset", "low"),
    ("mental toughness training through weightlifting", "mindset", "low"),
    ("goal setting for men starting fitness over 35", "mindset", "low"),
    ("how to restart fitness after a long break", "mindset", "low"),
    ("discipline vs motivation which matters more", "mindset", "low"),
    ("tracking progress without obsessing over scale weight", "mindset", "low"),

    # === EQUIPMENT ===
    ("best home gym setup under 1000 dollars", "equipment", "medium"),
    ("adjustable dumbbells vs fixed dumbbells for home gym", "equipment", "low"),
    ("best power rack for home gym garage", "equipment", "medium"),
    ("resistance bands for strength training at home", "equipment", "low"),
    ("best barbell for home gym under 300", "equipment", "low"),
    ("home gym flooring options and reviews", "equipment", "low"),
    ("best weight bench for home gym", "equipment", "medium"),
    ("pull up bar options for home gym", "equipment", "low"),
    ("best gym bag for men who lift", "equipment", "low"),
    ("wrist wraps vs lifting straps which do you need", "equipment", "low"),
    ("best lifting belt for squats and deadlifts", "equipment", "low"),
    ("compact home gym equipment for small spaces", "equipment", "low"),
    ("best wireless earbuds for weightlifting", "equipment", "low"),
    ("gym timer apps for rest periods and supersets", "equipment", "low"),

    # === HEALTH ===
    ("natural ways to support testosterone over 35", "health", "low"),
    ("joint health supplements for lifters over 35", "health", "low"),
    ("heart health benefits of strength training", "health", "low"),
    ("what bloodwork should men over 35 get", "health", "low"),
    ("lower back pain prevention for lifters", "health", "low"),
    ("knee health for men who squat heavy", "health", "low"),
    ("blood pressure and weightlifting over 35", "health", "low"),
    ("vitamin d benefits for men who train", "health", "low"),
    ("gut health and muscle building connection", "health", "low"),
    ("managing stress hormones and cortisol for lifters", "health", "low"),
    ("bone density and strength training after 35", "health", "low"),
    ("how to protect shoulder health long term", "health", "low"),
    ("sleep and testosterone connection for men over 35", "health", "low"),

    # === PROGRAMS ===
    ("best workout split for men over 35", "programs", "low"),
    ("4 day workout program for busy professionals", "programs", "low"),
    ("beginner strength program for men over 35", "programs", "low"),
    ("push pull legs for men over 35", "programs", "low"),
    ("upper lower split for time efficient training", "programs", "low"),
    ("12 week strength building program over 35", "programs", "low"),
    ("periodization guide for recreational lifters", "programs", "low"),
    ("3 day full body workout plan for men over 35", "programs", "low"),
    ("30 day muscle building challenge for beginners", "programs", "low"),
    ("deload programming for long term progress", "programs", "low"),
    ("how to design your own workout program", "programs", "low"),
    ("minimal effective dose training for busy men", "programs", "low"),
    ("strength training program for fat loss over 35", "programs", "low"),

    # === LIFESTYLE ===
    ("how to fit workouts into a busy schedule", "lifestyle", "low"),
    ("dad fitness tips for staying in shape", "lifestyle", "low"),
    ("morning workout routine for busy professionals", "lifestyle", "low"),
    ("work travel workout tips no gym needed", "lifestyle", "low"),
    ("aging well with strength training men over 35", "lifestyle", "low"),
    ("balancing family life and fitness goals", "lifestyle", "low"),
    ("best time of day to train for men over 35", "lifestyle", "low"),
    ("lunch break workout ideas for office workers", "lifestyle", "low"),
    ("fitness after kids how dads stay in shape", "lifestyle", "low"),
    ("bodybuilding as a hobby for men over 35", "lifestyle", "low"),
    ("how to build a sustainable fitness lifestyle", "lifestyle", "low"),
    ("weekend warrior fitness tips for busy men", "lifestyle", "low"),
    ("staying fit through career changes and stress", "lifestyle", "low"),
    ("fitness role models for men over 35", "lifestyle", "low"),
]


def load_used_keywords(state_file: str = "fitover35_keyword_state.json") -> set:
    """Load keywords that have already been used."""
    state_path = Path(state_file)
    if state_path.exists():
        data = json.loads(state_path.read_text())
        return set(data.get('used_keywords', []))
    return set()


def save_used_keyword(keyword: str, state_file: str = "fitover35_keyword_state.json"):
    """Mark a keyword as used."""
    state_path = Path(state_file)

    if state_path.exists():
        data = json.loads(state_path.read_text())
    else:
        data = {'used_keywords': [], 'last_updated': None}

    if keyword not in data['used_keywords']:
        data['used_keywords'].append(keyword)
        data['last_updated'] = datetime.utcnow().isoformat()

    state_path.write_text(json.dumps(data, indent=2))


def select_keyword(
    category: Optional[str] = None,
    difficulty: str = "low",
    state_file: str = "fitover35_keyword_state.json"
) -> Optional[dict]:
    """
    Select a keyword for article generation.

    Args:
        category: Optional category filter (strength_training, nutrition,
                  recovery, mindset, equipment, health, programs, lifestyle)
        difficulty: Preferred difficulty level ("low", "medium")
        state_file: Path to state file tracking used keywords

    Returns:
        Dict with keyword info or None if all used
    """
    used = load_used_keywords(state_file)

    # Filter available keywords
    available = [
        kw for kw in SEED_KEYWORDS
        if kw[0] not in used
        and (category is None or kw[1] == category)
        and kw[2] == difficulty
    ]

    # If no low difficulty available, try medium
    if not available and difficulty == "low":
        available = [
            kw for kw in SEED_KEYWORDS
            if kw[0] not in used
            and (category is None or kw[1] == category)
        ]

    # If specific category exhausted, try any category
    if not available and category is not None:
        available = [
            kw for kw in SEED_KEYWORDS
            if kw[0] not in used
        ]

    if not available:
        logger.warning("All keywords have been used! Resetting state.")
        # Reset and try again
        Path(state_file).unlink(missing_ok=True)
        available = list(SEED_KEYWORDS)

    # Random selection for variety
    selected = random.choice(available)

    return {
        'keyword': selected[0],
        'category': selected[1],
        'difficulty': selected[2],
        'slug': generate_slug(selected[0]),
    }


def generate_slug(keyword: str) -> str:
    """Generate a URL-friendly slug from a keyword."""
    slug = keyword.lower().replace(' ', '-').replace('?', '').replace("'", '')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    # Remove consecutive hyphens
    while '--' in slug:
        slug = slug.replace('--', '-')
    return slug[:60].rstrip('-')


def generate_article_filename(keyword_info: dict) -> str:
    """Generate a filename for the article."""
    return f"{keyword_info['slug']}.html"


def get_stats(state_file: str = "fitover35_keyword_state.json") -> dict:
    """Get keyword usage statistics."""
    used = load_used_keywords(state_file)
    total = len(SEED_KEYWORDS)
    used_count = len(used)

    categories = {}
    for kw in SEED_KEYWORDS:
        cat = kw[1]
        if cat not in categories:
            categories[cat] = {'total': 0, 'used': 0}
        categories[cat]['total'] += 1
        if kw[0] in used:
            categories[cat]['used'] += 1

    return {
        'total_keywords': total,
        'used_keywords': used_count,
        'remaining_keywords': total - used_count,
        'categories': categories,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Select keyword for FitOver35 article')
    parser.add_argument(
        '--category',
        choices=[
            'strength_training', 'nutrition', 'recovery', 'mindset',
            'equipment', 'health', 'programs', 'lifestyle'
        ],
        help='Filter by category'
    )
    parser.add_argument(
        '--mark-used',
        action='store_true',
        help='Mark the selected keyword as used'
    )
    parser.add_argument(
        '--list-used',
        action='store_true',
        help='List all used keywords'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show keyword usage statistics'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset used keywords state'
    )
    parser.add_argument(
        '--state-file',
        default='fitover35_keyword_state.json',
        help='Path to keyword state file'
    )

    args = parser.parse_args()

    state_file = args.state_file

    if args.reset:
        Path(state_file).unlink(missing_ok=True)
        print("Reset keyword state")
        return 0

    if args.list_used:
        used = load_used_keywords(state_file)
        print(f"Used keywords ({len(used)}):")
        for kw in sorted(used):
            print(f"  - {kw}")
        return 0

    if args.stats:
        stats = get_stats(state_file)
        print(f"Total keywords: {stats['total_keywords']}")
        print(f"Used: {stats['used_keywords']}")
        print(f"Remaining: {stats['remaining_keywords']}")
        print(f"\nBy category:")
        for cat, info in sorted(stats['categories'].items()):
            print(f"  {cat}: {info['used']}/{info['total']} used")
        return 0

    # Select keyword
    keyword_info = select_keyword(
        category=args.category,
        state_file=state_file
    )

    if not keyword_info:
        print("No available keywords!")
        return 1

    print(f"Selected keyword: {keyword_info['keyword']}")
    print(f"Category: {keyword_info['category']}")
    print(f"Difficulty: {keyword_info['difficulty']}")
    print(f"Filename: {generate_article_filename(keyword_info)}")

    if args.mark_used:
        save_used_keyword(keyword_info['keyword'], state_file)
        print("Marked as used")

    # Output for GitHub Actions
    github_output = os.environ.get('GITHUB_OUTPUT', '')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f"keyword={keyword_info['keyword']}\n")
            f.write(f"category={keyword_info['category']}\n")
            f.write(f"filename={generate_article_filename(keyword_info)}\n")
            f.write(f"slug={keyword_info['slug']}\n")
    else:
        # Fallback for local testing
        print(f"\nkeyword={keyword_info['keyword']}")
        print(f"category={keyword_info['category']}")
        print(f"filename={generate_article_filename(keyword_info)}")
        print(f"slug={keyword_info['slug']}")

    return 0


if __name__ == "__main__":
    exit(main())
