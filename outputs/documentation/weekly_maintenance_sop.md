# Weekly Maintenance SOP -- Pinterest Empire

Standard Operating Procedures for maintaining the automated Pinterest content pipeline across all brands. Total weekly time commitment: approximately 30 minutes.

---

## Table of Contents

1. [Monday Check (10 min)](#monday-check-10-min)
2. [Wednesday Check (5 min)](#wednesday-check-5-min)
3. [Friday Review (15 min)](#friday-review-15-min)
4. [Monthly Deep Review](#monthly-deep-review)
5. [Quarterly Strategy Review](#quarterly-strategy-review)
6. [Quick Reference: URLs and Dashboards](#quick-reference-urls-and-dashboards)

---

## Monday Check (10 min)

Start the week by verifying all automation ran correctly over the past 7 days.

### Make.com Scenario Health

- [ ] **Agent 2A (Listicle Creator)**: Open Make.com > Scenarios > Agent 2A
  - [ ] Check last 7 days of run history
  - [ ] Verify all runs show green (successful)
  - [ ] Count total successful runs (target: 21 runs = 3x/day x 7 days)
  - [ ] Note any failed runs -- click to see error details
  - [ ] If runs are missing entirely, check that the scenario is **Active** (not paused)
  - [ ] Check operations consumed vs. plan limit

- [ ] **Agent 2B (Inline Pinner)**: Open Make.com > Scenarios > Agent 2B
  - [ ] Check last 7 days of run history
  - [ ] Verify all runs show green
  - [ ] Count total pins posted (target: ~49 inline pins/week)
  - [ ] Note any "0 operations" runs (may indicate no pins were scheduled)

**If failures found**, record them here:

```
Date: ___________
Scenario: 2A / 2B
Error: ___________
Module that failed: ___________
Action taken: ___________
```

### Supabase Data Integrity

- [ ] Open Supabase Dashboard > Table Editor
- [ ] **pinterest_pins table**:
  - [ ] Check latest entries have non-null `title`, `description`, `featured_image_url`
  - [ ] Check `pin_id` is populated for entries with `status = posted`
  - [ ] Look for any entries with `status = pending` older than 24 hours (stuck)
- [ ] **scheduled_inline_pins table**:
  - [ ] Check that yesterday's pins all have `pinned = true`
  - [ ] Look for any overdue pins (`scheduled_date < today` AND `pinned = false`)
  - [ ] Verify next 3 days have scheduled pins queued
- [ ] **content_history table**:
  - [ ] Check that entries are being created (should match pinterest_pins count)
  - [ ] Spot-check that `brand` values are correct (no cross-contamination)
- [ ] **errors table**:
  - [ ] Check for unresolved errors from the past week
  - [ ] Resolve any that were transient (API timeouts, rate limits)

**Quick SQL for Monday check** (run in Supabase SQL Editor):

```sql
-- Last 7 days pin count by brand
SELECT brand, COUNT(*) as pin_count
FROM pinterest_pins
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY brand;

-- Stuck pending pins (older than 24h)
SELECT id, brand, title, created_at
FROM pinterest_pins
WHERE status = 'pending'
  AND created_at < NOW() - INTERVAL '24 hours';

-- Overdue inline pins
SELECT id, brand, original_title, scheduled_date
FROM scheduled_inline_pins
WHERE scheduled_date < CURRENT_DATE
  AND pinned = FALSE;

-- Unresolved errors this week
SELECT id, error_type, error_message, created_at
FROM errors
WHERE resolved = FALSE
  AND created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

### Pinterest Visual Verification

- [ ] Open Pinterest for **Daily Deal Darling** account
  - [ ] Verify latest pins appear on the correct boards
  - [ ] Check that images are loading correctly (not broken)
  - [ ] Ensure pin titles and descriptions look correct (no JSON artifacts)

- [ ] Open Pinterest for **Menopause Planner** account
  - [ ] Same checks as above

### Subdomain Site Verification

Quick load test for all 10 subdomain sites:

- [ ] Site 1: ________________________________ -- Loads? Y/N
- [ ] Site 2: ________________________________ -- Loads? Y/N
- [ ] Site 3: ________________________________ -- Loads? Y/N
- [ ] Site 4: ________________________________ -- Loads? Y/N
- [ ] Site 5: ________________________________ -- Loads? Y/N
- [ ] Site 6: ________________________________ -- Loads? Y/N
- [ ] Site 7: ________________________________ -- Loads? Y/N
- [ ] Site 8: ________________________________ -- Loads? Y/N
- [ ] Site 9: ________________________________ -- Loads? Y/N
- [ ] Site 10: ________________________________ -- Loads? Y/N

> **Tip**: Open all 10 URLs in tabs at once. Any that fail to load need immediate attention.

---

## Wednesday Check (5 min)

Quick mid-week pulse check on performance and account health.

### Pinterest Analytics Quick Scan

- [ ] **Daily Deal Darling**:
  - [ ] Open Pinterest Analytics > Overview
  - [ ] Note impressions for the past 7 days: ___________
  - [ ] Note saves for the past 7 days: ___________
  - [ ] Note outbound clicks for the past 7 days: ___________
  - [ ] Flag any top-performing pins (5x+ average impressions)
  - [ ] Note which board(s) are performing best

- [ ] **Menopause Planner / Fitness Made Easy** (whichever applies):
  - [ ] Same metrics as above
  - [ ] Impressions: ___________
  - [ ] Saves: ___________
  - [ ] Outbound clicks: ___________

### Account Health

- [ ] Check for any Pinterest notifications or warnings
  - [ ] Spam warnings? Y/N
  - [ ] Suspended boards? Y/N
  - [ ] Policy violations? Y/N
  - [ ] Account review pending? Y/N

> **If you receive ANY account warning**: Stop automation immediately (pause both Make.com scenarios), reduce posting frequency, and review the troubleshooting guide section on account suspensions.

### Top Performing Pins (Note for Friday Review)

| Pin Title | Brand | Impressions | Saves | Clicks |
|-----------|-------|------------|-------|--------|
| | | | | |
| | | | | |
| | | | | |

---

## Friday Review (15 min)

End-of-week comprehensive review, performance analysis, and planning for the next week.

### Pinterest Analytics Deep Dive

- [ ] **Screenshot Pinterest Analytics** for both brand accounts
  - [ ] Save to `outputs/documentation/analytics/YYYY-MM-DD/` folder
  - [ ] Take screenshots of: Overview, Top Pins, Top Boards, Audience Insights

- [ ] **Update Milestone Tracker**:

| Metric | Last Week | This Week | Change | Target |
|--------|-----------|-----------|--------|--------|
| Total pins posted | | | | 49/week |
| Impressions (Brand 1) | | | | |
| Impressions (Brand 2) | | | | |
| Saves (Brand 1) | | | | |
| Saves (Brand 2) | | | | |
| Outbound clicks (Brand 1) | | | | |
| Outbound clicks (Brand 2) | | | | |
| Followers (Brand 1) | | | | |
| Followers (Brand 2) | | | | |

### Pin Performance Review

- [ ] Identify the 3 best-performing pins this week
  - Pin 1: ___________ (Why? Topic? Style?)
  - Pin 2: ___________
  - Pin 3: ___________

- [ ] Identify the 3 worst-performing pins this week
  - Pin 1: ___________ (Why? Topic? Style?)
  - Pin 2: ___________
  - Pin 3: ___________

- [ ] **Pattern Analysis**:
  - [ ] Which topics drove the most engagement? ___________
  - [ ] Which visual styles performed best? ___________
  - [ ] Which boards had the most reach? ___________
  - [ ] What time of day had the best engagement? ___________

### Inline Pin Scheduling Queue

- [ ] Check the next 2 weeks of scheduled inline pins:

```sql
SELECT scheduled_date, brand, COUNT(*) as pin_count,
       SUM(CASE WHEN pinned THEN 1 ELSE 0 END) as completed
FROM scheduled_inline_pins
WHERE scheduled_date >= CURRENT_DATE
  AND scheduled_date < CURRENT_DATE + INTERVAL '14 days'
GROUP BY scheduled_date, brand
ORDER BY scheduled_date;
```

- [ ] Verify there are pins scheduled for each day
- [ ] If any days are empty, the listicle creation may have failed

### Topic Adjustment Planning

Based on this week's performance, note any adjustments for next week:

- Topics to emphasize: ___________
- Topics to reduce: ___________
- New topic ideas from trending analysis: ___________
- Board changes needed: ___________

### Infrastructure Checks

- [ ] **Netlify**: Verify all 10 subdomain sites are deployed and loading
  - [ ] Check Netlify dashboard for any failed deploys
  - [ ] Check HTTPS certificates are valid (not expiring soon)

- [ ] **Supabase Storage**:
  - [ ] Open Supabase Dashboard > Settings > General
  - [ ] Check database size: ___________ / 500MB (free tier limit)
  - [ ] If above 400MB, run cleanup:
    ```sql
    -- Delete old errors (>30 days, resolved)
    DELETE FROM errors
    WHERE resolved = TRUE AND created_at < NOW() - INTERVAL '30 days';

    -- Delete old content_history (>90 days)
    DELETE FROM content_history
    WHERE created_at < NOW() - INTERVAL '90 days';

    -- Delete completed inline pins (>60 days)
    DELETE FROM scheduled_inline_pins
    WHERE pinned = TRUE AND pinned_at < NOW() - INTERVAL '60 days';
    ```

- [ ] **GitHub Actions**:
  - [ ] Check content-engine workflow runs (Actions tab)
  - [ ] Check weekly-discovery workflow ran Sunday night
  - [ ] Note any workflow failures

---

## Monthly Deep Review

Perform this review on the first Friday of each month, in addition to the regular Friday review.

### Account Growth Analysis

| Metric | Month Start | Month End | Growth % |
|--------|-------------|-----------|----------|
| Pins posted (total) | | | |
| Monthly impressions (Brand 1) | | | |
| Monthly impressions (Brand 2) | | | |
| Monthly saves (Brand 1) | | | |
| Monthly saves (Brand 2) | | | |
| Monthly clicks (Brand 1) | | | |
| Monthly clicks (Brand 2) | | | |
| Followers (Brand 1) | | | |
| Followers (Brand 2) | | | |
| Email subscribers (total) | | | |
| Website traffic (Brand 1) | | | |
| Website traffic (Brand 2) | | | |

### Content Quality Audit

- [ ] Review 10 random pins from each brand
  - [ ] Titles create curiosity gap? Y/N
  - [ ] Descriptions are human-sounding? Y/N
  - [ ] Images are brand-appropriate? Y/N
  - [ ] No duplicate or near-duplicate content? Y/N
  - [ ] Destination URLs are working? Y/N

### API Usage and Cost Review

| API | Monthly Usage | Cost | Budget |
|-----|-------------|------|--------|
| Claude (Anthropic) | ___ tokens | $___ | $10/mo |
| Pexels | ___ calls | Free | Free |
| Make.com | ___ operations | $___ | Plan limit |
| Supabase | ___ DB size | Free | Free tier |
| Netlify | ___ bandwidth | Free | Free tier |

### Infrastructure Maintenance

- [ ] **Make.com**: Export both scenario blueprints as JSON backups
- [ ] **Supabase**: Run data cleanup queries (see Friday section)
- [ ] **Git**: Verify all code changes are committed and pushed
- [ ] **API Keys**: Check expiration dates for all API keys/tokens
  - [ ] Pinterest OAuth token (if applicable)
  - [ ] Claude API key
  - [ ] Pexels API key
  - [ ] Supabase service role key
  - [ ] Late API key(s)

### Board Strategy Review

- [ ] Review Pinterest board performance for each account
- [ ] Consider creating new boards for emerging topics
- [ ] Archive underperforming boards (unlink from scenario, don't delete)
- [ ] Update board descriptions with current SEO keywords

### Competitor Check

- [ ] Scan 3-5 competitor Pinterest accounts in each niche
- [ ] Note any content strategies they're using that you're not
- [ ] Identify gaps in their content that you could fill
- [ ] Check if any competitor is using similar listicle formats

---

## Quarterly Strategy Review

Perform every 3 months (January, April, July, October).

### Performance Trajectory

- [ ] Compare key metrics across all 3 months in the quarter
- [ ] Identify upward and downward trends
- [ ] Calculate average cost per click (total API costs / total clicks)
- [ ] Project growth for next quarter

### Brand Evaluation

For each brand, answer:

1. Is this brand growing? What's the trajectory?
2. Is the content resonating with the target audience?
3. Are we getting meaningful traffic to the websites?
4. Are affiliate links getting clicks?
5. Is email subscriber growth meeting targets?
6. Should we adjust the posting frequency?
7. Should we add or remove Pinterest boards?
8. Should we adjust the brand voice in content_brain.py?

### Technical Debt

- [ ] Review any accumulated errors in the errors table
- [ ] Check for patterns in failures (same module, same time, same brand)
- [ ] Update Make.com scenarios if any API endpoints have changed
- [ ] Update Claude model version if a newer Sonnet is available
- [ ] Review and update SEO keywords based on Search Console data

### Budget and ROI

| Item | Quarterly Cost | Quarterly Revenue | ROI |
|------|---------------|-------------------|-----|
| Make.com plan | | | |
| Claude API | | | |
| Domain/hosting | | | |
| Total | | | |
| Affiliate revenue | | | |
| Ad revenue | | | |
| **Net** | | | |

---

## Quick Reference: URLs and Dashboards

| Resource | URL |
|----------|-----|
| Make.com Dashboard | https://www.make.com/en/dashboard |
| Supabase Dashboard | https://supabase.com/dashboard/project/epfoxpgrpsnhlsglxvsa |
| Pinterest (Brand 1) | https://www.pinterest.com/[brand1_username]/ |
| Pinterest (Brand 2) | https://www.pinterest.com/[brand2_username]/ |
| Pinterest Analytics | https://analytics.pinterest.com/ |
| Netlify Dashboard | https://app.netlify.com/teams/talhahbilal1/overview |
| GitHub Actions | https://github.com/[owner]/social-media-empire/actions |
| Claude Console | https://console.anthropic.com/ |
| Pexels Dashboard | https://www.pexels.com/api/dashboard/ |
| fitover35.com | https://fitover35.com |
| dailydealdarling.com | https://dailydealdarling.com |
| ToolPilot Hub | https://ai-tools-hub-lilac.vercel.app |

### Emergency Contacts

- **Make.com support**: https://www.make.com/en/help
- **Supabase support**: https://supabase.com/support
- **Pinterest business support**: https://help.pinterest.com/en/business
- **Anthropic support**: https://support.anthropic.com
