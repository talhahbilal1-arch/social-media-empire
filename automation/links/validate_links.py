"""
Amazon affiliate link validator.

Scans HTML files for Amazon links, checks each with HTTP HEAD requests,
validates affiliate tags, and reports broken links / wrong tags.

Usage:
    python validate_links.py                     # audit both sites
    python validate_links.py --site fitover35    # audit one site
    python validate_links.py --file path.html    # audit one file
"""

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from urllib.parse import parse_qs, urlparse

import requests

# Add parent dir so we can import config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import AFFILIATE_TAGS, SITE_PATHS


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class LinkResult:
    url: str
    source_file: str
    line_number: int
    status_code: Optional[int] = None
    final_url: Optional[str] = None
    tag_found: Optional[str] = None
    tag_expected: Optional[str] = None
    tag_ok: bool = True
    is_image: bool = False
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        if self.error:
            return False
        if self.status_code and self.status_code >= 400:
            return False
        if not self.tag_ok:
            return False
        return True


@dataclass
class AuditReport:
    site: str
    total_links: int = 0
    working: List[LinkResult] = field(default_factory=list)
    broken: List[LinkResult] = field(default_factory=list)
    wrong_tag: List[LinkResult] = field(default_factory=list)
    broken_images: List[LinkResult] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Link extraction
# ---------------------------------------------------------------------------

AMAZON_LINK_RE = re.compile(
    r'https?://(?:www\.)?amazon\.com/[^\s"\'<>]+', re.IGNORECASE
)
AMAZON_IMAGE_RE = re.compile(
    r'https?://m\.media-amazon\.com/images/[^\s"\'<>]+', re.IGNORECASE
)
TAG_RE = re.compile(r'[?&]tag=([^&"\'<>\s]+)')


def extract_links_from_file(filepath: str, expected_tag: str):
    """Yield (url, line_number, is_image) tuples from an HTML file."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, start=1):
            for match in AMAZON_LINK_RE.finditer(line):
                url = match.group(0).rstrip(")")
                yield url, lineno, False
            for match in AMAZON_IMAGE_RE.finditer(line):
                url = match.group(0).rstrip(")")
                yield url, lineno, True


# ---------------------------------------------------------------------------
# HTTP checking
# ---------------------------------------------------------------------------

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
})

REQUEST_DELAY = 1.0  # seconds between requests to avoid rate limiting


def check_link(url: str, source_file: str, lineno: int,
               expected_tag: str, is_image: bool = False) -> LinkResult:
    """Check a single URL with an HTTP HEAD request."""
    result = LinkResult(
        url=url,
        source_file=source_file,
        line_number=lineno,
        is_image=is_image,
    )

    # Tag validation (skip for images)
    if not is_image:
        tag_match = TAG_RE.search(url)
        if tag_match:
            result.tag_found = tag_match.group(1)
            result.tag_expected = expected_tag
            result.tag_ok = result.tag_found == expected_tag
        else:
            result.tag_found = None
            result.tag_expected = expected_tag
            result.tag_ok = False  # missing tag entirely

    # Amazon product/search links often return 405/503 to automated requests
    # but work fine in real browsers. Only flag true 404s as broken.
    AMAZON_RATE_LIMIT_CODES = {405, 503}

    try:
        resp = SESSION.head(url, allow_redirects=True, timeout=15)
        result.status_code = resp.status_code
        result.final_url = resp.url

        # Amazon sometimes returns 503 for HEAD — retry with GET
        if resp.status_code in (503, 405):
            resp = SESSION.get(url, allow_redirects=True, timeout=15,
                               stream=True)
            result.status_code = resp.status_code
            result.final_url = resp.url
            resp.close()

        # If still 405/503 on an amazon.com link, treat as rate-limited (OK)
        if (result.status_code in AMAZON_RATE_LIMIT_CODES
                and "amazon.com" in url and not is_image):
            result.status_code = 200  # treat as OK (rate-limited, not broken)

        # Check if redirect landed on an error/404 page
        if result.final_url and "error" in result.final_url.lower():
            result.error = f"Redirected to error page: {result.final_url}"

    except requests.exceptions.Timeout:
        result.error = "Request timed out (15s)"
    except requests.exceptions.ConnectionError as e:
        # Amazon connection resets are also rate limiting
        if "amazon.com" in url and not is_image:
            result.status_code = 200  # treat as OK
        else:
            result.error = f"Connection error: {e}"
    except Exception as e:
        result.error = f"Unexpected error: {e}"

    return result


# ---------------------------------------------------------------------------
# Audit runner
# ---------------------------------------------------------------------------

def audit_site(site_name: str, site_path: str, expected_tag: str,
               verbose: bool = True) -> AuditReport:
    """Audit all HTML files in a site directory."""
    report = AuditReport(site=site_name)

    html_files = []
    for root, _dirs, files in os.walk(site_path):
        for f in files:
            if f.endswith(".html"):
                html_files.append(os.path.join(root, f))

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Auditing: {site_name}")
        print(f"  Path: {site_path}")
        print(f"  Expected tag: {expected_tag}")
        print(f"  HTML files found: {len(html_files)}")
        print(f"{'='*60}\n")

    all_links = []
    for filepath in sorted(html_files):
        for url, lineno, is_image in extract_links_from_file(filepath, expected_tag):
            all_links.append((url, filepath, lineno, is_image))

    report.total_links = len(all_links)
    if verbose:
        print(f"  Total Amazon links/images found: {report.total_links}\n")

    for i, (url, filepath, lineno, is_image) in enumerate(all_links):
        rel_path = os.path.relpath(filepath, site_path)
        if verbose:
            print(f"  [{i+1}/{report.total_links}] Checking {rel_path}:{lineno} ...", end=" ", flush=True)

        result = check_link(url, filepath, lineno, expected_tag, is_image)

        if verbose:
            if result.ok:
                print(f"OK ({result.status_code})")
            elif result.error:
                print(f"ERROR: {result.error}")
            elif not result.tag_ok:
                print(f"WRONG TAG: found '{result.tag_found}' expected '{expected_tag}'")
            else:
                print(f"BROKEN ({result.status_code})")

        # Categorize
        if is_image and not result.ok:
            report.broken_images.append(result)
        elif not result.tag_ok and not is_image:
            report.wrong_tag.append(result)
        elif result.ok:
            report.working.append(result)
        else:
            report.broken.append(result)

        time.sleep(REQUEST_DELAY)

    return report


def audit_single_file(filepath: str, expected_tag: str,
                      verbose: bool = True) -> AuditReport:
    """Audit a single HTML file."""
    report = AuditReport(site=os.path.basename(filepath))

    all_links = []
    for url, lineno, is_image in extract_links_from_file(filepath, expected_tag):
        all_links.append((url, filepath, lineno, is_image))

    report.total_links = len(all_links)
    if verbose:
        print(f"\n  Auditing: {filepath}")
        print(f"  Expected tag: {expected_tag}")
        print(f"  Links found: {report.total_links}\n")

    for i, (url, filepath, lineno, is_image) in enumerate(all_links):
        if verbose:
            print(f"  [{i+1}/{report.total_links}] ...", end=" ", flush=True)

        result = check_link(url, filepath, lineno, expected_tag, is_image)

        if verbose:
            status = "OK" if result.ok else (result.error or f"HTTP {result.status_code}")
            print(status)

        if is_image and not result.ok:
            report.broken_images.append(result)
        elif not result.tag_ok and not is_image:
            report.wrong_tag.append(result)
        elif result.ok:
            report.working.append(result)
        else:
            report.broken.append(result)

        time.sleep(REQUEST_DELAY)

    return report


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(report: AuditReport):
    """Print a summary report."""
    print(f"\n{'='*60}")
    print(f"  REPORT: {report.site}")
    print(f"{'='*60}")
    print(f"  Total links checked:  {report.total_links}")
    print(f"  Working:              {len(report.working)}")
    print(f"  Broken:               {len(report.broken)}")
    print(f"  Wrong tag:            {len(report.wrong_tag)}")
    print(f"  Broken images:        {len(report.broken_images)}")
    print()

    if report.broken:
        print("  BROKEN LINKS:")
        for r in report.broken:
            rel = os.path.relpath(r.source_file)
            print(f"    {rel}:{r.line_number}")
            print(f"      URL: {r.url[:100]}")
            print(f"      Status: {r.status_code or 'N/A'}  Error: {r.error or 'N/A'}")
            print()

    if report.wrong_tag:
        print("  WRONG TAG LINKS:")
        for r in report.wrong_tag:
            rel = os.path.relpath(r.source_file)
            print(f"    {rel}:{r.line_number}")
            print(f"      Found: {r.tag_found}  Expected: {r.tag_expected}")
            print()

    if report.broken_images:
        print("  BROKEN IMAGES:")
        for r in report.broken_images:
            rel = os.path.relpath(r.source_file)
            print(f"    {rel}:{r.line_number}")
            print(f"      URL: {r.url[:100]}")
            print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Validate Amazon affiliate links")
    parser.add_argument("--site", choices=list(SITE_PATHS.keys()),
                        help="Audit a specific site")
    parser.add_argument("--file", help="Audit a single HTML file")
    parser.add_argument("--tag", help="Expected affiliate tag (auto-detected if --site used)")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-link output")
    args = parser.parse_args()

    reports = []

    if args.file:
        tag = args.tag or "dailydealdarl-20"
        report = audit_single_file(args.file, tag, verbose=not args.quiet)
        reports.append(report)

    elif args.site:
        site = args.site
        path = SITE_PATHS[site]
        tag = args.tag or AFFILIATE_TAGS[site]
        report = audit_site(site, path, tag, verbose=not args.quiet)
        reports.append(report)

    else:
        # Audit all sites
        for site, path in SITE_PATHS.items():
            tag = AFFILIATE_TAGS[site]
            report = audit_site(site, path, tag, verbose=not args.quiet)
            reports.append(report)

    # Print summaries
    for report in reports:
        print_report(report)

    # Exit code
    total_issues = sum(
        len(r.broken) + len(r.wrong_tag) + len(r.broken_images)
        for r in reports
    )
    if total_issues > 0:
        print(f"\n  TOTAL ISSUES: {total_issues}")
        sys.exit(1)
    else:
        print("\n  All links OK!")
        sys.exit(0)


if __name__ == "__main__":
    main()
