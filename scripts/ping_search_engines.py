#!/usr/bin/env python3
"""Ping Google and Bing with updated sitemaps."""

import requests
import sys
import json
from datetime import datetime
from pathlib import Path

# Sitemaps to ping
SITEMAPS = [
    'https://fitover35.com/sitemap.xml',
    'https://dailydealdarling.com/sitemap.xml',
    'https://menopause-planner-website.vercel.app/sitemap.xml',
    'https://pilottools.ai/sitemap.xml',
]

def ping_sitemaps():
    """Ping Google and Bing search engines with updated sitemaps."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'google': {},
        'bing': {},
        'summary': {'success': 0, 'failed': 0}
    }

    for sitemap in SITEMAPS:
        brand = sitemap.split('//')[1].split('.')[0]  # Extract brand name

        # Google
        try:
            r = requests.get(
                f'https://www.google.com/ping?sitemap={sitemap}',
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            status_msg = f"Success ({r.status_code})" if r.status_code == 200 else f"Status {r.status_code}"
            results['google'][brand] = status_msg
            print(f"✓ Google ping {brand}: {status_msg}")
            if r.status_code == 200:
                results['summary']['success'] += 1
            else:
                results['summary']['failed'] += 1
        except Exception as e:
            results['google'][brand] = f"Failed: {str(e)}"
            print(f"✗ Google ping {brand}: FAILED ({e})")
            results['summary']['failed'] += 1

        # Bing
        try:
            r = requests.get(
                f'https://www.bing.com/ping?sitemap={sitemap}',
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            status_msg = f"Success ({r.status_code})" if r.status_code == 200 else f"Status {r.status_code}"
            results['bing'][brand] = status_msg
            print(f"✓ Bing ping {brand}: {status_msg}")
            if r.status_code == 200:
                results['summary']['success'] += 1
            else:
                results['summary']['failed'] += 1
        except Exception as e:
            results['bing'][brand] = f"Failed: {str(e)}"
            print(f"✗ Bing ping {brand}: FAILED ({e})")
            results['summary']['failed'] += 1

    # Log results
    log_file = Path.home() / 'tall-command-center' / 'briefings' / f'seo-ping-{datetime.now().strftime("%Y-%m-%d")}.json'
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📊 Summary: {results['summary']['success']} successful, {results['summary']['failed']} failed")
    print(f"📝 Log saved to {log_file}")

    return 0 if results['summary']['failed'] == 0 else 1

if __name__ == '__main__':
    sys.exit(ping_sitemaps())
