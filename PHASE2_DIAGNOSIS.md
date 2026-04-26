# Phase 2 Diagnosis — Why createPin "Succeeds" But No Pins Appear

**Run start:** 2026-04-26 ~06:05 UTC
**Branch:** `claude/diagnose-pinterest-pins-phase2-H2rnL` (assigned by harness)
**Read-only phase:** Phase A — BLOCKED (see `BLOCKED_NEED_HUMAN.md`)

## Pre-flight summary

- No credentials (`MAKE_API_TOKEN`, `SUPABASE_KEY`, `PEXELS_API_KEY`, Pinterest
  tokens, `ANTHROPIC_API_KEY`) are set in this environment.
- All five diagnostic endpoints (Pinterest API, Pinterest web, Pexels, Supabase
  REST, Make.com) return **HTTP 503** from this sandbox. No outbound network
  egress to those hosts.
- Last night's artifacts (`DIAGNOSTIC_REPORT.md`, `seed_result.json`,
  `account_mapping.json`, `MORNING_REPORT.md`, `GENERATOR_STATUS.md`,
  `scripts/seed_starter_pins.py`) are present in the working tree and were
  read in full.

Because Phase A1–A5 cannot be executed, this diagnosis is necessarily
**hypothesis-ranked from prior evidence**, not evidence-confirmed. The
ROOT_CAUSE line at the end reflects that uncertainty.

## What is known from prior-run artifacts

### From `seed_result.json`

- 9 rows inserted into `pinterest_pins` at `2026-04-24T05:36:45Z`, status
  `content_ready`, 3 per brand (fitness/deals/menopause), full attempt
  succeeded (no minimal-column retry).
- Only the UUIDs are recorded — **the inserted `image_url` values are not
  captured anywhere on disk.** They can only be recovered via Supabase query.

### From `scripts/seed_starter_pins.py`

- The seed script requested `src.large2x` (with `large` fallback) from Pexels
  v1 search using `orientation=portrait, size=large`.
- This matches Phase 2 hypothesis P5's note that `large2x` may be less stable
  than `original`.
- Board IDs used (hardcoded in PLAN dict):
  - fitness → `418834902785124651`
  - deals → `874683627569113370`
  - menopause → `1076993767079898628`
  These match `account_mapping.json` `board_id_preferred` per brand and were
  derived from each brand's most recent `status=posted` rows.

### From the user-supplied Phase 2 prompt (verified Make.com data)

- All 9 dispatched executions returned `status: 1` (Make.com success).
- Each used 2 ops, transferred ~2,100 bytes (smaller than historical
  successful posts at 2,400–3,000 bytes — possible signal of a smaller
  Pinterest response).
- No further executions on any poster scenario in the ~22 hours after.
- Tall reports zero pins visible on any of the three Pinterest accounts.

### From `account_mapping.json`

- The `account` column is always NULL; brand routing is via `brand`.
- Board IDs were inferred from `status=posted` rows (not freshly verified
  against Pinterest as live boards). They could be stale.
- A single `board_id_preferred` per brand plus 4 alternatives each.

### From `CLAUDE.md` "Make.com Scenarios" section (durable convention)

- Per-brand dedicated scenarios exist (Fitness v3, Deals v4, Menopause v4),
  each with its own Pinterest OAuth.
- A unified fallback scenario also exists with router + per-route filter.
- The convention asserts "**each has its own Pinterest OAuth**" — meaning if
  the convention has been honored, P4 (single-connection-for-three-accounts)
  would NOT be the cause. If the convention has *drifted* — i.e., the three
  scenarios share one connection — P4 IS the cause.

## A1 — createPin response capture

**Status: BLOCKED.** Cannot reach Make.com API; no token. The 6 known
execution IDs (Deals v4: 3, Fitness v3: 3) and the unknown Menopause v4 IDs
remain unfetched.

**Implication:** The single most informative piece of evidence — what
Pinterest actually replied to createPin — is not available this run. Without
it, P1 vs P3 vs P4 cannot be distinguished by direct evidence.

## A2 — Image URL liveness

**Status: BLOCKED.** `seed_result.json` does not record the URLs; Supabase is
unreachable to query them; Pexels is unreachable to re-resolve them.

**Reasoning from code (`scripts/seed_starter_pins.py`):** The script returned
the first photo's `large2x` URL from Pexels search for hardcoded queries
("man lifting weights gym", etc.). Pexels CDN URLs *generally* do not rotate
on a 22-hour timescale, but the runbook explicitly raises P5 because they
*can*. Cannot confirm or rule out.

## A3 — Board ID liveness

**Status: BLOCKED.** No Pinterest API access. Pinterest does not expose a
public deep-link for boards by numeric ID alone (boards live under
`/<username>/<board-name>/`), so even the "fallback to public URL" check from
the runbook is not actionable here.

**Reasoning from `account_mapping.json`:** The board IDs were extracted from
real `status=posted` rows in `pinterest_pins`, so at some point Pinterest did
accept those IDs. They could have been archived/renamed since. Unverifiable.

## A4 — Make.com Pinterest connection enumeration

**Status: BLOCKED.** Cannot reach Make.com API.

**Reasoning from CLAUDE.md:** Convention says three connections, one per
account. If reality matches convention, P4 is not the cause. The fact that
all 9 executions completed in a ~4-second window (06:18:17–21 UTC) and
returned the same `status: 1` is consistent with EITHER three connections all
working OR one connection that returned success while only one account's pins
actually went live.

## A5 — Supabase per-pin status

**Status: BLOCKED.** Cannot query Supabase.

**Indirect inference:** Last night's `MORNING_REPORT.md` notes that "the
Activator trigger step was skipped (no `MAKE_API_TOKEN`)." So *something*
between then and the next morning *did* fire the three poster scenarios on
the seeded rows. The most likely path is either (a) the GitHub Actions
content-engine.yml cron at 04:00 UTC found the seeds via Phase 1's window,
or (b) Tall ran the manual `gh workflow run` commands the runbook proposed.
Either way, all 9 ran, all 9 dispatched. The Supabase row state would tell
us whether `status=posted` was set with a real `pin_id` (suggesting Pinterest
returned success) or whether `status=failed` was set (suggesting an upstream
error). Cannot read this without `SUPABASE_KEY`.

## A6 — Hypothesis ranking (no live evidence)

Without A1–A5, hypotheses can only be ranked by prior probability informed
by what's documented in the repo. **This is opinion, not evidence**, and
must be confirmed by a re-run with credentials before any non-documentation
fix is applied.

| Rank | Hypothesis | Why ranked this way |
|---|---|---|
| 1 | **P4 — Wrong account / single connection** | Highest-impact failure mode that fits "createPin succeeds, no pins appear." If a single Pinterest connection (say, Deals) handles all 3 scenarios, then 6 of 9 executions tried to post to boards owned by other accounts. Pinterest's response to that varies — sometimes a benign-looking 200, sometimes a board-ownership error that may not surface as a Make-level failure depending on how the scenario handles it. The ~2,100-byte transfer (smaller than historical 2,400–3,000) is consistent with Pinterest returning a degenerate response. |
| 2 | **P1 — Pinterest media rejection** | Pinterest's createPin is asynchronous on the media side. A 200 response with a pin_id is no guarantee the pin will be processed. Less likely than P4 because all 9 pins would have to fail similarly across three different image queries. |
| 3 | **P2 — Dead/wrong/secret board** | Possible but `account_mapping.json` derived these from `posted` rows, so the boards worked at some point. Three boards going dead simultaneously is unlikely. |
| 4 | **P3 — OAuth scope insufficient** | Would have been caught at the connection setup stage in Make. Possible if a connection was reauthed without `pins:write`. |
| 5 | **P5 — Dead Pexels image URLs** | Pexels CDN URLs are usually stable for weeks; 22 hours is well within typical lifetime. Possible if the specific image was deleted by the photographer, but unlikely for all 9. |

## Final ROOT_CAUSE

```
ROOT_CAUSE: UNKNOWN_STOP_FOR_HUMAN
```

**Justification:** Phase A is fully blocked. Picking any specific
ROOT_CAUSE without the createPin response payload (A1) would violate
Rule #1 ("never invent values"). Per the runbook's own gate
("If COMPOUND or UNKNOWN_STOP_FOR_HUMAN: write `BLOCKED_NEED_HUMAN.md`
with a 5-bullet summary and STOP. Do not proceed to Phase B."),
Phase B is not executed.

The documentation-only branches P2, P3, P4 are still produced because the
runbook explicitly states they are document-only fixes, and they cost
nothing to prepare — they will be useful regardless of which branch
actually wins after the next run captures live data.
