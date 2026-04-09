#!/usr/bin/env python3
"""Build professional PDF products from markdown source files using fpdf2.

Generates 4 PDFs for Gumroad:
1. AI Fitness Coach Vault (blue accent)
2. Pinterest Automation Blueprint (red accent)
3. AI Coach Client Machine (green accent)
4. Free Lead Magnet (purple accent)
"""

import os
import re
from fpdf import FPDF

# Unicode -> ASCII replacements for Helvetica font compatibility
UNICODE_REPLACEMENTS = {
    "\u2192": "->",    # →
    "\u2190": "<-",    # ←
    "\u2713": "[x]",   # ✓
    "\u2714": "[x]",   # ✔
    "\u2717": "[ ]",   # ✗
    "\u2718": "[ ]",   # ✘
    "\u2022": "-",     # •
    "\u2026": "...",   # …
    "\u2018": "'",     # '
    "\u2019": "'",     # '
    "\u201c": '"',     # "
    "\u201d": '"',     # "
    "\u2014": "--",    # —
    "\u2013": "-",     # –
    "\u00a0": " ",     # non-breaking space
    "\u2605": "*",     # ★
    "\u2606": "*",     # ☆
    "\u2502": "|",     # │ box drawing
    "\u2500": "-",     # ─ box drawing
    "\u250c": "+",     # ┌
    "\u2510": "+",     # ┐
    "\u2514": "+",     # └
    "\u2518": "+",     # ┘
    "\u251c": "+",     # ├
    "\u2524": "+",     # ┤
    "\u252c": "+",     # ┬
    "\u2534": "+",     # ┴
    "\u253c": "+",     # ┼
    "\u2550": "=",     # ═
    "\u2551": "|",     # ║
    "\u25b6": ">",     # ▶
    "\u25cf": "*",     # ●
    "\u2588": "#",     # █
    "\u00b7": ".",     # ·
}


def sanitize_text(text):
    """Replace Unicode chars that Helvetica can't render."""
    for char, replacement in UNICODE_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    # Strip any remaining non-latin1 characters
    return text.encode("latin-1", errors="replace").decode("latin-1")


class ProductPDF(FPDF):
    """Custom PDF with branded styling."""

    def __init__(self, title, subtitle, accent_color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_title = title
        self.product_subtitle = subtitle
        self.accent_r, self.accent_g, self.accent_b = accent_color
        self.chapter_title = ""
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return  # Cover page has custom layout
        # Header line
        self.set_draw_color(self.accent_r, self.accent_g, self.accent_b)
        self.set_line_width(0.5)
        self.line(15, 12, self.w - 15, 12)
        # Header text
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.set_y(5)
        self.cell(0, 8, self.product_title, align="L")
        self.ln(10)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-20)
        self.set_draw_color(self.accent_r, self.accent_g, self.accent_b)
        self.set_line_width(0.3)
        self.line(15, self.h - 22, self.w - 15, self.h - 22)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_cover_page(self):
        """Create a branded cover page."""
        self.add_page()
        # Accent bar at top
        self.set_fill_color(self.accent_r, self.accent_g, self.accent_b)
        self.rect(0, 0, self.w, 8, "F")

        # Title block
        self.set_y(60)
        self.set_font("Helvetica", "B", 32)
        self.set_text_color(33, 33, 33)
        self.multi_cell(0, 14, self.product_title, align="C")

        # Subtitle
        self.ln(8)
        self.set_font("Helvetica", "", 14)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 8, self.product_subtitle, align="C")

        # Accent line
        self.ln(15)
        self.set_draw_color(self.accent_r, self.accent_g, self.accent_b)
        self.set_line_width(1.5)
        center_x = self.w / 2
        self.line(center_x - 40, self.get_y(), center_x + 40, self.get_y())

        # Bottom accent bar
        self.set_fill_color(self.accent_r, self.accent_g, self.accent_b)
        self.rect(0, self.h - 8, self.w, 8, "F")

    def add_toc(self, chapters):
        """Add a table of contents page."""
        self.add_page()
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(33, 33, 33)
        self.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
        self.ln(8)

        self.set_draw_color(self.accent_r, self.accent_g, self.accent_b)
        self.set_line_width(0.8)
        self.line(15, self.get_y(), 80, self.get_y())
        self.ln(10)

        for i, chapter in enumerate(chapters, 1):
            self.set_font("Helvetica", "", 12)
            self.set_text_color(33, 33, 33)
            self.cell(0, 8, sanitize_text(f"{i}.  {chapter}"), new_x="LMARGIN", new_y="NEXT")
            self.ln(2)

    def add_chapter_heading(self, title):
        """Add a chapter heading with accent styling."""
        self.chapter_title = sanitize_text(title)
        # Check if we need a new page (need at least 60mm space)
        if self.get_y() > self.h - 60:
            self.add_page()

        self.ln(8)
        # Accent bar
        self.set_fill_color(self.accent_r, self.accent_g, self.accent_b)
        self.rect(15, self.get_y(), 4, 12, "F")

        self.set_x(24)
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(33, 33, 33)
        self.cell(0, 12, self.chapter_title)
        self.ln(16)

    def add_subheading(self, text):
        """Add a subheading."""
        if self.get_y() > self.h - 40:
            self.add_page()
        self.ln(4)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(50, 50, 50)
        self.cell(0, 8, sanitize_text(text), new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def add_sub_subheading(self, text):
        """Add a sub-subheading (### level)."""
        if self.get_y() > self.h - 30:
            self.add_page()
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(70, 70, 70)
        self.cell(0, 7, sanitize_text(text), new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def add_body_text(self, text):
        """Add body paragraph text."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, sanitize_text(text))
        self.ln(3)

    def add_prompt_box(self, text):
        """Add a styled prompt box with colored left border."""
        text = sanitize_text(text)
        x = self.get_x()
        y = self.get_y()

        # Calculate height needed
        self.set_font("Courier", "", 9)
        # Estimate lines needed
        lines = text.split("\n")
        total_height = 0
        for line in lines:
            line_width = self.get_string_width(line)
            n_lines = max(1, int(line_width / (self.w - 45)) + 1)
            total_height += n_lines * 5
        total_height += 10  # padding

        # Check if we need a new page
        if y + total_height > self.h - 30:
            self.add_page()
            y = self.get_y()

        # Background
        self.set_fill_color(245, 245, 250)
        self.rect(20, y, self.w - 40, total_height, "F")

        # Left accent border
        self.set_fill_color(self.accent_r, self.accent_g, self.accent_b)
        self.rect(20, y, 3, total_height, "F")

        # Text
        self.set_xy(27, y + 4)
        self.set_font("Courier", "", 9)
        self.set_text_color(40, 40, 40)

        for line in lines:
            if self.get_y() > self.h - 25:
                self.add_page()
            self.set_x(27)
            self.multi_cell(self.w - 50, 5, sanitize_text(line))

        self.set_y(y + total_height + 4)

    def add_bullet_point(self, text):
        """Add a bullet point."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.set_x(22)
        # Bullet dash
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(self.accent_r, self.accent_g, self.accent_b)
        self.cell(5, 5.5, "-")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(self.w - 32, 5.5, sanitize_text(text))
        self.ln(1)

    def add_numbered_item(self, number, text):
        """Add a numbered list item."""
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.set_x(22)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(self.accent_r, self.accent_g, self.accent_b)
        self.cell(8, 5.5, f"{number}.")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(self.w - 35, 5.5, sanitize_text(text))
        self.ln(1)

    def add_separator(self):
        """Add a horizontal separator line."""
        self.ln(4)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(30, self.get_y(), self.w - 30, self.get_y())
        self.ln(6)


def parse_markdown(md_text):
    """Parse markdown into structured elements."""
    elements = []
    lines = md_text.split("\n")
    in_code_block = False
    code_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Code block start/end
        if line.strip().startswith("```"):
            if in_code_block:
                # End code block
                elements.append(("code", "\n".join(code_lines)))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            elements.append(("separator", ""))
            i += 1
            continue

        # Headings
        if stripped.startswith("# "):
            elements.append(("h1", stripped[2:].strip()))
            i += 1
            continue
        if stripped.startswith("## "):
            elements.append(("h2", stripped[3:].strip()))
            i += 1
            continue
        if stripped.startswith("### "):
            elements.append(("h3", stripped[4:].strip()))
            i += 1
            continue

        # Bullet points
        if stripped.startswith("- ") or stripped.startswith("* "):
            text = stripped[2:].strip()
            # Clean markdown formatting
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            text = re.sub(r'\*(.+?)\*', r'\1', text)
            text = re.sub(r'`(.+?)`', r'\1', text)
            elements.append(("bullet", text))
            i += 1
            continue

        # Numbered items
        num_match = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if num_match:
            text = num_match.group(2).strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            text = re.sub(r'\*(.+?)\*', r'\1', text)
            elements.append(("numbered", (num_match.group(1), text)))
            i += 1
            continue

        # Checkmark items
        if stripped.startswith(chr(10003)) or stripped.startswith(chr(10004)):
            text = stripped[1:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
            elements.append(("bullet", text))
            i += 1
            continue

        # Bold-only lines (treat as subheading)
        bold_match = re.match(r'^\*\*(.+?)\*\*$', stripped)
        if bold_match:
            elements.append(("h3", bold_match.group(1)))
            i += 1
            continue

        # Regular paragraph text
        text = stripped
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # links
        elements.append(("text", text))
        i += 1

    # Close any unclosed code block
    if in_code_block and code_lines:
        elements.append(("code", "\n".join(code_lines)))

    return elements


def render_elements(pdf, elements, skip_first_h1=False):
    """Render parsed elements into the PDF."""
    h1_seen = False
    for elem_type, content in elements:
        if elem_type == "h1":
            if skip_first_h1 and not h1_seen:
                h1_seen = True
                continue
            pdf.add_chapter_heading(content)
        elif elem_type == "h2":
            pdf.add_subheading(content)
        elif elem_type == "h3":
            pdf.add_sub_subheading(content)
        elif elem_type == "text":
            pdf.add_body_text(content)
        elif elem_type == "code":
            pdf.add_prompt_box(content)
        elif elem_type == "bullet":
            pdf.add_bullet_point(content)
        elif elem_type == "numbered":
            num, text = content
            pdf.add_numbered_item(num, text)
        elif elem_type == "separator":
            pdf.add_separator()


def build_fitness_vault(base_dir, output_dir):
    """Build AI Fitness Coach Vault PDF."""
    product_dir = os.path.join(base_dir, "prompt-packs/products/product-1-fitness-vault")

    pdf = ProductPDF(
        "AI Fitness Coach Vault",
        "75 AI Prompts + 5 Workout Programs + Discovery Call Script\nFor Fitness Coaches Working With Men Over 35",
        (37, 99, 235),  # Blue accent #2563EB
    )
    pdf.add_cover_page()

    chapters = [
        "75 AI Prompts for Fitness Coaches",
        "Done-For-You Workout Programs",
        "Discovery Call Script",
    ]
    pdf.add_toc(chapters)

    for fname, chapter_name in [
        ("prompts.md", "75 AI Prompts for Fitness Coaches"),
        ("workout-blocks.md", "Done-For-You Workout Programs"),
        ("discovery-call-script.md", "Discovery Call Script"),
    ]:
        pdf.add_page()
        pdf.add_chapter_heading(chapter_name)
        with open(os.path.join(product_dir, fname), "r", encoding="utf-8") as f:
            elements = parse_markdown(f.read())
        render_elements(pdf, elements, skip_first_h1=True)

    output_path = os.path.join(output_dir, "ai-fitness-vault.pdf")
    pdf.output(output_path)
    return output_path


def build_pinterest_blueprint(base_dir, output_dir):
    """Build Pinterest Automation Blueprint PDF."""
    product_dir = os.path.join(base_dir, "prompt-packs/products/product-2-pinterest-blueprint")

    pdf = ProductPDF(
        "Pinterest Automation Blueprint",
        "Complete System for Automated Pinterest Marketing\nFrom Setup to 15 Pins Per Day on Autopilot",
        (220, 38, 38),  # Red accent
    )
    pdf.add_cover_page()

    files = [
        ("01-system-overview.md", "System Overview"),
        ("02-claude-prompts.md", "AI Content Prompts"),
        ("03-pinterest-hooks.md", "Pinterest Hook Templates"),
        ("04-makecom-guide.md", "Make.com Automation Guide"),
        ("05-pexels-setup.md", "Pexels Image Setup"),
        ("06-content-strategy.md", "Content Strategy"),
    ]

    pdf.add_toc([name for _, name in files])

    for fname, chapter_name in files:
        filepath = os.path.join(product_dir, fname)
        if not os.path.exists(filepath):
            continue
        pdf.add_page()
        pdf.add_chapter_heading(chapter_name)
        with open(filepath, "r", encoding="utf-8") as f:
            elements = parse_markdown(f.read())
        render_elements(pdf, elements, skip_first_h1=True)

    output_path = os.path.join(output_dir, "pinterest-blueprint.pdf")
    pdf.output(output_path)
    return output_path


def build_coach_machine(base_dir, output_dir):
    """Build AI Coach Client Machine PDF."""
    product_dir = os.path.join(base_dir, "prompt-packs/products/product-3-coach-machine")

    pdf = ProductPDF(
        "AI Coach Client Machine",
        "50 AI Prompts to Automate Your Coaching Business\nFrom Discovery Calls to Client Retention",
        (22, 163, 74),  # Green accent
    )
    pdf.add_cover_page()

    files = [
        ("prompts.md", "50 AI Prompts for Online Coaches"),
        ("scripts.md", "Done-For-You Scripts"),
    ]

    pdf.add_toc([name for _, name in files])

    for fname, chapter_name in files:
        filepath = os.path.join(product_dir, fname)
        if not os.path.exists(filepath):
            continue
        pdf.add_page()
        pdf.add_chapter_heading(chapter_name)
        with open(filepath, "r", encoding="utf-8") as f:
            elements = parse_markdown(f.read())
        render_elements(pdf, elements, skip_first_h1=True)

    output_path = os.path.join(output_dir, "ai-coach-machine.pdf")
    pdf.output(output_path)
    return output_path


def build_lead_magnet(base_dir, output_dir):
    """Build Free Lead Magnet PDF."""
    filepath = os.path.join(base_dir, "prompt-packs/lead-magnet/free-5-prompts.md")

    pdf = ProductPDF(
        "5 AI Prompts That Save\nFitness Coaches 5 Hours",
        "Free Sample from the AI Fitness Coach Vault\nCopy, Paste, and Use Immediately",
        (139, 92, 246),  # Purple accent
    )
    pdf.add_cover_page()

    pdf.add_page()
    with open(filepath, "r", encoding="utf-8") as f:
        elements = parse_markdown(f.read())
    render_elements(pdf, elements, skip_first_h1=True)

    output_path = os.path.join(output_dir, "free-lead-magnet.pdf")
    pdf.output(output_path)
    return output_path


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "products")
    os.makedirs(output_dir, exist_ok=True)

    builders = [
        ("AI Fitness Vault", build_fitness_vault),
        ("Pinterest Blueprint", build_pinterest_blueprint),
        ("AI Coach Machine", build_coach_machine),
        ("Free Lead Magnet", build_lead_magnet),
    ]

    for name, builder in builders:
        try:
            path = builder(base_dir, output_dir)
            size_kb = os.path.getsize(path) / 1024
            print(f"OK: {name} -> {os.path.basename(path)} ({size_kb:.0f} KB)")
        except Exception as e:
            print(f"FAIL: {name} -> {str(e).encode('ascii', errors='replace').decode()}")


if __name__ == "__main__":
    main()
