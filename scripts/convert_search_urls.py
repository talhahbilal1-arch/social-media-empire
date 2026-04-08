#!/usr/bin/env python3
"""Convert Amazon search URLs to direct product links across all brands.

Step 2a: Remove garbage/CTA search URLs (article titles used as queries)
Step 2b: Use consolidated ASIN maps from fix_*_links.py scripts
Step 2c: Fuzzy match remaining search URLs to product ASINs
"""

import os
import re
import html as htmlmod
from urllib.parse import urlparse, parse_qs, unquote_plus, quote_plus
from difflib import SequenceMatcher

# Brand directories and tags
BRANDS = {
    "outputs/fitover35-website/articles": {
        "tag": "fitover3509-20",
        "name": "fitness",
    },
    "outputs/dailydealdarling-website/articles": {
        "tag": "dailydealdarl-20",
        "name": "deals",
    },
    "outputs/menopause-planner-website/articles": {
        "tag": "dailydealdarl-20",
        "name": "menopause",
    },
}

# ============================================================
# CONSOLIDATED ASIN MAPS (from fix_fitness/deals/menopause_links.py)
# ============================================================

FITNESS_ASINS = {
    # Supplements
    "creatine": "B002DYIZEO",
    "creatine monohydrate": "B002DYIZEO",
    "nutricost creatine": "B00EIY7AXE",
    "vitamin d3": "B00GB85JR4",
    "vitamin d": "B00GB85JR4",
    "magnesium": "B000BD0RT0",
    "magnesium glycinate": "B000BD0RT0",
    "magnesium sleep": "B000BD0RT0",
    "fish oil": "B004O2I9JO",
    "omega 3": "B004O2I9JO",
    "omega-3": "B004O2I9JO",
    "ashwagandha": "B078K6DHN1",
    "ksm-66 ashwagandha": "B078K6DHN1",
    "protein powder": "B000QSNYGI",
    "whey protein": "B000QSNYGI",
    "optimum nutrition": "B000QSNYGI",
    "optimum nutrition gold standard": "B000QSNYGI",
    "optimum nutrition gold standard whey protein": "B000QSNYGI",
    "gold standard whey": "B000QSNYGI",
    "collagen": "B00K6JUG40",
    "collagen peptides": "B00K6JUG40",
    "vital proteins collagen": "B00K6JUG40",
    "zinc": "B003QB97MC",
    "zinc picolinate": "B001B4WQ1S",
    "thorne zinc": "B001B4WQ1S",
    "thorne zinc picolinate": "B001B4WQ1S",
    "bcaa": "B00E7GV65Q",
    "branched chain amino acids": "B00E7GV65Q",
    "pre workout": "B07DNRXWF7",
    "preworkout": "B07DNRXWF7",
    "c4 pre workout": "B07DNRXWF7",
    "c4 original": "B07DNRXWF7",
    "nutrabolt c4": "B07DNRXWF7",
    "multivitamin": "B000GG2I9O",
    "multivitamin men": "B000GG2I9O",
    "multivitamin for men over 35": "B000GG2I9O",
    "mens multivitamin": "B000GG2I9O",
    "probiotics": "B07K2GKZLM",
    "probiotic": "B07K2GKZLM",
    "turmeric": "B01K2JUMJQ",
    "curcumin": "B01K2JUMJQ",
    "melatonin": "B005DEK990",
    "testosterone booster": "B07DWR9BNJ",
    "test booster": "B07DWR9BNJ",
    "tongkat ali": "B084GJJT3N",
    "electrolyte": "B01IT9NLHW",
    "electrolyte powder": "B01IT9NLHW",
    "electrolytes": "B01IT9NLHW",
    # Equipment
    "resistance bands": "B01AVDVHTI",
    "resistance band": "B01AVDVHTI",
    "resistance bands set": "B01AVDVHTI",
    "adjustable dumbbells": "B001ARYU58",
    "adjustable dumbbell": "B001ARYU58",
    "bowflex dumbbells": "B001ARYU58",
    "bowflex selecttech": "B001ARYU58",
    "pull up bar": "B001EJMS6K",
    "pullup bar": "B001EJMS6K",
    "doorway pull up bar": "B001EJMS6K",
    "foam roller": "B0040EKZDY",
    "yoga mat": "B01LYBOA9L",
    "exercise mat": "B01LYBOA9L",
    "kettlebell": "B003J9E5WO",
    "massage gun": "B07MHBJYRH",
    "percussion massager": "B07MHBJYRH",
    "theragun": "B07MHBJYRH",
    "workout gloves": "B01MQGF4TQ",
    "lifting gloves": "B01MQGF4TQ",
    "weight bench": "B07DNHHNNN",
    "adjustable weight bench": "B07DNHHNNN",
    "workout bench": "B07DNHHNNN",
    "barbell": "B001K4OPY2",
    "olympic barbell": "B001K4OPY2",
    "power rack": "B01NBFIIIA",
    "squat rack": "B01NBFIIIA",
    "home gym rack": "B01NBFIIIA",
    "ab roller": "B010FN6I2C",
    "ab wheel": "B010FN6I2C",
    "jump rope": "B01ID497GU",
    "speed rope": "B01ID497GU",
    "agility ladder": "B00TXF7B5A",
    "weight plates": "B074DZ9GHM",
    "olympic weight plates": "B074DZ9GHM",
    "dip station": "B002Y2SUU4",
    "dip bars": "B002Y2SUU4",
    "gym bag": "B08CXC5W36",
    "workout bag": "B08CXC5W36",
    "lifting belt": "B019SSHDSW",
    "weightlifting belt": "B019SSHDSW",
    "lifting straps": "B00NQ1353K",
    "wrist straps": "B00NQ1353K",
    "wrist wraps": "B01N3RWL6B",
    "knee sleeves": "B019NSMQ9E",
    "knee sleeve": "B019NSMQ9E",
    "weighted vest": "B078Z3SRNG",
    "weight vest": "B078Z3SRNG",
    "battle ropes": "B00KFXIBXW",
    "battle rope": "B00KFXIBXW",
    "suspension trainer": "B002YIA5QE",
    "trx": "B002YIA5QE",
    "trx suspension": "B002YIA5QE",
    "stability ball": "B0074TWTMU",
    "exercise ball": "B0074TWTMU",
    "swiss ball": "B0074TWTMU",
    "hand gripper": "B07B1D47FB",
    "grip strengthener": "B07B1D47FB",
    "hand grip": "B07B1D47FB",
    "parallettes": "B07BRDZ2WY",
    "parallette bars": "B07BRDZ2WY",
    "push up handles": "B001QCZQCM",
    "pushup handles": "B001QCZQCM",
    "hex dumbbells": "B074DZ9GHM",
    "rubber hex dumbbells": "B074DZ9GHM",
    "dumbbell set": "B074DZ9GHM",
    # Nutrition & Kitchen
    "food scale": "B004164SRA",
    "kitchen scale": "B004164SRA",
    "meal prep containers": "B078RFVKNR",
    "meal prep container": "B078RFVKNR",
    "glass meal prep": "B078RFVKNR",
    "protein shaker": "B01LZ2GH5O",
    "shaker bottle": "B01LZ2GH5O",
    "blender bottle": "B01LZ2GH5O",
    "stretching strap": "B07YQ2BX91",
    "yoga strap": "B07YQ2BX91",
    # Recovery
    "lacrosse ball": "B06XK3DLVQ",
    "massage ball": "B06XK3DLVQ",
    "ice pack": "B01N926DGN",
    "compression sleeves": "B019NSMQ9E",
    "compression sleeve": "B019NSMQ9E",
    # Trackers & Tech
    "fitness tracker": "B0B5F5SG6P",
    "activity tracker": "B0B5F5SG6P",
    "apple watch": "B0CHX7C7WH",
    "garmin watch": "B09YVYW5QQ",
    "garmin fitness": "B09YVYW5QQ",
    "whoop band": "B09LVYY15K",
    "whoop": "B09LVYY15K",
    "heart rate monitor": "B0B5F5SG6P",
    "smart watch": "B0B5F5SG6P",
    "smartwatch": "B0B5F5SG6P",
    "body fat scale": "B09CL72LN7",
    "smart scale": "B09CL72LN7",
    "bathroom scale": "B09CL72LN7",
    # Additional fitness products
    "water bottle": "B09MKVLHZM",
    "protein bars": "B08FDPN4DK",
    "workout log": "B0BW9GDRP7",
    "training journal": "B0BW9GDRP7",
    "gym timer": "B07DNRXWF7",
    "door anchor": "B01AVDVHTI",
    "chin up bar": "B001EJMS6K",
    "mini bands": "B01AVDVHTI",
    "booty bands": "B01AVDVHTI",
    "hip band": "B01AVDVHTI",
    "cable machine": "B01NBFIIIA",
    "landmine attachment": "B001K4OPY2",
    "dip belt": "B019SSHDSW",
    "hip thrust pad": "B07DNHHNNN",
    "deadlift platform": "B001K4OPY2",
    "plyo box": "B00TXF7B5A",
    "plyometric box": "B00TXF7B5A",
    # Specific brands seen in queries
    "isopure zero carb protein": "B07KX4Q1PL",
    "isopure protein": "B07KX4Q1PL",
    "rubbermaid brilliance": "B078RFVKNR",
    "rubbermaid brilliance food storage containers": "B078RFVKNR",
    "squat wedge": "B08QRXHQKF",
    "squat wedge blocks": "B08QRXHQKF",
    "heel elevation": "B08QRXHQKF",
    "ironmaster quick lock dumbbells": "B001ARYU58",
    "ironmaster dumbbells": "B001ARYU58",
    "powerblock elite dumbbells": "B006RJ4SHM",
    "powerblock dumbbells": "B006RJ4SHM",
    "nordic naturals ultimate omega": "B004O2I9JO",
    "nordic naturals omega": "B004O2I9JO",
    "nugenix testosterone": "B07DWR9BNJ",
    "nugenix ultimate testosterone": "B07DWR9BNJ",
    # Common fitness topics mapped to products
    "high protein convenience foods": "B000QSNYGI",
    "protein snacks": "B08FDPN4DK",
    "calorie deficit": "B004164SRA",
    "mobility routine": "B0040EKZDY",
    "morning mobility": "B0040EKZDY",
    "bodyweight mobility": "B0040EKZDY",
    "mobility flow": "B0040EKZDY",
    "agile 8 mobility": "B0040EKZDY",
    "core strength": "B010FN6I2C",
    "ab finisher": "B010FN6I2C",
    "ab workout": "B010FN6I2C",
    "grip strength": "B07B1D47FB",
    "functional fitness": "B01AVDVHTI",
    "hybrid athlete training": "B01AVDVHTI",
    "cold exposure": "B01N926DGN",
    "recovery tools": "B07MHBJYRH",
    "muscle recovery": "B07MHBJYRH",
    "deadlift form": "B019SSHDSW",
    "desk job workout": "B01AVDVHTI",
    "shoulder workout": "B01AVDVHTI",
    "chest workout": "B07DNHHNNN",
    "leg workout": "B003J9E5WO",
    "back workout": "B001EJMS6K",
    "arm workout": "B001ARYU58",
    "hiit workout": "B01ID497GU",
    "cardio equipment": "B01ID497GU",
    "home gym setup": "B01NBFIIIA",
    "home gym essentials": "B01NBFIIIA",
    "sleep optimization": "B005DEK990",
    "sleep quality": "B005DEK990",
    "stretching routine": "B07YQ2BX91",
    "flexibility training": "B07YQ2BX91",
    "posture corrector": "B019NSMQ9E",
    "back support": "B019NSMQ9E",
}

DEALS_ASINS = {
    # Kitchen - Air Fryers & Appliances
    "air fryer": "B07FDJMC9Q",
    "ninja air fryer": "B07FDJMC9Q",
    "instant pot": "B00FLYWNYQ",
    "coffee maker": "B083LNYLNJ",
    "electric kettle": "B07TZ5YHJN",
    "toaster": "B00CQLJEOC",
    "rice cooker": "B007WQ9YNO",
    "slow cooker": "B004P2NG0K",
    "blender": "B00VKUWMMG",
    "portable blender": "B07KJGP5KP",
    "food processor": "B01AXM4WOO",
    "stand mixer": "B00LEAWBQO",
    "ice cream maker": "B003KYSLMW",
    "waffle maker": "B00QHDR5L2",
    # Kitchen - Knives & Cutting
    "knife set": "B07TLZXRK2",
    "kitchen knife": "B07TLZXRK2",
    "chef knife": "B000IBVB8E",
    "cutting board": "B01J9AOF1G",
    "bamboo cutting board": "B01J9AOF1G",
    "plastic cutting board": "B07P3C2CP6",
    # Kitchen - Cookware
    "cast iron skillet": "B00006JSUA",
    "nonstick pan": "B00OEFBPIC",
    "dutch oven": "B000N501BK",
    "baking sheet": "B00BPXKFKM",
    # Kitchen - Tools & Utensils
    "mixing bowls": "B01L1UN7XO",
    "measuring cups": "B074XTSVJ7",
    "silicone spatula": "B07RLVHP5T",
    "silicone utensil set": "B091CFKWZJ",
    "cooking utensil set": "B091CFKWZJ",
    "microplane grater": "B00004S7V8",
    "thermometer": "B01IHHLB3W",
    "digital thermometer": "B01IHHLB3W",
    "can opener": "B001C2S0NO",
    "colander": "B002L6RTQK",
    "whisk": "B00GZI7VVG",
    "tongs": "B07MCLVV52",
    "avocado slicer": "B0088LR592",
    "vegetable chopper": "B0764HS4SL",
    # Kitchen - Storage & Organization
    "storage containers": "B0018AJFPY",
    "food storage containers": "B0018AJFPY",
    "glass food storage": "B078RFVKNR",
    "airtight containers": "B0018AJFPY",
    "drawer dividers": "B073VB74FJ",
    "bamboo drawer dividers": "B073VB74FJ",
    "drawer organizers": "B073VB74FJ",
    "spice rack": "B071LSRDJ6",
    "lazy susan": "B07WNRVMPH",
    "utensil holder": "B08R9QJRKL",
    # Home Organization
    "organizer bins": "B07DFDS56B",
    "storage bins": "B07DFDS56B",
    "stackable bins": "B07DFDS56B",
    "clear storage bins": "B07DFDS56B",
    "label maker": "B0719RFLTQ",
    "closet organizer": "B07N4KFMHZ",
    "shoe rack": "B079DJZTJH",
    "shoe organizer": "B079DJZTJH",
    "shelf organizer": "B07DFDS56B",
    "vacuum storage bags": "B07B6LGWJR",
    "hangers": "B0796P2FNM",
    "laundry basket": "B07YVHQSC2",
    "hamper": "B07YVHQSC2",
    "trash can": "B00BEXXVKE",
    "command hooks": "B00I62F5JW",
    "tension rod": "B001B1EJ08",
    "magazine holder": "B071LSRDJ6",
    "desk organizer": "B078HNYQWN",
    "cable organizer": "B06XNPGT71",
    "storage baskets": "B07DFDS56B",
    "under bed storage": "B07YVHQSC2",
    "garage hooks": "B07P6ZMBYX",
    # Beauty/Skincare
    "silk pillowcase": "B07P3SQCV3",
    "satin pillowcase": "B07P3SQCV3",
    "led face mask": "B07D3KVL4Z",
    "face roller": "B07WRFQ1Q5",
    "jade roller": "B07WRFQ1Q5",
    "gua sha": "B082FJSSV6",
    "retinol serum": "B01MSSDEPK",
    "vitamin c serum": "B01M4MCUAF",
    "hyaluronic acid": "B004FWZAAM",
    "sunscreen": "B00X1FWFG0",
    "moisturizer": "B00WJ3O9CQ",
    "face wash": "B003YMJJSK",
    "makeup organizer": "B01LYFSAEJ",
    "hair dryer": "B084DB3F9Z",
    "curling iron": "B00GQRK0M4",
    "hot air brush": "B01LSUQSB0",
    "flat iron": "B00BQIVONY",
    "hair brush": "B084LV2PPJ",
    "nail kit": "B07GQ3ZCLW",
    "dry shampoo": "B0B94CSHXZ",
    "face masks": "B08P414JH5",
    "setting spray": "B00TQZKFAE",
    # Home Decor
    "throw pillows": "B08RDSBWTK",
    "pillow covers": "B08RDSBWTK",
    "led candles": "B07P3SQCV3",
    "scented candles": "B079SCMFDC",
    "fairy lights": "B07BKY4XL2",
    "string lights": "B07BKY4XL2",
    "wall art": "B07SXHYV33",
    "area rug": "B076J4QSGY",
    "curtains": "B0725T8FD5",
    "throw blanket": "B0BYK2N6S3",
    "faux fur blanket": "B0BYK2N6S3",
    "picture frames": "B0177MTJLE",
    "diffuser": "B07L4R62GQ",
    "essential oils": "B07L4R62GQ",
    "plant pot": "B07BHJ5DQH",
    "planter": "B07BHJ5DQH",
    "door mat": "B07SXR8L2R",
    "mirror": "B0B5XPXPNW",
    "floating frames": "B0177MTJLE",
    "succulents": "B07QJCQD3R",
    "accent chair": "B07RDVFDK3",
    # Cleaning
    "robot vacuum": "B08G4V2J5D",
    "roomba": "B08G4V2J5D",
    "cordless vacuum": "B07FSFG1QQ",
    "steam mop": "B079ZQQP4M",
    "microfiber cloths": "B009FUF6DM",
    "cleaning supplies": "B09FGSKGBM",
    "laundry detergent": "B00J4S0PVQ",
    "dryer balls": "B00GA9P5OC",
    "dish brush": "B00004OCLJ",
    "bar keepers friend": "B000V72992",
    "degreaser": "B07MFWFXFD",
    # Tech/Gadgets
    "smart plug": "B07XJ8C8F5",
    "echo dot": "B09B8V1LZ3",
    "ring doorbell": "B08N5NQ69J",
    "fire stick": "B0C3M73TRS",
    "power bank": "B07QXV6N1B",
    "portable charger": "B07QXV6N1B",
    "wireless charger": "B07THHQMHM",
    "bluetooth speaker": "B01MTB55WH",
    "phone stand": "B07F8S18D5",
    "airtag": "B0933BVK6T",
    "led desk lamp": "B06XYDNQ68",
    "under cabinet lighting": "B07L4R62GQ",
    # Water Bottles & Tumblers
    "water bottle": "B09MKVLHZM",
    "hydro flask": "B084KJWNJK",
    "stanley tumbler": "B0BQY3KJ9D",
    "iron flask": "B079F73N7R",
    "tumbler": "B07YBT7BT7",
    # Bathroom
    "shower caddy": "B07HSCGBK2",
    "bathroom organizer": "B07DFDS56B",
    "over toilet storage": "B07HSCGBK2",
    "vanity tray": "B078HNYQWN",
    # Bedroom
    "bamboo sheets": "B089HHB9LR",
    "white noise machine": "B00E6D6LQY",
    "blackout curtains": "B0725T8FD5",
    # Misc
    "calendar": "B08L7VL8KR",
    "journal": "B082MYV7PB",
    "planner": "B082MYV7PB",
    "monitor stand": "B07DWM9WNM",
    "desk": "B082RQ9X3G",
    "board games": "B00000DMBD",
    "peel stick tile": "B07NQRKN95",
    "contact paper": "B07NQRKN95",
    "coasters": "B07CXVY6GG",
    "necklace": "B08R9QJRKL",
    # Additional deals products
    "kitchen gadget": "B0764HS4SL",
    "kitchen gadgets": "B0764HS4SL",
    "kitchen tools": "B091CFKWZJ",
    "home decor": "B08RDSBWTK",
    "bathroom accessories": "B07HSCGBK2",
    "office supplies": "B078HNYQWN",
    "craft supplies": "B07TLZXRK2",
    "diy craft supplies": "B07TLZXRK2",
    "gift basket": "B079SCMFDC",
    "gift set": "B079SCMFDC",
    "reusable bags": "B07B6LGWJR",
    "lunch box": "B078RFVKNR",
    "lunch bag": "B078RFVKNR",
    "wine glasses": "B07CXVY6GG",
    "mason jars": "B0018AJFPY",
    "welcome mat": "B07SXR8L2R",
    "doormat": "B07SXR8L2R",
    # Common deals topics mapped to products
    "kitchen finds under 10": "B0764HS4SL",
    "kitchen finds under 15": "B0764HS4SL",
    "kitchen gadgets under 15": "B0764HS4SL",
    "kitchen gadgets under 10": "B0764HS4SL",
    "bathroom upgrades": "B07HSCGBK2",
    "storage cabinets": "B07DFDS56B",
    "under sink organization": "B07DFDS56B",
    "under sink cabinet organization": "B07DFDS56B",
    "kitchen utensils": "B091CFKWZJ",
    "wooden kitchen utensils": "B091CFKWZJ",
    "home spa": "B01CUV6NMS",
    "spa night essentials": "B01CUV6NMS",
    "bath products": "B01CUV6NMS",
    "closet system": "B07N4KFMHZ",
    "garage organization": "B07P6ZMBYX",
    "bookshelf styling": "B0177MTJLE",
    "bedroom cozy": "B0BYK2N6S3",
    "candles": "B079SCMFDC",
    "home fragrance": "B079SCMFDC",
    "hair tools": "B084DB3F9Z",
    "holiday gift ideas": "B079SCMFDC",
    "gift ideas": "B079SCMFDC",
    "home organization": "B07DFDS56B",
    "cabinet organization": "B07DFDS56B",
    "pantry organization": "B0018AJFPY",
    "timeless kitchen gadgets": "B0764HS4SL",
    "grandma kitchen": "B0764HS4SL",
    "crate barrel": "B08RDSBWTK",
    "williams sonoma": "B000IBVB8E",
    "budget decor": "B08RDSBWTK",
    "home design trends": "B08RDSBWTK",
    "affordable decor": "B08RDSBWTK",
}

MENOPAUSE_ASINS = {
    # Menopause Supplements
    "black cohosh": "B0019LTI86",
    "evening primrose oil": "B00DWCZWHK",
    "magnesium glycinate": "B000BD0RT0",
    "magnesium": "B000BD0RT0",
    "vitamin d3": "B00GB85JR4",
    "vitamin d": "B00GB85JR4",
    "calcium": "B001G7QUXW",
    "collagen": "B00K6JUG40",
    "collagen powder": "B00K6JUG40",
    "collagen peptides": "B00K6JUG40",
    "probiotics": "B07K2GKZLM",
    "omega 3": "B004O2I9JO",
    "fish oil": "B004O2I9JO",
    "maca root": "B007IM1XFM",
    "ashwagandha": "B078K18HYN",
    "turmeric": "B01K2JUMJQ",
    "iron supplement": "B0019GKIB4",
    "b12 vitamin": "B005DG6GK6",
    "vitamin b complex": "B005F24H30",
    "dong quai": "B000MRISUE",
    "red clover": "B000MRIVAG",
    "soy isoflavones": "B007U2GZIY",
    "dhea": "B000NRVXGS",
    "vitex": "B0019LSF8Q",
    "chasteberry": "B0019LSF8Q",
    "st johns wort": "B000GG567Q",
    "valerian root": "B0012AMVHW",
    "melatonin": "B005DEK990",
    "5 htp": "B005GFLNA6",
    "l theanine": "B000JKD7OC",
    "multivitamin women": "B00J36DNR8",
    # Sleep
    "cooling pillow": "B07C7FQBDT",
    "bamboo sheets": "B07QDFLQ7J",
    "cooling pajamas": "B07YC684QN",
    "weighted blanket": "B07H2DKQGJ",
    "silk pillowcase": "B07P3SQCV3",
    "white noise machine": "B00MY8V86O",
    "sleep mask": "B07KC5DWCC",
    "essential oils diffuser": "B07L4R62GQ",
    "diffuser": "B07L4R62GQ",
    "lavender oil": "B005V2WRZI",
    "blackout curtains": "B0725T8FD5",
    "cooling mattress pad": "B07X3BKDPH",
    "bed fan": "B07SRJ4C1B",
    "cooling blanket": "B092QNCL7Q",
    # Wellness/Self-Care
    "symptom tracker journal": "B0BW9GDRP7",
    "journal": "B0BW9GDRP7",
    "yoga mat": "B01LYBOA9L",
    "resistance bands": "B01AVDVHTI",
    "foam roller": "B0040EKZDY",
    "face roller": "B07WRFQ1Q5",
    "jade roller": "B07WRFQ1Q5",
    "gua sha": "B082FJSSV6",
    "dry brush": "B07F5B9HRN",
    "bath salts": "B01CUV6NMS",
    "epsom salt": "B004N7DQHA",
    "heating pad": "B00075M1T6",
    "hot water bottle": "B07DFPNZ4Y",
    "tens unit": "B00NCRE4GO",
    "acupressure mat": "B07BFGH97T",
    "meditation cushion": "B01MAU17HF",
    "eye mask heated": "B07KC5DWCC",
    # Clothing/Comfort
    "moisture wicking clothes": "B077GWLWTR",
    "cooling towel": "B07MWCDR79",
    "compression socks": "B077GWLWTR",
    "comfort bra": "B071KPRQKN",
    # Home
    "fan": "B07DCVY6YQ",
    "humidifier": "B013IJPTFK",
    "air purifier": "B07VVK39F7",
    "water filter": "B015QS4OG0",
    "tea set": "B073W6F8K9",
    "herbal tea": "B0009F3QL6",
    # Additional menopause products
    "menopause supplement": "B0019LTI86",
    "menopause relief": "B0019LTI86",
    "menopause tea": "B0009F3QL6",
    "menopause relief tea": "B0009F3QL6",
    "hot flash relief": "B07MWCDR79",
    "night sweats pajamas": "B07YC684QN",
    "sleep supplement": "B005DEK990",
    "stress relief supplement": "B078K18HYN",
    "bone density supplement": "B001G7QUXW",
    "heart health supplement": "B004O2I9JO",
    "mood support supplement": "B000GG567Q",
    "anxiety relief supplement": "B000JKD7OC",
    "menopause book": "B0BW9GDRP7",
    "menopause journal": "B0BW9GDRP7",
    "hormone balance supplement": "B0019LSF8Q",
    "women multivitamin": "B00J36DNR8",
    "cooling sheets": "B07QDFLQ7J",
    "portable fan": "B07DCVY6YQ",
    "personal fan": "B07DCVY6YQ",
    # Specific books/brands seen in queries
    "the menopause manifesto": "B08YWQW78Y",
    "the menopause manifesto jen gunter": "B08YWQW78Y",
    "jen gunter": "B08YWQW78Y",
    "the galveston diet": "B0B8Z7QJ8H",
    "the galveston diet mary claire haver": "B0B8Z7QJ8H",
    "the new menopause": "B0CGLK7M3H",
    "the new menopause mary claire haver": "B0CGLK7M3H",
    "mary claire haver": "B0CGLK7M3H",
    "what fresh hell is this": "B088FBC13R",
    "heather corinna": "B088FBC13R",
    "menopause book": "B08YWQW78Y",
    "doctors best magnesium glycinate": "B000BD0RT0",
    "doctors best high absorption magnesium": "B000BD0RT0",
    "plant therapy essential oil": "B005V2WRZI",
    "plant therapy clary sage": "B005V2WRZI",
    "clary sage essential oil": "B005V2WRZI",
    "nutiva organic flaxseed": "B001UIBPTI",
    "nutiva organic ground flaxseed": "B001UIBPTI",
    "organic flaxseed": "B001UIBPTI",
    "ground flaxseed": "B001UIBPTI",
    # Common menopause topics mapped to products
    "breathing techniques hot flash": "B07MWCDR79",
    "hot flash triggers": "B07MWCDR79",
    "menopause support": "B0019LTI86",
    "hormone balance": "B0019LSF8Q",
    "menopause weight loss": "B00K6JUG40",
    "menopause anxiety": "B000JKD7OC",
    "menopause sleep": "B07C7FQBDT",
    "menopause insomnia": "B005DEK990",
    "frozen shoulder menopause": "B01AVDVHTI",
    "menopause joint pain": "B01K2JUMJQ",
    "menopause brain fog": "B004O2I9JO",
    "menopause mood swings": "B000GG567Q",
    "menopause hot flashes": "B07MWCDR79",
    "menopause night sweats": "B07YC684QN",
    "menopause dry skin": "B004FWZAAM",
    "menopause hair loss": "B00K6JUG40",
    "estrogen patch": "B0BW9GDRP7",
    "hrt alternatives": "B0019LTI86",
    "natural hormone support": "B0019LTI86",
    "hormone replacement therapy": "B0BW9GDRP7",
    "perimenopause": "B0019LTI86",
    "perimenopause supplement": "B0019LTI86",
    "foods balance hormones": "B001UIBPTI",
    "glp 1 menopause": "B00K6JUG40",
    "celebrating menopause": "B08YWQW78Y",
    "menopause community": "B08YWQW78Y",
    "bamboo cooling": "B07QDFLQ7J",
    "luxury bamboo mattress pad": "B07X3BKDPH",
}

BRAND_ASIN_MAP = {
    "fitness": FITNESS_ASINS,
    "deals": DEALS_ASINS,
    "menopause": MENOPAUSE_ASINS,
}

# Filler words to strip during matching
FILLER_WORDS = {
    'the', 'best', 'top', 'amazon', 'under', 'worth', 'buying',
    'actually', 'that', 'and', 'or', 'for', 'with', 'from',
    'rated', 'review', 'reviews', 'guide', 'comparison', 'a', 'an',
    'in', 'on', 'of', 'to', 'is', 'are', 'your', 'my', 'our',
    'this', 'these', 'those', 'it', 'its', 'can', 'how', 'what',
}


def is_garbage_query(query):
    """Detect non-product garbage search queries."""
    q = query.strip()
    # Too long = article title used as search
    if len(q) > 55:
        return True
    # Contains structural markers
    if re.search(r'[:\(\)]', q):
        return True
    # Numbered list items
    if re.match(r'^\d+\.', q):
        return True
    # Single generic word
    if q.lower() in ('product', 'products', 'item', 'items', 'thing', 'things'):
        return True
    # CTA patterns
    cta = q.lower()
    cta_patterns = [
        'free', 'get weekly', 'track every', 'sign up', 'subscribe',
        'download', 'join', 'start with', 'define identity',
        'non-negotiable', 'non negotiable', 'recommended primary',
        'reclaim your', 'product.', 'discipline beats', 'bruce springsteen',
    ]
    for p in cta_patterns:
        if p in cta:
            return True
    return False


def normalize_query(query):
    """Normalize a search query for matching."""
    q = query.lower().strip()
    q = q.replace('+', ' ').replace('%20', ' ').replace('-', ' ')
    q = re.sub(r'[^a-z0-9\s]', '', q)
    words = [w for w in q.split() if w not in FILLER_WORDS and not w.isdigit()]
    return ' '.join(words)


def find_asin(query, asin_map):
    """Find ASIN using 4-tier fuzzy matching."""
    normalized = normalize_query(query)
    if not normalized:
        return None

    # Tier 1: Exact match
    if normalized in asin_map:
        return asin_map[normalized]

    # Also try the raw lowercase
    raw = query.lower().strip()
    if raw in asin_map:
        return asin_map[raw]

    # Tier 2: Substring match
    for key, asin in asin_map.items():
        if key in normalized or normalized in key:
            return asin

    # Tier 3: Word overlap (70%+)
    query_words = set(normalized.split())
    best_overlap = 0
    best_asin = None
    for key, asin in asin_map.items():
        key_words = set(key.split())
        if len(key_words) == 0:
            continue
        overlap = len(query_words & key_words)
        ratio = overlap / len(key_words)
        if ratio >= 0.7 and overlap > best_overlap:
            best_overlap = overlap
            best_asin = asin

    if best_asin:
        return best_asin

    # Tier 4: SequenceMatcher
    best_ratio = 0
    best_asin = None
    for key, asin in asin_map.items():
        ratio = SequenceMatcher(None, normalized, key).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_asin = asin

    if best_ratio > 0.6:
        return best_asin

    return None


def process_file(filepath, correct_tag, brand_name):
    """Process a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    asin_map = BRAND_ASIN_MAP[brand_name]
    stats = {"converted": 0, "garbage_removed": 0, "unmatched": 0}

    def replace_search_href(match):
        full_match = match.group(0)
        url_raw = match.group(1)
        inner_html = match.group(2)
        close_tag = match.group(3)

        decoded = htmlmod.unescape(url_raw)
        if 'amazon.com' not in decoded.lower():
            return full_match
        if '/s?' not in decoded and '/s%3F' not in decoded:
            return full_match

        # Extract search query
        parsed = urlparse(decoded)
        params = parse_qs(parsed.query)
        if 'k' not in params:
            return full_match

        query = unquote_plus(params['k'][0]).strip()

        # Check garbage
        if is_garbage_query(query):
            stats["garbage_removed"] += 1
            return inner_html  # Keep text, remove link

        # Try ASIN match
        asin = find_asin(query, asin_map)
        if asin:
            new_url = f"https://www.amazon.com/dp/{asin}?tag={correct_tag}"
            stats["converted"] += 1
            return f'<a href="{new_url}"{close_tag}{inner_html}</a>'

        stats["unmatched"] += 1
        return full_match

    # Match <a href="...amazon.com/s?k=...">...</a>
    content = re.sub(
        r'<a\s+href="([^"]*amazon[^"]*?/s\?[^"]*?)"([^>]*)>(.*?)</a>',
        replace_search_href,
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return stats


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    total = {"converted": 0, "garbage_removed": 0, "unmatched": 0}
    files_modified = 0

    for brand_dir, config in BRANDS.items():
        full_dir = os.path.join(base, brand_dir)
        if not os.path.isdir(full_dir):
            print(f"SKIP: {brand_dir} (not found)")
            continue

        brand_stats = {"converted": 0, "garbage_removed": 0, "unmatched": 0}
        brand_files = 0

        for fn in sorted(os.listdir(full_dir)):
            if not fn.endswith('.html'):
                continue
            filepath = os.path.join(full_dir, fn)
            stats = process_file(filepath, config["tag"], config["name"])
            if any(v > 0 for v in stats.values()):
                brand_files += 1
                for k, v in stats.items():
                    brand_stats[k] += v

        print(f"\n{brand_dir} ({config['name']}):")
        print(f"  Files modified: {brand_files}")
        print(f"  Search->Direct converted: {brand_stats['converted']}")
        print(f"  Garbage URLs removed: {brand_stats['garbage_removed']}")
        print(f"  Unmatched (kept as search): {brand_stats['unmatched']}")

        files_modified += brand_files
        for k, v in brand_stats.items():
            total[k] += v

    print(f"\n=== TOTALS ===")
    print(f"Files modified: {files_modified}")
    print(f"Search->Direct converted: {total['converted']}")
    print(f"Garbage URLs removed: {total['garbage_removed']}")
    print(f"Unmatched remaining: {total['unmatched']}")


if __name__ == "__main__":
    main()
