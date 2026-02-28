#!/usr/bin/env python3
"""
Weekly Menopause Newsletter — auto-generates from existing articles.

Picks the next unsent article, extracts content, generates a newsletter
email via Claude, and sends as a ConvertKit broadcast.

Runs every Wednesday 10 AM PST via GitHub Actions.
"""
import os
import re
import sys
import json
import glob
import logging
import hashlib
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Optional

import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────
CONVERTKIT_API_KEY = os.environ.get('CONVERTKIT_API_KEY', '')
CONVERTKIT_API_SECRET = os.environ.get('CONVERTKIT_API_SECRET', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

CK_BASE = 'https://api.convertkit.com/v3'
ARTICLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'outputs', 'menopause-planner-website', 'articles')
SITE_URL = 'https://menopause-planner-website.vercel.app'
TRACKER_PDF = f'{SITE_URL}/menopause-symptom-tracker.pdf'
ETSY_URL = 'https://www.etsy.com/listing/4435219468/menopause-wellness-planner-bundle'


# ── Article Parser ────────────────────────────────
class ArticleExtractor(HTMLParser):
    """Extract title, description, and body text from article HTML."""

    def __init__(self):
        super().__init__()
        self._in_tag = None
        self._in_article = False
        self._depth = 0
        self.title = ''
        self.description = ''
        self.headings = []
        self.paragraphs = []
        self.date = ''
        self.url = ''

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'meta':
            name = attrs_dict.get('name', '')
            prop = attrs_dict.get('property', '')
            content = attrs_dict.get('content', '')
            if name == 'description':
                self.description = content
            if prop == 'og:url':
                self.url = content
        if tag == 'article':
            self._in_article = True
        if self._in_article:
            if tag == 'h1':
                self._in_tag = 'h1'
            elif tag == 'h2':
                self._in_tag = 'h2'
            elif tag == 'p':
                self._in_tag = 'p'

    def handle_endtag(self, tag):
        if tag in ('h1', 'h2', 'p'):
            self._in_tag = None
        if tag == 'article':
            self._in_article = False

    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        if self._in_tag == 'h1' and not self.title:
            self.title = text
        elif self._in_tag == 'h2':
            self.headings.append(text)
        elif self._in_tag == 'p':
            if 'article-meta' not in str(self._in_tag):
                self.paragraphs.append(text)
            # Check if it's a date
            if re.match(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d', text):
                self.date = text


def extract_article(filepath):
    """Parse an article HTML file and return structured content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    parser = ArticleExtractor()
    parser.feed(html)

    # Build article URL from filename
    filename = os.path.basename(filepath)
    article_url = f"{SITE_URL}/articles/{filename}"
    if parser.url:
        article_url = parser.url

    # Get first 3-4 paragraphs as preview (skip very short ones)
    body_preview = []
    for p in parser.paragraphs:
        if len(p) > 40:
            body_preview.append(p)
        if len(body_preview) >= 4:
            break

    return {
        'title': parser.title,
        'description': parser.description,
        'url': article_url,
        'date': parser.date,
        'headings': parser.headings[:5],
        'preview': '\n\n'.join(body_preview),
        'filename': filename,
        'file_hash': hashlib.md5(filepath.encode()).hexdigest()[:12],
    }


# ── Sent Tracking (Supabase) ─────────────────────
def get_sent_articles():
    """Get list of article filenames already sent as newsletters."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("No Supabase credentials — using empty sent list")
        return set()

    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/newsletter_sends?select=article_filename&brand=eq.menopause",
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
            },
            timeout=15
        )
        if resp.status_code == 200:
            return {r['article_filename'] for r in resp.json()}
        # Table might not exist yet — that's OK
        logger.warning(f"Supabase returned {resp.status_code} for newsletter_sends")
        return set()
    except Exception as e:
        logger.warning(f"Could not fetch sent articles: {e}")
        return set()


def record_sent_article(filename, subject, broadcast_id):
    """Record that an article was sent as a newsletter."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return

    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/newsletter_sends",
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal',
            },
            json={
                'brand': 'menopause',
                'article_filename': filename,
                'subject': subject,
                'broadcast_id': str(broadcast_id) if broadcast_id else None,
                'sent_at': datetime.now(timezone.utc).isoformat(),
            },
            timeout=15
        )
    except Exception as e:
        logger.warning(f"Could not record sent article: {e}")


# ── Pick Next Article ─────────────────────────────
def pick_next_article():
    """Select the next article to send as a newsletter."""
    sent = get_sent_articles()

    # Get all HTML articles, sorted by modification time (oldest first)
    pattern = os.path.join(ARTICLES_DIR, '*.html')
    files = sorted(glob.glob(pattern), key=os.path.getmtime)

    if not files:
        logger.error(f"No articles found in {ARTICLES_DIR}")
        return None

    # Skip already-sent articles and .md files
    for filepath in files:
        filename = os.path.basename(filepath)
        if filename not in sent:
            article = extract_article(filepath)
            if article['title']:
                logger.info(f"Selected article: {article['title']}")
                return article

    # All articles sent — loop back to oldest
    logger.info("All articles sent — cycling back to oldest")
    article = extract_article(files[0])
    return article


# ── Generate Newsletter via Claude ────────────────
def generate_newsletter_email(article):
    """Use Claude to generate a warm, engaging newsletter email from article content."""
    if not ANTHROPIC_API_KEY:
        logger.warning("No ANTHROPIC_API_KEY — using template fallback")
        return generate_template_fallback(article)

    prompt = f"""Write a warm, conversational newsletter email for "The Menopause Planner" weekly newsletter.

This email should feel like a knowledgeable friend sharing something helpful, not a corporate blast.

Article to feature:
- Title: {article['title']}
- Description: {article['description']}
- Key sections: {', '.join(article['headings'])}
- Preview: {article['preview'][:800]}
- URL: {article['url']}

Requirements:
1. Subject line: engaging, under 60 chars, no clickbait. Include a number or specific detail.
2. Preview text: 1 sentence teaser for inbox preview (under 100 chars).
3. Email body in HTML (inline styles only, max-width 600px):
   - Personal greeting using {{{{ subscriber.first_name | default: "friend" }}}}
   - 2-3 paragraph teaser that hooks the reader with the most interesting insight
   - "Read the full article" CTA button (sage green #7c9a82, white text, rounded)
   - A quick actionable tip they can use today (not from the article — bonus value)
   - Soft mention of the free Symptom Tracker: {TRACKER_PDF}
   - Sign-off from "The Menopause Planner Team"
4. Tone: warm, empathetic, evidence-informed, never preachy
5. Do NOT include unsubscribe links (ConvertKit adds those automatically)

Return JSON only:
{{"subject": "...", "preview_text": "...", "html": "..."}}"""

    try:
        resp = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': 'claude-sonnet-4-5-20241022',
                'max_tokens': 2000,
                'messages': [{'role': 'user', 'content': prompt}],
            },
            timeout=60
        )
        resp.raise_for_status()
        content = resp.json()['content'][0]['text']

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json.loads(json_match.group())

        logger.warning("Could not parse Claude response as JSON")
        return generate_template_fallback(article)

    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return generate_template_fallback(article)


def generate_template_fallback(article):
    """Fallback template when Claude API is unavailable."""
    subject = f"This week: {article['title'][:50]}"
    preview = article['description'][:95] if article['description'] else ''

    html = f"""
<div style="font-family:'Outfit',-apple-system,Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;color:#3d3d3d;line-height:1.7;">
  <div style="text-align:center;padding:24px 0;border-bottom:2px solid #a8c5ae;">
    <span style="font-size:22px;font-weight:700;color:#2d3436;">The Menopause <span style="color:#7c9a82;">Planner</span></span>
    <p style="font-size:13px;color:#6b7280;margin:4px 0 0;">Weekly Wellness Insights</p>
  </div>

  <div style="padding:28px 20px;">
    <p>Hi {{{{ subscriber.first_name | default: "friend" }}}},</p>

    <p>This week we're diving into something our community has been asking about:</p>

    <h2 style="font-size:20px;color:#2d3436;margin:20px 0 12px;">{article['title']}</h2>

    <p style="color:#6b7280;">{article['description']}</p>

    <p style="text-align:center;margin:28px 0;">
      <a href="{article['url']}" style="display:inline-block;padding:14px 32px;background:#7c9a82;color:#ffffff;text-decoration:none;border-radius:10px;font-weight:600;font-size:15px;">
        Read the Full Article
      </a>
    </p>

    <div style="background:#faf8f5;border-radius:10px;padding:18px 20px;margin:24px 0;">
      <p style="font-weight:600;color:#5a7a60;margin:0 0 6px;">Quick Tip of the Week</p>
      <p style="margin:0;font-size:14px;">Try this today: track your sugar intake for just 24 hours. Note everything sweet you eat and any symptoms within 4 hours. Most women spot a connection immediately.</p>
    </div>

    <p style="font-size:14px;color:#6b7280;">
      P.S. Haven't grabbed your free Symptom Tracker yet?
      <a href="{TRACKER_PDF}" style="color:#7c9a82;font-weight:600;">Download it here</a> — 27 pages of tracking sheets to help you find your triggers.
    </p>
  </div>

  <div style="border-top:1px solid #e5e7eb;padding:20px;text-align:center;font-size:12px;color:#9ca3af;">
    <p>The Menopause Planner &middot; Real information. No fear. Just clarity.</p>
  </div>
</div>"""

    return {'subject': subject, 'preview_text': preview, 'html': html}


# ── Send via ConvertKit Broadcast ─────────────────
def send_broadcast(subject, html_content, preview_text=''):
    """Create and send a ConvertKit broadcast."""
    if not CONVERTKIT_API_SECRET:
        logger.error("CONVERTKIT_API_SECRET not set — cannot send broadcast")
        return None

    data = {
        'api_secret': CONVERTKIT_API_SECRET,
        'subject': subject,
        'content': html_content,
        'public': True,
    }
    if preview_text:
        data['description'] = preview_text

    try:
        resp = requests.post(
            f'{CK_BASE}/broadcasts',
            json=data,
            timeout=30
        )
        resp.raise_for_status()
        broadcast = resp.json().get('broadcast', {})
        broadcast_id = broadcast.get('id')
        logger.info(f"Broadcast created: ID {broadcast_id}")
        return broadcast_id

    except Exception as e:
        logger.error(f"Failed to create broadcast: {e}")
        return None


# ── Main ──────────────────────────────────────────
def main():
    dry_run = '--dry-run' in sys.argv or os.environ.get('DRY_RUN', '').lower() == 'true'

    print("=" * 50)
    print("Menopause Planner — Weekly Newsletter")
    print("=" * 50)

    # 1. Pick next article
    print("\n[1/3] Selecting article...")
    article = pick_next_article()
    if not article:
        print("ERROR: No articles available")
        sys.exit(1)
    print(f"  Title: {article['title']}")
    print(f"  URL: {article['url']}")

    # 2. Generate newsletter email
    print("\n[2/3] Generating newsletter email...")
    newsletter = generate_newsletter_email(article)
    print(f"  Subject: {newsletter['subject']}")
    print(f"  Preview: {newsletter.get('preview_text', '')[:60]}...")

    if dry_run:
        print("\n[DRY RUN] Email content:")
        print(f"  Subject: {newsletter['subject']}")
        print(f"  Preview: {newsletter.get('preview_text', '')}")
        print(f"  HTML length: {len(newsletter['html'])} chars")
        print("\n  First 500 chars of HTML:")
        print(f"  {newsletter['html'][:500]}")
        print("\n[DRY RUN] Would send broadcast to all subscribers.")
        return

    # 3. Send broadcast
    print("\n[3/3] Sending broadcast via ConvertKit...")
    broadcast_id = send_broadcast(
        newsletter['subject'],
        newsletter['html'],
        newsletter.get('preview_text', '')
    )

    if broadcast_id:
        record_sent_article(article['filename'], newsletter['subject'], broadcast_id)
        print(f"  Broadcast sent! ID: {broadcast_id}")
        print(f"  Article '{article['filename']}' recorded as sent")
    else:
        print("  WARNING: Broadcast creation failed")
        # Still record to avoid re-sending
        record_sent_article(article['filename'], newsletter['subject'], None)

    print("\nDone!")


if __name__ == '__main__':
    main()
