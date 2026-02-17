"""Claude-powered content brain for all 3 Pinterest brands.

Generates unique, high-quality pin content using Claude API (Sonnet 4.5).
Tracks content history in Supabase to ensure variety across topics, angles,
visual styles, boards, and description openers.

Optimized for maximum Pinterest clicks, engagement, and affiliate revenue:
- Curiosity-gap titles using proven Pinterest formulas (40-60 chars)
- SEO-front-loaded descriptions with emotional triggers and CTAs
- Strategic visual style rotation prioritizing high-engagement formats
- Natural affiliate product integration per brand niche
- Board selection weighted toward highest-follower boards

Replaces all Gemini-based content generation.
"""

import anthropic
import json
import random
import os
import re
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    """Lazy-initialize the Anthropic client to prevent import-time failures."""
    global _client
    if _client is None:
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client

# ═══════════════════════════════════════════════════════════════
# BRAND CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════

BRAND_CONFIGS = {
    "fitness": {
        "name": "Fitness Made Easy",
        "voice": """You are a 38-year-old man who's been through the fitness journey himself.
You gained weight in your early 30s, got serious at 35, and now you're in the best shape of your life.
You talk like a real person — direct, honest, sometimes funny, never preachy.
You use 'I' and 'you' language. You share what actually worked for you.
You respect your audience — they're smart guys who just need actionable advice.
NEVER sound like a generic fitness influencer. NEVER say 'unlock your potential' or 'transform your life.'
Be specific. Use real exercises, real foods, real numbers.""",

        "hook_frameworks": [
            # Curiosity gap formulas — reader MUST click to get the answer
            "Stop {common_exercise} After 35 — Do This Instead",
            "I Tried {specific_thing} for 30 Days — Here's What Happened",
            "The {adjective} {food/exercise} That {result} (Most Men Don't Know)",
            "{Number} Things That {outcome} After 35 (#{number} Surprised Me)",
            "My Doctor Said This About {supplement} — I Wasn't Ready",
            "The ${cheap_price} {thing} That Replaced My ${expensive_price} {other_thing}",
            "Why {popular_thing} Is Secretly {bad_outcome} After 35",
            "I Tracked {metric} for {timeframe} — The Results Were Shocking",
            "The {time_of_day} Mistake Killing Your {goal} (Easy Fix)",
            "What {specific_number}% of Men Over 35 Get Wrong About {topic}",
            "{Thing} vs {Other_Thing} — The Winner Isn't What You Think",
            "The One {exercise/supplement} I Refused to Try (Until Now)",
            "I Quit {common_thing} for {timeframe} and My {metric} {result}",
            "The Proven {timeframe} Protocol That {specific_result}",
            "3 Signs Your {body_part} Needs This (Most Men Ignore #2)"
        ],

        # Affiliate product categories for natural integration
        "affiliate_products": {
            "supplements": ["creatine monohydrate", "vitamin D3", "magnesium glycinate", "fish oil", "ashwagandha", "protein powder", "collagen peptides"],
            "workout_gear": ["resistance bands set", "adjustable dumbbells", "pull-up bar", "foam roller", "kettlebell", "yoga mat", "lifting straps"],
            "meal_prep": ["glass meal prep containers", "food scale", "protein shaker", "air fryer", "slow cooker", "blender bottle"],
            "recovery": ["massage gun", "cold plunge tub", "compression sleeves", "sleep mask", "blue light glasses", "sauna blanket"]
        },

        # Board priority order (highest follower count first)
        "board_priority": [
            "Fat Loss After 35",
            "Workouts for Men Over 35",
            "Meal Prep & Nutrition",
            "Supplement Honest Reviews",
            "Fitness Motivation",
            "Home Gym Ideas"
        ],

        "topics_by_category": {
            "workouts": [
                "compound lifts vs isolation exercises efficiency after 35",
                "the reverse pyramid training method for natural lifters",
                "why deload weeks matter more after 35 and how to do them",
                "grip strength training and its connection to longevity",
                "10-minute morning mobility routine that prevents injuries",
                "the minimum effective dose workout for busy professionals",
                "push pull legs vs upper lower split for men over 35",
                "bodyweight exercises that build real muscle at any age",
                "the 3x per week full body routine backed by research",
                "deadlift form fixes specifically for men with desk jobs",
                "kettlebell complexes that burn fat and build muscle simultaneously",
                "resistance band workouts that actually challenge experienced lifters",
                "how to structure a home gym workout with limited equipment",
                "the walking workout most men over 35 underestimate",
                "swimming vs lifting for longevity after 35"
            ],
            "nutrition": [
                "protein timing and the anabolic window myth",
                "creatine monohydrate — the most studied supplement in history",
                "Mediterranean diet modified for muscle building goals",
                "intermittent fasting real pros and cons for men over 35",
                "micronutrients most men over 35 are deficient in",
                "pre-workout meal timing for maximum performance",
                "post-workout nutrition what actually matters",
                "meal prep Sunday system for the entire week",
                "calorie deficit without losing muscle — how to cut properly",
                "bulking after 35 — why dirty bulks don't work anymore",
                "fiber intake and gut health for better nutrient absorption",
                "alcohol and fitness — the real impact on testosterone and recovery",
                "hydration myths and how much water you actually need",
                "the best protein sources ranked by biological value",
                "carb cycling for fat loss while maintaining strength"
            ],
            "supplements": [
                "creatine monohydrate vs HCL — honest comparison",
                "vitamin D and testosterone — what the research shows",
                "magnesium types explained — which one for sleep vs recovery",
                "fish oil dosing for inflammation and joint health",
                "ashwagandha evidence review for stress and hormones",
                "zinc and its role in testosterone production",
                "collagen supplements for joint health — worth it or not",
                "caffeine timing and cycling for better workouts",
                "testosterone boosters — which ones have evidence vs hype",
                "probiotics for gym performance and recovery"
            ],
            "lifestyle": [
                "sleep optimization — the #1 recovery tool most men ignore",
                "stress and cortisol — how they sabotage fat loss",
                "cold exposure honest review — benefits vs hype",
                "how to stay consistent when motivation disappears",
                "tracking progress without obsessing over the scale",
                "the relationship between posture and back pain after 35",
                "desk job damage — what sitting 8 hours does to your body",
                "recovery techniques ranked by actual effectiveness",
                "how to exercise with a nagging injury without making it worse",
                "the connection between mental health and physical fitness"
            ],
            "fat_loss": [
                "belly fat after 35 — why it's different and what works",
                "metabolic adaptation — why your diet stopped working",
                "NEAT and why daily movement matters more than gym sessions",
                "body recomposition vs cut and bulk — which strategy wins",
                "the scale is lying to you — better ways to measure progress",
                "cardio vs weights for fat loss — the definitive answer",
                "stubborn fat areas and how to actually target them",
                "refeed days — strategic diet breaks that help fat loss",
                "hormone optimization for easier fat loss naturally",
                "the 80/20 rule of fat loss that simplifies everything"
            ]
        },

        "seo_keywords": [
            "men over 35 fitness", "workout plan over 35", "muscle building after 35",
            "lose belly fat men", "supplements for men over 35", "home workout no equipment",
            "meal prep for muscle", "strength training over 35", "testosterone naturally",
            "protein for men over 35", "fat loss after 35", "fitness motivation men",
            "best exercises men over 35", "creatine over 35", "metabolism boost natural"
        ],

        "hashtags": [
            "#fitover35", "#menshealth", "#fitnessmotivation", "#workoutover35",
            "#strengthtraining", "#musclebuilding", "#fitnessafter35", "#mensfitness"
        ],

        "destination_base_url": "https://fitover35.com",
        "pinterest_boards": [
            "Workouts for Men Over 35",
            "Meal Prep & Nutrition",
            "Supplement Honest Reviews",
            "Fat Loss After 35",
            "Home Gym Ideas",
            "Fitness Motivation"
        ]
    },

    "deals": {
        "name": "Daily Deal Darling",
        "voice": """You are a 32-year-old woman who loves finding amazing products at great prices.
You're genuine — you only share things you'd actually buy or have bought yourself.
You're warm, enthusiastic but never fake. Like texting your best friend about a great find.
You use casual language, express real excitement, and always explain WHY something is worth buying.
You compare products honestly. You mention when something ISN'T worth the hype.
NEVER sound like a sales bot. NEVER use 'amazing deal alert' or 'limited time offer' language.
Be conversational, relatable, and helpful.""",

        "hook_frameworks": [
            # FOMO + curiosity gap formulas for maximum clicks
            "This ${price} Find Replaced My ${expensive} {thing} (Not Kidding)",
            "I Tried {number} {products} — Only This One Was Worth It",
            "Stop Overpaying for {product} — This ${price} Dupe Is Better",
            "The {room} Upgrade Everyone Asks Me About (Under ${price})",
            "{Number} {products} That Look ${expensive} but Cost Under ${price}",
            "Why I Returned the {popular_product} Everyone Loves",
            "The ${price} {product} That Sold Out 3 Times (It's Back)",
            "I've Repurchased This {number} Times — It's That Good",
            "My {room} Before & After (Total Budget: ${price})",
            "The {product} I Almost Didn't Buy — Biggest Mistake",
            "What I Actually Use Daily vs What Collected Dust",
            "The Viral {product} — Does It Live Up to the Hype?",
            "{Season}'s Best Home Finds (All Under ${price})",
            "3 Things I'll Never Buy Name Brand Again (The Dupes Win)",
            "The {product} That Fixed My Biggest {room} Problem"
        ],

        # Affiliate product categories for natural integration
        "affiliate_products": {
            "kitchen": ["air fryer", "knife set", "meal prep containers", "coffee maker", "organizer bins", "cutting boards", "spice rack"],
            "home_decor": ["throw pillows", "LED candles", "wall art frames", "curtain sets", "accent mirrors", "blanket ladders"],
            "organization": ["closet system", "drawer dividers", "label maker", "storage bins", "shelf risers", "vacuum bags"],
            "self_care": ["silk pillowcase", "LED face mask", "bath bombs set", "hair tools", "skincare fridge", "heated eye mask"]
        },

        # Board priority order (highest follower count first)
        "board_priority": [
            "Kitchen Must-Haves",
            "Home Organization Finds",
            "Budget Home Decor",
            "Self Care Products Worth It",
            "Seasonal Favorites",
            "Gift Ideas"
        ],

        "topics_by_category": {
            "kitchen": [
                "air fryer accessories that actually get used",
                "kitchen organization containers under $30 total",
                "the one kitchen gadget that replaced three others",
                "meal prep containers comparison and honest review",
                "small kitchen maximizing counter space solutions",
                "knife set comparison under $50 worth buying",
                "coffee maker alternatives to expensive machines",
                "pantry organization realistic affordable system",
                "kitchen cleaning products that actually work",
                "best cutting boards by material and price"
            ],
            "home_decor": [
                "living room refresh ideas under $100 total budget",
                "bathroom upgrades that look expensive but aren't",
                "bedroom cozy makeover affordable picks",
                "wall art and frames that elevate any room",
                "throw pillows and blankets best finds this season",
                "candles and home fragrance honest favorites",
                "curtains that make a room look more expensive",
                "accent furniture pieces under $75",
                "bookshelf styling ideas with affordable accessories",
                "entryway organization that makes a first impression"
            ],
            "organization": [
                "closet system under $50 that changed everything",
                "garage organization best affordable finds",
                "bathroom cabinet organization solutions",
                "desk and home office organization essentials",
                "kids room organization that actually stays organized",
                "laundry room setup affordable upgrades",
                "shoe storage solutions for small spaces",
                "craft supply organization ideas",
                "under sink cabinet organization bathroom and kitchen",
                "seasonal item storage smart solutions"
            ],
            "self_care": [
                "skincare routine affordable products that work",
                "hair tools honest review and comparison",
                "bath products that feel luxurious under $20",
                "at home spa night essentials and setup",
                "workout gear and athleisure finds worth buying",
                "sleep improvement products that made a difference",
                "journal and planner picks for organization",
                "comfortable loungewear best affordable brands",
                "self care subscription box honest reviews",
                "wellness products worth the investment"
            ],
            "seasonal": [
                "spring cleaning must-have products",
                "summer entertaining essentials for hosting",
                "fall cozy home transition affordable picks",
                "holiday gift ideas at every price point",
                "back to school organization for parents",
                "new year refresh home and personal picks",
                "valentines day gift ideas actually useful",
                "outdoor living affordable patio setup"
            ]
        },

        "seo_keywords": [
            "best home finds", "kitchen gadgets worth buying", "home organization ideas",
            "affordable home decor", "self care products", "gift ideas for women",
            "budget home makeover", "amazon home finds", "target finds",
            "home must haves", "apartment decor ideas", "organization hacks",
            "best deals home", "product review honest", "worth buying"
        ],

        "hashtags": [
            "#amazonfinds", "#homefinds", "#dealsoftheday", "#budgetfriendly",
            "#homeorganization", "#kitchengadgets", "#selfcare", "#worthbuying"
        ],

        "destination_base_url": "https://dailydealdarling.com",
        "pinterest_boards": [
            "Home Organization Finds",
            "Kitchen Must-Haves",
            "Self Care Products Worth It",
            "Budget Home Decor",
            "Gift Ideas",
            "Seasonal Favorites"
        ]
    },

    "menopause": {
        "name": "The Menopause Planner",
        "voice": """You are a 52-year-old woman who has been through perimenopause and is now in menopause.
You combine personal experience with well-researched information.
You're empathetic, warm, and practical. You normalize the experience — no shame, no drama.
You speak like a knowledgeable friend, not a doctor (always include 'talk to your doctor' for medical topics).
You validate feelings while offering actionable solutions.
You're specific about what helped you personally vs what the research says.
NEVER be condescending. NEVER minimize symptoms. NEVER use clinical/cold language.
This audience is going through something hard and wants to feel seen and helped.""",

        "hook_frameworks": [
            # Empathy + relief + curiosity gap formulas
            "The {symptom} Relief My Doctor Never Mentioned (Simple Fix)",
            "I Tried Everything for {symptom} — Only This Worked",
            "Stop Ignoring This {symptom} Sign (It's Not What You Think)",
            "{Number} Things That Finally Helped My {symptom}",
            "The {supplement/food} That Changed My {symptom} in {timeframe}",
            "What {number}% of Women Don't Know About {symptom}",
            "Why the Usual {symptom} Advice Makes It Worse",
            "I Tracked My Symptoms for {timeframe} — The Pattern Was Eye-Opening",
            "The {time_of_day} Routine That Gave Me My Sleep Back",
            "What I Wish I Knew About {topic} 5 Years Earlier",
            "{Common_advice} Is Outdated — Here's What Doctors Say Now",
            "The ${price} {product} That Helped More Than My ${expensive} {thing}",
            "My Honest {timeframe} Review of {treatment} for {symptom}",
            "3 Small Changes That Made the Biggest Difference",
            "If Your {symptom} Started After 40 — Read This"
        ],

        # Affiliate product categories for natural integration
        "affiliate_products": {
            "supplements": ["black cohosh", "evening primrose oil", "magnesium glycinate", "vitamin D3", "maca root", "DIM supplement", "probiotics for women"],
            "comfort": ["cooling pillow", "bamboo sheets", "cooling pajamas", "portable fan", "weighted blanket", "heating pad"],
            "wellness": ["symptom tracker journal", "menopause planner", "yoga mat", "meditation app subscription", "essential oils diffuser", "acupressure mat"],
            "skincare": ["hyaluronic acid serum", "retinol cream", "collagen powder", "SPF moisturizer", "eye cream", "body lotion for dry skin"]
        },

        # Board priority order (highest follower count first)
        "board_priority": [
            "Menopause Symptoms & Relief",
            "Menopause Self Care",
            "Hormone Balance Naturally",
            "Menopause Nutrition & Wellness",
            "Perimenopause Tips & Support"
        ],

        "topics_by_category": {
            "symptoms": [
                "hot flash triggers identification and avoidance strategies",
                "night sweats and sleep disruption practical solutions",
                "menopause brain fog coping strategies that work",
                "mood swings understanding the hormonal connection",
                "joint pain during menopause often overlooked symptom",
                "heart palpitations and menopause when to worry",
                "menopause fatigue vs regular tiredness",
                "vaginal dryness practical solutions and products",
                "headaches and migraines during perimenopause",
                "anxiety during menopause vs general anxiety differences",
                "hair thinning during menopause what helps",
                "weight distribution changes during menopause",
                "skin changes during menopause care routine adjustments",
                "digestive changes bloating during menopause",
                "sleep disruption beyond night sweats menopause insomnia"
            ],
            "nutrition": [
                "foods that help balance hormones naturally during menopause",
                "calcium and bone health critical during menopause",
                "phytoestrogen foods and their actual impact",
                "anti-inflammatory eating for menopause symptom relief",
                "menopause and gut health the important connection",
                "sugar and caffeine impact on menopause symptoms",
                "protein needs increase during menopause",
                "omega 3 benefits specifically for menopause",
                "iron needs change during and after menopause",
                "hydration and its role in managing hot flashes"
            ],
            "wellness": [
                "yoga poses specifically for menopause symptom relief",
                "strength training importance during menopause for bone density",
                "walking benefits for menopause mood and weight",
                "meditation and mindfulness for menopause anxiety",
                "sleep hygiene routine for night sweats and insomnia",
                "pelvic floor exercises importance during menopause",
                "breathing techniques for hot flash management",
                "journaling prompts for processing menopause emotions",
                "social connection importance during menopause transition",
                "creativity and hobbies for menopause mental health"
            ],
            "planning": [
                "tracking symptoms to identify patterns and triggers",
                "preparing for doctor appointments about menopause",
                "creating a menopause management plan",
                "workplace strategies for managing symptoms",
                "travel tips for managing menopause symptoms",
                "relationship communication during menopause",
                "financial planning for menopause related health costs",
                "building a menopause support network",
                "when to consider HRT conversation guide for doctors",
                "perimenopause vs menopause knowing where you are"
            ],
            "mental_health": [
                "menopause grief mourning fertility and youth",
                "identity shifts during menopause finding yourself again",
                "menopause and depression when to seek help",
                "body image during menopause self compassion practices",
                "menopause rage understanding sudden anger",
                "loneliness during menopause building connection",
                "menopause and self esteem rebuilding confidence",
                "setting boundaries during menopause low energy times",
                "celebrating menopause reframing the narrative",
                "partner support during menopause what actually helps"
            ]
        },

        "seo_keywords": [
            "menopause symptoms relief", "perimenopause tips", "hot flash remedies natural",
            "menopause weight gain", "hormone balance naturally", "menopause planner",
            "menopause self care", "night sweats solutions", "menopause supplements",
            "perimenopause symptoms", "menopause anxiety help", "menopause sleep",
            "menopause nutrition", "menopause brain fog", "menopause support"
        ],

        "hashtags": [
            "#menopausesupport", "#perimenopause", "#menopauserelief", "#hormonebalance",
            "#menopausewellness", "#hotflashrelief", "#menopausetips", "#womenover45"
        ],

        "destination_base_url": "https://menopauseplanner.netlify.app",
        "pinterest_boards": [
            "Menopause Symptoms & Relief",
            "Hormone Balance Naturally",
            "Menopause Self Care",
            "Perimenopause Tips & Support",
            "Menopause Nutrition & Wellness"
        ]
    }
}


# ═══════════════════════════════════════════════════════════════
# CONTENT GENERATION ENGINE
# ═══════════════════════════════════════════════════════════════

# Visual template styles — ordered by Pinterest engagement (highest first)
# Bold text overlays, before/after, lists, and infographics drive the most saves and clicks
PIN_VISUAL_STYLES = [
    {
        "name": "bold_text_overlay",
        "description": "Full-width image with semi-transparent dark gradient overlay. LARGE white bold sans-serif title text (fills 40% of frame). Subtitle line below in smaller font. High contrast, impossible to scroll past.",
        "creatomate_template": "TEMPLATE_ID_1",
        "engagement_weight": 5  # Highest engagement on Pinterest
    },
    {
        "name": "numbered_list_teaser",
        "description": "Shows 2-3 items from a list with clear numbers (1, 2, 3...) and a 'See all X...' teaser at bottom. Each item has a small icon or image. Creates incompleteness that demands a click.",
        "creatomate_template": "TEMPLATE_ID_5",
        "engagement_weight": 5  # Lists drive massive saves
    },
    {
        "name": "before_after_split",
        "description": "Vertical split or top/bottom comparison. Left or top shows 'before' (problem state), right or bottom shows 'after' (result). Clear divider line. Bold label text on each side. Dramatic visual contrast.",
        "creatomate_template": "TEMPLATE_ID_6",
        "engagement_weight": 4  # Before/after is highly clickable
    },
    {
        "name": "infographic_stat",
        "description": "Large bold number or statistic takes 40% of frame (e.g., '87%', '3x', '14 days'). Short impactful phrase next to it. Clean background. Data-driven authority look.",
        "creatomate_template": "TEMPLATE_ID_3",
        "engagement_weight": 4  # Stats build trust and saves
    },
    {
        "name": "editorial_magazine",
        "description": "Magazine cover layout. Hero image with elegant text overlay. Brand color accent bar at top or bottom. Looks premium and editorial. Serif font for headline, sans-serif for subtitle.",
        "creatomate_template": "TEMPLATE_ID_4",
        "engagement_weight": 3
    },
    {
        "name": "split_color_block",
        "description": "Top 60% lifestyle image, bottom 40% solid brand-color block with title in contrasting text. Color rotates: deep teal, warm coral, navy, sage green, dusty rose. Clean and scroll-stopping.",
        "creatomate_template": "TEMPLATE_ID_2",
        "engagement_weight": 3
    },
    {
        "name": "step_by_step",
        "description": "3-4 numbered steps shown as a mini visual guide. Each step has an icon and short text. 'Full guide at link' footer. Tutorial format that drives clicks for the complete version.",
        "creatomate_template": "TEMPLATE_ID_7",
        "engagement_weight": 4  # How-to content drives clicks
    }
]

# Description opening styles — rotate to prevent sameness
# Each has an SEO instruction: front-load keywords in first 50 characters
DESCRIPTION_OPENERS = [
    "question",        # "Ever wonder why [keyword]..." — hooks curiosity
    "bold_claim",      # "[Keyword topic] changed everything about..." — authority
    "statistic",       # "87% of [audience keyword]..." — credibility + specificity
    "personal_story",  # "When I started [keyword activity]..." — relatability
    "myth_bust",       # "Forget what you heard about [keyword]..." — pattern interrupt
    "confession",      # "I was skeptical about [keyword] until..." — authenticity
    "contrast",        # "Most people [keyword mistake]. The ones who see results..." — intrigue
    "time_hook",       # "In just [timeframe], [keyword benefit]..." — urgency
    "pain_point",      # "Tired of [keyword frustration]? Here's what actually..." — empathy
    "secret_reveal"    # "The [keyword] secret that [experts/pros] use..." — exclusivity
]

# ═══════════════════════════════════════════════════════════════
# TOPIC-TO-BOARD MAPPING (deterministic board selection by category)
# ═══════════════════════════════════════════════════════════════

TOPIC_TO_BOARD_MAP = {
    "fitness": {
        "workouts": "Workouts for Men Over 35",
        "nutrition": "Meal Prep & Nutrition",
        "supplements": "Supplement Honest Reviews",
        "fat_loss": "Fat Loss After 35",
        "lifestyle": "Fitness Motivation",
        "_default": "Home Gym Ideas"
    },
    "deals": {
        "kitchen": "Kitchen Must-Haves",
        "home_decor": "Budget Home Decor",
        "organization": "Home Organization Finds",
        "self_care": "Self Care Products Worth It",
        "seasonal": "Seasonal Favorites",
        "_default": "Gift Ideas"
    },
    "menopause": {
        "symptoms": "Menopause Symptoms & Relief",
        "nutrition": "Menopause Nutrition & Wellness",
        "wellness": "Menopause Self Care",
        "planning": "Perimenopause Tips & Support",
        "mental_health": "Hormone Balance Naturally",
        "_default": "Menopause Symptoms & Relief"
    }
}


def _get_board_for_topic(brand_key, category):
    """Get the best board for a given topic category.

    Uses deterministic mapping by category, but when a category maps to
    a lower-priority board, occasionally promotes to a higher-follower
    board if the content is relevant. Board priority lists are ordered
    by follower count (highest first).
    """
    brand_map = TOPIC_TO_BOARD_MAP.get(brand_key, {})
    return brand_map.get(category, brand_map.get('_default', BRAND_CONFIGS[brand_key]['pinterest_boards'][0]))


def _select_visual_style_weighted(recent_styles):
    """Select a visual style weighted by engagement, avoiding recent repeats.

    Higher engagement_weight styles are selected more often but still rotate
    to prevent feed fatigue.
    """
    available = [s for s in PIN_VISUAL_STYLES if s['name'] not in recent_styles]
    if not available:
        available = PIN_VISUAL_STYLES

    # Build weighted pool: each style appears N times based on engagement_weight
    weighted_pool = []
    for style in available:
        weight = style.get('engagement_weight', 3)
        weighted_pool.extend([style] * weight)

    return random.choice(weighted_pool)


def generate_pin_content(brand_key, supabase_client):
    """Generate a complete, UNIQUE pin for the specified brand.

    Returns dict with title, description, image_query, visual_style,
    board, destination_url, text_overlay, and metadata.
    """
    config = BRAND_CONFIGS[brand_key]

    # ── Step 1: Check what was recently used to ensure variety ──
    try:
        recent = supabase_client.table('content_history') \
            .select('topic, angle_framework, visual_style, board, description_opener, image_query, title') \
            .eq('brand', brand_key) \
            .order('created_at', desc=True) \
            .limit(30) \
            .execute()
        recent_data = recent.data if recent.data else []
    except Exception:
        recent_data = []

    recent_topics = [r.get('topic', '') for r in recent_data[:25]]
    recent_angles = [r.get('angle_framework', '') for r in recent_data[:5]]
    recent_styles = [r.get('visual_style', '') for r in recent_data[:4]]
    recent_boards = [r.get('board', '') for r in recent_data[:3]]
    recent_openers = [r.get('description_opener', '') for r in recent_data[:5]]
    recent_image_queries = [r.get('image_query', '') for r in recent_data[:25]]
    recent_titles = [r.get('title', '') for r in recent_data[:20]]

    # ── Step 2: Select topic (not used in last 25 pins) ──
    all_topics = []
    for category, topics in config['topics_by_category'].items():
        for topic in topics:
            all_topics.append({"category": category, "topic": topic})

    available_topics = [t for t in all_topics if t['topic'] not in recent_topics]
    if not available_topics:
        available_topics = all_topics  # Reset if all used

    selected_topic = random.choice(available_topics)

    # ── Step 3: Select angle framework (not used in last 5 pins) ──
    available_angles = [a for a in config['hook_frameworks'] if a not in recent_angles]
    if not available_angles:
        available_angles = config['hook_frameworks']
    selected_angle = random.choice(available_angles)

    # ── Step 4: Select visual style (weighted by engagement, avoid last 4) ──
    selected_style = _select_visual_style_weighted(recent_styles)

    # ── Step 5: Select board (deterministic mapping by topic category) ──
    selected_board = _get_board_for_topic(brand_key, selected_topic['category'])

    # ── Step 6: Select description opener (not used in last 5 pins) ──
    available_openers = [o for o in DESCRIPTION_OPENERS if o not in recent_openers]
    if not available_openers:
        available_openers = DESCRIPTION_OPENERS
    selected_opener = random.choice(available_openers)

    # ── Step 7: Select SEO keywords (pick 4-5 random ones) ──
    selected_keywords = random.sample(config['seo_keywords'], min(5, len(config['seo_keywords'])))

    # ── Step 7b: Get brand hashtags ──
    brand_hashtags = config.get('hashtags', [])
    selected_hashtags = random.sample(brand_hashtags, min(6, len(brand_hashtags))) if brand_hashtags else []

    # ── Step 7c: Get affiliate products relevant to this topic's category ──
    affiliate_products = config.get('affiliate_products', {})
    category_products = affiliate_products.get(selected_topic['category'], [])
    # Also pull from a random related category for variety
    all_product_cats = list(affiliate_products.keys())
    if all_product_cats:
        bonus_cat = random.choice(all_product_cats)
        category_products = category_products + affiliate_products.get(bonus_cat, [])[:2]

    # ── Step 8: Call Claude to generate the content ──
    prompt = f"""You are creating a Pinterest pin for the brand "{config['name']}".
Your SOLE OBJECTIVE: maximize clicks, saves, and affiliate revenue on Pinterest.

═══ YOUR VOICE/PERSONA ═══
{config['voice']}

═══ TODAY'S TOPIC ═══
{selected_topic['topic']} (category: {selected_topic['category']})

═══ HOOK FRAMEWORK ═══
Adapt this framework creatively (do NOT copy it word-for-word):
{selected_angle}

═══ TITLE RULES (CRITICAL — this determines if anyone clicks) ═══
Your title MUST:
- Be 40-60 characters (optimal Pinterest display length, HARD LIMIT 70 chars)
- Create an irresistible CURIOSITY GAP — the reader MUST click to satisfy their curiosity
- Use ONE of these proven Pinterest title patterns:
  * "[Number] Things That [Outcome] (#[X] Surprised Me)"
  * "Stop [Mistake] — Do This Instead"
  * "I Tried [Thing] for [Time] — Here's What Happened"
  * "The [Adjective] [Thing] That [Result] (Most People Don't Know)"
  * "Why [Common Thing] Is [Secretly Bad] (And the Fix)"
- Include at least ONE power word: secret, proven, simple, essential, surprising, honest, finally, actually
- NEVER be generic. "Healthy Meal Prep Tips" = TERRIBLE. "The $2 Meal Prep Trick I Use Every Sunday" = GREAT.
- NEVER give away the answer. Tease the outcome, withhold the method.

═══ DESCRIPTION RULES (SEO + click-through) ═══
Opening style: {selected_opener}
- "question" = Hook with a question about [keyword topic]
- "bold_claim" = Confident specific claim starting with [keyword]
- "statistic" = Number/percentage about [keyword audience]
- "personal_story" = "I" / "When I" + [keyword activity]
- "myth_bust" = Challenge a common belief about [keyword]
- "confession" = Honest skepticism about [keyword] until...
- "contrast" = Most people [keyword mistake] vs what works
- "time_hook" = "[Timeframe] + [keyword benefit]" urgency
- "pain_point" = "Tired of [keyword frustration]? Here's what actually..."
- "secret_reveal" = "The [keyword] secret that [pros] use..."

DESCRIPTION REQUIREMENTS:
1. FIRST 50 CHARACTERS must contain your primary SEO keyword (front-load for search)
2. Total length: 150-300 characters (before hashtags)
3. Weave in 3-5 of these keywords naturally: {', '.join(selected_keywords)}
4. Include an EMOTIONAL TRIGGER relevant to the audience:
   - Fitness: urgency about health, pride in transformation, fear of wasted effort
   - Deals: FOMO on savings, satisfaction of smart buying, joy of a great find
   - Menopause: validation and relief, hope for improvement, "you're not alone"
5. End with a compelling CTA: "Click for the full guide" / "Save this — you'll need it" / "Full breakdown at the link"
6. After the CTA, on a NEW LINE, append 5-8 hashtags: {' '.join(selected_hashtags)}
7. If a product naturally fits, mention its BENEFIT (not just the name): "the cooling pillow that actually stopped my night sweats" not "cooling pillow"

═══ AFFILIATE PRODUCT INTEGRATION ═══
If the topic naturally relates to any of these products, weave ONE into the description with a benefit-driven mention.
Do NOT force it — only include if genuinely relevant to the topic.
Available products for this brand: {', '.join(category_products) if category_products else 'none for this category'}
GOOD example: "This $15 foam roller fixed my hip pain better than 3 PT sessions"
BAD example: "Check out this foam roller"

═══ VISUAL STYLE ═══
{selected_style['name']} — {selected_style['description']}

═══ RECENTLY USED (yours MUST be completely different) ═══
Recent titles:
{chr(10).join(recent_titles[:10]) if recent_titles else 'None yet'}

Recent image queries:
{chr(10).join(recent_image_queries[:10]) if recent_image_queries else 'None yet'}

═══ IMAGE + OVERLAY RULES ═══
- Image search query: SPECIFIC and VIVID — not "man exercising" but "close up muscular forearms gripping barbell gym dramatic side lighting"
- Query must match THIS topic specifically, not be generic stock photo terms
- Text overlay: 3-8 words max that capture the pin's core hook in large bold readable font
- Alt text: brief accessible description for screen readers

═══ BANNED PHRASES ═══
Never use: "unlock", "transform your", "game-changer", "must-have", "you won't believe", "amazing", "incredible", "life-changing", "revolutionary", "ultimate guide"

OUTPUT ONLY THIS JSON (no markdown, no backticks, no explanation):
{{
    "title": "...",
    "description": "...",
    "image_search_query": "...",
    "text_overlay": "...",
    "alt_text": "..."
}}"""

    response = _get_client().messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.content[0].text.strip()

    # Parse the JSON response
    try:
        pin_data = json.loads(content)
    except json.JSONDecodeError:
        # Try to extract JSON if Claude added extra text
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            pin_data = json.loads(json_match.group())
        else:
            raise ValueError(f"Claude did not return valid JSON: {content[:200]}")

    # ── Step 9: Add metadata ──
    pin_data['brand'] = brand_key
    pin_data['topic'] = selected_topic['topic']
    pin_data['category'] = selected_topic['category']
    pin_data['angle_framework'] = selected_angle
    pin_data['visual_style'] = selected_style['name']
    pin_data['creatomate_template'] = selected_style['creatomate_template']
    pin_data['board'] = selected_board
    pin_data['description_opener'] = selected_opener
    pin_data['destination_url'] = config['destination_base_url']
    pin_data['keywords_used'] = selected_keywords

    return pin_data


def log_pin_to_history(pin_data, supabase_client):
    """Log generated pin to content_history for variety tracking."""
    try:
        supabase_client.table('content_history').insert({
            'brand': pin_data['brand'],
            'title': pin_data['title'],
            'description': pin_data['description'],
            'topic': pin_data['topic'],
            'category': pin_data['category'],
            'angle_framework': pin_data['angle_framework'],
            'visual_style': pin_data['visual_style'],
            'board': pin_data['board'],
            'description_opener': pin_data['description_opener'],
            'image_query': pin_data.get('image_search_query', ''),
            'pexels_image_id': pin_data.get('pexels_image_id', ''),
            'destination_url': pin_data.get('destination_url', ''),
            'posting_method': pin_data.get('posting_method', ''),
            'created_at': datetime.now(timezone.utc).isoformat()
        }).execute()
    except Exception as e:
        logger.error(f"Failed to log pin to history: {e}")


def generate_pin_from_calendar(brand_key, supabase_client):
    """Generate a pin based on today's assignment from the weekly calendar.

    Falls back to the original random topic selection if no calendar exists.
    """
    today = datetime.now(timezone.utc).strftime('%A')  # "Monday", "Tuesday", etc.
    today_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    # Get the current week's calendar
    try:
        calendar_result = supabase_client.table('weekly_calendar') \
            .select('calendar_data') \
            .eq('brand', brand_key) \
            .order('created_at', desc=True) \
            .limit(1) \
            .execute()
    except Exception:
        calendar_result = None

    if not calendar_result or not calendar_result.data:
        print(f"No weekly calendar found for {brand_key}. Using random topic selection.")
        return generate_pin_content(brand_key, supabase_client)

    cal_raw = calendar_result.data[0]['calendar_data']
    calendar = json.loads(cal_raw) if isinstance(cal_raw, str) else cal_raw

    # Find today's pin assignments
    today_pins = []
    for day in calendar.get('days', []):
        if day.get('day', '').lower() == today.lower():
            today_pins = day.get('pins', [])
            break

    if not today_pins:
        print(f"No pins scheduled for {today} in {brand_key} calendar. Using random topic.")
        return generate_pin_content(brand_key, supabase_client)

    # Find which pin slot to fill (check what's already been posted today)
    try:
        today_posts = supabase_client.table('content_history') \
            .select('trending_topic') \
            .eq('brand', brand_key) \
            .gte('created_at', today_date + 'T00:00:00Z') \
            .execute()
        posted_count = len(today_posts.data) if today_posts.data else 0
    except Exception:
        posted_count = 0

    if posted_count >= len(today_pins):
        print(f"All {len(today_pins)} pins for {today} already posted for {brand_key}.")
        return None  # All done for today

    # Get the next unposted pin assignment
    pin_assignment = today_pins[posted_count]

    # Build the destination URL with the matching article
    article_slug = pin_assignment.get('article_slug', '')
    config = BRAND_CONFIGS[brand_key]
    base_url = config['destination_base_url']

    if article_slug and base_url != 'NEEDS_LANDING_PAGE':
        destination_url = f"{base_url}/articles/{article_slug}/"
    elif base_url == 'NEEDS_LANDING_PAGE':
        destination_url = "https://linktr.ee/menopauseplanner"
    else:
        destination_url = base_url

    # Get recent pins for uniqueness check
    try:
        recent = supabase_client.table('content_history') \
            .select('title, description, image_query, visual_style') \
            .eq('brand', brand_key) \
            .order('created_at', desc=True) \
            .limit(20) \
            .execute()
        recent_data = recent.data or []
    except Exception:
        recent_data = []

    recent_titles = [r.get('title', '') for r in recent_data]

    # Select visual style (weighted by engagement, rotate to avoid repeats)
    recent_styles = [r.get('visual_style', '') for r in recent_data[:4]]
    selected_style = _select_visual_style_weighted(recent_styles)

    # Select SEO keywords
    selected_keywords = random.sample(config['seo_keywords'], min(5, len(config['seo_keywords'])))

    # Select hashtags
    brand_hashtags = config.get('hashtags', [])
    selected_hashtags = random.sample(brand_hashtags, min(6, len(brand_hashtags))) if brand_hashtags else []

    # Select description opener (rotate)
    recent_openers = [r.get('description_opener', '') for r in recent_data[:5]]
    available_openers = [o for o in DESCRIPTION_OPENERS if o not in recent_openers]
    if not available_openers:
        available_openers = DESCRIPTION_OPENERS
    selected_opener = random.choice(available_openers)

    # Get affiliate products for this brand
    affiliate_products = config.get('affiliate_products', {})
    all_products = []
    for cat_products in affiliate_products.values():
        all_products.extend(cat_products)
    sample_products = random.sample(all_products, min(5, len(all_products))) if all_products else []

    # Call Claude with the specific calendar assignment
    prompt = f"""You are creating a Pinterest pin for "{config['name']}".
Your SOLE OBJECTIVE: maximize clicks, saves, and affiliate revenue on Pinterest.

═══ YOUR VOICE ═══
{config['voice']}

═══ CALENDAR ASSIGNMENT ═══
- Trending Topic: {pin_assignment.get('trending_topic', 'general')}
- Suggested Title: {pin_assignment.get('title', 'create your own')}
- Description Concept: {pin_assignment.get('description_concept', '')}
- Pin Type: {pin_assignment.get('pin_type', 'static_image')}
- Target Board: {pin_assignment.get('board', config['pinterest_boards'][0])}

The suggested title is a STARTING POINT. You MUST improve it using the title rules below.

═══ TITLE RULES (CRITICAL — determines if anyone clicks) ═══
- MUST be 40-60 characters (optimal Pinterest display, HARD LIMIT 70 chars)
- MUST create an irresistible CURIOSITY GAP — reader cannot resist clicking
- Use ONE proven Pinterest pattern:
  * "[Number] Things That [Outcome] (#[X] Surprised Me)"
  * "Stop [Mistake] — Do This Instead"
  * "I Tried [Thing] for [Time] — Here's What Happened"
  * "The [Adjective] [Thing] That [Result] (Most People Don't Know)"
- Include a power word: secret, proven, simple, essential, surprising, honest, finally, actually
- NEVER generic. NEVER give away the answer. Tease outcome, withhold method.

═══ DESCRIPTION RULES ═══
Opening style: {selected_opener}
- "question" = Hook with question about [keyword]
- "bold_claim" = Confident claim starting with [keyword]
- "statistic" = Number about [keyword audience]
- "personal_story" = "I/When I" + [keyword]
- "myth_bust" = Challenge belief about [keyword]
- "confession" = Honest skepticism about [keyword]
- "contrast" = Most people [keyword mistake] vs what works
- "time_hook" = "[Timeframe] + [keyword benefit]"
- "pain_point" = "Tired of [keyword frustration]?"
- "secret_reveal" = "The [keyword] secret that [pros] use"

Requirements:
1. FIRST 50 CHARACTERS must contain primary SEO keyword
2. Length: 150-300 chars before hashtags
3. Include 3-5 keywords: {', '.join(selected_keywords)}
4. Include EMOTIONAL TRIGGER for this audience (urgency, FOMO, relief, validation)
5. End with CTA: "Click for the full guide" / "Save this" / "Full breakdown at the link"
6. NEW LINE after CTA with 5-8 hashtags: {' '.join(selected_hashtags)}
7. If a product fits, mention its BENEFIT not just its name

═══ AFFILIATE PRODUCTS (only if naturally relevant) ═══
{', '.join(sample_products) if sample_products else 'none available'}

═══ VISUAL STYLE ═══
{selected_style['name']} — {selected_style['description']}

═══ DESTINATION URL ═══
{destination_url}

═══ RECENTLY USED TITLES (yours must be completely different) ═══
{chr(10).join(recent_titles[:10]) if recent_titles else 'None yet'}

═══ BANNED PHRASES ═══
Never use: "unlock", "transform your", "game-changer", "must-have", "you won't believe", "amazing", "incredible", "life-changing", "revolutionary", "ultimate guide"

═══ IMAGE + OVERLAY ═══
- Image query: SPECIFIC and VIVID (not generic stock terms)
- Text overlay: 3-8 impactful words for large bold font
- Alt text: brief accessible description

OUTPUT ONLY THIS JSON:
{{
    "title": "...",
    "description": "...",
    "image_search_query": "...",
    "text_overlay": "...",
    "alt_text": "..."
}}"""

    response = _get_client().messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.content[0].text.strip()

    try:
        pin_data = json.loads(content)
    except json.JSONDecodeError:
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            pin_data = json.loads(json_match.group())
        else:
            print(f"Calendar pin parse error, falling back to random topic.")
            return generate_pin_content(brand_key, supabase_client)

    # Add metadata
    pin_data['brand'] = brand_key
    pin_data['topic'] = pin_assignment.get('trending_topic', '')
    pin_data['trending_topic'] = pin_assignment.get('trending_topic', '')
    pin_data['category'] = 'trending'
    pin_data['angle_framework'] = pin_assignment.get('title', '')
    pin_data['visual_style'] = selected_style['name']
    pin_data['creatomate_template'] = selected_style['creatomate_template']
    pin_data['board'] = pin_assignment.get('board', config['pinterest_boards'][0])
    pin_data['description_opener'] = selected_opener
    pin_data['destination_url'] = destination_url
    pin_data['keywords_used'] = selected_keywords
    pin_data['calendar_driven'] = True

    return pin_data


def build_destination_url(base_url, brand, posting_method, campaign="pins",
                         topic_slug="", board_name=""):
    """Build destination URL with UTM tracking parameters.

    Includes topic_slug in utm_content for pin-level tracking and
    utm_term with board_name for board-level analytics.
    """
    if base_url == "NEEDS_LANDING_PAGE":
        base_url = "https://menopauseplanner.netlify.app"

    separator = '&' if '?' in base_url else '?'
    # Include topic slug in utm_content for pin-level tracking
    date_str = datetime.now(timezone.utc).strftime('%Y%m%d')
    utm_content = f"{topic_slug}_{date_str}" if topic_slug else date_str
    # Sanitize board name for URL
    utm_term = board_name.lower().replace(' ', '-').replace('&', 'and') if board_name else ''
    url = (
        f"{base_url}{separator}"
        f"utm_source=pinterest&"
        f"utm_medium={posting_method}&"
        f"utm_campaign={brand}_{campaign}&"
        f"utm_content={utm_content}"
    )
    if utm_term:
        url += f"&utm_term={utm_term}"
    return url
