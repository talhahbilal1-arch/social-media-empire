"""Convert Amazon search URLs (amazon.com/s?k=...) into direct /dp/<ASIN> links.

Uses the merged ASIN_DICT from asin_dictionary.py. Dry-run by default: prints
(old -> new) and counts, never writes unless --write is passed explicitly.

Usage:
    python3 scripts/convert_all_search_urls_v2.py                 # dry run, all brands
    python3 scripts/convert_all_search_urls_v2.py --brand fitness --limit 50
    python3 scripts/convert_all_search_urls_v2.py --write         # apply in place
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote_plus

# Allow running from repo root or scripts/ dir
sys.path.insert(0, str(Path(__file__).resolve().parent))
from asin_dictionary import ASIN_DICT, TAGS  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent

# Brand -> list of glob patterns (relative to repo root)
BRAND_GLOBS: dict[str, list[str]] = {
    "fitness": ["outputs/fitover35-website/articles/*.html"],
    "deals": ["outputs/dailydealdarling-website/articles/*.html"],
    "menopause": ["outputs/menopause-planner-website/articles/*.html"],
}
# Shared / non-brand markdown location — treated as fitness by default
EXTRA_MD_GLOBS = ["anti_gravity/site/content/articles/*.md"]

# Regex for amazon search URLs (inside href or bare)
SEARCH_URL_RE = re.compile(
    r'https?://(?:www\.)?amazon\.com/s\?[^"\s<>\']*?k=([^&"\s<>\']+)[^"\s<>\']*',
    re.IGNORECASE,
)

STOP_WORDS = {
    "the", "a", "an", "best", "for", "top", "and", "or", "with", "of", "to",
    "in", "on", "at", "by", "new", "cheap", "affordable", "2024", "2025",
    "2026", "review", "reviews", "amazon", "buy", "men", "women", "your",
}

UNCONVERTABLE_LOG = Path(__file__).resolve().parent / "unconvertable_urls.txt"


def normalize_query(raw: str) -> str:
    """URL-decode and strip stop-words from a search query."""
    decoded = unquote_plus(raw).lower()
    # Replace punctuation with spaces
    decoded = re.sub(r"[^a-z0-9 ]+", " ", decoded)
    tokens = [t for t in decoded.split() if t and t not in STOP_WORDS]
    return " ".join(tokens).strip()


def match_asin(query: str) -> str | None:
    """Return ASIN if query matches ASIN_DICT exactly or fuzzy-closely."""
    if not query:
        return None
    if query in ASIN_DICT:
        return ASIN_DICT[query]
    matches = difflib.get_close_matches(query, ASIN_DICT.keys(), n=1, cutoff=0.65)
    if matches:
        return ASIN_DICT[matches[0]]
    return None


def build_direct_url(asin: str, brand: str) -> str:
    tag = TAGS.get(brand, TAGS["fitness"])
    return f"https://www.amazon.com/dp/{asin}?tag={tag}"


def collect_files(brand_filter: str) -> list[tuple[str, Path]]:
    """Return list of (brand, path) tuples."""
    out: list[tuple[str, Path]] = []
    brands = list(BRAND_GLOBS) if brand_filter == "all" else [brand_filter]
    for b in brands:
        for pattern in BRAND_GLOBS.get(b, []):
            out.extend((b, p) for p in REPO_ROOT.glob(pattern))
    if brand_filter in ("all", "fitness"):
        for pattern in EXTRA_MD_GLOBS:
            out.extend(("fitness", p) for p in REPO_ROOT.glob(pattern))
    return out


def process_file(
    brand: str,
    path: Path,
    write: bool,
    unconvertable: list[tuple[str, str]],
) -> tuple[int, int]:
    """Return (converted_count, unconverted_count) for this file."""
    try:
        original = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        print(f"[warn] could not read {path}: {e}", file=sys.stderr)
        return (0, 0)

    converted = 0
    unconverted = 0
    new_content = original

    for m in SEARCH_URL_RE.finditer(original):
        full_url = m.group(0)
        raw_q = m.group(1)
        norm = normalize_query(raw_q)
        asin = match_asin(norm)
        if asin:
            new_url = build_direct_url(asin, brand)
            print(f"  [{brand}] {path.name}")
            print(f"      OLD: {full_url[:110]}")
            print(f"      NEW: {new_url}")
            new_content = new_content.replace(full_url, new_url)
            converted += 1
        else:
            unconvertable.append((brand, norm or raw_q))
            unconverted += 1

    if write and converted and new_content != original:
        try:
            path.write_text(new_content, encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            print(f"[warn] could not write {path}: {e}", file=sys.stderr)

    return (converted, unconverted)


def write_report(
    per_brand: dict[str, dict[str, int]],
    unconvertable: list[tuple[str, str]],
) -> Path:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = (
        Path(__file__).resolve().parent / f"conversion_report_{date_str}.md"
    )
    lines: list[str] = [
        f"# Conversion Report — {date_str} UTC",
        "",
        "## Counts per brand",
        "",
        "| Brand | Converted | Unconverted |",
        "|-------|-----------|-------------|",
    ]
    for b, d in sorted(per_brand.items()):
        lines.append(f"| {b} | {d.get('converted', 0)} | {d.get('unconverted', 0)} |")

    # Top-20 longest unconvertable queries (unique)
    longest = sorted(set(q for _, q in unconvertable), key=len, reverse=True)[:20]
    lines += ["", "## Top 20 longest unconvertable queries", ""]
    lines += [f"- `{q}`" for q in longest] or ["- (none)"]

    # Most frequent
    counter = Counter(q for _, q in unconvertable).most_common(20)
    lines += ["", "## Top 20 most-frequent unconvertable queries", ""]
    lines += [f"- ({n}x) `{q}`" for q, n in counter] or ["- (none)"]

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--brand",
        choices=["all", "fitness", "deals", "menopause"],
        default="all",
    )
    ap.add_argument(
        "--limit", type=int, default=0, help="Max files to process (0 = no limit)"
    )
    ap.add_argument(
        "--write",
        action="store_true",
        help="Apply changes in place. Default is DRY RUN (no writes).",
    )
    args = ap.parse_args()

    dry_run = not args.write
    mode = "DRY RUN" if dry_run else "WRITE"
    print(f"== convert_all_search_urls_v2 :: {mode} :: brand={args.brand} ==")

    files = collect_files(args.brand)
    if args.limit:
        files = files[: args.limit]
    print(f"Scanning {len(files)} file(s) ...")

    per_brand: dict[str, dict[str, int]] = defaultdict(lambda: {"converted": 0, "unconverted": 0})
    unconvertable: list[tuple[str, str]] = []

    for brand, path in files:
        c, u = process_file(brand, path, write=not dry_run, unconvertable=unconvertable)
        per_brand[brand]["converted"] += c
        per_brand[brand]["unconverted"] += u

    # Always dump unconvertable log for review
    try:
        UNCONVERTABLE_LOG.write_text(
            "\n".join(f"{b}\t{q}" for b, q in unconvertable) + "\n",
            encoding="utf-8",
        )
    except Exception as e:  # noqa: BLE001
        print(f"[warn] could not write unconvertable log: {e}", file=sys.stderr)

    print("\n=== Summary ===")
    for b, d in sorted(per_brand.items()):
        print(f"  {b}: converted={d['converted']} unconverted={d['unconverted']}")
    print(f"Unconvertable log: {UNCONVERTABLE_LOG}")

    if not dry_run:
        report = write_report(per_brand, unconvertable)
        print(f"Report: {report}")
    else:
        print("(dry run — no files written, no report generated)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
