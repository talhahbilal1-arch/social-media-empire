#!/usr/bin/env python3
"""
Batch SEO fixes across all 3 brand sites:
  Task 1: Add related article links to articles missing them
  Task 2: Fix DDD canonical URLs (bare domain → www)
  Task 3: Regenerate FitOver35 sitemap
  Task 4: Add Pinterest Pin-It button to all articles
"""

import os
import re
import glob
from datetime import datetime
from collections import defaultdict

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")

BRANDS = {
    "fitness": {
        "dir": os.path.join(BASE, "fitover35-website", "articles"),
        "section_header": "Keep reading",
        "template": (
            '\n<div style="margin-top:36px;padding-top:24px;border-top:1px solid #222">\n'
            '<h3 style="font-family:\'Space Grotesk\',sans-serif;font-size:1rem;color:#fff;margin-bottom:12px">Keep reading</h3>\n'
            '{links}'
            '</div>\n'
        ),
        "link_template": '<a href="{filename}" style="display:block;color:#E8C547;text-decoration:none;font-size:.88rem;margin-bottom:8px">{title}</a>\n',
    },
    "deals": {
        "dir": os.path.join(BASE, "dailydealdarling-website", "articles"),
        "section_header": "You might also like",
        "template": (
            '\n<div style="margin-top:36px;padding-top:24px;border-top:1px solid #EBEBEB">\n'
            '<h3 style="font-family:\'Lora\',serif;font-size:1rem;margin-bottom:12px">You might also like</h3>\n'
            '{links}'
            '</div>\n'
        ),
        "link_template": '<a href="{filename}" style="display:block;color:#C47D8E;text-decoration:none;font-size:.88rem;margin-bottom:8px">{title}</a>\n',
    },
    "menopause": {
        "dir": os.path.join(BASE, "menopause-planner-website", "articles"),
        "section_header": "More from The Menopause Planner",
        "template": (
            '\n<div style="margin-top:36px;padding-top:24px;border-top:1px solid #E8E0D8">\n'
            '<h3 style="font-family:\'DM Serif Display\',serif;font-size:1rem;color:#3D3D3D;margin-bottom:12px">More from The Menopause Planner</h3>\n'
            '{links}'
            '</div>\n'
        ),
        "link_template": '<a href="{filename}" style="display:block;color:#6B705C;text-decoration:none;font-size:.88rem;margin-bottom:8px">{title}</a>\n',
    },
}

RELATED_PATTERNS = re.compile(
    r'Related Articles|Keep reading|You might also like|More from The Menopause Planner',
    re.IGNORECASE
)

PINTEREST_JS = '<script async defer src="https://assets.pinterest.com/js/pinit.js"></script>'
PINTEREST_PATTERN = re.compile(r'pinit\.js|pinterest\.com/js', re.IGNORECASE)


def extract_title(filepath):
    """Extract title from <title> or <h1> tag."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(5000)  # Title is always near top
        # Try <title> first
        m = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if m:
            title = m.group(1).strip()
            # Remove brand suffix like " — FitOver35" or " | Daily Deal Darling"
            title = re.split(r'\s*[—|]\s*(?:FitOver35|Fit Over 35|Daily Deal Darling|The Menopause Planner|Menopause Planner)', title)[0].strip()
            if title:
                return title
        # Fallback to <h1>
        m = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
        if m:
            return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    except Exception:
        pass
    # Fallback: humanize filename
    name = os.path.splitext(os.path.basename(filepath))[0]
    return name.replace('-', ' ').title()


def get_keywords(filename):
    """Extract meaningful keywords from filename for matching."""
    name = os.path.splitext(filename)[0]
    words = set(name.split('-'))
    # Remove very common/short words
    stop = {'the', 'a', 'an', 'and', 'or', 'for', 'to', 'of', 'in', 'on', 'at',
            'is', 'it', 'that', 'this', 'with', 'your', 'how', 'what', 'why',
            'best', 'top', 'over', 'from', 'after', 'men', 'you', 'can', 'do',
            'does', 'are', 'be', 'its', 'not', 'but', 'all', 'my', 'we', 'our',
            'vs', 'about', '35', '2026', 'actually', 'i'}
    return words - stop


def find_related(target_file, all_files, n=3):
    """Find n most related articles by keyword overlap."""
    target_name = os.path.basename(target_file)
    target_kw = get_keywords(target_name)
    if not target_kw:
        # Just pick first n different files
        others = [f for f in all_files if os.path.basename(f) != target_name]
        return others[:n]

    scored = []
    for f in all_files:
        fname = os.path.basename(f)
        if fname == target_name or fname == 'index.html':
            continue
        kw = get_keywords(fname)
        overlap = len(target_kw & kw)
        if overlap > 0:
            scored.append((overlap, f))

    scored.sort(key=lambda x: -x[0])
    results = [f for _, f in scored[:n]]

    # If we don't have enough, fill with random others
    if len(results) < n:
        used = {os.path.basename(r) for r in results}
        used.add(target_name)
        used.add('index.html')
        for f in all_files:
            if os.path.basename(f) not in used:
                results.append(f)
                if len(results) >= n:
                    break

    return results[:n]


def has_related_section(content):
    """Check if article already has a related section."""
    return bool(RELATED_PATTERNS.search(content))


def has_pinterest_js(content):
    """Check if article already has Pinterest JS."""
    return bool(PINTEREST_PATTERN.search(content))


def insert_before_closing_tag(content, insertion):
    """Insert HTML before </article>, </main>, or </body>."""
    # Try </article> first
    for tag in ['</article>', '</main>', '</body>']:
        idx = content.rfind(tag)
        if idx != -1:
            return content[:idx] + insertion + content[idx:]
    # Fallback: append before end
    return content + insertion


def insert_pinterest_js(content):
    """Insert Pinterest JS before </body>."""
    idx = content.rfind('</body>')
    if idx != -1:
        return content[:idx] + PINTEREST_JS + '\n' + content[idx:]
    return content + '\n' + PINTEREST_JS


# ============================================================
# TASK 1: Add related article links
# ============================================================
def task1_add_related_links():
    print("=" * 60)
    print("TASK 1: Adding related article links")
    print("=" * 60)

    stats = {}
    for brand_key, config in BRANDS.items():
        articles_dir = config["dir"]
        if not os.path.isdir(articles_dir):
            print(f"  SKIP {brand_key}: directory not found")
            continue

        all_files = sorted(glob.glob(os.path.join(articles_dir, "*.html")))
        # Pre-cache titles
        titles = {}
        for f in all_files:
            titles[f] = extract_title(f)

        added = 0
        skipped = 0
        for filepath in all_files:
            if os.path.basename(filepath) == 'index.html':
                skipped += 1
                continue

            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            if has_related_section(content):
                skipped += 1
                continue

            # Find 3 related articles
            related = find_related(filepath, all_files, n=3)
            if not related:
                skipped += 1
                continue

            # Build links HTML
            links_html = ""
            for rel_file in related:
                links_html += config["link_template"].format(
                    filename=os.path.basename(rel_file),
                    title=titles.get(rel_file, os.path.basename(rel_file))
                )

            section_html = config["template"].format(links=links_html)
            new_content = insert_before_closing_tag(content, section_html)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            added += 1

        stats[brand_key] = {"added": added, "skipped": skipped, "total": len(all_files)}
        print(f"  {brand_key}: {added} articles updated, {skipped} skipped (already had related or index)")

    return stats


# ============================================================
# TASK 2: Fix DDD canonical URLs
# ============================================================
def task2_fix_ddd_canonicals():
    print("\n" + "=" * 60)
    print("TASK 2: Fixing DDD canonical URLs (bare domain → www)")
    print("=" * 60)

    ddd_dir = os.path.join(BASE, "dailydealdarling-website")
    all_html = glob.glob(os.path.join(ddd_dir, "**", "*.html"), recursive=True)

    fixed_files = 0
    total_replacements = 0

    for filepath in sorted(all_html):
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Replace bare domain with www (but not if already www)
        # Match https://dailydealdarling.com NOT preceded by www.
        new_content = re.sub(
            r'https://(?!www\.)dailydealdarling\.com',
            'https://www.dailydealdarling.com',
            content
        )

        if new_content != content:
            count = content.count('https://dailydealdarling.com') - content.count('https://www.dailydealdarling.com')
            total_replacements += count
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            fixed_files += 1

    print(f"  Fixed {fixed_files} files, {total_replacements} URL replacements")
    return {"files_fixed": fixed_files, "replacements": total_replacements}


# ============================================================
# TASK 3: Regenerate FitOver35 sitemap
# ============================================================
def task3_regenerate_sitemap():
    print("\n" + "=" * 60)
    print("TASK 3: Regenerating FitOver35 sitemap")
    print("=" * 60)

    fo35_dir = os.path.join(BASE, "fitover35-website")
    sitemap_path = os.path.join(fo35_dir, "sitemap.xml")

    # Read existing sitemap to preserve non-article URLs and format
    existing_urls = set()
    static_entries = []
    if os.path.exists(sitemap_path):
        with open(sitemap_path, 'r', encoding='utf-8') as f:
            sitemap_content = f.read()
        # Extract existing non-article URLs to preserve them
        for m in re.finditer(r'<url>\s*<loc>(.*?)</loc>.*?</url>', sitemap_content, re.DOTALL):
            url = m.group(1)
            if '/articles/' not in url:
                static_entries.append(m.group(0))
            existing_urls.add(url)

    # Get all articles
    articles_dir = os.path.join(fo35_dir, "articles")
    articles = sorted(glob.glob(os.path.join(articles_dir, "*.html")))
    today = datetime.now().strftime("%Y-%m-%d")

    # Build sitemap
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    # Add static entries first
    for entry in static_entries:
        lines.append(f"  {entry.strip()}")

    # Add all articles
    article_count = 0
    for filepath in articles:
        filename = os.path.basename(filepath)
        url = f"https://fitover35.com/articles/{filename}"
        # Try to get date from file
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(3000)
            date_match = re.search(r'"datePublished":\s*"(\d{4}-\d{2}-\d{2})"', content)
            if date_match:
                lastmod = date_match.group(1)
            else:
                lastmod = today
        except Exception:
            lastmod = today

        lines.append(f'  <url>')
        lines.append(f'    <loc>{url}</loc>')
        lines.append(f'    <lastmod>{lastmod}</lastmod>')
        lines.append(f'    <changefreq>monthly</changefreq>')
        lines.append(f'    <priority>0.7</priority>')
        lines.append(f'  </url>')
        article_count += 1

    lines.append('</urlset>')

    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    total_urls = len(static_entries) + article_count
    print(f"  Sitemap regenerated: {total_urls} total URLs ({len(static_entries)} static + {article_count} articles)")
    return {"total_urls": total_urls, "articles": article_count, "static": len(static_entries)}


# ============================================================
# TASK 4: Add Pinterest Pin-It button
# ============================================================
def task4_add_pinterest():
    print("\n" + "=" * 60)
    print("TASK 4: Adding Pinterest Pin-It button to all articles")
    print("=" * 60)

    stats = {}
    for brand_key, config in BRANDS.items():
        articles_dir = config["dir"]
        if not os.path.isdir(articles_dir):
            continue

        all_files = sorted(glob.glob(os.path.join(articles_dir, "*.html")))
        added = 0
        skipped = 0

        for filepath in all_files:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            if has_pinterest_js(content):
                skipped += 1
                continue

            new_content = insert_pinterest_js(content)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            added += 1

        stats[brand_key] = {"added": added, "skipped": skipped}
        print(f"  {brand_key}: {added} articles updated, {skipped} already had Pinterest JS")

    return stats


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("SEO Batch Fix Script")
    print(f"Running at {datetime.now().isoformat()}")
    print(f"Base directory: {BASE}\n")

    t1 = task1_add_related_links()
    t2 = task2_fix_ddd_canonicals()
    t3 = task3_regenerate_sitemap()
    t4 = task4_add_pinterest()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nTask 1 - Related Links:")
    for brand, s in t1.items():
        print(f"  {brand}: {s['added']}/{s['total']} articles updated")
    print(f"\nTask 2 - DDD Canonical Fix:")
    print(f"  {t2['files_fixed']} files fixed, {t2['replacements']} URLs corrected")
    print(f"\nTask 3 - FitOver35 Sitemap:")
    print(f"  {t3['total_urls']} URLs ({t3['static']} static + {t3['articles']} articles)")
    print(f"\nTask 4 - Pinterest Pin-It:")
    for brand, s in t4.items():
        print(f"  {brand}: {s['added']} articles updated, {s['skipped']} already had it")
    print("\nDone!")
