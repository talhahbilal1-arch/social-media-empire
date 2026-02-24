# Make.com CLAW v2 Scenario Inventory
*Updated: 2026-02-24*

## Overview

All 3 CLAW v2 Pin Poster scenarios are **active and posting**. Verified 2026-02-24 — all 3 brands posting directly to their dedicated scenarios with no fallbacks.

---

## CLAW v2 Pin Poster Scenarios (Phase 4.1–4.3)

These scenarios receive Pinterest pin data via webhook and post to Pinterest.

### 4.1 — FitOver35 Pin Poster
| Field | Value |
|-------|-------|
| **Scenario ID** | 4210216 |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4210216/edit` |
| **Webhook URL** | `https://hook.us2.make.com/c9hrx4dvf8nm5hkrq41sk29ty6lp1ir9` |
| **Webhook Hook ID** | 1924684 (new — old hook 1918987 was deleted/410) |
| **Webhook Name** | CLAW Fitness Pin Webhook v2 |
| **Pinterest Connection** | Fitness Made Easy (conn 7146197) |
| **Schedule** | Webhook-triggered (immediate) |
| **Status** | ✅ Active — verified posting 2026-02-24 |

### 4.2 — DailyDealDarling Pin Poster
| Field | Value |
|-------|-------|
| **Scenario ID** | 4210274 |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4210274/edit` |
| **Webhook URL** | `https://hook.us2.make.com/z1n9r2sv6kbv3weptghmimjevvtcrk6a` |
| **Webhook Name** | CLAW Deals Pin Webhook |
| **Pinterest Connection** | Daily Deal Darling board (conn 6738173) |
| **Schedule** | Webhook-triggered (immediate) |
| **Status** | ✅ Active — verified posting 2026-02-24 |

### 4.3 — MenopausePlanner Pin Poster
| Field | Value |
|-------|-------|
| **Scenario ID** | 4210434 |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4210434/edit` |
| **Webhook URL** | `https://hook.us2.make.com/rt4vqc92vzngvmtfn1cidb2u7yviyw9o` |
| **Webhook Name** | CLAW Menopause Pin Webhook |
| **Pinterest Connection** | TheMenopausePlanner-Pinterest (conn 6857103) |
| **Schedule** | Webhook-triggered (immediate) |
| **Status** | ✅ Active — verified posting 2026-02-24 |

---

## CLAW v2 Automation Scenarios (Phase 4.4–4.5)

### 4.4 — Retry Failed Pins
| Field | Value |
|-------|-------|
| **Scenario ID** | 4210597 |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4210597/edit` |
| **Schedule** | Every 6 hours (21600 seconds) |
| **Source table** | `pinterest_pins` where `status=failed` |
| **Flow** | GET failed pins → Iterator → Router (brand filter) → POST to brand webhook |
| **Status** | ✅ Active — verified 2026-02-24 |

#### Route Filters
| Route | Brand Filter | Target Webhook |
|-------|-------------|----------------|
| Fitness | `brand = fitness-made-easy` | `https://hook.us2.make.com/c9hrx4dvf8nm5hkrq41sk29ty6lp1ir9` |
| Deals | `brand = daily-deal-darling` | `https://hook.us2.make.com/z1n9r2sv6kbv3weptghmimjevvtcrk6a` |
| Menopause | `brand = menopause-planner` | `https://hook.us2.make.com/rt4vqc92vzngvmtfn1cidb2u7yviyw9o` |

### 4.5 — Daily Pin Health Report
| Field | Value |
|-------|-------|
| **Scenario ID** | 4210643 |
| **Make.com URL** | `https://us2.make.com/1686661/scenarios/4210643/edit` |
| **Schedule** | Every 24 hours (86400 seconds) |
| **Source table** | `pinterest_pins` last 24h |
| **Flow** | GET posted count → GET failed count → POST Telegram report |
| **Status** | ✅ Active — verified 2026-02-24 |

---

## Phase 5 — Video Posting Scenarios: BLOCKED

**Status: Cannot build — OAuth connections not set up**

Available Make.com connections (as of 2026-02-23):
- ✅ Pinterest: 3 connections (FitOver35, DailyDealDarling, MenopausePlanner)
- ✅ HeyGen: basic auth (conn 6826449)
- ✅ Creatomate: basic auth (conn 6807786)
- ❌ TikTok: no connection
- ❌ Instagram: no connection
- ❌ YouTube: no connection

**Action items to unblock:**
1. Go to Make.com → Connections → Add → TikTok → complete OAuth for each brand account
2. Repeat for Instagram (Meta Business OAuth)
3. Repeat for YouTube (Google OAuth)
4. Then rebuild video poster scenarios cloning the Pin Poster structure

---

## GitHub Secrets (current)

| Secret | Value |
|--------|-------|
| `MAKE_WEBHOOK_FITNESS` | `https://hook.us2.make.com/c9hrx4dvf8nm5hkrq41sk29ty6lp1ir9` |
| `MAKE_WEBHOOK_DEALS` | `https://hook.us2.make.com/z1n9r2sv6kbv3weptghmimjevvtcrk6a` |
| `MAKE_WEBHOOK_MENOPAUSE` | `https://hook.us2.make.com/rt4vqc92vzngvmtfn1cidb2u7yviyw9o` |

---

## Old Scenario (Deprecated)

| Field | Value |
|-------|-------|
| **Old scenario ID** | 3977247 |
| **Old webhook** | `https://hook.us2.make.com/8d51h67qpdt77jgz5brhvd5c9hgvaap8` |
| **Status** | Can be deactivated — all 3 CLAW v2 pin posters are active |

---

## Architecture Summary

```
GitHub Actions (content-engine.yml) — 5x daily
  └── Generates pin content (Claude API)
  └── Renders PIL image → Supabase Storage
  └── POST to per-brand webhook → Make.com CLAW v2 Pin Poster
        └── Router → Pinterest Create Pin (conn 7146197 / 6738173 / 6857103)
        └── HTTP POST → Supabase content_history log
        └── Break error handler (3 retries)

Make.com Retry (every 6h) — scenario 4210597 [INACTIVE]
  └── GET pinterest_pins WHERE status=failed
  └── Iterator → Router by brand
  └── POST to brand webhook (re-queues failed pins)

Make.com Health Report (every 24h) — scenario 4210643 [INACTIVE]
  └── GET posted count (last 24h)
  └── GET failed count (last 24h)
  └── POST to Telegram: @clawai_personal_bot (chat_id 8090293231)
```

## Activation Log

| Date | Action |
|------|--------|
| 2026-02-23 | All 5 scenarios built via Make.com REST API |
| 2026-02-24 | Scenarios 4210274 (deals) + 4210434 (menopause) activated; Supabase key injected via API |
| 2026-02-24 | Scenario 4210216 (fitness): old webhook hook 1918987 was dead (410); new hook 1924684 created + blueprint patched + activated |
| 2026-02-24 | All 3 brands verified posting end-to-end via CLAW v2 dedicated webhooks |
| 2026-02-24 | Scenario 4210597 (retry): activated; Supabase key injected + fitness webhook updated to new hook |
| 2026-02-24 | Scenario 4210643 (health report): activated; Supabase key + Telegram bot token injected |
