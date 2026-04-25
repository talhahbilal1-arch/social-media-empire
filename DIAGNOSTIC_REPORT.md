# Pinterest Automation Diagnostic Report

**Run start:** 2026-04-24 (UTC night job)
**Target:** restore 3 static image pins/day × 3 accounts (fitness, deals, menopause) = 9/day
**Scope:** image pipeline only. Video is OUT OF SCOPE.

## Pre-flight

- **Working directory:** `/Users/homefolder/Desktop/social-media-empire` (remote `talhahbilal1-arch/social-media-empire`). Fix branch: `fix/pinterest-automation-2026-04-24` from clean `main`.
- **Credentials available in `.env`:** `SUPABASE_URL`, `SUPABASE_KEY` (used for both apikey and Bearer), `PEXELS_API_KEY`, `GEMINI_API_KEY`, `MAKE_WEBHOOK_DEALS/FITNESS/MENOPAUSE/URL`.
- **Credentials missing:** `MAKE_API_TOKEN` (blocks Phase 1C/1D/1E + Phase 3C-H1 Activator trigger), `ANTHROPIC_API_KEY` (Phase 3B-H1 copy falls back to runbook's hardcoded literal).

## 1A — Supabase pipeline state (pinterest_pins table)

- **Total rows in table:** 1137 (Content-Range header confirmed).
- **HTTP auth:** 200 OK via `SUPABASE_KEY` as both `apikey` and `Authorization: Bearer`.
- **Status values (exact casing — lowercase, not runbook's `Ready`/`Queued`):**

  | status         | count |
  |----------------|-------|
  | `posted`       | 925 |
  | `pending`      | 192 |
  | `failed`       | 14 |
  | `content_ready`| 6 |
  | (Ready/Queued) | 0 |

- **`account` column is ALWAYS `NULL`.** Brand routing uses the `brand` column instead. Runbook's assumption of a populated `account` column does not hold.

- **Per-brand distribution:**

  | brand | posted | pending | content_ready | failed |
  |-------|-------:|--------:|--------------:|-------:|
  | `fitness`     | 262 | 24 | 1 | 6 |
  | `deals`       | 201 | 24 | 1 | 4 |
  | `menopause`   | 198 | 24 | 4 | 4 |
  | `beauty`      |   0 | 40 | 0 | 0 |
  | `homedecor`   |   0 | 40 | 0 | 0 |
  | `pilottools`  |   0 | 40 | 0 | 0 |
  | (null)        | 127 |  0 | 0 | 0 (legacy) |

- **Most recent `created_at`:** `2026-04-24T03:03:07Z` (brand=beauty, status=pending). Rows ARE being created; the pipeline is not idle at the write side.
- **Most recent `posted_at`:** `2026-04-19T01:06:08Z` (brand=menopause), with deals + fitness within 2 seconds of that. **No pins have posted for ~5 days** (longer than the runbook's 2.5-day assumption).
- **Posting rhythm (posts/day, last 500):** 28 on 4/13, 22 on 4/12 & 3/31, 17–19 on multiple dates through 4/9, tapering; last substantive day was 16 posts on 4/18, then the 3-pin batch on 4/19, then **zero**.
- **10 most recent rows:** saved to `supabase_recent_rows.json`.

## 1B — Schema integrity

**Present (from live row sampling, 44 columns):** `id, account, affiliate_url, article_generated, asin, background_image_url, board_id, brand, category, content_json, created_at, description, destination_url, discount_percentage, error_message, generated_image_base64, generated_image_url, hashtags, image_hash, image_prompt, image_url, list_price, niche, overlay_headline, overlay_subtext, pexels_search_term, pin_description, pin_id, pin_title, pin_type, pinterest_pin_id, posted_at, price, product_title, retry_count, scheduled_date, score, source, status, tips, title, topic, updated_at, visual_style`

**Runbook's "required" set vs reality:**
- `id` ✓, `title` ✓, `image_url` ✓, `status` ✓, `board_id` ✓, `destination_url` ✓, `affiliate_url` ✓, `pin_id` ✓, `posted_at` ✓, `error_message` ✓, `retry_count` ✓, `created_at` ✓, `updated_at` ✓
- **`pin_title` / `pin_description` / `hashtags`: column EXISTS but NEVER populated on posted rows.** The content engine uses `title`/`description`/`overlay_headline`/`overlay_subtext` instead. Seeding must follow live convention, not runbook literal.
- **`account` column exists but always NULL.** Brand routing is via `brand`.

**Schema gaps observed in error logs:** `'board' column does not exist` — code has historically attempted to write a column named `board` (22 errors from 2026-04-22). This was either fixed or the buggy code path is no longer exercised; no content_engine errors after 2026-04-22.

## 1C/1D/1E — Make.com diagnosis (SKIPPED)

**Status:** Cannot confirm — `MAKE_API_TOKEN` absent per explicit plan-time decision.

- 1C (connections health): unverifiable without API token.
- 1D (scenario blueprints 4261421/4261294/4261143/4261296): not fetched.
- 1E (Activator last execution detail): not fetched.

**Consequence:** H2 (filter regression), H3 (OAuth), H4 (webhook URL mismatch) cannot be confirmed or ruled out from within this run.

### Substitute upstream evidence (GitHub Actions, not in original runbook)

The real upstream generator is `.github/workflows/content-engine.yml` (scheduled 15:00, 23:00, 04:00 UTC), not a Make.com Activator. Its recent run history via `gh run list --workflow=content-engine.yml`:

| Run ID | Trigger | Start (UTC) | Duration | Outcome |
|---|---|---|---|---|
| 24866727012 | workflow_dispatch | 2026-04-24 03:00:01 | 3m38s | failure |
| 24864758300 | schedule | 2026-04-24 01:00:01 | 4m03s | failure |
| 24863493125 | workflow_dispatch | 2026-04-24 01:00:02 | 4m37s | failure |
| 24861239717 | workflow_dispatch | 2026-04-23 23:00:01 | 3m56s | failure |
| … (10 consecutive failures from 2026-04-23 17:00 onward) | | | | failure |

**Last failing run's Render-and-publish step output (run 24866727012):**

```
=== RUN TYPE: VIDEO ===
=== PHASE 0: Generating pin content ===
  SKIPPED — this is a video run (Phase 1v will handle content)
=== ACTIVE BRANDS THIS RUN: ['pilottools', 'homedecor', 'beauty'] (hour=3) ===

=== PHASE 1: Rendering content_ready pins ===
  Query: status=eq.content_ready AND created_at>=2026-04-23T03:02:57Z  (24h window)
  Found 0 content_ready pins
  Rendered 0/0 pins

=== PHASE 1v: video strategy = *** ===
  [pilottools] Staged video_pending pin (board PENDING)
  [homedecor] Staged video_pending pin (board PENDING)
  [beauty] Staged video_pending pin (board PENDING)

=== PHASE 1b: Posting pins to Pinterest ===
  Posted 0/0 pins to Pinterest

=== Content Engine Summary ===
  Rendered: 0, Articles: 0, Posted: 0
DAILY PIN SUMMARY: fitness=0, deals=0, menopause=0, pilottools=0, homedecor=0, beauty=0
```

**Two mutually-reinforcing failures visible in this output:**

1. **Phase 1 (`status=content_ready` + `created_at >= now()-24h`) returns 0 rows.** The 6 `content_ready` rows in the table are from 2026-04-03/04/06, 18–21 days old, well outside the 24-hour window. They are stuck: they have `image_url=null`, so they were never rendered, and no process re-queues them.
2. **Phase 0 (fresh pin content generation) is SKIPPED because the run is in VIDEO mode.** Whatever logic decides "RUN TYPE: VIDEO" vs. IMAGE based on hour is sending every recent run to VIDEO. Active brands for hour=3 are `pilottools/homedecor/beauty` (new brands, no boards configured — log shows "board PENDING"). Meanwhile `fitness/deals/menopause` have not been in any active-brand list for the recent runs I inspected.

**Net effect:** No fresh `content_ready` rows for fitness/deals/menopause are being created, and the 6 stale ones are invisible to the engine's time-windowed query. The pipeline is functionally empty from Phase 1's perspective even though 6 `content_ready` rows physically exist.

### Supabase `errors` table (pipeline self-reporting)

```
768 posting_failure   (most recent 2026-03-21, Instagram/TikTok/Late 403)
 89 render_failure    (most recent 2026-01-30, Creatomate)
 82 content_engine    (most recent 2026-04-22, PGRST204 'board' col)
 50 generation_failure (most recent 2026-03-18, Gemini 429 + Anthropic billing)
  9 article_url_404
  2 pin_watchdog      ←← fresh, see below
```

Most recent watchdog/alert entries (saved to `_phase1_tmp/content_engine_errors.json`):

- 2026-04-24T03:56:13 `pin_watchdog` (medium): "No pins generated in 55 hours!"
- 2026-04-24T01:00:26 `pinterest_drop_alert` (**critical**): "fitness: only 0/3 expected; deals: only 0/3 expected; menopause: only 0/3 expected"
- 2026-04-24T00:07:10 `pin_watchdog` (medium): "No pins generated in 51 hours!"

**The system is self-reporting the exact symptom.**

## 1F — Root cause

`ROOT_CAUSE: H1_EMPTY_QUEUE`

**Justification (with the caveat that the letter vs. spirit of "empty queue" matters here):**

- The runbook defines H1 as "Supabase has 0 `Ready`/`Queued`". Literally, the schema has 0 `Ready` + 0 `Queued` rows (the schema uses `content_ready` and `pending` instead). Zero by the letter.
- Functionally, the content engine's Phase 1 query (`status=content_ready` AND `created_at >= now()-24h`) returns 0 rows on every run I inspected — so from the posting pipeline's perspective, the queue IS empty.
- The 6 stale `content_ready` rows (2026-04-03 to 2026-04-06) are orphans: incomplete (`image_url=null`) and outside the time window. They prove the problem is not "nothing ever gets to content_ready" but rather "the pipeline stopped replenishing content_ready with fresh rows ~3 weeks ago."
- H2/H3/H4 cannot be confirmed without `MAKE_API_TOKEN`, but the Supabase + GitHub Actions evidence together is conclusive for H1 without needing Make.com inspection.

**Deeper upstream cause (captured for Phase 3E-H1, not blocking Phase 2 decision):**
The content-engine.yml logic is gating every recent scheduled run to `RUN TYPE: VIDEO`, skipping Phase 0 image-pin generation entirely. Combined with hour-based brand-rotation that does not appear to include fitness/deals/menopause in any active-brand list for the hours I observed, the result is zero new `content_ready` rows for the three target brands. Fixing that gate is the durable fix; seeding + manually triggering posts is the immediate stopgap.

---

ROOT_CAUSE: H1_EMPTY_QUEUE
