# CHANGES-SUMMARY — Quality Pivot v2

**Branch:** `quality-pivot-v2`
**Date:** 2026-02-05
**Purpose:** Transform over-engineered, $0-revenue system into quality content machine across 3 Pinterest brands

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
| Item | Before | After |
|------|--------|-------|
| Claude API (Sonnet 4.5) | $0 | $5-12/mo |
| Gemini API | $5-10/mo | $0 (removed) |
| Creatomate renders | $45-90/mo | $20-40/mo |
| Make.com | $16/mo | $16/mo |
| Other | ~$10/mo | ~$10/mo |
| **TOTAL** | **$76-126/mo** | **$51-78/mo** |
