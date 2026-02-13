# Performance Monitoring

## Overview

This Standard Operating Procedure outlines how to monitor, analyze, and optimize the performance of the Social Media Empire automation system. Effective performance monitoring ensures content reaches its intended audience, identifies issues before they impact growth, and provides data-driven insights for continuous improvement. This guide covers Pinterest analytics, content performance, system health, and revenue tracking.

## Prerequisites

- Pinterest Business account access with Analytics enabled
- Access to Supabase database dashboard
- Access to Make.com execution logs
- Access to Late API dashboard (if configured for Pinterest video posting)
- ConvertKit account access for email metrics
- Affiliate program dashboard access (Amazon Associates, etc.)
- Understanding of key performance indicators (KPIs)

---

## Why Performance Monitoring Matters

Regular monitoring enables you to:

1. **Detect Issues Early**: Catch posting failures, API errors, or content quality drops before they compound
2. **Optimize Content**: Identify what resonates with your audience and double down
3. **Maximize ROI**: Focus resources on high-performing categories and platforms
4. **Track Growth**: Measure progress against goals and adjust strategy
5. **Maintain System Health**: Ensure automation runs reliably without intervention

---

## Key Metrics to Track

### Pinterest Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Impressions | Times pins are shown | Growing MoM | -20% WoW |
| Saves | Users saving pins | 2%+ of impressions | <1% save rate |
| Outbound Clicks | Clicks to destination URL | 0.5%+ CTR | <0.2% CTR |
| Pin Clicks | Clicks to expand pin | 3%+ of impressions | <1.5% |
| Engagement Rate | (Saves + Clicks) / Impressions | 5%+ | <2% |
| Followers | Account followers | Growing | Declining |
| Monthly Views | 30-day profile views | Growing | -30% MoM |

### Content Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Posts per Day | Videos created and posted | 12 (3 per brand) | <10 |
| Posting Success Rate | Successful posts / attempts | >95% | <90% |
| Content Variety Score | Unique topics / total posts | >80% | <60% |
| Category Distribution | Posts per category | Even distribution | >50% in one category |
| A/B Test Completion | Tests run per month | 4+ tests | <2 tests |
| Hook Style Performance | Engagement by hook type | Track variance | N/A |

### System Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Error Rate | Errors / total operations | <5% | >10% |
| API Response Time | Average API latency | <500ms | >1000ms |
| Health Check Score | Healthy services / total | 100% | <80% |
| Workflow Success Rate | Successful runs / total | >98% | <95% |
| Make.com Operations | Monthly operation usage | <80% of limit | >90% of limit |
| Database Size | Supabase storage used | <80% of limit | >90% of limit |

### Revenue Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Affiliate Clicks | Clicks on affiliate links | Growing | -30% WoW |
| Conversion Rate | Purchases / clicks | 2%+ | <1% |
| Revenue per Pin | Earnings / pins posted | Track trend | Declining |
| Email Signups | New subscribers | Growing | Declining |
| Email Open Rate | Opens / delivered | >25% | <15% |
| Email Click Rate | Clicks / opens | >3% | <1.5% |

---

## How to Access Analytics

### Pinterest Analytics

**Method 1: Pinterest Analytics Dashboard**

1. Log into Pinterest Business account
2. Click "Analytics" in the top menu
3. Select "Overview" for summary metrics
4. Navigate to specific sections:
   - **Overview**: High-level performance
   - **Audience Insights**: Demographics and interests
   - **Conversion Insights**: Website activity (requires Pinterest tag)

**Key Reports to Review:**
- Top Pins (by impressions, saves, clicks)
- Audience demographics
- Traffic sources
- Best performing times

**Method 2: Export Data**

1. In Pinterest Analytics, click "Export"
2. Select date range (recommend last 30 days)
3. Download CSV for detailed analysis
4. Import to spreadsheet for trend tracking

**Method 3: Pinterest API (Advanced)**

```bash
# If using Pinterest API directly
python -c "
from utils.api_clients import PinterestClient
client = PinterestClient()
analytics = client.get_analytics(
    start_date='2026-01-01',
    end_date='2026-01-28',
    metrics=['IMPRESSION', 'SAVE', 'PIN_CLICK', 'OUTBOUND_CLICK']
)
print(analytics)
"
```

### Supabase Performance Dashboards

**Access Database Metrics:**

1. Log into Supabase dashboard
2. Navigate to your project
3. Click "Reports" in the sidebar
4. Review:
   - Database size
   - API requests
   - Storage usage
   - Connection count

**Custom Performance Queries:**

```sql
-- Daily video creation summary
SELECT
    DATE(created_at) as date,
    brand,
    COUNT(*) as videos_created,
    COUNT(CASE WHEN status = 'posted' THEN 1 END) as successfully_posted,
    ROUND(COUNT(CASE WHEN status = 'posted' THEN 1 END)::numeric / COUNT(*) * 100, 2) as success_rate
FROM videos
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at), brand
ORDER BY date DESC, brand;

-- Error frequency by type
SELECT
    error_type,
    COUNT(*) as error_count,
    MAX(created_at) as last_occurrence
FROM errors
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY error_type
ORDER BY error_count DESC;

-- Content category performance
SELECT
    content_category,
    brand,
    COUNT(*) as total_posts,
    COUNT(CASE WHEN status = 'posted' THEN 1 END) as successful,
    ROUND(AVG(CASE WHEN status = 'posted' THEN 1.0 ELSE 0.0 END) * 100, 2) as success_rate
FROM videos
WHERE content_category IS NOT NULL
AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY content_category, brand
ORDER BY total_posts DESC;
```

**Automated Daily Queries:**

```bash
# Run from command line
python -c "
from database.supabase_client import get_supabase_client
from datetime import datetime, timedelta

db = get_supabase_client()

# Get daily stats
stats = db.get_daily_stats()
print('=== Daily Performance ===')
print(f'Videos Created: {stats[\"videos_created\"]}')
print(f'Successful Posts: {stats[\"successful_posts\"]}')
print(f'Success Rate: {stats[\"success_rate\"]}%')
print(f'Errors: {stats[\"error_count\"]}')

# Get brand breakdown
print('\n=== By Brand ===')
for brand, count in stats['videos_by_brand'].items():
    print(f'  {brand}: {count} videos')
"
```

### Make.com Execution Logs

**Access Execution History:**

1. Log into Make.com
2. Navigate to "Scenarios"
3. Click on the relevant scenario
4. Select "History" tab
5. Review execution status and details

**Key Information to Check:**
- Execution success/failure status
- Error messages for failed runs
- Data transferred
- Operations consumed
- Execution duration

**Monthly Operations Report:**

1. Go to Make.com dashboard
2. Click your organization/team
3. View "Operations" usage
4. Check current usage vs. plan limit

**Export Execution Data:**

1. In scenario History, filter by date range
2. Click export (if available)
3. Or use Make.com API for programmatic access

### Late API Logs (If Configured)

If using Late API for Pinterest video posting:

```bash
python -c "
from src.clients.late_api import LateAPIClient

client = LateAPIClient()
if client.is_configured():
    # Get recent posting history
    history = client.get_posting_history(days=7)
    print('=== Late API Posting History ===')
    for post in history:
        print(f'{post[\"date\"]}: {post[\"status\"]} - {post[\"platform\"]}')
else:
    print('Late API not configured')
"
```

---

## Interpretation Guidelines

### What's Good Performance?

**Pinterest Pin Performance (Per Pin Average):**

| Performance Level | Impressions | Save Rate | CTR |
|-------------------|-------------|-----------|-----|
| Excellent | 1000+ | 5%+ | 1%+ |
| Good | 500-1000 | 2-5% | 0.5-1% |
| Average | 100-500 | 1-2% | 0.2-0.5% |
| Below Average | <100 | <1% | <0.2% |

**System Performance:**

| Performance Level | Success Rate | Error Rate | Response Time |
|-------------------|--------------|------------|---------------|
| Excellent | >99% | <1% | <300ms |
| Good | 95-99% | 1-5% | 300-500ms |
| Acceptable | 90-95% | 5-10% | 500-1000ms |
| Needs Attention | <90% | >10% | >1000ms |

### What's Bad Performance?

**Red Flags Requiring Immediate Action:**

1. **Posting Success Rate < 80%**: Investigate API failures, credential issues
2. **Error Rate > 20%**: System-wide issue, check health status
3. **Zero Impressions on Recent Pins**: Pinterest account issue or shadowban
4. **Sudden Engagement Drop > 50%**: Algorithm change or content issue
5. **API Response Time > 2000ms**: Network or service degradation

**Warning Signs Requiring Investigation:**

1. **Declining Impressions Week over Week**: Content quality or timing issue
2. **Save Rate Below 1%**: Content not resonating with audience
3. **High Unfollows**: Content frequency or quality issue
4. **Content Variety < 60%**: Repetitive topics, refresh content bank
5. **A/B Tests Not Completing**: Test setup or volume issues

---

## When to Make Changes

### Change Thresholds

| Metric | Review Threshold | Change Threshold | Urgent Action |
|--------|------------------|------------------|---------------|
| Weekly Impressions | -10% | -20% | -50% |
| Save Rate | <2% | <1% | <0.5% |
| Posting Success | <98% | <95% | <90% |
| Error Rate | >3% | >5% | >10% |
| Content Variety | <80% | <70% | <50% |

### Decision Framework

**Before making changes, ask:**

1. **Is it significant?** Single data points can be noise; look for trends over 7+ days
2. **Is it consistent?** Check if issue affects all brands or specific ones
3. **Is it actionable?** Can you actually influence this metric?
4. **Is it isolated?** External factors (holidays, platform issues) may be the cause

**Change Priority Matrix:**

| Impact | Urgency | Action |
|--------|---------|--------|
| High | High | Immediate fix (same day) |
| High | Low | Scheduled fix (this week) |
| Low | High | Quick fix if easy, else schedule |
| Low | Low | Add to backlog |

---

## A/B Testing Procedures

### What to Test

**High-Impact Tests:**
1. Hook styles (question vs. statement vs. curiosity gap)
2. Video thumbnail/first frame
3. Posting times
4. Hashtag sets
5. Description formats

**Medium-Impact Tests:**
1. Content categories
2. Video length variations
3. Call-to-action phrases
4. Color schemes
5. Music/audio choices

### How to Set Up A/B Tests

**Step 1: Define the Test**

```python
# Example test configuration
test_config = {
    "test_name": "hook_style_comparison",
    "brand": "daily_deal_darling",
    "variable": "hook_style",
    "variants": {
        "A": "question_hook",      # "Want to know the secret to..."
        "B": "statement_hook"       # "This $10 find changed everything"
    },
    "sample_size": 20,              # Posts per variant
    "primary_metric": "save_rate",
    "secondary_metrics": ["impressions", "clicks"],
    "duration_days": 14
}
```

**Step 2: Implement the Test**

```bash
# Using built-in A/B testing module
python -c "
from video_automation.ab_testing import ABTestManager

manager = ABTestManager()
test_id = manager.create_test(
    name='Hook Style Test Q1',
    brand='daily_deal_darling',
    variable='hook_style',
    variants=['question', 'statement'],
    sample_size=20
)
print(f'Test created: {test_id}')
"
```

**Step 3: Monitor the Test**

```bash
# Check test progress
python -c "
from video_automation.ab_testing import ABTestManager

manager = ABTestManager()
status = manager.get_test_status('Hook Style Test Q1')
print(f'Progress: {status[\"progress\"]}%')
print(f'Variant A posts: {status[\"variant_a_count\"]}')
print(f'Variant B posts: {status[\"variant_b_count\"]}')
"
```

**Step 4: Analyze Results**

```bash
# Get test results
python -c "
from video_automation.ab_testing import ABTestManager

manager = ABTestManager()
results = manager.analyze_test('Hook Style Test Q1')
print('=== Test Results ===')
print(f'Winner: Variant {results[\"winner\"]}')
print(f'Confidence: {results[\"confidence\"]}%')
print(f'Lift: {results[\"lift\"]}%')
print(f'Recommendation: {results[\"recommendation\"]}')
"
```

### Statistical Significance

- Minimum sample size: 20 posts per variant
- Minimum test duration: 7 days
- Required confidence level: 95%
- Effect size threshold: 10% improvement

---

## Weekly Review Process

### When: Every Monday Morning (30-45 minutes)

### Checklist

**1. Gather Metrics (10 minutes)**

```bash
# Generate weekly report
python -m monitoring.daily_report_generator --weekly
```

Or manually collect:
- [ ] Pinterest Analytics export (last 7 days)
- [ ] Supabase video creation stats
- [ ] Error summary from monitoring
- [ ] Make.com operations usage
- [ ] Email subscriber count

**2. Review Dashboard (10 minutes)**

| Metric | Last Week | This Week | Change | Status |
|--------|-----------|-----------|--------|--------|
| Videos Created | | | | |
| Success Rate | | | | |
| Pinterest Impressions | | | | |
| Pinterest Saves | | | | |
| Pinterest CTR | | | | |
| Error Count | | | | |
| New Subscribers | | | | |

**3. Identify Issues (10 minutes)**

- [ ] Any metrics below threshold?
- [ ] Any brand underperforming?
- [ ] Any category underperforming?
- [ ] Any recurring errors?
- [ ] Any A/B tests to conclude?

**4. Plan Actions (10 minutes)**

For each identified issue:
1. Root cause hypothesis
2. Proposed fix
3. Timeline
4. Owner

**5. Document (5 minutes)**

Record in weekly tracking document:
- Key metrics
- Issues identified
- Actions taken
- Notes for next week

---

## Monthly Review Process

### When: First Monday of Each Month (2-3 hours)

### Agenda

**1. Monthly Metrics Summary (30 minutes)**

Create comprehensive report:

```sql
-- Monthly performance summary
SELECT
    TO_CHAR(created_at, 'YYYY-MM') as month,
    brand,
    COUNT(*) as total_videos,
    COUNT(CASE WHEN status = 'posted' THEN 1 END) as successful,
    ROUND(AVG(CASE WHEN status = 'posted' THEN 1.0 ELSE 0.0 END) * 100, 2) as success_rate
FROM videos
WHERE created_at >= NOW() - INTERVAL '3 months'
GROUP BY TO_CHAR(created_at, 'YYYY-MM'), brand
ORDER BY month DESC, brand;
```

**2. Platform Performance Analysis (30 minutes)**

For each platform (Pinterest, YouTube, etc.):
- Top performing content
- Worst performing content
- Audience growth
- Engagement trends

**3. Content Analysis (30 minutes)**

- Best performing categories
- Hook styles analysis
- Topic freshness review
- Content bank health check

**4. System Health Review (20 minutes)**

- Error trends and resolution
- API usage and costs
- Infrastructure performance
- Security review

**5. Revenue Analysis (20 minutes)**

- Affiliate earnings by brand
- Email conversion rates
- Cost per acquisition trends
- ROI calculations

**6. Planning (30 minutes)**

- Quarterly goal progress
- Next month priorities
- Resource allocation
- Test planning

---

## Automated Monitoring Setup

### Daily Automated Report

Configure in `.github/workflows/daily-report.yml`:

```yaml
name: Daily Performance Report
on:
  schedule:
    - cron: '0 6 * * *'  # 6 AM UTC daily

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate Report
        run: python -m monitoring.daily_report_generator
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
      - name: Send Report
        run: python -m monitoring.email_report
```

### Alert Thresholds

Configure alerts in `/monitoring/alert_config.py`:

```python
ALERT_THRESHOLDS = {
    "critical": {
        "success_rate": 80,       # Alert if below 80%
        "error_rate": 20,         # Alert if above 20%
        "health_score": 60        # Alert if below 60
    },
    "warning": {
        "success_rate": 95,
        "error_rate": 10,
        "health_score": 80
    }
}
```

### Custom Dashboard (Optional)

For real-time monitoring, consider setting up:

1. **Supabase Dashboard**: Custom SQL queries on schedule
2. **Grafana**: Connect to Supabase for visualizations
3. **Simple HTML Dashboard**: Generated daily with metrics

---

## Troubleshooting Performance Issues

### Low Impressions

**Possible Causes:**
1. Pinterest algorithm changes
2. Content not SEO-optimized
3. Posting time not optimal
4. Account reach limited

**Diagnostic Steps:**
1. Check Pinterest Analytics for reach changes
2. Review recent pin keywords and descriptions
3. Compare posting times to audience activity
4. Check for any Pinterest notifications

**Solutions:**
1. Refresh keywords and descriptions
2. Adjust posting schedule
3. Increase content quality signals
4. Diversify content topics

### Low Engagement

**Possible Causes:**
1. Content not resonating
2. Wrong audience targeting
3. Visual quality issues
4. Call-to-action unclear

**Diagnostic Steps:**
1. Review top performing pins vs. underperformers
2. Analyze audience insights
3. Review video thumbnail quality
4. Check CTA clarity

**Solutions:**
1. A/B test different content styles
2. Refine audience targeting
3. Improve video production
4. Strengthen call-to-action

### High Error Rate

See [Troubleshooting Guide](troubleshooting-guide.md) for detailed error resolution.

---

## Related Procedures

- [Weekly Maintenance Checklist](weekly-maintenance-checklist.md)
- [Troubleshooting Guide](troubleshooting-guide.md)
- [Add New Pinterest Boards](add-new-pinterest-boards.md)
- [Add New Product Categories](add-new-product-categories.md)

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-28 | 1.0 | Initial creation |
