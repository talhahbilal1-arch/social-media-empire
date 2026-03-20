"""Inject product promotion pins into the daily content-engine pipeline.

On each run, there's a 30% chance of injecting one product promo pin into
the fitness brand's daily batch. This keeps Gumroad products visible on
Pinterest without overwhelming the organic content mix.

The pin content rotates through different angles/products to stay fresh.
"""

import random
import hashlib
from datetime import datetime, timezone

# Product pin templates — rotated through on each injection
PRODUCT_PIN_TEMPLATES = [
    # AI Fitness Coach Vault ($27)
    {
        "title": "75 AI Prompts That Replace Your Program Design Time",
        "description": "Fitness coaches: stop spending 2+ hours writing programs from scratch. This vault has 75 copy-paste AI prompts built for the men over 35 market — programs, nutrition, recovery, client management. Written by an ISSA CPT. Link in pin. #fitnesscoach #aifitness #personaltrainer #chatgpt #fitover35 #coachingtools",
        "image_query": "personal trainer man tablet technology gym modern",
        "destination_url": "https://talhahbilal.gumroad.com/l/lupkl",
        "board": "Fitness Coach Business",
    },
    {
        "title": "The AI Shortcut Every Fitness Coach Over 35 Needs",
        "description": "Your clients over 35 need different training. These 75 AI prompts generate age-appropriate programs, testosterone-friendly nutrition plans, and recovery protocols in minutes. Built by a certified trainer who specializes in this demographic. Save this. #fitover35 #personaltrainer #aitools #coachingbusiness #fitnesscoach",
        "image_query": "athletic man over 40 gym training determined focused",
        "destination_url": "https://talhahbilal.gumroad.com/l/lupkl",
        "board": "Men's Fitness Over 35",
    },
    # Free lead magnet
    {
        "title": "5 Free AI Prompts That Save Coaches 5 Hours a Week",
        "description": "Not sure if AI prompts work for fitness coaching? Try these 5 free ones first. Generate a complete 4-week program, a nutrition plan, and a recovery protocol — all tailored for men over 35. Free download, no email required. #fitnesscoach #freeresource #personaltrainer #chatgpt #aifitness #fitover35",
        "image_query": "man fitness workout planning smartphone modern gym",
        "destination_url": "https://talhahbilal.gumroad.com/l/dkschg",
        "board": "Fitness Coach Business",
    },
    # Pinterest Automation Blueprint ($47)
    {
        "title": "How I Post 15 Pinterest Pins a Day Without Touching My Phone",
        "description": "This isn't a scheduling tool — it's a full automation system. AI writes the copy, generates images, and posts to Pinterest while you sleep. I built it for my 3 brand accounts and now I'm sharing the exact blueprint. Works with free tools only. #pinterestmarketing #pinterestautomation #digitalmarketing #passiveincome #aitools",
        "image_query": "woman working laptop social media marketing modern office",
        "destination_url": "https://talhahbilal.gumroad.com/l/epjybe",
        "board": "Fitness Coach Business",
    },
    # Online Coach Client Machine ($17)
    {
        "title": "5 AI Scripts That Convert DMs Into Paying Clients",
        "description": "Online coaches: your DM game needs an upgrade. These AI-powered scripts handle discovery calls, follow-ups, objection handling, and onboarding — all written for the coaching industry. Stop winging your sales conversations. Link below. #onlinecoach #coachingbusiness #salesscripts #chatgpt #aitools #clientacquisition",
        "image_query": "coach professional man laptop conversation business meeting",
        "destination_url": "https://talhahbilal.gumroad.com/l/weaaa",
        "board": "Fitness Coach Business",
    },
    {
        "title": "How to Land 3 New Coaching Clients This Week Using AI",
        "description": "Your prospect said 'I'll think about it' and ghosted. Sound familiar? These 50 AI prompt scripts handle every step — from first DM to signed client. Discovery call scripts, follow-up sequences, objection handlers. Built for online coaches. #onlinecoach #salesfunnel #coachingbusiness #aitools #clientacquisition",
        "image_query": "successful business man celebrating handshake deal professional",
        "destination_url": "https://talhahbilal.gumroad.com/l/weaaa",
        "board": "Fitness Coach Business",
    },
]

# Injection probability per content-engine run (30% = ~1 promo pin/day across 3 runs)
INJECTION_PROBABILITY = 0.30


def should_inject_product_pin():
    """Return True if we should inject a product pin this run."""
    return random.random() < INJECTION_PROBABILITY


def get_product_pin():
    """Return a product pin dict compatible with the content-engine pipeline.

    Selects based on the current hour to rotate through templates predictably.
    """
    # Use hour-based rotation so each run gets a different template
    hour = datetime.now(timezone.utc).hour
    idx = hour % len(PRODUCT_PIN_TEMPLATES)
    template = PRODUCT_PIN_TEMPLATES[idx]

    # Build a pin_data dict matching what content-engine expects
    return {
        'brand': 'fitness',
        'title': template['title'],
        'description': template['description'],
        'image_search_query': template['image_query'],
        'graphic_title': template['title'][:60],
        'tips': [],
        'destination_url': template['destination_url'],
        'board': template['board'],
        'visual_style': 'gradient_overlay',
        'topic': 'product_promotion',
        'category': 'product_promotion',
        'angle_framework': 'product_promo',
        'description_opener': '',
        'is_product_pin': True,
    }
