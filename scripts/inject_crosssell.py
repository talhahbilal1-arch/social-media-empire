#!/usr/bin/env python3
"""Inject a Gumroad cross-sell CTA into every FitOver35 article.

For each HTML file in outputs/fitover35-website/articles/:
  - Skip if it already links to gumroad.com or fitover35.com/products
  - Find the article footer (<div class="footer">  or  <footer class="footer">)
  - Insert a branded "AI Fitness Coach Vault" CTA immediately BEFORE it
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / "outputs" / "fitover35-website" / "articles"

CTA_BLOCK = """<div style="background:linear-gradient(135deg,#1a181e 0%,#2a2530 100%);border:2px solid #d4a843;border-radius:12px;padding:24px;margin:32px 0;text-align:center">
  <p style="color:#d4a843;font-weight:700;font-size:.85rem;margin:0 0 4px;letter-spacing:1px">FOR COACHES & SERIOUS LIFTERS</p>
  <h3 style="color:#fff;margin:0 0 8px;font-size:1.1rem">AI Fitness Coach Vault - 75 Expert Prompts</h3>
  <p style="color:#8a8894;font-size:.88rem;margin:0 0 16px">Written by an ISSA-CPT for men over 35. Workout programming, nutrition, fat loss, hormone health + 5 complete training programs.</p>
  <a href="https://talhahbilal.gumroad.com/l/lupkl" target="_blank" style="display:inline-block;padding:12px 28px;background:#d4a843;color:#111;border-radius:8px;text-decoration:none;font-weight:700;font-size:.95rem">Get the Vault - $27</a>
  <p style="color:#555;font-size:.75rem;margin:12px 0 0"><a href="https://fitover35.com/products/" style="color:#8a8894;text-decoration:underline">See all products &rarr;</a></p>
</div>
"""

# Match either <div class="footer"> or <footer class="footer">
FOOTER_PATTERN = re.compile(r'(<(?:div|footer)\s+class="footer")')


def process_file(path: Path) -> str:
    """Return one of: 'skipped', 'injected', 'no_footer'."""
    html = path.read_text(encoding="utf-8")

    if "gumroad.com" in html or "fitover35.com/products" in html:
        return "skipped"

    match = FOOTER_PATTERN.search(html)
    if not match:
        return "no_footer"

    insert_at = match.start()
    new_html = html[:insert_at] + CTA_BLOCK + html[insert_at:]
    path.write_text(new_html, encoding="utf-8")
    return "injected"


def main() -> int:
    if not ARTICLES_DIR.exists():
        print(f"ERROR: {ARTICLES_DIR} does not exist", file=sys.stderr)
        return 1

    counts = {"injected": 0, "skipped": 0, "no_footer": 0}
    no_footer_files = []

    for html in sorted(ARTICLES_DIR.glob("*.html")):
        result = process_file(html)
        counts[result] += 1
        if result == "no_footer":
            no_footer_files.append(html.name)

    print(f"Injected: {counts['injected']}")
    print(f"Skipped  (already had CTA): {counts['skipped']}")
    print(f"No footer found: {counts['no_footer']}")
    if no_footer_files:
        for name in no_footer_files[:20]:
            print(f"  - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
