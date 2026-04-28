#!/usr/bin/env python3
"""
Set up menopauseplanner.com DNS records on Namecheap for Vercel hosting.

Required env vars:
  NAMECHEAP_API_USER  - your Namecheap username
  NAMECHEAP_API_KEY   - API key from https://ap.www.namecheap.com/settings/tools/apiaccess/
  NAMECHEAP_USERNAME  - same as NAMECHEAP_API_USER (PyNamecheap requires both)
  NAMECHEAP_CLIENT_IP - your public IP (whitelisted in Namecheap API settings)

Install dependency:
  pip3 install PyNamecheap --break-system-packages

Vercel records being added:
  A     @    76.76.21.21
  CNAME www  cname.vercel-dns.com
"""

import os
import sys

DOMAIN_SLD = "menopauseplanner"
DOMAIN_TLD = "com"

VERCEL_RECORDS = [
    {"Type": "A",     "Name": "@",   "Address": "76.76.21.21",       "TTL": "1800"},
    {"Type": "CNAME", "Name": "www", "Address": "cname.vercel-dns.com", "TTL": "1800"},
]


def check_deps():
    try:
        import namecheap  # noqa: F401
    except ImportError:
        print("PyNamecheap not installed. Run:")
        print("  pip3 install PyNamecheap --break-system-packages")
        sys.exit(1)


def get_env():
    required = ["NAMECHEAP_API_USER", "NAMECHEAP_API_KEY", "NAMECHEAP_USERNAME", "NAMECHEAP_CLIENT_IP"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print("Missing required environment variables:")
        for k in missing:
            print(f"  {k}")
        print("\nSet them and re-run. Example:")
        print("  export NAMECHEAP_API_USER=youruser")
        print("  export NAMECHEAP_API_KEY=yourkey")
        print("  export NAMECHEAP_USERNAME=youruser")
        print("  export NAMECHEAP_CLIENT_IP=$(curl -s https://api.ipify.org)")
        sys.exit(1)
    return {
        "api_user": os.environ["NAMECHEAP_API_USER"],
        "api_key": os.environ["NAMECHEAP_API_KEY"],
        "username": os.environ["NAMECHEAP_USERNAME"],
        "client_ip": os.environ["NAMECHEAP_CLIENT_IP"],
    }


def merge_records(existing, new_records):
    """
    Add new_records to existing list, skipping any that already match
    on both Type and Name (case-insensitive) to avoid duplicates.
    """
    merged = list(existing)
    existing_keys = {(r.get("Type", "").upper(), r.get("Name", "").lower()) for r in existing}
    for rec in new_records:
        key = (rec["Type"].upper(), rec["Name"].lower())
        if key in existing_keys:
            print(f"  [skip] {rec['Type']} {rec['Name']} already exists")
        else:
            merged.append(rec)
            print(f"  [add]  {rec['Type']} {rec['Name']} → {rec['Address']}")
    return merged


def run():
    check_deps()
    creds = get_env()

    import namecheap

    api = namecheap.Api(
        ApiUser=creds["api_user"],
        ApiKey=creds["api_key"],
        UserName=creds["username"],
        ClientIp=creds["client_ip"],
        sandbox=False,
    )

    print(f"Fetching existing DNS records for {DOMAIN_SLD}.{DOMAIN_TLD}...")
    existing = api.domains_dns_getHosts(DOMAIN_SLD, DOMAIN_TLD)
    print(f"  Found {len(existing)} existing record(s)")

    print("\nMerging Vercel records:")
    merged = merge_records(existing, VERCEL_RECORDS)

    print(f"\nSetting {len(merged)} total record(s)...")
    api.domains_dns_setHosts(DOMAIN_SLD, DOMAIN_TLD, merged)
    print("Done. DNS records updated.")
    print("\nNote: DNS propagation typically takes 5–30 minutes.")
    print("After propagation, add the custom domain in Vercel:")
    print("  npx vercel domains add menopauseplanner.com --scope talhahbilal1-arch")


if __name__ == "__main__":
    run()
