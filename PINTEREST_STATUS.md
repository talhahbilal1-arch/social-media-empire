# Pinterest Automation Status Report
Generated: 2026-04-12 (updated: 2026-04-12 late session)

## 2026-04-12 Late Session Update

- **Architecture change verified**: `nano_banana_generator.generate_pin_image()` now **raises RuntimeError** on Gemini failure (instead of silently returning raw Pexels bytes). The caller (`content-engine.yml` Phase 1b) handles fallback via `render_pin_to_bytes` which applies the full branded PIL template. This produces on-brand fallback images instead of plain stock photos.
- **`add_text_overlay`** is applied ONLY to Nano Banana AI images — NOT to Pexels+PIL renders (which already have the brand template baked in). Applying it twice would ghost the headline.
- **Test fixes**:
  - `test_fitness_brand_targets_men` now accepts `man`/`men`/`masculine` (current prompt uses "muscular man over 35")
  - `test_generate_pin_image_retries_then_falls_back_to_pexels` → renamed to `test_generate_pin_image_retries_then_raises` to match current architecture
- **All 15 Pinterest tests passing**, all 31 workflow YAMLs syntax-valid, all key Python modules compile cleanly.
- **Current `IMAGE_MODEL`**: `gemini-2.0-flash-exp` (changed again from prior attempts).


## What's Working

- [x] **Content generation** — Gemini (gemini-2.0-flash fallback from 2.5-flash) generates pin content for all 3 brands
- [x] **Nano Banana wired** — Phase 1 tries AI image generation before Pexels+PIL
- [x] **Pexels fallback** — when Gemini image gen fails, nano_banana returns Pexels bytes automatically
- [x] **Supabase upload** — images uploaded to `pin-images` bucket successfully
- [x] **Brand slug routing** — fitness→fitness-made-easy, deals→daily-deal-darling, menopause→menopause-planner (from brand_slugs.py)
- [x] **Per-brand webhooks** — MAKE_WEBHOOK_FITNESS, MAKE_WEBHOOK_DEALS, MAKE_WEBHOOK_MENOPAUSE all configured and active
- [x] **Article generation** — 800-1200 word SEO articles written per pin
- [x] **Vercel deploy** — all 3 brand sites deployed after article push
- [x] **Pinterest posting** — 4/4 pins posted successfully in verified real run (run #24312252417)
- [x] **Video pins** — rendered per brand (3.3–8MB), uploaded and posted via Late API (when key valid)
- [x] **Dry run** — passed (run #24312165470, 3m32s)
- [x] **Real run** — passed (run #24312252417, 4m02s), Posted 4/4 pins
- [x] **61/61 unit tests** pass

## What's Not Working

- [ ] **Gemini image generation** — `gemini-2.0-flash-preview-image-generation` model returns 404. Currently falling back to raw Pexels images (no text overlay). Images still post successfully; just not AI-generated yet.
  - Root cause: image generation model may require different API endpoint or billing tier
  - Impact: pins use raw Pexels photos instead of AI art — functional but not ideal
- [ ] **Late API (video pins)** — all 3 keys return 401 Unauthorized. Video pins generated and uploaded but not posted.
  - Fix: refresh keys at getlate.dev
- [ ] **MAKE_WEBHOOK** (unified fallback) — not configured. Optional — not needed while per-brand webhooks work.

## Secrets Status

| Secret | Status |
|--------|--------|
| GEMINI_API_KEY | ✅ set |
| PEXELS_API_KEY | ✅ set |
| SUPABASE_URL | ✅ set |
| SUPABASE_KEY | ✅ set |
| MAKE_WEBHOOK_FITNESS | ✅ set |
| MAKE_WEBHOOK_DEALS | ✅ set |
| MAKE_WEBHOOK_MENOPAUSE | ✅ set |
| MAKE_WEBHOOK_ACTIVATOR | ✅ set |
| MAKE_WEBHOOK | ❌ not set (optional fallback) |
| LATE_API_KEY / _2 / _3 / _4 | ✅ set (but returning 401 — keys expired) |
| VERCEL_BRAND_TOKEN | ✅ set |

## Next Scheduled Runs (content-engine.yml)

All times UTC:
- 14:00 UTC (6 AM PST)
- 17:00 UTC (9 AM PST)
- 20:00 UTC (12 PM PST)
- 23:00 UTC (3 PM PST)
- 03:00 UTC (7 PM PST)

## Manual Steps Needed

1. **Refresh Late API keys** — go to getlate.dev, get new tokens, update LATE_API_KEY_2/3/4 GitHub secrets
2. **Gemini image gen access** — check if `gemini-2.0-flash-preview-image-generation` is available on your API key tier at aistudio.google.com. May need to enable Imagen API billing.

## Changes Made This Session

1. **`video_automation/nano_banana_generator.py`** — fixed IMAGE_MODEL from `gemini-2.5-flash-preview-image-generation` to `gemini-2.0-flash-preview-image-generation`
2. **`.github/workflows/content-engine.yml`** — wired Nano Banana into Phase 1: tries AI image gen first, falls back to Pexels+PIL on failure
