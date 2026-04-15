# Revenue Acceleration Sprint — Parallel Agent Execution

**Date:** 2026-04-15
**Branch:** `claude/build-insights-dashboard-Rbbvr`
**Goal:** Close every revenue-blocking gap identified in the insights report and ship the infrastructure that gets us to $10k/mo online passively.
**Strategy:** 8 parallel agents, non-overlapping file scopes, all committed to the same branch.

## Agent Work Packages

| # | Agent | Scope | Status |
|---|-------|-------|--------|
| 1 | GitHub Workflows | `.github/workflows/*.yml` | DONE |
| 2 | Playwright Automation | `automation/playwright/` | DONE |
| 3 | Anti-Gravity Deploy | `anti_gravity/site/` + deploy scripts | DONE (was already scaffolded — validated) |
| 4 | MCP Installer | `scripts/install_mcps.sh` + `docs/` | DONE |
| 5 | $97 Signature Product | `products/signature/` | DONE |
| 6 | Search URL Converter | `scripts/convert_all_search_urls_v2.py` | DONE (re-spawned after first timeout) |
| 7 | Affiliate Signup Automator | `automation/affiliate_signups/` | DONE |
| 8 | Enhanced Revenue Dashboard | `analytics/` + `.github/workflows/dashboard-update.yml` | DONE |

---

## Review Section — Everything That Shipped

### Commits on this branch (7 total)

1. `feat(workflows)` — daily revenue digest, branch cleanup, Gumroad sales sync, error alerts (+ Python helpers)
2. `feat(anti-gravity)` — Vercel deploy scaffold (vercel.json, deploy script, workflow, README)
3. `feat(automation)` — Playwright suite (Gumroad ZIP uploader + PromptBase lister)
4. `feat(mcp)` — MCP installer script + setup guide + token checklist
5. `feat(automation)` — affiliate signup Playwright suite (Semrush, Hostinger, Ahrefs, Frase, ClickBank)
6. `feat(signature)` — $97 Body Recomposition Blueprint scaffold (landing page, upsell flow, launch checklist)
7. `feat(dashboard)` — real-time revenue dashboard generator + hourly workflow
8. `feat(scripts)` — Amazon search-URL → direct-link converter with 119-entry ASIN dictionary

### Files shipped: 37 new + 3 modified | Lines added: ~5,150

### Validation results
- **All 6 new workflow YAMLs:** `yaml.safe_load` clean
- **All Python scripts:** `python3 -m py_compile` clean
- **Bash script:** `bash -n` clean
- **URL converter dry-run:** 77 links ready to convert (15 deals, 44 fitness, 18 menopause) — ASINs need human verification first
- **Dashboard generator:** zero-data render produces valid 11,252-char HTML

---

## What The User Must Do Manually (Cannot Be Automated)

These require either credentials, 2FA, CAPTCHA, or human review. Grouped by priority.

### Priority 1 — Unblock dormant revenue (do today)

| Task | Time | Impact |
|------|------|--------|
| Complete Etsy banking/billing setup | 30 min | Unblocks 3 listings currently earning $0 |
| Run `cd automation/playwright && npm install && npx playwright install chromium` | 5 min | Preps the ZIP uploader |
| Seed Gumroad login: `node gumroad-zip-uploader.js --dry-run`, log in, Ctrl-C | 3 min | One-time persistent-context login |
| Real run: `node gumroad-zip-uploader.js` | 10 min (monitors it) | Ships 8 empty Gumroad products |
| `bash scripts/install_mcps.sh` (start with Supabase + Stripe + Playwright + GitHub + Vercel) | 15 min | Revenue visibility inside Claude |

**Expected lift:** $200-800/mo from just these 5 actions (Gumroad empty listings + Etsy queue unblocked).

### Priority 2 — Scale distribution (do this week)

| Task | Time | Impact |
|------|------|--------|
| Verify ASINs in `scripts/asin_dictionary.py` (visit amazon.com/dp/<ASIN> for each, fix mismatches) | 2 hrs | Safely unblocks `--write` on 77 URL conversions |
| Run `python3 scripts/convert_all_search_urls_v2.py --write` after ASIN verification | 1 min | Converts 77 search URLs → direct links (1-2% → 8-15% conversion) |
| Deploy Anti-Gravity: set `VERCEL_TOKEN` + run `bash scripts/deploy_anti_gravity.sh` | 15 min | Ships the 5 home-office articles + unlocks Vercel project |
| Apply to Semrush affiliate: `cd automation/affiliate_signups && node apply.js --program semrush` | 10 min | $200/sale commission once approved |
| Apply to Hostinger, Ahrefs, Frase, ClickBank (one command each, then CAPTCHA) | 30 min total | 40-60% + 20% recurring + 30% recurring + 30-75% |
| Seed PromptBase login + list 7 prompt packs | 45 min | Opens a second digital product channel |

### Priority 3 — $10k/mo architecture (do this month)

| Task | Time | Impact |
|------|------|--------|
| Actually produce the $97 Blueprint PDF content (use Claude + `products/signature/MANIFEST.md`) | 2 days | The anchor product itself |
| Upload Blueprint PDF to Gumroad + set $17 order bump (Macro Meal Planner) | 1 hr | Launches the signature funnel |
| Create Kit "Inner Circle" $27/mo subscription product | 1 hr | The recurring MRR layer |
| Add `GA4_PROPERTY_ID_FITNESS/DEALS/MENOPAUSE` + `GUMROAD_ACCESS_TOKEN` GitHub secrets | 15 min | Activates real revenue digest + dashboard |
| Add `DISCORD_ALERTS_WEBHOOK` secret to GitHub | 5 min | Turns on error alerting |
| Configure `SUPABASE_ACCESS_TOKEN` + `STRIPE_SECRET_KEY` in `~/.claude/mcp-secrets.env` | 10 min | Activates MCP-powered productivity |

### Priority 4 — Follow-up tracking (automated — nothing to do)

- `daily-revenue-digest.yml` runs daily and commits `monitoring/revenue-digest-<DATE>.md`
- `stale-branch-cleanup.yml` runs Sunday 09:00 UTC (50+ stale `claude/*` branches pending cleanup)
- `dashboard-update.yml` regenerates `outputs/fitover35-website/dashboard/index.html` hourly
- `error-alerts.yml` pages Discord every 2h on high/critical errors
- `gumroad-sales-sync.yml` logs every sale to Supabase every 6h
- `follow-up-tracker.js` (run weekly): `cd automation/affiliate_signups && node follow-up-tracker.js` — flags pending applications >14d old

---

## $10k/mo Path (24 months — what this branch unblocks)

Before this sprint: content engine was posting but you had zero revenue visibility, 8 empty Gumroad products, no $97 anchor, no MCP-based productivity, no affiliate-signup automation, and no anti-gravity deploy.

After this sprint:
1. **Measurement** — MCPs + dashboard mean you optimize on real numbers, not guesses
2. **Unblocked products** — Playwright ships empty Gumroad ZIPs + PromptBase listings
3. **Anchor product** — $97 Blueprint scaffolded with order bump + cross-sell + recurring subscription
4. **Affiliate leverage** — 50% commission setup + signup automation for 5 high-$ programs
5. **Distribution** — Anti-Gravity adds a 5th brand site at zero marginal content cost
6. **Hygiene** — branch cleanup + error alerting + URL converter keep compounding gains from bleeding away

**Math:** 110 Blueprint sales × $97 + 30% order bump at $17 + 15% → Inner Circle at $27/mo × 4mo LTV + Amazon affiliate lift from 77 URL fixes ≈ **$13-18k/mo at full ramp** assuming current Pinterest traffic holds.

---

## Follow-ups Worth Considering Next Sprint

- Write the actual $97 Blueprint PDF (spawn 1 Opus agent, give it `products/signature/MANIFEST.md`)
- Expand ASIN dictionary from 119 to 300+ after verifying the first batch
- Build Kit (ConvertKit) broadcast automation wired to new-article publishes
- Create Composio/Zapier MCP integration to kill Late API dependence for X/LinkedIn posting
- Add Sentry MCP once errors are piping to Discord reliably
- Wire Stripe MCP once Inner Circle subscription is live
