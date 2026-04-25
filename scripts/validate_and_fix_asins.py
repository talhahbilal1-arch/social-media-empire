#!/usr/bin/env python3
"""Validate all Amazon ASINs in the product database and find replacements for broken ones.

Run this as a scheduled maintenance task or before article generation.
Updates pin_article_generator.py with working ASINs.
"""
import os, sys, re, json, time, requests

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from video_automation.pin_article_generator import AMAZON_AFFILIATE_LINKS, BRAND_AFFILIATE_TAGS

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9',
}

def check_asin(url, timeout=10):
    """Check if an Amazon ASIN URL is valid. Returns (ok, status_code, final_url)."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        final = resp.url
        # Check for soft 404s (Amazon search redirect, dog page)
        if resp.status_code >= 400:
            return False, resp.status_code, final
        if '/s?k=' in final or '/gp/search/' in final:
            return False, 'search_redirect', final
        if 'Sorry, we just need to make sure' in resp.text[:2000]:
            return None, 'captcha', final  # Can't verify, don't mark as broken
        return True, resp.status_code, final
    except requests.RequestException as e:
        return None, str(e)[:50], ''

def find_replacement_asin(product_name, tag):
    """Search Amazon for a replacement product and return a working ASIN URL."""
    search_url = f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}&tag={tag}"
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=15)
        # Extract first ASIN from search results
        asins = re.findall(r'/dp/([A-Z0-9]{10})', resp.text)
        if asins:
            new_url = f"https://www.amazon.com/dp/{asins[0]}?tag={tag}"
            # Verify the new ASIN works
            ok, status, _ = check_asin(new_url)
            if ok:
                return new_url, asins[0]
    except Exception:
        pass
    return None, None

def main():
    broken = []
    working = 0
    captcha = 0

    print("Validating all Amazon ASINs...\n")

    for brand, links in AMAZON_AFFILIATE_LINKS.items():
        tag = BRAND_AFFILIATE_TAGS.get(brand, 'dailydealdarl-20')
        for key, url in links.items():
            if key == '_default':
                continue
            ok, status, final = check_asin(url)
            if ok is None:
                captcha += 1
                print(f"  ? [{brand}] {key}: captcha/timeout — skipping")
            elif ok:
                working += 1
            else:
                broken.append({'brand': brand, 'key': key, 'url': url, 'status': status, 'tag': tag})
                print(f"  ✗ [{brand}] {key}: HTTP {status}")
            time.sleep(0.5)  # Rate limit

    print(f"\n{'='*60}")
    print(f"Working: {working} | Broken: {len(broken)} | Captcha/Skip: {captcha}")
    print(f"{'='*60}\n")

    if not broken:
        print("All ASINs valid!")
        return

    # Find replacements
    print("Searching for replacements...\n")
    replacements = {}
    for item in broken:
        new_url, new_asin = find_replacement_asin(item['key'], item['tag'])
        if new_url:
            replacements[f"{item['brand']}:{item['key']}"] = {
                'old_url': item['url'],
                'new_url': new_url,
                'new_asin': new_asin,
            }
            print(f"  ✓ [{item['brand']}] {item['key']}: {item['url'][-20:]} → /dp/{new_asin}")
        else:
            print(f"  ✗ [{item['brand']}] {item['key']}: no replacement found")
        time.sleep(1)

    # Apply replacements to pin_article_generator.py
    if replacements:
        gen_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'video_automation', 'pin_article_generator.py')
        with open(gen_path, 'r') as f:
            content = f.read()
        
        fixed = 0
        for key, rep in replacements.items():
            old_url = rep['old_url']
            new_url = rep['new_url']
            if old_url in content:
                content = content.replace(old_url, new_url)
                fixed += 1
        
        with open(gen_path, 'w') as f:
            f.write(content)
        
        print(f"\n{'='*60}")
        print(f"Updated {fixed} ASINs in pin_article_generator.py")
        print(f"{'='*60}")

        # Also fix any existing articles that use the old ASINs
        article_dirs = [
            'outputs/fitover35-website/articles',
            'outputs/dailydealdarling-website/articles',
            'outputs/menopause-planner-website/articles',
        ]
        articles_fixed = 0
        for d in article_dirs:
            if not os.path.exists(d):
                continue
            for fname in os.listdir(d):
                if not fname.endswith('.html'):
                    continue
                fpath = os.path.join(d, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    html = f.read()
                changed = False
                for key, rep in replacements.items():
                    if rep['old_url'] in html:
                        html = html.replace(rep['old_url'], rep['new_url'])
                        changed = True
                if changed:
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(html)
                    articles_fixed += 1
        
        print(f"Fixed {articles_fixed} existing article files")

    # Save report
    report = {
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'working': working,
        'broken': len(broken),
        'replacements_found': len(replacements),
        'details': broken,
    }
    report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'asin_validation.json')
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to {report_path}")

if __name__ == '__main__':
    main()
