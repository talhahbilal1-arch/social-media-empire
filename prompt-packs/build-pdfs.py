#!/usr/bin/env python3
"""
Convert all product markdown files to styled HTML ready for PDF printing in Chrome.
Run: python3 build-pdfs.py
Then open each HTML file in Chrome → Print → Save as PDF.
"""

import markdown
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

PRODUCTS = [
    {
        "name": "AI Fitness Coach Vault — Men Over 35",
        "subtitle": "75 Prompts · 5 Programs · Discovery Call Script",
        "accent": "#2563eb",
        "output": "product-1-fitness-vault.html",
        "files": [
            ("products/product-1-fitness-vault/README.md", None),
            ("products/product-1-fitness-vault/prompts.md", None),
            ("products/product-1-fitness-vault/workout-blocks.md", None),
            ("products/product-1-fitness-vault/discovery-call-script.md", None),
        ]
    },
    {
        "name": "Pinterest Automation Blueprint",
        "subtitle": "The Exact System · Real Prompts · Full Setup Guide",
        "accent": "#dc2626",
        "output": "product-2-pinterest-blueprint.html",
        "files": [
            ("products/product-2-pinterest-blueprint/README.md", None),
            ("products/product-2-pinterest-blueprint/01-system-overview.md", None),
            ("products/product-2-pinterest-blueprint/02-claude-prompts.md", None),
            ("products/product-2-pinterest-blueprint/03-pinterest-hooks.md", None),
            ("products/product-2-pinterest-blueprint/04-makecom-guide.md", None),
            ("products/product-2-pinterest-blueprint/05-pexels-setup.md", None),
            ("products/product-2-pinterest-blueprint/06-content-strategy.md", None),
        ]
    },
    {
        "name": "Online Coach AI Client Machine",
        "subtitle": "50 Prompts · Word-for-Word Scripts · Every Business Stage",
        "accent": "#16a34a",
        "output": "product-3-coach-machine.html",
        "files": [
            ("products/product-3-coach-machine/README.md", None),
            ("products/product-3-coach-machine/prompts.md", None),
            ("products/product-3-coach-machine/scripts.md", None),
        ]
    },
    {
        "name": "FREE: 5 AI Prompts That Save Fitness Coaches 5 Hours a Week",
        "subtitle": "Lead Magnet — Free Download",
        "accent": "#9333ea",
        "output": "lead-magnet-free-prompts.html",
        "files": [
            ("lead-magnet/free-5-prompts.md", None),
        ]
    },
]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {{
  --accent: {accent};
  --accent-light: {accent}18;
  --text: #111827;
  --muted: #6b7280;
  --border: #e5e7eb;
  --bg-code: #f3f4f6;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text);
  max-width: 820px;
  margin: 0 auto;
  padding: 40px 40px 60px;
}}

/* Cover page */
.cover {{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 60px 0;
  border-bottom: 3px solid var(--accent);
  margin-bottom: 60px;
  page-break-after: always;
}}
.cover-badge {{
  display: inline-block;
  background: var(--accent-light);
  color: var(--accent);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 6px 14px;
  border-radius: 100px;
  margin-bottom: 28px;
}}
.cover h1 {{
  font-size: 36px;
  font-weight: 800;
  line-height: 1.2;
  color: var(--text);
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}}
.cover-sub {{
  font-size: 16px;
  color: var(--muted);
  margin-bottom: 40px;
  font-weight: 400;
}}
.cover-divider {{
  width: 60px;
  height: 4px;
  background: var(--accent);
  border-radius: 2px;
  margin-bottom: 40px;
}}
.cover-meta {{
  font-size: 12px;
  color: var(--muted);
}}
.cover-meta strong {{ color: var(--text); }}

/* Section breaks */
.section-break {{
  page-break-before: always;
  padding-top: 20px;
}}

/* Headings */
h1 {{
  font-size: 26px;
  font-weight: 800;
  color: var(--text);
  margin: 48px 0 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--accent);
  letter-spacing: -0.02em;
  page-break-after: avoid;
}}
h2 {{
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  margin: 36px 0 14px;
  padding-left: 12px;
  border-left: 3px solid var(--accent);
  page-break-after: avoid;
}}
h3 {{
  font-size: 14px;
  font-weight: 700;
  color: var(--accent);
  margin: 24px 0 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  page-break-after: avoid;
}}

/* Paragraphs */
p {{ margin: 10px 0; color: var(--text); }}

/* Lists */
ul, ol {{
  margin: 10px 0 16px 20px;
  padding-left: 4px;
}}
li {{
  margin: 5px 0;
  padding-left: 4px;
}}
li > ul, li > ol {{ margin: 4px 0 4px 16px; }}

/* Code blocks */
pre {{
  background: var(--bg-code);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 6px;
  padding: 18px 20px;
  margin: 16px 0;
  overflow-x: auto;
  page-break-inside: avoid;
  font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace;
  font-size: 11.5px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}}
code {{
  font-family: 'SF Mono', 'Fira Code', Consolas, monospace;
  font-size: 11.5px;
  background: var(--bg-code);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--border);
}}
pre code {{
  background: none;
  padding: 0;
  border: none;
  font-size: inherit;
}}

/* Tables */
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  font-size: 12px;
  page-break-inside: avoid;
}}
th {{
  background: var(--accent);
  color: white;
  text-align: left;
  padding: 10px 14px;
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}
td {{
  padding: 9px 14px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}}
tr:nth-child(even) td {{ background: var(--accent-light); }}

/* Blockquotes (used for prompt boxes) */
blockquote {{
  border-left: 3px solid var(--accent);
  background: var(--accent-light);
  padding: 14px 18px;
  margin: 14px 0;
  border-radius: 0 6px 6px 0;
  page-break-inside: avoid;
}}
blockquote p {{ margin: 4px 0; color: var(--text); font-style: normal; }}

/* Horizontal rule */
hr {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 32px 0;
}}

/* Strong / em */
strong {{ font-weight: 700; color: var(--text); }}
em {{ font-style: italic; color: var(--muted); }}

/* Page numbers via CSS */
@page {{
  size: letter;
  margin: 20mm 18mm 20mm;
  @bottom-right {{
    content: counter(page);
    font-size: 10px;
    color: #9ca3af;
  }}
}}

@media print {{
  body {{ padding: 0; max-width: 100%; }}
  .cover {{ page-break-after: always; }}
  a {{ color: inherit; text-decoration: none; }}
  pre {{ background: #f9fafb; }}
}}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{css}</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
  <span class="cover-badge">Digital Product</span>
  <h1>{title}</h1>
  <p class="cover-sub">{subtitle}</p>
  <div class="cover-divider"></div>
  <p class="cover-meta">
    <strong>fitover35.com</strong><br>
    ISSA Certified Personal Trainer · 6 Years Experience<br>
    <br>
    This document is for personal and business use only.<br>
    Please do not redistribute without permission.
  </p>
</div>

<!-- CONTENT -->
{content}

</body>
</html>
"""

def convert_file(filepath):
    """Read a markdown file and convert to HTML."""
    full_path = os.path.join(BASE, filepath)
    if not os.path.exists(full_path):
        print(f"  WARNING: {filepath} not found, skipping")
        return ""
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'codehilite'])
    html = md.convert(content)
    return html

def build_product(product):
    """Build the complete HTML for one product."""
    print(f"\nBuilding: {product['name']}")

    sections = []
    for i, (filepath, _) in enumerate(product['files']):
        html = convert_file(filepath)
        if html:
            # Add section break for all files after the first
            if i > 0:
                wrapper = f'<div class="section-break">{html}</div>'
            else:
                wrapper = html
            sections.append(wrapper)
            print(f"  ✓ {filepath}")

    content = "\n\n".join(sections)
    css = CSS.format(accent=product['accent'])

    final_html = HTML_TEMPLATE.format(
        title=product['name'],
        subtitle=product['subtitle'],
        css=css,
        content=content
    )

    output_path = os.path.join(BASE, "output", product['output'])
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"  → Saved: output/{product['output']}")
    return output_path

if __name__ == "__main__":
    # Create output directory
    output_dir = os.path.join(BASE, "output")
    os.makedirs(output_dir, exist_ok=True)

    built_files = []
    for product in PRODUCTS:
        path = build_product(product)
        built_files.append(path)

    print(f"\n{'='*50}")
    print(f"✅ Built {len(built_files)} HTML files in prompt-packs/output/")
    print(f"\nTo create PDFs:")
    print("  Open each HTML file in Chrome → Ctrl+P → Save as PDF")
    print("  Settings: Paper=Letter, Margins=Default, Background graphics=ON")
    print(f"\nFiles built:")
    for f in built_files:
        print(f"  {os.path.basename(f)}")
