"""Link-in-bio page generator (Stan Store / Linktree style)."""

from pathlib import Path
from dataclasses import dataclass

# Link-in-bio configurations for all brands
LINK_IN_BIO_CONFIG = {
    "daily_deal_darling": {
        "name": "Daily Deal Darling",
        "handle": "@dailydealdarling",
        "tagline": "Helping you save $500+/month on things you already buy!",
        "avatar_emoji": "💕",
        "primary_color": "#E91E63",
        "secondary_color": "#FFC107",
        "background": "linear-gradient(180deg, #E91E63 0%, #FF80AB 100%)",
        "links": [
            {
                "emoji": "🎁",
                "title": "FREE Deal Tracker",
                "subtitle": "My #1 saving tool - yours free!",
                "url": "{{LANDING_PAGE_URL}}",
                "highlight": True
            },
            {
                "emoji": "🛒",
                "title": "Today's Best Deals",
                "subtitle": "Updated daily - don't miss out!",
                "url": "{{DEALS_PAGE_URL}}",
                "highlight": False
            },
            {
                "emoji": "⭐",
                "title": "Amazon Favorites",
                "subtitle": "My tried & tested must-haves",
                "url": "{{AMAZON_STOREFRONT_URL}}",
                "highlight": False
            },
            {
                "emoji": "📱",
                "title": "TikTok",
                "subtitle": "Daily deal alerts",
                "url": "https://tiktok.com/@dailydealdarling",
                "highlight": False
            },
            {
                "emoji": "📸",
                "title": "Instagram",
                "subtitle": "More deals & behind the scenes",
                "url": "https://instagram.com/dailydealdarling",
                "highlight": False
            },
            {
                "emoji": "📺",
                "title": "YouTube",
                "subtitle": "Deal hauls & tutorials",
                "url": "https://youtube.com/@dailydealdarling",
                "highlight": False
            }
        ],
        "featured_products": [
            {"name": "Organization Bins", "price": "$12.99", "image_emoji": "📦", "url": "{{AFFILIATE_URL_1}}"},
            {"name": "Kitchen Gadget Set", "price": "$24.99", "image_emoji": "🍳", "url": "{{AFFILIATE_URL_2}}"},
            {"name": "Cleaning Bundle", "price": "$18.99", "image_emoji": "✨", "url": "{{AFFILIATE_URL_3}}"}
        ]
    },
    "menopause_planner": {
        "name": "The Menopause Planner",
        "handle": "@menopauseplanner",
        "tagline": "Helping women navigate menopause with confidence 💜",
        "avatar_emoji": "💜",
        "primary_color": "#9C27B0",
        "secondary_color": "#E1BEE7",
        "background": "linear-gradient(180deg, #9C27B0 0%, #E1BEE7 100%)",
        "links": [
            {
                "emoji": "📊",
                "title": "FREE Symptom Tracker",
                "subtitle": "Start understanding your body today",
                "url": "{{LANDING_PAGE_URL}}",
                "highlight": True
            },
            {
                "emoji": "🥗",
                "title": "Hormone Food Guide",
                "subtitle": "Eat for better hormone balance",
                "url": "{{FOOD_GUIDE_URL}}",
                "highlight": False
            },
            {
                "emoji": "😴",
                "title": "Sleep Better Guide",
                "subtitle": "Conquer night sweats & insomnia",
                "url": "{{SLEEP_GUIDE_URL}}",
                "highlight": False
            },
            {
                "emoji": "🛍️",
                "title": "My Favorite Products",
                "subtitle": "Cooling products, supplements & more",
                "url": "{{AMAZON_STOREFRONT_URL}}",
                "highlight": False
            },
            {
                "emoji": "📱",
                "title": "TikTok",
                "subtitle": "Daily menopause tips",
                "url": "https://tiktok.com/@menopauseplanner",
                "highlight": False
            },
            {
                "emoji": "📸",
                "title": "Instagram",
                "subtitle": "Community & support",
                "url": "https://instagram.com/menopauseplanner",
                "highlight": False
            }
        ],
        "featured_products": [
            {"name": "Cooling Pillow", "price": "$34.99", "image_emoji": "🧊", "url": "{{AFFILIATE_URL_1}}"},
            {"name": "Menopause Supplements", "price": "$28.99", "image_emoji": "💊", "url": "{{AFFILIATE_URL_2}}"},
            {"name": "Sleep Mask", "price": "$15.99", "image_emoji": "😴", "url": "{{AFFILIATE_URL_3}}"}
        ]
    },
    "nurse_planner": {
        "name": "The Nurse Planner",
        "handle": "@nurseplanner",
        "tagline": "Helping nurses thrive, not just survive 💙",
        "avatar_emoji": "💙",
        "primary_color": "#00BCD4",
        "secondary_color": "#B2EBF2",
        "background": "linear-gradient(180deg, #00BCD4 0%, #B2EBF2 100%)",
        "links": [
            {
                "emoji": "📅",
                "title": "FREE Shift Planner",
                "subtitle": "Finally organize your nursing life",
                "url": "{{LANDING_PAGE_URL}}",
                "highlight": True
            },
            {
                "emoji": "❤️",
                "title": "Self-Care Guide",
                "subtitle": "Prevent burnout & protect your energy",
                "url": "{{SELFCARE_GUIDE_URL}}",
                "highlight": False
            },
            {
                "emoji": "💊",
                "title": "Quick Med Reference",
                "subtitle": "Free printable reference card",
                "url": "{{MED_REFERENCE_URL}}",
                "highlight": False
            },
            {
                "emoji": "🛍️",
                "title": "Nurse Essentials",
                "subtitle": "My must-have gear & supplies",
                "url": "{{AMAZON_STOREFRONT_URL}}",
                "highlight": False
            },
            {
                "emoji": "📱",
                "title": "TikTok",
                "subtitle": "Nurse life content",
                "url": "https://tiktok.com/@nurseplanner",
                "highlight": False
            },
            {
                "emoji": "📸",
                "title": "Instagram",
                "subtitle": "Join our nurse community",
                "url": "https://instagram.com/nurseplanner",
                "highlight": False
            }
        ],
        "featured_products": [
            {"name": "Compression Socks", "price": "$18.99", "image_emoji": "🧦", "url": "{{AFFILIATE_URL_1}}"},
            {"name": "Nurse Watch", "price": "$22.99", "image_emoji": "⌚", "url": "{{AFFILIATE_URL_2}}"},
            {"name": "Badge Reel Set", "price": "$12.99", "image_emoji": "🏷️", "url": "{{AFFILIATE_URL_3}}"}
        ]
    },
    "adhd_planner": {
        "name": "The ADHD Planner",
        "handle": "@adhdplanner",
        "tagline": "Systems for brains like ours 🧠",
        "avatar_emoji": "🧡",
        "primary_color": "#FF9800",
        "secondary_color": "#FFE0B2",
        "background": "linear-gradient(180deg, #FF9800 0%, #FFE0B2 100%)",
        "links": [
            {
                "emoji": "🧠",
                "title": "FREE Brain Dump Sheets",
                "subtitle": "Get the chaos out of your head",
                "url": "{{LANDING_PAGE_URL}}",
                "highlight": True
            },
            {
                "emoji": "✅",
                "title": "ADHD Habit Tracker",
                "subtitle": "Build habits that actually stick",
                "url": "{{HABIT_TRACKER_URL}}",
                "highlight": False
            },
            {
                "emoji": "🎯",
                "title": "Focus Hacks Guide",
                "subtitle": "20 strategies that actually work",
                "url": "{{FOCUS_GUIDE_URL}}",
                "highlight": False
            },
            {
                "emoji": "🛍️",
                "title": "ADHD-Friendly Products",
                "subtitle": "Timers, fidgets, planners & more",
                "url": "{{AMAZON_STOREFRONT_URL}}",
                "highlight": False
            },
            {
                "emoji": "📱",
                "title": "TikTok",
                "subtitle": "ADHD tips & humor",
                "url": "https://tiktok.com/@adhdplanner",
                "highlight": False
            },
            {
                "emoji": "📸",
                "title": "Instagram",
                "subtitle": "ADHD community",
                "url": "https://instagram.com/adhdplanner",
                "highlight": False
            }
        ],
        "featured_products": [
            {"name": "Visual Timer", "price": "$24.99", "image_emoji": "⏰", "url": "{{AFFILIATE_URL_1}}"},
            {"name": "Fidget Cube", "price": "$12.99", "image_emoji": "🎲", "url": "{{AFFILIATE_URL_2}}"},
            {"name": "ADHD Planner", "price": "$29.99", "image_emoji": "📓", "url": "{{AFFILIATE_URL_3}}"}
        ]
    }
}


@dataclass
class LinkInBioGenerator:
    """Generates link-in-bio pages for all brands."""

    output_dir: Path = None

    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = Path(__file__).parent / "generated"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> list[str]:
        """Generate link-in-bio pages for all brands."""
        generated = []
        for brand in LINK_IN_BIO_CONFIG:
            filepath = self.generate_bio_page(brand)
            generated.append(filepath)
        return generated

    def generate_bio_page(self, brand: str) -> str:
        """Generate a link-in-bio page for a specific brand."""
        config = LINK_IN_BIO_CONFIG.get(brand)
        if not config:
            raise ValueError(f"Unknown brand: {brand}")

        html = self._render_template(config, brand)

        filename = f"{brand}_linkinbio.html"
        filepath = self.output_dir / filename

        with open(filepath, "w") as f:
            f.write(html)

        return str(filepath)

    def _render_template(self, config: dict, brand: str) -> str:
        """Render the link-in-bio template."""

        # Generate links HTML
        links_html = ""
        for link in config["links"]:
            highlight_class = "highlight" if link.get("highlight") else ""
            links_html += f'''
            <a href="{link["url"]}" class="link-button {highlight_class}" target="_blank">
                <span class="link-emoji">{link["emoji"]}</span>
                <div class="link-text">
                    <span class="link-title">{link["title"]}</span>
                    <span class="link-subtitle">{link["subtitle"]}</span>
                </div>
                <span class="link-arrow">→</span>
            </a>
            '''

        # Generate featured products HTML
        products_html = ""
        for product in config["featured_products"]:
            products_html += f'''
            <a href="{product["url"]}" class="product-card" target="_blank">
                <div class="product-image">{product["image_emoji"]}</div>
                <div class="product-name">{product["name"]}</div>
                <div class="product-price">{product["price"]}</div>
            </a>
            '''

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config["name"]} | Links</title>
    <meta name="description" content="{config["tagline"]}">

    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background: {config["background"]};
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 480px;
            margin: 0 auto;
            padding: 30px 0;
        }}

        /* Profile Section */
        .profile {{
            text-align: center;
            margin-bottom: 30px;
        }}

        .avatar {{
            width: 100px;
            height: 100px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            margin: 0 auto 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}

        .profile-name {{
            color: white;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}

        .profile-handle {{
            color: rgba(255,255,255,0.8);
            font-size: 0.95rem;
            margin-bottom: 10px;
        }}

        .profile-bio {{
            color: white;
            font-size: 0.95rem;
            max-width: 300px;
            margin: 0 auto;
            line-height: 1.5;
        }}

        /* Links Section */
        .links {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 40px;
        }}

        .link-button {{
            display: flex;
            align-items: center;
            background: white;
            padding: 16px 20px;
            border-radius: 15px;
            text-decoration: none;
            color: #333;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .link-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}

        .link-button.highlight {{
            background: {config["primary_color"]};
            color: white;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            50% {{ box-shadow: 0 4px 25px rgba(0,0,0,0.2); }}
        }}

        .link-emoji {{
            font-size: 1.5rem;
            margin-right: 15px;
        }}

        .link-text {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}

        .link-title {{
            font-weight: 600;
            font-size: 1rem;
        }}

        .link-subtitle {{
            font-size: 0.8rem;
            opacity: 0.7;
            margin-top: 2px;
        }}

        .link-arrow {{
            font-size: 1.2rem;
            opacity: 0.5;
        }}

        /* Products Section */
        .products-section {{
            margin-top: 40px;
        }}

        .section-title {{
            color: white;
            font-size: 1rem;
            font-weight: 600;
            text-align: center;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .products-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }}

        .product-card {{
            background: white;
            padding: 15px 10px;
            border-radius: 12px;
            text-align: center;
            text-decoration: none;
            color: #333;
            transition: transform 0.2s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .product-card:hover {{
            transform: translateY(-3px);
        }}

        .product-image {{
            font-size: 2rem;
            margin-bottom: 8px;
        }}

        .product-name {{
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 4px;
            line-height: 1.2;
        }}

        .product-price {{
            font-size: 0.85rem;
            color: {config["primary_color"]};
            font-weight: 700;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
        }}

        .footer p {{
            color: rgba(255,255,255,0.6);
            font-size: 0.75rem;
        }}

        .footer a {{
            color: rgba(255,255,255,0.8);
            text-decoration: none;
        }}

        /* Share Button */
        .share-button {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            font-size: 0.85rem;
            margin-bottom: 20px;
            transition: background 0.2s;
        }}

        .share-button:hover {{
            background: rgba(255,255,255,0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Profile -->
        <div class="profile">
            <div class="avatar">{config["avatar_emoji"]}</div>
            <h1 class="profile-name">{config["name"]}</h1>
            <p class="profile-handle">{config["handle"]}</p>
            <p class="profile-bio">{config["tagline"]}</p>
        </div>

        <!-- Links -->
        <div class="links">
            {links_html}
        </div>

        <!-- Featured Products -->
        <div class="products-section">
            <h2 class="section-title">Shop My Favorites</h2>
            <div class="products-grid">
                {products_html}
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Affiliate links support this page at no cost to you 💕</p>
            <p style="margin-top: 10px;">© 2024 {config["name"]}</p>
        </div>
    </div>

    <!-- Analytics tracking placeholder -->
    <script>
        // Track link clicks
        document.querySelectorAll('.link-button, .product-card').forEach(link => {{
            link.addEventListener('click', function() {{
                // Add your analytics tracking here
                console.log('Clicked:', this.querySelector('.link-title, .product-name')?.textContent);
            }});
        }});
    </script>
</body>
</html>'''


def generate_all_bio_pages():
    """Generate all link-in-bio pages."""
    generator = LinkInBioGenerator()
    files = generator.generate_all()
    print(f"Generated {len(files)} link-in-bio pages:")
    for f in files:
        print(f"  - {f}")
    return files


if __name__ == "__main__":
    generate_all_bio_pages()
