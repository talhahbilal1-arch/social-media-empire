# Weekly Maintenance Checklist

## Overview

This Standard Operating Procedure outlines the routine maintenance tasks required to keep the Social Media Empire automation system running smoothly. Tasks are organized by frequency: daily quick checks, weekly reviews, monthly optimizations, and quarterly planning activities.

## Prerequisites

- Access to GitHub repository and Actions dashboard
- Access to Supabase database dashboard
- Access to Make.com account
- Access to all social media platform analytics (Pinterest, YouTube, TikTok, Instagram)
- Access to ConvertKit email marketing dashboard
- Access to Creatomate video rendering dashboard
- Alert email configured and receiving notifications

---

## Daily Quick Checks (5-10 minutes)

### 1. Health Check Status

**What to Check:**
- Run the automated health check or review the most recent health monitoring workflow run

**How to Check:**
```bash
# Local check
python -m monitoring.health_checker --full

# Or check GitHub Actions
# Navigate to: Actions > health-monitoring workflow > Latest run
```

**Expected Result:**
- Overall status: "healthy"
- All 8 services showing "healthy" status
- Response times under 1000ms for all APIs

**Action if Failed:**
- Check individual service status in the output
- See troubleshooting-guide.md for specific service failures
- Create issue in GitHub if persistent

### 2. Video Generation Status

**What to Check:**
- Verify all 3 daily workflow runs completed successfully (morning, noon, evening)
- Confirm 12 videos were created (3 per brand x 4 brands)

**How to Check:**
```bash
# Check today's videos in Supabase
# Navigate to Supabase > Table Editor > videos table
# Filter by created_at >= today's date

# Or run locally
python -c "
from database.supabase_client import get_supabase_client
db = get_supabase_client()
stats = db.get_daily_stats()
print(f'Videos created today: {stats[\"videos_created\"]}')
print(f'By brand: {stats[\"videos_by_brand\"]}')
"
```

**Expected Result:**
- 12 videos created
- Each brand (daily_deal_darling, menopause_planner, nurse_planner, adhd_planner) has 3 videos
- Status column shows "posted" for all videos

**Action if Failed:**
- Check workflow logs in GitHub Actions
- Review error alerts in email
- Manually trigger failed workflows with workflow_dispatch

### 3. Error Alert Review

**What to Check:**
- Review any error alert emails received
- Check error count in Supabase errors table

**How to Check:**
```bash
python -m monitoring.error_reporter --summary
```

**Expected Result:**
- Zero critical or high severity errors
- No new unresolved errors from today

**Action if Failed:**
- Prioritize critical errors immediately
- Document recurring errors for weekly review
- Resolve simple errors same-day

### 4. Platform Post Verification (Spot Check)

**What to Check:**
- Verify at least one video per platform was actually posted

**How to Check:**
- Pinterest: Check each brand's board for new pins
- YouTube: Check channel for new Shorts
- Review Late API logs if Pinterest video posting is configured

**Expected Result:**
- New content visible on all active platforms
- No posting errors in logs

---

## Weekly Review Tasks (30-45 minutes)

### 1. Performance Metrics Review

**When:** Every Monday morning

**Metrics to Collect:**

| Metric | Source | Target |
|--------|--------|--------|
| Videos Created | Supabase | 84/week (12/day x 7) |
| Posting Success Rate | Supabase | >95% |
| New Subscribers | ConvertKit | Track trend |
| Health Score Average | Daily Reports | >80 |
| Critical Errors | Supabase | 0 |
| API Response Times | Health Checks | <1000ms avg |

**How to Collect:**
```bash
# Generate weekly summary
python -c "
from database.supabase_client import get_supabase_client
from datetime import datetime, timedelta

db = get_supabase_client()
# Get last 7 days of videos
videos = db.get_recent_videos(limit=100)
week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
weekly_videos = [v for v in videos if v['created_at'] >= week_ago]
print(f'Videos this week: {len(weekly_videos)}')

# Count by brand
brands = {}
for v in weekly_videos:
    b = v['brand']
    brands[b] = brands.get(b, 0) + 1
print(f'By brand: {brands}')
"
```

**Action Items:**
- [ ] Record metrics in tracking spreadsheet
- [ ] Compare to previous week
- [ ] Note any significant changes (>10% variance)
- [ ] Create action items for underperforming areas

### 2. Error Analysis

**When:** Every Monday

**What to Review:**
- All errors from the past week
- Patterns in error types
- Recurring issues

**How to Review:**
```bash
# Get error summary
python -m monitoring.error_reporter --summary

# Get detailed unresolved errors
python -c "
from database.supabase_client import get_supabase_client
db = get_supabase_client()
errors = db.get_unresolved_errors(limit=50)
for e in errors:
    print(f'{e[\"created_at\"]}: [{e[\"error_type\"]}] {e[\"error_message\"][:100]}')
"
```

**Action Items:**
- [ ] Resolve any simple errors
- [ ] Document patterns for recurring issues
- [ ] Create GitHub issues for bugs requiring code changes
- [ ] Update troubleshooting guide if new solutions found

### 3. Content Bank Review

**When:** Every Wednesday

**What to Check:**
- Remaining unused content in each category
- Content freshness and relevance

**How to Check:**
```bash
# Check content bank levels
python -c "
from database.supabase_client import get_supabase_client
db = get_supabase_client()
for brand in ['daily_deal_darling', 'menopause_planner', 'nurse_planner', 'adhd_planner']:
    unused = db.get_unused_content(brand, 'tips', limit=100)
    print(f'{brand}: {len(unused)} unused content ideas')
"
```

**Target Levels:**
- Each brand should have 20+ unused content ideas
- Seasonal content should be refreshed monthly

**Action Items:**
- [ ] Add new content if any brand below 20 ideas
- [ ] Review and remove outdated content
- [ ] Add seasonal content for upcoming holidays

### 4. Make.com Scenario Review

**When:** Every Friday

**What to Check:**
- Scenario execution history
- Error rates in scenarios
- Remaining operations quota

**How to Review:**
1. Log into Make.com dashboard
2. Navigate to each active scenario:
   - Pinterest video posting scenario
   - Instagram Reels scenario (if configured)
   - TikTok scenario (if configured)
3. Check "History" tab for execution status

**Expected Result:**
- >95% success rate on all scenarios
- No scenario disabled due to errors
- Sufficient operations remaining for the month

**Action Items:**
- [ ] Investigate any failed executions
- [ ] Upgrade plan if approaching operation limits
- [ ] Test webhook connections if failures detected

### 5. API Quota Check

**When:** Every Friday

**Quotas to Monitor:**

| API | Check Location | Monthly Limit |
|-----|----------------|---------------|
| Gemini | Google AI Studio | 60 RPM, check daily usage |
| Pexels | Pexels API Dashboard | 200 req/hour |
| Creatomate | Creatomate Dashboard | Based on plan |
| YouTube | Google Cloud Console | Check quota usage |
| Resend | Resend Dashboard | 100/day free tier |

**Action Items:**
- [ ] Record current usage levels
- [ ] Project if limits will be hit before month end
- [ ] Plan upgrades if needed

---

## Monthly Optimization Tasks (2-3 hours)

### 1. Content Performance Analysis

**When:** First week of each month

**What to Analyze:**
- Best performing video topics by brand
- Hook styles with highest engagement (from A/B testing)
- Optimal posting times
- Underperforming content categories

**How to Analyze:**
```bash
# Get A/B testing report
python -c "
from video_automation.ab_testing import get_best_hook_style_report
report = get_best_hook_style_report()
for brand, data in report.items():
    print(f'{brand}: Best hook style = {data[\"winning_style\"]} ({data[\"style_name\"]})')
"
```

**Action Items:**
- [ ] Update content bank with high-performing topic types
- [ ] Adjust hook style weights based on A/B test results
- [ ] Retire underperforming content categories
- [ ] Document insights for future content planning

### 2. Template Performance Review

**When:** Second week of each month

**What to Review:**
- Video template engagement rates
- Template rendering success rates
- Template load times

**Files to Review:**
- `/video_automation/templates/deal_alert.json`
- `/video_automation/templates/wellness_tips.json`
- `/video_automation/templates/menopause_tips.json`
- `/video_automation/templates/nurse_lifestyle.json`
- `/video_automation/templates/adhd_hacks.json`

**Action Items:**
- [ ] Update underperforming templates
- [ ] Test new template variations
- [ ] Update Creatomate template IDs if needed

### 3. Email Sequence Optimization

**When:** Third week of each month

**What to Review:**
- Welcome sequence open rates
- Click-through rates
- Unsubscribe rates by sequence
- Subscriber growth trends

**How to Review:**
1. Log into ConvertKit
2. Navigate to Sequences
3. Review metrics for each brand's welcome sequence

**Action Items:**
- [ ] Update subject lines for low open rates (<20%)
- [ ] Revise content for low click rates (<2%)
- [ ] A/B test new email variations
- [ ] Update lead magnets if conversion dropping

### 4. Security and Access Review

**When:** Last week of each month

**What to Review:**
- API key rotation needs
- GitHub secrets validity
- OAuth token freshness
- Access logs for unusual activity

**Action Items:**
- [ ] Rotate any compromised or old API keys
- [ ] Update GitHub secrets if keys rotated
- [ ] Refresh YouTube OAuth token if needed
- [ ] Review and revoke unused access

### 5. Database Cleanup

**When:** Last week of each month

**What to Clean:**
- Old video records (>90 days)
- Resolved error logs (>30 days)
- Stale content bank entries
- Old analytics events (>90 days)

**How to Clean:**
```sql
-- Run in Supabase SQL Editor

-- Archive old videos (keep last 90 days)
DELETE FROM videos
WHERE created_at < NOW() - INTERVAL '90 days'
AND status = 'posted';

-- Clean resolved errors (keep last 30 days)
DELETE FROM errors
WHERE resolved = true
AND resolved_at < NOW() - INTERVAL '30 days';

-- Clean old analytics (keep last 90 days)
DELETE FROM analytics
WHERE created_at < NOW() - INTERVAL '90 days';
```

**Action Items:**
- [ ] Backup data before deletion
- [ ] Run cleanup queries
- [ ] Verify table sizes reduced
- [ ] Document cleanup in maintenance log

---

## Quarterly Planning Tasks (Half day)

### 1. Platform Strategy Review

**When:** First month of each quarter

**What to Review:**
- Platform algorithm changes
- New platform features to leverage
- Platform performance comparison
- New platforms to consider

**Action Items:**
- [ ] Research recent platform updates
- [ ] Evaluate new platform opportunities
- [ ] Adjust posting strategy based on algorithm changes
- [ ] Plan platform-specific feature implementations

### 2. Brand Strategy Assessment

**When:** First month of each quarter

**What to Assess for Each Brand:**
- Audience growth rate
- Engagement trends
- Content relevance
- Competitive positioning

**Action Items:**
- [ ] Review each brand's quarterly metrics
- [ ] Identify growth opportunities
- [ ] Plan content themes for next quarter
- [ ] Set quarterly growth targets

### 3. Infrastructure Review

**When:** Mid-quarter

**What to Review:**
- GitHub Actions usage and costs
- Supabase plan adequacy
- API cost projections
- Automation efficiency

**Action Items:**
- [ ] Analyze infrastructure costs
- [ ] Identify optimization opportunities
- [ ] Plan necessary upgrades
- [ ] Budget for next quarter

### 4. Disaster Recovery Test

**When:** End of quarter

**What to Test:**
- Database backup restoration
- Workflow manual triggering
- API failover procedures
- Error recovery processes

**Action Items:**
- [ ] Restore from backup to test environment
- [ ] Run all workflows manually
- [ ] Verify error handling works correctly
- [ ] Update disaster recovery documentation

### 5. Documentation Update

**When:** End of quarter

**What to Update:**
- CLAUDE.md with new patterns
- All SOP documents
- Troubleshooting guide
- API documentation

**Action Items:**
- [ ] Review and update all documentation
- [ ] Add new procedures discovered
- [ ] Remove outdated information
- [ ] Ensure all team members have access

---

## Specific Metrics to Monitor

### Critical Metrics (Check Daily)

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Daily Videos Created | 12 | <10 |
| Health Check Status | Healthy | Any unhealthy |
| Critical Errors | 0 | >0 |
| Platform Posting Success | 100% | <90% |

### Important Metrics (Check Weekly)

| Metric | Target | Review Threshold |
|--------|--------|------------------|
| Weekly Videos | 84 | <75 |
| API Response Time | <500ms | >1000ms |
| Error Resolution Time | <24h | >48h |
| Content Bank Level | 20+ per brand | <15 |

### Growth Metrics (Check Monthly)

| Metric | Target | Notes |
|--------|--------|-------|
| New Subscribers | +10% MoM | Track by brand |
| Video Views | +5% MoM | Track by platform |
| Engagement Rate | >3% | Likes+Comments/Views |
| A/B Test Completion | 4/month | Minimum tests |

---

## Related Procedures

- [Troubleshooting Guide](troubleshooting-guide.md)
- [Add New Pinterest Boards](add-new-pinterest-boards.md)
- [Add New Product Categories](add-new-product-categories.md)
- [Performance Monitoring](performance-monitoring.md)

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-27 | 1.0 | Initial creation |
