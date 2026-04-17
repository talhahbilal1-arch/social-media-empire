# Make.com Scenario Health Audit — 2026-04-16

**Report Generated:** 2026-04-16  
**Audit Period:** 7-day active, 30-day inactive lookback  
**Team ID:** 1686661  
**Total Scenarios Audited:** 18

---

## Executive Summary

- **Active Core Scenarios:** 9 (all operational, ~440 ops in 7 days)
- **Estimated Monthly Burn:** ~1,880 operations
- **Failed Migrations:** 4 scenarios (v5/v7 versions with persistent errors)
- **Zombies:** 2 scenarios (0 ops in 30 days, safe to delete)
- **Recommended for Deletion:** 7 scenarios (failed migrations + zombies)

---

## Active Core Scenarios — 7-Day Health

| Scenario ID | Name | 7d Execs | Success Rate | Ops in 7d | Avg Ops/Exec | Last Success |
|---|---|---|---|---|---|---|
| 4261421 | 9am Deals Pin | 48 | 100% (48/48) | 96 | 2.0 | 2026-04-16 07:12 |
| 4261294 | 9am Fitness Pin | 47 | 100% (47/47) | 94 | 2.0 | 2026-04-16 07:12 |
| 4261143 | 9am Menopause Pin | 47 | 100% (47/47) | 94 | 2.0 | 2026-04-16 07:12 |
| 4261296 | 7pm Deals Pin Apr7 | 50 | 100% (50/50) | 100 | 2.0 | 2026-04-16 07:12 |
| 4726262 | Post NOW Deals | 8 | 100% (8/8) | 16 | 2.0 | 2026-04-16 06:45 |
| 4263862 | Video Poster—Deals (v4) | 2 | 100% (2/2) | 4 | 2.0 | 2026-04-13 12:30 |
| 4726259 | Post NOW Fitness | 8 | 100% (8/8) | 16 | 2.0 | 2026-04-16 06:45 |
| 4263864 | Video Poster—Menopause (v4) | 2 | 100% (2/2) | 4 | 2.0 | 2026-04-13 12:30 |
| 4726264 | Post NOW Menopause | 8 | 100% (8/8) | 16 | 2.0 | 2026-04-16 06:45 |

**Total 7-Day Operations:** 440  
**Estimated Monthly Operations:** ~1,880 (assuming stable daily burn)

---

## Failed Migrations — v5/v7 Versions

### Pattern: HTTP Download Failures (v5 Era)

| Scenario ID | Name | Version | Last Exec | Error Pattern | Issue |
|---|---|---|---|---|---|
| 4669524 | Create Video Pin—Deals | v5 | 2026-04-09 | HTTP 404 DownloadFile service | Media download failure; pin creation blocked |
| 4671823 | Create Video Pin—Fitness | v5 | 2026-04-09 | HTTP 404 DownloadFile service | Media download failure; pin creation blocked |
| 4671827 | Create Video Pin—Menopause | v5 | 2026-04-09 | HTTP 404 DownloadFile service | Media download failure; pin creation blocked |

**Root Cause:** v5 scenarios rely on external DownloadFile module that returns 404. Service appears unreachable or deprecated.

### Pattern: Pinterest API Validation Failures (v7 Era)

| Scenario ID | Name | Version | Last Exec | Error Pattern | Issue |
|---|---|---|---|---|---|
| 4732882 | Post Remotion Video—Deals v2 | v7 | 2026-04-15 | Missing `cover_image` parameter | Pinterest API requires cover image; not provided by module |
| 4732899 | Post Remotion Video—Fitness v2 | v7 | 2026-04-15 | Missing `cover_image` parameter | Pinterest API requires cover image; not provided by module |
| 4732903 | Post Remotion Video—Menopause v2 | v7 | 2026-04-15 | Missing `cover_image` parameter | Pinterest API requires cover image; not provided by module |

**Root Cause:** v7 scenarios generate Remotion-rendered video pins but fail to upload media to Pinterest before attempting pin creation. Missing `media_id` and cover image parameter.

---

## Zombie Scenarios — 0 Operations in 30 Days

| Scenario ID | Name | Version | Last Exec | 30d Ops | Status |
|---|---|---|---|---|---|
| 3840951 | Register Video—Deals | v3 | 2026-01-15 | 0 | **ZOMBIE** — no activity in 90+ days |
| 3963775 | Register Video—Fitness | v3 | 2026-01-15 | 0 | **ZOMBIE** — no activity in 90+ days |

**Recommendation:** Safe to delete. No recent executions, no error spikes. Appears dormant since v3→v4 migration.

---

## Anomaly: Video Poster Scenarios (v4 Era)

| Scenario ID | Name | Status | Observation |
|---|---|---|---|
| 4263862 | Video Poster—Deals (v4) | Active but dormant | Last exec: 2026-04-13 (~3 days ago). Only 2 execs in 7d window. Expected higher frequency. **Investigate:** Does this require manual triggering? |
| 4263864 | Video Poster—Menopause (v4) | Active but dormant | Last exec: 2026-04-13 (~3 days ago). Only 2 execs in 7d window. Expected higher frequency. **Investigate:** Does this require manual triggering? |

These scenarios are operational (100% success rate) but significantly underutilized compared to 9am/7pm scheduled pins.

---

## Operations Budget Summary

**Metrics:**
- Total ops (7d): 440
- Daily average: ~63 ops
- Monthly projection: ~1,880 ops
- Utilization: Monitor against Make.com plan limits

**Burn Breakdown:**
- Scheduled pins (9am/7pm): ~284 ops (64.5%)
- Manual pins (NOW): ~48 ops (10.9%)
- Video posters (v4): ~8 ops (1.8%)
- Inactive/error scenarios: 0 ops

---

## Recommended Deletions

**Category 1: Failed v5 Migrations (HTTP Download Failures)**
- **4669524** — Create Video Pin—Deals (v5)
- **4671823** — Create Video Pin—Fitness (v5)
- **4671827** — Create Video Pin—Menopause (v5)

*Rationale:* All three v5 scenarios consistently fail with HTTP 404 DownloadFile errors. No successful executions in 7+ days. Migrated away to v7 (post-Remotion) but v5 remains broken. Safe to delete.

**Category 2: Failed v7 Migrations (Pinterest API Validation)**
- **4732882** — Post Remotion Video—Deals v2 (v7)
- **4732899** — Post Remotion Video—Fitness v2 (v7)
- **4732903** — Post Remotion Video—Menopause v2 (v7)

*Rationale:* All three v7 scenarios consistently fail with missing `cover_image` parameter when calling Pinterest API. No successful pin creation in 7+ days. Blocked on media upload workflow. Recommend redesign or rollback to v4 video posters.

**Category 3: Zombies (No Activity in 30+ Days)**
- **3963775** — Register Video—Fitness (v3)

*Rationale:* Zero operations in 30-day window. Last execution 2026-01-15 (90+ days ago). Orphaned from v3→v4 migration. Safe to delete.

**Total Recommended Deletions:** 7 scenarios

---

## Next Steps

1. **Immediate:** Delete 7 failed scenarios (Categories 1–3 above).
2. **Short-term:** Investigate v4 video posters (4263862, 4263864) — determine if manual trigger is expected.
3. **Medium-term:** Redesign v7 Remotion workflow to include media upload before pin creation (or rollback to v4 pattern).
4. **Ongoing:** Monitor scheduled pins (9am/7pm) for error spikes; all currently at 100% success.

---

**End of Report**
