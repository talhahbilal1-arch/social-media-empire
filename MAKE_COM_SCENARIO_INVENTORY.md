# Make.com Scenario Inventory — Rebuild v2
*Updated: 2026-02-26*

## Architecture Overview

3-stage hybrid pipeline. Make.com handles content generation + Pinterest posting; GitHub Actions handles image rendering + article generation + Vercel deploy.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: Make.com Content Generator (every 4h)                          │
│   → Claude API generates 3 pins (one per brand)                         │
│   → HTTP POST to Supabase pinterest_pins (status='content_ready')       │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│ STAGE 2: GitHub Actions content-engine.yml (3x/day: 8AM/2PM/8PM PST)   │
│   Phase 1 — Reads content_ready pins → Pexels fetch → PIL render        │
│              → Supabase Storage upload → status='ready'                 │
│   Phase 2 — Generate SEO article per pin → save to outputs/             │
│   Phase 3 — Git commit + push articles → Vercel auto-deploy             │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│ STAGE 3: Make.com Pin Posters × 3 (every 3h per brand)                  │
│   → Read status='ready' pins → status='posting' lock                    │
│   → Pinterest Create Pin → status='posted' | 'failed'                  │
└─────────────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│ SUPPORT: Make.com Health Monitor (every 12h)                             │
│   → Bulk retry failed pins → mark dead (≥3 retries)                    │
│   → Send Telegram summary report                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

**Status values**: `content_ready` → `rendering` → `ready` → `posting` → `posted` / `failed` → `dead`

---

## Active Scenarios — Rebuild v2

### 1. Pin Content Generator v2
| Field | Value |
|-------|-------|
| **Scenario ID** | 4243147 |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4243147/edit` |
| **Schedule** | Every 4 hours (14400s) |
| **Status** | ✅ Active — created + activated 2026-02-26 |
| **Ops/month** | ~1,260 (7 ops/run × 6 runs/day × 30 days) |

**Flow** (4 modules):
1. HTTP POST → Anthropic API (`/v1/messages`, claude-sonnet-4-6) — generate 3 pins as JSON object
2. HTTP POST → Supabase `pinterest_pins` (deals, `status='content_ready'`)
3. HTTP POST → Supabase `pinterest_pins` (menopause, `status='content_ready'`)
4. HTTP POST → Supabase `pinterest_pins` (fitness, `status='content_ready'`)

**Claude output parsed inline** using Make.com `json()` function:
`{{json(1.data.content[0].text).deals.title}}`

---

### 2. Pin Poster — DailyDealDarling v2
| Field | Value |
|-------|-------|
| **Scenario ID** | 4243032 |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4243032/edit` |
| **Brand** | `deals` |
| **Pinterest Connection** | Daily Deal Darling (conn 6738173) |
| **Schedule** | Every 3 hours (10800s) |
| **Status** | ✅ Active — created + activated 2026-02-26 |
| **Ops/month** | ~1,000 |

**Flow** (5 modules + error handler):
1. HTTP GET → Supabase `pinterest_pins?brand=eq.deals&status=eq.ready&order=created_at.asc&limit=1`
2. HTTP PATCH → set `status='posting'` (filter: result not empty)
3. Pinterest Create Pin (conn 6738173) — `image_url`, `title`, `description`, `link`, `board_id` from pin row
4. HTTP PATCH → set `status='posted'`, `pinterest_pin_id`, `posted_at`
5. Error handler: HTTP PATCH → set `status='failed'`, `error_message`, `retry_count+1` + Break (3 retries, 5s interval)

---

### 3. Pin Poster — MenopausePlanner v2
| Field | Value |
|-------|-------|
| **Scenario ID** | 4243035 |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4243035/edit` |
| **Brand** | `menopause` |
| **Pinterest Connection** | TheMenopausePlanner (conn 6857103) |
| **Schedule** | Every 3 hours (10800s) |
| **Status** | ✅ Active — created + activated 2026-02-26 |
| **Ops/month** | ~1,000 |

**Flow**: Same as DailyDealDarling v2, filtered to `brand=eq.menopause`.

---

### 4. Pin Poster — FitOver35 v2
| Field | Value |
|-------|-------|
| **Scenario ID** | 4243036 |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4243036/edit` |
| **Brand** | `fitness` |
| **Pinterest Connection** | Fitness Made Easy (conn 7146197) |
| **Schedule** | Every 3 hours (10800s) |
| **Status** | ⏸ INACTIVE — pending Pinterest connection re-auth |
| **Ops/month** | ~1,000 (once active) |

**Action required**: Go to Make.com → Connections → "Fitness Made Easy" (ID 7146197) → Re-authorize.
Then activate: `POST /api/v2/scenarios/4243036/start?teamId=1686661`

**Flow**: Same as DailyDealDarling v2, filtered to `brand=eq.fitness`.

---

### 5. Pin Health Monitor v2
| Field | Value |
|-------|-------|
| **Scenario ID** | 4243206 |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4243206/edit` |
| **Schedule** | Every 12 hours (43200s) |
| **Status** | ✅ Active — created + activated 2026-02-26 |
| **Ops/month** | ~480 (8 ops/run × 2 runs/day × 30 days) |

**Flow** (6 modules):
1. HTTP PATCH → Supabase bulk retry: `status='ready'` where `status=failed AND retry_count<3`
2. HTTP PATCH → Supabase bulk dead: `status='dead'` where `status=failed AND retry_count>=3`
3. HTTP GET → count `posted` pins (last 24h)
4. HTTP GET → count `failed` pins (last 24h)
5. HTTP GET → count `ready` pins (pending post)
6. HTTP POST → Telegram Bot API (chat_id 8090293231) — daily summary

---

## Total Ops Budget

| Scenario | Ops/Month |
|----------|-----------|
| Content Generator (4243147) | ~1,260 |
| Poster — DDD (4243032) | ~1,000 |
| Poster — TMP (4243035) | ~1,000 |
| Poster — FO35 (4243036) | ~1,000 |
| Health Monitor (4243206) | ~480 |
| **Total** | **~4,740** |
| Plan limit | 10,000 |
| Headroom | 53% |

---

## Pinterest Connections

| Brand | Connection ID | Account | Default Board ID |
|-------|--------------|---------|-----------------|
| Daily Deal Darling | 6738173 | DailyDealDarlin | 874683627569021288 |
| Menopause Planner | 6857103 | TheMenopausePlanner | 1076993767079887530 |
| Fit Over 35 | 7146197 | pinterest2 (needs re-auth) | 418834902785123337 |

---

## Old Scenarios (Archived)

These were the CLAW v2 webhook-based scenarios. Webhook posters (4210274, 4210434) still active
but unused — to be deactivated after 24h verified operation of rebuild v2.

| ID | Name | Status | Notes |
|----|------|--------|-------|
| 4210216 | FitOver35 Webhook Poster | ❌ Inactive/invalid | Replaced by 4243036 |
| 4210274 | DailyDealDarling Webhook Poster | ⚠️ Active, unused | Deactivate after 24h soak test |
| 4210434 | MenopausePlanner Webhook Poster | ⚠️ Active, unused | Deactivate after 24h soak test |
| 4210597 | Retry Failed Pins | ❌ Deactivated 2026-02-26 | Replaced by Health Monitor 4243206 |
| 4210643 | Daily Health Report | ❌ Inactive/invalid | Replaced by Health Monitor 4243206 |
| 3715423 | Agent 1 Discovery + Scoring | ❌ Deactivated 2026-02-26 | Was burning 8,640 ops/month |
| 3763471 | Agent 2 Creative Engine | ❌ Deactivated 2026-02-26 | Was burning 8,640 ops/month |
| 3977247 | Pinterest Pin Publisher - All Brands | ❌ Deactivated 2026-02-24 | Original single-webhook scenario |

---

## Phase 6 Cutover Checklist

After 24h verified posting from DDD + TMP (and FO35 once re-authed):

- [ ] Deactivate 4210274 (DDD webhook poster): `POST /api/v2/scenarios/4210274/stop`
- [ ] Deactivate 4210434 (TMP webhook poster): `POST /api/v2/scenarios/4210434/stop`
- [ ] Remove GitHub secrets no longer needed: `MAKE_WEBHOOK_FITNESS`, `MAKE_WEBHOOK_DEALS`, `MAKE_WEBHOOK_MENOPAUSE`
- [ ] Activate FO35 poster (4243036) after Pinterest connection 7146197 re-auth

---

## Activation Log

| Date | Action |
|------|--------|
| 2026-02-24 | Scenarios 3715423 + 3763471 deactivated (saved ~17,280 ops/month) |
| 2026-02-24 | Scenario 4210597 (retry) deactivated |
| 2026-02-24 | Old scenario 3977247 deactivated |
| 2026-02-24 | CLAW v2 scenarios 4210216 / 4210274 / 4210434 verified posting end-to-end |
| 2026-02-26 | Rebuild v2: 5 new scenarios created via Make.com REST API |
| 2026-02-26 | Scenario 4243147 (Content Generator) activated |
| 2026-02-26 | Scenarios 4243032 (DDD poster) + 4243035 (TMP poster) activated |
| 2026-02-26 | Scenario 4243036 (FO35 poster) created but left inactive — conn 7146197 needs re-auth |
| 2026-02-26 | Scenario 4243206 (Health Monitor) activated |
| 2026-02-26 | content-engine.yml modified: 3x/day schedule, Phase 1 reads content_ready pins, Vercel deploy retained |
