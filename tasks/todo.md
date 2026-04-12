# Pinterest Automation Fix — Deals + Menopause Not Posting (April 12, 2026)

## Diagnosis

**Symptom:** Fitness brand posts to Pinterest daily, but deals and menopause don't.

**Evidence gathered:**

1. `monitoring/system-health-report.md` (2026-03-31) showed all 3 brand scenarios
   (Fitness v3, Deals v4, Menopause v4) active and healthy with 167/383/383
   executions. So the issue developed sometime in April.

2. `.github/workflows/content-engine.yml` Phase 1b sends the webhook payload:
   ```python
   payload = {
       'pin_id': ...,
       'brand': brand,          # short key: "fitness", "deals", "menopause"
       ...
   }
   ```

3. `docs/MANUAL_SETUP_GUIDE.md` + `docs/HANDOFF.md` document that the Make.com
   routing filters expect **hyphenated** brand names (`fitness-made-easy`,
   `daily-deal-darling`, `menopause-planner`), NOT the short keys.

4. `prompt-packs/post-product-pins.py` line 220 sends `"brand": "fitness-made-easy"`
   (hyphenated) — and that script is documented as working.

5. `HANDOFF.md` line 96: only `MAKE_WEBHOOK_DEALS` was updated to point to the new
   unified `pinterest-pin-publisher` scenario. Fitness + menopause secrets still
   point to the older per-brand scenarios.

**Most likely root cause:** Any Make.com scenario (new or old) that filters by
`brand == "daily-deal-darling"` or `brand == "menopause-planner"` REJECTS the
workflow's payload because the workflow sends the short key instead of the
hyphenated slug. Fitness happens to still work because its webhook either has
no filter (dedicated per-brand scenario) or matches the short key by accident.

Additionally, if any webhook secret is empty, the workflow silently skips
(`print('SKIP — no webhook URL configured'); continue`) with no Supabase
error log, so the problem is invisible from monitoring.

## Fix Plan

Scope: `.github/workflows/content-engine.yml` + `.github/workflows/pin-watchdog.yml`
+ `scripts/preflight_check.py` + `CLAUDE.md`. No changes to Python modules needed.

- [x] Read codebase to understand the content engine flow
- [x] Confirm brand key mismatch in webhook payload
- [x] Add brand slug mapping (`fitness` → `fitness-made-easy`, etc.) in
      content-engine.yml Phase 1b
- [x] Send both the hyphenated `brand` slug AND the short `brand_key` in the
      Make.com payload, so dedicated AND filtered scenarios both work
- [x] Add unified `MAKE_WEBHOOK` fallback env var — if the brand-specific
      webhook secret is empty, fall back to the unified one
- [x] Upgrade the "SKIP — no webhook URL" path: log a CRITICAL error to
      Supabase `errors` table AND mark pin `failed` so watchdog sees it
- [x] Wire the new `MAKE_WEBHOOK` env into `content-engine.yml` and
      `pin-watchdog.yml` workflow env blocks
- [x] Update pin-watchdog.yml webhook check to accept the same fallback
- [x] Update `scripts/preflight_check.py` to treat unified fallback as valid
- [x] Update `CLAUDE.md` to document the brand-slug convention correctly
- [x] Syntax check both YAML files + inline Python heredocs
- [ ] Commit + push to claude/fix-pinterest-automation-8hdVZ

## Review

**Root cause:** The content-engine Phase 1b webhook payload sent the short brand
key (`fitness`/`deals`/`menopause`) as the `brand` field, but Make.com route
filters compare against the hyphenated slug (`fitness-made-easy` /
`daily-deal-darling` / `menopause-planner`). Any filtered route silently
rejected deals and menopause pins while fitness kept working because its
webhook happens to point to a dedicated (unfiltered) scenario. On top of that,
if a brand's webhook secret was empty, the workflow silently `continue`d with
no Supabase error, so the problem was invisible from monitoring.

**Fix:** Five surgical edits, no module refactors.

1. `content-engine.yml` Phase 1b — added `BRAND_SLUG` mapping, send hyphenated
   slug as `brand` in the payload (short key moved to `brand_key` for any
   legacy consumer).
2. `content-engine.yml` Phase 1b — added `MAKE_WEBHOOK` unified fallback: if
   `MAKE_WEBHOOK_<BRAND>` is empty, use `MAKE_WEBHOOK`.
3. `content-engine.yml` Phase 1b — replaced the silent `continue` skip with:
   log to `errors` table (`severity=high`), mark pin `status='failed'` with an
   explicit `error_message`. Watchdog now sees the dropped pins.
4. `pin-watchdog.yml` — same unified fallback logic so the 5/5 webhook check
   doesn't false-positive when `MAKE_WEBHOOK` alone is set.
5. `scripts/preflight_check.py` — treat `MAKE_WEBHOOK` as a valid configuration
   source in section [5].
6. `CLAUDE.md` — documented the hyphenated-slug convention explicitly, listed
   `MAKE_WEBHOOK` secret, removed the stale dead webhook URL from the Make.com
   section and replaced it with the per-brand + unified fallback architecture.

**What the user needs to do next:** Add a GitHub repository secret called
`MAKE_WEBHOOK` pointing at any working unified Make.com scenario URL. Once set,
the next content-engine run will start posting deals + menopause pins via the
fallback, even if their dedicated scenarios are still broken. If the dedicated
scenarios come back online, the workflow automatically prefers them.

**Files changed:**
- `.github/workflows/content-engine.yml`
- `.github/workflows/pin-watchdog.yml`
- `scripts/preflight_check.py`
- `CLAUDE.md`
- `tasks/todo.md`
