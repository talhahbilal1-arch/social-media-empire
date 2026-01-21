"""Lead magnet PDF generation utilities."""

import os
import logging
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

# Note: For actual PDF generation, you'd use a library like:
# - reportlab (pure Python)
# - weasyprint (HTML to PDF)
# - FPDF2 (simple PDFs)
# This module provides the structure and content generation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lead magnet content configurations
LEAD_MAGNETS = {
    "daily_deal_darling": {
        "deals_guide": {
            "title": "The Ultimate Deals Guide",
            "subtitle": "50+ Ways to Save Money on Products You Love",
            "sections": [
                {
                    "heading": "Where to Find the Best Deals",
                    "content": [
                        "Amazon Lightning Deals - check daily at 3 AM PST",
                        "Target Circle Week - quarterly sales event",
                        "Rakuten cashback - stack with store sales",
                        "Honey browser extension - automatic coupons",
                        "Slickdeals community - user-submitted deals"
                    ]
                },
                {
                    "heading": "My Favorite Deal-Finding Apps",
                    "content": [
                        "Ibotta - cashback on groceries",
                        "Fetch Rewards - scan any receipt",
                        "RetailMeNot - coupon codes",
                        "ShopSavvy - price comparison",
                        "CamelCamelCamel - Amazon price history"
                    ]
                },
                {
                    "heading": "Best Times to Shop",
                    "content": [
                        "Prime Day (July) - Amazon's biggest sale",
                        "Black Friday/Cyber Monday - November",
                        "End of season - clearance deals",
                        "New product launches - old stock discounts",
                        "Tuesday mornings - many stores restock sales"
                    ]
                }
            ],
            "cta": "Follow @dailydealdarling for daily deal alerts!"
        }
    },
    "menopause_planner": {
        "symptom_tracker": {
            "title": "Menopause Symptom Tracker",
            "subtitle": "Track, Understand, and Manage Your Symptoms",
            "sections": [
                {
                    "heading": "Daily Tracking Page",
                    "content": [
                        "Date: ___________",
                        "Hot flashes: □ None □ Mild □ Moderate □ Severe",
                        "Sleep quality: 1 2 3 4 5 6 7 8 9 10",
                        "Mood: 😊 😐 😢 😤 😰",
                        "Energy level: Low / Medium / High",
                        "Notes: _________________________"
                    ]
                },
                {
                    "heading": "Common Triggers to Track",
                    "content": [
                        "Caffeine intake",
                        "Alcohol consumption",
                        "Spicy foods",
                        "Stress levels",
                        "Exercise",
                        "Room temperature"
                    ]
                },
                {
                    "heading": "Weekly Reflection Questions",
                    "content": [
                        "What symptom was most challenging this week?",
                        "What helped me feel better?",
                        "Did I notice any patterns?",
                        "What do I want to discuss with my doctor?",
                        "What self-care did I practice?"
                    ]
                }
            ],
            "cta": "Get the full Menopause Planner at menopauseplanner.com"
        }
    },
    "nurse_planner": {
        "shift_planner": {
            "title": "Nurse Shift Survival Planner",
            "subtitle": "Organize Your Shifts, Protect Your Energy",
            "sections": [
                {
                    "heading": "Pre-Shift Checklist",
                    "content": [
                        "□ Meal prepped and packed",
                        "□ Scrubs laid out",
                        "□ Badge and ID ready",
                        "□ Comfortable shoes clean",
                        "□ Water bottle filled",
                        "□ Healthy snacks packed",
                        "□ Phone charger in bag"
                    ]
                },
                {
                    "heading": "Shift Notes Template",
                    "content": [
                        "Date: _____ Shift: Day / Night",
                        "Patient assignments: _________",
                        "Priority tasks: _____________",
                        "Medications due: ____________",
                        "Questions for charge nurse: ____",
                        "End of shift notes: __________"
                    ]
                },
                {
                    "heading": "Self-Care After Shift",
                    "content": [
                        "□ Decompress for 10 minutes",
                        "□ Shower and change clothes",
                        "□ Eat a nourishing meal",
                        "□ Hydrate (not just coffee!)",
                        "□ 5 minutes of stretching",
                        "□ Set boundaries - no work talk"
                    ]
                }
            ],
            "cta": "Get the complete Nurse Planner at nurseplanner.com"
        }
    },
    "adhd_planner": {
        "productivity_guide": {
            "title": "ADHD-Friendly Productivity Guide",
            "subtitle": "Work With Your Brain, Not Against It",
            "sections": [
                {
                    "heading": "The Dopamine Menu",
                    "content": [
                        "Quick hits (5 min): Listen to one song, stretch, get water",
                        "Medium (15 min): Short walk, watch one video, snack break",
                        "Long (30+ min): Exercise, creative hobby, video game",
                        "Fill in YOUR dopamine menu:",
                        "Quick: _________",
                        "Medium: _________",
                        "Long: _________"
                    ]
                },
                {
                    "heading": "Task Initiation Hacks",
                    "content": [
                        "1. Make it smaller - what's the FIRST tiny step?",
                        "2. Body double - work alongside someone",
                        "3. Set a timer - just 10 minutes",
                        "4. Change location - try a coffee shop",
                        "5. Reward yourself - dopamine hit after"
                    ]
                },
                {
                    "heading": "Time Blindness Solutions",
                    "content": [
                        "Visual timers you can SEE time passing",
                        "Backwards planning - start from deadline",
                        "Buffer time - add 50% to estimates",
                        "Transition alerts - 15, 10, 5 min warnings",
                        "Calendar blocking - schedule EVERYTHING"
                    ]
                }
            ],
            "cta": "Get the full ADHD Planner at adhdplanner.com"
        }
    }
}


@dataclass
class PDFGenerator:
    """Generates lead magnet PDFs."""

    output_dir: Path = Path("./output")
    brand_colors: dict = None

    def __post_init__(self):
        self.output_dir.mkdir(exist_ok=True)

        if self.brand_colors is None:
            self.brand_colors = {
                "daily_deal_darling": {"primary": "#E91E63", "secondary": "#FFC107"},
                "menopause_planner": {"primary": "#9C27B0", "secondary": "#E1BEE7"},
                "nurse_planner": {"primary": "#00BCD4", "secondary": "#B2EBF2"},
                "adhd_planner": {"primary": "#FF9800", "secondary": "#FFE0B2"}
            }

    def generate_html_content(
        self,
        brand: str,
        lead_magnet_key: str
    ) -> str:
        """Generate HTML content for PDF conversion."""
        brand_data = LEAD_MAGNETS.get(brand, {})
        magnet_data = brand_data.get(lead_magnet_key)

        if not magnet_data:
            raise ValueError(f"Lead magnet not found: {brand}/{lead_magnet_key}")

        colors = self.brand_colors.get(brand, {"primary": "#333", "secondary": "#eee"})

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: letter;
            margin: 1in;
        }}
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            text-align: center;
            padding: 40px 0;
            border-bottom: 3px solid {colors['primary']};
            margin-bottom: 30px;
        }}
        .title {{
            font-size: 32px;
            font-weight: bold;
            color: {colors['primary']};
            margin-bottom: 10px;
        }}
        .subtitle {{
            font-size: 18px;
            color: #666;
        }}
        .section {{
            margin: 30px 0;
            page-break-inside: avoid;
        }}
        .section-heading {{
            font-size: 22px;
            font-weight: bold;
            color: {colors['primary']};
            border-left: 4px solid {colors['primary']};
            padding-left: 15px;
            margin-bottom: 15px;
        }}
        .content-list {{
            list-style: none;
            padding: 0;
        }}
        .content-list li {{
            padding: 10px 0;
            padding-left: 30px;
            position: relative;
            border-bottom: 1px solid #eee;
        }}
        .content-list li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: {colors['primary']};
            font-weight: bold;
        }}
        .cta-box {{
            background: {colors['secondary']};
            padding: 25px;
            text-align: center;
            border-radius: 10px;
            margin-top: 40px;
        }}
        .cta-text {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
        }}
        .footer {{
            text-align: center;
            padding-top: 30px;
            border-top: 1px solid #eee;
            margin-top: 40px;
            font-size: 12px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">{magnet_data['title']}</div>
        <div class="subtitle">{magnet_data['subtitle']}</div>
    </div>
"""

        for section in magnet_data['sections']:
            html += f"""
    <div class="section">
        <h2 class="section-heading">{section['heading']}</h2>
        <ul class="content-list">
"""
            for item in section['content']:
                html += f"            <li>{item}</li>\n"

            html += """        </ul>
    </div>
"""

        html += f"""
    <div class="cta-box">
        <div class="cta-text">{magnet_data['cta']}</div>
    </div>

    <div class="footer">
        <p>© {brand.replace('_', ' ').title()} | All Rights Reserved</p>
        <p>This guide is for informational purposes only.</p>
    </div>
</body>
</html>
"""
        return html

    def save_html(self, brand: str, lead_magnet_key: str) -> Path:
        """Save HTML file for the lead magnet."""
        html = self.generate_html_content(brand, lead_magnet_key)

        filename = f"{brand}_{lead_magnet_key}.html"
        filepath = self.output_dir / filename

        with open(filepath, "w") as f:
            f.write(html)

        logger.info(f"HTML saved to {filepath}")
        return filepath

    def generate_pdf(self, brand: str, lead_magnet_key: str) -> Path:
        """Generate PDF from HTML content.

        Note: Requires weasyprint or similar library.
        pip install weasyprint

        For systems without weasyprint, you can:
        1. Use the HTML output with a browser print-to-PDF
        2. Use an online HTML-to-PDF service
        3. Use reportlab for pure Python PDF generation
        """
        try:
            from weasyprint import HTML

            html_content = self.generate_html_content(brand, lead_magnet_key)

            filename = f"{brand}_{lead_magnet_key}.pdf"
            filepath = self.output_dir / filename

            HTML(string=html_content).write_pdf(filepath)

            logger.info(f"PDF generated at {filepath}")
            return filepath

        except ImportError:
            logger.warning("weasyprint not installed. Saving HTML instead.")
            return self.save_html(brand, lead_magnet_key)

    def generate_all_lead_magnets(self) -> list[Path]:
        """Generate all lead magnets for all brands."""
        generated = []

        for brand, magnets in LEAD_MAGNETS.items():
            for magnet_key in magnets.keys():
                try:
                    filepath = self.generate_pdf(brand, magnet_key)
                    generated.append(filepath)
                except Exception as e:
                    logger.error(f"Failed to generate {brand}/{magnet_key}: {e}")

        return generated


def main():
    """CLI entry point for PDF generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate lead magnet PDFs")
    parser.add_argument("--brand", help="Specific brand to generate for")
    parser.add_argument("--magnet", help="Specific lead magnet key")
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--html-only", action="store_true", help="Generate HTML only")

    args = parser.parse_args()

    generator = PDFGenerator(output_dir=Path(args.output))

    if args.brand and args.magnet:
        if args.html_only:
            path = generator.save_html(args.brand, args.magnet)
        else:
            path = generator.generate_pdf(args.brand, args.magnet)
        print(f"Generated: {path}")
    else:
        paths = generator.generate_all_lead_magnets()
        print(f"Generated {len(paths)} files")


if __name__ == "__main__":
    main()
