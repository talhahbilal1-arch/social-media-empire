# Sitemap Fix Plan — Menopause Domain Migration

**Status**: Diagnosis only — DO NOT IMPLEMENT until user picks Path 1 vs Path 2.

## Problem (one paragraph)

Menopause site has a domain split-brain. The HTML canonical tags + sitemap point to `menopause-planner-website.vercel.app` (which is what Google currently indexes). But the JSON-LD structured data inside articles, the email sequences, the lead magnets, and 7 supporting site pages all link to `menopauseplanner.com` — a custom domain whose DNS is unconfigured and returns connection failures. Email subscribers hitting `https://menopauseplanner.com/planner` get a dead link, killing conversions on the lead-magnet flow.

## Path 1 (RECOMMENDED) — Migrate everything to `menopauseplanner.com`

### Manual prerequisites (user does these on phone tomorrow morning)
1. Log into the domain registrar for `menopauseplanner.com`
2. Set DNS records per Vercel docs:
   - `A @ 76.76.21.21`
   - `CNAME www cname.vercel-dns.com`
3. In Vercel project for menopause site → Settings → Domains → Add `menopauseplanner.com` and `www.menopauseplanner.com`
4. Wait for SSL cert provisioning (5–15 min)
5. Verify `curl -sI https://menopauseplanner.com/` returns 200

### Code migration (next Codespace session, after DNS verified)
**One-shot replace** in these 20 files:

```
.github/workflows/content-engine.yml
.github/workflows/social-distribution.yml
scripts/regenerate_sitemaps.py
scripts/ping_search_engines.py
scripts/seed_starter_pins.py
scripts/render_video_pins.py
scripts/post_sales_pins.py
scripts/add_internal_links.py
scripts/batch_restyle_articles.py
scripts/setup_menopause_email_sequence.py
scripts/generate_symptom_tracker_pdf.py
distribution/auto_distribute.py
video_automation/pin_article_generator.py
video_automation/seo_content_machine.py
video_automation/template_renderer.py
video_pipeline/config.py
video_pipeline/content_repurposer.py
analytics/generate_dashboard.py
email_marketing/menopause_newsletter.py
.github/workflows/archive/system-health.yml  (low priority — archived)
```

**Replacement command** (RUN ONLY AFTER USER CONFIRMS PATH 1):
```bash
git ls-files | xargs grep -l "menopause-planner-website.vercel.app" 2>/dev/null \
  | xargs sed -i 's|menopause-planner-website\.vercel\.app|menopauseplanner.com|g'
```

### Then regenerate sitemap and ping search engines
```bash
python3 scripts/regenerate_sitemaps.py
python3 scripts/ping_search_engines.py menopause
```

### Then update Vercel project settings
- Set primary domain to `menopauseplanner.com` (so vercel.app issues a 308 redirect)
- This preserves any inbound links to vercel.app

### GSC actions (manual, by user on phone)
1. Add `https://menopauseplanner.com/` as a new property
2. Verify ownership via DNS TXT or HTML file (Vercel auto-handles HTML file)
3. Submit `https://menopauseplanner.com/sitemap.xml`
4. In old vercel.app GSC property: use Change of Address tool pointing to new domain

## Path 2 — Stay on `vercel.app` permanently (NOT recommended)

Replacement command (if user picks this):
```bash
git ls-files | xargs grep -l "menopauseplanner\.com" 2>/dev/null \
  | xargs sed -i 's|menopauseplanner\.com|menopause-planner-website.vercel.app|g'
```

Drawbacks:
- Brand looks unprofessional (preview URL in emails)
- Lost domain equity (the user already paid for menopauseplanner.com)
- Vercel can rotate preview URLs; custom domain is stable

## Estimated effort

| Path | DNS work | Code edits | Verification | Total |
|------|----------|-----------|--------------|-------|
| 1 | 10 min mobile + 15 min wait | 5 min sed + 1 commit | 10 min curl + GSC | ~45 min |
| 2 | 0 | 5 min sed + 1 commit | 5 min curl | ~15 min |

## Decision needed from user
- Path 1 or Path 2?
- If Path 1, willing to do 10-min DNS step on registrar tomorrow?
