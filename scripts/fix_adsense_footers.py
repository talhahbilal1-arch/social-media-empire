#!/usr/bin/env python3
"""
Inject legal-link footer block into every article HTML in
outputs/dailydealdarling-website/articles/ and
outputs/menopause-planner-website/articles/.

AdSense policy reviewers expect Privacy / Terms / Contact / Medical Disclaimer
(for Menopause) or Disclosure (for DDD) to be reachable from every indexed
page. Article footers in outputs/ are currently a one-liner with copyright
only — this script inserts a legal-nav <p> above the copyright text, inside
the existing <footer>.

Idempotent: skips files where the marker class "legal-nav-adsense" is already
present in the footer.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

MARKER_CLASS = "legal-nav-adsense"

# Two brands, two link sets. Paths are relative to the article file
# (articles/ is one level below the site root).
def _ddd_links(prefix: str) -> str:
    return (
        '<p class="' + MARKER_CLASS + '" '
        'style="text-align:center;font-size:0.8em;margin:10px 0 8px;">'
        f'<a href="{prefix}about.html" style="color:#666;margin:0 6px;">About</a>|'
        f'<a href="{prefix}contact.html" style="color:#666;margin:0 6px;">Contact</a>|'
        f'<a href="{prefix}privacy.html" style="color:#666;margin:0 6px;">Privacy</a>|'
        f'<a href="{prefix}terms.html" style="color:#666;margin:0 6px;">Terms</a>|'
        f'<a href="{prefix}disclosure.html" style="color:#666;margin:0 6px;">Affiliate Disclosure</a>'
        '</p>\n  '
    )


def _mp_links(prefix: str) -> str:
    return (
        '<p class="' + MARKER_CLASS + '" '
        'style="text-align:center;font-size:0.8em;margin:10px 0 8px;">'
        f'<a href="{prefix}about.html" style="color:#6B705C;margin:0 6px;">About</a>|'
        f'<a href="{prefix}contact.html" style="color:#6B705C;margin:0 6px;">Contact</a>|'
        f'<a href="{prefix}privacy.html" style="color:#6B705C;margin:0 6px;">Privacy</a>|'
        f'<a href="{prefix}terms.html" style="color:#6B705C;margin:0 6px;">Terms</a>|'
        f'<a href="{prefix}medical-disclaimer.html" style="color:#6B705C;margin:0 6px;">Medical Disclaimer</a>'
        '</p>\n  '
    )


SITES = [
    {
        "name": "DDD articles",
        "dir": REPO_ROOT / "outputs" / "dailydealdarling-website" / "articles",
        "recursive": False,
        "links_block": _ddd_links("../"),
    },
    {
        "name": "DDD root pages",
        "dir": REPO_ROOT / "outputs" / "dailydealdarling-website",
        "recursive": False,
        "links_block": _ddd_links("/"),
    },
    {
        "name": "Menopause articles",
        "dir": REPO_ROOT / "outputs" / "menopause-planner-website" / "articles",
        "recursive": False,
        "links_block": _mp_links("../"),
    },
    {
        "name": "Menopause root pages",
        "dir": REPO_ROOT / "outputs" / "menopause-planner-website",
        "recursive": False,
        "links_block": _mp_links("/"),
    },
]

# Match the closing </footer> tag preceded by optional whitespace. We insert
# the links block immediately before it so the nav lives *inside* the footer.
FOOTER_CLOSE_RE = re.compile(r"(\s*)</footer>", re.IGNORECASE)
BODY_CLOSE_RE = re.compile(r"(\s*)</body>", re.IGNORECASE)

# Skip files that are just meta-refresh redirect stubs — AdSense follows the
# canonical, and the stub has no content to show legal links alongside.
REDIRECT_MARKER = 'http-equiv="refresh"'


def process_file(path: Path, links_block: str) -> str:
    """Return one of: skipped, updated, updated-fallback, no-anchor, redirect, error."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ERROR reading {path.name}: {e}")
        return "error"

    if MARKER_CLASS in content:
        return "skipped"

    if REDIRECT_MARKER in content.lower():
        return "redirect"

    # Preferred: inject inside the existing <footer>.
    if "</footer>" in content.lower():
        new_content, n = FOOTER_CLOSE_RE.subn(
            lambda m: "\n  " + links_block + m.group(0), content, count=1
        )
        if n:
            path.write_text(new_content, encoding="utf-8")
            return "updated"

    # Fallback: no <footer> element. Inject a standalone <div> before </body>.
    # This covers older articles that use <div class="footer"> or inline
    # copyright blocks — we add our own legal-nav as a sibling before body close.
    if "</body>" in content.lower():
        fallback_block = (
            '<div style="text-align:center;padding:12px 20px;border-top:1px solid #eee;'
            'font-size:0.8em;">' + links_block.rstrip() + "</div>\n"
        )
        new_content, n = BODY_CLOSE_RE.subn(
            lambda m: "\n  " + fallback_block + m.group(0), content, count=1
        )
        if n:
            path.write_text(new_content, encoding="utf-8")
            return "updated-fallback"

    return "no-anchor"


def main() -> int:
    overall_updated = 0
    overall_skipped = 0
    overall_missing = 0
    overall_errors = 0

    for site in SITES:
        name = site["name"]
        target_dir: Path = site["dir"]
        links_block: str = site["links_block"]

        print(f"\n=== {name} ({target_dir.relative_to(REPO_ROOT)}) ===")

        if not target_dir.exists():
            print(f"  ERROR: directory missing")
            overall_errors += 1
            continue

        html_files = sorted(target_dir.glob("*.html"))
        print(f"  Found {len(html_files)} HTML files")

        updated = fallback = skipped = redirect = missing = errors = 0
        for path in html_files:
            result = process_file(path, links_block)
            if result == "updated":
                updated += 1
            elif result == "updated-fallback":
                fallback += 1
                print(f"  NOTE: used </body> fallback for {path.name}")
            elif result == "skipped":
                skipped += 1
            elif result == "redirect":
                redirect += 1
            elif result == "no-anchor":
                missing += 1
                print(f"  WARNING: no </footer> or </body> in {path.name}")
            else:
                errors += 1

        print(f"  Updated: {updated} (+{fallback} fallback) | Skipped: {skipped} "
              f"| Redirect stubs: {redirect} | No anchor: {missing} | Errors: {errors}")
        overall_updated += updated + fallback
        overall_skipped += skipped
        overall_missing += missing
        overall_errors += errors

    print("\n" + "=" * 60)
    print("TOTALS")
    print(f"  Updated:              {overall_updated}")
    print(f"  Skipped (idempotent): {overall_skipped}")
    print(f"  Missing </footer>:    {overall_missing}")
    print(f"  Errors:               {overall_errors}")
    print("=" * 60)

    return 0 if overall_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
