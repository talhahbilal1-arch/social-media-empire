# Make.com Webhook Configuration

This document tracks all active Make.com webhooks and their GitHub secret mappings.

## Webhook Overview

All Make.com webhook URLs are stored as GitHub Secrets for security and are referenced in GitHub Actions workflows.

## Content Posters (Static Image Pins)

Three scenarios post static image pins to Pinterest (3x daily at 8AM/2PM/8PM PST):

| Brand | Scenario ID | Hook ID | GitHub Secret | Status | Last Updated |
|-------|-------------|---------|---------------|--------|--------------|
| Fitness Made Easy | 4261143 | 1944760 | `MAKE_WEBHOOK_FITNESS` | Active ✅ | 2026-02-28 |
| Daily Deal Darling | 4261294 | 1944762 | `MAKE_WEBHOOK_DEALS` | Active ✅ | 2026-02-28 |
| Menopause Planner | 4261296 | 1944763 | `MAKE_WEBHOOK_MENOPAUSE` | Active ✅ | 2026-02-28 |

## Video Posters (Remotion-Rendered Videos)

Three scenarios post Remotion-rendered video pins to Pinterest (daily at 10AM PST):

| Brand | Scenario ID | Hook ID | GitHub Secret | Status | Last Updated |
|-------|-------------|---------|---------------|--------|--------------|
| Fitness Made Easy | 4263862 | 1945946 | `MAKE_WEBHOOK_VIDEO_FITNESS` | Active ✅ | 2026-02-28 |
| Daily Deal Darling | 4263863 | 1945947 | `MAKE_WEBHOOK_VIDEO_DEALS` | Active ✅ | 2026-02-28 |
| Menopause Planner | 4263864 | 1945948 | `MAKE_WEBHOOK_VIDEO_MENOPAUSE` | Active ✅ | 2026-02-28 |

## Scenario Activator

One utility scenario reactivates poster scenarios on a schedule (called by `system-health.yml` every 2 hours):

| Purpose | Scenario ID | Hook ID | GitHub Secret | Status | Last Updated |
|---------|-------------|---------|---------------|--------|--------------|
| Reactivate all posters | 4261421 | 1944850 | `MAKE_WEBHOOK_ACTIVATOR` | Active ✅ | 2026-02-28 |

## GitHub Actions Integration

### Workflows Using These Webhooks

- **`content-engine.yml`** (3x/day): Calls content posters via `MAKE_WEBHOOK_*` secrets
- **`video-pins.yml`** (daily 10AM): Calls video posters via `MAKE_WEBHOOK_VIDEO_*` secrets
- **`system-health.yml`** (every 6h): Calls activator via `MAKE_WEBHOOK_ACTIVATOR`

### Secret List

To view all Make.com secrets in GitHub:

```bash
gh secret list | grep -i make
```

Expected output:
```
MAKE_WEBHOOK_ACTIVATOR              2026-02-28
MAKE_WEBHOOK_DEALS                  2026-02-28
MAKE_WEBHOOK_FITNESS                2026-02-28
MAKE_WEBHOOK_MENOPAUSE              2026-02-28
MAKE_WEBHOOK_VIDEO_DEALS            2026-02-28
MAKE_WEBHOOK_VIDEO_FITNESS          2026-02-28
MAKE_WEBHOOK_VIDEO_MENOPAUSE        2026-02-28
```

## Important Notes

1. **Webhook URLs are secret** — Never expose them in logs, pull requests, or public repos
2. **Hook Connections** — All hooks use existing Make.com connections (no new auth setup needed)
3. **Error Handling** — All poster scenarios have `builtin:Ignore` error handlers to stay active even if Pinterest rejects a pin
4. **Reactivation** — If a scenario becomes inactive, the Activator webhook will reactivate it (bypasses Cloudflare blocks on GitHub Actions)
5. **Rate Limits** — Pinterest has daily limits; monitor using `pinterest_analytics_scraper` tool in CLAW

## Troubleshooting

### Webhook Not Firing
- Check if scenario is active: `claw make scenarios_get {scenario_id}`
- Verify secret exists: `gh secret list | grep MAKE_WEBHOOK`
- Check GitHub Actions logs for error details

### Scenario Became Inactive
- The Activator scenario will reactivate it within 2 hours
- Or manually call: `claw make scenarios_activate {scenario_id}`

### 400 Bad Request on Webhook Call
- Verify pin data schema matches Make.com expectation
- Check Supabase `pinterest_pins` table for data integrity
- Review `content_engine.yml` phase 1b (webhook call) for issues

## References

- [Make.com Webhook Documentation](https://www.make.com/en/help/scenarios/webhooks)
- [Social Media Empire GitHub Workflows](.github/workflows/)
- [CLAW Project - Making Tools](../memory/MEMORY.md#project-claw-personal-ai-assistant)
