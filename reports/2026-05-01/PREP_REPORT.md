# Prep Report — 2026-05-01 Mobile Session Prep

**Branch**: `claude/prep-affiliate-infrastructure-audit-iRNq9`
**Generated**: 2026-05-01 (UTC)
**Scope**: Audit + prep only. No production code changed. No PRs merged. No pushes to main.

---

## TL;DR

### Critical findings (revenue-relevant, in priority order)

1. **🔴 Menopause site is split-brained across two domains** — emails and JSON-LD schema link to `menopauseplanner.com` (DNS broken, 404), while sitemap and HTML canonicals point to `menopause-planner-website.vercel.app` (live). Email subscribers clicking the "open the planner" CTA hit a dead domain. **This is bleeding subscriber conversions right now.** See "Task 1 — Sitemap Audit" + `SITEMAP_FIX_PLAN.md`. Fix: configure DNS for `menopauseplanner.com` (10-min mobile task at registrar) → then run a one-shot sed migration in next desktop session.

2. **🟡 Menopause Amazon tag is shared with DailyDealDarling** — every Amazon click from a menopause article currently routes commission to `dailydealdarl-20`. This is a known issue you've already flagged. Tomorrow's mobile task: create new tag (e.g. `menoplanr-20`) in Amazon Associates dashboard. The desktop migration is documented in "Task 3" (single critical line: `pin_article_generator.py:299`, plus 124 menopause HTML files via scoped sed). Auto-rewrite logic (`_sanitize_affiliate_links`) will silently undo any partial fix — **the line-299 update is non-negotiable**.

3. **🟡 4 Gumroad source-of-truth ZIPs live only on the user's Mac** — `zero-miss-lead-engine-v1.zip`, `content-repurposing-machine-v1.zip`, `automated-review-generator-v1.zip`, `ai-automation-empire-bundle-v1.zip` are at `~/Desktop/ai-monetization/gumroad-deliverables/` and not version-controlled. If the Mac dies, those product deliverables are unrecoverable. Tomorrow's mobile task: confirm via Gumroad app which 8 products are actually live + which have ZIPs attached, so we can reconcile docs.

4. **🟢 No active money-leaking bugs in affiliate tags** — `fitover35-20` and `dailydealdarling1-20` (the two suspected wrong tags) are referenced ONLY inside `scripts/fix_amazon_urls.py` as cleanup targets in a `WRONG_TAGS` set, not as active references. The 411 hits for `fitover3509-20` (correct fitness tag) and 627 hits for `dailydealdarl-20` (correct DDD tag) all map to the right brand directories.

5. **🟢 Sitemaps for FitOver35 (189 URLs) and DailyDealDarling (127 URLs) are healthy** — both serve 200 OK. DDD redirects apex → www; submit `https://www.dailydealdarling.com/sitemap.xml` to GSC, not the apex.

### Tomorrow's manual mobile checklist (15 minutes total)

Order matters — top tasks unlock later ones.

| # | Task | Time | Where |
|---|------|------|-------|
| 1 | Configure DNS for `menopauseplanner.com` at registrar (A `@` → `76.76.21.21`, CNAME `www` → `cname.vercel-dns.com`) | 5 min | Domain registrar (GoDaddy/Namecheap/etc.) |
| 2 | Add `menopauseplanner.com` and `www.menopauseplanner.com` as custom domains in Vercel project | 1 min | Vercel mobile |
| 3 | Create new Amazon tracking ID for Menopause (suggested: `menoplanr-20`). Note exact tag. | 2 min | Amazon Associates app |
| 4 | Submit sitemaps to Google Search Console: `https://fitover35.com/sitemap.xml` and `https://www.dailydealdarling.com/sitemap.xml`. (Skip menopause until DNS is live.) | 2 min | GSC mobile |
| 5 | Apply to Surfer SEO affiliate (paste from `AFFILIATE_APPLICATIONS.md`) | 2 min | surferseo.com/affiliate-program |
| 6 | Apply to Grammarly affiliate via Impact (paste from `AFFILIATE_APPLICATIONS.md`) | 2 min | grammarly.com/affiliates |
| 7 | Apply to Semrush affiliate via Impact (paste from `AFFILIATE_APPLICATIONS.md`) | 1 min | semrush.com/lp/affiliate-program |
| 8 | Open Gumroad → confirm 8 live products + which have ZIPs attached. Photo/screenshot results. | 3 min | Gumroad mobile |
| 9 | Make.com → delete 9 deactivated scenarios listed in Task 5 (keep 3 most-recent failures as forensic if desired) | 3 min | Make.com mobile |

After completing 1, 3, and 8, send a single message back to the next desktop session with: new Menopause tag string, screenshots of Gumroad product list, and DNS status — that unlocks the desktop-side migration sweep (sitemap + tag + Gumroad ZIP versioning).

### Files generated this session

- `reports/2026-05-01/PREP_REPORT.md` (this file)
- `reports/2026-05-01/SITEMAP_FIX_PLAN.md` (menopause domain migration runbook)
- `reports/2026-05-01/AFFILIATE_APPLICATIONS.md` (paste-ready application copy)

### What was NOT changed
- Zero production code touched (no `.py`, `.yml`, `.js` outside `reports/`)
- Zero Amazon affiliate tags modified
- Zero Make.com scenarios touched
- Zero PRs created or merged
- Zero pushes to `main`

---

## Task 0 — Setup & Safety

- Working tree: clean
- Branch in use: `claude/prep-affiliate-infrastructure-audit-iRNq9` (harness-mandated; preferred over user's suggested `prep/2026-04-30-...` to keep GitHub integration wired correctly)
- Report directory: `reports/2026-05-01/` (using real session date, not the 2026-04-30 in the original prompt)
- Core production scripts confirmed present:
  - `video_automation/pin_article_generator.py` (77 KB)
  - `.github/workflows/content-engine.yml` (78 KB)
  - `scripts/regenerate_sitemaps.py` (sitemap generator — also: `ai-tools-hub/scripts/generate-sitemap.js` for PilotTools)

---

## Task 1 — Sitemap Audit

### Sitemap Status

| Domain | URL | HTTP Status | URL Count | Diagnosis |
|---|---|---|---|---|
| FitOver35 | https://fitover35.com/sitemap.xml | 200 OK | **189** | Healthy. Content-Type application/xml. |
| DailyDealDarling | https://dailydealdarling.com/sitemap.xml | 308 → www | **127** | Healthy via apex→www redirect. Submit `https://www.dailydealdarling.com/sitemap.xml` to GSC (the redirect target), not the apex. |
| Menopause (custom) | https://menopauseplanner.com/sitemap.xml | **DNS FAIL** | 0 | Domain not pointed at hosting. Known issue per CLAUDE.md (`menopauseplanner.com → 000`). |
| Menopause (Vercel) | https://menopause-planner-website.vercel.app/sitemap.xml | 200 OK | **108** | Healthy. This is the live URL Google currently sees. |
| PilotTools | (not audited live — domain TBD; on-disk sitemap has 12 URLs) | - | 12 | On-disk file at `outputs/pilottools-website/sitemap.xml`. |

### Critical Finding — Menopause SEO is split-brained (revenue-relevant)

The Menopause site has a **canonical/schema mismatch** that is bleeding ranking signals:

| Signal | Value | Reachable? |
|---|---|---|
| HTML `<link rel="canonical">` on 107/110 articles | `menopause-planner-website.vercel.app/...` | YES |
| Sitemap URLs (`<loc>`) | `menopause-planner-website.vercel.app/...` | YES |
| Schema.org JSON-LD `publisher.url` + `mainEntityOfPage.@id` | `menopauseplanner.com/...` | NO (DNS broken) |
| Email sequence CTAs | `https://menopauseplanner.com/planner` | NO (DNS broken) |
| Lead-magnet PDFs and `agents/blog_factory.py` | `menopauseplanner.com` | NO (DNS broken) |

**Result**: Google indexes the vercel.app URL (canonical wins for ranking), but structured data and email links advertise a 404 domain. Email subscribers clicking `menopauseplanner.com/planner` hit DNS failure → conversion loss.

**Repo-wide split**:
- 16+ files use `menopauseplanner.com` (articles, schema JSON-LD, email sequences, lead magnets)
- 20+ files use `menopause-planner-website.vercel.app` (sitemap generator, content engine, video pipeline, distribution)

### Files referencing each menopause domain

**`menopauseplanner.com`** (custom, currently DNS-broken):
```
agents/blog_factory.py
email_marketing/sequences/welcome_sequences.py
email_marketing/kit_sequence_uploader.py
email_marketing/email_sender.py
email_marketing/lead_magnets/generate_pdfs.py
menopause-planner-site/{contact,privacy,index,about,terms,editorial-process,medical-disclaimer}.html
scripts/regenerate_all_articles.py
scripts/generate_symptom_tracker_pdf.py
outputs/menopause-planner-website/{contact,privacy,about,...}.html
outputs/menopause-planner-website/articles/*.html  (in JSON-LD blocks)
```

**`menopause-planner-website.vercel.app`** (Vercel preview, currently live):
```
.github/workflows/content-engine.yml
.github/workflows/social-distribution.yml
scripts/regenerate_sitemaps.py    ← sitemap generator
scripts/ping_search_engines.py
scripts/seed_starter_pins.py
scripts/render_video_pins.py
scripts/post_sales_pins.py
scripts/add_internal_links.py
distribution/auto_distribute.py
video_automation/pin_article_generator.py
video_automation/seo_content_machine.py
video_automation/template_renderer.py
video_pipeline/config.py
video_pipeline/content_repurposer.py
analytics/generate_dashboard.py
email_marketing/menopause_newsletter.py
```

### Diagnosis (DO NOT FIX TONIGHT — see SITEMAP_FIX_PLAN.md)

**Two viable paths**, mutually exclusive — user must pick one:

1. **Fix DNS, migrate everything to `menopauseplanner.com`** (preferred for branding + email CTRs).
   - Configure DNS A/CNAME at registrar to Vercel
   - Add custom domain in Vercel project
   - Run a one-shot migration script: replace `menopause-planner-website.vercel.app` → `menopauseplanner.com` in the 20 files above
   - Regenerate sitemap, ping Google, submit to GSC
2. **Stay on vercel.app permanently** (faster, no DNS work, but loses brand consistency and email links stay broken).
   - Run a one-shot migration the OTHER direction: replace all `menopauseplanner.com` → `menopause-planner-website.vercel.app`
   - Email sequences go to vercel.app
   - Article JSON-LD canonicalizes to vercel.app

**Recommendation**: Path 1. The custom domain is owned, the brand consistency win is real, and email CTAs going to a 404 is a definite revenue leak.

---

## Task 2 — Gumroad Product → ZIP Mapping Audit

### ZIPs found in repo (11 total)

| ZIP | Path | Size | Modified | Inside |
|---|---|---|---|---|
| product-1-fitness-vault.zip | `prompt-packs/products/` | 34K | Apr 29 | 4 files (prompts, workouts, README, discovery script) |
| product-2-pinterest-blueprint.zip | `prompt-packs/products/` | 22K | Apr 29 | 7 files (system-overview, claude-prompts, hooks, makecom-guide, pexels-setup, content-strategy, README) |
| product-3-coach-machine.zip | `prompt-packs/products/` | 19K | Apr 29 | 4 files (prompts, scripts, README) |
| ai-money-maker-mega-bundle.zip | `prompt-packs/` | 50K | Apr 29 | 7 prompts.md files (one per pack below) |
| ai-business-automation-playbook.zip | `prompt-packs/products/` | 7.1K | Apr 29 | 1 file (prompts.md) |
| ai-content-machine.zip | `prompt-packs/products/` | 9.0K | Apr 29 | 1 file (prompts.md) |
| ai-copywriter.zip | `prompt-packs/products/` | 5.9K | Apr 29 | 1 file (prompts.md) |
| digital-product-launch-system.zip | `prompt-packs/products/` | 6.3K | Apr 29 | 1 file (prompts.md) |
| etsy-ecommerce-assistant.zip | `prompt-packs/products/` | 6.9K | Apr 29 | 1 file (prompts.md) |
| freelancer-ai-toolkit.zip | `prompt-packs/products/` | 8.8K | Apr 29 | 1 file (prompts.md) |
| side-hustle-finder.zip | `prompt-packs/products/` | 6.0K | Apr 29 | 1 file (prompts.md) |

### Live Gumroad products documented (per `prompt-packs/SESSION-HANDOFF.md`, last verified 2026-03-19)

The repo has **two competing handoff docs** describing different launches. There appears to be **8 live Gumroad products total**, but only some match ZIPs available in this Codespace.

| # | Gumroad Product Name | Slug | Price | Matching ZIP | ZIP location | Confidence |
|---|---|---|---|---|---|---|
| 1 | AI Fitness Coach Vault | `lupkl` | $27 | `product-1-fitness-vault.zip` | repo ✅ | HIGH (filename + content match) |
| 2 | Pinterest Automation Blueprint | `epjybe` | $47 | `product-2-pinterest-blueprint.zip` | repo ✅ | HIGH |
| 3 | Online Coach AI Client Machine | `weaaa` | $17 | `product-3-coach-machine.zip` | repo ✅ | HIGH |
| 4 | AI Automation Empire Bundle | `rwzcy` | $87 | `ai-automation-empire-bundle-v1.zip` (224 KB per handoff) | **NOT IN REPO** ⚠️ | LOW — file lives on Mac at `~/Desktop/ai-monetization/gumroad-deliverables/`; could be the same as `ai-money-maker-mega-bundle.zip` OR a different bundle entirely |
| 5 | Zero-Miss Lead Engine | `bxslh` | ? | `zero-miss-lead-engine-v1.zip` (54 KB per handoff) | **NOT IN REPO** ⚠️ | REQUIRES MANUAL VERIFICATION |
| 6 | Content Repurposing Machine | `rfoee` | ? | `content-repurposing-machine-v1.zip` (117 KB per handoff) | **NOT IN REPO** ⚠️ | REQUIRES MANUAL VERIFICATION |
| 7 | Automated Review Generator | `olryh` | ? | `automated-review-generator-v1.zip` (45 KB per handoff) | **NOT IN REPO** ⚠️ | REQUIRES MANUAL VERIFICATION |
| 8 | (one of these is presumably also live) | - | - | One of: `ai-business-automation-playbook`, `ai-content-machine`, `ai-copywriter`, `digital-product-launch-system`, `etsy-ecommerce-assistant`, `freelancer-ai-toolkit`, `side-hustle-finder` | - | UNCLEAR |

### Conflicting evidence between docs

- `prompt-packs/SESSION-HANDOFF.md` (2026-03-19): Lists 4 verified-live products + 4 newer ones uploaded — totals 8
- `PROMPT_PACK_HANDOFF.md` (older): Says 8 products published BUT files **not yet attached** (the 7 individual prompt packs + mega-bundle in `prompt-packs/products/`)
- `reports/2026-04-16/GUMROAD_ZIP_AUDIT.md`: Audited 11 ZIPs in this repo with grades — STRONG/MEDIUM ratings

### Critical gap

The 4 ZIPs supposedly attached to the higher-revenue products (`zero-miss-lead-engine-v1.zip`, `content-repurposing-machine-v1.zip`, `automated-review-generator-v1.zip`, `ai-automation-empire-bundle-v1.zip`) are **NOT in this repo**. They live on the user's Mac under `~/Desktop/ai-monetization/gumroad-deliverables/`. If the Mac is wiped or the path moves, those source-of-truth ZIPs disappear.

### Tomorrow's mobile checklist (Gumroad — 5 min)

1. Open https://gumroad.com/products on phone
2. For each of the 8 products, tap → Content tab → confirm a ZIP is attached and downloadable
3. Note any product showing "No file uploaded" — those need attention next desktop session
4. Report back: which 8 product names + slugs are actually live (so we can fix the doc drift)

### REQUIRES MANUAL VERIFICATION (do not guess)

- The 4 `*-v1.zip` files: copy them from the Mac into this repo at `gumroad-deliverables/` so they're version-controlled going forward
- The 8th live Gumroad product's identity (mapped to which of the 7 single-file ZIPs)
- Whether the 7 single-file ZIPs in `prompt-packs/products/` (freelancer/copywriter/etc.) are even live as products, or were never uploaded

---

## Task 3 — Amazon Tag Separation Scope (Menopause split)

### Tag hit counts (all file types)

| Tag | Files | Status |
|---|---|---|
| `dailydealdarl-20` | **627** | Active. Used for DDD + Menopause + Homedecor + Beauty (problematic) |
| `fitover3509-20` | **411** | Active. Fitness only — correct |
| `fitover35-20` | 3 | Listed as `WRONG_TAGS` in `scripts/fix_amazon_urls.py` (cleanup target, not active reference) |
| `dailydealdarling1-20` | 3 | Listed as `WRONG_TAGS` in `scripts/fix_amazon_urls.py` (cleanup target, not active reference) |

### `dailydealdarl-20` distribution by directory

| Path | Files | Notes |
|---|---|---|
| `outputs/dailydealdarling-website/` | 147 | DDD articles — KEEP (correct tag) |
| `outputs/menopause-planner-website/` | **124** | Menopause articles — **NEED TO CHANGE** to new menopause tag |
| `outputs_backup/dailydealdarling-website/` | 121 | Backup — leave alone |
| `outputs_backup/menopause-planner-website/` | 108 | Backup — leave alone |
| `outputs/homedecor-website/` | 13 | Homedecor uses DDD tag (intentional sub-brand) |
| `outputs/beauty-website/` | 13 | Beauty uses DDD tag (intentional sub-brand) |
| `dailydealdarling_website/articles/` | 13 | Legacy DDD articles |
| `email_marketing/sequences/` | 6 | **MIXED** — DDD + Menopause emails — manual review needed |
| `_backup/articles/` | 6 | Backup |
| `anti_gravity/site/` | 5 | Different brand (FYI) |
| Various Python/YAML files | 30 | **Mixed scope — see code-file table below** |

### Code files referencing `dailydealdarl-20`

| File | Affects | Risk |
|---|---|---|
| `video_automation/pin_article_generator.py` | All brands (uses `BRAND_AFFILIATE_TAGS` lookup) | LOW — already conditional on `brand_key`. Just need to update `BRAND_AFFILIATE_TAGS["menopause"]` |
| `video_automation/article_generator.py` | All brands | LOW — same pattern |
| `video_automation/article_templates.py` | All brands | LOW |
| `video_automation/seo_content_machine.py` | All brands | LOW |
| `video_pipeline/config.py` | All brands | LOW |
| `video_pipeline/content_repurposer.py` | All brands | LOW |
| `tiktok_automation/tiktok_pipeline.py` | All brands | MEDIUM — verify menopause routing |
| `automation/affiliate/link_generator.py` | All brands | MEDIUM — central tag generator |
| `automation/articles/article_generator.py` | All brands | MEDIUM |
| `automation/articles/dailydealdarling_article_generator.py` | DDD only (filename-locked) | LOW — leave alone |
| `automation/deals/fetch_deals.py` | DDD only | LOW |
| `automation/email/weekly_deals_finder.py` | DDD only | LOW |
| `automation/email/generate_lead_magnet_pdf.py` | Mixed | MEDIUM |
| `automation/amazon/rainforest_client.py` | All brands | MEDIUM |
| `automation/links/validate_links.py` | All brands | MEDIUM |
| `automation/config.py` | All brands | HIGH — central config |
| `email_marketing/kit_sequence_uploader.py` | Mixed (DDD + Menopause sequences) | HIGH — must split per-brand |
| `email_marketing/email_automation.py` | Mixed | HIGH |
| `email_marketing/sequences/welcome_sequences.py` | Mixed | HIGH |
| `monetization/affiliate_setup.py` | All brands | MEDIUM |
| `analytics/article_tracker.py` | All brands (logging) | LOW — read-only |
| `scripts/fix_amazon_urls.py` | Cleanup tool | LOW — already brand-aware |
| `scripts/fix_deals_links.py` | DDD only | LOW |
| `scripts/fix_menopause_links.py` | Menopause only | **HIGH PRIORITY** — must update to new tag |
| `scripts/regenerate_all_articles.py` | All brands | MEDIUM |
| `scripts/batch_restyle_articles.py` | All brands | MEDIUM |
| `scripts/validate_and_fix_asins.py` | All brands | MEDIUM |
| `scripts/convert_search_urls.py` | All brands | MEDIUM |
| `scripts/add_images_to_ddd.py` | DDD only | LOW |
| `.github/workflows/content-engine.yml` | All brands (orchestrator) | MEDIUM — verify env vars route correctly |

### `_sanitize_affiliate_links` analysis (lines 1374–1481, `pin_article_generator.py`)

The function reads `BRAND_AFFILIATE_TAGS[brand_key]` to determine the canonical tag, then **forcefully rewrites every Amazon URL's `?tag=...` query string** to that canonical (lines 1449–1461, Pass 3 "_enforce_tag").

**Specific risk for Menopause split**: After the user creates a new Amazon tag (e.g., `menoplanner-20`), if you only update existing article HTML files but **forget to update line 299** (`"menopause": "dailydealdarl-20"`), every subsequently-generated article will get its tags rewritten BACK to `dailydealdarl-20` by Pass 3. Future earnings would be silently routed to the wrong account.

**Additional landmine** at line 1416–1418:
```python
typo_map = {
    'menopauseplan-20': 'dailydealdarl-20',
}
```
This was apparently added because Claude/Gemini hallucinated a tag name. If the new real Menopause tag is similar to `menopauseplan-20`, this rule will erase it. Whatever tag the user picks must be checked against this typo_map.

### Required changes when user creates new Menopause tag (DO NOT EXECUTE TONIGHT)

**Single-line change in source code** (the most critical edit):
```python
# video_automation/pin_article_generator.py line 299
"menopause": "<NEW_MENOPAUSE_TAG>",  # was: dailydealdarl-20
```

Then in 6 places, also update the inline `tag=dailydealdarl-20` strings inside the menopause AMAZON_AFFILIATE_LINKS block (lines 156–205, ~50 entries). Easiest: a scoped sed inside that region.

**Other code files that need brand-aware updates**:
1. `email_marketing/sequences/welcome_sequences.py` — split into menopause-specific tag
2. `email_marketing/kit_sequence_uploader.py` — same
3. `automation/affiliate/link_generator.py` — central generator must branch on brand
4. `automation/config.py` — add `MENOPAUSE_AMAZON_TAG` env var
5. `scripts/fix_menopause_links.py` — update its target tag
6. `automation/email/generate_lead_magnet_pdf.py` — verify menopause PDFs

**Existing article files** (124 menopause HTML files): bulk replace ONLY within `outputs/menopause-planner-website/`:
```bash
# SAFE COMMAND (run only after new tag is created)
find outputs/menopause-planner-website -name "*.html" \
  -exec sed -i 's/tag=dailydealdarl-20/tag=<NEW_MENOPAUSE_TAG>/g' {} +
```

### Co-occurrence safety check

The user asked for a "safe grep" command to find Menopause references co-occurring with `dailydealdarl-20`. Use this to discover any sneaky cross-references in mixed-scope code files:
```bash
grep -rn "menopause" --include="*.py" --include="*.yml" --include="*.json" \
  | grep -i "dailydealdarl-20"
```

### Tomorrow's mobile checklist (Amazon — 5 min)

1. Log into Amazon Associates dashboard
2. Click "Create New Tracking ID" / "Add Tracking ID" (limit: 100 per account)
3. Suggest tag: `menoplanr-20` or `menoplanner-20` (within Amazon's 20-char limit)
4. Note the new tag exactly
5. **Do NOT delete the old tag yet** — articles still use it until next desktop session updates code
6. Report new tag back so the desktop session can run the migration

### Risk: 180-day Amazon Associates clock

User's account has ~120 days remaining and 1/3 sales done. **Switching the menopause tag does NOT reset the clock** — Amazon counts sales across all tracking IDs in the same Associates account. But:
- Any sale attributed to the old tag (`dailydealdarl-20`) before the migration counts under DDD's running total too
- Adding a new tracking ID is free and doesn't trigger account review
- Tag changes are not audited — Amazon doesn't care which tracking ID a sale comes through, only that the parent account converts

**Verdict**: Safe to do whenever. No clock impact.

---

## Task 4 — Affiliate Application Copy

Full copy-paste-ready application text for **Semrush**, **Grammarly**, and **Surfer SEO** is in:

**`reports/2026-05-01/AFFILIATE_APPLICATIONS.md`**

Each application includes:
- Form-field-by-form-field text (no editing needed, just paste)
- Realistic traffic estimates based on actual repo article counts (199 fitness / 130 deals / 110 menopause / 13 pilottools)
- ~150-word audience description per program
- ~150-word "how will you promote" per program
- Likely rejection risk + strongest rebuttal angle

Application order recommended in that file: Surfer first (lowest risk, highest commission %), then Grammarly, then Semrush.

---

## Task 5 — Make.com Error-Scenario Cleanup Plan

The user's Make.com team has 9 deactivated scenarios with 100% error rates. These are not bleeding ops budget (they're inactive), but they clutter the team workspace and obscure the healthy 9 active scenarios.

### Scenario IDs to clean up

| Bucket | IDs | Status | Recommended action |
|---|---|---|---|
| v5/v7 video scenarios (deactivated, 100% error) | 4669524, 4671823, 4671827, 4732882, 4732899, 4732903 | Inactive | DELETE all 6 — replaced by current pipeline |
| Old v1 video scenarios | 4263862, 4263863, 4263864 | Marked invalid | DELETE all 3 — superseded twice over |

### Recommendation: keep one most-recent failed version per brand for forensic reference

Of the v5/v7 scenarios above, keep the **single most recent failure per brand** (one for fitness, one for deals, one for menopause). This preserves error logs for a future "why did v5 fail?" debug if you ever revisit video pipelines. Mapping requires Make.com UI access (scenario names/brands aren't visible from IDs alone).

### Delete plan (DO NOT EXECUTE — user approves manually in Make UI)

1. In Make.com → Team workspace, sort scenarios by status (Inactive first)
2. For each ID above, open the scenario, screenshot the last error in execution history (forensic backup — 30 sec each)
3. Click ⋮ → Delete scenario → confirm
4. Estimated time: 3 minutes total

### Why DON'T do this remotely tonight
The Make.com MCP tools available to this session **do** have a `scenarios_delete` capability, but per the user's rules ("DO NOT delete any Make.com scenarios — only recommend") this is recommendation-only. Tomorrow's mobile session can do this in 3 minutes via the Make UI.

### What NOT to delete
The 9 active scenarios (per CLAUDE.md "Make.com: 9 active scenarios healthy") — including the per-brand video pin posters (`Fitness v3`, `Deals v4`, `Menopause v4`) and the unified fallback router. Don't touch any scenario currently flagged as Active.

### Tomorrow's mobile checklist (Make.com — 3 min)

1. Open Make.com on phone
2. Sort by Inactive
3. Delete the 9 listed scenario IDs (skip the 3 you choose to retain for forensics if desired)
4. Optionally: rename surviving forensic scenarios to `archive-fitness-v5-failed-2026-04`, etc., for clarity


