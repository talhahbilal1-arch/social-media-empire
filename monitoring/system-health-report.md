# System Health Report

Generated: 2026-03-31

## Make.com Scenarios (9 Active, 0 Errors)

| ID | Name | Executions | Errors | Status |
|----|------|-----------|--------|--------|
| 3840951 | Integration Webhooks | 0 | 0 | Active (webhook-triggered) |
| 4261421 | Scenario Activator | 425 | 0 | Active, healthy |
| 4261143 | Pinterest Fitness v3 | 167 | 0 | Active, healthy |
| 4261294 | Pinterest Deals v4 | 383 | 0 | Active, healthy |
| 4261296 | Pinterest Menopause v4 | 383 | 0 | Active, healthy |
| 4263862 | Video Pin Fitness | 24 | 0 | Active, healthy |
| 4263863 | Video Pin Deals | 24 | 0 | Active, healthy |
| 4263864 | Video Pin Menopause | 23 | 0 | Active, healthy |
| 3963775 | TikTok Video Automation | 0 | 0 | Active (webhook-triggered, awaiting first trigger) |

**Cleanup performed:** 29 inactive scenarios with 0 executions deleted on 2026-03-31.

**Total operations used:** 2,904 ops across all scenarios
**Total errors:** 0 (clean across all scenarios)

## Notes

- Integration Webhooks (3840951) and TikTok Video Automation (3963775) show 0 executions but are webhook-triggered — they fire only when called externally
- Pinterest posters (Deals v4 and Menopause v4) have highest execution counts (383 each) — these are the primary content distribution engines
- Video Pin posters are newer (created Feb 28) with 23-24 executions each — running normally
- Scenario Activator has 425 executions — the meta-orchestrator that triggers other scenarios

## GitHub Actions Workflows

38+ workflows exist in `.github/workflows/`. Key active ones include:
- content-engine.yml — Content generation pipeline
- deploy-brand-sites.yml — Site deployment
- video-automation-morning.yml — Daily video automation
- system-health.yml — System monitoring
- seo-ping.yml — Weekly SEO sitemap ping (newly created)

## Content Infrastructure

| Brand | Articles | Sitemap | Status |
|-------|---------|---------|--------|
| FitOver35 | 142 | Updated (148 URLs) | Healthy |
| DailyDealDarling | 95 | Updated (99 URLs) | Healthy |
| MenopausePlanner | 82 | Updated (86 URLs) | Healthy |
| PilotTools | 35 tools, 29 comparisons, 25 articles | Existing | Healthy |
| Anti-Gravity | 5 seed articles | Pending deploy | New |
