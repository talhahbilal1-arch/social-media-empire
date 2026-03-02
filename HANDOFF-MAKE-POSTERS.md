# HANDOFF: Fix Make.com Pinterest Poster Scenarios

> **INSTRUCTION TO CLAUDE**: Run non-stop until all poster scenarios are posting pins to Pinterest successfully. Do not stop to ask questions. If one approach fails, try the next. Keep going until verified end-to-end.

---

## THE GOAL

Get 3 Make.com Pinterest poster scenarios executing successfully so that `status='ready'` pins in Supabase get posted to Pinterest and updated to `status='posted'`.

**Current state**: Stage 1 (content generation + image rendering) is FULLY WORKING via GitHub Actions. Pins accumulate in Supabase with `status='ready'` but NEVER get posted to Pinterest because the Make.com poster scenarios all fail with `BundleValidationError`.

---

## WHAT'S WORKING (DO NOT TOUCH)

- **GitHub Actions `content-engine.yml`** — runs 3x/day, generates content (Phase 0), renders images (Phase 1), generates articles (Phase 2), pushes to Vercel (Phase 3). Last verified run: 22475195514. This is DONE.
- **Supabase `pinterest_pins` table** — has all needed columns (43 total after migration 003). Schema is correct.
- **Pinterest connections** — 3 connections exist in Make.com, all show valid scopes:
  - `6738173` — Daily Deal Darling (DailyDealDarlin account)
  - `6857103` — Menopause Planner (TheMenopausePlanner account)
  - `7146197` — Fit Over 35 (pinterest2 account, re-authed 2026-02-26)

---

## THE PROBLEM

**Every Make.com scenario created via the REST API fails with:**
```
BundleValidationError: Validation failed for 2 parameter(s).
```

This happens at pre-execution time (ops=1, duration=80-200ms). No module actually runs. This affects ALL API-created scheduled scenarios regardless of blueprint content — even a minimal 1-module HTTP GET scenario fails.

### What was tried and FAILED:
1. **Setting `dlq: true`** in blueprint metadata — didn't fix it
2. **Adding `metadata.expect`** from working CLAW v2 scenarios — made scenarios `isinvalid: true` (worse)
3. **Removing `builtin:Break`** error handler — still BundleValidationError
4. **Keyboard shortcut Cmd+S / Ctrl+S** via browser extension — didn't trigger Make.com save
5. **Clicking "Exit editing"** via browser extension ref-click — didn't fix the validation
6. **Creating fresh scenarios** with different module IDs — same error
7. **Minimal 1-module test scenarios** — same error

### What was NOT tried:
1. **Manually opening each scenario in Make.com UI, clicking a module to open its settings panel, clicking OK/Save in that module panel, then saving the scenario** — the browser automation couldn't reach the canvas SVG modules
2. **Creating scenarios via Make.com UI** (not API) and configuring them there
3. **Using `pinterest:makeAnApiCall`** module instead of `pinterest:createPin` to bypass the Pinterest module validation
4. **Replacing Make.com entirely** with a Python script in GitHub Actions that posts directly to Pinterest API
5. **Using Make.com webhooks** instead of scheduled triggers (CLAW v2 webhook scenarios DID work)

---

## CURRENT SCENARIO STATE

| Scenario | ID | Brand | Status | Notes |
|----------|-----|-------|--------|-------|
| DDD Poster | **4251814** (NEW) | deals | Active, `isinvalid=false` | Recreated fresh. Old 4243032 was deleted. |
| TMP Poster | 4243035 | menopause | Active, `isinvalid=false` | Has metadata.expect patch (from failed fix attempt) |
| FO35 Poster | 4243036 | fitness | Active, `isinvalid=false` | Has metadata.expect patch (from failed fix attempt) |
| Health Monitor | 4243206 | all | Active | Also BundleValidationError |

Old deactivated scenarios (for reference, not in use):
- 4243147, 4251297, 4251305 — old content generators (replaced by GH Actions Phase 0)
- 4210274, 4210434 — CLAW v2 webhook posters (inactive but their blueprints WORKED)

---

## CREDENTIALS

- **Make.com API token**: `4cb8d3d2-947d-40a0-85da-8daf8ead80c6`
- **Make.com team ID**: `1686661`
- **Make.com org ID**: `6032269`
- **Supabase URL**: `https://epfoxpgrpsnhlsglxvsa.supabase.co`
- **Supabase anon key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVwZm94cGdycHNuaGxzZ2x4dnNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU0Nzg0MTMsImV4cCI6MjA4MTA1NDQxM30.ARgBqWk60rOC-d-FnP2CNLkKwt0Bca_wcK_LdiEjYqM`
- **Pinterest connections**: 6738173 (deals), 6857103 (menopause), 7146197 (fitness)
- **Pinterest board IDs**:
  - deals: Kitchen=874683627569113370, Organization=874683627569113339, Decor=874683627569021288, SelfCare=874683627569113342, Seasonal=874683627569114674
  - menopause: Symptoms=1076993767079898616, Hormones=1076993767079887530, SelfCare=1076993767079898619, Perimenopause=1076993767079898628, Nutrition=1076993767079898631
  - fitness: Workouts=418834902785123337, MealPrep=418834902785124651, Supplements=756745612325868912, FatLoss=418834902785125486, Motivation=418834902785122642

---

## RECOMMENDED APPROACH (try in order, keep going until one works)

### Approach 1: Add Pinterest Posting Directly to GitHub Actions (BYPASS Make.com entirely)

This is the most reliable approach. Make.com has a platform limitation with API-created scenarios. Skip it.

**How:**
1. Add a new Phase (after Phase 1 rendering, before Phase 2 articles) to `content-engine.yml` that:
   - Queries Supabase for `status='ready'` pins
   - For each pin, calls the **Pinterest API v5** directly:
     ```
     POST https://api.pinterest.com/v5/pins
     Authorization: Bearer <ACCESS_TOKEN>
     Content-Type: application/json
     {
       "title": "<pin title>",
       "description": "<pin description>",
       "board_id": "<board_id>",
       "link": "<destination_url>",
       "media_source": {"source_type": "image_url", "url": "<image_url>"}
     }
     ```
   - Updates `status='posted'`, `pinterest_pin_id`, `posted_at` on success
   - Updates `status='failed'`, `error_message`, `retry_count+1` on failure

2. **Pinterest OAuth tokens needed**: The Make.com connections (6738173, 6857103, 7146197) hold the OAuth tokens. You need to either:
   - Extract the access tokens from Make.com connections via the API (check `GET /api/v2/connections/{id}` for token data)
   - OR create new Pinterest API apps at https://developers.pinterest.com and get fresh tokens
   - OR use Make.com's `rpc` endpoint to make Pinterest API calls through the existing connections

3. Store the Pinterest access tokens as GitHub secrets: `PINTEREST_TOKEN_DEALS`, `PINTEREST_TOKEN_MENOPAUSE`, `PINTEREST_TOKEN_FITNESS`

4. Create `video_automation/pinterest_poster.py`:
   ```python
   import requests

   def post_pin_to_pinterest(access_token, pin_data):
       """Post a single pin to Pinterest via API v5"""
       resp = requests.post(
           'https://api.pinterest.com/v5/pins',
           headers={'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'},
           json={
               'title': pin_data['title'],
               'description': pin_data['description'],
               'board_id': pin_data['board_id'],
               'link': pin_data.get('destination_url', ''),
               'media_source': {'source_type': 'image_url', 'url': pin_data['image_url']}
           }
       )
       resp.raise_for_status()
       return resp.json()['id']  # pinterest pin id
   ```

5. Add posting phase to `content-engine.yml` inline Python after Phase 1 (rendering).

6. Deactivate all Make.com poster scenarios (4251814, 4243035, 4243036) since they're no longer needed.

**Pros**: No Make.com dependency. Runs reliably in GitHub Actions. Simple.
**Cons**: Need Pinterest OAuth tokens. Tokens expire and need refresh logic.

---

### Approach 2: Use Make.com RPC to Post Pins (keep Make.com connections, bypass BundleValidationError)

Use `mcp__claude_ai_Make__rpc_execute` MCP tool to call the Pinterest `createPin` action through Make.com's existing connections, without needing a running scenario.

**How:**
```
mcp__claude_ai_Make__rpc_execute(
  appName="pinterest",
  appVersion=2,
  rpcName="createPin",  # or whatever the RPC name is
  data={
    "__IMTCONN__": 6738173,
    "board_id": "...",
    "title": "...",
    ...
  }
)
```

If Make.com exposes the Pinterest actions as RPCs, this bypasses the scenario execution entirely while still using the authenticated connections.

**Step 1**: List available RPCs for the pinterest app:
```
mcp__claude_ai_Make__app-modules_list(appName="pinterest", appVersion=2, organizationId=6032269)
```

**Step 2**: Check if `createPin` action can be called via RPC. Try:
```
mcp__claude_ai_Make__rpc_execute(
  appName="pinterest",
  appVersion=2,
  rpcName="createPin",
  data={"__IMTCONN__": 6738173, "board_id": "874683627569021288", "title": "Test Pin", ...}
)
```

**Step 3**: If it works, create a Python script or GH Actions step that calls the Make.com RPC for each ready pin.

---

### Approach 3: Create Make.com Scenarios via UI (manual, then automate)

Since the BundleValidationError only affects API-created scenarios, create the scenarios manually in Make.com UI.

**How:**
1. Open https://us2.make.com/1686661/scenarios in browser
2. Click "Create a new scenario"
3. Add modules manually:
   - Module 1: HTTP → Make a request (GET Supabase for ready pins)
   - Module 2: HTTP → Make a request (PATCH status=posting)
   - Module 3: Pinterest → Create a Pin (select connection)
   - Module 4: HTTP → Make a request (PATCH status=posted)
   - Error handler on Module 3: HTTP PATCH (status=failed) + Break (3 retries)
4. Set schedule to every 3 hours
5. Save and activate
6. Repeat for all 3 brands

This is tedious but guaranteed to work since UI-created scenarios don't have BundleValidationError.

---

### Approach 4: Fix BundleValidationError via Make.com UI Save (browser automation)

The previous session tried and failed to do this via chrome browser extension. The issue is that Make.com's canvas uses SVG with custom web components (IMT-BUTTON shadow DOM) that are hard to automate.

**If trying this approach:**
1. Use Playwright (not chrome extension) to navigate to Make.com
2. You'll need to log in first — Make.com uses email/password auth
3. Navigate to each scenario edit URL
4. Click on a module (the circular nodes on the canvas) to open its settings panel
5. Click "OK" to close the module settings
6. Click the floppy disk icon or press Ctrl+S to save
7. This UI save resolves the BundleValidationError

**Make.com account**: talhahbilal1@gmail.com (password unknown to Claude — user needs to provide or use existing session)

---

## VERIFICATION STEPS (run after fixing)

1. **Check Supabase for ready pins**:
   ```bash
   curl -s "https://epfoxpgrpsnhlsglxvsa.supabase.co/rest/v1/pinterest_pins?status=eq.ready&limit=5" \
     -H "apikey: <SUPABASE_KEY>" -H "Authorization: Bearer <SUPABASE_KEY>"
   ```

2. **After posting attempt, check for posted pins**:
   ```bash
   curl -s "https://epfoxpgrpsnhlsglxvsa.supabase.co/rest/v1/pinterest_pins?status=eq.posted&order=posted_at.desc&limit=5" \
     -H "apikey: <SUPABASE_KEY>" -H "Authorization: Bearer <SUPABASE_KEY>"
   ```

3. **Verify pins appear on Pinterest boards** — check the actual Pinterest accounts.

4. **Monitor for 24h** — ensure the pipeline works across multiple scheduled runs.

---

## KEY FILES

| File | Purpose |
|------|---------|
| `.github/workflows/content-engine.yml` | Main pipeline — modify if adding Pinterest posting to GH Actions |
| `video_automation/pinterest_boards.py` | Board ID mappings per brand |
| `video_automation/content_brain.py` | Content generation (working, don't modify) |
| `video_automation/pin_image_generator.py` | Image rendering (working, don't modify) |
| `video_automation/supabase_storage.py` | Image upload (working, don't modify) |
| `database/supabase_client.py` | Supabase client helper |
| `MAKE_COM_SCENARIO_INVENTORY.md` | Full scenario documentation — update when done |
| `MEMORY.md` (in .claude/projects/) | Auto-memory — update when done |

---

## STATUS VALUES (pinterest_pins table)

```
content_ready → rendering → ready → posting → posted
                                  → failed → dead (after 3 retries)
```

- `content_ready`: Content generated by Phase 0, awaiting image render
- `rendering`: Currently being processed by Phase 1
- `ready`: Image rendered + uploaded, WAITING TO BE POSTED TO PINTEREST ← this is the backlog
- `posting`: Lock flag while posting is in progress
- `posted`: Successfully on Pinterest
- `failed`: Error occurred, eligible for retry
- `dead`: Failed 3+ times, abandoned

---

## WHEN DONE

1. Update `MAKE_COM_SCENARIO_INVENTORY.md` with the solution used
2. Update memory file at `/Users/homefolder/.claude/projects/-Users-homefolder-Desktop-social-media-empire/memory/MEMORY.md` — change the "Stage 2" section to reflect the fix
3. Commit changes with message: `fix: pinterest posting pipeline — [description of approach used]`
4. Verify at least 1 pin per brand has been posted successfully
