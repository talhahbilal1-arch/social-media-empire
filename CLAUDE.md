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
| `MAKE_WEBHOOK_FITNESS` | Make.com webhook — fitness brand |
| `MAKE_WEBHOOK_DEALS` | Make.com webhook — deals brand |
| `MAKE_WEBHOOK_MENOPAUSE` | Make.com webhook — menopause brand |
| `VERCEL_BRAND_TOKEN` | Vercel deploy (personal access token) |
| `VERCEL_FITOVER35_PROJECT_ID` | Vercel project ID for fitover35 |
| `VERCEL_DEALS_PROJECT_ID` | Vercel project ID for deals |
| `VERCEL_MENOPAUSE_PROJECT_ID` | Vercel project ID for menopause |

## Brand Key Convention

Python code uses short keys: `fitness`, `deals`, `menopause`
Make.com payload uses hyphenated names: `fitness-made-easy`, `daily-deal-darling`, `menopause-planner`

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

## Make.com Scenario

- **ID**: 3977247 | **Webhook hook ID**: 1802056
- **URL** (all brands): `https://hook.us2.make.com/8d51h67qpdt77jgz5brhvd5c9hgvaap8`
- Routes by `brand` field in payload → brand-specific Pinterest connection
- Board ID provided dynamically in payload (`board_id` field)

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
- **Pinterest posting**: Active — 5x daily (6AM, 9AM, 12PM, 3PM, 7PM PST), 5 pins/brand/day (15 total)
- **All workflows**: Green — content engine, rescue poster, social distribution all active
- **Content generated**: 400+ articles across 3 brands (333 articles indexed in sitemaps)
- **Affiliate tags**: FIXED — fitness=fitover3509-20, deals/menopause=dailydealdarl-20. All 144 fitness articles corrected.
- **Google Analytics**: All articles now have brand-specific GA tracking (G-1FC6FH34L9, G-HVCLZPEYNS, G-02ZPS3H3GC)
- **Email capture**: Kit forms working on all 3 brand sites with correct form IDs (8946984, 9144859, 9144926)
- **FitOver35**: Live on Vercel with schema markup, sticky CTA, lead magnet page, correct affiliate tags
- **DDD**: Live on Netlify with email capture, correct GA tracking
- **Gumroad products**: All listed — AI Fitness Vault ($27), Pinterest Blueprint ($47), Bundle ($87)
- **Social distribution**: Weekly workflow generates Reddit/Twitter content from latest articles
- **Make.com**: 9 active scenarios healthy
- **Content quality improvements**: Enhanced Gemini prompts (stronger CTAs, quick verdict box, related articles), internal linking automation, comprehensive sitemap updates (333 articles indexed), og:image tags added
- **PilotTools**: Expanded to 35 tools, 29 comparisons, 25 articles. Affiliate tracker created.
- **Product funnels**: Bundle landing page + 3 product pages deployed. Product CTAs injected into article templates.
- **Anti-Gravity**: 5 home office articles created (11,724 words). Site pending Vercel deploy.
- **Distribution**: SEO ping system + GitHub Action, 20 Pinterest product pins, Reddit/Twitter content generated
- **Make.com**: 29 dead scenarios DELETED. 9 active scenarios remain, all healthy (0 errors).
- **Revenue dashboard**: Created at outputs/fitover35-website/dashboard/index.html
- **Last session**: March 31, 2026 — Overnight revenue activation (7-agent execution)

## Active Priorities (April 2026)
1. Sign up for top affiliate programs — Semrush ($200/sale), Grammarly, Ahrefs, Hostinger (see PHONE-ACTION-CHECKLIST.md)
2. Deploy Anti-Gravity home office site to Vercel
3. Post distribution content from distribution/weekly-posts/
4. Monitor GA4 for Pinterest traffic across all brands
5. Desmond Wong creator services — delivering free short-form + website
6. QuantConnect trading algo — on hold until $1K/month online revenue achieved

## Known Issues
- Schema-code mismatches have occurred (missing columns, malformed PostgREST filters)
- Affiliate tags cross-contamination: FIXED March 31, 2026 (code + 144 articles corrected)
- Late API keys expired — video pin posting via Late returns 401. Refresh at getlate.dev
- Etsy shop onboarding still needs banking/billing setup (manual)
- Make.com: CLEANED UP — 29 dead scenarios deleted March 31, 2026
- Phase 13 work stashed — run `git stash pop` to restore

## Development Rules
- NEVER commit API keys or secrets
- Auto-checkpoint hooks are active — commits happen automatically
- Always git pull before starting work on any device
- When session ends, update the "Current Status" section of this file before closing
- Use conventional commit messages for manual commits (feat:, fix:, refactor:)
