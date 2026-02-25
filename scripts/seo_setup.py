#!/usr/bin/env python3
"""
SEO Setup Script - Add GA, sitemaps, robots.txt, and OG tags to brand websites
"""

import os
import re
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

# Configuration
SITES = {
    'fitover35': {
        'base_dir': '/Users/homefolder/Desktop/social-media-empire/outputs/fitover35-website',
        'base_url': 'https://www.fitover35.com',
        'ga_id': 'G-1FC6FH34L9',
        'og_site_name': 'FitOver35',
    },
    'dailydealdarling': {
        'base_dir': '/Users/homefolder/Desktop/social-media-empire/outputs/dailydealdarling-website',
        'base_url': 'https://www.dailydealdarling.com',
        'ga_id': 'G-1FC6FH34L9',
        'og_site_name': 'Daily Deal Darling',
    }
}

GA_SNIPPET = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{ga_id}');
</script>'''

def ensure_ga_in_file(file_path, ga_id, site_name):
    """Add GA snippet to file if not already present"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if GA already present with this ID
    if ga_id in content:
        return False

    # Don't add if different GA ID is already there
    if 'googletagmanager.com/gtag/js' in content:
        return False

    # Find </head> tag
    head_close = content.find('</head>')
    if head_close == -1:
        print(f"  ERROR: No </head> found in {file_path}")
        return False

    # Insert GA snippet before </head>
    ga_snippet = GA_SNIPPET.format(ga_id=ga_id)
    new_content = content[:head_close] + ga_snippet + '\n  ' + content[head_close:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True

def get_page_title_and_desc(file_path):
    """Extract title and description from HTML file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
    title = title_match.group(1) if title_match else None

    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
    description = desc_match.group(1) if desc_match else None

    return title, description

def add_og_tags_to_article(file_path, base_url, url_path, og_site_name):
    """Add missing OG tags to article"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if OG tags already exist
    if re.search(r'property=["\']og:title["\']\s+content=["\']', content, re.IGNORECASE):
        return False

    title, description = get_page_title_and_desc(file_path)
    if not title or not description:
        return False

    # Build OG meta tags
    og_tags = f'''  <meta property="og:type" content="article">
  <meta property="og:site_name" content="{og_site_name}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{base_url}{url_path}">
'''

    # Insert after existing meta tags (before </head>)
    head_close = content.find('</head>')
    if head_close == -1:
        return False

    new_content = content[:head_close] + og_tags + content[head_close:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True

def create_sitemap(site_config):
    """Create sitemap.xml"""
    base_dir = site_config['base_dir']
    base_url = site_config['base_url']

    urls = []

    # Find all HTML files
    html_files = sorted(Path(base_dir).rglob('*.html'))

    for html_file in html_files:
        # Skip 404 pages
        if '404' in html_file.name:
            continue

        rel_path = html_file.relative_to(base_dir)

        # Convert to URL
        if rel_path.name == 'index.html':
            url = base_url + '/'
            priority = '1.0'
        else:
            # Remove .html extension
            url_path = str(rel_path).replace('\\', '/').replace('.html', '')
            url = base_url + '/' + url_path
            if 'articles' in url_path:
                priority = '0.8'
            else:
                priority = '0.6'

        urls.append({
            'loc': url,
            'priority': priority,
            'lastmod': datetime.now().strftime('%Y-%m-%d')
        })

    # Generate XML
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''

    for url_data in urls:
        xml += f'''  <url>
    <loc>{url_data['loc']}</loc>
    <lastmod>{url_data['lastmod']}</lastmod>
    <priority>{url_data['priority']}</priority>
  </url>
'''

    xml += '</urlset>'

    sitemap_path = os.path.join(base_dir, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(xml)

    return len(urls)

def create_robots_txt(site_config):
    """Create robots.txt"""
    base_dir = site_config['base_dir']
    base_url = site_config['base_url']

    robots_txt = f'''User-agent: *
Allow: /
Sitemap: {base_url}/sitemap.xml
'''

    robots_path = os.path.join(base_dir, 'robots.txt')
    with open(robots_path, 'w', encoding='utf-8') as f:
        f.write(robots_txt)

def process_site(site_name, site_config):
    """Process a single site"""
    print(f"\n{'='*60}")
    print(f"Processing: {site_name}")
    print(f"{'='*60}")

    base_dir = site_config['base_dir']
    base_url = site_config['base_url']
    ga_id = site_config['ga_id']
    og_site_name = site_config['og_site_name']

    if not os.path.exists(base_dir):
        print(f"ERROR: Directory not found: {base_dir}")
        return

    # Task 1: Add Google Analytics
    print(f"\n1. Adding Google Analytics ({ga_id})...")
    ga_count = 0
    html_files = sorted(Path(base_dir).rglob('*.html'))
    for html_file in html_files:
        if ensure_ga_in_file(str(html_file), ga_id, site_name):
            ga_count += 1
            print(f"   ✓ {html_file.relative_to(base_dir)}")
    print(f"   Total GA added: {ga_count}")

    # Task 2: Add OG tags to articles
    print(f"\n2. Adding OG tags to articles...")
    og_count = 0
    articles_dir = os.path.join(base_dir, 'articles')
    if os.path.exists(articles_dir):
        article_files = sorted(Path(articles_dir).glob('*.html'))
        for article_file in article_files:
            rel_path = article_file.relative_to(base_dir)
            url_path = '/' + str(rel_path).replace('\\', '/').replace('.html', '')
            if add_og_tags_to_article(str(article_file), base_url, url_path, og_site_name):
                og_count += 1
                print(f"   ✓ {rel_path}")
    print(f"   Total OG tags added: {og_count}")

    # Task 3: Create sitemap.xml
    print(f"\n3. Creating sitemap.xml...")
    sitemap_count = create_sitemap(site_config)
    print(f"   ✓ Created with {sitemap_count} URLs")

    # Task 4: Create robots.txt
    print(f"\n4. Creating robots.txt...")
    create_robots_txt(site_config)
    print(f"   ✓ Created")

    return {
        'ga_added': ga_count,
        'og_added': og_count,
        'sitemap_urls': sitemap_count,
    }

def check_verification_tags():
    """Check for google-site-verification tags"""
    print(f"\n{'='*60}")
    print("Checking google-site-verification tags")
    print(f"{'='*60}")

    for site_name, site_config in SITES.items():
        base_dir = site_config['base_dir']
        print(f"\n{site_name}:")

        found = []
        html_files = sorted(Path(base_dir).rglob('*.html'))
        for html_file in html_files:
            with open(str(html_file), 'r', encoding='utf-8') as f:
                if 'google-site-verification' in f.read():
                    found.append(html_file.relative_to(base_dir))

        if found:
            for file in found:
                print(f"   ✓ Found in: {file}")
        else:
            print(f"   ✗ None found")

def check_amazon_links():
    """Check all Amazon links"""
    print(f"\n{'='*60}")
    print("Checking Amazon affiliate links")
    print(f"{'='*60}")

    amazon_links = {}

    for site_name, site_config in SITES.items():
        base_dir = site_config['base_dir']
        print(f"\n{site_name}:")

        site_links = []
        html_files = sorted(Path(base_dir).rglob('*.html'))
        for html_file in html_files:
            with open(str(html_file), 'r', encoding='utf-8') as f:
                content = f.read()
                # Find all amazon.com links
                matches = re.findall(r'href=["\']([^"\']*amazon\.com[^"\']*)["\']', content)
                for match in matches:
                    site_links.append({
                        'file': html_file.relative_to(base_dir),
                        'url': match
                    })

        if site_links:
            for link_info in site_links:
                print(f"   {link_info['file']}")
                print(f"      {link_info['url']}")
        else:
            print(f"   No Amazon links found")

        amazon_links[site_name] = site_links

    return amazon_links

if __name__ == '__main__':
    results = {}

    # Process each site
    for site_name, site_config in SITES.items():
        results[site_name] = process_site(site_name, site_config)

    # Check verification and affiliate links
    check_verification_tags()
    amazon_links = check_amazon_links()

    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for site_name, stats in results.items():
        print(f"\n{site_name}:")
        print(f"  GA added to: {stats['ga_added']} files")
        print(f"  OG tags added: {stats['og_added']} files")
        print(f"  Sitemap URLs: {stats['sitemap_urls']}")
