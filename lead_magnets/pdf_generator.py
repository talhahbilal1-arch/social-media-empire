"""Lead magnet PDF generator for all brands."""

import os
from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

# PDF generation using reportlab
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# Brand configurations for lead magnets
LEAD_MAGNET_CONFIG = {
    "daily_deal_darling": {
        "name": "Daily Deal Darling",
        "primary_color": "#E91E63",
        "secondary_color": "#FFC107",
        "lead_magnets": [
            {
                "id": "deal-tracker",
                "title": "The Ultimate Deal Tracker",
                "subtitle": "Never Miss a Sale Again",
                "description": "Track prices, set alerts, and find the best deals",
                "pages": 5,
                "content_type": "tracker"
            },
            {
                "id": "amazon-hacks",
                "title": "50 Secret Amazon Hacks",
                "subtitle": "Save Hundreds on Your Next Order",
                "description": "Insider tips for maximum savings",
                "pages": 10,
                "content_type": "guide"
            }
        ]
    },
    "menopause_planner": {
        "name": "The Menopause Planner",
        "primary_color": "#9C27B0",
        "secondary_color": "#E1BEE7",
        "lead_magnets": [
            {
                "id": "symptom-tracker",
                "title": "Menopause Symptom Tracker",
                "subtitle": "30-Day Tracking Journal",
                "description": "Track symptoms, triggers, and patterns",
                "pages": 35,
                "content_type": "tracker"
            },
            {
                "id": "hot-flash-guide",
                "title": "Hot Flash Relief Guide",
                "subtitle": "15 Natural Remedies That Actually Work",
                "description": "Evidence-based solutions for hot flashes",
                "pages": 8,
                "content_type": "guide"
            },
            {
                "id": "hormone-food-guide",
                "title": "Hormone-Balancing Foods",
                "subtitle": "Eat Your Way to Better Hormones",
                "description": "Foods that support hormonal health",
                "pages": 12,
                "content_type": "guide"
            }
        ]
    },
    "nurse_planner": {
        "name": "The Nurse Planner",
        "primary_color": "#00BCD4",
        "secondary_color": "#B2EBF2",
        "lead_magnets": [
            {
                "id": "shift-planner",
                "title": "Ultimate Shift Planner",
                "subtitle": "Organize Your Nursing Life",
                "description": "Weekly shift planning with self-care",
                "pages": 15,
                "content_type": "planner"
            },
            {
                "id": "self-care-guide",
                "title": "Nurse Self-Care Survival Guide",
                "subtitle": "Prevent Burnout & Thrive",
                "description": "Essential self-care strategies for nurses",
                "pages": 10,
                "content_type": "guide"
            },
            {
                "id": "medication-reference",
                "title": "Quick Med Reference Card",
                "subtitle": "Most Common Medications at a Glance",
                "description": "Printable medication quick reference",
                "pages": 4,
                "content_type": "reference"
            }
        ]
    },
    "adhd_planner": {
        "name": "The ADHD Planner",
        "primary_color": "#FF9800",
        "secondary_color": "#FFE0B2",
        "lead_magnets": [
            {
                "id": "brain-dump",
                "title": "ADHD Brain Dump Sheets",
                "subtitle": "Get Everything Out of Your Head",
                "description": "Structured brain dump templates",
                "pages": 10,
                "content_type": "worksheet"
            },
            {
                "id": "habit-tracker",
                "title": "ADHD-Friendly Habit Tracker",
                "subtitle": "Build Habits That Stick",
                "description": "Visual tracking designed for ADHD brains",
                "pages": 8,
                "content_type": "tracker"
            },
            {
                "id": "focus-guide",
                "title": "Focus Hacks for ADHD",
                "subtitle": "20 Strategies That Actually Work",
                "description": "Practical focus techniques",
                "pages": 12,
                "content_type": "guide"
            }
        ]
    }
}


@dataclass
class LeadMagnetGenerator:
    """Generates lead magnet PDFs for all brands."""

    output_dir: Path = None

    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = Path(__file__).parent / "generated"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self) -> list[str]:
        """Generate all lead magnets for all brands."""
        generated_files = []

        for brand, config in LEAD_MAGNET_CONFIG.items():
            for magnet in config["lead_magnets"]:
                filepath = self.generate_lead_magnet(brand, magnet["id"])
                if filepath:
                    generated_files.append(filepath)

        return generated_files

    def generate_lead_magnet(self, brand: str, magnet_id: str) -> Optional[str]:
        """Generate a specific lead magnet PDF."""
        if not REPORTLAB_AVAILABLE:
            return self._generate_placeholder(brand, magnet_id)

        brand_config = LEAD_MAGNET_CONFIG.get(brand)
        if not brand_config:
            return None

        magnet_config = None
        for m in brand_config["lead_magnets"]:
            if m["id"] == magnet_id:
                magnet_config = m
                break

        if not magnet_config:
            return None

        filename = f"{brand}_{magnet_id}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Build content based on type
        content_type = magnet_config.get("content_type", "guide")

        if content_type == "tracker":
            story = self._build_tracker_content(brand_config, magnet_config)
        elif content_type == "planner":
            story = self._build_planner_content(brand_config, magnet_config)
        elif content_type == "worksheet":
            story = self._build_worksheet_content(brand_config, magnet_config)
        else:
            story = self._build_guide_content(brand_config, magnet_config)

        doc.build(story)
        return str(filepath)

    def _generate_placeholder(self, brand: str, magnet_id: str) -> str:
        """Generate a placeholder text file when reportlab is not available."""
        brand_config = LEAD_MAGNET_CONFIG.get(brand, {})
        magnet_config = None
        for m in brand_config.get("lead_magnets", []):
            if m["id"] == magnet_id:
                magnet_config = m
                break

        if not magnet_config:
            return None

        filename = f"{brand}_{magnet_id}_content.txt"
        filepath = self.output_dir / filename

        content = f"""
{'=' * 60}
{magnet_config['title'].upper()}
{magnet_config['subtitle']}
{'=' * 60}

Brand: {brand_config.get('name', brand)}
Pages: {magnet_config['pages']}
Type: {magnet_config['content_type']}

{magnet_config['description']}

{'=' * 60}
CONTENT OUTLINE
{'=' * 60}

[This is a placeholder. Install reportlab to generate actual PDFs]

pip install reportlab

{'=' * 60}
"""

        with open(filepath, "w") as f:
            f.write(content)

        return str(filepath)

    def _get_styles(self, brand_config: dict) -> dict:
        """Get paragraph styles for the brand."""
        styles = getSampleStyleSheet()

        # Custom styles
        primary_color = colors.HexColor(brand_config["primary_color"])

        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=primary_color,
            alignment=TA_CENTER,
            spaceAfter=12
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.gray,
            alignment=TA_CENTER,
            spaceAfter=30
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=primary_color,
            spaceBefore=20,
            spaceAfter=10
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=12,
            leading=18,
            spaceAfter=12
        )

        return {
            'title': title_style,
            'subtitle': subtitle_style,
            'heading': heading_style,
            'body': body_style,
            'normal': styles['Normal']
        }

    def _build_guide_content(self, brand_config: dict, magnet_config: dict) -> list:
        """Build content for a guide-type lead magnet."""
        styles = self._get_styles(brand_config)
        story = []

        # Cover page
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph(magnet_config["title"], styles['title']))
        story.append(Paragraph(magnet_config["subtitle"], styles['subtitle']))
        story.append(Spacer(1, inch))
        story.append(Paragraph(f"By {brand_config['name']}", styles['body']))
        story.append(PageBreak())

        # Introduction
        story.append(Paragraph("Welcome!", styles['heading']))
        story.append(Paragraph(
            f"Thank you for downloading {magnet_config['title']}. "
            f"This guide will help you {magnet_config['description'].lower()}.",
            styles['body']
        ))
        story.append(Spacer(1, 0.5 * inch))

        # Sample content sections
        sections = self._get_guide_sections(magnet_config)
        for section in sections:
            story.append(Paragraph(section["title"], styles['heading']))
            story.append(Paragraph(section["content"], styles['body']))
            if section.get("tips"):
                for tip in section["tips"]:
                    story.append(Paragraph(f"• {tip}", styles['body']))
            story.append(Spacer(1, 0.3 * inch))

        # Call to action
        story.append(PageBreak())
        story.append(Paragraph("Want More?", styles['heading']))
        story.append(Paragraph(
            f"Follow {brand_config['name']} on social media for daily tips and exclusive content!",
            styles['body']
        ))

        return story

    def _build_tracker_content(self, brand_config: dict, magnet_config: dict) -> list:
        """Build content for a tracker-type lead magnet."""
        styles = self._get_styles(brand_config)
        story = []

        # Cover page
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph(magnet_config["title"], styles['title']))
        story.append(Paragraph(magnet_config["subtitle"], styles['subtitle']))
        story.append(PageBreak())

        # Instructions
        story.append(Paragraph("How to Use This Tracker", styles['heading']))
        story.append(Paragraph(
            "Use this tracker daily to monitor your progress and identify patterns. "
            "Be consistent for best results!",
            styles['body']
        ))
        story.append(Spacer(1, 0.5 * inch))

        # Generate tracking pages
        for day in range(1, 8):  # Sample week
            story.append(Paragraph(f"Day {day}", styles['heading']))

            # Create tracking table
            data = [
                ["Time", "Notes", "Rating (1-10)"],
                ["Morning", "", ""],
                ["Afternoon", "", ""],
                ["Evening", "", ""],
            ]

            table = Table(data, colWidths=[1.5*inch, 3.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(brand_config["primary_color"])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.gray),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3 * inch))

            # Notes section
            story.append(Paragraph("Daily Reflection:", styles['body']))
            story.append(Paragraph("_" * 60, styles['normal']))
            story.append(Paragraph("_" * 60, styles['normal']))
            story.append(Spacer(1, 0.5 * inch))

        return story

    def _build_planner_content(self, brand_config: dict, magnet_config: dict) -> list:
        """Build content for a planner-type lead magnet."""
        styles = self._get_styles(brand_config)
        story = []

        # Cover
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph(magnet_config["title"], styles['title']))
        story.append(Paragraph(magnet_config["subtitle"], styles['subtitle']))
        story.append(PageBreak())

        # Weekly planning pages
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for day in days:
            story.append(Paragraph(day, styles['heading']))

            # Schedule table
            data = [["Time", "Task/Activity", "Priority"]]
            for hour in range(6, 22, 2):
                data.append([f"{hour}:00", "", ""])

            table = Table(data, colWidths=[1*inch, 4*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(brand_config["primary_color"])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ]))
            story.append(table)

            # Self-care reminder
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("Self-Care Today: ________________________", styles['body']))
            story.append(PageBreak())

        return story

    def _build_worksheet_content(self, brand_config: dict, magnet_config: dict) -> list:
        """Build content for a worksheet-type lead magnet."""
        styles = self._get_styles(brand_config)
        story = []

        # Cover
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph(magnet_config["title"], styles['title']))
        story.append(Paragraph(magnet_config["subtitle"], styles['subtitle']))
        story.append(PageBreak())

        # Brain dump worksheets
        for i in range(1, 6):
            story.append(Paragraph(f"Brain Dump #{i}", styles['heading']))
            story.append(Paragraph("Date: _______________", styles['body']))
            story.append(Spacer(1, 0.3 * inch))

            # Sections
            sections = [
                "Tasks Swimming in My Head:",
                "Ideas I Don't Want to Forget:",
                "Things Stressing Me Out:",
                "What I Actually Need to Do Today:"
            ]

            for section in sections:
                story.append(Paragraph(section, styles['body']))
                for _ in range(4):
                    story.append(Paragraph("• _________________________________", styles['normal']))
                story.append(Spacer(1, 0.2 * inch))

            story.append(PageBreak())

        return story

    def _get_guide_sections(self, magnet_config: dict) -> list:
        """Get content sections based on the guide type."""
        # Default sections that can be customized per guide
        guide_id = magnet_config.get("id", "")

        if "amazon" in guide_id or "deal" in guide_id:
            return [
                {
                    "title": "1. Use Price Tracking Tools",
                    "content": "Never pay full price again by using these free tools:",
                    "tips": ["CamelCamelCamel", "Keepa", "Honey browser extension"]
                },
                {
                    "title": "2. Shop at the Right Time",
                    "content": "Timing is everything when it comes to deals:",
                    "tips": ["Prime Day (July)", "Black Friday", "Cyber Monday", "End of season"]
                },
                {
                    "title": "3. Stack Discounts",
                    "content": "Combine multiple savings methods:",
                    "tips": ["Coupons + Subscribe & Save", "Warehouse deals", "Amazon credit card rewards"]
                }
            ]
        elif "hot-flash" in guide_id or "menopause" in guide_id:
            return [
                {
                    "title": "1. Cooling Strategies",
                    "content": "Immediate relief techniques:",
                    "tips": ["Keep a small fan handy", "Wear layered clothing", "Use cooling towels"]
                },
                {
                    "title": "2. Dietary Changes",
                    "content": "Foods that can help reduce symptoms:",
                    "tips": ["Avoid spicy foods", "Limit caffeine and alcohol", "Eat phytoestrogen-rich foods"]
                },
                {
                    "title": "3. Lifestyle Modifications",
                    "content": "Long-term strategies for management:",
                    "tips": ["Regular exercise", "Stress management", "Adequate sleep"]
                }
            ]
        elif "focus" in guide_id or "adhd" in guide_id:
            return [
                {
                    "title": "1. Environment Setup",
                    "content": "Create a focus-friendly space:",
                    "tips": ["Minimize visual clutter", "Use noise-canceling headphones", "Good lighting"]
                },
                {
                    "title": "2. Time Management",
                    "content": "Work with your ADHD brain:",
                    "tips": ["Pomodoro technique (25 min focus)", "Time blocking", "Visual timers"]
                },
                {
                    "title": "3. Body Doubling",
                    "content": "Use accountability to stay on task:",
                    "tips": ["Virtual coworking", "Study groups", "Focusmate sessions"]
                }
            ]
        else:
            return [
                {
                    "title": "Getting Started",
                    "content": "Here's how to make the most of this guide:",
                    "tips": ["Read through once completely", "Highlight key points", "Take action on one tip today"]
                },
                {
                    "title": "Key Strategies",
                    "content": "The most important things to remember:",
                    "tips": ["Consistency is key", "Start small", "Track your progress"]
                },
                {
                    "title": "Next Steps",
                    "content": "Keep the momentum going:",
                    "tips": ["Join our community", "Follow for daily tips", "Share with a friend"]
                }
            ]


def generate_all_lead_magnets():
    """Generate all lead magnets for all brands."""
    generator = LeadMagnetGenerator()
    files = generator.generate_all()
    print(f"Generated {len(files)} lead magnets:")
    for f in files:
        print(f"  - {f}")
    return files


if __name__ == "__main__":
    generate_all_lead_magnets()
