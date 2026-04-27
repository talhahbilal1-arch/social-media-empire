# Workflow Health Report

Generated: 2026-04-27 17:37 UTC

## Summary

| Metric | Count |
|--------|-------|
| Active workflows | 40 |
| Archived workflows | 24 |
| Total | 64 |

| Scheduled (cron) | 34 |
| Event-driven (push/manual) | 6 |

## Scheduled Workflows

| Workflow | File | Schedule |
|----------|------|----------|
| Amazon ASIN Health Check | `asin-health-check.yml` | Daily 10:00 UTC |
| Analytics Collector | `analytics-collector.yml` | Daily 23:00 UTC |
| Check Affiliate Links | `check-affiliate-links.yml` | Mon 08:00 UTC |
| Content Engine | `content-engine.yml` | Daily 15:00 UTC, Daily 23:00 UTC, Daily 04:00 UTC |
| Daily Analytics | `daily-analytics.yml` | Daily 14:00 UTC |
| Daily Trend Scout | `daily-trend-scout.yml` | Daily 13:00 UTC |
| Email Automation | `email-automation.yml` | Daily 17:00 UTC, Daily 01:00 UTC |
| Emergency Alert (Dead Man's Switch) | `emergency-alert.yml` | Daily 08:00 UTC |
| Enable All Workflows + Run Pins | `enable-and-run.yml` | Daily 13:00 UTC |
| Etsy Product Pins | `etsy-product-pins.yml` | Daily 18:00 UTC |
| Fitness & Deals Articles | `fitness-articles.yml` | Mon/Tue/Wed/Thu/Fri 07:00 UTC |
| Menopause Weekly Newsletter | `menopause-newsletter.yml` | Wed 18:00 UTC |
| PilotTools Backlink Outreach | `toolpilot-outreach.yml` | Mon 15:00 UTC |
| PilotTools Content Repurposer | `toolpilot-repurpose.yml` | Daily 08:00 UTC |
| PilotTools Daily Content | `toolpilot-content.yml` | Mon/Tue/Wed/Thu/Fri 06:00 UTC |
| PilotTools LinkedIn Automation | `toolpilot-linkedin.yml` | Mon/Wed/Fri 18:00 UTC |
| PilotTools Newsletter | `toolpilot-newsletter.yml` | Mon 17:00 UTC |
| PilotTools Pinterest Automation | `toolpilot-pinterest.yml` | Daily 16:00 UTC, Daily 22:00 UTC |
| PilotTools Twitter Automation | `toolpilot-twitter.yml` | Daily 17:00 UTC, Daily 21:00 UTC, Daily 02:00 UTC |
| PilotTools Weekly Discovery | `toolpilot-weekly.yml` | Mon 07:00 UTC |
| PilotTools Weekly Report | `toolpilot-report.yml` | Sun 08:00 UTC |
| Pin Watchdog | `pin-watchdog.yml` | Every 1h at :30 |
| Pinterest Drop Alert | `pinterest-drop-alert.yml` | Daily 23:00 UTC |
| Post Product Pins | `post-product-pins.yml` | Mon/Thu 19:00 UTC |
| Post Sales Pins | `post-sales-pins.yml` | Tue/Wed/Fri 22:00 UTC |
| Revenue Activation Team | `revenue-activation.yml` | Mon 17:00 UTC |
| Revenue Intelligence Engine | `revenue-intelligence.yml` | Daily 15:00 UTC |
| SEO Content Machine | `seo-content-machine.yml` | Mon/Wed/Fri 16:00 UTC |
| Self-Improvement | `self-improve.yml` | Sun 06:00 UTC |
| Weekly Health Report | `weekly-health-report.yml` | Mon 16:00 UTC |
| Weekly SEO Ping | `seo-ping.yml` | Mon 06:00 UTC |
| Weekly Social Distribution | `social-distribution.yml` | Mon 02:00 UTC |
| Weekly Summary Report | `weekly-summary.yml` | Sun 17:00 UTC |
| Weekly Trend Discovery + Content Planning | `weekly-discovery.yml` | Mon 06:00 UTC |

## Event-Driven Workflows

| Workflow | File | Triggers |
|----------|------|----------|
| Article Format Guard | `article-guard.yml` | push |
| Auto Merge to Main | `auto-merge.yml` | manual, push |
| Deploy Brand Sites | `deploy-brand-sites.yml` | manual, callable |
| Deploy Subdomain Sites to Vercel | `subdomain-deploy.yml` | manual, push |
| PilotTools Deploy | `toolpilot-deploy.yml` | manual, push |
| Regenerate All Articles | `regenerate-articles.yml` | manual |

## Daily Schedule (UTC)

```
  01:00  Email Automation
  02:00  Weekly Social Distribution (Mon only)
  02:00  PilotTools Twitter Automation
  04:00  Content Engine
  06:00  Self-Improvement (Sun only)
  06:00  Weekly SEO Ping (Mon only)
  06:00  PilotTools Daily Content (Mon/Tue/Wed/Thu/Fri only)
  06:00  Weekly Trend Discovery + Content Planning (Mon only)
  07:00  Fitness & Deals Articles (Mon/Tue/Wed/Thu/Fri only)
  07:00  PilotTools Weekly Discovery (Mon only)
  08:00  Check Affiliate Links (Mon only)
  08:00  Emergency Alert (Dead Man's Switch)
  08:00  PilotTools Weekly Report (Sun only)
  08:00  PilotTools Content Repurposer
  10:00  Amazon ASIN Health Check
  13:00  Daily Trend Scout
  13:00  Enable All Workflows + Run Pins
  14:00  Daily Analytics
  15:00  Content Engine
  15:00  Revenue Intelligence Engine
  15:00  PilotTools Backlink Outreach (Mon only)
  16:00  SEO Content Machine (Mon/Wed/Fri only)
  16:00  PilotTools Pinterest Automation
  16:00  Weekly Health Report (Mon only)
  17:00  Email Automation
  17:00  Revenue Activation Team (Mon only)
  17:00  PilotTools Newsletter (Mon only)
  17:00  PilotTools Twitter Automation
  17:00  Weekly Summary Report (Sun only)
  18:00  Etsy Product Pins
  18:00  Menopause Weekly Newsletter (Wed only)
  18:00  PilotTools LinkedIn Automation (Mon/Wed/Fri only)
  19:00  Post Product Pins (Mon/Thu only)
  21:00  PilotTools Twitter Automation
  22:00  Post Sales Pins (Tue/Wed/Fri only)
  22:00  PilotTools Pinterest Automation
  23:00  Analytics Collector
  23:00  Content Engine
  23:00  Pinterest Drop Alert
  Every 1h  Pin Watchdog
```

## Archived Workflows

- `blog-factory.yml` — Blog Factory (ARCHIVED)
- `content-brain.yml` — Content Brain (ARCHIVED)
- `daily-report.yml` — Daily Report
- `email-automation.yml` — Email Automation
- `error-alerts.yml` — Error Monitoring
- `fitover35-blog-automation.yml` — Fit Over 35 Blog Automation
- `generate-fitover35-articles.yml` — Generate FitOver35 Article
- `health-monitor.yml` — Health Monitor (ARCHIVED)
- `health-monitoring.yml` — Health Monitoring
- `pinterest-analytics.yml` — Pinterest Analytics
- `rescue-poster.yml` — Pinterest Rescue Poster
- `self-healing.yml` — Self-Healing
- `system-health.yml` — System Health
- `tiktok-content.yml` — TikTok Content Pipeline
- `tiktok-poster.yml` — TikTok Video Poster
- `video-automation-evening.yml` — Video Automation - Evening (6 PM PST)
- `video-automation-morning.yml` — Video Automation - Morning (6 AM PST)
- `video-automation-noon.yml` — Video Automation - Noon (12 PM PST)
- `video-factory.yml` — Video Factory (ARCHIVED)
- `video-pins.yml` — Video Pin Generator
- `weekly-maintenance.yml` — Weekly Maintenance
- `weekly-summary.yml` — Weekly Summary Report
- `workflow-guardian.yml` — Workflow Guardian
- `youtube-fitness.yml` — YouTube Fitness Shorts
