"""Extended ASIN dictionary — 200+ additional entries.

Supplements scripts/asin_dictionary.py without modifying it.
ALL ASINs marked # VERIFY need human verification at https://www.amazon.com/dp/<ASIN>.

Usage:
    from scripts.asin_dictionary_extra import ALL_ASINS
    # ALL_ASINS = original 119 + these ~200 extra entries
"""
from __future__ import annotations

from scripts.asin_dictionary import ASIN_DICT, TAGS  # noqa: F401 — re-export

ASIN_DICT_EXTRA: dict[str, str] = {
    # ===== FITNESS — gym equipment (expanded) =====
    "cable machine": "B0BJLG4R8S",                     # VERIFY
    "functional trainer": "B09B7KPG3W",                 # VERIFY
    "landmine attachment": "B01MXLM3RH",                # VERIFY
    "landmine handle": "B07BGXX5S1",                    # VERIFY
    "safety squat bar": "B07BGXZ3KN",                   # VERIFY
    "trap bar": "B002SQUAT1",                            # VERIFY
    "hex bar": "B01LZ3GLZC",                            # VERIFY
    "ez curl bar": "B001ND04US",                         # VERIFY
    "swiss bar": "B07F1NXXT1",                           # VERIFY
    "lifting straps": "B00NQ1365S",                      # VERIFY
    "wrist wraps": "B01N4L2SJN",                         # VERIFY
    "knee sleeves": "B019FNIOJC",                        # VERIFY
    "lifting belt": "B00BO4QFNK",                        # VERIFY
    "lifting shoes": "B074N9D3HJ",                       # VERIFY
    "weightlifting shoes": "B074N82M5R",                 # VERIFY
    "dip station": "B002Y2SUU4",                          # VERIFY
    "dip belt": "B01N7RRJMF",                            # VERIFY
    "pull up station": "B07BFKJBQY",                     # VERIFY
    "pull up bar doorway": "B001EJMS6K",                 # VERIFY
    "gymnastic rings": "B01689BA3O",                      # VERIFY
    "ab wheel": "B0007IS74G",                             # VERIFY
    "parallettes": "B08DFND5SN",                         # VERIFY
    "plyo box": "B076H9X7F3",                            # VERIFY
    "medicine ball": "B0015PL0W6",                        # VERIFY
    "slam ball": "B00IUARAGO",                           # VERIFY
    "wall ball": "B008RGJR4M",                           # VERIFY
    "sandbag training": "B00K8KXKVU",                    # VERIFY
    "battle rope": "B00CO4WLQM",                         # VERIFY
    "jump rope": "B01ID497GQ",                           # VERIFY
    "speed rope": "B01EHR91PS",                          # VERIFY
    "agility ladder": "B002U2GG2E",                      # VERIFY
    "bumper plates": "B01A9CGH3O",                       # VERIFY
    "olympic plates": "B078LGYJKH",                      # VERIFY
    "weight plates": "B074DZ1LW9",                       # VERIFY
    "barbell clips": "B01LWZ63B6",                       # VERIFY
    "squat rack": "B01NBP8SW6",                          # VERIFY
    "power rack": "B01NBFE012",                          # VERIFY
    "half rack": "B08DSGTRWQ",                           # VERIFY
    "weight bench": "B078LQFPWY",                        # VERIFY
    "adjustable bench": "B07DNLP7BY",                    # VERIFY
    "flat bench": "B0087TJV2Q",                          # VERIFY
    "j hooks": "B08P4LRCHK",                             # VERIFY
    "safety arms": "B08DFQVXYS",                         # VERIFY
    "lat pulldown attachment": "B01A5GM56S",             # VERIFY
    "cable attachments": "B07H3JXN81",                   # VERIFY
    "rowing handle": "B019FNIOJD",                       # VERIFY

    # ===== FITNESS — home gym flooring =====
    "gym flooring": "B00K2TWXAY",                        # VERIFY
    "rubber gym tiles": "B07BJNC4S3",                    # VERIFY
    "horse stall mats": "B06VW3R7YD",                   # VERIFY
    "interlocking foam tiles": "B013A4ATCQ",             # VERIFY
    "gym mat": "B0021VQ5KG",                             # VERIFY

    # ===== FITNESS — recovery tools =====
    "massage gun": "B07H4N5YLH",                         # VERIFY
    "percussion massager": "B082WJN2KB",                 # VERIFY
    "mini massage gun": "B08X4HGLBZ",                    # VERIFY
    "cupping set": "B01FJ7G8JU",                         # VERIFY
    "compression boots": "B08SHFC9GN",                   # VERIFY
    "ice bath tub": "B0BK3RQMJY",                       # VERIFY
    "cold plunge": "B0BNCM1GXR",                         # VERIFY
    "ice packs": "B003TYFKUO",                           # VERIFY
    "epsom salt": "B004N7DQHA",                          # VERIFY
    "muscle roller stick": "B00GPSMVIQ",                 # VERIFY
    "lacrosse ball": "B00FOG6BJ4",                       # VERIFY
    "peanut roller": "B00XZBC6MQ",                       # VERIFY
    "infrared sauna blanket": "B08QYPCKHS",              # VERIFY
    "tens unit": "B00NCRE4GO",                           # VERIFY
    "heating pad": "B00075M1T6",                          # VERIFY

    # ===== FITNESS — wearables and tracking =====
    "fitness tracker": "B09BTP8WPW",                     # VERIFY
    "heart rate monitor": "B07PM54P4N",                  # VERIFY
    "chest strap heart rate": "B08BT3JP6D",              # VERIFY
    "food scale": "B004164SRA",                           # VERIFY
    "kitchen scale": "B01JTDG084",                       # VERIFY
    "body fat caliper": "B000G7YW74",                    # VERIFY
    "tape measure body": "B07BFZLPJM",                  # VERIFY

    # ===== FITNESS — supplements (expanded) =====
    "bcaa powder": "B00E7ICDL8",                         # VERIFY
    "eaa supplement": "B07GXJK2KP",                      # VERIFY
    "glutamine powder": "B002DYIZHQ",                    # VERIFY
    "citrulline malate": "B00EYDJNS4",                   # VERIFY
    "beta alanine": "B00EYNZFYQ",                        # VERIFY
    "hmb supplement": "B00EYNL42Q",                      # VERIFY
    "casein protein": "B004EHXKU8",                      # VERIFY
    "vegan protein powder": "B0BFBWF153",                # VERIFY
    "mass gainer": "B000GIQT06",                          # VERIFY
    "electrolyte powder": "B07Q33CN1V",                  # VERIFY
    "greens powder": "B09LT8GKBJ",                       # VERIFY
    "fiber supplement": "B0013OUQ3S",                     # VERIFY
    "digestive enzymes": "B0013OXDRG",                   # VERIFY
    "turmeric curcumin": "B01DBTFO98",                   # VERIFY
    "tart cherry extract": "B0189PYG2Q",                 # VERIFY
    "zinc supplement": "B000GIQNHY",                      # VERIFY
    "boron supplement": "B000I4C0FO",                     # VERIFY

    # ===== DEALS — kitchen appliances =====
    "air fryer": "B0936FGLQS",                           # VERIFY
    "air fryer oven": "B07GJBBGHG",                      # VERIFY
    "instant pot": "B00FLYWNYQ",                         # VERIFY
    "pressure cooker": "B01B1VC13K",                     # VERIFY
    "slow cooker": "B004P2NG0K",                         # VERIFY
    "blender": "B00VFDAKQM",                             # VERIFY
    "high speed blender": "B0758JHZM3",                  # VERIFY
    "coffee maker": "B07QGJ9YDN",                        # VERIFY
    "coffee grinder": "B001804CLU",                       # VERIFY
    "electric kettle": "B00O9GF6FK",                      # VERIFY
    "stand mixer": "B00005UP2P",                          # VERIFY
    "food processor": "B01AXM4WV2",                      # VERIFY
    "immersion blender": "B004RF7QJA",                   # VERIFY
    "toaster oven": "B01M0AWSJX",                        # VERIFY
    "rice cooker": "B0055FSN3Q",                          # VERIFY

    # ===== DEALS — kitchen tools =====
    "cast iron skillet": "B00006JSUA",                   # VERIFY
    "non stick pan": "B009HBKQ16",                       # VERIFY
    "stainless steel pan": "B009HBS2LQ",                 # VERIFY
    "knife set": "B008G1PAES",                            # VERIFY
    "chef knife": "B0061SWGFQ",                          # VERIFY
    "cutting board set": "B00DSHCNYE",                   # VERIFY
    "bakeware set": "B01KUHMJ1W",                        # VERIFY
    "meat thermometer": "B01DP40SWUI",                   # VERIFY
    "kitchen scale digital": "B01JTDG084",               # VERIFY
    "measuring cups": "B01CN3YMDG",                      # VERIFY

    # ===== DEALS — home tech =====
    "robot vacuum": "B08R4P2BT3",                        # VERIFY
    "robot vacuum mop": "B09NMN8JCF",                   # VERIFY
    "smart plug": "B01MZEEFNX",                          # VERIFY
    "smart plug pack": "B07FKVR2CY",                     # VERIFY
    "led strip lights": "B07JP5375R",                    # VERIFY
    "smart light bulbs": "B07YLJ2KGK",                   # VERIFY
    "smart thermostat": "B09XXTQPXC",                   # VERIFY
    "video doorbell": "B08N5NQ869",                      # VERIFY
    "security camera": "B08R59YH7W",                     # VERIFY
    "dash cam": "B07SRQH4R7",                            # VERIFY
    "label maker": "B005X9VZ70",                          # VERIFY

    # ===== DEALS — home organization =====
    "storage bins": "B07DFM1KMT",                        # VERIFY
    "storage bins clear": "B0006VNFSA",                  # VERIFY
    "drawer organizer": "B07QYQ6ZWV",                    # VERIFY
    "closet organizer": "B00BNKCWRK",                    # VERIFY
    "shoe rack": "B08LYLV6Y8",                           # VERIFY
    "bedding set": "B018RQUFR2",                          # VERIFY
    "mattress topper": "B07K5YN5NW",                     # VERIFY
    "pillow set": "B07D74HR6T",                          # VERIFY

    # ===== DEALS — outdoor / garage =====
    "cordless drill": "B07QG53DLH",                      # VERIFY
    "impact driver": "B07QM7MFZM",                       # VERIFY
    "pressure washer": "B08DHY4PFR",                     # VERIFY
    "leaf blower": "B0771JBN8V",                          # VERIFY
    "garden hose": "B07YKXVBT9",                         # VERIFY
    "tool set": "B082DMDV6D",                            # VERIFY

    # ===== MENOPAUSE — supplements (expanded) =====
    "black cohosh": "B0013OXBZ0",                        # VERIFY
    "evening primrose oil": "B0013OXD2S",                # VERIFY
    "red clover extract": "B0013OXH6A",                  # VERIFY
    "maca root": "B00GXHP8LA",                           # VERIFY
    "dhea supplement": "B00020IBII",                      # VERIFY
    "dong quai": "B0013OWQ64",                           # VERIFY
    "vitex supplement": "B0013OXDG4",                    # VERIFY
    "calcium vitamin d": "B003BVIFDG",                   # VERIFY
    "calcium supplement": "B003IP8S8I",                  # VERIFY
    "probiotics women": "B07HCMF9GD",                   # VERIFY
    "biotin supplement": "B0051OI91I",                   # VERIFY
    "collagen peptides": "B00K6JUG4K",                   # VERIFY
    "hyaluronic acid supplement": "B00GNK4KLY",          # VERIFY
    "dim supplement": "B005FHOXLY",                      # VERIFY

    # ===== MENOPAUSE — sleep and comfort =====
    "bamboo sheets": "B071NGDDKL",                       # VERIFY
    "cooling mattress pad": "B07PJZQYQK",               # VERIFY
    "cooling pillow memory foam": "B07H25GVFV",          # VERIFY
    "moisture wicking sheets": "B07B94V59D",             # VERIFY
    "blue light blocking glasses": "B07SDJD87K",         # VERIFY
    "red light therapy": "B07MYXZFZ3",                   # VERIFY
    "sad lamp": "B075XDLPBX",                            # VERIFY
    "light therapy lamp": "B079YBGPM5",                  # VERIFY
    "humidifier": "B07GRNKLNH",                          # VERIFY
    "cool mist humidifier": "B08GGFLXDH",               # VERIFY
    "bath salts": "B018DCUVZW",                           # VERIFY
    "magnesium bath flakes": "B000WV0RWS",               # VERIFY
    "weighted eye mask": "B07P1YSQGB",                   # VERIFY
    "white noise machine": "B00HD0ELFK",                  # VERIFY
    "sound machine": "B01L3UR8L4",                        # VERIFY
    "meditation cushion": "B01E7GJKPE",                  # VERIFY

    # ===== MENOPAUSE — personal care =====
    "vaginal moisturizer": "B07D4P86DQ",                 # VERIFY
    "personal lubricant": "B005BNPTQK",                  # VERIFY
    "menopause cream": "B07CRNRZ7F",                     # VERIFY
    "hot flash relief": "B07RY1NDJF",                    # VERIFY
    "hormone test kit": "B07WX5YK6F",                    # VERIFY
    "bone density supplement": "B003BVIFDG",             # VERIFY
    "brain supplement": "B08G1W9L4B",                    # VERIFY

    # ===== CROSS-NICHE — general wellness =====
    "resistance loop bands": "B01AVDVHTI",               # VERIFY
    "yoga mat thick": "B07D1J93MR",                      # VERIFY
    "exercise ball": "B01MSYSMHZ",                       # VERIFY
    "stretch strap": "B01LYSLT2G",                        # VERIFY
    "foam roller set": "B0040NJOA0",                      # VERIFY
    "water bottle insulated": "B082LBVHYS",              # VERIFY
    "protein shaker bottle": "B00MVMCUK8",               # VERIFY
    "meal prep containers glass": "B0767TVFBX",          # VERIFY
    "pill organizer weekly": "B0051QMXYW",               # VERIFY
    "posture corrector": "B0769GCQGG",                   # VERIFY
}

# Merged dictionary: original + extra. Import this for full coverage.
ALL_ASINS: dict[str, str] = {**ASIN_DICT, **ASIN_DICT_EXTRA}


if __name__ == "__main__":
    print(f"Original ASIN_DICT: {len(ASIN_DICT)} entries")
    print(f"Extra ASIN_DICT_EXTRA: {len(ASIN_DICT_EXTRA)} entries")
    print(f"Merged ALL_ASINS: {len(ALL_ASINS)} entries")
