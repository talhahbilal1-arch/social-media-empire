"""
Pre-deploy link checker.

Runs affiliate link validation on both sites before deployment.
Exits with code 1 if any issues found (blocks deployment).

Usage:
    python pre_deploy_check.py           # check both sites
    python pre_deploy_check.py --quick   # tag-only check (no HTTP requests)
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Add parent dir so we can import config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import AFFILIATE_TAGS, SITE_PATHS


TAG_RE = re.compile(r'[?&]tag=([^&"\'<>\s]+)')
AMAZON_LINK_RE = re.compile(
    r'https?://(?:www\.)?amazon\.com/[^\s"\'<>]+', re.IGNORECASE
)


def quick_tag_check(site_name: str, site_path: str, expected_tag: str):
    """Fast check: only validates affiliate tags (no HTTP requests)."""
    issues = []
    for root, _dirs, files in os.walk(site_path):
        for fname in files:
            if not fname.endswith(".html"):
                continue
            filepath = os.path.join(root, fname)
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                for lineno, line in enumerate(f, start=1):
                    for match in AMAZON_LINK_RE.finditer(line):
                        url = match.group(0)
                        tag_match = TAG_RE.search(url)
                        if tag_match:
                            found_tag = tag_match.group(1)
                            if found_tag != expected_tag:
                                rel = os.path.relpath(filepath, site_path)
                                issues.append((rel, lineno, found_tag))
                        else:
                            rel = os.path.relpath(filepath, site_path)
                            issues.append((rel, lineno, "(missing)"))
    return issues


def main():
    parser = argparse.ArgumentParser(description="Pre-deploy affiliate link check")
    parser.add_argument("--quick", action="store_true",
                        help="Tag-only check (no HTTP requests)")
    args = parser.parse_args()

    total_issues = 0

    if args.quick:
        # Fast tag-only check
        for site, path in SITE_PATHS.items():
            tag = AFFILIATE_TAGS[site]
            print(f"\n  Checking {site} tags (expected: {tag})...")
            issues = quick_tag_check(site, path, tag)
            if issues:
                print(f"  ISSUES FOUND: {len(issues)}")
                for rel, lineno, found in issues:
                    print(f"    {rel}:{lineno} — tag={found}")
                total_issues += len(issues)
            else:
                print(f"  All tags OK")
    else:
        # Full HTTP-based validation
        from validate_links import audit_site, print_report
        for site, path in SITE_PATHS.items():
            tag = AFFILIATE_TAGS[site]
            report = audit_site(site, path, tag, verbose=True)
            print_report(report)
            total_issues += len(report.broken) + len(report.wrong_tag) + len(report.broken_images)

    if total_issues > 0:
        print(f"\n  DEPLOY BLOCKED: {total_issues} issues found")
        sys.exit(1)
    else:
        print(f"\n  All checks passed — safe to deploy!")
        sys.exit(0)


if __name__ == "__main__":
    main()
