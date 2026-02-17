"""Pinterest board ID mappings for all 3 brand accounts.

Maps content_brain board names to actual Pinterest board IDs.
Board IDs discovered via Make.com Pinterest API connections.

Connections:
  - Fitness Made Easy: conn 7146197
  - Daily Deal Darling: conn 6738173
  - TheMenopausePlanner: conn 6857103
"""

# Brand slug (content_brain key) → {board_name → board_id}
PINTEREST_BOARDS = {
    "fitness": {
        # Actual Pinterest boards for Fitness Made Easy account
        "Workouts for Men Over 35": "418834902785123337",    # "My personal workouts!"
        "Meal Prep & Nutrition": "418834902785124651",       # "Food"
        "Supplement Honest Reviews": "756745612325868912",   # "Fitness Goods"
        "Fat Loss After 35": "418834902785125486",           # "Muscle building"
        "Home Gym Ideas": "756745612325868912",              # "Fitness Goods"
        "Fitness Motivation": "418834902785122642",          # "motivation"
    },
    "deals": {
        # Actual Pinterest boards for Daily Deal Darling account
        "Kitchen Must-Haves": "874683627569113370",          # "Kitchen Hacks"
        "Home Organization Finds": "874683627569113339",     # "Home Organization Hacks"
        "Budget Home Decor": "874683627569021288",           # "Daily Deal Darling - Amazon Finds"
        "Self Care Products Worth It": "874683627569113342", # "Morning & Self-Care Routines"
        "Seasonal Favorites": "874683627569114674",          # "Beauty Tips"
        "Gift Ideas": "874683627569021288",                  # "Daily Deal Darling - Amazon Finds"
    },
    "menopause": {
        # Actual Pinterest boards for TheMenopausePlanner account
        "Menopause Symptoms & Relief": "1076993767079898616",  # "Hot Flash Relief Tips"
        "Hormone Balance Naturally": "1076993767079887530",    # "Menopause Wellness Tips"
        "Menopause Self Care": "1076993767079898619",          # "Menopause Self-Care"
        "Perimenopause Tips & Support": "1076993767079898628", # "Perimenopause Guide"
        "Menopause Nutrition & Wellness": "1076993767079898631",  # "Menopause Nutrition & Diet"
    },
}

# Default board per brand (highest-traffic board as fallback)
DEFAULT_BOARDS = {
    "fitness": "756745612325868912",       # Fitness Goods
    "deals": "874683627569021288",          # Daily Deal Darling - Amazon Finds
    "menopause": "1076993767079887530",     # Menopause Wellness Tips
}

# Make.com Pinterest connection IDs per brand
PINTEREST_CONNECTIONS = {
    "fitness": 7146197,
    "deals": 6738173,
    "menopause": 6857103,
}


def get_board_id(brand, board_name):
    """Resolve a content_brain board name to a Pinterest board ID.

    Args:
        brand: Brand key (e.g. 'fitness', 'deals', 'menopause')
        board_name: Board name from content_brain (e.g. 'Fat Loss After 35')

    Returns:
        Pinterest board ID string, or default board if name not found.
    """
    brand_boards = PINTEREST_BOARDS.get(brand, {})
    board_id = brand_boards.get(board_name)
    if board_id:
        return board_id

    # Fuzzy match: try case-insensitive partial match
    board_name_lower = board_name.lower()
    for name, bid in brand_boards.items():
        if board_name_lower in name.lower() or name.lower() in board_name_lower:
            return bid

    # Fall back to default board
    return DEFAULT_BOARDS.get(brand, "")
