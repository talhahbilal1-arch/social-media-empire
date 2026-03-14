# Make.com Scenario Inventory — Rebuild v3
*Updated: 2026-02-27*

## Architecture Overview

2-stage pipeline. GitHub Actions handles ALL content generation + image rendering + Pinterest posting via Make.com webhooks + article generation + Vercel deploy.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: GitHub Actions content-engine.yml (3x/day: 8AM/2PM/8PM PST)   │
│   Phase 0 — Claude generates pin content → status='content_ready'       │
│   Phase 1 — PIL render → Supabase Storage upload → status='ready'       │
│   Phase 1b— POST to Make.com webhook per brand → Pinterest Create Pin   │
│              → status='posted' | 'failed'                               │
│   Phase 2 — Generate SEO article per pin → save to outputs/             │
│   Phase 3 — Git commit + push articles → Vercel auto-deploy             │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│ STAGE 2: Make.com Webhook Posters × 3 (triggered by GH Actions)         │
│   Deals (4251934)    → receives POST → Pinterest Create Pin (conn 6738173)│
│   Menopause (4251935)→ receives POST → Pinterest Create Pin (conn 6857103)│
│   Fitness (4251937)  → receives POST → Pinterest Create Pin (conn 7146197)│
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

### 1. Pin Content Generator — GitHub Actions Phase 0
| Field | Value |
|-------|-------|
| **Where** | `.github/workflows/content-engine.yml` Phase 0 |
| **Schedule** | 3x/day (8 AM, 2 PM, 8 PM PST) — same as content-engine.yml |
| **Status** | ✅ Active — verified 2026-02-27 (3/3 brands, 3/3 articles) |

**Flow**: `generate_pin_content(brand, db)` → insert `pinterest_pins` (`status='content_ready'`) → Phase 1 renders same run

**Note**: Make.com scenarios (4243147, 4251297, 4251305) replaced by GH Actions Phase 0.
Make.com API-created scheduled scenarios cannot execute due to a Make.com platform limitation
(`BundleValidationError` affects all API-created scheduled scenarios — fix requires UI save).
Deactivate Make.com scenarios 4243147, 4251297, 4251305 to avoid confusion.

---

### 2. Pin Poster — DailyDealDarling v3 (Webhook)
| Field | Value |
|-------|-------|
| **Scenario ID** | **4251934** |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4251934/edit` |
| **Brand** | `deals` |
| **Pinterest Connection** | Daily Deal Darling (conn 6738173) |
| **Trigger** | Webhook (called by GitHub Actions Phase 1b) |
| **Webhook URL** | `https://hook.us2.make.com/s5r2hm41lnupten8e1k5fn6uagpqdhmk` |
| **GitHub Secret** | `MAKE_WEBHOOK_DEALS` |
| **Status** | ✅ Active — VERIFIED 2026-02-27 (status=1, 2 ops) |
| **Ops/month** | ~90 (3 runs/day × 30 days) |

**Flow** (2 modules):
1. `gateway:CustomWebHook` — receives `{pin_id, brand, title, description, image_url, link, board_id}`
2. `pinterest:createPin` (conn 6738173) — posts pin to Pinterest

**Status tracking**: GitHub Actions sets `status='posting'` before call, `status='posted'` after HTTP 200.

*Replaced broken scheduled scenario 4243032 (BundleValidationError). Old scenario deactivated.*

---

### 3. Pin Poster — MenopausePlanner v3 (Webhook)
| Field | Value |
|-------|-------|
| **Scenario ID** | **4251935** |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4251935/edit` |
| **Brand** | `menopause` |
| **Pinterest Connection** | TheMenopausePlanner (conn 6857103) |
| **Trigger** | Webhook (called by GitHub Actions Phase 1b) |
| **Webhook URL** | `https://hook.us2.make.com/h712u9ydn9w5ur1ekyqbglvdevnes6sa` |
| **GitHub Secret** | `MAKE_WEBHOOK_MENOPAUSE` |
| **Status** | ✅ Active — VERIFIED 2026-02-27 (status=1, 2 ops) |
| **Ops/month** | ~90 |

**Flow**: Same as DDD v3. *Replaced 4243035.*

---

### 4. Pin Poster — FitOver35 v3 (Webhook)
| Field | Value |
|-------|-------|
| **Scenario ID** | **4251937** |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4251937/edit` |
| **Brand** | `fitness` |
| **Pinterest Connection** | Fitness Made Easy (conn 7146197) |
| **Trigger** | Webhook (called by GitHub Actions Phase 1b) |
| **Webhook URL** | `https://hook.us2.make.com/4mwp49ymhkdfjcx8puc21d00s62s753f` |
| **GitHub Secret** | `MAKE_WEBHOOK_FITNESS` |
| **Status** | ✅ Active — VERIFIED 2026-02-27 (status=1, 2 ops) |
| **Ops/month** | ~90 |

**Flow**: Same as DDD v3. *Replaced 4243036.*

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
| 2026-02-27 | **Rebuild v3**: Replaced all broken scheduled poster scenarios with webhook-triggered ones |
| 2026-02-27 | Root cause: Make.com API-created scheduled scenarios always get BundleValidationError — unfixable without UI save |
| 2026-02-27 | Fix: 3 new webhook scenarios (4251934/4251935/4251937) created + activated — ALL VERIFIED working |
| 2026-02-27 | content-engine.yml: added Phase 1b — GitHub Actions calls webhook after rendering each pin |
| 2026-02-27 | GitHub secrets MAKE_WEBHOOK_FITNESS/DEALS/MENOPAUSE updated with new webhook URLs |
| 2026-02-27 | End-to-end test: 1 pin per brand posted to Pinterest successfully |
