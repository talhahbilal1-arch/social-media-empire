"""
Affiliate link health checker.

Checks all Amazon affiliate links across website files using either
HTTP HEAD requests or the Rainforest API (if configured).

Reuses extract_asins.py for link discovery and rainforest_client.py
for API-based verification.
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path (same pattern as verify_asins.py)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from automation.links.extract_asins import extract_all_asins

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


def check_asin_http(asin: str, timeout: int = 10) -> dict:
    """
    Check a single ASIN via HTTP HEAD request.

    Args:
        asin: Amazon ASIN to check
        timeout: Request timeout in seconds

    Returns:
        Dict with status, http_status, and error info
    """
    import requests

    url = f"https://www.amazon.com/dp/{asin}"
    headers = {"User-Agent": USER_AGENT}

    for attempt in range(2):  # Retry once on failure
        try:
            resp = requests.head(
                url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True,
            )

            # Check for broken indicators
            final_url = resp.url or ""
            if resp.status_code >= 400:
                return {
                    "status": "broken",
                    "http_status": resp.status_code,
                    "error": f"HTTP {resp.status_code}",
                }

            if "/errors/" in final_url or "dogsofamazon" in final_url:
                return {
                    "status": "broken",
                    "http_status": resp.status_code,
                    "error": f"Redirected to error page: {final_url}",
                }

            return {
                "status": "valid",
                "http_status": resp.status_code,
                "error": None,
            }

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if attempt == 0:
                logger.warning(f"Retrying {asin} after error: {e}")
                time.sleep(1)
                continue
            return {
                "status": "error",
                "http_status": None,
                "error": str(e),
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "http_status": None,
                "error": str(e),
            }

    # Should not reach here, but just in case
    return {"status": "error", "http_status": None, "error": "Unknown error"}


def check_asin_rainforest(asin: str, client) -> dict:
    """
    Check a single ASIN via the Rainforest API.

    Args:
        asin: Amazon ASIN to check
        client: RainforestClient instance

    Returns:
        Dict with status, title, and error info
    """
    try:
        result = client.verify_asin(asin)
        return {
            "status": "valid" if result["valid"] else "broken",
            "http_status": None,
            "title": result.get("title"),
            "error": result.get("error"),
        }
    except Exception as e:
        return {
            "status": "error",
            "http_status": None,
            "title": None,
            "error": str(e),
        }


def run_checks(source_paths: list[str], output_dir: str, timeout: int = 10) -> dict:
    """
    Extract all ASINs from sources and check each one.

    Args:
        source_paths: Files/directories to scan for affiliate links
        output_dir: Directory to write reports to
        timeout: HTTP request timeout in seconds

    Returns:
        Full report dict
    """
    # Step 1: Extract ASINs
    logger.info(f"Scanning sources: {source_paths}")
    asins_data = extract_all_asins(source_paths)
    logger.info(
        f"Found {asins_data['total_links_found']} links, "
        f"{asins_data['unique_asins']} unique ASINs"
    )

    if asins_data["unique_asins"] == 0:
        logger.warning("No ASINs found in source files.")

    # Step 2: Determine check mode
    rainforest_client = None
    mode = "http"

    if os.getenv("RAINFOREST_API_KEY"):
        try:
            from automation.amazon.rainforest_client import RainforestClient
            rainforest_client = RainforestClient()
            mode = "rainforest"
            logger.info("Using Rainforest API for verification (more accurate)")
        except Exception as e:
            logger.warning(f"Failed to init Rainforest client, falling back to HTTP: {e}")

    if mode == "http":
        logger.info("Using HTTP HEAD requests for verification")

    # Step 3: Check each ASIN
    results = []
    valid_count = 0
    broken_count = 0
    error_count = 0

    for item in asins_data.get("asins", []):
        asin = item["asin"]
        logger.info(f"Checking {asin}...")

        if mode == "rainforest":
            check = check_asin_rainforest(asin, rainforest_client)
        else:
            check = check_asin_http(asin, timeout=timeout)
            # Rate limit: 1 request per second
            time.sleep(1)

        status = check["status"]
        if status == "valid":
            valid_count += 1
        elif status == "broken":
            broken_count += 1
        else:
            error_count += 1

        results.append({
            "asin": asin,
            "status": status,
            "http_status": check.get("http_status"),
            "title": check.get("title"),
            "error": check.get("error"),
            "locations": item.get("locations", []),
        })

    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "sources": source_paths,
        "summary": {
            "total": len(results),
            "valid": valid_count,
            "broken": broken_count,
            "errors": error_count,
        },
        "results": results,
    }

    return report


def write_json_report(report: dict, output_dir: Path) -> Path:
    """Write JSON report to output directory."""
    path = output_dir / "link_report.json"
    path.write_text(json.dumps(report, indent=2))
    logger.info(f"JSON report written to {path}")
    return path


def write_markdown_report(report: dict, output_dir: Path) -> Path:
    """Write Markdown summary to output directory."""
    summary = report["summary"]
    broken = [r for r in report["results"] if r["status"] != "valid"]

    lines = [
        "# Affiliate Link Health Report",
        "",
        f"**Checked at:** {report['checked_at']}",
        f"**Mode:** {report['mode']}",
        f"**Sources:** {', '.join(report['sources'])}",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total  | {summary['total']} |",
        f"| Valid  | {summary['valid']} |",
        f"| Broken | {summary['broken']} |",
        f"| Errors | {summary['errors']} |",
        "",
    ]

    if broken:
        lines.append("## Broken Links")
        lines.append("")
        lines.append("| ASIN | Status | Error | File Locations |")
        lines.append("|------|--------|-------|----------------|")

        for item in broken:
            locations = ", ".join(
                f"`{loc['file']}` L{loc['line']}"
                for loc in item.get("locations", [])[:3]
            )
            error = item.get("error") or "Unknown"
            lines.append(
                f"| `{item['asin']}` | {item['status']} | {error} | {locations} |"
            )

        lines.append("")
        lines.append("## Suggested Actions")
        lines.append("")
        lines.append("1. Remove or replace broken ASINs with working alternatives")
        lines.append("2. Search Amazon for similar products in the same category")
        lines.append("3. Update both the ASIN and any associated product images")
    else:
        lines.append("All affiliate links are valid.")

    lines.append("")

    path = output_dir / "link_report.md"
    path.write_text("\n".join(lines))
    logger.info(f"Markdown report written to {path}")
    return path


def write_github_issue(report: dict, output_dir: Path) -> Path | None:
    """Write GitHub issue body if there are broken links."""
    from automation.links.verify_asins import generate_github_issue_body

    broken = [r for r in report["results"] if r["status"] != "valid"]
    if not broken:
        return None

    # Build a report in the format generate_github_issue_body expects
    compat_report = {
        "verified_at": report["checked_at"],
        "summary": {
            "total": report["summary"]["total"],
            "invalid": report["summary"]["broken"],
            "errors": report["summary"]["errors"],
        },
        "results": [
            {
                "asin": r["asin"],
                "status": "invalid" if r["status"] == "broken" else r["status"],
                "error": r.get("error"),
                "locations": r.get("locations", []),
            }
            for r in report["results"]
            if r["status"] != "valid"
        ],
    }

    body = generate_github_issue_body(compat_report)
    if not body:
        return None

    path = output_dir / "github_issue_body.md"
    path.write_text(body)
    logger.info(f"GitHub issue body written to {path}")
    return path


def print_summary(report: dict):
    """Print a clear summary to stdout."""
    summary = report["summary"]
    broken = [r for r in report["results"] if r["status"] != "valid"]

    print()
    print("=" * 55)
    print("  AFFILIATE LINK HEALTH CHECK")
    print("=" * 55)
    print(f"  Mode:    {report['mode']}")
    print(f"  Sources: {', '.join(report['sources'])}")
    print(f"  Time:    {report['checked_at']}")
    print("-" * 55)
    print(f"  Total checked:  {summary['total']}")
    print(f"  Valid:          {summary['valid']}")
    print(f"  Broken:         {summary['broken']}")
    print(f"  Errors:         {summary['errors']}")
    print("=" * 55)

    if broken:
        print()
        print("  BROKEN LINKS:")
        for item in broken:
            error = item.get("error") or "Unknown"
            print(f"    {item['asin']}  [{item['status']}]  {error}")
            for loc in item.get("locations", [])[:2]:
                print(f"      -> {loc['file']} line {loc['line']}")
        print()
        print("  ACTION REQUIRED: Fix the broken links listed above.")
    else:
        print()
        print("  All affiliate links are healthy.")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Check health of Amazon affiliate links across website files"
    )
    parser.add_argument(
        "--source",
        nargs="+",
        default=["outputs/fitover35-website/", "dailydealdarling_website/"],
        help="Files or directories to scan (default: website output dirs)",
    )
    parser.add_argument(
        "--output-dir",
        default="automation/links/reports/",
        help="Directory for output reports (default: automation/links/reports/)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="HTTP request timeout in seconds (default: 10)",
    )

    args = parser.parse_args()

    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run checks
    report = run_checks(args.source, args.output_dir, timeout=args.timeout)

    # Write reports
    write_json_report(report, output_dir)
    write_markdown_report(report, output_dir)
    write_github_issue(report, output_dir)

    # Print summary
    print_summary(report)

    # Exit code: 0 if all valid, 1 if any broken/error
    if report["summary"]["broken"] > 0 or report["summary"]["errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
