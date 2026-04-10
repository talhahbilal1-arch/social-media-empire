#!/usr/bin/env python3
"""Build production-ready Gumroad PDFs from prompt-pack markdown files.

For each product folder in prompt-packs/products/:
  1. Parse all .md files in the folder
  2. Render a professional PDF (cover, TOC, content, page numbers)
  3. Save the PDF inside the product folder as {product-name}.pdf
  4. Rebuild the product's .zip so it contains BOTH the .md files AND the .pdf
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from typing import List, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_DIR = ROOT / "prompt-packs" / "products"


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

_EMOJI_RE = re.compile(
    "["                     # strip emoji / pictograph code points
    "\U0001F300-\U0001FAFF"
    "\U0001F600-\U0001F64F"
    "\U00002600-\U000027BF"
    "\U0001F900-\U0001F9FF"
    "]+",
    flags=re.UNICODE,
)


def _strip_emoji(text: str) -> str:
    return _EMOJI_RE.sub("", text).strip()


def _escape(text: str) -> str:
    """Escape text for reportlab mini-markup + convert simple inline markdown."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(
        r"`([^`]+)`",
        r'<font face="Courier" backColor="#f0f0f0">\1</font>',
        text,
    )
    return text


def _pretty_name(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------


def _build_styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "PackTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=32,
            alignment=1,
            textColor=colors.HexColor("#1a181e"),
            spaceAfter=18,
        ),
        "subtitle": ParagraphStyle(
            "PackSubtitle",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=14,
            leading=18,
            alignment=1,
            textColor=colors.HexColor("#8a8894"),
            spaceAfter=10,
        ),
        "cover_tag": ParagraphStyle(
            "PackCoverTag",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            alignment=1,
            textColor=colors.HexColor("#8a8894"),
        ),
        "h1": ParagraphStyle(
            "PackH1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1a181e"),
            spaceBefore=18,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "PackH2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#2a2530"),
            spaceBefore=14,
            spaceAfter=8,
        ),
        "h3": ParagraphStyle(
            "PackH3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#3a3540"),
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "PackBody",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#222"),
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "PackBullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            leftIndent=18,
            textColor=colors.HexColor("#222"),
            spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "PackQuote",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=11,
            leading=15,
            leftIndent=16,
            textColor=colors.HexColor("#555"),
            spaceBefore=6,
            spaceAfter=6,
        ),
        "code": ParagraphStyle(
            "PackCode",
            parent=base["Code"],
            fontName="Courier",
            fontSize=9,
            leading=12,
            leftIndent=12,
            rightIndent=12,
            textColor=colors.HexColor("#1a181e"),
            backColor=colors.HexColor("#f4f4f4"),
            borderColor=colors.HexColor("#e0e0e0"),
            borderWidth=0.5,
            borderPadding=8,
            spaceBefore=6,
            spaceAfter=8,
        ),
        "toc_file": ParagraphStyle(
            "TOCFile",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=18,
            textColor=colors.HexColor("#1a181e"),
            spaceBefore=8,
        ),
        "toc_h1": ParagraphStyle(
            "TOCH1",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            leftIndent=12,
            textColor=colors.HexColor("#2a2530"),
        ),
        "toc_h2": ParagraphStyle(
            "TOCH2",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            leftIndent=26,
            textColor=colors.HexColor("#555"),
        ),
    }


# ---------------------------------------------------------------------------
# Markdown -> flowables
# ---------------------------------------------------------------------------


def parse_markdown(md: str, styles: dict) -> Tuple[list, List[Tuple[int, str]]]:
    lines = md.splitlines()
    flow = []
    toc: List[Tuple[int, str]] = []  # (level, title)

    in_code = False
    code_buf: List[str] = []
    bullet_buf: List[str] = []

    def flush_bullets():
        if not bullet_buf:
            return
        for item in bullet_buf:
            flow.append(Paragraph("&bull;&nbsp;" + _escape(item), styles["bullet"]))
        bullet_buf.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        # Code fence
        if stripped.startswith("```"):
            flush_bullets()
            if in_code:
                code_text = "\n".join(code_buf)
                if code_text.strip():
                    # Preformatted keeps line breaks, Paragraph would re-flow
                    flow.append(Preformatted(code_text, styles["code"]))
                code_buf.clear()
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^\s*(---+|\*\*\*+|___+)\s*$", stripped):
            flush_bullets()
            flow.append(Spacer(1, 10))
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            flush_bullets()
            level = len(m.group(1))
            title = _strip_emoji(m.group(2).strip())
            if not title:
                i += 1
                continue
            if level == 1:
                flow.append(Paragraph(_escape(title), styles["h1"]))
                toc.append((1, title))
            elif level == 2:
                flow.append(Paragraph(_escape(title), styles["h2"]))
                toc.append((2, title))
            else:
                flow.append(Paragraph(_escape(title), styles["h3"]))
            i += 1
            continue

        # Blockquote
        if stripped.startswith("> "):
            flush_bullets()
            flow.append(Paragraph(_escape(stripped[2:]), styles["quote"]))
            i += 1
            continue

        # Bullet item (- or *)
        bm = re.match(r"^\s*[-*]\s+(.*)$", line)
        if bm:
            bullet_buf.append(bm.group(1))
            i += 1
            continue

        # Numbered item
        nm = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if nm:
            flush_bullets()
            flow.append(
                Paragraph(
                    f"{nm.group(1)}. {_escape(nm.group(2))}",
                    styles["bullet"],
                )
            )
            i += 1
            continue

        # Blank line
        if not stripped:
            flush_bullets()
            flow.append(Spacer(1, 4))
            i += 1
            continue

        # Plain paragraph
        flush_bullets()
        flow.append(Paragraph(_escape(stripped), styles["body"]))
        i += 1

    flush_bullets()
    if in_code and code_buf:
        flow.append(Preformatted("\n".join(code_buf), styles["code"]))

    return flow, toc


# ---------------------------------------------------------------------------
# Page template
# ---------------------------------------------------------------------------


def _make_footer(product_title: str):
    def _footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawRightString(
            LETTER[0] - inch,
            0.5 * inch,
            f"Page {canvas.getPageNumber()}",
        )
        canvas.drawString(inch, 0.5 * inch, f"{product_title} - FitOver35")
        canvas.restoreState()

    return _footer


# ---------------------------------------------------------------------------
# PDF builder
# ---------------------------------------------------------------------------


def build_pdf(product_slug: str, md_files: List[Path], output_path: Path) -> None:
    styles = _build_styles()
    pretty = _pretty_name(product_slug)

    doc = BaseDocTemplate(
        str(output_path),
        pagesize=LETTER,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
        title=pretty,
        author="FitOver35",
    )
    frame = Frame(
        doc.leftMargin,
        doc.bottomMargin,
        doc.width,
        doc.height,
        id="normal",
    )
    doc.addPageTemplates(
        [PageTemplate(id="main", frames=frame, onPage=_make_footer(pretty))]
    )

    story = []

    # Cover page
    story.append(Spacer(1, 2.5 * inch))
    story.append(Paragraph(pretty, styles["title"]))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("by FitOver35", styles["subtitle"]))
    story.append(Spacer(1, 0.3 * inch))

    rule = Table([[""]], colWidths=[4 * inch], rowHeights=[2])
    rule.setStyle(
        TableStyle(
            [("LINEABOVE", (0, 0), (-1, -1), 1.2, colors.HexColor("#d4a843"))]
        )
    )
    story.append(rule)
    story.append(Spacer(1, 0.25 * inch))
    story.append(
        Paragraph(
            "Premium Prompt Pack - Production-Ready Templates", styles["cover_tag"]
        )
    )
    story.append(PageBreak())

    # Parse all markdown first to build the TOC
    parsed: List[Tuple[Path, list, List[Tuple[int, str]]]] = []
    for md_file in md_files:
        md_text = md_file.read_text(encoding="utf-8")
        flow, toc = parse_markdown(md_text, styles)
        parsed.append((md_file, flow, toc))

    # Table of contents
    story.append(Paragraph("Table of Contents", styles["h1"]))
    story.append(Spacer(1, 0.1 * inch))
    for md_file, _flow, toc in parsed:
        file_label = _pretty_name(md_file.stem)
        story.append(Paragraph(file_label, styles["toc_file"]))
        for level, title in toc:
            style = styles["toc_h1"] if level == 1 else styles["toc_h2"]
            story.append(Paragraph(_escape(title), style))
    story.append(PageBreak())

    # Content sections
    for idx, (md_file, flow, _toc) in enumerate(parsed):
        file_label = _pretty_name(md_file.stem)
        story.append(Paragraph(file_label, styles["h1"]))
        story.extend(flow)
        if idx < len(parsed) - 1:
            story.append(PageBreak())

    doc.build(story)


# ---------------------------------------------------------------------------
# Zip rebuild
# ---------------------------------------------------------------------------


def rebuild_zip(product_dir: Path, zip_path: Path) -> None:
    folder_name = product_dir.name
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(product_dir.iterdir()):
            if file.is_file():
                arcname = f"{folder_name}/{file.name}"
                zf.write(file, arcname)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    if not PRODUCTS_DIR.exists():
        print(f"ERROR: {PRODUCTS_DIR} does not exist", file=sys.stderr)
        return 1

    built = 0
    failed = 0
    for entry in sorted(PRODUCTS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        md_files = sorted(entry.glob("*.md"))
        if not md_files:
            print(f"skip {entry.name}: no markdown files")
            continue

        pdf_path = entry / f"{entry.name}.pdf"
        print(f"Building {pdf_path.relative_to(ROOT)}...")
        try:
            build_pdf(entry.name, md_files, pdf_path)
        except Exception as exc:  # pragma: no cover
            print(f"  FAILED: {exc}", file=sys.stderr)
            failed += 1
            continue

        zip_path = PRODUCTS_DIR / f"{entry.name}.zip"
        print(f"  Repacking {zip_path.relative_to(ROOT)}...")
        rebuild_zip(entry, zip_path)
        built += 1

    print(f"\nBuilt {built} PDFs ({failed} failures).")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
