"""
Phase 8: Add Exit-Intent & Scroll-Triggered Email Capture

Adds email capture bars to all articles across 3 brands.
Triggers on exit intent and 60% scroll depth.
"""

import os
from pathlib import Path
from bs4 import BeautifulSoup

# Brand-specific email capture HTML
EMAIL_CAPTURES = {
    'fitness': '''<div id="capture-bar" data-capture-modal style="display:none;position:fixed;bottom:0;left:0;right:0;background:#1a181e;border-top:2px solid #d4a843;padding:14px 20px;z-index:300;box-shadow:0 -4px 20px rgba(0,0,0,.3);transform:translateY(100%);transition:transform .3s ease">
<div style="max-width:680px;margin:0 auto;display:flex;align-items:center;gap:12px;flex-wrap:wrap">
<div style="flex:1;min-width:200px"><strong style="color:#d4a843;font-size:.9rem">FREE 7-Day Fat Burn Plan</strong><p style="color:#8a8894;font-size:.78rem;margin:2px 0 0">Join 7,500+ men building muscle after 35</p></div>
<form action="https://app.kit.com/forms/8946984/subscriptions" method="post" data-sv-form="8946984" style="display:flex;gap:6px;flex:1;min-width:240px"><input type="email" name="email_address" placeholder="Your email" required style="flex:1;padding:10px 12px;border:1px solid #2e2c33;border-radius:6px;background:#111014;color:#fff;font-size:.85rem"><button type="submit" style="padding:10px 16px;background:#d4a843;color:#111;border:none;border-radius:6px;font-weight:700;font-size:.85rem;cursor:pointer;white-space:nowrap">Get Free Plan</button></form>
<button onclick="this.parentElement.parentElement.style.display='none'" style="background:none;border:none;color:#8a8894;font-size:1.2rem;cursor:pointer;padding:4px">✕</button>
</div></div>
<script>
(function(){var shown=false;function showBar(){if(shown)return;shown=true;var b=document.getElementById('capture-bar');if(b){b.style.display='block';setTimeout(function(){b.style.transform='translateY(0)'},50)}}
window.addEventListener('scroll',function(){var h=document.documentElement.scrollHeight-window.innerHeight;if(h>0&&window.scrollY/h>0.6)showBar()});
document.addEventListener('mouseout',function(e){if(e.clientY<10&&!e.relatedTarget)showBar()})})();
</script>''',

    'deals': '''<div id="capture-bar" data-capture-modal style="display:none;position:fixed;bottom:0;left:0;right:0;background:#fff8f0;border-top:2px solid #E91E63;padding:14px 20px;z-index:300;box-shadow:0 -4px 20px rgba(0,0,0,.15);transform:translateY(100%);transition:transform .3s ease">
<div style="max-width:680px;margin:0 auto;display:flex;align-items:center;gap:12px;flex-wrap:wrap">
<div style="flex:1;min-width:200px"><strong style="color:#E91E63;font-size:.9rem">FREE Weekly Deals Digest</strong><p style="color:#666;font-size:.78rem;margin:2px 0 0">Join smart shoppers saving 40%+ weekly</p></div>
<form action="https://app.kit.com/forms/9144859/subscriptions" method="post" data-sv-form="9144859" style="display:flex;gap:6px;flex:1;min-width:240px"><input type="email" name="email_address" placeholder="Your email" required style="flex:1;padding:10px 12px;border:1px solid #ddd;border-radius:6px;background:#fff;color:#333;font-size:.85rem"><button type="submit" style="padding:10px 16px;background:#E91E63;color:#fff;border:none;border-radius:6px;font-weight:700;font-size:.85rem;cursor:pointer;white-space:nowrap">Get Free Digest</button></form>
<button onclick="this.parentElement.parentElement.style.display='none'" style="background:none;border:none;color:#999;font-size:1.2rem;cursor:pointer;padding:4px">✕</button>
</div></div>
<script>
(function(){var shown=false;function showBar(){if(shown)return;shown=true;var b=document.getElementById('capture-bar');if(b){b.style.display='block';setTimeout(function(){b.style.transform='translateY(0)'},50)}}
window.addEventListener('scroll',function(){var h=document.documentElement.scrollHeight-window.innerHeight;if(h>0&&window.scrollY/h>0.6)showBar()});
document.addEventListener('mouseout',function(e){if(e.clientY<10&&!e.relatedTarget)showBar()})})();
</script>''',

    'menopause': '''<div id="capture-bar" data-capture-modal style="display:none;position:fixed;bottom:0;left:0;right:0;background:#f5f0f8;border-top:2px solid #7B1FA2;padding:14px 20px;z-index:300;box-shadow:0 -4px 20px rgba(0,0,0,.15);transform:translateY(100%);transition:transform .3s ease">
<div style="max-width:680px;margin:0 auto;display:flex;align-items:center;gap:12px;flex-wrap:wrap">
<div style="flex:1;min-width:200px"><strong style="color:#7B1FA2;font-size:.9rem">FREE Menopause Symptom Tracker</strong><p style="color:#666;font-size:.78rem;margin:2px 0 0">Join 5,000+ women managing menopause naturally</p></div>
<form action="https://app.kit.com/forms/9144926/subscriptions" method="post" data-sv-form="9144926" style="display:flex;gap:6px;flex:1;min-width:240px"><input type="email" name="email_address" placeholder="Your email" required style="flex:1;padding:10px 12px;border:1px solid #ddd;border-radius:6px;background:#fff;color:#333;font-size:.85rem"><button type="submit" style="padding:10px 16px;background:#7B1FA2;color:#fff;border:none;border-radius:6px;font-weight:700;font-size:.85rem;cursor:pointer;white-space:nowrap">Get Free Tracker</button></form>
<button onclick="this.parentElement.parentElement.style.display='none'" style="background:none;border:none;color:#999;font-size:1.2rem;cursor:pointer;padding:4px">✕</button>
</div></div>
<script>
(function(){var shown=false;function showBar(){if(shown)return;shown=true;var b=document.getElementById('capture-bar');if(b){b.style.display='block';setTimeout(function(){b.style.transform='translateY(0)'},50)}}
window.addEventListener('scroll',function(){var h=document.documentElement.scrollHeight-window.innerHeight;if(h>0&&window.scrollY/h>0.6)showBar()});
document.addEventListener('mouseout',function(e){if(e.clientY<10&&!e.relatedTarget)showBar()})})();
</script>'''
}

def detect_brand(filepath):
    """Detect brand from file path"""
    path_str = str(filepath).lower()
    if 'fitover35' in path_str:
        return 'fitness'
    elif 'dailydealdarling' in path_str:
        return 'deals'
    elif 'menopause' in path_str:
        return 'menopause'
    return None

def has_capture_modal(html):
    """Check if HTML already has email capture modal"""
    return 'data-capture-modal' in html

def add_email_capture(filepath, brand):
    """Add email capture snippet to article before </body>"""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Check if already has capture
    if has_capture_modal(html):
        return False, 'already_has'

    # Get brand-specific capture HTML
    capture_html = EMAIL_CAPTURES.get(brand)
    if not capture_html:
        return False, 'unknown_brand'

    # Insert before </body>
    if '</body>' not in html:
        return False, 'no_body_tag'

    # Insert capture snippet before </body>
    html = html.replace('</body>', f'{capture_html}\n</body>')

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return True, 'added'

def main():
    base_path = Path('C:/Users/talha/Desktop/social-media-empire/outputs')

    # Define article directories for each brand
    directories = {
        'fitness': base_path / 'fitover35-website/articles',
        'deals': base_path / 'dailydealdarling-website/articles',
        'menopause': base_path / 'menopause-planner-website/articles'
    }

    stats = {
        'total': 0,
        'already_has': 0,
        'newly_added': 0,
        'errors': 0,
        'by_brand': {
            'fitness': {'total': 0, 'already_has': 0, 'newly_added': 0},
            'deals': {'total': 0, 'already_has': 0, 'newly_added': 0},
            'menopause': {'total': 0, 'already_has': 0, 'newly_added': 0}
        }
    }

    print("=" * 60)
    print("EMAIL CAPTURE ADDITION - PHASE 8")
    print("=" * 60)
    print()

    for brand, dir_path in directories.items():
        if not dir_path.exists():
            print(f"WARNING: Directory not found: {dir_path}")
            continue

        print(f"Processing {brand.upper()} articles...")

        # Find all HTML files
        html_files = list(dir_path.glob('*.html'))

        for filepath in html_files:
            stats['total'] += 1
            stats['by_brand'][brand]['total'] += 1

            success, status = add_email_capture(filepath, brand)

            if status == 'already_has':
                stats['already_has'] += 1
                stats['by_brand'][brand]['already_has'] += 1
                print(f"  SKIP (already has): {filepath.name}")

            elif status == 'added':
                stats['newly_added'] += 1
                stats['by_brand'][brand]['newly_added'] += 1
                print(f"  ADDED: {filepath.name}")

            else:
                stats['errors'] += 1
                print(f"  ERROR ({status}): {filepath.name}")

        print()

    # Print summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total articles processed: {stats['total']}")
    print(f"Already had capture (skipped): {stats['already_has']}")
    print(f"Newly added: {stats['newly_added']}")
    print(f"Errors: {stats['errors']}")
    print()

    print("BY BRAND:")
    for brand, brand_stats in stats['by_brand'].items():
        print(f"  {brand.upper()}: {brand_stats['newly_added']} added, {brand_stats['already_has']} already had, {brand_stats['total']} total")

    print()
    print("Email capture addition complete!")

if __name__ == '__main__':
    main()
