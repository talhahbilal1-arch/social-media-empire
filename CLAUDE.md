# Execution Instructions
You are to execute all work directly. No planning stage. Just do it.

**Workflow:**
1. Read the codebase to understand context
2. Write a plan to tasks/todo.md (internal planning only)
3. Ask user to verify the plan
4. Execute the plan and check off items as you go
5. Provide high-level explanations of changes
6. Add review section to tasks/todo.md with summary

Keep all changes simple, focused, and minimal. No lazy fixes or temporary solutions.

Automated Pinterest content system for 3 lifestyle brands. Generates pin content via Claude (Sonnet),
renders images with PIL, uploads to Supabase Storage, and posts to Pinterest via Make.com webhooks.
15 pins/day total (5 per brand x 3 brands x 5 daily runs).

## Active Brands (3 only)

| Brand key | Site | Niche | Pins/day | Amazon Tag |
|-----------|------|-------|----------|------------|
| `fitness` | fitover35.com | Men's fitness over 35 | 5 | fitover3509-20 |
| `deals` | dailydealdarling.com | Budget home & lifestyle | 5 | dailydealdarl-20 |
| `menopause` | menopause-planner-website.vercel.app | Menopause wellness | 5 | dailydealdarl-20 |

## Pipeline Architecture (content-engine.yml — 5x daily)

```
Phase 0: Pre-flight check (scripts/preflight_check.py) — validate secrets, connectivity
Phase 1: Generate pin content (Claude API) → brand topic + title + tips + image query
Phase 2: Generate article per pin (Claude API) → 800-1200 word SEO article
Phase 3: Git commit + push articles → deploys to Vercel brand sites
Phase 4: Render PIL image → upload Supabase Storage → post via Make.com webhook
```

## Key Files

| File | Purpose |
|------|---------|
| `video_automation/content_brain.py` | Claude API generates all pin content (Sonnet 4.5) |
| `video_automation/pin_image_generator.py` | PIL renders 1000x1500 overlay images |
| `video_automation/pin_article_generator.py` | Claude generates 800-1200 word SEO articles |
| `video_automation/image_selector.py` | Unique Pexels images per brand |
| `video_automation/pinterest_boards.py` | Board ID mappings per brand |
| `video_automation/supabase_storage.py` | Upload/cleanup pin images in Supabase Storage |
| `video_automation/trend_discovery.py` | Weekly trend discovery (Google Trends + Claude) |
| `scripts/preflight_check.py` | Pre-flight secret/API validation |
| `database/migrations/001_master_schema.sql` | Consolidated idempotent master schema |
| `.github/workflows/content-engine.yml` | Main 5x-daily pipeline workflow |
| `.github/workflows/weekly-discovery.yml` | Sunday trend discovery |

## GitHub Secrets Required

| Secret | Purpose |
|--------|---------|
| `GEMINI_API_KEY` | Google Gemini API (primary AI — gemini-2.5-flash) |
| `PEXELS_API_KEY` | Background images |
| `SUPABASE_URL` | Database |
| `SUPABASE_KEY` | Database |
| `MAKE_WEBHOOK_FITNESS` | Make.com webhook — fitness brand (optional if `MAKE_WEBHOOK` is set) |
| `MAKE_WEBHOOK_DEALS` | Make.com webhook — deals brand (optional if `MAKE_WEBHOOK` is set) |
| `MAKE_WEBHOOK_MENOPAUSE` | Make.com webhook — menopause brand (optional if `MAKE_WEBHOOK` is set) |
| `MAKE_WEBHOOK` | Unified Make.com webhook — used as fallback when a brand-specific webhook is empty. The unified scenario routes by the hyphenated `brand` field in the payload. |
| `VERCEL_BRAND_TOKEN` | Vercel deploy (personal access token) |
| `VERCEL_FITOVER35_PROJECT_ID` | Vercel project ID for fitover35 |
| `VERCEL_DEALS_PROJECT_ID` | Vercel project ID for deals |
| `VERCEL_MENOPAUSE_PROJECT_ID` | Vercel project ID for menopause |

## Brand Key Convention

Python code uses short keys: `fitness`, `deals`, `menopause`.

Make.com webhook payload uses **hyphenated slugs**: `fitness-made-easy`,
`daily-deal-darling`, `menopause-planner`. Route filters inside Make.com compare
against this hyphenated field — sending the short key causes filtered routes to
silently drop the pin. The content-engine Phase 1b payload maps short key →
hyphenated slug before POSTing; the original short key is also included as
`brand_key` for any legacy consumers.

## Supabase Projects (CRITICAL — two separate projects)

- **Production** (`epfoxpgrpsnhlsglxvsa`): ALL workflow tables — content_history, errors, agent_runs,
  daily_trending, generated_articles, weekly_calendar, pinterest_pins, etc.
  GitHub secrets (`SUPABASE_URL` / `SUPABASE_KEY`) point here.
- **Secondary** (`bjacmhjtpkdcxngkasux`): TikTok tables only (tiktok_queue, tiktok_analytics).
  Do NOT create workflow tables here.

## Supabase Table: Key Columns

- `errors`: requires `severity` VARCHAR(20) DEFAULT 'medium' — run `001_master_schema.sql` if missing
- `content_history`: requires `trending_topic`, `status` columns — included in migration
- `agent_runs`: unique on `agent_name` — upserted on every pipeline run

## Make.com Scenarios (per-brand + unified fallback)

Two posting paths exist. The content engine tries the brand-specific webhook
first, then falls back to the unified one.

**Per-brand dedicated scenarios** (no filter — each has its own Pinterest OAuth):
- Fitness v3 — secret `MAKE_WEBHOOK_FITNESS`
- Deals v4 — secret `MAKE_WEBHOOK_DEALS`
- Menopause v4 — secret `MAKE_WEBHOOK_MENOPAUSE`

**Unified fallback scenario** (router + per-route filter on the `brand` field):
- Secret `MAKE_WEBHOOK`
- Filter: `brand == "fitness-made-easy"` | `"daily-deal-darling"` | `"menopause-planner"`
- Board ID provided dynamically in payload (`board_id` field)

If a brand's dedicated scenario is disabled/broken, set `MAKE_WEBHOOK` and the
content engine will automatically fall back to it without code changes.

## PIL Pin Image Styles (5 overlays)

| Style | Description |
|-------|-------------|
| `gradient` | Black gradient bottom 60%, white bold text |
| `box_dark` | Dark semi-transparent box, centered text |
| `numbered_list` | Numbered items with accent circles |
| `big_stat` | Large number/percentage + supporting text |
| `split_layout` | Top 60% image, bottom 40% brand-color block |

## Vercel Brand Sites

- fitover35.com → `outputs/fitover35-website/` (articles/, index.html, blog.html)
- dailydealdarling.com → `outputs/dailydealdarling-website/`
- menopause-planner-website.vercel.app → `outputs/menopause-planner-website/`

## Active GitHub Workflows (35 active, 24 archived)

### Core Pipeline (daily)
1. `content-engine.yml` — 5x daily pin + article + deploy pipeline (6/9/12/3/7 PM UTC)
2. `fitness-articles.yml` — Mon-Fri article generation (7AM UTC)
3. `daily-trend-scout.yml` — Daily trend scouting (1PM UTC)
4. `daily-analytics.yml` — Daily analytics collection (2PM UTC)
5. `analytics-collector.yml` — Analytics data (11PM UTC)
6. `pin-watchdog.yml` — Every 2h safety net for pin generation
7. `enable-and-run.yml` — Daily workflow re-enabler (1PM UTC)
8. `emergency-alert.yml` — Dead man's switch (8AM UTC)
9. `revenue-intelligence.yml` — Daily revenue analysis (3PM UTC)

### Weekly
10. `weekly-discovery.yml` — Sunday 10PM PST trend discovery
11. `weekly-summary.yml` — Sunday weekly report
12. `social-distribution.yml` — Monday social content distribution
13. `seo-ping.yml` — Monday SEO ping
14. `check-affiliate-links.yml` — Monday affiliate link check
15. `post-product-pins.yml` — Mon/Thu product pins
16. `seo-content-machine.yml` — Mon/Wed/Fri SEO articles
17. `menopause-newsletter.yml` — Wednesday newsletter
18. `revenue-activation.yml` — Monday revenue team
19. `self-improve.yml` — Sunday self-optimization
20. `weekly-health-report.yml` — Monday workflow health report (4PM UTC)

### PilotTools
21. `toolpilot-content.yml` — Mon-Fri daily content (6AM UTC)
22. `toolpilot-pinterest.yml` — 2x daily pins (4PM/10PM UTC)
23. `toolpilot-twitter.yml` — 3x daily tweets
24. `toolpilot-linkedin.yml` — Mon/Wed/Fri LinkedIn posts
25. `toolpilot-repurpose.yml` — Daily content repurposing
26. `toolpilot-weekly.yml` — Monday trend discovery
27. `toolpilot-newsletter.yml` — Monday newsletter
28. `toolpilot-outreach.yml` — Monday backlink outreach
29. `toolpilot-report.yml` — Sunday weekly report

### Event-Driven (no schedule)
30. `toolpilot-deploy.yml` — PilotTools deploy (push to main)
31. `deploy-brand-sites.yml` — Brand site deploy (manual/callable)
32. `subdomain-deploy.yml` — Subdomain deploy (push to main)
33. `auto-merge.yml` — Auto-merge PRs (push)
34. `article-guard.yml` — Article format validation (push)
35. `regenerate-articles.yml` — Manual article regeneration

Full report: `monitoring/workflow-health.md` (auto-updated weekly)

## Common Issues & Fixes

- **`severity` column missing in errors**: Run `database/migrations/001_master_schema.sql`
- **Pins not posting**: Check Make.com scenario is ON; verify per-brand webhook secrets
- **Font download crash**: Fixed in `pin_image_generator.py` — returns None gracefully
- **Article timeout**: 3 articles via Claude ~15-20 min; workflow timeout is 45 min
- **Supabase new tables**: Always `GRANT ALL` + **ENABLE RLS** (not disable — service_role bypasses RLS, anon is blocked) + restart project (5-8 min)
- **Python**: Use `python3`, not `python` (macOS default)
- **Workflow git push**: Needs `permissions: contents: write`

## Code Patterns

### Database
```python
from database.supabase_client import get_supabase_client
db = get_supabase_client()
db.client.table('content_history').insert({...}).execute()
```

### Content Generation
```python
from video_automation.content_brain import generate_pin_content, log_pin_to_history
pin_data = generate_pin_content('fitness', db.client)
log_pin_to_history(pin_data, db.client)
```

### Error Logging
```python
db.client.table('errors').insert({
    'error_type': 'content_engine',
    'error_message': str(e),
    'context': json.dumps({'brand': brand}),
    'severity': 'high',  # REQUIRED — column exists after migration
    'created_at': datetime.now(timezone.utc).isoformat()
}).execute()
```

## Testing

```bash
# Syntax check
python3 -m py_compile video_automation/content_brain.py
python3 -m py_compile video_automation/pin_image_generator.py
python3 -m py_compile scripts/preflight_check.py

# Validate workflow YAML
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/content-engine.yml'))"

# Dry run (no posting)
# Trigger content-engine workflow with dry_run=true in GitHub Actions UI
```

## Deployment Checklist (after fresh setup)

1. Run `database/migrations/001_master_schema.sql` in Supabase SQL Editor
2. Restart Supabase project (Settings > General) — wait 5-8 min
3. Set all GitHub secrets (see table above)
4. Verify Make.com scenario "Pinterest Pin Publisher - All Brands" is ON
5. Trigger content-engine.yml manually with `dry_run=true` to validate

## Current Status
<!-- UPDATE THIS AFTER EVERY WORK SESSION — just tell Claude "update CLAUDE.md status" -->
- **AI API**: Gemini (gemini-2.5-flash) — migrated from 2.0-flash before June 1 deprecation. Paid tier enabled.
- **Pinterest posting**: Active — 3x daily (7AM, 3PM, 8PM PST), 3 pins/brand/day (9 total), 50% video mix, 90-pin dedup window, 8 trending topics/brand/day
- **All workflows**: Green — content engine, rescue poster, social distribution all active
- **Content generated**: 438 articles across 3 brands (412 indexed in sitemaps) — 186 fitness, 123 DDD, 103 menopause
- **Buyer-intent articles**: 20 new high-intent articles added April 21 (7 fitness, 7 DDD, 6 menopause) targeting "Best X for Y", "X vs Y", "Top X" keywords
- **Affiliate links**: CLEAN — 0 duplicate tags, 0 wrong tags, 0 missing tags. 1106 direct /dp/ links, 672 search URLs remaining.
- **ASIN dictionaries**: Generator expanded from 32 to 154 products. Fix scripts have 421+ entries total.
- **Google Analytics**: All articles have brand-specific GA tracking (G-1FC6FH34L9, G-HVCLZPEYNS, G-02ZPS3H3GC)
- **Email capture**: Kit forms working on all 3 brand sites with correct form IDs (8946984, 9144859, 9144926)
- **Internal links**: 363/373 articles have Related Articles sections (97%)
- **Gumroad products**: 4 professional PDFs built — AI Fitness Vault, Pinterest Blueprint, AI Coach Machine, Free Lead Magnet
- **Gumroad/Etsy CTAs**: Added to 49 articles total — 15 fitness (AI Vault + Free Prompts), 15 DDD (Free Prompts), 19 menopause (Etsy Planner + Free Prompts)
- **Make.com**: 9 active scenarios healthy
- **Revenue dashboard**: Created at outputs/fitover35-website/dashboard/index.html
- **Sitemaps**: Regenerated all 3 — 189 URLs (fitness), 127 URLs (DDD), 108 URLs (menopause). robots.txt verified for all sites.
- **Last session**: April 25, 2026 — Overnight sprint (8-phase autonomous run). Pushed 16 commits + merged PRs #32 (DDD AdSense) and #33 (Menopause AdSense). Diagnosed 14 failed content-engine runs — root cause was the unpushed fix for "0 pins" health-check exit; resolved by Phase 1 push. Built PilotTools `/reviews/` section (5 hands-on tool reviews, 8350 words, JSON-LD Review schema, sitemap 470→476). Optimized 10 affiliate articles (4 fitness/3 menopause/3 DDD) with 8 conversion changes each. Sales pins workflow: deps + Pexels-retry fixes deployed but blocked by Supabase transient timeouts — re-trigger when network is healthier. Launchd jobs (videogen exit 78, videopipeline exit 2): root cause = macOS Full Disk Access for `/usr/bin/python3` and `/bin/bash` accessing `~/Desktop/`. menopauseplanner.com → 000 (DNS unconfigured). See `tasks/OVERNIGHT_REPORT_2026-04-25.md` for full details.

## Active Priorities (April 2026)
1. Sign up for top affiliate programs — Semrush ($200/sale), Grammarly, Ahrefs, Hostinger (see PHONE-ACTION-CHECKLIST.md)
2. Deploy Anti-Gravity home office site to Vercel
3. Post distribution content from distribution/weekly-posts/
4. Monitor GA4 for Pinterest traffic across all brands
5. Desmond Wong creator services — delivering free short-form + website
6. QuantConnect trading algo — on hold until $1K/month online revenue achieved

## Known Issues
- Schema-code mismatches have occurred (missing columns, malformed PostgREST filters)
- Affiliate tags: CLEAN as of April 21, 2026. 0 duplicate tags, 0 wrong tags across all 438 articles.
- Late API keys expired — video pin posting via Late returns 401. Refresh at getlate.dev
- Etsy shop onboarding still needs banking/billing setup (manual)
- 672 search URLs remain — these are long article-title queries that don't map to single products
- Phase 13 work stashed — run `git stash pop` to restore

## Development Rules
- NEVER commit API keys or secrets
- Auto-checkpoint hooks are active — commits happen automatically
- Always git pull before starting work on any device
- When session ends, update the "Current Status" section of this file before closing
- Use conventional commit messages for manual commits (feat:, fix:, refactor:)
