# CHANGES-SUMMARY

---

## Health System Overhaul (2026-02-16)

Resolved 3 CRITICAL errors and 3 WARNINGS that caused the system to report `unhealthy` status. Overhauled the self-healing and email notification systems.

### CRITICAL FIXES

| # | Error | File(s) Changed | Fix |
|---|-------|-----------------|-----|
| 1 | PGRST204: Missing `affiliate_products` column on `content_bank` | `database/migrations/2026-02-16-fix-critical-health-issues.sql` | Migration adds column with `ALTER TABLE content_bank ADD COLUMN IF NOT EXISTS affiliate_products JSONB DEFAULT '[]'` |
| 2 | PGRST100: Malformed filter `is.not.null` | `core/supabase_client.py:206` | Changed `.is_('video_script', 'not.null')` to `.not_.is_('video_script', 'null')` |
| 3 | 42703: Column `content_bank.brand_id` does not exist | `database/migrations/2026-02-16-fix-critical-health-issues.sql` | Migration adds `brand_id` column with sync trigger to keep `brand` and `brand_id` in sync |

### WARNING FIXES

| # | Warning | File(s) Changed | Fix |
|---|---------|-----------------|-----|
| 1 | `trend_discovery` dormant (873h) | `.github/workflows/trend-discovery.yml` | Updated cron to `0 6 * * *` (6:00 AM UTC daily) |
| 1 | `multi_platform_poster` dormant (858h) | `.github/workflows/content-engine.yml` | Updated cron to `0 14, 0 19, 0 0 * * *` (14:00, 19:00, 00:00 UTC) |
| 2 | High DB failure rate (18 in 24h) | `agents/content_brain.py`, `agents/video_factory.py`, `agents/trend_discovery.py`, `agents/analytics_collector.py`, `agents/self_improve.py` | Added try/except wrappers around all Supabase queries |

### OVERHAULS

**Self-Healing System** (`agents/self_healer.py` - NEW):
- Checks all agent statuses and database health
- Auto-fixes: re-triggers workflows, retries with exponential backoff
- Schema errors logged only (needs human review)
- Emails only after 10+ consecutive failures or critical agent down 48+ hours

**Email Notification System** (`core/notifications.py`):
- Added `should_send_alert()` with 10-failure threshold and 24h cooldown
- Added `send_critical_alert()` with formatted subject: `EMPIRE CRITICAL: [agent] failed 10x`
- Updated `agents/health_monitor.py` to use threshold-based alerts

**Health Monitor Workflow** (`.github/workflows/health-monitor.yml`):
- Changed from hourly to every 6 hours (`0 */6 * * *`)
- Added self-healer step after health check

### Database Changes

**Migration:** `database/migrations/2026-02-16-fix-critical-health-issues.sql` (run in Supabase SQL Editor)
- Adds `affiliate_products`, `brand_id`, and other missing content_bank columns
- Adds `consecutive_failures`, `last_notified_at`, `auto_heal_attempted`, `auto_heal_success` to health_checks
- Clears stale errors and reloads PostgREST schema cache

**Schema:** `database/schema.sql` - Added notification tracking columns to health_checks table

### All Files Changed

| File | Action |
|------|--------|
| `core/supabase_client.py` | Fixed `is.not.null` filter syntax |
| `core/notifications.py` | Added threshold-based notification functions |
| `agents/self_healer.py` | **NEW** - Self-healing agent |
| `agents/health_monitor.py` | Updated schedules and threshold-based alerts |
| `agents/content_brain.py` | Added try/except wrappers |
| `agents/video_factory.py` | Added try/except wrappers |
| `agents/trend_discovery.py` | Added try/except wrappers |
| `agents/analytics_collector.py` | Added try/except wrappers |
| `agents/self_improve.py` | Added try/except wrappers |
| `database/schema.sql` | Added health_checks notification columns |
| `database/migrations/2026-02-16-fix-critical-health-issues.sql` | **NEW** - All DB fixes |
| `.github/workflows/health-monitor.yml` | 6h cron, added self-healer step |
| `.github/workflows/trend-discovery.yml` | Updated cron to 6:00 AM UTC |
| `.github/workflows/content-engine.yml` | Updated cron to 14:00/19:00/00:00 UTC |
| `.github/workflows/system-health.yml` | Changed to 6h cron |

### Post-Deployment

1. Run `database/migrations/2026-02-16-fix-critical-health-issues.sql` in Supabase SQL Editor
2. Manually trigger `trend-discovery.yml` and `content-engine.yml` to clear dormant warnings
3. Monitor the next health-monitor run to confirm system reports healthy

---

# Previous Changes

---

# Quality Pivot v2 + Trending Discovery

**Branch:** `quality-pivot-v2` (merged) + `trending-discovery`
**Date:** 2026-02-05
**Purpose:** Transform over-engineered, $0-revenue system into quality content machine across 3 Pinterest brands, then add weekly trending topic discovery and article-per-pin generation

---

## 1. Files Changed, Created, Moved, or Archived

### New Files Created
| File | Purpose |
|------|---------|
| `video_automation/content_brain.py` | Claude-powered content generation for all 3 brands. Replaces Gemini. Handles uniqueness tracking, topic/angle/style/board/opener rotation. |
| `video_automation/image_selector.py` | Unique Pexels image fetching with no repeats per brand (last 50 pins) |
| `database/content_history_schema.sql` | Supabase SQL for `content_history` table — run in SQL Editor |
| `monetization/affiliate_config.json` | Placeholder affiliate links for fitness, deals, menopause brands |
| `.github/workflows/content-engine.yml` | Main event — generates and posts all 7 pins/day across 3 brands |
| `.github/workflows/fitness-articles.yml` | Daily fitover35 articles + Mon/Wed/Fri deals articles |
| `.github/workflows/system-health.yml` | Combined health check + self-healing + error alerts |
| `.github/workflows/weekly-maintenance.yml` | Weekly summary + cleanup + email report |
| `.github/workflows/emergency-alert.yml` | Dead man's switch — alerts if content engine down >24h |

### Files Modified
| File | Change |
|------|--------|
| `video_automation/cross_platform_poster.py` | Moved ALL hardcoded Pinterest account/board IDs to environment variables. Updated posting slots to 3+2+2 (7/day). |
| `outputs/fitover35-website/index.html` | Added GA4 tracking code (placeholder `GA_MEASUREMENT_ID`) |
| `outputs/fitover35-website/blog.html` | Added GA4 tracking code |
| `outputs/fitover35-website/about.html` | Added GA4 tracking code |
| `outputs/fitover35-website/contact.html` | Added GA4 tracking code |

### Workflows Archived (moved to `.github/workflows/archive/`)
| Workflow | Reason |
|----------|--------|
| `video-automation-morning.yml` | Replaced by `content-engine.yml` |
| `video-automation-noon.yml` | Replaced by `content-engine.yml` |
| `video-automation-evening.yml` | Replaced by `content-engine.yml` |
| `workflow-guardian.yml` | Overkill (ran every 30 min). Replaced by `system-health.yml` |
| `daily-report.yml` | Replaced by `weekly-maintenance.yml` |
| `error-alerts.yml` | Replaced by `system-health.yml` |
| `health-monitoring.yml` | Replaced by `system-health.yml` |
| `self-healing.yml` | Replaced by `system-health.yml` |
| `fitover35-blog-automation.yml` | Duplicate of `generate-fitover35-articles.yml`. Replaced by `fitness-articles.yml` |
| `generate-fitover35-articles.yml` | Replaced by `fitness-articles.yml` |
| `weekly-summary.yml` | Replaced by `weekly-maintenance.yml` |

### Dead Code Archived (moved to `archive/deprecated/`)
| File/Directory | Reason |
|----------------|--------|
| `monitoring/analytics_dashboard.py` | 417 lines, never imported or referenced |
| `video_automation/ab_testing.py` | 383 lines, A/B testing never integrated |
| `automation/affiliate/product_database.py` | 530 lines, in-memory dict never used |
| `youtube-automation/` (entire directory) | Orphaned pipeline, not referenced by any workflow |
| `tiktok_automation/` (entire directory) | Make.com schemas, not connected to Python code |

---

## 2. New GitHub Secrets Needed

Add these in **GitHub Repo Settings → Secrets and variables → Actions**:

| Secret Name | Description | Where to Get It |
|-------------|-------------|-----------------|
| `ANTHROPIC_API_KEY` | Claude API key (Sonnet 4.5 for content generation) | https://console.anthropic.com/settings/keys |
| `PINTEREST_FITNESS_ACCOUNT_ID` | Late API account ID for Fitness Made Easy | Late API dashboard (currently: `697bb4b893a320156c4221ab`) |
| `PINTEREST_FITNESS_BOARD_ID` | Default board ID for fitness pins | Pinterest board URL → numeric ID (currently: `756745612325868912`) |
| `PINTEREST_DEALS_ACCOUNT_ID` | Late API account ID for Daily Deal Darling | Late API dashboard (currently: `697ba20193a320156c4220b4`) |
| `PINTEREST_DEALS_BOARD_ID` | Default board ID for deals pins | Pinterest board URL → numeric ID (currently: `874683627569021288`) |
| `PINTEREST_MENOPAUSE_ACCOUNT_ID` | Late API account ID for Menopause Planner | Late API dashboard (currently: `697c329393a320156c422e6d`) |
| `PINTEREST_MENOPAUSE_BOARD_ID` | Default board ID for menopause pins | Pinterest board URL → numeric ID (currently: `1076993767079887530`) |
| `MAKE_WEBHOOK_DEALS` | Make.com Scenario 1 webhook URL for Daily Deal Darling pins | Make.com → Scenario 1 → Webhook trigger URL |
| `MAKE_WEBHOOK_MENOPAUSE` | Make.com Scenario 2 webhook URL for Menopause Planner pins | Make.com → Scenario 2 → Webhook trigger URL |
| `GA4_MEASUREMENT_ID` | Google Analytics 4 measurement ID | GA4 Admin → Data Streams → Measurement ID (format: G-XXXXXXXXXX) |

**Existing secrets to keep:** `LATE_API_KEY`, `LATE_API_KEY_3`, `PEXELS_API_KEY`, `CREATOMATE_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `RESEND_API_KEY`, `ALERT_EMAIL`, `CONVERTKIT_API_KEY`, `CONVERTKIT_API_SECRET`

**Secrets that can be removed:** `GEMINI_API_KEY` (no longer used — replaced by Claude), `LATE_API_KEY_2`, `LATE_API_KEY_4` (if not needed by content-engine)

---

## 3. New Supabase Tables/Columns

Run this SQL in **Supabase Dashboard → SQL Editor**:

```sql
CREATE TABLE IF NOT EXISTS content_history (
    id BIGSERIAL PRIMARY KEY,
    brand TEXT NOT NULL,
    title TEXT,
    description TEXT,
    topic TEXT,
    category TEXT,
    angle_framework TEXT,
    visual_style TEXT,
    board TEXT,
    description_opener TEXT,
    image_query TEXT,
    pexels_image_id TEXT,
    destination_url TEXT,
    pin_url TEXT,
    posting_method TEXT,  -- 'late_api', 'make_s1', 'make_s2'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_content_history_brand ON content_history(brand);
CREATE INDEX IF NOT EXISTS idx_content_history_created ON content_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_history_brand_created ON content_history(brand, created_at DESC);
```

The SQL file is also saved at `database/content_history_schema.sql`.

---

## 4. MAKE.COM MANUAL CONFIGURATION

### Scenario 1: Daily Deal Darling Pinterest Posting

1. **Open Make.com** → Dashboard → Scenarios
2. **Find the Daily Deal Darling scenario** (or create a new one)
3. **Set up Webhook trigger:**
   - Add a "Webhooks" module → "Custom webhook"
   - Copy the webhook URL → add as `MAKE_WEBHOOK_DEALS` GitHub Secret
   - The webhook will receive this JSON payload:
     ```json
     {
       "title": "Pin title from Claude",
       "description": "Pin description with keywords",
       "image_url": "https://images.pexels.com/photos/...",
       "destination_url": "https://dailydealdarling.com?utm_source=pinterest&utm_medium=make_s1&...",
       "board_name": "Kitchen Must-Haves",
       "text_overlay": "Short overlay text"
     }
     ```
4. **Add HTTP module** to download the image from `image_url`
5. **Add Pinterest module:**
   - Connect your **Daily Deal Darling Pinterest account**
   - Map fields: Title → `title`, Description → `description`, Link → `destination_url`
   - Upload the downloaded image
   - Board → use `board_name` from webhook (or map to specific board IDs)
6. **Remove any old content generation modules** (Gemini, text generators, etc.)
7. **Test:** Run the scenario manually with a test webhook payload
8. **Activate** the scenario

### Scenario 2: Menopause Planner Pinterest Posting

1. Follow the same steps as Scenario 1
2. Connect your **Menopause Planner Pinterest account**
3. Copy the webhook URL → add as `MAKE_WEBHOOK_MENOPAUSE` GitHub Secret
4. Same payload format as above
5. Test and activate

### Important Notes:
- All content (title, description, image selection) comes from Claude via the webhook — Make.com just receives and posts
- Do NOT add any content generation within Make.com scenarios
- Fitness pins do NOT use Make.com — they use Late API directly from GitHub Actions

---

## 5. Affiliate Program Signup TODO List

### Fitness (FitOver35)
- [ ] **ClickBank** — https://www.clickbank.com/affiliate/ — Browse fitness/health marketplace for programs paying 30-75% commission
- [ ] **ShareASale** — https://www.shareasale.com/ — Apply to: Transparent Labs, Legion Athletics, TRX, supplement brands
- [ ] **Bodybuilding.com Affiliate** — https://www.bodybuilding.com/affiliate — Supplements + programs at 5-15%

### Deals (Daily Deal Darling)
- [ ] **ShareASale** — https://www.shareasale.com/ — Home, kitchen, lifestyle brands
- [ ] **Impact** — https://impact.com/ — Major retail brands
- [ ] **Rakuten Advertising** — https://rakutenadvertising.com/ — Department stores, specialty retailers

### Menopause (The Menopause Planner)
- [ ] **ShareASale** — https://www.shareasale.com/ — Health/wellness supplement brands
- [ ] **ClickBank** — https://www.clickbank.com/affiliate/ — Health programs for women

### After Signup:
1. Replace `PLACEHOLDER` URLs in `monetization/affiliate_config.json` with actual affiliate links
2. Replace `PLACEHOLDER` URLs in `monetization/fitness_affiliates.py` with actual links
3. Update `fitover35.com/products.html` Gumroad links with real product URLs

---

## 6. New Workflow Schedule

| Workflow | Schedule | Purpose | Brands |
|----------|----------|---------|--------|
| `content-engine.yml` | 8 AM, 1 PM, 6 PM PST | Generate + post pins | All 3 |
| `fitness-articles.yml` | 11 PM PST Mon-Fri | SEO articles | Fitness daily, Deals Mon/Wed/Fri |
| `system-health.yml` | Every 6 hours | Health check + self-healing | N/A |
| `email-automation.yml` | 9 AM, 5 PM PST | Email sequences | All |
| `weekly-maintenance.yml` | Sunday 9 AM PST | Summary + cleanup | All |
| `emergency-alert.yml` | Midnight PST | Dead man's switch | N/A |
| `auto-merge.yml` | Push to claude/** | Auto-merge branches | N/A |

### Daily Pin Distribution
```
8 AM PST:  1x Fitness (Late API) + 1x Deals (Make.com S1) + 1x Menopause (Make.com S2) = 3 pins
1 PM PST:  1x Fitness (Late API) + 1x Deals (Make.com S1)                                = 2 pins
6 PM PST:  1x Fitness (Late API)                           + 1x Menopause (Make.com S2) = 2 pins
                                                                                     TOTAL = 7 pins/day
```

---

## 7. What the Owner Needs to Do Manually vs What's Automated

### Owner Must Do (One-Time Setup)
1. **Create `content_history` table** in Supabase (SQL provided above)
2. **Add new GitHub Secrets** (list in Section 2)
3. **Replace `GA_MEASUREMENT_ID`** in HTML files with actual GA4 property ID (or add as GitHub Secret for dynamic injection)
4. **Configure Make.com scenarios** (instructions in Section 4)
5. **Sign up for affiliate programs** (list in Section 5)
6. **Replace placeholder affiliate URLs** in config files
7. **Create Creatomate templates** for the 5 pin visual styles (IDs go in `content_brain.py` as `TEMPLATE_ID_1` through `TEMPLATE_ID_5`)
8. **Create Menopause Planner landing page/blog** (currently using Linktree placeholder) — Pinterest penalizes direct Etsy links
9. **Create Daily Deal Darling website** if it doesn't exist yet

### Automated After Setup
- All pin content generation (Claude API)
- Image selection (Pexels with uniqueness)
- Pin posting to all 3 Pinterest accounts
- Article generation for fitover35.com
- Health monitoring + self-healing
- Weekly summary reports
- Emergency alerts if system goes down
- Content uniqueness tracking in Supabase

---

## 8. Estimated Timeline to Results

| Milestone | Timeline | What Happens |
|-----------|----------|-------------|
| System live | Day 1-3 | Complete owner setup tasks, merge PR, content engine starts posting |
| Content quality visible | Week 1-2 | Pinterest algorithm starts seeing unique, quality content |
| Impressions increase | Week 2-4 | Pinterest rewards non-repetitive content with more distribution |
| Click-through rate improves | Week 3-6 | Curiosity-gap titles and quality descriptions drive clicks |
| Email list grows | Month 1-2 | 5-20+ signups/week from fitover35.com |
| Affiliate revenue begins | Month 1-3 | First commissions from high-commission programs |
| Meaningful revenue | Month 3-6 | $200-500/month possible at 1-2% CTR with 15-50% commissions |

---

## 9. Known Limitations and Next Steps

### Known Limitations
- **Creatomate template IDs** are placeholders (`TEMPLATE_ID_1` through `TEMPLATE_ID_5`) — owner must create templates and update IDs
- **Menopause Planner** has no website — using Linktree as placeholder. Pinterest penalizes direct product links.
- **Daily Deal Darling** website may not exist yet — needs blog/article pages for pin destinations
- **Affiliate links** are all placeholders — no revenue until owner signs up and replaces URLs
- **GA4 measurement ID** is placeholder — analytics won't work until replaced
- **Make.com webhooks** need manual configuration — can't be automated from code
- **Article generator** still uses Gemini for fitover35 (existing pipeline) — can be migrated to Claude later
- **Content engine** doesn't render via Creatomate yet — just generates content and posts images directly

### Recommended Next Steps
1. **Create Creatomate pin templates** — 5 visual styles (bold overlay, split layout, minimal number, editorial, list teaser) in 1000x1500 Pinterest dimensions
2. **Build Menopause Planner blog** — even a simple single-page blog with articles would dramatically improve Pinterest performance
3. **Build Daily Deal Darling blog** — article pages with affiliate product recommendations
4. **Set up ConvertKit email sequences** for each brand
5. **Monitor Pinterest Analytics** weekly — adjust topics/styles based on what gets clicks
6. **Add Creatomate rendering** to content-engine.yml once templates are ready
7. **Migrate fitover35 article generation** from Gemini to Claude API

### Cost Projection
| Item | Before | After (with trending discovery) |
|------|--------|-------|
| Claude API (Sonnet 4.5) | $0 | $15-30/mo |
| Gemini API | $5-10/mo | $0 (removed) |
| Creatomate renders | $45-90/mo | $20-40/mo |
| Make.com | $16/mo | $16/mo |
| Other | ~$10/mo | ~$10/mo |
| **TOTAL** | **$76-126/mo** | **$61-96/mo** |

---

## 10. Trending Discovery System (Branch: `trending-discovery`)

### How the Weekly Cycle Works

```
Sunday 10 PM PST (weekly-discovery.yml):
  1. DISCOVER — Find what's trending in each niche this week
     - Google Trends API (pytrends) — rising/surging search terms
     - Pinterest trend analysis via Claude — what's popular on Pinterest now
     - Web trend synthesis via Claude — news, seasonal, viral content
     - Claude filters, deduplicates, ranks → selects top 5 topics per brand

  2. PLAN — Build a 7-day content calendar per brand
     - Maps each trending topic to specific daily pin assignments
     - Assigns pin types (static, infographic, carousel), boards, title ideas
     - Each pin gets an article_slug for its destination URL
     - Stored in Supabase weekly_calendar table as JSONB

  3. GENERATE ARTICLES — Create SEO articles for every trending topic
     - Each article: 1,200-1,800 words, SEO-optimized, with brand voice
     - Includes email capture CTA, 2-3 affiliate product recommendations
     - Published as Markdown files to brand website directories
     - Committed + pushed to GitHub for deployment

Monday-Sunday (content-engine.yml, 3x daily):
  4. EXECUTE — Content engine pulls from weekly calendar
     - generate_pin_from_calendar() reads today's assignments from Supabase
     - Each pin links to its matching article (not homepage)
     - Falls back to random topic selection if no calendar exists
     - All uniqueness checks still apply

Next Sunday (before new discovery):
  5. REVIEW — Check last week's performance
     - Which topics got posted, which didn't
     - Future: Pinterest analytics integration for click data
     - Feeds insights into next week's topic selection
```

### New Files Created
| File | Purpose |
|------|---------|
| `video_automation/trend_discovery.py` | Trend discovery engine: Google Trends + Pinterest + web analysis via Claude. Fallback evergreen topics. Weekly calendar builder. |
| `video_automation/article_generator.py` | SEO article generator for each trending topic. Includes affiliate CTAs, email capture, image placeholders. |
| `database/weekly_calendar_schema.sql` | New Supabase tables: `weekly_calendar`, `generated_articles` + new columns on `content_history` |
| `.github/workflows/weekly-discovery.yml` | Sunday 10 PM PST workflow: discover trends, generate articles, commit + push |

### Files Modified
| File | Change |
|------|--------|
| `video_automation/content_brain.py` | Added `generate_pin_from_calendar()` function — reads weekly calendar from Supabase, generates calendar-driven pins with article destination URLs, falls back to random if no calendar |
| `.github/workflows/content-engine.yml` | Updated to call `generate_pin_from_calendar()` first, falls back to `generate_pin_content()` if calendar exhausted |
| `requirements.txt` | Added `pytrends>=4.9.0` for Google Trends API |

### New Supabase Tables (run AFTER content_history_schema.sql)

Run `database/weekly_calendar_schema.sql` in **Supabase Dashboard → SQL Editor**:

```sql
-- Weekly content calendars built from trend discovery
CREATE TABLE IF NOT EXISTS weekly_calendar (
    id BIGSERIAL PRIMARY KEY,
    brand TEXT NOT NULL,
    week_starting DATE NOT NULL,
    calendar_data JSONB NOT NULL,
    trends_data JSONB,
    performance_review JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_weekly_calendar_brand ON weekly_calendar(brand);
CREATE INDEX IF NOT EXISTS idx_weekly_calendar_week ON weekly_calendar(week_starting DESC);

-- Generated articles for trending topics
CREATE TABLE IF NOT EXISTS generated_articles (
    id BIGSERIAL PRIMARY KEY,
    brand TEXT NOT NULL,
    slug TEXT NOT NULL,
    trending_topic TEXT,
    content_preview TEXT,
    word_count INTEGER,
    published_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_articles_brand ON generated_articles(brand);
CREATE INDEX IF NOT EXISTS idx_articles_slug ON generated_articles(slug);

-- Add trending topic tracking to content_history
ALTER TABLE content_history ADD COLUMN IF NOT EXISTS trending_topic TEXT;
ALTER TABLE content_history ADD COLUMN IF NOT EXISTS week_calendar_id BIGINT;
```

### New Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| `pytrends` | >=4.9.0 | Google Trends API wrapper for trending topic discovery |

No new GitHub Secrets are needed beyond what's already configured.

### How to Manually Trigger Trend Discovery

1. Go to **GitHub Actions** → **Weekly Trend Discovery + Content Planning**
2. Click **Run workflow** → **Run workflow** (uses `workflow_dispatch`)
3. This will discover trends, build calendars, and generate articles for all 3 brands
4. Check the workflow logs to see which trending topics were selected

### Updated Workflow Schedule

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| `weekly-discovery.yml` | **Sunday 10 PM PST** | Discover trends, plan week, generate articles |
| `content-engine.yml` | 8 AM, 1 PM, 6 PM PST | Generate + post pins (now calendar-aware) |
| `fitness-articles.yml` | 11 PM PST Mon-Fri | SEO articles |
| `system-health.yml` | Every 6 hours | Health check + self-healing |
| `weekly-maintenance.yml` | Sunday 9 AM PST | Summary + cleanup |
| `emergency-alert.yml` | Midnight PST | Dead man's switch |

### Graceful Degradation

The system never stops posting, even if trend discovery completely fails:

1. **Google Trends fails** → Pinterest + web analysis via Claude still work
2. **All trend sources fail** → Evergreen fallback topics are used (hardcoded per brand)
3. **Calendar build fails** → Content engine falls back to random topic selection from `content_brain.py` topic banks
4. **Article generation fails for a topic** → Pin still posts, just links to homepage instead of article
5. **Weekly discovery workflow doesn't run** → Content engine continues with random topics (same as before this change)

### Claude API Cost Increase

The weekly discovery adds ~$8-18/month in Claude API calls:

| Component | Calls/Week | Est. Cost/Week |
|-----------|-----------|----------------|
| Trend discovery (3 brands x 3 sources) | 9 calls | $0.50-1.00 |
| Trend ranking + filtering (3 brands) | 3 calls | $0.30-0.60 |
| Calendar building (3 brands) | 3 calls | $0.30-0.60 |
| Article generation (~12-15 articles) | 12-15 calls | $3.00-6.00 |
| **Weekly total** | ~30 calls | **$4.10-8.20** |
| **Monthly total** | ~120 calls | **$16-33** |

### Owner Manual Steps for Trending Discovery

1. **Run `weekly_calendar_schema.sql`** in Supabase SQL Editor (required before first run)
2. **Manually trigger** the weekly-discovery workflow once to verify it works
3. **Check Supabase** `weekly_calendar` table to confirm calendars were created
4. **Check article output directories** (`outputs/fitover35-website/articles/`, etc.) for generated articles
5. **Configure Menopause Planner landing page** — articles are generated but need a website to host them
