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
