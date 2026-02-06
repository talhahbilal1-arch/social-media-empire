# CHANGES SUMMARY — Fitness Pivot
**Date:** 2026-02-05
**Branch:** `fitness-pivot`

---

## 1. WHAT WAS CHANGED

### Configuration (Fitness-Only Pivot)

| File | Change |
|------|--------|
| `utils/config.py` | Removed daily_deal_darling and menopause_planner from active brands. Only `fitnessmadeasy` is now active. Platforms reduced to pinterest + youtube_shorts. |
| `video_automation/cross_platform_poster.py` | Disabled daily_deal_darling and menopause_planner (enabled=False, videos_per_day=0). Reduced fitnessmadeasy from 6 videos/day to 3. Changed link_url to fitover35.com/blog.html to drive traffic to articles with embedded affiliates. |
| `video_automation/video_content_generator.py` | Updated fitnessmadeasy brand config with stronger CTAs, more urgency hooks, Pinterest SEO keywords, destination URLs. Added pin_title and pin_description to AI prompt for Pinterest-optimized content. |
| `email_marketing/email_sender.py` | Added fitnessmadeasy brand to BRAND_EMAIL_CONFIG (from: hello@fitover35.com). |

### Website (fitover35.com)

| File | Change |
|------|--------|
| `outputs/fitover35-website/index.html` | Updated nav to include Products page. Changed hero CTA to "Get Free 7-Day Kickstart". Updated lead magnet from "5-Day Density Guide" to "7-Day Fat Loss Kickstart". Updated footer copyright to 2026 + affiliate disclosure. |
| `outputs/fitover35-website/blog.html` | Updated nav, lead magnet text, popup text, footer to match. |
| `outputs/fitover35-website/products.html` | **NEW** — Complete digital products sales page with: featured 7-Day Fat Burn Challenge ($17), 30-Day Meal Prep Guide ($27), 12-Week Muscle Building Blueprint ($47), Recovery Protocol ($17). Includes Gumroad purchase links (TODO: create actual Gumroad products). Affiliate gear section with Amazon links. Email capture CTA. |

### Affiliate System

| File | Change |
|------|--------|
| `monetization/fitness_affiliates.py` | **NEW** — Complete affiliate product management system. 13 products across supplements, equipment, and programs. Includes ClickBank (75% commission), ShareASale (15-25%), and Amazon (4%). Functions for: random product selection (weighted by commission), article-matched product recommendations, HTML section generation for articles. |

### Email Marketing

| File | Change |
|------|--------|
| `email_marketing/sequences/fitnessmadeasy_welcome.py` | **NEW** — Complete 7-email welcome sequence over 14 days. Email 1: Lead magnet delivery. Email 2: Quick win workout. Email 3: Nutrition rule + protein affiliate. Email 4: Recovery + foam roller/bands affiliates. Email 5: Identity/mindset shift. Email 6: Product pitch ($17 Fat Burn Challenge). Email 7: Wrap-up + weekly newsletter transition. Full HTML + plain text versions. |

### Content Pipeline

| File | Change |
|------|--------|
| `video_automation/content_bank/fitness_pinterest_topics.json` | **NEW** — 60 Pinterest-optimized fitness topics across 6 categories: fat loss, muscle building, nutrition, recovery, home gym, testosterone. Each category has Pinterest SEO keywords. Pin description template included. |

### Tracking & Analytics

| File | Change |
|------|--------|
| `monitoring/fitness_tracker.py` | **NEW** — Fitness-specific business metrics tracking: pins posted, email signups, affiliate clicks, revenue. Weekly summary generator with actionable metrics. |

### Workflows

| File | Change |
|------|--------|
| `.github/workflows/workflow-guardian.yml` | Reduced from every 30 minutes to every 6 hours. |
| `.github/workflows/fitness-email-sequence.yml` | **NEW** — Daily email sequence processor for welcome automation. |

### Archived Workflows (moved to `.github/workflows/archived/`)

| Workflow | Reason |
|----------|--------|
| `video-automation-midmorning.yml` | Reduced to 3 daily slots (morning/noon/evening) |
| `video-automation-afternoon.yml` | Reduced to 3 daily slots |
| `generate-article.yml` | Daily Deal Darling article generator — brand disabled |
| `update-deals.yml` | Amazon deals page updater — brand disabled |
| `verify-links.yml` | Amazon affiliate link verifier — brand disabled |
| `weekly-deals-email.yml` | Weekly deals newsletter — brand disabled |
| `tiktok-instagram-automation.yml` | TikTok/Instagram posting — webhooks were broken |
| `generate-videos.yml` | Redundant with time-slot video workflows |
| `debug-config.yml` | Development-only diagnostic tool |
| `test-pinterest-post.yml` | Development-only Pinterest test |

---

## 2. WHAT'S NOW AUTOMATED

| Automation | Schedule | What It Does |
|------------|----------|-------------|
| Video Automation - Morning | 6 AM PST daily | Generate + post 1 fitness video to Pinterest + YouTube |
| Video Automation - Noon | 12 PM PST daily | Generate + post 1 fitness video to Pinterest + YouTube |
| Video Automation - Evening | 6 PM PST daily | Generate + post 1 fitness video to Pinterest + YouTube |
| FitOver35 Blog Automation | Mon-Fri 1 AM PST | Generate SEO fitness article for fitover35.com |
| FitOver35 Article Generator | Mon-Fri 11 PM PST | Generate additional fitness article |
| Fitness Email Sequence | Daily 10 AM PST | Process welcome email sequence for new subscribers |
| Email Automation | 2x daily | Process general email sequences |
| Health Monitoring | Every 4 hours | Check all API integrations |
| Self-Healing | Every 4 hours | Auto-fix broken workflows |
| Error Alerts | Every 4 hours | Check for unresolved errors |
| Workflow Guardian | Every 6 hours | Monitor GitHub Actions (reduced from 30 min) |
| Weekly Summary | Sundays 9 AM PST | Aggregate metrics and email report |
| Auto Merge | On push to claude/** | Auto-merge branches to main |

**Total active workflows: 13** (reduced from 24)
**Daily content output: 3 videos + 1-2 articles** (all fitness, all driving to fitover35.com)

---

## 3. WHAT THE OWNER NEEDS TO DO MANUALLY

### Immediate (This Week)

- [ ] **Cancel HeyGen subscription** — $48/month savings, zero code integration
- [ ] **Sign up for Gumroad** at gumroad.com — free to start, they take 10% of sales
  - Create product: "7-Day Fat Burn Challenge" at $17
  - Create product: "30-Day Meal Prep Guide" at $27 (when ready)
  - Update product links in `outputs/fitover35-website/products.html`
- [ ] **Sign up for ClickBank** as affiliate at clickbank.com/affiliates
  - Search for fitness offers with 50%+ commission
  - Replace placeholder URLs in `monetization/fitness_affiliates.py`
- [ ] **Sign up for ShareASale** at shareasale.com
  - Apply to: Transparent Labs, Legion Athletics, TRX, Rogue Fitness
  - Replace placeholder URLs in `monetization/fitness_affiliates.py`
- [ ] **Create the 7-Day Fat Loss Kickstart PDF** (the free lead magnet)
  - Use AI to generate content, format in Canva or Google Docs
  - Upload to fitover35.com/downloads/7-day-kickstart.pdf
  - This is the most important manual task — it's the lead magnet for ALL email capture
- [ ] **Set up ConvertKit automation** for the welcome sequence
  - Create automation rule: new subscriber → start welcome sequence
  - Map the 7 emails from `email_marketing/sequences/fitnessmadeasy_welcome.py`
  - Set delays: Day 0, Day 2, Day 4, Day 7, Day 9, Day 12, Day 14
- [ ] **Configure Resend** for fitover35.com domain (verify hello@fitover35.com)
- [ ] **Push this branch** and merge to main to activate changes

### Soon (This Month)

- [ ] **Create the $17 digital product** (7-Day Fat Burn Challenge PDF)
  - Use AI to generate 15-20 page PDF with workouts, nutrition, tracking
  - Professional formatting in Canva
  - Upload to Gumroad, get purchase link
- [ ] **Add Google Analytics** to fitover35.com
  - Install GA4 tracking script on all pages
  - Set up conversion events: email_signup, product_page_view, affiliate_click
- [ ] **Review Pinterest Analytics** weekly
  - Note which pin topics get most engagement
  - Feed winning topics back into content generation
- [ ] **Add UTM parameters** to all links shared on Pinterest
  - Format: `?utm_source=pinterest&utm_medium=pin&utm_campaign=fitover35`

### Optional (When Revenue Starts)

- [ ] **Create additional digital products** ($27 meal prep, $47 muscle building)
- [ ] **Set up Gumroad webhook** to track sales automatically
- [ ] **Apply to Amazon Influencer Program** for higher commissions
- [ ] **Consider running Pinterest ads** ($5-10/day) to boost top-performing pins

---

## 4. ESTIMATED TIMELINE TO FIRST DOLLAR

| Milestone | Timeframe | Dependency |
|-----------|-----------|------------|
| Free lead magnet live | Week 1 | Owner creates PDF + uploads |
| Gumroad product live ($17) | Week 1-2 | Owner creates PDF + Gumroad account |
| ClickBank/ShareASale approved | Week 2-3 | Application + approval process |
| First email subscribers | Week 2-4 | Lead magnet must be live, pins driving traffic |
| First affiliate click | Week 3-6 | Articles with affiliate links + Pinterest traffic |
| **First dollar (most likely)** | **Week 4-8** | Most likely from ClickBank/ShareASale affiliate sale OR Gumroad product sale |
| First $100 month | Month 3-6 | Requires 500+ email subscribers or consistent affiliate traffic |

**Realistic scenario:** If the owner creates the lead magnet PDF and signs up for ClickBank/ShareASale this week, automated Pinterest posting (3 pins/day) + article generation (1-2/day) should drive first affiliate clicks within 3-6 weeks. With 30-50% commission products, even 5-10 clicks/month could generate $20-100.

**Key insight:** The first dollar will most likely come from a ClickBank fitness product (75% commission = $15 per sale) or the $17 Gumroad product. NOT from Amazon (3-4% commission is too low at current traffic levels).

---

## 5. REMAINING GAPS

| Gap | Impact | Resolution |
|-----|--------|------------|
| **No lead magnet PDF exists yet** | Email capture has nothing to deliver | Owner must create this ASAP |
| **No Gumroad products created** | Product page links go nowhere | Owner must create Gumroad account + products |
| **Affiliate URLs are placeholders** | ClickBank/ShareASale links don't work yet | Owner must sign up + replace URLs |
| **No Google Analytics** | Can't track conversions or traffic sources | Owner adds GA4 script to site |
| **ConvertKit automation not configured** | Welcome sequence emails won't send | Owner sets up automation rules in ConvertKit |
| **fitover35.com email not verified in Resend** | Can't send from hello@fitover35.com | Owner verifies domain in Resend dashboard |
| **No UTM tracking on Pinterest links** | Can't attribute traffic to specific pins | Should add UTM params to video link URLs |
| **Pinterest static image pins not automated** | Only video pins are automated; static pins often perform better | Could add static pin generation in future |

---

## 6. NEW SECRETS/ENVIRONMENT VARIABLES NEEDED

### Already Required (should be set)
- `GEMINI_API_KEY` — Content generation
- `PEXELS_API_KEY` — Stock media
- `SUPABASE_URL` — Database
- `SUPABASE_KEY` — Database auth
- `LATE_API_KEY_3` — Pinterest posting (Fitness Made Easy account)
- `CREATOMATE_API_KEY` — Video rendering

### Recommended to Add
- `RESEND_API_KEY` — Email sending (verify fitover35.com domain)
- `CONVERTKIT_API_KEY` — Email subscriber management
- `CONVERTKIT_API_SECRET` — Subscriber data access
- `CONVERTKIT_FORM_ID` — Form ID for fitover35.com (currently: 8946984)

### No Longer Needed (can remove)
- `LATE_API_KEY_2` — Daily Deal Darling (disabled)
- `LATE_API_KEY_4` — Menopause Planner (disabled)
- `RAINFOREST_API_KEY` — Amazon deals page (disabled)
- `MAKE_COM_TIKTOK_WEBHOOK` — TikTok posting (disabled)
- `MAKE_COM_INSTAGRAM_WEBHOOK` — Instagram posting (disabled)

---

## COST IMPACT

| Before | After |
|--------|-------|
| ~$140-200/month | ~$50-80/month |
| 12 videos/day (3 brands) | 3 videos/day (1 brand) |
| 24 workflows | 13 workflows |
| $48/month HeyGen (unused) | $0 (cancelled) |
| Creatomate: ~$90/month | Creatomate: ~$30/month |
| Guardian: 48 runs/day | Guardian: 4 runs/day |

**Estimated savings: $60-120/month**

---

*Changes made on fitness-pivot branch. Ready for review and merge.*
