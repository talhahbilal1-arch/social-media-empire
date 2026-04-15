# Revenue Acceleration Sprint — Parallel Agent Execution

**Date:** 2026-04-15
**Branch:** `claude/build-insights-dashboard-Rbbvr`
**Goal:** Close every revenue-blocking gap identified in the insights report and ship the infrastructure that gets us to $10k/mo online passively.
**Strategy:** 8 parallel agents, non-overlapping file scopes, all committed to the same branch.

## Agent Work Packages

| # | Agent | Scope (non-overlapping) | Outputs |
|---|-------|-------------------------|---------|
| 1 | GitHub Workflows | `.github/workflows/*.yml` (new files only) | `daily-revenue-digest.yml`, `stale-branch-cleanup.yml`, `gumroad-sales-sync.yml`, `error-alerts.yml` |
| 2 | Playwright Automation | `automation/playwright/` (new directory) | `gumroad-zip-uploader.js`, `promptbase-lister.js`, `playwright.config.js`, `README.md` |
| 3 | Anti-Gravity Deploy | `anti_gravity/site/` + deploy scripts | `vercel.json`, `scripts/deploy_anti_gravity.sh`, README updates |
| 4 | MCP Installer | `docs/MCP_SETUP.md` + `scripts/install_mcps.sh` | One-command installer for all 10 recommended MCPs + token guide |
| 5 | $97 Signature Product | `products/signature/` (new directory) | Bundle manifest, landing page copy, Gumroad description, upsell logic |
| 6 | Search URL Converter | `scripts/convert_all_search_urls_v2.py` | Expanded ASIN dictionary + converter that handles 672 remaining URLs |
| 7 | Affiliate Signup Automator | `automation/affiliate_signups/` (new directory) | Playwright scripts for top-5 high-value programs + tracker |
| 8 | Enhanced Revenue Dashboard | `outputs/fitover35-website/dashboard/` | Real-time pulls from Supabase, Gumroad, GA4 endpoints + Pinterest clicks |

## Execution Order

1. Checkout branch (already on `claude/build-insights-dashboard-Rbbvr`)
2. Write this plan file
3. Spawn 8 parallel agents (all 8 in one tool-call batch)
4. Review each agent's outputs
5. Stage + commit batched by agent work package
6. Push branch

## Review Section

_Pending — will be populated with a summary of everything that shipped, files changed, and follow-ups the user must do manually (sign-ups requiring 2FA, entering API tokens, etc.)._
