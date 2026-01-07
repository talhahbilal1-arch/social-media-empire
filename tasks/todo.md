# Social Media Empire - Setup Checklist

Last Updated: January 6, 2026

---

## COMPLETED

### Infrastructure
- [x] All 8 agents built (Python files in /agents folder)
- [x] All 8 GitHub workflows created (.github/workflows)
- [x] Database schema created (database/schema.sql)
- [x] Code pushed to GitHub: https://github.com/talhahbilal1-arch/social-media-empire
- [x] Database tables created in Supabase (15+ tables)

### GitHub Secrets (All 10 Configured)
- [x] SUPABASE_URL
- [x] SUPABASE_KEY
- [x] ANTHROPIC_API_KEY
- [x] ALERT_EMAIL_FROM
- [x] ALERT_EMAIL_PASSWORD
- [x] ALERT_EMAIL_TO
- [x] CREATOMATE_API_KEY
- [x] NETLIFY_API_TOKEN
- [x] NETLIFY_SITE_ID
- [x] YOUTUBE_API_KEY

### Workflows Tested & Passing
- [x] Health Monitor - PASSED (28s)
- [x] Content Brain - PASSED (3m 26s)
- [x] Trend Discovery - PASSED (1m 3s, found 22 trends)
- [x] Video Factory - PASSED (34s)
- [x] Blog Factory - PASSED (1m 56s)
- [x] Analytics Collector - PASSED (27s)
- [x] Self-Improvement - PASSED (29s)
- [x] Multi-Platform Poster - Created (awaiting first run)

### Database Data
- [x] brands table: 2 brands (Daily Deal Darling, The Menopause Planner)
- [x] trending_discoveries table: 22 trends
- [x] pinterest_pins table: 37 pins

### External Services
- [x] Netlify: dailydealdarling.com connected
- [x] Creatomate: Account configured with templates
- [x] YouTube Data API v3: Enabled
- [x] Make.com: Pinterest scenarios running (398+ executions)

---

## CRITICAL AUDIT - January 6, 2026

### Audit 1: Blog Factory Affiliate Links & SEO
**Status:** FIXED
**Issues Found:**
- Blog Factory was NOT adding affiliate tags to Amazon links
- No internal links to quiz pages
- affiliate_products had asin="unknown"

**Fixes Applied:**
- Added `_add_affiliate_links()` method to `blog_factory.py` - transforms all Amazon URLs to include `?tag=dailydealdarling1-20`
- Added `_add_internal_links()` method - adds quiz page links and related posts
- Added `quiz_links` config for both brands in BRAND_CONFIG

### Audit 2: Blog Publishing to Netlify
**Status:** FIXED
**Issues Found:**
- dailydealdarling.com/blog showing 404
- blog_articles table has 2 records but `published_at` is NULL
- Netlify Deploy API was incorrectly replacing entire site with single file

**Fixes Applied:**
- Rewrote `netlify_client.py` to preserve existing files when deploying
- Now fetches current production deploy files first
- Creates deploy with ALL files (existing + new)
- Only uploads new file content

### Audit 3: Two Pinterest Accounts Separation
**Status:** VERIFIED OK
**Findings:**
- Daily Deal Darling: Amazon affiliate (beauty, home, lifestyle)
- The Menopause Planner: Etsy + Pinterest (wellness planners)
- Make.com has separate scenarios for each brand
- brands table has correct separate IDs

### Audit 4: posts_log Not Logging
**Status:** REQUIRES MANUAL ACTION
**Issues Found:**
- posts_log table is EMPTY
- Make.com scenarios post directly to Pinterest but don't log to Supabase
- Multi-Platform Poster logs correctly, but Make.com bypasses it

**Fix Required (Manual in Make.com):**
Add HTTP module to each Pinterest scenario AFTER successful pin creation:
```
POST https://epfoxpgrpsnhlsglxvsa.supabase.co/rest/v1/posts_log
Headers:
  apikey: [SUPABASE_KEY]
  Authorization: Bearer [SUPABASE_KEY]
  Content-Type: application/json
Body:
{
  "brand_id": "[brand UUID]",
  "platform": "pinterest",
  "platform_post_id": "{{pin_id}}",
  "post_url": "{{pin_url}}",
  "status": "posted",
  "posted_at": "{{now}}"
}
```

### Audit 5: Multi-Platform Poster Webhook
**Status:** VERIFIED OK
**Findings:**
- Webhook functionality exists in code
- MAKECOM_PINTEREST_WEBHOOK is optional (scenarios run on schedule)
- Make.com scenarios already running successfully (398+ executions)

### Audit 6: YouTube Shorts Capability
**Status:** DOCUMENTED LIMITATION
**Findings:**
- YOUTUBE_API_KEY only allows reading, not uploading
- Full YouTube posting requires OAuth 2.0 with refresh token
- Code correctly marks videos as "youtube_ready" for manual upload
- This is expected behavior - YouTube upload automation requires OAuth setup

---

## SYSTEM STATUS

### Operational Agents
| Agent | Schedule | Status |
|-------|----------|--------|
| Trend Discovery | 5:00 AM UTC | Running |
| Content Brain | 6:00 AM UTC | Running |
| Blog Factory | 7:00 AM UTC | Running |
| Video Factory | 8:00 AM UTC | Running |
| Multi-Platform Poster | 9 AM, 1 PM, 9 PM UTC | Created |
| Analytics Collector | 11:00 PM UTC | Running |
| Self-Improvement | Sundays 2:00 AM | Running |
| Health Monitor | Every hour | Running |

### Content Pipeline Flow
```
Trend Discovery (5 AM) -> finds trending products/topics
        |
Content Brain (6 AM) -> generates 10-20 content pieces per brand
        |
Blog Factory (7 AM) -> creates SEO blog articles -> Netlify
        |
Video Factory (8 AM) -> renders short-form videos -> Creatomate
        |
Multi-Platform Poster (3x daily) -> posts to Pinterest (via Make.com)
        |
Analytics Collector (11 PM) -> tracks engagement metrics
        |
Self-Improvement (Weekly) -> optimizes based on patterns
```

### Make.com Scenarios (Live)
- Agent 2: Pinterest Value Pins (Complete) - 398+ runs
- The Menopause Planner - Pinterest Value Pins - 154+ runs
- 4 additional scenarios running

---

## QUICK REFERENCE

### Repository
- GitHub: https://github.com/talhahbilal1-arch/social-media-empire
- Branch: main

### Supabase
- Project ID: epfoxpgrpsnhlsglxvsa
- Tables: 15+ (brands, content_bank, posts_log, analytics, etc.)

### Brands
1. **Daily Deal Darling** - Amazon affiliate (beauty, home, lifestyle)
   - Website: dailydealdarling.com
   - Amazon tag: dailydealdarling1-20
2. **The Menopause Planner** - Etsy + Pinterest (wellness planners)

### Estimated Monthly Costs
| Service | Cost |
|---------|------|
| GitHub Actions | Free (2000 min/month) |
| Supabase | Free tier |
| Claude API | ~$5-20 |
| Creatomate | $39 (100 videos) |
| Make.com | $9-16 |
| **Total** | **~$55-75/month** |

---

## NEXT STEPS

1. **Add posts_log HTTP module to Make.com scenarios** - Manual action required
2. **YouTube OAuth Setup** - Enable actual YouTube Shorts uploading (requires OAuth refresh token)
3. **Content Quality Review** - Monitor first week of automated content
4. **Performance Tuning** - Adjust posting frequency based on engagement data
5. **Test Blog Factory** - Run manually to verify Netlify publishing works with fix

---

## AGENT 3 TASKS - Content Enhancements (January 6, 2026)

**Status: COMPLETED**

### Task 1: Pinterest Idea Pins in Video Factory
- [x] Add `idea_pin_url` field to videos table
- [x] Update video_factory.py to create TWO outputs:
  - Regular short video (current behavior)
  - Pinterest Idea Pin format (multi-page, vertical 9:16)
- [x] Idea Pin specs: 9:16 ratio, 2-20 pages, each 1-60 seconds

### Task 2: Higher Commission Affiliate Programs
- [x] Add `affiliate_programs` table to schema.sql
- [x] Add `product_affiliates` table to schema.sql
- [x] Update content_brain.py with affiliate matching function
- [x] Priority: ShareASale (10-30%) > Impact (10-25%) > CJ (5-20%) > Amazon (3-4%)
- [x] Update blog_factory.py to use best affiliate link

### Task 3: Documentation
- [x] Create tasks/agent3-content-enhancements.md with implementation details

### Files Changed by Agent 3
- `database/schema.sql` - Added idea_pin fields, affiliate_programs & product_affiliates tables
- `agents/video_factory.py` - Added Idea Pin creation methods
- `agents/content_brain.py` - Added affiliate matching with priority system
- `agents/blog_factory.py` - Updated to use best affiliate links
- `tasks/agent3-content-enhancements.md` - Full documentation

---

## AGENT 4 TASKS - Email Monetization (January 6, 2026)

**Status: COMPLETED**

### Task 1: ConvertKit Setup
- [x] Created `core/convertkit_client.py` - Full API client
- [x] Documented manual setup steps for ConvertKit account
- [ ] **MANUAL**: Create ConvertKit (Kit) account at https://kit.com
- [ ] **MANUAL**: Create form "Get Your Personalized Product Guide"
- [ ] **MANUAL**: Create tags: quiz-morning, quiz-organization, quiz-selfcare, quiz-beauty, quiz-lifestyle
- [ ] **MANUAL**: Create brand tags: daily-deal-darling, menopause-planner
- [ ] **MANUAL**: Add CONVERTKIT_API_KEY to GitHub Secrets
- [ ] **MANUAL**: Add CONVERTKIT_FORM_ID to GitHub Secrets

### Task 2: Quiz Email Capture
- [x] Created `QuizEmailCapture` class with automatic tagging
- [x] Created `capture_quiz_email()` helper function
- [x] Integrated Etsy product recommendations for Menopause Planner brand

### Task 3: Email Sequence Templates
- [x] Email 1: Quiz Results + Top Picks (Immediate)
- [x] Email 2: Common Mistake (Day 2)
- [x] Email 3: Reader Favorite (Day 4)
- [x] Email 4: New Arrivals (Day 7)
- [x] Email 5: Hidden Gems (Day 14)
- [ ] **MANUAL**: Create sequence in ConvertKit using templates

### Task 4: Etsy Product Connections
- [x] Created `etsy_product_mapping.json` with quiz-to-product mappings
- [x] Integrated Etsy recommendations in QuizEmailCapture class
- [x] Products: Symptom Tracker, Hot Flash Journal, Mood Tracker, Sleep Log, Wellness Planner

### Files Created by Agent 4
- `core/convertkit_client.py` - ConvertKit API client
- `content/email_templates/email_1_quiz_results.md`
- `content/email_templates/email_2_common_mistake.md`
- `content/email_templates/email_3_reader_favorite.md`
- `content/email_templates/email_4_new_arrivals.md`
- `content/email_templates/email_5_hidden_gems.md`
- `content/email_templates/etsy_product_mapping.json`
- `tasks/agent4-email-monetization.md` - Full documentation

### Notes
- Browser automation had auth issues, so ConvertKit account setup requires manual action
- All code is ready to use once API credentials are added to GitHub Secrets
- Did NOT touch: Make.com, video_factory.py, content_brain.py, YouTube, Repurpose.io

---

## AGENT 2 TASKS - Video Distribution (January 6, 2026)

**Status: PARTIALLY COMPLETE - Manual Steps Required**

### Task 1: YouTube OAuth Setup
- [x] Created Google Cloud project "social-media-empire"
- [x] Enabled YouTube Data API v3
- [x] Started OAuth consent screen configuration
- [x] Created `core/youtube_client.py` with full OAuth flow
- [x] Updated `agents/multi_platform_poster.py` to use YouTube client
- [ ] **MANUAL**: Complete OAuth consent screen (add scopes, test users)
- [ ] **MANUAL**: Create OAuth 2.0 credentials (Desktop app)
- [ ] **MANUAL**: Run `python core/youtube_client.py` to get refresh token
- [ ] **MANUAL**: Add to GitHub Secrets:
  - YOUTUBE_CLIENT_ID
  - YOUTUBE_CLIENT_SECRET
  - YOUTUBE_REFRESH_TOKEN

### Task 2: Repurpose.io for TikTok/Instagram
- [x] Documented setup steps in agent2-video-distribution.md
- [ ] **MANUAL**: Sign up at https://repurpose.io
- [ ] **MANUAL**: Connect TikTok account (Daily Deal Darling)
- [ ] **MANUAL**: Connect Instagram account (Daily Deal Darling)
- [ ] **MANUAL**: Create workflow: Source -> TikTok + Instagram Reels

### Task 3: Documentation
- [x] Created `tasks/agent2-video-distribution.md` with full setup guide

### Files Created/Modified by Agent 2
- `core/youtube_client.py` - NEW: Full OAuth 2.0 YouTube upload client
- `agents/multi_platform_poster.py` - MODIFIED: Uses YouTubeClient for uploads
- `tasks/agent2-video-distribution.md` - NEW: Full documentation

### Notes
- YouTube OAuth requires manual browser authentication for refresh token
- Repurpose.io account creation requires human verification
- Did NOT touch: Make.com, quiz pages, blog_factory.py affiliate logic, content_brain.py

---

## FILES CHANGED (January 6, 2026)

1. `agents/blog_factory.py`
   - Added `_add_affiliate_links()` method
   - Added `_add_internal_links()` method
   - Added `quiz_links` to BRAND_CONFIG for both brands
   - Modified `_create_for_brand()` to call new methods

2. `core/netlify_client.py`
   - Fixed `publish_article()` to preserve existing site files
   - Now fetches current deploy files before creating new deploy
   - Added better error handling

3. `tasks/todo.md`
   - Updated with full audit findings and fixes
