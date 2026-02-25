"""SEO Content Machine — Team 3 of 4 autonomous agent teams.

Runs Mon/Wed/Fri 8AM PST via seo-content-machine.yml GitHub Action.
Finds keyword gaps → writes pillar/cluster articles targeting those gaps
→ injects internal links across all existing articles.

As articles accumulate, organic traffic compounds. More traffic → more
affiliate clicks → more revenue. Goal: 45 articles → 150+ in 60 days.

Agents (run sequentially — each depends on previous output):
  1. gsc_researcher   — finds keyword gaps using existing article data + Claude
  2. article_writer   — generates 2 SEO articles per brand targeting those gaps
  3. internal_linker  — scans all articles, injects cross-links
"""

import os
import sys
import re
import json
import anthropic
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '.')
from database.supabase_client import get_supabase_client

BRANDS = ['fitness', 'deals', 'menopause']

BRAND_SITE_DIRS = {
    'fitness': 'outputs/fitover35-website',
    'deals': 'outputs/dailydealdarling-website',
    'menopause': 'outputs/menopause-planner-website',
}

BRAND_BASE_URLS = {
    'fitness': 'https://fitover35.com',
    'deals': 'https://dailydealdarling.com',
    'menopause': 'https://menopause-planner-website.vercel.app',
}

BRAND_NICHES = {
    'fitness': "men's fitness over 35, supplements, strength training, weight loss, testosterone",
    'deals': "budget home decor, kitchen gadgets, organization hacks, beauty deals, lifestyle",
    'menopause': "menopause symptoms, hot flashes, sleep problems, supplements, mood, weight gain",
}

# Per-brand Amazon Associate tags
BRAND_AMAZON_TAGS = {
    'fitness': 'fitover35-20',
    'deals': 'dailydealdarl-20',
    'menopause': 'menopauseplan-20',
}


def _get_anthropic_client():
    key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not key:
        raise ValueError('ANTHROPIC_API_KEY not set')
    return anthropic.Anthropic(api_key=key)


def _make_slug(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug[:60]


def _md_to_html(md_text: str, title: str, brand: str) -> str:
    """Minimal markdown-to-HTML converter for article content."""
    html_lines = []
    for line in md_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('# '):
            pass  # skip duplicate h1 (already in template)
        elif line.startswith('- '):
            html_lines.append(f'<li>{line[2:]}</li>')
        else:
            # Convert markdown links to HTML
            line = re.sub(
                r'\[([^\]]+)\]\(([^)]+)\)',
                r'<a href="\2" rel="nofollow sponsored" target="_blank">\1</a>',
                line
            )
            line = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', line)
            html_lines.append(f'<p>{line}</p>')

    return '\n'.join(html_lines)


# ─── Agent 1: GSC Researcher ──────────────────────────────────────────────────

def gsc_researcher_agent(db, client):
    """Identify keyword gaps for each brand using existing content + Claude analysis."""
    print('[gsc_researcher] Finding keyword gaps for all brands...')
    all_gaps = {}

    def _find_gaps_for_brand(brand):
        # Get existing article titles to prevent duplication
        try:
            existing = db.client.table('generated_articles').select(
                'article_title, slug'
            ).eq('brand', brand).execute()
            existing_titles = [
                a.get('article_title', '') or a.get('slug', '').replace('-', ' ')
                for a in (existing.data or [])
            ]
        except Exception:
            existing_titles = []

        prompt = f"""You are an SEO content strategist for a {BRAND_NICHES[brand]} website.

These articles already exist — do NOT suggest duplicates:
{json.dumps(existing_titles[:20], indent=2)}

Identify 5 article topics with HIGH buyer intent that:
1. Are NOT already covered above
2. Target long-tail keywords (3-5 words) people search when ready to buy
3. Can include Amazon affiliate product recommendations naturally
4. Are specific enough to rank in 60-90 days

Return JSON only:
{{
  "keyword_gaps": [
    {{
      "title": "exact H1 title for the article",
      "target_keyword": "3-5 word search phrase to optimize for",
      "search_intent": "buyer",
      "affiliate_angle": "specific products to recommend",
      "why_itll_rank": "brief reason (not too competitive, specific intent)"
    }}
  ]
}}"""

        try:
            response = client.messages.create(
                model='claude-sonnet-4-5',
                max_tokens=1000,
                messages=[{'role': 'user', 'content': prompt}]
            )
            text = response.content[0].text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            result = json.loads(text)
            gaps = result.get('keyword_gaps', [])
            print(f'  [gsc_researcher] {brand}: {len(gaps)} keyword gaps found')
            return brand, gaps
        except Exception as e:
            print(f'  [gsc_researcher] {brand} failed: {e}')
            return brand, []

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(_find_gaps_for_brand, b): b for b in BRANDS}
        for future in as_completed(futures):
            brand, gaps = future.result()
            all_gaps[brand] = gaps

    return all_gaps


# ─── Agent 2: Article Writer ──────────────────────────────────────────────────

def article_writer_agent(keyword_gaps, db, client):
    """Write 2 SEO articles per brand targeting the identified keyword gaps."""
    print('[article_writer] Writing SEO articles (parallel across brands)...')
    all_written = []
    all_written_lock = __import__('threading').Lock()

    def _write_for_brand(brand):
        gaps = keyword_gaps.get(brand, [])
        if not gaps:
            return []

        amazon_tag = BRAND_AMAZON_TAGS.get(brand, 'dailydealdarl-20')
        articles_dir = Path(BRAND_SITE_DIRS[brand]) / 'articles'
        articles_dir.mkdir(parents=True, exist_ok=True)
        brand_written = []

        for gap in gaps[:2]:  # Write top 2 per brand per run
            title = gap['title']
            slug = _make_slug(title)
            output_path = articles_dir / f'{slug}.html'

            if output_path.exists():
                print(f'  [article_writer] {brand}/{slug}: already exists, skipping')
                continue

            try:
                prompt = f"""Write a complete, helpful SEO article for a {BRAND_NICHES[brand]} website.

Title: {title}
Target keyword: {gap.get("target_keyword", title)}
Affiliate focus: {gap.get("affiliate_angle", "relevant products")}
Amazon tag: {amazon_tag}

Requirements:
- 850-1000 words, markdown format
- H2 subheadings every 200 words for structure
- Include 2-3 Amazon product recommendations using this exact format:
  [Product Name](https://www.amazon.com/s?k=PRODUCT+KEYWORDS&tag={amazon_tag})
- Conversational, helpful tone — written by a real person, not a robot
- End with a clear next step CTA
- Start with FTC disclosure: *This article contains affiliate links.*

Write the full article now:"""

                response = client.messages.create(
                    model='claude-sonnet-4-5',
                    max_tokens=2000,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                article_md = response.content[0].text.strip()
                article_body = _md_to_html(article_md, title, brand)
                base_url = BRAND_BASE_URLS[brand]

                html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{gap.get('target_keyword', title)} — tips and recommendations">
<link rel="stylesheet" href="../styles.css">
</head>
<body>
<article class="blog-post">
<h1>{title}</h1>
<p class="affiliate-disclosure"><em>This article contains affiliate links. If you purchase through these links, we may earn a small commission at no extra cost to you.</em></p>
{article_body}
</article>
</body>
</html>"""

                output_path.write_text(html, encoding='utf-8')
                entry = {'brand': brand, 'slug': slug, 'title': title}
                brand_written.append(entry)
                print(f'  [article_writer] {brand}/{slug}: {len(html)} bytes written')

                # Log to generated_articles table
                try:
                    db.client.table('generated_articles').insert({
                        'brand': brand,
                        'slug': slug,
                        'article_title': title,
                        'article_url': f'{base_url}/articles/{slug}.html',
                        'has_affiliate_links': True,
                        'word_count': len(article_md.split()),
                        'source': 'seo_content_machine',
                        'created_at': datetime.now(timezone.utc).isoformat()
                    }).execute()
                except Exception as e:
                    print(f'  [article_writer] DB log failed {brand}/{slug}: {e}')

            except Exception as e:
                print(f'  [article_writer] Failed {brand}/{slug}: {e}')

        return brand_written

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(_write_for_brand, b): b for b in BRANDS}
        for future in as_completed(futures):
            brand_written = future.result()
            with all_written_lock:
                all_written.extend(brand_written)

    print(f'  [article_writer] Total articles written this run: {len(all_written)}')
    return all_written


# ─── Agent 3: Internal Linker ─────────────────────────────────────────────────

def internal_linker_agent():
    """Scan all articles across all brands and inject internal links."""
    print('[internal_linker] Injecting internal links across articles...')
    total_links = 0

    for brand in BRANDS:
        articles_dir = Path(BRAND_SITE_DIRS[brand]) / 'articles'
        if not articles_dir.exists():
            continue

        html_files = list(articles_dir.glob('*.html'))
        if len(html_files) < 2:
            print(f'  [internal_linker] {brand}: fewer than 2 articles, skipping')
            continue

        # Build slug → title map
        slug_title_map = {}
        for f in html_files:
            try:
                content = f.read_text(encoding='utf-8')
                m = re.search(r'<title>([^<]+)</title>', content)
                slug_title_map[f.stem] = m.group(1) if m else f.stem.replace('-', ' ').title()
            except Exception:
                pass

        base_url = BRAND_BASE_URLS[brand]
        brand_links = 0

        for html_file in html_files:
            try:
                content = html_file.read_text(encoding='utf-8')
                original = content

                for target_slug, target_title in slug_title_map.items():
                    if target_slug == html_file.stem:
                        continue  # don't link to self

                    target_url = f'{base_url}/articles/{target_slug}.html'
                    if target_url in content:
                        continue  # already linked

                    # Match first 2-3 words of target title in paragraph text
                    words = target_title.split()[:3]
                    phrase = ' '.join(words)
                    pattern = re.compile(
                        rf'(<p>[^<]*)({re.escape(phrase)})([^<]*</p>)',
                        re.IGNORECASE
                    )
                    replacement = (
                        rf'\1<a href="{target_url}" title="{target_title}">\2</a>\3'
                    )
                    new_content, n = re.subn(pattern, replacement, content, count=1)
                    if n > 0:
                        content = new_content
                        brand_links += 1

                if content != original:
                    html_file.write_text(content, encoding='utf-8')

            except Exception as e:
                print(f'  [internal_linker] Error in {html_file.name}: {e}')

        print(
            f'  [internal_linker] {brand}: {brand_links} links added '
            f'across {len(html_files)} articles'
        )
        total_links += brand_links

    return total_links


# ─── Coordinator ─────────────────────────────────────────────────────────────

def run_seo_content_machine():
    print('=== SEO Content Machine starting ===')
    print(f'Timestamp: {datetime.now(timezone.utc).isoformat()}')

    db = get_supabase_client()
    client = _get_anthropic_client()

    # Step 1: Find keyword gaps (parallel by brand)
    keyword_gaps = gsc_researcher_agent(db, client)

    # Step 2: Write articles (parallel by brand)
    written_articles = article_writer_agent(keyword_gaps, db, client)

    # Step 3: Inject internal links across ALL articles
    links_added = internal_linker_agent()

    # Update agent_runs
    try:
        db.client.table('agent_runs').upsert({
            'agent_name': 'seo_content_machine',
            'last_run_at': datetime.now(timezone.utc).isoformat(),
            'status': 'success',
            'updated_at': datetime.now(timezone.utc).isoformat()
        }, on_conflict='agent_name').execute()
    except Exception:
        pass

    print('\n=== SEO Content Machine Summary ===')
    print(f'  Articles written this run: {len(written_articles)}')
    for a in written_articles:
        print(f'    {a["brand"]}: {a["title"]}')
    print(f'  Internal links added: {links_added}')
    print('=== Done ===')

    return written_articles


if __name__ == '__main__':
    run_seo_content_machine()
