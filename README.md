# Social Media Content Empire

Fully autonomous social media content system that runs 24/7 without manual intervention.

## Architecture

```
TREND DISCOVERY (5 AM)      ← Finds trending products, topics, news
        ↓
CONTENT BRAIN (6 AM)        ← Generates content using AI + trends
        ↓
BLOG FACTORY (7 AM)         ← Creates SEO blog articles
        ↓
VIDEO FACTORY (8 AM)        ← Renders short-form videos
        ↓
MULTI-PLATFORM POSTER       ← Posts to Pinterest, YouTube, etc.
(9 AM, 1 PM, 9 PM)            (via Make.com for TikTok/Instagram)
        ↓
ANALYTICS COLLECTOR (11 PM) ← Tracks performance
        ↓
SELF-IMPROVEMENT (Weekly)   ← Optimizes everything automatically
        ↓
HEALTH MONITOR (Hourly)     ← Alerts only if something breaks
```

## Agents

| Agent | Schedule | Description |
|-------|----------|-------------|
| Trend Discovery | 5:00 AM | Finds trending topics from Amazon, Reddit, Google Trends, news |
| Content Brain | 6:00 AM | Uses Claude AI to generate 10-20 content pieces per brand |
| Blog Factory | 7:00 AM | Creates full SEO blog articles, publishes to Netlify |
| Video Factory | 8:00 AM | Renders videos using Creatomate |
| Multi-Platform Poster | 3x daily | Posts to Pinterest, YouTube (TikTok/IG via Make.com) |
| Analytics Collector | 11:00 PM | Collects engagement metrics |
| Self-Improvement | Sundays | Analyzes patterns, optimizes system automatically |
| Health Monitor | Hourly | Checks health, alerts only on failures |

## Setup

### 1. Run Database Schema

Copy `database/schema.sql` and run it in your Supabase SQL Editor.

### 2. Configure GitHub Secrets

Go to your repository → Settings → Secrets and add:

```
SUPABASE_URL          = https://your-project.supabase.co
SUPABASE_KEY          = your-anon-key

ANTHROPIC_API_KEY     = sk-ant-...

CREATOMATE_API_KEY    = your-creatomate-key (optional)

NETLIFY_API_TOKEN     = your-netlify-token (optional)
NETLIFY_SITE_ID       = your-site-id (optional)

YOUTUBE_API_KEY       = your-youtube-key (optional)

ALERT_EMAIL_FROM      = your-gmail@gmail.com
ALERT_EMAIL_PASSWORD  = gmail-app-password
ALERT_EMAIL_TO        = alerts@youremail.com
```

### 3. Push to GitHub

```bash
git init
git add .
git commit -m "Initial setup"
git remote add origin https://github.com/yourusername/social-media-empire.git
git push -u origin main
```

### 4. Enable GitHub Actions

Go to repository → Actions → Enable workflows

## Brands

Currently configured for:

1. **Daily Deal Darling** - Pinterest/Amazon affiliate (beauty, home, lifestyle)
2. **The Menopause Planner** - Etsy + Pinterest (menopause planners, wellness)

To add a new brand:
1. Add to `brands` table in Supabase
2. Add configuration in `agents/content_brain.py` BRAND_GUIDELINES
3. Add configuration in `agents/trend_discovery.py` BRAND_CONFIG
4. Add configuration in `agents/blog_factory.py` BRAND_CONFIG

## Make.com Integration

For TikTok and Instagram posting (which don't have easy APIs), use Make.com:

1. Create a scenario that triggers on schedule (9 AM, 1 PM, 9 PM)
2. Fetch pending content from Supabase using HTTP module
3. Post to TikTok/Instagram using their modules
4. Update post status in Supabase

## Costs

| Service | Estimated Monthly Cost |
|---------|----------------------|
| GitHub Actions | Free (2000 min/month) |
| Supabase | Free tier |
| Claude API | ~$5-20 |
| Creatomate | $39 (100 videos) |
| Make.com | $9-16 |
| **Total** | **~$55-75/month** |

## Monitoring

- Health Monitor runs hourly and emails you ONLY if something breaks
- Silence = everything working
- Check `health_checks` and `agent_runs` tables for history
- Check `system_changes` table for automatic optimizations

## Manual Triggers

You can manually trigger any agent from GitHub Actions:

1. Go to Actions tab
2. Select the workflow
3. Click "Run workflow"

## License

Private - All rights reserved
