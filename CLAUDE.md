# CLAUDE.md - Social Media Empire Project Context

## Project Overview

Automated Pinterest content system for 3 lifestyle brands. Generates pin content via Claude (Sonnet),
renders images with PIL, uploads to Supabase Storage, and posts to Pinterest via Make.com webhooks.
15 pins/day total (5 per brand × 3 brands × 5 daily runs).

## Active Brands (3 only)

| Brand key | Site | Niche | Pins/day |
|-----------|------|-------|----------|
| `fitness` | fitover35.com | Men's fitness over 35 | 5 |
| `deals` | dailydealdarling.com | Budget home & lifestyle | 5 |
| `menopause` | menopause-planner-website.vercel.app | Menopause wellness | 5 |

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
| `ANTHROPIC_API_KEY` | Claude API |
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

## Active GitHub Workflows (9)

1. `content-engine.yml` — 5x daily pin + article + deploy pipeline
2. `weekly-discovery.yml` — Sunday 10PM PST trend discovery
3. `fitness-articles.yml` — FitOver35 article generation
4. `system-health.yml` — 6-hourly self-healing + DB maintenance
5. `email-automation.yml` — ConvertKit email sequences
6. `weekly-maintenance.yml` — Sunday cleanup + DB vacuum
7. `emergency-alert.yml` — Critical failure alerts
8. `auto-merge.yml` — Auto-merge passing PRs
9. `toolpilot-deploy.yml` — ToolPilot AI directory deploy

## Common Issues & Fixes

- **`severity` column missing in errors**: Run `database/migrations/001_master_schema.sql`
- **Pins not posting**: Check Make.com scenario is ON; verify per-brand webhook secrets
- **Font download crash**: Fixed in `pin_image_generator.py` — returns None gracefully
- **Article timeout**: 3 articles via Claude ~15-20 min; workflow timeout is 45 min
- **Supabase new tables**: Always `GRANT ALL` + disable RLS + restart project (5-8 min)
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
