"""Landing page generator for all brands."""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# Landing page configurations
LANDING_PAGE_CONFIG = {
    "daily_deal_darling": {
        "name": "Daily Deal Darling",
        "tagline": "Never Pay Full Price Again",
        "hero_headline": "Get the FREE Ultimate Deal Tracker",
        "hero_subheadline": "Join 10,000+ savvy shoppers saving $500+/month with my proven system",
        "primary_color": "#E91E63",
        "secondary_color": "#FFC107",
        "accent_color": "#FF4081",
        "benefits": [
            {"icon": "💰", "title": "Save $500+/Month", "description": "Learn the exact system I use to find the best deals every single day"},
            {"icon": "⏰", "title": "Save Hours of Searching", "description": "Stop scrolling endlessly - my tracker shows you exactly what to buy and when"},
            {"icon": "🎯", "title": "Never Miss a Sale", "description": "Price drop alerts ensure you always buy at the lowest price"}
        ],
        "social_proof": {
            "testimonials": [
                {"name": "Sarah M.", "text": "I saved $347 in my first month using this tracker!", "rating": 5},
                {"name": "Jennifer K.", "text": "Finally a system that actually works for busy moms", "rating": 5},
                {"name": "Michelle R.", "text": "My husband thought I was crazy until he saw our savings", "rating": 5}
            ],
            "stats": ["10,000+ Downloads", "$2.3M+ Saved by Members", "4.9/5 Rating"]
        },
        "lead_magnet": {
            "title": "The Ultimate Deal Tracker",
            "description": "Your FREE printable tracker to find, track, and score the best deals",
            "features": ["Price tracking templates", "Best times to buy guide", "Coupon organization system", "Weekly deal planner"]
        },
        "cta_button": "GET FREE INSTANT ACCESS",
        "footer_text": "Join the Daily Deal Darling community and start saving today!"
    },
    "menopause_planner": {
        "name": "The Menopause Planner",
        "tagline": "Navigate Menopause with Confidence",
        "hero_headline": "FREE 30-Day Symptom Tracker",
        "hero_subheadline": "Finally understand your body and find relief from hot flashes, mood swings, and sleepless nights",
        "primary_color": "#9C27B0",
        "secondary_color": "#E1BEE7",
        "accent_color": "#AB47BC",
        "benefits": [
            {"icon": "📊", "title": "Identify Your Triggers", "description": "Track symptoms and discover patterns that help you predict and prevent flare-ups"},
            {"icon": "😴", "title": "Sleep Better Tonight", "description": "Learn evidence-based strategies for conquering night sweats and insomnia"},
            {"icon": "💪", "title": "Take Control", "description": "Armed with data, have more productive conversations with your doctor"}
        ],
        "social_proof": {
            "testimonials": [
                {"name": "Linda T.", "text": "I finally feel like I understand what my body is doing", "rating": 5},
                {"name": "Karen S.", "text": "This tracker helped me identify wine as my hot flash trigger!", "rating": 5},
                {"name": "Diane M.", "text": "My doctor was so impressed with my tracking data", "rating": 5}
            ],
            "stats": ["50,000+ Women Helped", "87% Report Feeling Better", "Trusted by Doctors"]
        },
        "lead_magnet": {
            "title": "30-Day Symptom Tracker",
            "description": "A comprehensive tracking system designed specifically for perimenopause and menopause",
            "features": ["Daily symptom tracking", "Trigger identification", "Sleep quality log", "Doctor visit prep sheets"]
        },
        "cta_button": "DOWNLOAD FREE TRACKER",
        "footer_text": "You're not alone. Join thousands of women navigating this journey together."
    },
    "nurse_planner": {
        "name": "The Nurse Planner",
        "tagline": "Thrive in Your Nursing Career",
        "hero_headline": "FREE Ultimate Shift Planner for Nurses",
        "hero_subheadline": "Stop surviving and start thriving - organize your shifts, prioritize self-care, and prevent burnout",
        "primary_color": "#00BCD4",
        "secondary_color": "#B2EBF2",
        "accent_color": "#26C6DA",
        "benefits": [
            {"icon": "📅", "title": "Master Your Schedule", "description": "Plan shifts, track swap requests, and never double-book yourself again"},
            {"icon": "❤️", "title": "Prioritize Self-Care", "description": "Built-in self-care reminders because you can't pour from an empty cup"},
            {"icon": "💪", "title": "Prevent Burnout", "description": "Intentional planning helps you set boundaries and protect your energy"}
        ],
        "social_proof": {
            "testimonials": [
                {"name": "Amanda R., RN", "text": "This planner saved my sanity during my first year in the ER", "rating": 5},
                {"name": "Jessica L., BSN", "text": "Finally a planner that understands rotating shifts!", "rating": 5},
                {"name": "Michael T., RN", "text": "The self-care sections are actually useful, not just fluff", "rating": 5}
            ],
            "stats": ["25,000+ Nurses Using It", "92% Feel More Organized", "Made by a Nurse, for Nurses"]
        },
        "lead_magnet": {
            "title": "Ultimate Shift Planner",
            "description": "The only planner designed specifically for the unique challenges of nursing",
            "features": ["Weekly shift overview", "Self-care check-ins", "Meal prep planning", "CEU tracking"]
        },
        "cta_button": "GET YOUR FREE PLANNER",
        "footer_text": "You take care of everyone else. Let us help you take care of YOU."
    },
    "adhd_planner": {
        "name": "The ADHD Planner",
        "tagline": "Work WITH Your Brain, Not Against It",
        "hero_headline": "FREE ADHD Brain Dump Worksheets",
        "hero_subheadline": "Finally quiet the mental chaos and actually get things done - designed for brains like ours",
        "primary_color": "#FF9800",
        "secondary_color": "#FFE0B2",
        "accent_color": "#FFB74D",
        "benefits": [
            {"icon": "🧠", "title": "Clear Mental Clutter", "description": "Get everything out of your head and onto paper where you can actually deal with it"},
            {"icon": "✅", "title": "Actually Complete Tasks", "description": "Break down overwhelming projects into ADHD-friendly action steps"},
            {"icon": "🎯", "title": "Reduce Overwhelm", "description": "Stop the anxiety spiral and focus on what actually matters today"}
        ],
        "social_proof": {
            "testimonials": [
                {"name": "Chris M.", "text": "These worksheets are the only thing that's ever worked for my ADHD brain", "rating": 5},
                {"name": "Taylor S.", "text": "I do a brain dump every morning now. Game changer!", "rating": 5},
                {"name": "Alex P.", "text": "Finally something designed FOR ADHD, not despite it", "rating": 5}
            ],
            "stats": ["30,000+ Downloads", "Created by Someone with ADHD", "No Shame, Just Systems"]
        },
        "lead_magnet": {
            "title": "ADHD Brain Dump Sheets",
            "description": "Structured worksheets that work with your ADHD brain, not against it",
            "features": ["Brain dump templates", "Priority sorting system", "Today's focus page", "Weekly review sheets"]
        },
        "cta_button": "DOWNLOAD FREE SHEETS",
        "footer_text": "Your brain is different, not broken. Let's build systems that work for YOU."
    },
    "fitnessmadeasy": {
        "name": "Fit Over 35",
        "tagline": "Build Strength. Burn Fat. Feel Unstoppable.",
        "hero_headline": "FREE 12-Week Workout Program for Men 35+",
        "hero_subheadline": "Build muscle, torch fat, and boost testosterone with science-backed workouts designed for your body",
        "primary_color": "#1565C0",
        "secondary_color": "#BBDEFB",
        "accent_color": "#1976D2",
        "benefits": [
            {"icon": "💪", "title": "Build Real Strength", "description": "Compound movements and progressive overload designed for the male body over 35"},
            {"icon": "🔥", "title": "Burn Stubborn Fat", "description": "Strategic HIIT and metabolic conditioning that works with your hormones, not against them"},
            {"icon": "⚡", "title": "Boost Testosterone", "description": "Exercise protocols proven to naturally increase T-levels and energy"}
        ],
        "social_proof": {
            "testimonials": [
                {"name": "Mike R., 42", "text": "Lost 30 lbs and my energy is through the roof. Wish I found this years ago!", "rating": 5},
                {"name": "David S., 38", "text": "Finally a program that understands recovery matters more as you age", "rating": 5},
                {"name": "James T., 45", "text": "Stronger at 45 than I was at 25. This program is the real deal.", "rating": 5}
            ],
            "stats": ["15,000+ Men Transformed", "Avg. 18 lbs Fat Lost", "No Equipment Required Options"]
        },
        "lead_magnet": {
            "title": "12-Week Transformation Program",
            "description": "The complete workout system built specifically for men over 35",
            "features": ["3-day and 5-day workout splits", "Exercise video library", "Nutrition guidelines for men", "Progress tracking sheets"]
        },
        "cta_button": "GET YOUR FREE PROGRAM",
        "footer_text": "Age is just a number. Your best shape is still ahead of you."
    }
}


@dataclass
class LandingPageGenerator:
    """Generates landing pages for all brands."""

    output_dir: Path = None

    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = Path(__file__).parent / "generated"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> list[str]:
        """Generate landing pages for all brands."""
        generated = []
        for brand in LANDING_PAGE_CONFIG:
            filepath = self.generate_landing_page(brand)
            generated.append(filepath)
        return generated

    def generate_landing_page(self, brand: str) -> str:
        """Generate a landing page for a specific brand."""
        config = LANDING_PAGE_CONFIG.get(brand)
        if not config:
            raise ValueError(f"Unknown brand: {brand}")

        html = self._render_template(config, brand)

        filename = f"{brand}_landing.html"
        filepath = self.output_dir / filename

        with open(filepath, "w") as f:
            f.write(html)

        return str(filepath)

    def _render_template(self, config: dict, brand: str) -> str:
        """Render the landing page template."""

        # Generate benefits HTML
        benefits_html = ""
        for benefit in config["benefits"]:
            benefits_html += f'''
            <div class="benefit-card">
                <div class="benefit-icon">{benefit["icon"]}</div>
                <h3>{benefit["title"]}</h3>
                <p>{benefit["description"]}</p>
            </div>
            '''

        # Generate testimonials HTML
        testimonials_html = ""
        for testimonial in config["social_proof"]["testimonials"]:
            stars = "⭐" * testimonial["rating"]
            testimonials_html += f'''
            <div class="testimonial-card">
                <div class="stars">{stars}</div>
                <p class="testimonial-text">"{testimonial["text"]}"</p>
                <p class="testimonial-author">- {testimonial["name"]}</p>
            </div>
            '''

        # Generate stats HTML
        stats_html = ""
        for stat in config["social_proof"]["stats"]:
            stats_html += f'<div class="stat">{stat}</div>'

        # Generate features HTML
        features_html = ""
        for feature in config["lead_magnet"]["features"]:
            features_html += f'<li>✓ {feature}</li>'

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config["hero_headline"]} | {config["name"]}</title>
    <meta name="description" content="{config["hero_subheadline"]}">

    <!-- Open Graph / Social -->
    <meta property="og:title" content="{config["hero_headline"]}">
    <meta property="og:description" content="{config["hero_subheadline"]}">
    <meta property="og:type" content="website">

    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #333;
        }}

        /* Hero Section */
        .hero {{
            background: linear-gradient(135deg, {config["primary_color"]} 0%, {config["accent_color"]} 100%);
            color: white;
            padding: 80px 20px;
            text-align: center;
        }}

        .hero-content {{
            max-width: 800px;
            margin: 0 auto;
        }}

        .hero h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 20px;
            line-height: 1.2;
        }}

        .hero p {{
            font-size: 1.25rem;
            opacity: 0.95;
            margin-bottom: 30px;
        }}

        .cta-button {{
            display: inline-block;
            background: white;
            color: {config["primary_color"]};
            padding: 18px 40px;
            font-size: 1.1rem;
            font-weight: 700;
            text-decoration: none;
            border-radius: 50px;
            transition: transform 0.3s, box-shadow 0.3s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}

        .cta-button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }}

        /* Stats Bar */
        .stats-bar {{
            background: {config["secondary_color"]};
            padding: 30px 20px;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 40px;
        }}

        .stat {{
            font-weight: 600;
            color: {config["primary_color"]};
            font-size: 1rem;
        }}

        /* Benefits Section */
        .benefits {{
            padding: 80px 20px;
            background: white;
        }}

        .benefits-container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .section-title {{
            text-align: center;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 50px;
            color: #333;
        }}

        .benefits-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 40px;
        }}

        .benefit-card {{
            text-align: center;
            padding: 30px;
            border-radius: 15px;
            background: #f8f9fa;
            transition: transform 0.3s;
        }}

        .benefit-card:hover {{
            transform: translateY(-5px);
        }}

        .benefit-icon {{
            font-size: 3rem;
            margin-bottom: 15px;
        }}

        .benefit-card h3 {{
            font-size: 1.25rem;
            margin-bottom: 10px;
            color: {config["primary_color"]};
        }}

        /* Lead Magnet Section */
        .lead-magnet {{
            background: linear-gradient(135deg, {config["secondary_color"]} 0%, white 100%);
            padding: 80px 20px;
        }}

        .lead-magnet-container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 50px;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .lead-magnet h2 {{
            color: {config["primary_color"]};
            font-size: 1.75rem;
            margin-bottom: 15px;
        }}

        .lead-magnet .description {{
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 25px;
        }}

        .lead-magnet ul {{
            list-style: none;
            text-align: left;
            max-width: 400px;
            margin: 0 auto 30px;
        }}

        .lead-magnet li {{
            padding: 10px 0;
            font-size: 1rem;
            color: #333;
        }}

        /* Email Form */
        .email-form {{
            max-width: 400px;
            margin: 0 auto;
        }}

        .email-form input {{
            width: 100%;
            padding: 15px 20px;
            font-size: 1rem;
            border: 2px solid {config["primary_color"]};
            border-radius: 10px;
            margin-bottom: 15px;
        }}

        .email-form input:focus {{
            outline: none;
            border-color: {config["accent_color"]};
        }}

        .email-form button {{
            width: 100%;
            padding: 18px;
            font-size: 1.1rem;
            font-weight: 700;
            background: {config["primary_color"]};
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: background 0.3s;
        }}

        .email-form button:hover {{
            background: {config["accent_color"]};
        }}

        .privacy-note {{
            font-size: 0.85rem;
            color: #999;
            margin-top: 15px;
        }}

        /* Testimonials */
        .testimonials {{
            padding: 80px 20px;
            background: #f8f9fa;
        }}

        .testimonials-grid {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }}

        .testimonial-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}

        .stars {{
            font-size: 1.25rem;
            margin-bottom: 15px;
        }}

        .testimonial-text {{
            font-style: italic;
            color: #555;
            margin-bottom: 15px;
        }}

        .testimonial-author {{
            font-weight: 600;
            color: {config["primary_color"]};
        }}

        /* Footer */
        .footer {{
            background: #333;
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}

        .footer p {{
            opacity: 0.9;
            margin-bottom: 20px;
        }}

        .footer-links {{
            margin-top: 20px;
        }}

        .footer-links a {{
            color: {config["secondary_color"]};
            text-decoration: none;
            margin: 0 15px;
        }}

        /* Mobile Responsiveness */
        @media (max-width: 768px) {{
            .hero h1 {{
                font-size: 1.75rem;
            }}

            .hero p {{
                font-size: 1rem;
            }}

            .cta-button {{
                padding: 15px 30px;
                font-size: 1rem;
            }}

            .lead-magnet-container {{
                padding: 30px 20px;
            }}
        }}
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="hero">
        <div class="hero-content">
            <p style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px;">{config["name"]}</p>
            <h1>{config["hero_headline"]}</h1>
            <p>{config["hero_subheadline"]}</p>
            <a href="#signup" class="cta-button">{config["cta_button"]}</a>
        </div>
    </section>

    <!-- Stats Bar -->
    <div class="stats-bar">
        {stats_html}
    </div>

    <!-- Benefits Section -->
    <section class="benefits">
        <div class="benefits-container">
            <h2 class="section-title">Why You'll Love This</h2>
            <div class="benefits-grid">
                {benefits_html}
            </div>
        </div>
    </section>

    <!-- Lead Magnet / Signup Section -->
    <section class="lead-magnet" id="signup">
        <div class="lead-magnet-container">
            <h2>{config["lead_magnet"]["title"]}</h2>
            <p class="description">{config["lead_magnet"]["description"]}</p>
            <ul>
                {features_html}
            </ul>
            <div class="email-form">
                <form action="{{{{CONVERTKIT_FORM_ACTION}}}}" method="post">
                    <input type="text" name="first_name" placeholder="Your first name">
                    <input type="email" name="email" placeholder="Your best email" required>
                    <button type="submit">{config["cta_button"]}</button>
                </form>
                <p class="privacy-note">🔒 We respect your privacy. Unsubscribe anytime.</p>
            </div>
        </div>
    </section>

    <!-- Testimonials Section -->
    <section class="testimonials">
        <div class="section-title">What People Are Saying</div>
        <div class="testimonials-grid">
            {testimonials_html}
        </div>
    </section>

    <!-- Final CTA -->
    <section class="hero" style="padding: 60px 20px;">
        <div class="hero-content">
            <h2 style="font-size: 1.75rem; margin-bottom: 20px;">Ready to Get Started?</h2>
            <a href="#signup" class="cta-button">{config["cta_button"]}</a>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <p>{config["footer_text"]}</p>
        <div class="footer-links">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Contact</a>
        </div>
        <p style="margin-top: 30px; opacity: 0.6; font-size: 0.85rem;">© 2024 {config["name"]}. All rights reserved.</p>
    </footer>

    <!-- Tracking Scripts Placeholder -->
    <!-- Add your Google Analytics, Facebook Pixel, etc. here -->

</body>
</html>'''


def generate_all_landing_pages():
    """Generate all landing pages."""
    generator = LandingPageGenerator()
    files = generator.generate_all()
    print(f"Generated {len(files)} landing pages:")
    for f in files:
        print(f"  - {f}")
    return files


if __name__ == "__main__":
    generate_all_landing_pages()
