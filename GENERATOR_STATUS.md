# Upstream Generator Status — Content Engine (Phase 3E-H1)

**Scope extension vs runbook:** the runbook's §3E-H1 asks for investigation of a Make.com-scenario generator. The real upstream generator for this repo is **GitHub Actions `.github/workflows/content-engine.yml`**, so this document investigates that instead.

## The generator is broken in a very specific way

`content-engine.yml` has run on its scheduled cron (15:00, 23:00, 04:00 UTC) plus ad-hoc dispatches for the last several days. **Every run since 2026-04-23 17:00 UTC has failed with exit code 1** (10+ consecutive failures). But the failure is not a crash — it's an assertion-style "0 pins posted" exit. The real problem is two layered gates:

### Gate 1 — Phase 0 (fresh pin generation) is skipped on "VIDEO" runs

From the 2026-04-24 03:00 UTC run log:

```
=== RUN TYPE: VIDEO ===
=== PHASE 0: Generating pin content ===
  SKIPPED — this is a video run (Phase 1v will handle content)
```

Whatever logic decides `RUN TYPE` (almost certainly hour-based) is sending every scheduled run to VIDEO mode. This means no new `content_ready` rows are ever written for the three target brands (fitness/deals/menopause) by the scheduled cron.

**Video mode is dead weight.** Per `PINTEREST_STATUS.md` (2026-04-12): "Late API (video pins) — all 3 keys return 401 Unauthorized." The video pipeline has been broken for at least 11 days, yet the content engine still spends every run on it.

### Gate 2 — Phase 1 (posting) uses a 24-hour `created_at` window

Same run, next line:

```
=== PHASE 1: Rendering content_ready pins ===
  GET .../pinterest_pins?select=*&status=eq.content_ready&created_at=gte.2026-04-23T03:02:57Z
  Found 0 content_ready pins
  Rendered 0/0 pins
```

The 6 `content_ready` rows in Supabase are from 2026-04-03 / 04 / 06 — 18–21 days old. They also have `image_url=null` (the Phase 1 render step never ran on them), so they're doubly stuck.

### Gate 3 — Active-brand rotation rarely includes the target brands

```
=== ACTIVE BRANDS THIS RUN: ['pilottools', 'homedecor', 'beauty'] (hour=3) ===
```

The 3 "active brands" in the 03:00 UTC run are the NEW brands (pilottools/homedecor/beauty), which have ZERO posted rows and 40 pending rows each — their pipeline was never complete. Commit `1fb8ba2` ("stagger 6 brands into 2 groups to avoid Gemini 429 errors") is the likely source. If fitness/deals/menopause are only active during certain hours but VIDEO mode skips Phase 0 in those hours, they're never generated either.

## Consequence

- **Zero fresh content_ready rows are being produced** for fitness/deals/menopause.
- **Zero stale content_ready rows can flow** because they're outside the 24h window.
- **The 9 seed rows this job created** (see `seed_result.json`) are inside the window and fully populated, so they're the only rows that a Phase 1 pass could actually render. But Phase 1 only runs for the active brands.

## Minimal next actions for Tall (pick one)

Ordered by effort. **Do #1 first** because it unblocks posting tonight regardless of which deeper fix is chosen:

### 1. Manually dispatch content-engine.yml for each target brand (~2 min)

```
gh workflow run content-engine.yml --ref main --field dry_run=false --field brand=fitness
gh workflow run content-engine.yml --ref main --field dry_run=false --field brand=deals
gh workflow run content-engine.yml --ref main --field dry_run=false --field brand=menopause
```

**What this does:** runs the engine with a single-brand filter that likely overrides the active-brand rotation, causing Phase 1 to see and render the 3 seeded rows for that brand. If it still routes to VIDEO mode, move to #2.

**What to watch:** `gh run watch <run-id>` for each. Success = Posted >0 in the final summary.

### 2. Temporarily disable VIDEO mode (~5 min)

Find wherever `RUN TYPE: VIDEO` is decided (grep `RUN_TYPE\|RUN TYPE` inside the workflow and `scripts/`). Temporarily force `RUN TYPE: IMAGE` for all hours. Re-deploy / push. Late API is dead, so the VIDEO path can't accomplish anything right now anyway.

### 3. Widen Phase 1's time window (~5 min)

Change the `created_at >= now() - 24h` to `created_at >= now() - 30d`. This resurrects the 6 stale rows — but they have `image_url=null`, so they may still fail to render. Skip this unless #1 and #2 don't work.

### 4. Add a manual trigger path for `content_ready` seeds (structural fix)

Create a thin `scripts/post_content_ready.py` that queries `pinterest_pins?status=eq.content_ready` (no time filter) and fires the per-brand Make.com webhook for each. This is the "manual posting" path the runbook's H1 branch expects; the repo doesn't have one.

## Why this is out of scope for the automated overnight job

The runbook's Phase 3E-H1 is explicitly "document only" — I am not permitted to modify the upstream generator. The diagnosis and proposed fixes above are the hand-off.

## Grep pointers to save Tall time

```
# Find the VIDEO/IMAGE gate:
cd /Users/homefolder/Desktop/social-media-empire
grep -rn "RUN.TYPE\|RUN_TYPE\|is.a.video.run\|video_run\b\|IMAGE.*VIDEO" --include="*.py" --include="*.yml" .

# Find the 24h window:
grep -rn "created_at.*gte\|24.*hour\|days=1\|timedelta" --include="*.py" .

# Find the active-brand rotation:
grep -rn "ACTIVE BRANDS\|active_brands\|hour=" --include="*.py" .
```
