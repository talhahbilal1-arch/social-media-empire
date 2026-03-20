"""Inject prompt pack CTA banners into all existing fitover35.com articles.

Adds a visually distinct product promotion section between the author byline
and the existing 'Want more tips?' CTA. Idempotent — skips articles that
already have the banner.
"""

import os
import glob

ARTICLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "outputs", "fitover35-website", "articles"
)

# Marker to detect if CTA was already injected
MARKER = 'id="prompt-pack-cta"'

# The CTA banner HTML — dark card with brand-green accent, two products
CTA_HTML = '''<div id="prompt-pack-cta" style="border:2px solid #CCFF00;border-radius:16px;padding:28px 24px;margin-top:36px;background:linear-gradient(135deg,#111 0%,#1a1a1a 100%)">
<p style="margin:0 0 6px;font-family:Oswald,sans-serif;font-size:1.3em;font-weight:700;color:#CCFF00">🔓 AI-Powered Fitness Coaching Tools</p>
<p style="margin:0 0 18px;color:#ccc;font-size:0.92em;line-height:1.6">Stop writing workout programs from scratch. These copy-paste AI prompt packs save fitness coaches 5+ hours every week.</p>
<div style="display:flex;flex-wrap:wrap;gap:14px;margin-bottom:18px">
<a href="https://talhahbilal.gumroad.com/l/lupkl" target="_blank" rel="noopener" style="flex:1;min-width:220px;display:block;background:#1a1a1a;border:1px solid #333;border-radius:10px;padding:16px;text-decoration:none;transition:border-color 0.2s" onmouseover="this.style.borderColor='#CCFF00'" onmouseout="this.style.borderColor='#333'">
<p style="margin:0 0 4px;color:#CCFF00;font-weight:700;font-size:0.95em">AI Fitness Coach Vault</p>
<p style="margin:0 0 8px;color:#999;font-size:0.82em;line-height:1.5">75 copy-paste prompts for programs, nutrition plans, and client management</p>
<span style="color:#fff;font-weight:700;font-size:0.95em">$27</span> <span style="color:#666;font-size:0.8em;text-decoration:line-through">$37</span>
</a>
<a href="https://talhahbilal.gumroad.com/l/dkschg" target="_blank" rel="noopener" style="flex:1;min-width:220px;display:block;background:#1a1a1a;border:1px solid #333;border-radius:10px;padding:16px;text-decoration:none;transition:border-color 0.2s" onmouseover="this.style.borderColor='#CCFF00'" onmouseout="this.style.borderColor='#333'">
<p style="margin:0 0 4px;color:#CCFF00;font-weight:700;font-size:0.95em">FREE: 5 AI Fitness Prompts</p>
<p style="margin:0 0 8px;color:#999;font-size:0.82em;line-height:1.5">Try before you buy — 5 prompts that save fitness coaches 5 hours/week</p>
<span style="color:#fff;font-weight:700;font-size:0.95em">Free Download</span>
</a>
</div>
<p style="margin:0;text-align:center;font-size:0.78em;color:#666">Used by 50+ fitness coaches and personal trainers</p>
</div>
'''


def inject_cta(filepath):
    """Inject CTA into a single article. Returns True if modified."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Skip if already injected
    if MARKER in html:
        return False

    # Strategy: Insert BEFORE the yellow "Want more tips?" CTA block
    # This block starts with: <div style="background:#CCFF00;border-radius:12px;padding:24px;margin-top:32px;text-align:center">
    insert_marker = '<div style="background:#CCFF00;border-radius:12px;padding:24px;margin-top:32px;text-align:center">'

    if insert_marker in html:
        html = html.replace(insert_marker, CTA_HTML + '\n' + insert_marker, 1)
    else:
        # Fallback: insert before </main>
        html = html.replace('</main>', CTA_HTML + '\n</main>', 1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return True


def main():
    articles = glob.glob(os.path.join(ARTICLES_DIR, '*.html'))
    print(f"Found {len(articles)} articles in {ARTICLES_DIR}")

    injected = 0
    skipped = 0
    for path in sorted(articles):
        name = os.path.basename(path)
        if inject_cta(path):
            injected += 1
            print(f"  ✓ Injected: {name}")
        else:
            skipped += 1

    print(f"\nDone: {injected} injected, {skipped} already had CTA")


if __name__ == '__main__':
    main()
