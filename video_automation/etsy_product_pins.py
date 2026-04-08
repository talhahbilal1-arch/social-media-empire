"""Etsy product pin templates for ADHD Planner and Night Shift Nurse Planner.

These pins post to the DailyDealDarling Pinterest account (connection 6738173)
on the "Self Care Products Worth It" and "Gift Ideas" boards.

Update ETSY_URLS with your actual Etsy listing URLs before running.
"""

# ─── UPDATE THESE WITH YOUR REAL ETSY LISTING URLS ─────────────────────────
ETSY_URLS = {
    "adhd_planner": "https://www.etsy.com/listing/YOUR-ADHD-PLANNER-ID",
    "nurse_planner": "https://www.etsy.com/listing/YOUR-NURSE-PLANNER-ID",
}

# ─── PIN TEMPLATES ───────────────────────────────────────────────────────────
# 5 pins per product = 10 total, rotated 1-2/day via etsy-product-pins.yml

ETSY_PIN_TEMPLATES = [
    # ── ADHD PLANNER (5 pins) ────────────────────────────────────────────────
    {
        "product": "adhd_planner",
        "title": "The ADHD Planner That Actually Works (No More Blank Pages)",
        "description": (
            "Designed for ADHD brains — not against them. This planner uses body "
            "doubling cues, time-blocking in 25-min sprints, and a daily 'dopamine "
            "menu' to keep you on track without overwhelm. No rigid schedules. "
            "No guilt trips. Just a system that works with your brain. "
            "⭐ Perfect gift for anyone with ADHD. Available on Etsy. "
            "#ADHDplanner #ADHDorganization #ADHDproductivity #plannerforADHD "
            "#neurodivergent #ADHDtools #selfcare #giftideas"
        ),
        "image_query": "woman organized desk planner notebook productivity colorful",
        "board": "Self Care Products Worth It",
    },
    {
        "product": "adhd_planner",
        "title": "ADHD Time Blindness Fix: This Planner Changed Everything",
        "description": (
            "Time blindness is one of the hardest ADHD symptoms to manage. This "
            "planner breaks every day into visible time blocks with built-in "
            "transition reminders, priority sorting, and an 'energy check' so you "
            "schedule tasks when your brain is actually ready for them. "
            "Stop losing hours. Start seeing your day. "
            "#ADHDtime #timeblindness #ADHDhacks #productivityplanner #planneraddict "
            "#ADHDawareness #neurodivergentlife #focustools"
        ),
        "image_query": "planner open flat lay desk timer clock productivity",
        "board": "Self Care Products Worth It",
    },
    {
        "product": "adhd_planner",
        "title": "5 ADHD Planner Features That Make It Actually Usable",
        "description": (
            "1. Task initiation prompts (breaks 'I don't know where to start') "
            "2. Visual time blocks (fights time blindness) "
            "3. Daily dopamine menu (builds motivation) "
            "4. Body doubling box (virtual accountability check-in) "
            "5. Low-stakes weekly reset (no guilt, just restart) "
            "Every feature designed with ADHD in mind. Link below. "
            "#ADHDplanner #ADHDproductivity #ADHDorganization #neurodivergent "
            "#plannerforADHD #ADHDlife #selfhelp #focushacks"
        ),
        "image_query": "flat lay planner stickers pens organized desk aesthetic",
        "board": "Gift Ideas",
    },
    {
        "product": "adhd_planner",
        "title": "ADHD Planner Under $30 — The Gift They'll Actually Use",
        "description": (
            "Most planners fail people with ADHD because they're designed for "
            "neurotypical brains. This one isn't. Built with task initiation cues, "
            "visual time blocks, and a weekly reset that takes 5 minutes. "
            "Under $30. Bestseller on Etsy. Perfect for students, parents, "
            "professionals — anyone managing ADHD day to day. "
            "#giftideas #ADHDgift #plannerlovers #ADHDplanner #selfcaregift "
            "#etsyfinds #etsyseller #neurodivergentgifts"
        ),
        "image_query": "gift wrap planner book present ribbon desk cozy",
        "board": "Gift Ideas",
    },
    {
        "product": "adhd_planner",
        "title": "Why Generic Planners Fail ADHD Brains (And What Works Instead)",
        "description": (
            "Generic planners assume you'll remember to check them, feel motivated "
            "to start tasks, and stick to a rigid daily structure. ADHD brains need "
            "visual cues, flexible time blocks, and built-in dopamine hits for "
            "completing small wins. This planner was built around those exact needs. "
            "Save this if you've given up on planners before. "
            "#ADHDtips #ADHDhacks #neurodivergent #ADHDplanner #plannerforADHD "
            "#ADHDorganization #brainhealth #productivityhacks"
        ),
        "image_query": "woman focused writing journal planner morning coffee home",
        "board": "Self Care Products Worth It",
    },

    # ── NIGHT SHIFT NURSE PLANNER (5 pins) ──────────────────────────────────
    {
        "product": "nurse_planner",
        "title": "The Night Shift Nurse Planner — Built for 12-Hour Shifts",
        "description": (
            "Regular planners weren't made for nurses on rotating night shifts. "
            "This one was. Track shift rotations, meal prep, sleep windows, "
            "self-care routines, and monthly goals — all in a format that works "
            "around a 12-hour schedule, not against it. "
            "Perfect gift for any nurse who needs to feel organized. "
            "Available on Etsy. "
            "#nurseplanner #nightshiftnurse #nurselife #nursinggifts "
            "#nursegift #selfcarefornurses #nursesofinstagram #giftideas"
        ),
        "image_query": "nurse woman uniform smiling professional confident healthcare",
        "board": "Self Care Products Worth It",
    },
    {
        "product": "nurse_planner",
        "title": "Night Shift Self-Care: The Nurse Planner That Fits Your Schedule",
        "description": (
            "Working nights flips your entire routine. Sleep hygiene, meal timing, "
            "social life — all different. This planner has a dedicated 'night shift "
            "reset' section, shift-specific meal prep templates, and a weekly "
            "self-care tracker so you stop putting yourself last. "
            "Because you take care of everyone else — now take care of you. "
            "#nursewellness #nightshiftnurse #nurseself care #nursinglife "
            "#nurseplanner #healthcareworker #nursetips #selfcarefornurses"
        ),
        "image_query": "woman self care morning routine journaling peaceful bedroom",
        "board": "Self Care Products Worth It",
    },
    {
        "product": "nurse_planner",
        "title": "Best Gift for a Night Shift Nurse (Under $30)",
        "description": (
            "She works 12-hour nights, barely sleeps, and still shows up for "
            "everyone. This planner was designed specifically for night shift "
            "nurses: shift rotation tracker, meal prep grid, sleep log, monthly "
            "budget, and self-care checklist. Practical and thoughtful. "
            "Nurses actually use this one. "
            "#nursegift #giftfornurse #nurselife #nursingschool #giftsforher "
            "#nightshiftnurse #etsyfinds #nursinggraduation"
        ),
        "image_query": "gift wrap present ribbon pink healthcare professional gift",
        "board": "Gift Ideas",
    },
    {
        "product": "nurse_planner",
        "title": "5 Things Every Night Shift Nurse Needs to Track (Planner Inside)",
        "description": (
            "1. Shift rotation calendar (so your body clock has a fighting chance) "
            "2. Sleep windows (non-negotiable for long-term health) "
            "3. Meal prep on off days (prevents vending machine meals at 3AM) "
            "4. Hydration + step goals (12 hours on your feet is brutal) "
            "5. Monthly self-care wins (remember you're human too) "
            "This planner tracks all 5. Link below. "
            "#nightshiftnurse #nursetips #nurseplanner #nursewellness "
            "#healthcareworker #selfcarefornurses #nurselife #burnoutprevention"
        ),
        "image_query": "nurse checklist notes clipboard hospital healthy lifestyle",
        "board": "Self Care Products Worth It",
    },
    {
        "product": "nurse_planner",
        "title": "Night Shift Nurse Burnout Fix: Start With This Planner",
        "description": (
            "Nurse burnout is real and it's preventable. One major driver: no "
            "structured recovery between shifts. This planner has a 'shift recovery "
            "protocol' section — sleep, food, decompression — so you actually "
            "recover between 12-hour nights instead of just surviving until the "
            "next one. Designed by a healthcare worker, for healthcare workers. "
            "#nurseburnout #nightshiftnurse #nurseself care #nursewellness "
            "#healthcareworkers #nursestrong #nurseplanner #selfcare"
        ),
        "image_query": "woman relaxing cozy blanket tea book self care rest recovery",
        "board": "Self Care Products Worth It",
    },
]
