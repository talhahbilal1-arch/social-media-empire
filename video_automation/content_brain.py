"""Claude-powered content brain for all 3 Pinterest brands.

Generates unique, high-quality pin content using Claude API (Sonnet 4.5).
Tracks content history in Supabase to ensure variety across topics, angles,
visual styles, boards, and description openers.

Replaces all Gemini-based content generation.
"""

import anthropic
import json
import random
import os
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))

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
            "The {specific} mistake that's killing your {goal} after 35",
            "I {did_specific_thing} for {timeframe} — here's what happened to my {body_part/metric}",
            "{Thing_A} vs {Thing_B}: which actually works for men over 35",
            "The one {exercise/food/supplement} that changed my {result} at {age}",
            "Stop doing {common_thing} if you're over 35 (here's what to do instead)",
            "Why {commonly_accepted_thing} is actually {bad_outcome} after 35",
            "{Number} {things} I wish I knew about {topic} before turning 35",
            "My {body_part} transformation: what {timeframe} of {specific_action} actually looks like",
            "The {time_of_day} habit that {specific_benefit} (backed by research)",
            "I asked my doctor about {supplement/practice} at 37 — his answer surprised me",
            "What nobody tells you about {fitness_topic} in your late 30s",
            "The {cheap/free thing} that outperformed my ${expensive_thing} for {goal}",
            "{Food/Exercise} is overhyped for men over 35 — here's what actually works",
            "I tracked my {metric} for {timeframe} — the pattern was eye-opening"
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
            "This ${price} {product} replaced my ${expensive_price} {expensive_thing}",
            "The {room} upgrade that gets the most compliments (under ${price})",
            "I've tried {number} {product_category} — this is the one I actually kept",
            "My most-used {category} find this {season}",
            "{Number} {products} that look expensive but cost under ${price}",
            "The {product} my {person} won't stop asking me about",
            "Honest unboxing: the {product} everyone on {platform} is talking about",
            "Why I returned {popular_product} and bought this {alternative} instead",
            "The {product} I've repurchased {number} times (it's that good)",
            "{Room} before and after with only ${budget} in new finds",
            "Things I stopped buying name brand and the dupes that are better",
            "The {season} home refresh I did for under ${budget}",
            "What I actually use daily vs what collected dust — honest list",
            "The {product} that solved my biggest {room/task} frustration"
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
            "The {symptom} hack my gynecologist told me that changed everything",
            "What finally helped my {symptom} after trying everything else",
            "{Number} signs your {symptom} might be related to {perimenopause/menopause}",
            "The {supplement/food/habit} that improved my {symptom} within {timeframe}",
            "Why the usual advice for {symptom} makes it worse (and what to do instead)",
            "I tracked my {symptoms} for {timeframe} — the pattern I found was surprising",
            "The {time_of_day} routine that finally helped me {benefit}",
            "What I wish someone had told me about {menopause_topic} years earlier",
            "The difference between {perimenopause_thing} and {menopause_thing} explained simply",
            "{Common_menopause_advice} is outdated — here's what doctors say now",
            "My honest experience with {treatment/supplement} for {symptom}",
            "The {free/simple} thing that helped my {symptom} more than anything expensive",
            "How I explained {menopause_topic} to my {partner/family} (and it helped)",
            "{Number} small changes that made the biggest difference in my {symptom}"
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

        "destination_base_url": "NEEDS_LANDING_PAGE",
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

# Visual template styles — rotate to prevent sameness
PIN_VISUAL_STYLES = [
    {
        "name": "bold_dark_overlay",
        "description": "Full-width image with semi-transparent dark overlay, large white bold text centered",
        "creatomate_template": "TEMPLATE_ID_1"
    },
    {
        "name": "split_layout",
        "description": "Top 60% image, bottom 40% solid color block with title. Color rotates: deep teal, warm coral, navy, sage green, dusty rose",
        "creatomate_template": "TEMPLATE_ID_2"
    },
    {
        "name": "minimal_number",
        "description": "Large number or statistic takes 40% of frame, short phrase next to it, clean image background",
        "creatomate_template": "TEMPLATE_ID_3"
    },
    {
        "name": "editorial_magazine",
        "description": "Magazine-style layout with image and text arranged like a editorial spread. Clean, sophisticated.",
        "creatomate_template": "TEMPLATE_ID_4"
    },
    {
        "name": "list_teaser",
        "description": "Shows 2-3 items partially visible with 'See all X...' teaser. Implies more behind the click.",
        "creatomate_template": "TEMPLATE_ID_5"
    }
]

# Description opening styles — rotate to prevent sameness
DESCRIPTION_OPENERS = [
    "question",       # "Ever wonder why..."
    "bold_claim",     # "This changed everything about..."
    "statistic",      # "87% of men over 35..."
    "personal_story", # "When I started..."
    "myth_bust",      # "Forget what you've heard about..."
    "confession",     # "I'll be honest — I was skeptical about..."
    "contrast",       # "Most people do X. But the ones who get results..."
    "time_hook"       # "In the next 30 days..."
]


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

    recent_topics = [r.get('topic', '') for r in recent_data[:10]]
    recent_angles = [r.get('angle_framework', '') for r in recent_data[:5]]
    recent_styles = [r.get('visual_style', '') for r in recent_data[:4]]
    recent_boards = [r.get('board', '') for r in recent_data[:3]]
    recent_openers = [r.get('description_opener', '') for r in recent_data[:5]]
    recent_image_queries = [r.get('image_query', '') for r in recent_data[:15]]
    recent_titles = [r.get('title', '') for r in recent_data[:20]]

    # ── Step 2: Select topic (not used in last 10 pins) ──
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

    # ── Step 4: Select visual style (not used in last 4 pins) ──
    available_styles = [s for s in PIN_VISUAL_STYLES if s['name'] not in recent_styles]
    if not available_styles:
        available_styles = PIN_VISUAL_STYLES
    selected_style = random.choice(available_styles)

    # ── Step 5: Select board (not used in last 3 pins) ──
    available_boards = [b for b in config['pinterest_boards'] if b not in recent_boards]
    if not available_boards:
        available_boards = config['pinterest_boards']
    selected_board = random.choice(available_boards)

    # ── Step 6: Select description opener (not used in last 5 pins) ──
    available_openers = [o for o in DESCRIPTION_OPENERS if o not in recent_openers]
    if not available_openers:
        available_openers = DESCRIPTION_OPENERS
    selected_opener = random.choice(available_openers)

    # ── Step 7: Select SEO keywords (pick 4-5 random ones) ──
    selected_keywords = random.sample(config['seo_keywords'], min(5, len(config['seo_keywords'])))

    # ── Step 8: Call Claude to generate the content ──
    prompt = f"""You are creating a Pinterest pin for the brand "{config['name']}".

YOUR VOICE/PERSONA:
{config['voice']}

TODAY'S TOPIC: {selected_topic['topic']} (category: {selected_topic['category']})

HOOK FRAMEWORK TO USE (adapt creatively, don't copy the template literally):
{selected_angle}

DESCRIPTION MUST OPEN WITH THIS STYLE: {selected_opener}
- "question" = Start with a question that hooks the reader
- "bold_claim" = Start with a confident, specific claim
- "statistic" = Start with a number or percentage (can be approximate/general)
- "personal_story" = Start with "I" or "When I" sharing brief personal experience
- "myth_bust" = Start by challenging a common belief
- "confession" = Start with honest admission of skepticism or surprise
- "contrast" = Start by contrasting what most people do vs what works
- "time_hook" = Start with a timeframe that creates urgency

SEO KEYWORDS TO NATURALLY INCLUDE (use 3-5 in description):
{', '.join(selected_keywords)}

VISUAL STYLE FOR THIS PIN: {selected_style['name']} — {selected_style['description']}

RECENTLY USED TITLES (your title MUST be completely different from all of these):
{chr(10).join(recent_titles[:10]) if recent_titles else 'None yet'}

RECENTLY USED IMAGE QUERIES (your image query MUST be different):
{chr(10).join(recent_image_queries[:10]) if recent_image_queries else 'None yet'}

RULES:
1. Title MUST create a curiosity gap — viewer NEEDS to click to get the answer
2. Title must be under 100 characters
3. NEVER give away the complete answer in the pin title or description
4. Description must be 150-300 characters, conversational, with keywords woven in naturally
5. Description must end with a soft CTA (not "BUY NOW" — more like "Full guide at the link" or "More at fitover35.com")
6. Image search query must be SPECIFIC and DETAILED — not "man exercising" but "close up muscular forearms gripping barbell gym dramatic lighting"
7. Image query should match this pin's specific topic, not be generic
8. Text overlay should be 3-8 words max, large readable font, that captures the pin's core hook
9. EVERYTHING must feel written by a real human, not an AI content mill
10. NO generic phrases: "unlock", "transform", "game-changer", "must-have", "you won't believe"

OUTPUT ONLY THIS JSON (no markdown, no backticks, no explanation):
{{
    "title": "...",
    "description": "...",
    "image_search_query": "...",
    "text_overlay": "...",
    "alt_text": "Brief accessible description of what the pin image should show"
}}"""

    response = client.messages.create(
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
            'created_at': datetime.utcnow().isoformat()
        }).execute()
    except Exception as e:
        logger.error(f"Failed to log pin to history: {e}")


def generate_pin_from_calendar(brand_key, supabase_client):
    """Generate a pin based on today's assignment from the weekly calendar.

    Falls back to the original random topic selection if no calendar exists.
    """
    today = datetime.utcnow().strftime('%A')  # "Monday", "Tuesday", etc.
    today_date = datetime.utcnow().strftime('%Y-%m-%d')

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

    # Select visual style (rotate)
    recent_styles = [r.get('visual_style', '') for r in recent_data[:4]]
    available_styles = [s for s in PIN_VISUAL_STYLES if s['name'] not in recent_styles]
    if not available_styles:
        available_styles = PIN_VISUAL_STYLES
    selected_style = random.choice(available_styles)

    # Select SEO keywords
    selected_keywords = random.sample(config['seo_keywords'], min(5, len(config['seo_keywords'])))

    # Select description opener (rotate)
    recent_openers = [r.get('description_opener', '') for r in recent_data[:5]]
    available_openers = [o for o in DESCRIPTION_OPENERS if o not in recent_openers]
    if not available_openers:
        available_openers = DESCRIPTION_OPENERS
    selected_opener = random.choice(available_openers)

    # Call Claude with the specific calendar assignment
    prompt = f"""You are creating a Pinterest pin for "{config['name']}".

YOUR VOICE: {config['voice']}

THIS PIN'S ASSIGNMENT FROM THE WEEKLY CALENDAR:
- Trending Topic: {pin_assignment.get('trending_topic', 'general')}
- Suggested Title: {pin_assignment.get('title', 'create your own')}
- Description Concept: {pin_assignment.get('description_concept', '')}
- Pin Type: {pin_assignment.get('pin_type', 'static_image')}
- Target Board: {pin_assignment.get('board', config['pinterest_boards'][0])}

The suggested title is a starting point. Improve it or create a different angle on the same trending topic. It must create a curiosity gap.

DESCRIPTION MUST OPEN WITH THIS STYLE: {selected_opener}
VISUAL STYLE FOR THIS PIN: {selected_style['name']} — {selected_style['description']}
SEO KEYWORDS TO INCLUDE (3-5 naturally): {', '.join(selected_keywords)}
DESTINATION URL: {destination_url}

RECENTLY USED TITLES (yours must be completely different):
{chr(10).join(recent_titles[:10]) if recent_titles else 'None yet'}

RULES:
1. Title creates a CURIOSITY GAP — viewer must click to get the answer (max 100 chars)
2. Description is 150-300 chars, conversational, keyword-rich, ends with soft CTA
3. Image search query is SPECIFIC and DETAILED (not generic stock photo terms)
4. Text overlay is 3-8 words, large readable font
5. Everything must feel human-written, not AI-generated
6. NO generic phrases: "unlock", "transform", "game-changer", "must-have"

OUTPUT ONLY THIS JSON:
{{
    "title": "...",
    "description": "...",
    "image_search_query": "...",
    "text_overlay": "...",
    "alt_text": "..."
}}"""

    response = client.messages.create(
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


def build_destination_url(base_url, brand, posting_method, campaign="pins"):
    """Build destination URL with UTM tracking parameters."""
    if base_url == "NEEDS_LANDING_PAGE":
        base_url = "https://linktr.ee/menopauseplanner"

    separator = '&' if '?' in base_url else '?'
    return (
        f"{base_url}{separator}"
        f"utm_source=pinterest&"
        f"utm_medium={posting_method}&"
        f"utm_campaign={brand}_{campaign}&"
        f"utm_content={datetime.utcnow().strftime('%Y%m%d')}"
    )
