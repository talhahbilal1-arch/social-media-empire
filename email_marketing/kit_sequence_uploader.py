#!/usr/bin/env python3
"""
Kit (ConvertKit) Sequence Uploader
Reads JSON sequence files and uploads them to Kit via API v4.

Usage:
    python kit_sequence_uploader.py                     # Dry-run (default)
    python kit_sequence_uploader.py --live              # Actually push to Kit
    python kit_sequence_uploader.py --brand fitness     # Upload single brand
    python kit_sequence_uploader.py --list              # List all sequences

Requires:
    KIT_API_KEY     - Kit API key (from Kit account settings)
    KIT_API_SECRET  - Kit API secret

Kit API v4 docs: https://developers.kit.com/v4
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Install with: pip install requests")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

KIT_API_BASE = "https://api.kit.com/v4"

BRAND_CONFIG = {
    "fitness": {
        "name": "Fit Over 35 Welcome Sequence",
        "json_file": "sequences/fitness_welcome.json",
        "form_id": 8946984,
        "from_name": "Fit Over 35",
        "from_email": "hello@fitover35.com",
        "affiliate_tag": "fitover3509-20",
    },
    "deals": {
        "name": "Daily Deal Darling Welcome Sequence",
        "json_file": "sequences/deals_welcome.json",
        "form_id": 9144859,
        "from_name": "Sarah from Daily Deal Darling",
        "from_email": "sarah@dailydealdarling.com",
        "affiliate_tag": "dailydealdarl-20",
    },
    "menopause": {
        "name": "Menopause Planner Welcome Sequence",
        "json_file": "sequences/menopause_welcome.json",
        "form_id": 9144926,
        "from_name": "The Menopause Planner",
        "from_email": "hello@menopauseplanner.com",
        "affiliate_tag": "dailydealdarl-20",
    },
    "reengagement": {
        "name": "Cross-Brand Re-Engagement Sequence",
        "json_file": "sequences/reengagement_welcome.json",
        "form_id": None,  # Applied per-brand via automation
        "from_name": None,
        "from_email": None,
        "affiliate_tag": None,
    },
}

SCRIPT_DIR = Path(__file__).parent


# ---------------------------------------------------------------------------
# Kit API Client
# ---------------------------------------------------------------------------

class KitClient:
    """Minimal Kit API v4 client."""

    def __init__(self, api_key: str, api_secret: str, live: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.live = live
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make an API request. In dry-run mode, just print what would happen."""
        url = f"{KIT_API_BASE}/{endpoint.lstrip('/')}"

        if not self.live:
            print(f"  [DRY-RUN] {method} {url}")
            if data:
                print(f"            Payload: {json.dumps(data, indent=2)[:500]}")
            return {"id": 0, "name": "dry-run-placeholder"}

        resp = self.session.request(method, url, json=data)

        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", 5))
            print(f"  Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            resp = self.session.request(method, url, json=data)

        if resp.status_code not in (200, 201):
            print(f"  ERROR: {resp.status_code} {resp.text[:300]}")
            return None

        return resp.json()

    def create_sequence(self, name: str) -> dict:
        """Create a new email sequence."""
        return self._request("POST", "sequences", {
            "name": name,
        })

    def add_email_to_sequence(self, sequence_id: int, email_data: dict) -> dict:
        """Add an email to an existing sequence."""
        return self._request("POST", f"sequences/{sequence_id}/emails", {
            "subject": email_data["subject"],
            "body": email_data.get("body_html") or email_data.get("body_text", ""),
            "delay": email_data.get("delay_days", 0),
        })

    def list_sequences(self) -> list:
        """List all sequences."""
        result = self._request("GET", "sequences")
        if result and "sequences" in result:
            return result["sequences"]
        return result if isinstance(result, list) else []

    def add_form_to_sequence(self, form_id: int, sequence_id: int) -> dict:
        """Link a form to trigger a sequence (via automation/rules)."""
        return self._request("POST", "automations/rules", {
            "trigger": {"type": "form_subscribe", "form_id": form_id},
            "action": {"type": "add_to_sequence", "sequence_id": sequence_id},
        })


# ---------------------------------------------------------------------------
# Sequence Loading
# ---------------------------------------------------------------------------

def load_sequence(brand_key: str) -> list:
    """Load a sequence JSON file for a given brand."""
    config = BRAND_CONFIG.get(brand_key)
    if not config:
        print(f"ERROR: Unknown brand '{brand_key}'")
        return []

    json_path = SCRIPT_DIR / config["json_file"]
    if not json_path.exists():
        print(f"ERROR: Sequence file not found: {json_path}")
        return []

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_affiliate_tags(emails: list, expected_tag: str, brand_key: str) -> list:
    """Check that all affiliate links use the correct tag for this brand."""
    issues = []
    if not expected_tag:
        return issues

    for email in emails:
        links = email.get("affiliate_links", [])
        for link in links:
            if "tag=" in link and expected_tag not in link:
                issues.append({
                    "email": email.get("sequence_order"),
                    "subject": email.get("subject"),
                    "link": link,
                    "expected_tag": expected_tag,
                })
    return issues


# ---------------------------------------------------------------------------
# Upload Logic
# ---------------------------------------------------------------------------

def upload_brand_sequence(client: KitClient, brand_key: str) -> bool:
    """Upload a single brand's welcome sequence to Kit."""
    config = BRAND_CONFIG[brand_key]
    emails = load_sequence(brand_key)

    if not emails:
        return False

    print(f"\n{'='*60}")
    print(f"Brand: {config['name']}")
    print(f"Emails: {len(emails)}")
    print(f"Form ID: {config['form_id']}")
    print(f"Affiliate Tag: {config['affiliate_tag']}")
    print(f"{'='*60}")

    # Validate affiliate tags
    tag_issues = validate_affiliate_tags(emails, config["affiliate_tag"], brand_key)
    if tag_issues:
        print(f"\n  WARNING: {len(tag_issues)} affiliate tag issue(s) found:")
        for issue in tag_issues:
            print(f"    Email {issue['email']} ({issue['subject']})")
            print(f"      Link: {issue['link']}")
            print(f"      Expected tag: {issue['expected_tag']}")
        if client.live:
            print("  Aborting upload for this brand. Fix tags first.")
            return False

    # Create the sequence
    print(f"\n  Creating sequence: {config['name']}")
    seq_result = client.create_sequence(config["name"])
    if not seq_result:
        print("  FAILED to create sequence.")
        return False

    sequence_id = seq_result.get("id", 0)
    print(f"  Sequence ID: {sequence_id}")

    # Add each email
    for email in emails:
        order = email["sequence_order"]
        subject = email["subject"]
        delay = email["delay_days"]
        print(f"\n  Adding Email {order}: \"{subject}\" (delay: {delay} days)")

        body = email.get("body_html") or email.get("body_text", "")
        if not body:
            print(f"    WARNING: Email {order} has no body content.")

        email_result = client.add_email_to_sequence(sequence_id, {
            "subject": subject,
            "body_html": email.get("body_html", ""),
            "body_text": email.get("body_text", ""),
            "delay_days": delay,
        })

        if email_result:
            print(f"    OK (email ID: {email_result.get('id', 'n/a')})")
        else:
            print(f"    FAILED to add email {order}")

        # Rate limit courtesy
        if client.live:
            time.sleep(0.5)

    # Link form to sequence
    if config["form_id"] and sequence_id:
        print(f"\n  Linking form {config['form_id']} -> sequence {sequence_id}")
        client.add_form_to_sequence(config["form_id"], sequence_id)

    print(f"\n  Done: {config['name']}")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def list_sequences_info():
    """Print a summary of all available sequences."""
    print("\nAvailable email sequences:\n")
    for key, config in BRAND_CONFIG.items():
        json_path = SCRIPT_DIR / config["json_file"]
        exists = json_path.exists()

        if exists:
            with open(json_path, "r", encoding="utf-8") as f:
                emails = json.load(f)
            count = len(emails)
            total_links = sum(len(e.get("affiliate_links", [])) for e in emails)
        else:
            count = 0
            total_links = 0

        status = "OK" if exists else "MISSING"
        print(f"  [{status}] {key}")
        print(f"         Name: {config['name']}")
        print(f"         File: {config['json_file']}")
        print(f"         Emails: {count}")
        print(f"         Affiliate links: {total_links}")
        print(f"         Form ID: {config['form_id']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Upload email sequences to Kit (ConvertKit) via API v4"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Actually push to Kit API (default: dry-run)",
    )
    parser.add_argument(
        "--brand",
        choices=list(BRAND_CONFIG.keys()),
        help="Upload a single brand (default: all)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_sequences",
        help="List all available sequences and exit",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate affiliate tags, don't upload",
    )

    args = parser.parse_args()

    # List mode
    if args.list_sequences:
        list_sequences_info()
        return

    # Validate-only mode
    if args.validate_only:
        print("\nValidating affiliate tags across all sequences...\n")
        all_ok = True
        for key, config in BRAND_CONFIG.items():
            emails = load_sequence(key)
            if not emails:
                continue
            issues = validate_affiliate_tags(emails, config["affiliate_tag"], key)
            if issues:
                all_ok = False
                print(f"  FAIL: {key} has {len(issues)} tag issue(s):")
                for issue in issues:
                    print(f"    Email {issue['email']}: {issue['link']}")
            else:
                print(f"  OK: {key}")
        if all_ok:
            print("\nAll affiliate tags are correct.")
        else:
            print("\nSome tags need fixing. See above.")
        return

    # Upload mode - check env vars
    api_key = os.environ.get("KIT_API_KEY", "")
    api_secret = os.environ.get("KIT_API_SECRET", "")

    if args.live and (not api_key or not api_secret):
        print("ERROR: KIT_API_KEY and KIT_API_SECRET environment variables required for --live mode.")
        print("  Set them with:")
        print("    export KIT_API_KEY=your_key_here")
        print("    export KIT_API_SECRET=your_secret_here")
        sys.exit(1)

    mode = "LIVE" if args.live else "DRY-RUN"
    print(f"\nKit Sequence Uploader ({mode} mode)")
    print(f"{'='*40}")

    if not args.live:
        print("(No changes will be made. Use --live to push to Kit.)\n")

    client = KitClient(api_key or "dry-run-key", api_secret or "dry-run-secret", live=args.live)

    # Determine which brands to upload
    brands = [args.brand] if args.brand else [k for k in BRAND_CONFIG.keys() if k != "reengagement"]

    success_count = 0
    for brand_key in brands:
        ok = upload_brand_sequence(client, brand_key)
        if ok:
            success_count += 1

    print(f"\n{'='*40}")
    print(f"Completed: {success_count}/{len(brands)} sequences uploaded ({mode})")

    if not args.live:
        print("\nTo actually push to Kit, run with --live flag:")
        print("  python kit_sequence_uploader.py --live")


if __name__ == "__main__":
    main()
