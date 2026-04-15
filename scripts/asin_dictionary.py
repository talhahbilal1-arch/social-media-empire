"""Merged ASIN dictionary for affiliate link conversion.

ALL ASINs marked # VERIFY need human verification against Amazon before use
in production. Verify by visiting https://www.amazon.com/dp/<ASIN>.

These ASINs are placeholder/best-guess and MUST be confirmed by a human before
rolling out a write pass. Unverified ASINs can dead-link revenue to 404s.
"""
from __future__ import annotations

# Affiliate tags per brand
TAGS = {
    "fitness": "fitover3509-20",
    "deals": "dailydealdarl-20",
    "menopause": "dailydealdarl-20",
}

# Search-query-keyword -> ASIN. ~120 entries across 3 brand niches.
# Keys are lowercase, hyphen/space normalized. Every ASIN needs human review.
ASIN_DICT: dict[str, str] = {
    # ===== FITNESS — protein & supplements =====
    "whey protein powder": "B00QQA0GSI",            # VERIFY
    "vegan protein powder": "B00J074W94",           # VERIFY
    "casein protein powder": "B001G7QNZG",          # VERIFY
    "plant based protein": "B07H2V8YQ9",            # VERIFY
    "creatine monohydrate": "B002DYIZEO",           # VERIFY
    "pre workout": "B00TFZZM2Y",                    # VERIFY
    "pre workout powder": "B07GC1R1PZ",             # VERIFY
    "collagen peptides powder": "B00K6JUG4C",       # VERIFY
    "omega 3 fish oil": "B002VLZHLS",               # VERIFY
    "vitamin d3": "B0032BH76O",                     # VERIFY
    "vitamin d3 5000 iu": "B004GW4S1U",             # VERIFY
    "magnesium supplement": "B00BPUY3X0",           # VERIFY
    "magnesium glycinate": "B00YQZQH32",            # VERIFY
    "zinc supplement": "B0013OXD3M",                # VERIFY
    "ashwagandha supplement": "B01ABU7GRY",         # VERIFY
    "bcaa powder": "B00E9M4XEE",                    # VERIFY
    "electrolyte powder": "B07YZY9F8Z",             # VERIFY
    "greens powder": "B07GDG5M41",                  # VERIFY
    "sleep aid supplement": "B00O9A6RJE",           # VERIFY
    "melatonin": "B00NR1YQHM",                      # VERIFY

    # ===== FITNESS — equipment =====
    "resistance bands": "B01AVDVHTI",               # VERIFY
    "resistance band set": "B077Z6VBLW",            # VERIFY
    "adjustable dumbbells": "B000VFTS9K",           # VERIFY
    "adjustable dumbbell set": "B0B5R1FP4K",        # VERIFY
    "kettlebell": "B07M6BJGDC",                     # VERIFY
    "kettlebell set": "B0058XKYJS",                 # VERIFY
    "foam roller": "B0040EGNIU",                    # VERIFY
    "massage gun": "B08P2P4BSH",                    # VERIFY
    "pull up bar": "B001EJMS6K",                    # VERIFY
    "weight bench": "B07DK2Z3XC",                   # VERIFY
    "adjustable bench": "B08N6YRZTK",               # VERIFY
    "yoga mat": "B01LP0VI8U",                       # VERIFY
    "trx strap": "B01DOGE7UE",                      # VERIFY
    "suspension trainer": "B07RG2FZRP",             # VERIFY
    "jump rope": "B01G5EMEN4",                      # VERIFY
    "weighted vest": "B07F71NZD3",                  # VERIFY
    "gym bag": "B07MPVQRYY",                        # VERIFY
    "lifting gloves": "B00TZSDPY6",                 # VERIFY
    "wrist wraps": "B071JVTHJG",                    # VERIFY
    "knee sleeves": "B01MYXF6GP",                   # VERIFY

    # ===== DEALS — kitchen small appliances =====
    "air fryer": "B08FBL5R1K",                      # VERIFY
    "ninja air fryer": "B07VHGV4K6",                # VERIFY
    "instant pot": "B00FLYWNYQ",                    # VERIFY
    "instant pot duo": "B01B1VC13K",                # VERIFY
    "blender": "B07KS9V3L3",                        # VERIFY
    "high speed blender": "B07N5QBP7S",             # VERIFY
    "coffee maker": "B077JBQZPX",                   # VERIFY
    "drip coffee maker": "B003TOAM98",              # VERIFY
    "slow cooker": "B004P2NG0K",                    # VERIFY
    "pressure cooker": "B01NBKTPTS",                # VERIFY
    "electric kettle": "B01IRIHY0K",                # VERIFY
    "stand mixer": "B00005UP2P",                    # VERIFY
    "food processor": "B0002IBE74",                 # VERIFY
    "kitchen scale": "B06WRRCG8P",                  # VERIFY
    "meat thermometer": "B01GE77QT0",               # VERIFY
    "cast iron skillet": "B00006JSUA",              # VERIFY
    "non stick pan": "B077HSZKSC",                  # VERIFY
    "knife set": "B01N5GBX1C",                      # VERIFY
    "kitchen knife set": "B07QKKG3NH",              # VERIFY
    "cutting board": "B0722WZ2MY",                  # VERIFY
    "spice rack": "B07RBKGDV7",                     # VERIFY
    "vacuum sealer": "B07YBFZFV4",                  # VERIFY
    "dutch oven": "B000LEXR0K",                     # VERIFY
    "rice cooker": "B003TOAM98",                    # VERIFY
    "toaster oven": "B01LXNHUYS",                   # VERIFY
    "immersion blender": "B00Z7ZKIAQ",              # VERIFY
    "espresso machine": "B01N7LUVDO",               # VERIFY
    "water filter pitcher": "B0060MWTZS",           # VERIFY
    "reusable food wraps": "B01HPKHIO0",            # VERIFY

    # ===== DEALS — home & smart =====
    "robot vacuum": "B07GNP5NRD",                   # VERIFY
    "smart plug": "B01MZEEFNX",                     # VERIFY
    "led strip lights": "B08LVCVWKM",               # VERIFY
    "led strips": "B07TDYP43F",                     # VERIFY
    "bedding set": "B07VJDFHD9",                    # VERIFY
    "sheet set": "B00N30J6VI",                      # VERIFY
    "storage bin": "B07T5HLWLJ",                    # VERIFY
    "storage bins": "B01N46N7DY",                   # VERIFY
    "label maker": "B08QVMCF2H",                    # VERIFY
    "robot vacuum cleaner": "B09B8RVKGW",           # VERIFY
    "cordless vacuum": "B08CRJ7SS5",                # VERIFY
    "air purifier": "B07VVK39F7",                   # VERIFY
    "humidifier": "B07TT41KVL",                     # VERIFY
    "smart light bulbs": "B07XLML2YS",              # VERIFY
    "memory foam pillow": "B07D74HR6T",             # VERIFY
    "throw blanket": "B07G3YNLKB",                  # VERIFY
    "desk organizer": "B07QYQ6ZWV",                 # VERIFY

    # ===== MENOPAUSE — herbal & supplements =====
    "black cohosh": "B001LF39WG",                   # VERIFY
    "evening primrose oil": "B000GFPD7G",           # VERIFY
    "red clover supplement": "B0013OUMGO",          # VERIFY
    "maca root": "B01A2VP4ME",                      # VERIFY
    "maca root powder": "B00KLGUTPS",               # VERIFY
    "dhea supplement": "B000GFSUEG",                # VERIFY
    "calcium d3": "B0019LTGNU",                     # VERIFY
    "calcium with vitamin d3": "B003JH8HEA",        # VERIFY
    "probiotics women": "B01M0NCS2U",               # VERIFY
    "collagen peptides": "B00K6JUG4C",              # VERIFY
    "biotin supplement": "B01EU4XTHG",              # VERIFY
    "menopause multivitamin": "B072LQ2S3S",         # VERIFY
    "phytoestrogen supplement": "B0013OUMGO",       # VERIFY
    "soy isoflavones": "B0013OXH2M",                # VERIFY
    "flaxseed oil": "B0013OXNGY",                   # VERIFY
    "vitamin b complex": "B00014D2FI",              # VERIFY
    "chamomile tea": "B000GG0BKY",                  # VERIFY
    "adaptogens supplement": "B07QQK5LJY",          # VERIFY
    "ashwagandha root": "B01ABU7GRY",               # VERIFY
    "rhodiola rosea": "B001E10C3S",                 # VERIFY
    "l theanine": "B0013OXKHC",                     # VERIFY
    "gaba supplement": "B0013OUMGS",                # VERIFY

    # ===== MENOPAUSE — sleep & cooling =====
    "cooling pillow": "B07H25GVFV",                 # VERIFY
    "cooling sheets": "B07PJZQYQK",                 # VERIFY
    "cooling bed sheets": "B07V9SFQXD",             # VERIFY
    "moisture wicking pajamas": "B07QQXG5BW",       # VERIFY
    "cooling pajamas": "B08FD7HCHZ",                # VERIFY
    "silk pillowcase": "B07K71B3HD",                # VERIFY
    "blackout curtains": "B07BLFMRQF",              # VERIFY
    "weighted blanket": "B07FPKQS67",               # VERIFY
    "aromatherapy diffuser": "B01KQNBXCS",          # VERIFY
    "essential oil diffuser": "B01E7QE0D0",         # VERIFY
    "lavender essential oil": "B0748HBR8J",         # VERIFY
}


def verify_asin(asin: str) -> int:
    """HEAD request to amazon.com/dp/<asin>; returns HTTP status code.

    Use responsibly — rate-limited by Amazon. Not called by default.
    Returns 0 on any exception (timeout, block, bad URL).
    """
    import urllib.request
    req = urllib.request.Request(
        f"https://www.amazon.com/dp/{asin}",
        method="HEAD",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status
    except Exception:  # noqa: BLE001
        return 0


if __name__ == "__main__":
    print(f"ASIN_DICT entries: {len(ASIN_DICT)}")
    print(f"Brands: {list(TAGS.keys())}")
