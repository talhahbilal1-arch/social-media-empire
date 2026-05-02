#!/usr/bin/env python3
"""Conversion leak fixes — one-time migration.

Idempotent: each fix is gated by a marker comment so re-running is safe.

Usage:
  python3 scripts/migrations/fix_conversion_leaks.py --dry-run   # show what would change
  python3 scripts/migrations/fix_conversion_leaks.py --leak 1    # fix one specific leak (1-8)
  python3 scripts/migrations/fix_conversion_leaks.py             # fix all leaks

Leaks (see reports/2026-05-01/CONVERSION_LEAKS.md):
  1. Add Gumroad CTA to 37 fitness buyer-intent articles
  2. Pinterest share buttons to all 438 articles (template-level — separate concern)
  3. Add Kit form to 3 Gumroad landing pages
  4. Add lead-magnet CTA to 23 deals buyer-intent articles
  5. Investigate 5 cross-pub menopause-on-DDD (read-only — reports findings)
  6. Replace 12+ amazon search URL placeholders
  7. Add Kit forms to 32 articles missing email capture
  8. Add Etsy planner CTA to 6 menopause buyer-intent articles
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# ─── Marker comments (idempotency gates) ──────────────────────────────────
MARK_LEAK1 = "<!-- FIX_LEAK_1_GUMROAD_CTA -->"
MARK_LEAK2 = "<!-- FIX_LEAK_2_PIN_BUTTON -->"
MARK_LEAK3 = "<!-- FIX_LEAK_3_LANDING_EMAIL -->"
MARK_LEAK4 = "<!-- FIX_LEAK_4_DEALS_CTA -->"
MARK_LEAK7 = "<!-- FIX_LEAK_7_KIT_FORM -->"
MARK_LEAK8 = "<!-- FIX_LEAK_8_MENOPAUSE_CTA -->"

# Pinterest "Pin This" button — uses JS to read page URL/title at click time so
# the same block works on every article without needing to bake URLs in.
PIN_BUTTON_BLOCK = f"""
{MARK_LEAK2}
<div style="text-align:center;margin:32px 0;">
  <a href="#" onclick="window.open('https://pinterest.com/pin/create/button/?url='+encodeURIComponent(window.location.href)+'&description='+encodeURIComponent(document.title), 'pin', 'width=720,height=600'); return false;" style="display:inline-block;background:#E60023;color:#fff;padding:10px 22px;border-radius:6px;text-decoration:none;font-weight:700;font-size:0.95em;">📌 Pin This Article</a>
</div>
"""

# ─── Brand Kit form IDs (from CLAUDE.md) ──────────────────────────────────
KIT_FORM_IDS = {
    "fitover35": "8946984",
    "dailydealdarling": "9144859",
    "menopause-planner": "9144926",
}

# ─── CTA blocks ───────────────────────────────────────────────────────────

GUMROAD_FITNESS_CTA = f"""
{MARK_LEAK1}
<div style="background:linear-gradient(135deg,#1565C0,#0D47A1);color:#fff;padding:28px;border-radius:14px;margin:36px 0;text-align:center;box-shadow:0 4px 16px rgba(13,71,161,0.18);">
  <h3 style="color:#fff;margin:0 0 12px;font-size:1.4em;">Want a Done-For-You Coaching System?</h3>
  <p style="color:#e3f2fd;margin:0 0 20px;font-size:1.05em;line-height:1.5;">The AI Fitness Coach Vault — 75 prompts, 5 done-for-you training blocks, and a discovery call script. Built for men 35+ who want to stop guessing and start training smarter.</p>
  <a href="https://talhahbilal.gumroad.com/l/lupkl" target="_blank" rel="noopener sponsored" style="background:#CCFF00;color:#000;padding:14px 32px;border-radius:8px;font-weight:800;text-decoration:none;display:inline-block;font-size:1.05em;">Get the Vault — $27 →</a>
</div>
"""

DEALS_LEADMAG_CTA = f"""
{MARK_LEAK4}
<div style="background:#FDF6F0;border:2px solid #C47D8E;color:#2c2c2c;padding:24px;border-radius:14px;margin:36px 0;text-align:center;">
  <h3 style="color:#C47D8E;margin:0 0 12px;font-size:1.3em;">Free: 30 AI Prompts for Smart Shopping</h3>
  <p style="margin:0 0 18px;line-height:1.5;">Get the curated prompt pack to find better deals, compare products faster, and stop overspending. Free download, instant access.</p>
  <a href="https://talhahbilal.gumroad.com/l/free-ai-prompts" target="_blank" rel="noopener" style="background:#C47D8E;color:#fff;padding:12px 28px;border-radius:8px;font-weight:700;text-decoration:none;display:inline-block;">Download Free →</a>
</div>
"""

MENOPAUSE_ETSY_CTA = f"""
{MARK_LEAK8}
<div style="background:#F4F1EA;border:2px solid #6B705C;padding:24px;border-radius:14px;margin:36px 0;text-align:center;">
  <h3 style="color:#6B705C;font-family:'DM Serif Display',serif;margin:0 0 12px;">Track Every Symptom. Reclaim Your Sleep.</h3>
  <p style="color:#555;margin:0 0 18px;line-height:1.5;">A printable digital planner built specifically for women navigating menopause — track symptoms, sleep patterns, supplements, and mood in one place.</p>
  <a href="https://www.etsy.com/listing/4435219468/menopause-wellness-planner-bundle?utm_source=article&utm_medium=organic" target="_blank" rel="noopener sponsored" style="background:#6B705C;color:#fff;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:700;display:inline-block;">Get the Planner on Etsy →</a>
  <p style="font-size:0.85em;color:#888;margin:12px 0 0;">Instant download · Print at home · One-time purchase</p>
</div>
"""

def kit_form_block(brand_dir, accent_color="#C47D8E"):
    """Build a Kit email-capture form for a specific brand."""
    form_id = KIT_FORM_IDS.get(brand_dir, "")
    if not form_id:
        return ""
    return f"""
{MARK_LEAK7}
<div style="background:#fff;border:2px solid {accent_color};border-radius:14px;padding:24px;margin:36px 0;text-align:center;">
  <h3 style="color:{accent_color};margin:0 0 8px;font-size:1.3em;">Get the Free Newsletter</h3>
  <p style="margin:0 0 16px;color:#555;">Hand-picked tips and product breakdowns delivered weekly. No spam, unsubscribe anytime.</p>
  <script src="https://f.convertkit.com/ckjs/ck.5.js"></script>
  <form action="https://app.kit.com/forms/{form_id}/subscriptions" method="post" data-sv-form="{form_id}" style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
    <input type="email" name="email_address" placeholder="Enter your email" required style="padding:12px 16px;border:1px solid #ddd;border-radius:8px;width:100%;max-width:300px;font-size:1em;">
    <button type="submit" style="padding:12px 24px;background:{accent_color};color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:700;font-size:1em;">Join Free</button>
  </form>
</div>
"""

LANDING_KIT_BLOCK = lambda brand_dir, accent: f"""
{MARK_LEAK3}
<div style="background:#fafafa;border:2px dashed {accent};border-radius:12px;padding:22px;margin:24px 0;text-align:center;">
  <h3 style="color:{accent};margin:0 0 10px;font-size:1.2em;">Not Ready to Buy?</h3>
  <p style="margin:0 0 14px;color:#444;">Get a free chapter and stay in the loop on updates.</p>
  <script src="https://f.convertkit.com/ckjs/ck.5.js"></script>
  <form action="https://app.kit.com/forms/{KIT_FORM_IDS[brand_dir]}/subscriptions" method="post" data-sv-form="{KIT_FORM_IDS[brand_dir]}" style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
    <input type="email" name="email_address" placeholder="Enter your email" required style="padding:11px 14px;border:1px solid #ccc;border-radius:6px;width:100%;max-width:280px;font-size:0.95em;">
    <button type="submit" style="padding:11px 22px;background:{accent};color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:700;">Get Free Chapter</button>
  </form>
</div>
"""

# ─── Search URL → /dp/ASIN replacements (Leak #6) ─────────────────────────
SEARCH_URL_REPLACEMENTS = {
    # Fitness brand replacements (use fitover3509-20)
    ("fitness", "resistance+bands"): "https://www.amazon.com/dp/B01AVDVHTI?tag=fitover3509-20",
    ("fitness", "resistance+bands+set"): "https://www.amazon.com/dp/B01AVDVHTI?tag=fitover3509-20",
    ("fitness", "yoga+mat"): "https://www.amazon.com/dp/B0B74MRJS3?tag=fitover3509-20",
    ("fitness", "kettlebell"): "https://www.amazon.com/dp/B0731DWW5K?tag=fitover3509-20",
    ("fitness", "foam+roller"): "https://www.amazon.com/dp/B0040EKZDY?tag=fitover3509-20",
    ("fitness", "creatine+monohydrate"): "https://www.amazon.com/dp/B002DYIZEO?tag=fitover3509-20",
    ("fitness", "b12+supplement"): "https://www.amazon.com/dp/B001F71XAI?tag=fitover3509-20",  # multivitamin default
    ("fitness", "product"): "https://www.amazon.com/dp/B0DPFW7F4B?tag=fitover3509-20",  # default fitness
    # Deals brand
    ("deals", "product"): "https://www.amazon.com/dp/B002VK5QN8?tag=dailydealdarl-20",
    ("deals", "affordable+skincare+product+sales"): "https://www.amazon.com/dp/B01M4MCUAF?tag=dailydealdarl-20",  # vitamin C serum default
}


def detect_brand_dir(filepath):
    """Return brand directory name from path."""
    parts = filepath.parts
    for p in parts:
        if "fitover35-website" in p:
            return "fitover35"
        if "dailydealdarling-website" in p:
            return "dailydealdarling"
        if "menopause-planner-website" in p:
            return "menopause-planner"
    return None


def detect_brand_short(filepath):
    """Map directory → short brand key for SEARCH_URL_REPLACEMENTS."""
    bd = detect_brand_dir(filepath)
    return {"fitover35": "fitness", "dailydealdarling": "deals", "menopause-planner": "menopause"}.get(bd)


def insert_before_closing_article(html, block):
    """Insert block before the most appropriate closing structural tag.

    Tries in order: </article>, </main>, <footer (opening), </body>. Returns
    (new_html, ok) — ok is False only if NONE of the anchors are present.
    Skips redirect-only pages (very short + 'Redirecting to' marker).
    """
    if "Redirecting to" in html and len(html) < 800:
        return html, False  # don't pollute redirect stubs
    if "</article>" in html:
        return html.replace("</article>", f"{block}\n  </article>", 1), True
    if "</main>" in html:
        return html.replace("</main>", f"{block}\n  </main>", 1), True
    m = re.search(r'<footer[\s>]', html)
    if m:
        idx = m.start()
        return html[:idx] + block + "\n" + html[idx:], True
    if "</body>" in html:
        return html.replace("</body>", f"{block}\n  </body>", 1), True
    return html, False


# ─── Leak fixers ──────────────────────────────────────────────────────────

def fix_leak_1(dry_run=False):
    """Add Gumroad CTA to fitness buyer-intent articles missing one."""
    base = REPO / "outputs/fitover35-website/articles"
    patterns = ["best-*.html", "top-*.html", "*-vs-*.html", "*-review*.html"]
    targets = []
    for pat in patterns:
        for f in base.glob(pat):
            content = f.read_text(encoding="utf-8")
            if "gumroad.com/l/" in content or "etsy.com/listing" in content:
                continue
            if MARK_LEAK1 in content:
                continue
            targets.append(f)
    print(f"[Leak 1] {len(targets)} fitness articles need Gumroad CTA")
    if dry_run:
        for t in targets[:5]:
            print(f"  would patch: {t.name}")
        if len(targets) > 5:
            print(f"  ... and {len(targets)-5} more")
        return len(targets)
    patched = 0
    for f in targets:
        content = f.read_text(encoding="utf-8")
        new, ok = insert_before_closing_article(content, GUMROAD_FITNESS_CTA)
        if ok:
            f.write_text(new, encoding="utf-8")
            patched += 1
        else:
            print(f"  WARN no-anchor: {f.name}")
    print(f"[Leak 1] ✓ Patched {patched}/{len(targets)} files")
    return patched


def fix_leak_3(dry_run=False):
    """Add Kit form to 3 Gumroad product landing pages."""
    landing_pages = [
        (REPO / "outputs/fitover35-website/articles/ai-fitness-vault.html", "fitover35", "#1565C0"),
        (REPO / "outputs/fitover35-website/articles/ai-coach-machine.html", "fitover35", "#1565C0"),
        (REPO / "outputs/dailydealdarling-website/articles/pinterest-automation-blueprint.html", "dailydealdarling", "#C47D8E"),
    ]
    patched = 0
    for path, brand_dir, accent in landing_pages:
        if not path.exists():
            print(f"[Leak 3] SKIP missing: {path.name}")
            continue
        content = path.read_text(encoding="utf-8")
        if MARK_LEAK3 in content:
            print(f"[Leak 3] SKIP already-patched: {path.name}")
            continue
        if dry_run:
            print(f"[Leak 3] would patch: {path.name}")
            patched += 1
            continue
        block = LANDING_KIT_BLOCK(brand_dir, accent)
        new, ok = insert_before_closing_article(content, block)
        if ok:
            path.write_text(new, encoding="utf-8")
            patched += 1
        else:
            print(f"[Leak 3] WARN no-anchor: {path.name}")
    print(f"[Leak 3] {'would patch' if dry_run else '✓ Patched'} {patched} landing pages")
    return patched


def fix_leak_4(dry_run=False):
    """Add lead-magnet CTA to deals buyer-intent articles missing one."""
    base = REPO / "outputs/dailydealdarling-website/articles"
    patterns = ["best-*.html", "top-*.html", "*-vs-*.html", "*-review*.html"]
    targets = []
    for pat in patterns:
        for f in base.glob(pat):
            content = f.read_text(encoding="utf-8")
            if "gumroad.com/l/" in content or "etsy.com/listing" in content:
                continue
            if MARK_LEAK4 in content:
                continue
            targets.append(f)
    print(f"[Leak 4] {len(targets)} deals articles need lead-magnet CTA")
    if dry_run:
        for t in targets[:5]:
            print(f"  would patch: {t.name}")
        if len(targets) > 5:
            print(f"  ... and {len(targets)-5} more")
        return len(targets)
    patched = 0
    for f in targets:
        content = f.read_text(encoding="utf-8")
        new, ok = insert_before_closing_article(content, DEALS_LEADMAG_CTA)
        if ok:
            f.write_text(new, encoding="utf-8")
            patched += 1
        else:
            print(f"  WARN no-anchor: {f.name}")
    print(f"[Leak 4] ✓ Patched {patched}/{len(targets)} files")
    return patched


def fix_leak_6(dry_run=False):
    """Replace amazon.com/s?k= search URLs with direct /dp/ASIN links.

    Real-world URLs in articles look like:
      https://www.amazon.com/s?k=creatine+monohydrate&tag=fitover3509-20
      https://www.amazon.com/s?k=product&tag=dailydealdarl-20
    We match the FULL search URL (including any &tag=...) and replace with the
    /dp/ASIN URL, which already includes the correct tag.
    """
    fixes = 0
    files_touched = set()
    # Regex: capture the search query, allow optional &-params after it
    search_url_re = re.compile(
        r'https?://(?:www\.)?amazon\.com/s\?k=([^"&<>\s\']+)(?:&[^"<>\s\']*)?'
    )
    for brand_dir, brand_key in [("fitover35", "fitness"), ("dailydealdarling", "deals"), ("menopause-planner", "menopause")]:
        base = REPO / f"outputs/{brand_dir}-website/articles"
        for f in base.glob("*.html"):
            content = f.read_text(encoding="utf-8")
            if not search_url_re.search(content):
                continue
            file_fixes = [0]

            def _replace(m):
                query = m.group(1)
                key = (brand_key, query)
                replacement = SEARCH_URL_REPLACEMENTS.get(key)
                if not replacement:
                    replacement = SEARCH_URL_REPLACEMENTS.get((brand_key, "product"))
                if not replacement:
                    return m.group(0)
                file_fixes[0] += 1
                return replacement

            new_content = search_url_re.sub(_replace, content)
            if file_fixes[0] > 0:
                files_touched.add(f.name)
                fixes += file_fixes[0]
                if not dry_run:
                    f.write_text(new_content, encoding="utf-8")
    print(f"[Leak 6] {'would replace' if dry_run else '✓ Replaced'} {fixes} search URLs across {len(files_touched)} files")
    return fixes


def fix_leak_7(dry_run=False):
    """Add Kit email-capture form to articles missing one."""
    accent_by_brand = {"fitover35": "#CCFF00", "dailydealdarling": "#C47D8E", "menopause-planner": "#6B705C"}
    total = 0
    for brand_dir in KIT_FORM_IDS:
        base = REPO / f"outputs/{brand_dir}-website/articles"
        if not base.exists():
            continue
        targets = []
        for f in base.glob("*.html"):
            content = f.read_text(encoding="utf-8")
            # Skip if already has Kit form
            if "kit.com/forms/" in content or "convertkit" in content or "data-uid" in content:
                continue
            if MARK_LEAK7 in content:
                continue
            targets.append(f)
        print(f"[Leak 7] {brand_dir}: {len(targets)} articles need Kit form")
        if dry_run:
            for t in targets[:3]:
                print(f"  would patch: {t.name}")
            total += len(targets)
            continue
        block = kit_form_block(brand_dir, accent_by_brand[brand_dir])
        for f in targets:
            content = f.read_text(encoding="utf-8")
            new, ok = insert_before_closing_article(content, block)
            if ok:
                f.write_text(new, encoding="utf-8")
                total += 1
            else:
                print(f"  WARN no-anchor: {f.name}")
    print(f"[Leak 7] {'would patch' if dry_run else '✓ Patched'} {total} files total")
    return total


def fix_leak_8(dry_run=False):
    """Add Etsy planner CTA to menopause buyer-intent articles missing one."""
    base = REPO / "outputs/menopause-planner-website/articles"
    patterns = ["best-*.html", "top-*.html", "*-vs-*.html", "*-review*.html"]
    targets = []
    for pat in patterns:
        for f in base.glob(pat):
            content = f.read_text(encoding="utf-8")
            if "gumroad.com/l/" in content or "etsy.com/listing" in content:
                continue
            if MARK_LEAK8 in content:
                continue
            targets.append(f)
    print(f"[Leak 8] {len(targets)} menopause articles need Etsy CTA")
    if dry_run:
        for t in targets:
            print(f"  would patch: {t.name}")
        return len(targets)
    patched = 0
    for f in targets:
        content = f.read_text(encoding="utf-8")
        new, ok = insert_before_closing_article(content, MENOPAUSE_ETSY_CTA)
        if ok:
            f.write_text(new, encoding="utf-8")
            patched += 1
        else:
            print(f"  WARN no-anchor: {f.name}")
    print(f"[Leak 8] ✓ Patched {patched}/{len(targets)} files")
    return patched


def fix_leak_2(dry_run=False):
    """Add Pinterest 'Pin This' button to every article on all 3 brand sites."""
    total_targets = 0
    total_patched = 0
    total_skipped = 0
    for brand_dir in KIT_FORM_IDS:
        base = REPO / f"outputs/{brand_dir}-website/articles"
        if not base.exists():
            continue
        targets = []
        for f in base.glob("*.html"):
            content = f.read_text(encoding="utf-8")
            # Skip if marker present OR template-rendered pin button text exists
            if MARK_LEAK2 in content or "Pin This Article" in content:
                continue
            targets.append(f)
        total_targets += len(targets)
        if dry_run:
            print(f"[Leak 2] {brand_dir}: would patch {len(targets)} articles")
            continue
        patched = 0
        skipped = 0
        for f in targets:
            content = f.read_text(encoding="utf-8")
            new, ok = insert_before_closing_article(content, PIN_BUTTON_BLOCK)
            if ok:
                f.write_text(new, encoding="utf-8")
                patched += 1
            else:
                skipped += 1
        total_patched += patched
        total_skipped += skipped
        print(f"[Leak 2] {brand_dir}: patched {patched}, skipped {skipped}")
    if dry_run:
        print(f"[Leak 2] would patch {total_targets} articles total")
    else:
        print(f"[Leak 2] ✓ Patched {total_patched} articles total ({total_skipped} skipped)")
    return total_patched


def investigate_leak_5():
    """Read-only: report on the 5 menopause articles cross-published in DDD."""
    cross_pub = [
        "menopause-hot-flash-relief.html",
        "menopause-self-care-routine.html",
        "menopause-sleep-solutions.html",
        "menopause-wellness-guide.html",
        "perimenopause-guide.html",
    ]
    ddd_dir = REPO / "outputs/dailydealdarling-website/articles"
    meno_dir = REPO / "outputs/menopause-planner-website/articles"
    print("[Leak 5] Cross-pub menopause articles in DDD:")
    for name in cross_pub:
        ddd = ddd_dir / name
        meno = meno_dir / name
        ddd_exists = ddd.exists()
        meno_exists = meno.exists()
        verdict = "DUPLICATE — pick canonical" if (ddd_exists and meno_exists) else ("DDD-only — orphan" if ddd_exists else "missing")
        print(f"  {name}: DDD={ddd_exists}, Menopause={meno_exists} → {verdict}")


# ─── Entrypoint ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--leak", type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8], help="Run only this leak's fix")
    args = parser.parse_args()

    leaks = {1: fix_leak_1, 2: fix_leak_2, 3: fix_leak_3, 4: fix_leak_4, 6: fix_leak_6, 7: fix_leak_7, 8: fix_leak_8}

    if args.leak == 5:
        investigate_leak_5()
        return
    if args.leak:
        leaks[args.leak](dry_run=args.dry_run)
        return

    print("=== Running all conversion-leak fixes ===\n")
    for n in sorted(leaks):
        leaks[n](dry_run=args.dry_run)
        print()
    investigate_leak_5()


if __name__ == "__main__":
    main()
