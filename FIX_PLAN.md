# Fix Plan (Phase 2) — H1 Empty Queue

**Commit:** Execute the `BRANCH H1` branch of the runbook, **with one mandatory deviation**: Phase 3C-H1 (trigger Activator via Make.com API) is SKIPPED because `MAKE_API_TOKEN` is absent (confirmed at plan time). The skip is documented, not improvised.

## What I will do in Phase 3

### 3A-H1 — Account mapping from live data

Rather than the runbook's `account_mapping.json` keyed on `account` column (which is always NULL), I will build a **brand mapping** from the 3 most recent `posted` rows per brand, capturing real `board_id` values used by the engine. Values confirmed from Phase 1 preview:

| brand | recent board_ids (sampled) | destination_url pattern |
|---|---|---|
| fitness | 418834902785124651, 418834902785125486 | `https://fitover35.com/articles/<slug>.html` |
| deals | 874683627569113370, 874683627569113339, 874683627569021288 | `https://www.dailydealdarling.com/articles/<slug>.html` |
| menopause | 1076993767079898628, 1076993767079898616, 1076993767079887530 | `https://menopause-planner-website.vercel.app/articles/<slug>.html` |

Saved to `account_mapping.json`. Per-brand `ready_status_string`: **`content_ready`** (lowercase, derived from live schema — runbook's `"Ready"` does not exist).

### 3B-H1 — Seed 9 pins with the correct schema

Build `scripts/seed_starter_pins.py` that inserts 3 rows each for fitness/deals/menopause. Each row uses **live-schema columns**, not runbook-literal ones:

- `brand` (not `account`)
- `title` + `description` + `overlay_headline` + `overlay_subtext` (not `pin_title`/`pin_description`/`hashtags` — those are never populated on posted rows)
- `image_url` = Pexels `large2x` portrait URL (per runbook §3B-H1 step 3, with simpler-query retry)
- `board_id` = first value from that brand's recent-posted sample
- `destination_url` = homepage fallback (`https://fitover35.com`, `https://dailydealdarling.com`, `https://menopause-planner-website.vercel.app`) — flagged as placeholder in `MORNING_REPORT.md`; article-URL wiring is a separate follow-up
- `status = 'content_ready'` (lowercase, matches engine's filter)
- `pin_type = 'image'`
- `niche` = topic-derived (e.g., `fat_loss`, `home_decor`, `wellness`)
- `visual_style = 'bold_text_overlay'` (simple, matches recent posted rows)
- `retry_count = 0`

**Copy generation:** Hardcoded fallback per plan-time decision (no `ANTHROPIC_API_KEY`). `title` and `description` use the runbook's §3B-H1 fallback literal, adapted: `title = "<Topic>: Simple Tips"`, `description = "Ideas and inspiration for <topic>. Save this pin for later."`

**Topics (runbook §3B-H1 step 2):**
- fitness: `man lifting weights gym`, `healthy meal prep protein bowl`, `morning stretching workout mat`
- deals: `home organization storage baskets`, `cozy neutral bedroom decor`, `modern kitchen utensils wooden`
- menopause: `woman meditation peaceful calm`, `herbal tea cup cozy`, `woman walking outdoors nature`

Insert as single batch POST with one retry on 4xx; hard-stop on second failure per runbook.

Verify by re-querying `status=eq.content_ready` and dumping IDs to `seed_result.json`.

### 3C-H1 — Activator trigger (SKIPPED)

**Reason:** `MAKE_API_TOKEN` absent. Cannot call `POST https://us2.make.com/api/v2/scenarios/4261421/run`. Document in `test_trigger_result.md` with clear instructions for Tall: either add token and re-run, or manually trigger the Activator via Make.com UI, or manually dispatch `gh workflow run content-engine.yml` (which would exercise Phase 1 and pick up the fresh `content_ready` rows).

### 3D-H1 — Dead scenario inventory

Cannot call Make.com API to list scenarios by `isinvalid: true`. Will transcribe the runbook's pre-confirmed dead list (`4263862, 4263863, 4263864, 4669524, 4671823, 4671827, 4732882, 4732899, 4732903`) into `SCENARIOS_TO_DELETE.md` for manual cleanup, with a note that this is sourced from the runbook and not re-verified.

### 3E-H1 — Upstream generator investigation (the real fix)

Write `GENERATOR_STATUS.md` documenting:

- The GH Actions `content-engine.yml` workflow is the real upstream generator, not a Make.com scenario.
- Every recent run failed with exit code 1 due to `Posted: 0 pins`.
- Phase 1 query `status=content_ready` + `created_at>=now()-24h` returns 0 rows because the 6 existing `content_ready` rows are 18–21 days old and have `image_url=null`.
- Phase 0 (fresh pin content generation) is SKIPPED by `RUN TYPE: VIDEO` gate.
- Active-brand rotation does not include fitness/deals/menopause in any hour I observed.
- **Proposed fixes for Tall (pick one):**
  1. Manually dispatch `gh workflow run content-engine.yml --field dry_run=false --field brand=fitness` (and deals, menopause) to force Phase 0 generation for the stuck brands. Fastest.
  2. Flip the VIDEO/IMAGE gate in `.github/workflows/content-engine.yml` or in `scripts/` (wherever it lives) to prefer IMAGE mode while the Late API keys are expired.
  3. Widen the Phase 1 query's time window from 24h to 30d so the 6 stale `content_ready` rows become visible again. (Risky — those rows have `image_url=null` and may still not render.)

## Success criteria for this run

- Per runbook: 9 `content_ready` rows exist in Supabase with `image_url` populated, created by this job.
- Per runbook H1: at least one row transitions to `posted` within 90s of an Activator trigger → **not verifiable this run** because Activator trigger is skipped. Instead, the success bar moves to: seed rows are visible, `MORNING_REPORT.md` documents the exact next action Tall must take (≤5 minutes) to unblock posting.

## Branches not taken

- **H2 (filter regression):** cannot confirm or rule out; Make.com API unavailable. But the Phase 1F evidence makes H2 unlikely as the primary cause — the empty-queue symptom is already explained by upstream gating.
- **H3 (OAuth):** Late API keys are known expired (confirmed in `PINTEREST_STATUS.md`), but that affects video only, which is out of scope. Per-brand Make.com webhooks (`MAKE_WEBHOOK_DEALS/FITNESS/MENOPAUSE`) appear to work per the last successful posts on 2026-04-19.
- **H4 (webhook mismatch):** cannot inspect Make.com Activator blueprint without API token. Functionally moot — even if webhooks were correct, there's nothing upstream to dispatch.
