# Phase 3C-H1 — Activator Trigger (SKIPPED)

**Status:** Not executed. `MAKE_API_TOKEN` absent.

The runbook's 3C-H1 step calls `POST https://us2.make.com/api/v2/scenarios/4261421/run` to trigger the Make.com Scenario Activator, then waits 90 seconds and observes execution + poster runs + row status changes. Without a Make.com API token in `.env` (confirmed at plan time with Tall), this API call is not possible.

## Why I did not improvise

The runbook's §3C-H1 is explicit that the trigger happens via the Make.com API, and Rule #0 forbids improvising. Two alternatives were considered and rejected:

1. **Direct webhook POST** to `MAKE_WEBHOOK_DEALS/FITNESS/MENOPAUSE` from Python — not forbidden literally by the runbook's "what you are NOT allowed to do" list, but would diverge from the runbook's defined procedure and would bypass any filtering the Activator applies (which is itself diagnostic evidence we'd lose). Not worth the deviation.
2. **`gh workflow run content-engine.yml`** — would fire the next scheduled run early. Same concern: deviates from the runbook's procedure, and would exercise the content engine's "RUN TYPE: VIDEO" gate that's currently skipping Phase 1 image rendering.

## What this means for tonight's run

The 9 seeded `content_ready` rows (see `seed_result.json`) are sitting in Supabase ready to render. They have fresh `created_at=2026-04-24T05:36:45Z`, so they satisfy the content engine's 24-hour window. On the **next** scheduled content-engine.yml run (next cron: **2026-04-24 15:00 UTC / 7 AM PST**), Phase 1 should see them:

```
=== PHASE 1: Rendering content_ready pins ===
  Query: status=eq.content_ready AND created_at>=now()-24h
  Found 9 content_ready pins   ← our seeds
```

Whether they actually render and post depends on:
- Whether that run's **active-brand rotation** includes fitness/deals/menopause (the 2026-04-24T03:00 run's hour-3 active list was `[pilottools, homedecor, beauty]`; the hour-15 list is TBD — see `GENERATOR_STATUS.md`).
- Whether the engine's nano_banana/Pexels+PIL render step runs cleanly with our pre-populated `image_url`, or whether it tries to regenerate and fails.
- Whether the Make.com per-brand webhooks are still wired correctly (last successful post was 2026-04-19; no confirmed dispatches since).

## What Tall should do to observe / force posting

Pick one of these, ordered by effort:

### Option A (lowest effort, ~30s) — Wait and observe

Let the natural 15:00 UTC cron run. After it completes, check:

```
curl -s -H "apikey: $SUPABASE_KEY" -H "Authorization: Bearer $SUPABASE_KEY" \
  "$SUPABASE_URL/rest/v1/pinterest_pins?select=id,brand,status,posted_at,pinterest_pin_id&id=in.(b42bc5be-68b3-4130-bef0-03cd87abeac1,9af609d4-a400-4107-a71c-7a06844d7a5b,14c73a07-8f86-41d8-a5ad-064025bc9b86,31098f90-b540-4e65-96bd-3bfa8d9c86d7,b493fcb8-cce8-4c23-8220-837ab0c69ab1,04398ef3-5db3-4d7d-9432-c127863d1365,3f2f8278-5718-40f8-9d25-f85680da95b3,55e94d55-48af-4b0c-a4a9-281f332382b2,cf28812c-ca74-48ef-8f4c-d71bfc3bc81d)"
```

Rows with `status=posted` and `posted_at` set = success. Rows still `content_ready` = the active-brand gate skipped them.

### Option B (~2 min) — Force a dispatch

```
gh workflow run content-engine.yml --ref main \
  --field dry_run=false \
  --field brand=fitness
# repeat for deals and menopause
```

This re-exercises Phase 1 for each specific brand. Still subject to whatever the `RUN TYPE: VIDEO` gate does.

### Option C (~5 min) — Add MAKE_API_TOKEN and re-run this job

1. Get a Make.com API token with `scenarios:read, connections:read` at `https://us2.make.com/account` → **API access** → create token.
2. Append `MAKE_API_TOKEN=<token>` to `social-media-empire/.env`.
3. Run:
   ```
   curl -X POST -H "Authorization: Token $MAKE_API_TOKEN" \
     "https://us2.make.com/api/v2/scenarios/4261421/run"
   ```
4. Wait 90s, then query posted status per Option A.

This is closest to the runbook's original §3C-H1 procedure.

## Outcome

**Cannot confirm H1 is fully resolved tonight.** The queue is no longer functionally empty (9 fresh `content_ready` rows exist with `image_url` populated), which is Phase 1F's stated failure mode. But without the Make.com API trigger or a manual workflow_dispatch, there's no observed pipeline-movement evidence within this run.
