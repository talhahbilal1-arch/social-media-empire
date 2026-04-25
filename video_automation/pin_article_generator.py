"""High-converting affiliate buying guide generator for per-pin articles.

Generates a Wirecutter-style buying guide (1200-1800 words) for each pin
during the content-engine run. One Gemini API call per article.
Articles are saved as HTML to the brand's website directory and
registered in the generated_articles Supabase table.
"""

import os
import re
import json
import logging
import urllib.parse
from datetime import datetime, timezone

import requests
from video_automation.gemini_client import generate_json, generate_text, get_client

logger = logging.getLogger(__name__)


def _get_client():
    """Get the shared Gemini client (delegates to gemini_client module)."""
    return get_client()


# ── Amazon Associates affiliate links ──────────────────────────────────────────
# Fitness uses fitover3509-20, all other brands use dailydealdarl-20.
# Direct /dp/ASIN links are preferred. For any product NOT in this list, the
# code falls back to Amazon search URLs (/s?k=...) which always work.

AMAZON_AFFILIATE_LINKS = {
    "fitness": {
        # Supplements
        "creatine monohydrate": "https://www.amazon.com/dp/B002DYIZEO?tag=fitover3509-20",
        "creatine": "https://www.amazon.com/dp/B002DYIZEO?tag=fitover3509-20",
        "vitamin D3": "https://www.amazon.com/dp/B00GB85JR4?tag=fitover3509-20",
        "magnesium glycinate": "https://www.amazon.com/dp/B000BD0RT0?tag=fitover3509-20",
        "magnesium": "https://www.amazon.com/dp/B000BD0RT0?tag=fitover3509-20",
        "fish oil": "https://www.amazon.com/dp/B004O2I9JO?tag=fitover3509-20",
        "omega 3": "https://www.amazon.com/dp/B004O2I9JO?tag=fitover3509-20",
        "ashwagandha": "https://www.amazon.com/dp/B073DN2YG9?tag=fitover3509-20",
        "protein powder": "https://www.amazon.com/dp/B000QSNYGI?tag=fitover3509-20",
        "whey protein": "https://www.amazon.com/dp/B000QSNYGI?tag=fitover3509-20",
        "collagen peptides": "https://www.amazon.com/dp/B07CG8BCWK?tag=fitover3509-20",
        "collagen": "https://www.amazon.com/dp/B07CG8BCWK?tag=fitover3509-20",
        "zinc": "https://www.amazon.com/dp/B08YLTCDTN?tag=fitover3509-20",
        "bcaa": "https://www.amazon.com/dp/B009NW9U3Y?tag=fitover3509-20",
        "pre workout": "https://www.amazon.com/dp/B00PYB335O?tag=fitover3509-20",
        "multivitamin": "https://www.amazon.com/dp/B001F71XAI?tag=fitover3509-20",
        "probiotics": "https://www.amazon.com/dp/B079H53D2B?tag=fitover3509-20",
        "turmeric": "https://www.amazon.com/dp/B0C1G7YCJF?tag=fitover3509-20",
        "melatonin": "https://www.amazon.com/dp/B005DEK990?tag=fitover3509-20",
        "testosterone booster": "https://www.amazon.com/dp/B01MQ1JLWY?tag=fitover3509-20",
        "tongkat ali": "https://www.amazon.com/dp/B0C361XRFK?tag=fitover3509-20",
        "electrolytes": "https://www.amazon.com/dp/B01IT9NLHW?tag=fitover3509-20",
        # Equipment
        "resistance bands": "https://www.amazon.com/dp/B01AVDVHTI?tag=fitover3509-20",
        "adjustable dumbbells": "https://www.amazon.com/dp/B0DPFW7F4B?tag=fitover3509-20",
        "pull-up bar": "https://www.amazon.com/dp/B001EJMS6K?tag=fitover3509-20",
        "foam roller": "https://www.amazon.com/dp/B0040EKZDY?tag=fitover3509-20",
        "yoga mat": "https://www.amazon.com/dp/B0B74MRJS3?tag=fitover3509-20",
        "kettlebell": "https://www.amazon.com/dp/B0731DWW5K?tag=fitover3509-20",
        "massage gun": "https://www.amazon.com/dp/B0CG6FQPC5?tag=fitover3509-20",
        "workout gloves": "https://www.amazon.com/dp/B07KQR9VXG?tag=fitover3509-20",
        "weight bench": "https://www.amazon.com/dp/B07DNHHNNN?tag=fitover3509-20",
        "barbell": "https://www.amazon.com/dp/B001K4OPY2?tag=fitover3509-20",
        "power rack": "https://www.amazon.com/dp/B0BFQVVFB7?tag=fitover3509-20",
        "squat rack": "https://www.amazon.com/dp/B0BFQVVFB7?tag=fitover3509-20",
        "ab roller": "https://www.amazon.com/dp/B0007IS74G?tag=fitover3509-20",
        "jump rope": "https://www.amazon.com/dp/B09DF9NWC7?tag=fitover3509-20",
        "weight plates": "https://www.amazon.com/dp/B0DHYNHYJD?tag=fitover3509-20",
        "dip station": "https://www.amazon.com/dp/B002Y2SUU4?tag=fitover3509-20",
        "lifting belt": "https://www.amazon.com/dp/B074KKQJYH?tag=fitover3509-20",
        "lifting straps": "https://www.amazon.com/dp/B0FFBNL8BG?tag=fitover3509-20",
        "knee sleeves": "https://www.amazon.com/dp/B08JGP1WYM?tag=fitover3509-20",
        "weighted vest": "https://www.amazon.com/dp/B0GM2JS7LH?tag=fitover3509-20",
        "battle ropes": "https://www.amazon.com/dp/B072Z2ZTLJ?tag=fitover3509-20",
        "suspension trainer": "https://www.amazon.com/dp/B08BCKK41K?tag=fitover3509-20",
        "stability ball": "https://www.amazon.com/dp/B07RX2J294?tag=fitover3509-20",
        "grip strengthener": "https://www.amazon.com/dp/B092DRRGFC?tag=fitover3509-20",
        # Nutrition & Recovery
        "food scale": "https://www.amazon.com/dp/B004164SRA?tag=fitover3509-20",
        "glass meal prep containers": "https://www.amazon.com/dp/B07Q498XSZ?tag=fitover3509-20",
        "protein shaker": "https://www.amazon.com/dp/B0FMY6YJ3B?tag=fitover3509-20",
        "stretching strap": "https://www.amazon.com/dp/B09WVC526G?tag=fitover3509-20",
        "lacrosse ball": "https://www.amazon.com/dp/B07K3B17Q3?tag=fitover3509-20",
        "ice pack": "https://www.amazon.com/dp/B01LXM8W8T?tag=fitover3509-20",
        # Tech
        "fitness tracker": "https://www.amazon.com/dp/B0B5F9SZW7?tag=fitover3509-20",
        "smart scale": "https://www.amazon.com/dp/B01N1UX8RW?tag=fitover3509-20",
        "water bottle": "https://www.amazon.com/dp/B0DLCG65B5?tag=fitover3509-20",
        "_default": "https://www.amazon.com/dp/B0DPFW7F4B?tag=fitover3509-20",
    },
    "deals": {
        # Kitchen Appliances
        "air fryer": "https://www.amazon.com/dp/B07FDJMC9Q?tag=dailydealdarl-20",
        "instant pot": "https://www.amazon.com/dp/B00FLYWNYQ?tag=dailydealdarl-20",
        "coffee maker": "https://www.amazon.com/dp/B01GJOMWVA?tag=dailydealdarl-20",
        "blender": "https://www.amazon.com/dp/B0G6FR8V9Y?tag=dailydealdarl-20",
        "food processor": "https://www.amazon.com/dp/B089TP3K77?tag=dailydealdarl-20",
        "slow cooker": "https://www.amazon.com/dp/B004P2NG0K?tag=dailydealdarl-20",
        "electric kettle": "https://www.amazon.com/dp/B07TZ5YHJN?tag=dailydealdarl-20",
        "stand mixer": "https://www.amazon.com/dp/B005PVPI2E?tag=dailydealdarl-20",
        # Kitchen Tools
        "knife set": "https://www.amazon.com/dp/B07RTH8LM7?tag=dailydealdarl-20",
        "chef knife": "https://www.amazon.com/dp/B0CKZ1MJ7Y?tag=dailydealdarl-20",
        "cutting board": "https://www.amazon.com/dp/B01GP2MTXW?tag=dailydealdarl-20",
        "cast iron skillet": "https://www.amazon.com/dp/B00006JSUA?tag=dailydealdarl-20",
        "nonstick pan": "https://www.amazon.com/dp/B0F9YK3VZM?tag=dailydealdarl-20",
        "dutch oven": "https://www.amazon.com/dp/B000N501BK?tag=dailydealdarl-20",
        "baking sheet": "https://www.amazon.com/dp/B088P9H3V7?tag=dailydealdarl-20",
        "mixing bowls": "https://www.amazon.com/dp/B0CGWQ53L3?tag=dailydealdarl-20",
        "cooking utensil set": "https://www.amazon.com/dp/B089FBYT3W?tag=dailydealdarl-20",
        "vegetable chopper": "https://www.amazon.com/dp/B0764HS4SL?tag=dailydealdarl-20",
        "meal prep containers": "https://www.amazon.com/dp/B08CVTY9FS?tag=dailydealdarl-20",
        "storage containers": "https://www.amazon.com/dp/B001RCUNJ8?tag=dailydealdarl-20",
        # Organization
        "organizer bins": "https://www.amazon.com/dp/B002VK5QN8?tag=dailydealdarl-20",
        "label maker": "https://www.amazon.com/dp/B0C3L93F2Q?tag=dailydealdarl-20",
        "drawer dividers": "https://www.amazon.com/dp/B0D5Y391WS?tag=dailydealdarl-20",
        "closet organizer": "https://www.amazon.com/dp/B0C7PWN1JV?tag=dailydealdarl-20",
        "shoe rack": "https://www.amazon.com/dp/B0747QX7QG?tag=dailydealdarl-20",
        "hangers": "https://www.amazon.com/dp/B09MFQL6P5?tag=dailydealdarl-20",
        "lazy susan": "https://www.amazon.com/dp/B0F8J2ZTQ9?tag=dailydealdarl-20",
        "vacuum storage bags": "https://www.amazon.com/dp/B07RSCPH4N?tag=dailydealdarl-20",
        "command hooks": "https://www.amazon.com/dp/B0753NHZVQ?tag=dailydealdarl-20",
        "desk organizer": "https://www.amazon.com/dp/B0BYDGF8DT?tag=dailydealdarl-20",
        # Beauty
        "silk pillowcase": "https://www.amazon.com/dp/B09BFQG17F?tag=dailydealdarl-20",
        "LED face mask": "https://www.amazon.com/dp/B0F18BBHCC?tag=dailydealdarl-20",
        "jade roller": "https://www.amazon.com/dp/B0FRMB9NJV?tag=dailydealdarl-20",
        "gua sha": "https://www.amazon.com/dp/B09TPDYS7N?tag=dailydealdarl-20",
        "retinol serum": "https://www.amazon.com/dp/B01MSSDEPK?tag=dailydealdarl-20",
        "vitamin c serum": "https://www.amazon.com/dp/B01M4MCUAF?tag=dailydealdarl-20",
        "sunscreen": "https://www.amazon.com/dp/B01MQXX9US?tag=dailydealdarl-20",
        "hair dryer": "https://www.amazon.com/dp/B003TQPRGY?tag=dailydealdarl-20",
        # Home Decor
        "throw pillows": "https://www.amazon.com/dp/B0714K41PB?tag=dailydealdarl-20",
        "LED candles": "https://www.amazon.com/dp/B09BFQG17F?tag=dailydealdarl-20",
        "fairy lights": "https://www.amazon.com/dp/B0DWMYJF8Y?tag=dailydealdarl-20",
        "throw blanket": "https://www.amazon.com/dp/B08NWSLV61?tag=dailydealdarl-20",
        "area rug": "https://www.amazon.com/dp/B098DP5MH8?tag=dailydealdarl-20",
        "curtains": "https://www.amazon.com/dp/B01CS31R94?tag=dailydealdarl-20",
        "diffuser": "https://www.amazon.com/dp/B01MR4Y0CZ?tag=dailydealdarl-20",
        "scented candles": "https://www.amazon.com/dp/B0CR7L79Q2?tag=dailydealdarl-20",
        # Cleaning & Tech
        "robot vacuum": "https://www.amazon.com/dp/B0GDXV2KJ4?tag=dailydealdarl-20",
        "cordless vacuum": "https://www.amazon.com/dp/B0F2B29SPC?tag=dailydealdarl-20",
        "smart plug": "https://www.amazon.com/dp/B07XJ8C8F5?tag=dailydealdarl-20",
        "echo dot": "https://www.amazon.com/dp/B09B8V1LZ3?tag=dailydealdarl-20",
        "water bottle": "https://www.amazon.com/dp/B085DTZQNZ?tag=dailydealdarl-20",
        "stanley tumbler": "https://www.amazon.com/dp/B0CV64341S?tag=dailydealdarl-20",
        "_default": "https://www.amazon.com/dp/B002VK5QN8?tag=dailydealdarl-20",
    },
    "menopause": {
        # Supplements
        "black cohosh": "https://www.amazon.com/dp/B000GG6ABI?tag=dailydealdarl-20",
        "evening primrose oil": "https://www.amazon.com/dp/B000GH0PFM?tag=dailydealdarl-20",
        "magnesium glycinate": "https://www.amazon.com/dp/B000BD0RT0?tag=dailydealdarl-20",
        "magnesium": "https://www.amazon.com/dp/B000BD0RT0?tag=dailydealdarl-20",
        "vitamin D3": "https://www.amazon.com/dp/B00GB85JR4?tag=dailydealdarl-20",
        "calcium": "https://www.amazon.com/dp/B002FH5I0I?tag=dailydealdarl-20",
        "collagen powder": "https://www.amazon.com/dp/B09QV3XG8B?tag=dailydealdarl-20",
        "collagen": "https://www.amazon.com/dp/B09QV3XG8B?tag=dailydealdarl-20",
        "probiotics": "https://www.amazon.com/dp/B079H53D2B?tag=dailydealdarl-20",
        "omega 3": "https://www.amazon.com/dp/B004O2I9JO?tag=dailydealdarl-20",
        "fish oil": "https://www.amazon.com/dp/B004O2I9JO?tag=dailydealdarl-20",
        "maca root": "https://www.amazon.com/dp/B01M362DU7?tag=dailydealdarl-20",
        "ashwagandha": "https://www.amazon.com/dp/B073DN2YG9?tag=dailydealdarl-20",
        "turmeric": "https://www.amazon.com/dp/B08HY91VTB?tag=dailydealdarl-20",
        "dong quai": "https://www.amazon.com/dp/B0C91ZK92W?tag=dailydealdarl-20",
        "red clover": "https://www.amazon.com/dp/B000Z95EZC?tag=dailydealdarl-20",
        "valerian root": "https://www.amazon.com/dp/B0012AMVHW?tag=dailydealdarl-20",
        "melatonin": "https://www.amazon.com/dp/B005DEK990?tag=dailydealdarl-20",
        "multivitamin women": "https://www.amazon.com/dp/B09QBKGDLS?tag=dailydealdarl-20",
        # Sleep & Comfort
        "cooling pillow": "https://www.amazon.com/dp/B0BFRH42QJ?tag=dailydealdarl-20",
        "bamboo sheets": "https://www.amazon.com/dp/B07YKCZHGK?tag=dailydealdarl-20",
        "cooling pajamas": "https://www.amazon.com/dp/B0BR9PVMP9?tag=dailydealdarl-20",
        "weighted blanket": "https://www.amazon.com/dp/B092LZLLGF?tag=dailydealdarl-20",
        "silk pillowcase": "https://www.amazon.com/dp/B09BFQG17F?tag=dailydealdarl-20",
        "white noise machine": "https://www.amazon.com/dp/B07VRJSFVC?tag=dailydealdarl-20",
        "sleep mask": "https://www.amazon.com/dp/B07KC5DWCC?tag=dailydealdarl-20",
        "cooling mattress pad": "https://www.amazon.com/dp/B07D5DN269?tag=dailydealdarl-20",
        "cooling blanket": "https://www.amazon.com/dp/B0DR8CHFKV?tag=dailydealdarl-20",
        "blackout curtains": "https://www.amazon.com/dp/B01CS31R94?tag=dailydealdarl-20",
        # Wellness
        "symptom tracker journal": "https://www.amazon.com/dp/B0DNSRBRN1?tag=dailydealdarl-20",
        "essential oils diffuser": "https://www.amazon.com/dp/B01MR4Y0CZ?tag=dailydealdarl-20",
        "yoga mat": "https://www.amazon.com/dp/B0B74MRJS3?tag=dailydealdarl-20",
        "resistance bands": "https://www.amazon.com/dp/B01AVDVHTI?tag=dailydealdarl-20",
        "foam roller": "https://www.amazon.com/dp/B0040EKZDY?tag=dailydealdarl-20",
        "jade roller": "https://www.amazon.com/dp/B0FRMB9NJV?tag=dailydealdarl-20",
        "gua sha": "https://www.amazon.com/dp/B09TPDYS7N?tag=dailydealdarl-20",
        "heating pad": "https://www.amazon.com/dp/B00075M1T6?tag=dailydealdarl-20",
        "tens unit": "https://www.amazon.com/dp/B00NCRE4GO?tag=dailydealdarl-20",
        "acupressure mat": "https://www.amazon.com/dp/B071FNYSJY?tag=dailydealdarl-20",
        "cooling towel": "https://www.amazon.com/dp/B0CBPFF73Y?tag=dailydealdarl-20",
        "herbal tea": "https://www.amazon.com/dp/B0009F3QL6?tag=dailydealdarl-20",
        "lavender oil": "https://www.amazon.com/dp/B00TSTZQEY?tag=dailydealdarl-20",
        "humidifier": "https://www.amazon.com/dp/B013IJPTFK?tag=dailydealdarl-20",
        "air purifier": "https://www.amazon.com/dp/B07VVK39F7?tag=dailydealdarl-20",
        "_default": "https://www.amazon.com/dp/B002FH5I0I?tag=dailydealdarl-20",
    },
    "pilottools": {
        # PilotTools does NOT use Amazon — SaaS affiliate programs instead
        # These are placeholder URLs; actual affiliate links are managed externally
        "_default": "https://pilottools.ai/tools/",
    },
    "homedecor": {
        # Home Decor — uses dailydealdarl-20 tag
        "throw pillows": "https://www.amazon.com/dp/B0714K41PB?tag=dailydealdarl-20",
        "accent pillows": "https://www.amazon.com/dp/B0714K41PB?tag=dailydealdarl-20",
        "curtains": "https://www.amazon.com/dp/B01CS31R94?tag=dailydealdarl-20",
        "blackout curtains": "https://www.amazon.com/dp/B01CS31R94?tag=dailydealdarl-20",
        "area rug": "https://www.amazon.com/dp/B098DP5MH8?tag=dailydealdarl-20",
        "rug": "https://www.amazon.com/dp/B098DP5MH8?tag=dailydealdarl-20",
        "wall art": "https://www.amazon.com/dp/B07TYWLQFR?tag=dailydealdarl-20",
        "canvas art": "https://www.amazon.com/dp/B07TYWLQFR?tag=dailydealdarl-20",
        "scented candles": "https://www.amazon.com/dp/B0CR7L79Q2?tag=dailydealdarl-20",
        "candles": "https://www.amazon.com/dp/B0CR7L79Q2?tag=dailydealdarl-20",
        "picture frames": "https://www.amazon.com/dp/B08GFY4NKT?tag=dailydealdarl-20",
        "frames": "https://www.amazon.com/dp/B08GFY4NKT?tag=dailydealdarl-20",
        "vases": "https://www.amazon.com/dp/B0BXDSH6CJ?tag=dailydealdarl-20",
        "vase": "https://www.amazon.com/dp/B0BXDSH6CJ?tag=dailydealdarl-20",
        "table lamp": "https://www.amazon.com/dp/B08GKF46GW?tag=dailydealdarl-20",
        "lamp": "https://www.amazon.com/dp/B08GKF46GW?tag=dailydealdarl-20",
        "decorative tray": "https://www.amazon.com/dp/B08XZHGS9J?tag=dailydealdarl-20",
        "tray": "https://www.amazon.com/dp/B08XZHGS9J?tag=dailydealdarl-20",
        "storage baskets": "https://www.amazon.com/dp/B07WNHP7PK?tag=dailydealdarl-20",
        "baskets": "https://www.amazon.com/dp/B07WNHP7PK?tag=dailydealdarl-20",
        "floating shelves": "https://www.amazon.com/dp/B0B5LMDCB7?tag=dailydealdarl-20",
        "shelves": "https://www.amazon.com/dp/B0B5LMDCB7?tag=dailydealdarl-20",
        "accent mirror": "https://www.amazon.com/dp/B07W4LXHP5?tag=dailydealdarl-20",
        "mirror": "https://www.amazon.com/dp/B07W4LXHP5?tag=dailydealdarl-20",
        "artificial plants": "https://www.amazon.com/dp/B0834LBKHQ?tag=dailydealdarl-20",
        "fake plants": "https://www.amazon.com/dp/B0834LBKHQ?tag=dailydealdarl-20",
        "throw blanket": "https://www.amazon.com/dp/B08NWSLV61?tag=dailydealdarl-20",
        "blanket": "https://www.amazon.com/dp/B08NWSLV61?tag=dailydealdarl-20",
        "coasters": "https://www.amazon.com/dp/B07PZMQBPJ?tag=dailydealdarl-20",
        "duvet cover": "https://www.amazon.com/dp/B07VHFTQH7?tag=dailydealdarl-20",
        "nightstand lamp": "https://www.amazon.com/dp/B08GKF46GW?tag=dailydealdarl-20",
        "blanket ladder": "https://www.amazon.com/dp/B09CTQG1CX?tag=dailydealdarl-20",
        "coffee table books": "https://www.amazon.com/dp/B0BLHB8VT1?tag=dailydealdarl-20",
        "bar stools": "https://www.amazon.com/dp/B0B9GJ6M8T?tag=dailydealdarl-20",
        "shower curtain": "https://www.amazon.com/dp/B07DFBQRSF?tag=dailydealdarl-20",
        "bath mat": "https://www.amazon.com/dp/B08D3Y5PFZ?tag=dailydealdarl-20",
        "towel set": "https://www.amazon.com/dp/B07D4JRLHH?tag=dailydealdarl-20",
        "soap dispenser": "https://www.amazon.com/dp/B07Z8P1R4P?tag=dailydealdarl-20",
        "_default": "https://www.amazon.com/dp/B0714K41PB?tag=dailydealdarl-20",
    },
    "beauty": {
        # Beauty — uses dailydealdarl-20 tag
        "vitamin C serum": "https://www.amazon.com/dp/B01M4MCUAF?tag=dailydealdarl-20",
        "vitamin c serum": "https://www.amazon.com/dp/B01M4MCUAF?tag=dailydealdarl-20",
        "retinol cream": "https://www.amazon.com/dp/B01MSSDEPK?tag=dailydealdarl-20",
        "retinol": "https://www.amazon.com/dp/B01MSSDEPK?tag=dailydealdarl-20",
        "jade roller": "https://www.amazon.com/dp/B0FRMB9NJV?tag=dailydealdarl-20",
        "face masks": "https://www.amazon.com/dp/B09BFQG17F?tag=dailydealdarl-20",
        "LED face mask": "https://www.amazon.com/dp/B0F18BBHCC?tag=dailydealdarl-20",
        "makeup brushes": "https://www.amazon.com/dp/B01LY3QHOE?tag=dailydealdarl-20",
        "brush set": "https://www.amazon.com/dp/B01LY3QHOE?tag=dailydealdarl-20",
        "setting spray": "https://www.amazon.com/dp/B003YPZN5O?tag=dailydealdarl-20",
        "mascara": "https://www.amazon.com/dp/B004Y9GTYE?tag=dailydealdarl-20",
        "lip gloss": "https://www.amazon.com/dp/B004EHXZ22?tag=dailydealdarl-20",
        "moisturizer": "https://www.amazon.com/dp/B00TTD9BRC?tag=dailydealdarl-20",
        "sunscreen": "https://www.amazon.com/dp/B01MQXX9US?tag=dailydealdarl-20",
        "SPF": "https://www.amazon.com/dp/B01MQXX9US?tag=dailydealdarl-20",
        "hair oil": "https://www.amazon.com/dp/B003WJI070?tag=dailydealdarl-20",
        "dry shampoo": "https://www.amazon.com/dp/B00B3TMSUQ?tag=dailydealdarl-20",
        "makeup mirror": "https://www.amazon.com/dp/B01M0ABYIY?tag=dailydealdarl-20",
        "beauty blender": "https://www.amazon.com/dp/B003ZVJEEM?tag=dailydealdarl-20",
        "sponge": "https://www.amazon.com/dp/B003ZVJEEM?tag=dailydealdarl-20",
        "nail polish": "https://www.amazon.com/dp/B00FO4UQ5K?tag=dailydealdarl-20",
        "hyaluronic acid serum": "https://www.amazon.com/dp/B01INENT5G?tag=dailydealdarl-20",
        "hyaluronic acid": "https://www.amazon.com/dp/B01INENT5G?tag=dailydealdarl-20",
        "niacinamide serum": "https://www.amazon.com/dp/B07Q2GKX7Y?tag=dailydealdarl-20",
        "niacinamide": "https://www.amazon.com/dp/B07Q2GKX7Y?tag=dailydealdarl-20",
        "cleanser": "https://www.amazon.com/dp/B000052YMQ?tag=dailydealdarl-20",
        "toner": "https://www.amazon.com/dp/B00016XJ4M?tag=dailydealdarl-20",
        "foundation": "https://www.amazon.com/dp/B01DF1ERRG?tag=dailydealdarl-20",
        "concealer": "https://www.amazon.com/dp/B004Y9GZII?tag=dailydealdarl-20",
        "blush": "https://www.amazon.com/dp/B002LCZFIK?tag=dailydealdarl-20",
        "eyeshadow palette": "https://www.amazon.com/dp/B019FME2S6?tag=dailydealdarl-20",
        "eyelash curler": "https://www.amazon.com/dp/B0002JFI5Q?tag=dailydealdarl-20",
        "heat protectant": "https://www.amazon.com/dp/B00JNA436S?tag=dailydealdarl-20",
        "leave-in conditioner": "https://www.amazon.com/dp/B001AO0WCG?tag=dailydealdarl-20",
        "body lotion": "https://www.amazon.com/dp/B001E6OCOM?tag=dailydealdarl-20",
        "lip balm": "https://www.amazon.com/dp/B00XKYUKFA?tag=dailydealdarl-20",
        "ice roller": "https://www.amazon.com/dp/B09CL65JBT?tag=dailydealdarl-20",
        "_default": "https://www.amazon.com/dp/B01M4MCUAF?tag=dailydealdarl-20",
    },
}

BRAND_AFFILIATE_TAGS = {
    "fitness": "fitover3509-20",
    "deals": "dailydealdarl-20",
    "menopause": "dailydealdarl-20",
    "pilottools": "none",
    "homedecor": "dailydealdarl-20",
    "beauty": "dailydealdarl-20",
}


# ── Brand website config ────────────────────────────────────────────────────

BRAND_SITE_CONFIG = {
    "fitness": {
        "site_name": "FitOver35",
        "base_url": "https://fitover35.com",
        "output_dir": "outputs/fitover35-website/articles",
        "primary_color": "#1565C0",
        "accent_color": "#0D47A1",
        "logo_html": 'Fit<span style="color:#1565C0">Over35</span>',
        "nav_links": [
            ("Home", "../index.html"),
            ("Articles", "../blog.html"),
            ("About", "../about.html"),
            ("Contact", "../contact.html"),
        ],
        "has_css": True,
        "lead_magnet": "FREE 7-Day Fat Burn Kickstart Plan",
        "signup_form_id": "8946984",
        "signup_button_text": "Get Free Program",
    },
    "deals": {
        "site_name": "Daily Deal Darling",
        "base_url": "https://www.dailydealdarling.com",
        "output_dir": "outputs/dailydealdarling-website/articles",
        "primary_color": "#E91E63",
        "accent_color": "#C2185B",
        "logo_html": 'Daily Deal <span style="color:#E91E63">Darling</span>',
        "nav_links": [
            ("Home", "../index.html"),
            ("Articles", "./"),
            ("About", "../about.html"),
        ],
        "has_css": True,
        "lead_magnet": "FREE Weekly Deals Digest",
        "signup_form_id": "9144859",
        "signup_button_text": "Join Free",
    },
    "menopause": {
        "site_name": "The Menopause Planner",
        "base_url": "https://menopause-planner-website.vercel.app",  # no custom domain yet
        "output_dir": "outputs/menopause-planner-website/articles",
        "primary_color": "#7B1FA2",
        "accent_color": "#6A1B9A",
        "logo_html": 'The Menopause <span style="color:#7B1FA2">Planner</span>',
        "nav_links": [
            ("Home", "../index.html"),
            ("Articles", "./"),
            ("About", "../about.html"),
        ],
        "has_css": False,
        "lead_magnet": "FREE Menopause Symptom Tracker & Relief Guide",
        "signup_form_id": "9144926",
        "signup_button_text": "Get Free Guide",
    },
    "pilottools": {
        "site_name": "PilotTools",
        "base_url": "https://pilottools.ai",
        "output_dir": "outputs/pilottools-website/articles",
        "primary_color": "#0EA5E9",
        "accent_color": "#0284C7",
        "logo_html": 'Pilot<span style="color:#0EA5E9">Tools</span>',
        "nav_links": [
            ("Home", "../index.html"),
            ("Articles", "../blog.html"),
            ("Tools", "../tools.html"),
            ("About", "../about.html"),
        ],
        "has_css": True,
        "lead_magnet": "FREE: Top 25 AI Tools Cheat Sheet (2026 Edition)",
        "signup_form_id": "",
        "signup_button_text": "Get Free Cheat Sheet",
    },
    "homedecor": {
        "site_name": "Home Decor Edit",
        "base_url": "https://www.dailydealdarling.com",
        "output_dir": "outputs/homedecor-website/articles",
        "primary_color": "#6B705C",
        "accent_color": "#A5A58D",
        "logo_html": 'Home Decor <span style="color:#6B705C">Edit</span>',
        "nav_links": [
            ("Home", "../index.html"),
            ("Articles", "./"),
            ("About", "../about.html"),
        ],
        "has_css": False,
        "lead_magnet": "FREE Room-by-Room Budget Decorating Checklist",
        "signup_form_id": "",
        "signup_button_text": "Get Free Checklist",
    },
    "beauty": {
        "site_name": "The Beauty Shelf",
        "base_url": "https://www.dailydealdarling.com",
        "output_dir": "outputs/beauty-website/articles",
        "primary_color": "#D4A0A0",
        "accent_color": "#C47D8E",
        "logo_html": 'The Beauty <span style="color:#D4A0A0">Shelf</span>',
        "nav_links": [
            ("Home", "../index.html"),
            ("Articles", "./"),
            ("About", "../about.html"),
        ],
        "has_css": False,
        "lead_magnet": "FREE: 5-Step Skincare Routine Builder",
        "signup_form_id": "",
        "signup_button_text": "Get Free Routine",
    },
}


def _get_approved_asins():
    """Build set of all ASINs in our approved product lists."""
    asins = set()
    for brand_links in AMAZON_AFFILIATE_LINKS.values():
        for url in brand_links.values():
            m = re.search(r'/dp/([A-Z0-9]{10})', url)
            if m:
                asins.add(m.group(1))
    return asins


_APPROVED_ASINS = None  # lazy-loaded


def _fetch_pexels_image(query, orientation='landscape'):
    """Fetch a stock photo URL from Pexels. Returns URL string or None."""
    pexels_key = os.environ.get('PEXELS_API_KEY', '')
    if not pexels_key:
        logger.info("No PEXELS_API_KEY — skipping hero image fetch")
        return None
    if not query:
        return None
    # Shorten overly long queries (Pexels works best with 3-5 words)
    words = query.split()
    if len(words) > 6:
        query = ' '.join(words[:6])
    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": pexels_key},
            params={"query": query, "per_page": 5, "orientation": orientation},
            timeout=10,
        )
        if resp.status_code == 200:
            photos = resp.json().get('photos', [])
            if photos:
                img_url = photos[0]['src']['large']
                logger.info(f"Hero image found for '{query}': {img_url[:80]}...")
                return img_url
            logger.warning(f"No Pexels results for query: '{query}'")
        else:
            logger.warning(f"Pexels API returned {resp.status_code} for '{query}'")
    except Exception as e:
        logger.warning(f"Pexels hero image fetch failed for '{query}': {e}")
    # NEVER return None — use fallback image
    logger.info(f"Using fallback image for query: '{query}'")
    fallback_queries = {
        'woman': 'https://images.pexels.com/photos/6585764/pexels-photo-6585764.jpeg?auto=compress&cs=tinysrgb&w=900',
        'man': 'https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=900',
        'product': 'https://images.pexels.com/photos/5632399/pexels-photo-5632399.jpeg?auto=compress&cs=tinysrgb&w=900',
        'home': 'https://images.pexels.com/photos/1457842/pexels-photo-1457842.jpeg?auto=compress&cs=tinysrgb&w=900',
        'kitchen': 'https://images.pexels.com/photos/2062426/pexels-photo-2062426.jpeg?auto=compress&cs=tinysrgb&w=900',
        'sleep': 'https://images.pexels.com/photos/6585764/pexels-photo-6585764.jpeg?auto=compress&cs=tinysrgb&w=900',
        'fitness': 'https://images.pexels.com/photos/841130/pexels-photo-841130.jpeg?auto=compress&cs=tinysrgb&w=900',
    }
    query_lower = query.lower() if query else ''
    for keyword, url in fallback_queries.items():
        if keyword in query_lower:
            return url
    return 'https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=900'


def _fetch_pexels_video(query, orientation='landscape'):
    """Fetch a short Pexels stock video URL for article hero."""
    api_key = os.environ.get('PEXELS_API_KEY', '')
    if not api_key:
        return None
    if not query:
        return None
    words = query.split()
    if len(words) > 6:
        query = ' '.join(words[:6])
    try:
        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": api_key},
            params={"query": query, "per_page": 5, "orientation": orientation, "size": "medium"},
            timeout=10,
        )
        if resp.status_code == 200:
            videos = resp.json().get('videos', [])
            if videos:
                for vf in videos[0].get('video_files', []):
                    if vf.get('quality') == 'hd' and vf.get('width', 0) <= 1920:
                        return vf['link']
                if videos[0].get('video_files'):
                    return videos[0]['video_files'][0]['link']
    except Exception as e:
        logger.warning(f"Pexels video fetch failed: {e}")
    return None


def _fetch_pexels_batch(query, count=5, orientation='landscape'):
    """Fetch multiple Pexels image URLs for a query. Returns list of URL strings."""
    api_key = os.environ.get('PEXELS_API_KEY', '')
    if not api_key or not query:
        return []
    words = query.split()
    if len(words) > 6:
        query = ' '.join(words[:6])
    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": query, "per_page": count, "orientation": orientation},
            timeout=10,
        )
        if resp.status_code == 200:
            return [p['src']['large'] for p in resp.json().get('photos', [])]
    except Exception as e:
        logger.warning(f"Pexels batch fetch failed for '{query}': {e}")
    return []


def _try_parse_json(content):
    """Try to parse content as JSON, stripping code fences if present."""
    if not content:
        return None
    text = content.strip()
    # Strip markdown code fences
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
    text = text.strip()
    if not text.startswith('{'):
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        logger.warning("JSON parse failed, falling back to markdown path")
        return None


def _build_product_card(link_text, amazon_url, primary_color='#1565C0'):
    """Build a styled product card div with Amazon product image and urgency badge."""
    asin_match = re.search(r'/dp/([A-Z0-9]{10})', amazon_url)
    img_html = ''
    if asin_match:
        asin = asin_match.group(1)
        img_url = f"https://m.media-amazon.com/images/P/{asin}.01.LZZZZZZZ.jpg"
        img_html = (
            f'<a href="{amazon_url}" target="_blank" rel="nofollow sponsored" style="flex-shrink:0;">'
            f'<img src="{img_url}" alt="{link_text}" width="90" height="90" '
            f'style="object-fit:contain;border-radius:8px;background:#f8f8f8;padding:4px;" loading="lazy" '
            f'onerror="this.parentElement.style.display=\'none\'">'
            f'</a>'
        )
    # Urgency badge to boost conversion
    urgency_html = (
        f'<span style="display:inline-block;background:#dc2626;color:#fff;font-size:0.72em;'
        f'padding:2px 8px;border-radius:4px;margin-bottom:6px;font-weight:600;">'
        f'Popular Pick</span>'
    )
    return (
        f'<div style="border:1px solid #e5e7eb;border-radius:12px;padding:16px;margin:16px 0;'
        f'display:flex;gap:16px;align-items:center;background:#fafafa;">'
        f'{img_html}'
        f'<div>'
        f'{urgency_html}'
        f'<strong style="display:block;margin-bottom:8px;font-size:1em;color:#111;">{link_text}</strong>'
        f'<a href="{amazon_url}" target="_blank" rel="nofollow sponsored" '
        f'style="display:inline-block;background:#FF9900;color:#111;padding:7px 18px;'
        f'border-radius:6px;text-decoration:none;font-weight:700;font-size:0.88em;">'
        f'Check Price on Amazon \u2192</a>'
        f'</div></div>'
    )


def _inject_product_cards(body_html, brand_key):
    """Replace bolded Amazon links and list-item Amazon links with product cards."""
    primary_color = BRAND_SITE_CONFIG[brand_key]['primary_color']

    def _card_from_match(url, link_text):
        return _build_product_card(link_text, url, primary_color)

    # 1. Replace <strong><a href="amazon_url">text</a></strong> → product card
    body_html = re.sub(
        r'<strong><a href="([^"]*amazon\.com[^"]*)"[^>]*>([^<]+)</a></strong>',
        lambda m: _card_from_match(m.group(1), m.group(2)),
        body_html,
    )

    # 2. Replace <li> elements whose primary content is an Amazon link → product card
    def _upgrade_li(match):
        li_content = match.group(1)
        am = re.search(r'<a href="([^"]*amazon\.com[^"]*)"[^>]*>([^<]+)</a>', li_content)
        if not am:
            return match.group(0)
        return _card_from_match(am.group(1), am.group(2))

    body_html = re.sub(r'<li>(.*?)</li>', _upgrade_li, body_html, flags=re.DOTALL)

    # 3. Remove empty <ul></ul> wrappers left behind after li upgrades
    body_html = re.sub(r'<ul>\s*</ul>', '', body_html)

    return body_html


def _make_slug(topic):
    """Create a URL-safe slug from a topic string."""
    slug = topic.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug[:60]


def _build_deals_prompt(topic, pin_data, config, available_keys_str, products_text, tips_section, affiliate_tag, year):
    """Build the Gemini prompt for deals brand — first-person product review, PAS framework."""
    return f"""You are a conversational product reviewer writing for DailyDealDarling.com.
Write as a real person sharing honest product opinions. First-person, warm, relatable.

Generate ONLY valid JSON (no markdown, no backticks, no code fences).

AVAILABLE PRODUCT KEYS (use ONLY these): {available_keys_str}

TOPIC: {topic}
PIN TITLE: {pin_data.get('title', '')}
{tips_section}

WRITING STYLE:
- First-person conversational ("I grabbed this on a whim and honestly...")
- PAS framework in intro: Problem the reader has → Agitate why it's annoying → Solution you found
- Honest personal reviews — mention what you actually like AND what's meh
- Natural scarcity: "goes in/out of stock", "I've seen the price bounce around"
- Outcome-specific CTAs: "Get the exact blanket I bought", "See if it's still in stock"
- NO: comparison tables, trust badges, methodology sections, before/after cards, payment icons

OUTPUT THIS EXACT JSON STRUCTURE:
{{
  "title": "Catchy first-person title about {topic} ({year})",
  "meta_description": "155 chars max, conversational, SEO-optimized",
  "intro_paragraphs": [
    "PAS paragraph 1 — state the problem the reader probably has",
    "Agitate paragraph — why this problem is annoying/costly",
    "Solution paragraph — how you found the answer, transition to products"
  ],
  "products": [
    {{
      "name": "Product Name",
      "amazon_product_key": "key from AVAILABLE PRODUCT KEYS",
      "price": "$XX",
      "rating": 4.6,
      "review_count": "12,400+",
      "is_winner": true,
      "section_heading": "The One I Actually Kept",
      "personal_review_text": "3-4 sentences of honest first-person review. What you love, what's just okay, who it's perfect for. Sound like a real person, not a copywriter."
    }}
  ],
  "verdict_text": "2-3 sentences wrapping up your honest take. Restate the winner and why.",
  "faq": [
    {{"q": "Common question about {topic}?", "a": "Helpful 2-sentence answer."}}
  ]
}}

RULES:
- 2-4 products, the FIRST one should be is_winner: true (gets the special "The one I bought" card)
- Use ONLY keys from AVAILABLE PRODUCT KEYS for amazon_product_key
- Ratings: 4.3-4.8 (never 5.0). Review counts: realistic 1000-50000.
- BANNED: "In today's world", "it's important to note", "when it comes to", "let's dive in", "game-changer", "without further ado"
- Output ONLY valid JSON"""


def _build_fitness_prompt(topic, pin_data, config, available_keys_str, products_text, tips_section, affiliate_tag, year):
    """Build the Gemini prompt for fitness brand — educational article, gear at end only."""
    return f"""You are an experienced fitness coach writing educational content for FitOver35.com.
Your readers are men over 35 who want actionable advice, not product pitches.

Generate ONLY valid JSON (no markdown, no backticks, no code fences).

AVAILABLE PRODUCT KEYS (use ONLY these): {available_keys_str}

TOPIC: {topic}
PIN TITLE: {pin_data.get('title', '')}
{tips_section}

WRITING STYLE:
- 90% education, 10% product recommendations AT THE END only
- Teach something real: recovery science, nutrition timing, training principles
- Each section gets an actionable "The fix" tip box with a specific protocol
- Write with authority — cite studies, give specific numbers (reps, sets, grams, timing)
- Products appear ONLY in a compact "What I Use" section at the very bottom
- NO big CTAs in the body, no hard sell. Earn trust through knowledge.
- Voice: direct, confident, like a coach talking to a training partner

OUTPUT THIS EXACT JSON STRUCTURE:
{{
  "title": "Educational title about {topic} ({year})",
  "meta_description": "155 chars max, value-first, SEO-optimized",
  "intro_hook": "2-3 sentences that hook with a surprising fact, common mistake, or bold claim about {topic}. Make the reader think 'I need to know this.'",
  "sections": [
    {{
      "heading": "Section heading — educational, not salesy",
      "body_paragraphs": [
        "Paragraph 1 — teach the concept, cite a study or mechanism",
        "Paragraph 2 — explain why this matters for men over 35 specifically",
        "Paragraph 3 — practical application"
      ],
      "tip_box_text": "THE FIX: Specific actionable protocol. Example: 'Take 5g creatine monohydrate daily with your post-workout shake. Timing doesn't matter — consistency does. Load phase is optional.'"
    }}
  ],
  "gear_recommendations": [
    {{
      "name": "Product Name",
      "amazon_product_key": "key from AVAILABLE PRODUCT KEYS",
      "price": "$XX",
      "rating": 4.6,
      "review_count": "8,200+",
      "one_line_note": "What I use for [specific purpose]. Does the job, nothing fancy."
    }}
  ],
  "faq": [
    {{"q": "Common question about {topic}?", "a": "Helpful 2-sentence answer with specific numbers."}}
  ]
}}

RULES:
- 3-5 educational sections (this is the meat of the article)
- 2-4 gear recommendations at the end only
- Use ONLY keys from AVAILABLE PRODUCT KEYS for amazon_product_key
- Ratings: 4.3-4.8 (never 5.0). Review counts: realistic 1000-50000.
- BANNED: "In today's world", "it's important to note", "when it comes to", "let's dive in", "game-changer", "without further ado", "unlock your potential"
- Output ONLY valid JSON"""


def _build_menopause_prompt(topic, pin_data, config, available_keys_str, products_text, tips_section, affiliate_tag, year):
    """Build the Gemini prompt for menopause brand — warm wellness, Etsy product at end."""
    return f"""You are a warm, knowledgeable wellness writer for TheMenopausePlanner.com.
Your readers are women navigating perimenopause and menopause who want practical relief.

Generate ONLY valid JSON (no markdown, no backticks, no code fences).

AVAILABLE PRODUCT KEYS (use ONLY these): {available_keys_str}

TOPIC: {topic}
PIN TITLE: {pin_data.get('title', '')}
{tips_section}

WRITING STYLE:
- Value-first wellness content — teach practical advice (triggers, sleep, supplements, routines)
- Warm, empathetic tone — acknowledge the struggle, then provide solutions
- Each section gets a "Try this" tip box with something she can do TODAY
- Products at the end only: first a FREE symptom tracker download (trust builder), then the Etsy planner
- For Amazon products, keep it gentle: "Here's what's been helping me" — small cards, no hard sell
- NO: comparison tables, trust badges, payment icons, before/after cards, methodology sections

OUTPUT THIS EXACT JSON STRUCTURE:
{{
  "title": "Warm, practical title about {topic} ({year})",
  "meta_description": "155 chars max, empathetic, SEO-optimized",
  "intro_hook": "2-3 sentences that connect emotionally. Acknowledge what she's going through with {topic}, then promise practical help. No medical claims.",
  "sections": [
    {{
      "heading": "Section heading — practical and supportive",
      "body_paragraphs": [
        "Paragraph 1 — explain the symptom/issue in plain language",
        "Paragraph 2 — why this happens during menopause (hormonal context, not medical advice)",
        "Paragraph 3 — what actually helps, based on research and real experience"
      ],
      "tip_box_text": "TRY THIS: Specific actionable tip she can start tonight. Example: 'Keep your bedroom at 65°F. Use bamboo sheets instead of cotton — they wick moisture 3x faster. Put a cooling towel on your nightstand.'"
    }}
  ],
  "free_resource_cta": {{
    "heading": "Free: Symptom Tracker Printable",
    "description": "Track your hot flashes, sleep quality, and what's actually helping — so you can spot patterns and share real data with your doctor.",
    "button_text": "Download Free Tracker"
  }},
  "etsy_product_section": {{
    "heading": "The Menopause Wellness Planner",
    "description": "Everything in the free tracker plus daily logging, supplement tracking, appointment prep sheets, and mood patterns. Built specifically for women navigating this transition.",
    "price": "$14.99",
    "button_text": "Get the Planner on Etsy"
  }},
  "amazon_products": [
    {{
      "name": "Product Name",
      "amazon_product_key": "key from AVAILABLE PRODUCT KEYS",
      "price": "$XX",
      "rating": 4.6,
      "review_count": "5,200+",
      "one_line_note": "Helps with [specific symptom]. I keep this on my nightstand."
    }}
  ],
  "faq": [
    {{"q": "Common question about {topic} during menopause?", "a": "Helpful 2-sentence answer. No medical claims."}}
  ]
}}

RULES:
- 3-5 educational/wellness sections
- 1-3 Amazon products at the end (gentle, not salesy)
- Use ONLY keys from AVAILABLE PRODUCT KEYS for amazon_product_key
- Ratings: 4.3-4.8 (never 5.0). Review counts: realistic 1000-50000.
- NEVER make medical claims. Use "may help", "research suggests", "many women find"
- BANNED: "In today's world", "it's important to note", "when it comes to", "let's dive in", "game-changer", "without further ado"
- Output ONLY valid JSON"""


def _build_pilottools_prompt(topic, pin_data, config, available_keys_str, products_text, tips_section, affiliate_tag, year):
    """Build the Gemini prompt for pilottools brand — value-first AI tool education, SaaS recs at end."""
    return f"""You are a tech-savvy creator writing educational AI tool content for PilotTools.ai.
Your readers are creators, freelancers, and small business owners who want to work smarter with AI.

Generate ONLY valid JSON (no markdown, no backticks, no code fences).

TOPIC: {topic}
PIN TITLE: {pin_data.get('title', '')}
{tips_section}

WRITING STYLE:
- 80% education, 20% tool recommendations
- Teach real workflows: how to use tools, compare alternatives, save time
- Each section gets a "Pro Tip" box with a specific technique or workflow
- Write with authority — cite specific features, pricing, limitations
- Tool recommendations appear throughout naturally (not just at the end)
- Voice: direct, data-driven, like a smart friend who's tested everything
- Include specific pricing: "$20/month" not "affordable"

OUTPUT THIS EXACT JSON STRUCTURE:
{{
  "title": "Educational title about {topic} ({year})",
  "meta_description": "155 chars max, value-first, SEO-optimized",
  "intro_hook": "2-3 sentences that hook with a pain point about {topic}. Make the reader think 'I need to know this.'",
  "sections": [
    {{
      "heading": "Section heading — educational, specific",
      "body_paragraphs": [
        "Paragraph 1 — explain the concept or problem",
        "Paragraph 2 — specific tool or technique that solves it, with pricing",
        "Paragraph 3 — practical step-by-step application"
      ],
      "tip_box_text": "PRO TIP: Specific actionable workflow. Example: 'Use Claude for long-form writing and ChatGPT for brainstorming. This combo costs $40/month total and replaces a $2000/month content agency.'"
    }}
  ],
  "tool_recommendations": [
    {{
      "name": "Tool Name",
      "category": "writing/design/productivity/marketing",
      "price": "$XX/month or Free",
      "best_for": "One-line description of ideal use case",
      "affiliate_url": "https://toolname.com",
      "one_line_note": "What makes this stand out from alternatives."
    }}
  ],
  "faq": [
    {{"q": "Common question about {topic}?", "a": "Helpful 2-sentence answer with specific tool names and prices."}}
  ]
}}

RULES:
- 3-5 educational sections (this is the meat of the article)
- 3-5 tool recommendations with real pricing
- Do NOT use Amazon links — PilotTools uses SaaS affiliate programs
- BANNED: "In today's world", "it's important to note", "when it comes to", "let's dive in", "game-changer", "without further ado", "leverage", "empower"
- Output ONLY valid JSON"""


def _build_homedecor_prompt(topic, pin_data, config, available_keys_str, products_text, tips_section, affiliate_tag, year):
    """Build the Gemini prompt for homedecor brand — room transformation, product-forward."""
    return f"""You are a home decor enthusiast writing room-by-room transformation guides.
Your readers are women 25-45 who want beautiful homes on a real budget.

Generate ONLY valid JSON (no markdown, no backticks, no code fences).

AVAILABLE PRODUCT KEYS (use ONLY these): {available_keys_str}

TOPIC: {topic}
PIN TITLE: {pin_data.get('title', '')}
{tips_section}

WRITING STYLE:
- Visual and descriptive — help readers SEE the transformation
- Product-forward but educational: explain WHY each piece works (color theory, scale, texture)
- First-person conversational: "When I swapped my old curtains for these..."
- Each section gets a "Style Tip" box with a specific decorating technique
- Always mention approximate prices: "this $35 rug" not just "this rug"
- Reference specific room sizes: "in my 12x14 living room..."

OUTPUT THIS EXACT JSON STRUCTURE:
{{
  "title": "Room transformation title about {topic} ({year})",
  "meta_description": "155 chars max, visual, SEO-optimized",
  "intro_paragraphs": [
    "Set the scene — describe the room problem the reader probably has",
    "Agitate — why this problem makes the room feel off",
    "Solution — how specific product swaps transform the look"
  ],
  "products": [
    {{
      "name": "Product Name",
      "amazon_product_key": "key from AVAILABLE PRODUCT KEYS",
      "price": "$XX",
      "rating": 4.6,
      "review_count": "12,400+",
      "is_winner": true,
      "section_heading": "The Piece That Changed Everything",
      "personal_review_text": "3-4 sentences describing how this piece transformed the room. Be specific about colors, dimensions, and how it pairs with other items."
    }}
  ],
  "verdict_text": "2-3 sentences summarizing the room transformation and total budget.",
  "faq": [
    {{"q": "Common question about {topic}?", "a": "Helpful 2-sentence answer with decorating advice."}}
  ]
}}

RULES:
- 2-4 products, the FIRST one should be is_winner: true
- Use ONLY keys from AVAILABLE PRODUCT KEYS for amazon_product_key
- Ratings: 4.3-4.8 (never 5.0). Review counts: realistic 1000-50000.
- BANNED: "In today's world", "it's important to note", "when it comes to", "let's dive in", "game-changer", "elevate your space", "curate your aesthetic"
- Output ONLY valid JSON"""


def _build_beauty_prompt(topic, pin_data, config, available_keys_str, products_text, tips_section, affiliate_tag, year):
    """Build the Gemini prompt for beauty brand — personal review style, product-forward."""
    return f"""You are a beauty enthusiast writing honest product reviews and routine guides.
Your readers are women 20-40 who want effective skincare and makeup without overspending.

Generate ONLY valid JSON (no markdown, no backticks, no code fences).

AVAILABLE PRODUCT KEYS (use ONLY these): {available_keys_str}

TOPIC: {topic}
PIN TITLE: {pin_data.get('title', '')}
{tips_section}

WRITING STYLE:
- First-person, honest personal reviews: "I've been using this for 6 weeks and..."
- Mention your skin type (combination, acne-prone) so readers can relate
- Be specific about texture, scent, how it feels on skin, application tips
- Each section gets a "Beauty Tip" box with a specific technique
- Compare to well-known products: "performs like the $52 version but costs $14"
- Always mention specific ingredients: "the 20% vitamin C concentration"

OUTPUT THIS EXACT JSON STRUCTURE:
{{
  "title": "Honest review title about {topic} ({year})",
  "meta_description": "155 chars max, personal, SEO-optimized",
  "intro_paragraphs": [
    "Problem — the beauty frustration the reader has",
    "Agitate — why most products don't solve it (or cost too much)",
    "Solution — how you found products that actually work"
  ],
  "products": [
    {{
      "name": "Product Name",
      "amazon_product_key": "key from AVAILABLE PRODUCT KEYS",
      "price": "$XX",
      "rating": 4.6,
      "review_count": "12,400+",
      "is_winner": true,
      "section_heading": "The One I Keep Repurchasing",
      "personal_review_text": "3-4 sentences of honest first-person review. Mention texture, scent, how it feels on skin, how long it lasts. Compare to expensive alternatives if relevant."
    }}
  ],
  "verdict_text": "2-3 sentences with your honest recommendation and who each product is best for.",
  "faq": [
    {{"q": "Common question about {topic}?", "a": "Helpful 2-sentence answer with beauty advice."}}
  ]
}}

RULES:
- 2-4 products, the FIRST one should be is_winner: true
- Use ONLY keys from AVAILABLE PRODUCT KEYS for amazon_product_key
- Ratings: 4.3-4.8 (never 5.0). Review counts: realistic 1000-50000.
- BANNED: "In today's world", "it's important to note", "when it comes to", "let's dive in", "game-changer", "holy grail", "obsessed"
- Output ONLY valid JSON"""


def generate_article_for_pin(brand_key, pin_data, supabase_client):
    """Generate a brand-specific article matching a pin's topic.

    Returns (slug, content) where content is JSON string or None.
    Or (None, None) if skipped.
    """
    from .content_brain import BRAND_CONFIGS

    topic = pin_data.get('topic', '') or pin_data.get('trending_topic', '')
    if not topic:
        logger.warning("No topic in pin_data, skipping article generation")
        return None, None

    slug = _make_slug(topic)
    if not slug:
        return None, None

    # Check if article already exists — regenerate if using old template
    TEMPLATE_VERSION = 2  # Bump this to force regeneration of all articles
    try:
        # First try with template_version column
        try:
            existing = supabase_client.table('generated_articles') \
                .select('slug,template_version') \
                .eq('brand', brand_key) \
                .eq('slug', slug) \
                .limit(1) \
                .execute()
        except Exception:
            # Column might not exist yet — query without it
            existing = supabase_client.table('generated_articles') \
                .select('slug') \
                .eq('brand', brand_key) \
                .eq('slug', slug) \
                .limit(1) \
                .execute()
        if existing.data:
            row = existing.data[0]
            existing_version = row.get('template_version') or 1
            if existing_version >= TEMPLATE_VERSION:
                logger.info(f"Article '{slug}' already at template v{existing_version}, skipping")
                return slug, None
            else:
                logger.info(f"Article '{slug}' needs upgrade (v{existing_version} → v{TEMPLATE_VERSION}) — regenerating")
                # Delete old record so upsert creates a fresh one
                try:
                    supabase_client.table('generated_articles') \
                        .delete() \
                        .eq('brand', brand_key) \
                        .eq('slug', slug) \
                        .execute()
                except Exception:
                    pass
                # Fall through to regenerate with new template
    except Exception as e:
        logger.warning(f"Could not check existing articles: {e}")

    config = BRAND_CONFIGS[brand_key]
    site_config = BRAND_SITE_CONFIG[brand_key]

    # Gather affiliate products with Amazon links
    brand_amazon = AMAZON_AFFILIATE_LINKS.get(brand_key, {})
    affiliate_products = config.get('affiliate_products', {})
    category = pin_data.get('category', '')
    products = affiliate_products.get(category, [])
    if not products:
        all_products = []
        for cat_products in affiliate_products.values():
            all_products.extend(cat_products)
        products = all_products[:5]

    # Build product + Amazon link pairs for the prompt
    product_links = []
    for product in products[:6]:
        amazon_url = brand_amazon.get(product, brand_amazon.get('_default', ''))
        if amazon_url:
            product_links.append(f'- {product}: {amazon_url}')
        else:
            product_links.append(f'- {product}')
    products_text = '\n'.join(product_links) if product_links else 'none available'

    # Get tips from pin if available
    tips = pin_data.get('tips', [])
    tips_section = ''
    if tips:
        tips_section = f"""
PIN TIPS (expand on each of these in the article):
{chr(10).join(f'{i+1}. {t}' for i, t in enumerate(tips))}
"""

    year = datetime.now(timezone.utc).year
    affiliate_tag = BRAND_AFFILIATE_TAGS.get(brand_key, 'dailydealdarl-20')

    # ── Build brand-specific prompt ───────────────────────────────────────
    available_keys = [k for k in brand_amazon.keys() if k != '_default']
    available_keys_str = ', '.join(available_keys) if available_keys else 'none available'

    prompt_builders = {
        'deals': _build_deals_prompt,
        'fitness': _build_fitness_prompt,
        'menopause': _build_menopause_prompt,
        'pilottools': _build_pilottools_prompt,
        'homedecor': _build_homedecor_prompt,
        'beauty': _build_beauty_prompt,
    }
    builder = prompt_builders.get(brand_key, _build_deals_prompt)
    json_prompt = builder(
        topic, pin_data, config, available_keys_str, products_text,
        tips_section, affiliate_tag, year
    )

    try:
        article_json = generate_json(json_prompt, max_tokens=4000)
        parsed = _try_parse_json(article_json)
        if parsed and isinstance(parsed, dict):
            # Tag with brand_key so the HTML builder knows which template to use
            parsed['_brand_key'] = brand_key
            logger.info(f"JSON article generated successfully for '{topic}' ({brand_key})")
            return slug, json.dumps(parsed)
        else:
            logger.warning(f"JSON parsing failed for '{topic}' ({brand_key})")
    except Exception as e:
        logger.warning(f"JSON generation failed for '{topic}' ({brand_key}): {e}")

    return slug, None


def _extract_frontmatter(markdown_content):
    """Extract title and meta_description from frontmatter."""
    title = ""
    meta_desc = ""
    match = re.search(r'^---\s*\n(.*?)\n---', markdown_content, re.DOTALL)
    if match:
        fm = match.group(1)
        title_match = re.search(r'title:\s*"([^"]*)"', fm)
        if title_match:
            title = title_match.group(1)
        desc_match = re.search(r'meta_description:\s*"([^"]*)"', fm)
        if desc_match:
            meta_desc = desc_match.group(1)
    return title, meta_desc


def _markdown_to_html_body(markdown_content, brand_key='deals'):
    """Convert markdown article body to HTML.

    Handles: headings, bold, italic, paragraphs, lists, links, tables,
    PRODUCT_CARD comments, and the SIGNUP_FORM_PLACEHOLDER.
    """
    # Strip frontmatter
    body = re.sub(r'^---\s*\n.*?\n---\s*\n?', '', markdown_content, flags=re.DOTALL)
    body = body.strip()

    lines = body.split('\n')
    html_lines = []
    in_list = False
    in_table = False
    first_table_row = True
    table_body_started = False

    for line in lines:
        stripped = line.strip()

        # Empty line
        if not stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if in_table:
                if table_body_started:
                    html_lines.append('</tbody>')
                html_lines.append('</table></div>')
                in_table = False
            continue

        # Product card comment — pass through without wrapping in <p>
        if stripped.startswith('<!--PRODUCT_CARD:'):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(stripped)
            continue

        # Signup form placeholder
        if '[SIGNUP_FORM_PLACEHOLDER]' in stripped:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append(stripped.replace('[SIGNUP_FORM_PLACEHOLDER]', '<!-- email-signup-placeholder -->'))
            continue

        # Table rows
        if stripped.startswith('|') and '|' in stripped[1:]:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if not in_table:
                html_lines.append('<div style="overflow-x:auto"><table>')
                in_table = True
                first_table_row = True
                table_body_started = False
            # Skip separator rows like | --- | --- |
            if re.match(r'^\|[\s\-:|]+\|$', stripped):
                continue
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            cells = [c for c in cells if c]
            if first_table_row:
                html_lines.append(
                    '<thead><tr>'
                    + ''.join(f'<th>{_inline_format(c, brand_key)}</th>' for c in cells)
                    + '</tr></thead>'
                )
                first_table_row = False
            else:
                if not table_body_started:
                    html_lines.append('<tbody>')
                    table_body_started = True
                html_lines.append(
                    '<tr>'
                    + ''.join(f'<td>{_inline_format(c, brand_key)}</td>' for c in cells)
                    + '</tr>'
                )
            continue

        # Close table if we hit a non-table line
        if in_table:
            if table_body_started:
                html_lines.append('</tbody>')
            html_lines.append('</table></div>')
            in_table = False

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if heading_match:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            level = len(heading_match.group(1))
            text = _inline_format(heading_match.group(2), brand_key)
            html_lines.append(f'<h{level}>{text}</h{level}>')
            continue

        # Blockquotes
        if stripped.startswith('> '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            text = _inline_format(stripped[2:], brand_key)
            html_lines.append(f'<blockquote>{text}</blockquote>')
            continue

        # List items
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            text = _inline_format(stripped[2:], brand_key)
            html_lines.append(f'  <li>{text}</li>')
            continue

        # Regular paragraph
        if in_list:
            html_lines.append('</ul>')
            in_list = False
        text = _inline_format(stripped, brand_key)
        html_lines.append(f'<p>{text}</p>')

    if in_list:
        html_lines.append('</ul>')
    if in_table:
        if table_body_started:
            html_lines.append('</tbody>')
        html_lines.append('</table></div>')

    return '\n'.join(html_lines)


def _inline_format(text, brand_key='deals'):
    """Apply inline markdown formatting (bold, italic, links)."""
    global _APPROVED_ASINS

    affiliate_tag = BRAND_AFFILIATE_TAGS.get(brand_key, 'dailydealdarl-20')

    # Links [text](url) — Amazon affiliate links get nofollow + new tab
    def _link_replace(match):
        global _APPROVED_ASINS
        link_text = match.group(1)
        url = match.group(2)
        if 'amazon.com' in url and 'tag=' in url:
            # Sanitize: if Claude invented a /dp/ASIN not in our approved list,
            # replace with a search URL that always works.
            asin_m = re.search(r'/dp/([A-Z0-9]{10})', url)
            if asin_m:
                # Keep all /dp/ASIN links — don't convert to search URLs
                pass
            return f'<a href="{url}" target="_blank" rel="nofollow sponsored">{link_text}</a>'
        return f'<a href="{url}">{link_text}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _link_replace, text)
    # Bold **text**
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic *text*
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    return text


def _resolve_product_urls(products_list, brand_key, key_field='amazon_product_key'):
    """Resolve amazon_product_key → actual Amazon URLs for a list of products."""
    brand_amazon = AMAZON_AFFILIATE_LINKS.get(brand_key, {})
    for product in products_list:
        product_key = product.get(key_field, '')
        if product_key and product_key in brand_amazon:
            product['amazon_url'] = brand_amazon[product_key]
        else:
            product['amazon_url'] = brand_amazon.get('_default', '')
        # Generate Amazon product image from ASIN
        asin_m = re.search(r'/dp/([A-Z0-9]{10})', product.get('amazon_url', ''))
        if asin_m:
            product['product_image'] = f"https://m.media-amazon.com/images/P/{asin_m.group(1)}.01.LZZZZZZZ.jpg"
        else:
            product['product_image'] = ''


def _build_article_html(article_data, brand_key, slug, pin_data=None):
    """Build a clean brand-specific article from structured JSON data.

    Dispatches to the appropriate brand builder.
    """
    from .template_renderer import render_clean_article

    site = BRAND_SITE_CONFIG[brand_key]

    # Fetch hero image
    hero_query = article_data.get('title', slug)
    hero_url = _fetch_pexels_image(hero_query)
    article_data['hero_url'] = hero_url

    # Resolve product URLs for all product lists
    if brand_key in ('deals', 'homedecor', 'beauty'):
        _resolve_product_urls(article_data.get('products', []), brand_key)
    elif brand_key == 'fitness':
        _resolve_product_urls(article_data.get('gear_recommendations', []), brand_key)
    elif brand_key == 'menopause':
        _resolve_product_urls(article_data.get('amazon_products', []), brand_key)
    # pilottools uses SaaS affiliate links, not Amazon — no URL resolution needed

    return render_clean_article(
        brand_key=brand_key,
        article_data=article_data,
        site_config=site,
        slug=slug,
    )


def article_to_html(markdown_content, brand_key, slug, pin_data=None):
    """Convert article content to complete HTML page.

    Parses JSON from Gemini and dispatches to brand-specific template builder.
    """
    article_data = _try_parse_json(markdown_content)

    if article_data and isinstance(article_data, dict):
        return _build_article_html(article_data, brand_key, slug, pin_data)
    else:
        # Fallback: if we somehow got non-JSON, build minimal article_data
        logger.warning(f"Non-JSON content for {brand_key}/{slug}, building minimal article")
        title = slug.replace('-', ' ').title()
        minimal_data = {
            'title': title,
            'meta_description': f'{title} - {BRAND_SITE_CONFIG[brand_key]["site_name"]}',
        }
        if brand_key in ('deals', 'homedecor', 'beauty'):
            minimal_data['intro_paragraphs'] = [str(markdown_content)[:500] if markdown_content else '']
            minimal_data['products'] = []
            minimal_data['verdict_text'] = ''
            minimal_data['faq'] = []
        elif brand_key in ('fitness', 'pilottools'):
            minimal_data['intro_hook'] = str(markdown_content)[:500] if markdown_content else ''
            minimal_data['sections'] = []
            minimal_data['gear_recommendations'] = [] if brand_key == 'fitness' else []
            minimal_data['tool_recommendations'] = [] if brand_key == 'pilottools' else []
            minimal_data['faq'] = []
        else:
            minimal_data['intro_hook'] = str(markdown_content)[:500] if markdown_content else ''
            minimal_data['sections'] = []
            minimal_data['amazon_products'] = []
            minimal_data['faq'] = []
        return _build_article_html(minimal_data, brand_key, slug, pin_data)


def _sanitize_affiliate_links(html_content, brand_key):
    """Post-generation sanitization — checks every Amazon link.

    1. Rejects amazon.com/s?k= search URLs — replaces with /dp/ASIN from approved list or removes
    2. Enforces per-brand affiliate tags
    3. Converts fake/placeholder ASINs to approved defaults
    4. Fixes known AI-generated tag typos
    5. Logs any issues found for monitoring
    """
    CANONICAL_TAG = BRAND_AFFILIATE_TAGS.get(brand_key, 'dailydealdarl-20')
    brand_amazon = AMAZON_AFFILIATE_LINKS.get(brand_key, {})
    default_url = brand_amazon.get('_default', '')
    issues = []

    # ── Pass 0: Replace search URLs with real /dp/ASIN links ──
    def _fix_search_url(m):
        url = m.group(0)
        # Extract the search query to try matching against approved products
        query_match = re.search(r'[?&]k=([^&"]+)', url)
        if query_match:
            query = urllib.parse.unquote_plus(query_match.group(1)).lower()
            # Try to match against approved product keys
            for product_key, product_url in brand_amazon.items():
                if product_key == '_default':
                    continue
                if product_key.lower() in query or query in product_key.lower():
                    issues.append(f'Replaced search URL with approved ASIN for: {product_key}')
                    return product_url
        # No match — use brand default
        if default_url:
            issues.append(f'Replaced unmatched search URL with brand default')
            return default_url
        issues.append(f'Removed unmatched search URL (no default available)')
        return ''

    html_content = re.sub(
        r'https://www\.amazon\.com/s\?k=[^"]+',
        _fix_search_url,
        html_content,
    )

    # ── Pass 1: Fix known tag typos ──
    typo_map = {
        'menopauseplan-20': 'dailydealdarl-20',
    }
    if brand_key != 'fitness':
        typo_map['fitover3509-20'] = CANONICAL_TAG
    for wrong, right in typo_map.items():
        if wrong in html_content:
            count = html_content.count(wrong)
            issues.append(f'Fixed tag typo: {wrong} → {right} ({count}x)')
            html_content = html_content.replace(wrong, right)

    # ── Pass 2: Fix obviously fake ASINs ──
    fake_asin_pattern = re.compile(r'^[X0]{5,}|^XXXXXXXXXX$|^B0{9}$')

    def _fix_bad_asin(m):
        full_match = m.group(0)
        asin = m.group(1)
        if not fake_asin_pattern.match(asin):
            return full_match
        issues.append(f'Replaced fake ASIN: {asin}')
        # Use default product URL instead of search URL
        if default_url:
            asin_m = re.search(r'/dp/([A-Z0-9]{10})', default_url)
            if asin_m:
                return f'amazon.com/dp/{asin_m.group(1)}?tag={CANONICAL_TAG}'
        return f'amazon.com/dp/B001ARYU58?tag={CANONICAL_TAG}'

    html_content = re.sub(
        r'amazon\.com/dp/([A-Z0-9]{10})\?tag=[a-z0-9-]+',
        _fix_bad_asin,
        html_content,
    )

    # ── Pass 3: Force correct tag on ALL Amazon links ──
    def _enforce_tag(m):
        prefix = m.group(1)
        current_tag = m.group(2)
        if current_tag != CANONICAL_TAG:
            issues.append(f'Corrected tag: {current_tag} → {CANONICAL_TAG}')
        return f'{prefix}{CANONICAL_TAG}'

    html_content = re.sub(
        r'(amazon\.com/[^"]*[\?&]tag=)([a-z0-9-]+)',
        _enforce_tag,
        html_content,
    )

    # ── Pass 4: Ensure Amazon links WITHOUT a tag get one ──
    def _add_missing_tag(m):
        url = m.group(0)
        if 'tag=' not in url:
            sep = '&' if '?' in url else '?'
            issues.append(f'Added missing tag to Amazon link')
            return f'{url}{sep}tag={CANONICAL_TAG}'
        return url

    html_content = re.sub(
        r'https://www\.amazon\.com/[^"]+',
        _add_missing_tag,
        html_content,
    )

    if issues:
        logger.info(f'Affiliate sanitization ({brand_key}): {len(issues)} fixes — {"; ".join(issues[:5])}')

    return html_content


def validate_amazon_links(html_content, brand_key):
    """Validate every Amazon URL in the article via HTTP HEAD requests.

    - Sends HEAD request with browser user-agent, 10s timeout
    - If 404 or redirects to search page: replaces with verified ASIN from approved list
    - Verifies correct affiliate tag per brand
    - Rejects any remaining /s?k= search URLs
    - Returns (fixed_html, validation_log) tuple
    """
    CANONICAL_TAG = BRAND_AFFILIATE_TAGS.get(brand_key, 'dailydealdarl-20')
    brand_amazon = AMAZON_AFFILIATE_LINKS.get(brand_key, {})
    default_url = brand_amazon.get('_default', '')
    log = []

    # Find all Amazon URLs
    amazon_urls = re.findall(r'https://www\.amazon\.com/[^"<\s]+', html_content)
    if not amazon_urls:
        log.append('No Amazon links found')
        return html_content, log

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for url in set(amazon_urls):
        # Skip already-validated /dp/ URLs from our approved list
        asin_m = re.search(r'/dp/([A-Z0-9]{10})', url)

        # Reject search URLs outright
        if '/s?k=' in url or '/s?' in url:
            log.append(f'REJECTED search URL: {url[:80]}')
            # Try to find a replacement
            query_m = re.search(r'[?&]k=([^&"]+)', url)
            replacement = default_url
            if query_m:
                query = urllib.parse.unquote_plus(query_m.group(1)).lower()
                for key, approved_url in brand_amazon.items():
                    if key == '_default':
                        continue
                    if key.lower() in query or query in key.lower():
                        replacement = approved_url
                        break
            if replacement:
                html_content = html_content.replace(url, replacement)
                log.append(f'  → Replaced with: {replacement[:80]}')
            continue

        # Verify /dp/ links via GET request (Amazon blocks HEAD with 405)
        if asin_m:
            try:
                resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True, stream=True)
                final_url = resp.url if hasattr(resp, 'url') else ''
                resp.close()  # Don't download the full page
                is_broken = False
                if resp.status_code == 404:
                    is_broken = True
                elif '/s?k=' in final_url or '/gp/search/' in final_url:
                    is_broken = True
                elif resp.status_code == 200 and 'Page Not Found' in resp.text[:500]:
                    is_broken = True
                
                if is_broken:
                    log.append(f'BROKEN link (HTTP {resp.status_code}): {url[:80]}')
                    # Try to find a product-specific replacement from approved list
                    asin_val = asin_m.group(1)
                    replacement_found = False
                    for key, approved_url in brand_amazon.items():
                        if key == '_default':
                            continue
                        if asin_val in approved_url and approved_url != url:
                            html_content = html_content.replace(url, approved_url)
                            log.append(f'  → Replaced with approved: {approved_url[:80]}')
                            replacement_found = True
                            break
                    if not replacement_found and default_url:
                        html_content = html_content.replace(url, default_url)
                        log.append(f'  → Replaced with default: {default_url[:80]}')
                elif resp.status_code in (405, 503):
                    log.append(f'SKIP: {url[:60]} → HTTP {resp.status_code} (Amazon rate limit, not broken)')
                else:
                    log.append(f'OK: {url[:80]} → HTTP {resp.status_code}')
            except requests.RequestException as e:
                log.append(f'Request failed for {url[:60]}: {e}')
                # Don't replace on timeout — might just be rate limited

        # Verify affiliate tag
        if f'tag={CANONICAL_TAG}' not in url and 'tag=' in url:
            old_tag_m = re.search(r'tag=([a-z0-9-]+)', url)
            if old_tag_m:
                fixed_url = url.replace(f'tag={old_tag_m.group(1)}', f'tag={CANONICAL_TAG}')
                html_content = html_content.replace(url, fixed_url)
                log.append(f'Fixed tag: {old_tag_m.group(1)} → {CANONICAL_TAG}')

    logger.info(f'Amazon link validation ({brand_key}): {len(log)} entries')
    return html_content, log


def save_and_register_article(html_content, brand_key, slug, pin_data, supabase_client):
    """Save article HTML to disk and register in Supabase.

    Returns the public article URL.
    """
    # Sanitize affiliate links before saving
    html_content = _sanitize_affiliate_links(html_content, brand_key)

    # Validate Amazon links (HTTP HEAD checks, reject search URLs)
    try:
        html_content, validation_log = validate_amazon_links(html_content, brand_key)
        if validation_log:
            logger.info(f'Link validation for {brand_key}/{slug}: {len(validation_log)} checks')
            for entry in validation_log[:10]:
                logger.info(f'  {entry}')
    except Exception as e:
        logger.warning(f'Amazon link validation skipped for {brand_key}/{slug}: {e}')

    site = BRAND_SITE_CONFIG[brand_key]

    workspace = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.dirname(__file__)))
    full_dir = os.path.join(workspace, site['output_dir'])
    os.makedirs(full_dir, exist_ok=True)

    file_path = os.path.join(full_dir, f"{slug}.html")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"Article saved: {file_path}")

    # Register in Supabase
    try:
        record = {
            'brand': brand_key,
            'slug': slug,
            'trending_topic': pin_data.get('topic', '') or pin_data.get('trending_topic', ''),
            'content_preview': html_content[:500],
            'word_count': len(html_content.split()),
            'created_at': datetime.now(timezone.utc).isoformat(),
        }
        # Try with template_version first, fall back without if column doesn't exist
        try:
            record['template_version'] = 2
            supabase_client.table('generated_articles').upsert(record, on_conflict='brand,slug').execute()
        except Exception:
            record.pop('template_version', None)
            supabase_client.table('generated_articles').upsert(record, on_conflict='brand,slug').execute()
    except Exception as e:
        logger.error(f"Failed to log article to Supabase: {e}")

    article_url = f"{site['base_url']}/articles/{slug}.html"
    return article_url
