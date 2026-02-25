# Autonomous Revenue Engine — Design Doc
**Date**: 2026-02-24
**Status**: Approved for implementation
**Goal**: Make the system fully autonomous, self-improving, self-healing, and continuously growing revenue without human input.

---

## Problem Statement

The system generates content and posts pins but earns almost no money because:
1. 70% of affiliate programs are PLACEHOLDER URLs — zero revenue from ShareASale, ClickBank, Impact, Rakuten
2. Email sequences (3 brands, 7 emails each) are **written but never connected to ConvertKit** — $0 from email
3. All 3 brands share one Amazon Associates tag (`dailydealdarl-20`) — can't track per-brand revenue
4. Zero revenue tracking tables in Supabase — blind to what converts
5. Self-healing workflow (`system-health.yml`) ignores revenue entirely

---

## Architecture: 4 Autonomous Agent Teams + Pipeline Fixes

### Track 1 — Pipeline Code Fixes (content-engine.yml)

| Fix | Lines | Impact |
|-----|-------|--------|
| Remove 60s Vercel deploy sleep | 236-237 | Unnecessary wait |
| Remove 30s inter-brand staggers | 363-365 | 30+ hours/year wasted |
| Parallelize 3-brand pin generation | 137+ | 3× faster Phase 1 |
| Parallelize 3 Vercel deploys | 434-458 | 3× faster deploys |

### Track 2 — 4 Agent Teams (new GitHub Actions workflows)

Each team is a Python script using `concurrent.futures.ThreadPoolExecutor` to run multiple Claude API calls in parallel, each with a specialized system prompt and role.

#### Team 1: Revenue Intelligence Engine
- **File**: `video_automation/revenue_intelligence.py`
- **Workflow**: `.github/workflows/revenue-intelligence.yml`
- **Schedule**: Daily 6AM PST
- **Agents**: analytics_reader, performance_analyzer, strategy_updater
- **Self-improving loop**: Reads GA4+GSC → scores content by revenue → rewrites `weekly_calendar` in Supabase → Content Engine reads it next run → more high-converting content made automatically

#### Team 2: Revenue Activation Team
- **File**: `video_automation/revenue_activation.py`
- **Workflow**: `.github/workflows/revenue-activation.yml`
- **Schedule**: Monday 9AM PST (also runs once immediately)
- **Agents**: email_activator, affiliate_discoverer, revenue_db_setup, tag_separator
- **Action**: Connects written email sequences to live ConvertKit; auto-discovers and applies to real affiliate programs; sets up per-brand Amazon tags; creates revenue tracking DB tables

#### Team 3: SEO Content Machine
- **File**: `video_automation/seo_content_machine.py`
- **Workflow**: `.github/workflows/seo-content-machine.yml`
- **Schedule**: Mon/Wed/Fri 8AM PST
- **Agents**: gsc_researcher, article_writer, internal_linker
- **Scales**: 45 articles → 150+ in 60 days → organic traffic compounds → more affiliate clicks

#### Team 4: Revenue-Aware Self-Healing Watchdog
- **File**: Enhanced `.github/workflows/system-health.yml`
- **Schedule**: Every 6 hours (already running)
- **New capabilities**: affiliate link validator, email delivery monitor, zero-revenue alert, Make.com scenario guard, auto-repair broken links with active alternatives

### New Database Tables (002_revenue_tracking.sql)
- `affiliate_revenue` — daily clicks + conversions + earnings per brand/program
- `email_conversions` — email → click → purchase attribution
- `content_performance` — pin/article → traffic → revenue score
- `affiliate_programs` — catalog of active + discovered programs

---

## The Autonomous Revenue Loop

```
Revenue Intelligence (daily 6AM)
  → reads GA4+GSC → scores content → updates weekly_calendar
Content Engine (5× daily, 15 pins/day)
  → reads weekly_calendar → makes content about top-earning topics
SEO Content Machine (3×/week)
  → generates pillar pages filling GSC keyword gaps → organic traffic scales
Revenue Activation (weekly Monday)
  → email sequences live → new affiliate programs enrolled → per-brand tags set
Self-Healing Watchdog (every 6h)
  → validates affiliate links → fixes 404s → verifies email delivery → alerts if $0 for 48h
  → feeds revenue data back to Intelligence → loop repeats
```

No human input required at any point.

---

## Revenue Projections (Conservative, 60 days)

| Source | Current | After 60 days |
|--------|---------|---------------|
| Amazon affiliate (3 brands) | ~$20-50/mo | ~$100-200/mo |
| Email sequences (LIVE) | $0 | +$200-600/mo |
| New affiliate programs | $0 | +$100-300/mo |
| Organic SEO (150+ articles) | ~$30/mo | +$150-400/mo |
| **Total** | ~$50-80/mo | **$550-1,500/mo** |

---

## Files Created/Modified

**Created:**
- `docs/plans/2026-02-24-autonomous-revenue-engine-design.md` (this file)
- `database/migrations/002_revenue_tracking.sql`
- `video_automation/revenue_intelligence.py`
- `video_automation/revenue_activation.py`
- `video_automation/seo_content_machine.py`
- `.github/workflows/revenue-intelligence.yml`
- `.github/workflows/revenue-activation.yml`
- `.github/workflows/seo-content-machine.yml`

**Modified:**
- `.github/workflows/content-engine.yml` (remove sleeps, parallelize)
- `.github/workflows/system-health.yml` (add revenue watchdog)
