# Handoff — Pinterest Tool Rewrite + Make.com MCP Setup

**Date:** 2026-02-19
**Session goal:** Rewrite CLAW's broken Pinterest tool to use the Make.com webhook, wire up the Make.com MCP server, and verify end-to-end posting works.

---

## What Was Completed ✅

### 1. CLAW Pinterest Tool — Full Rewrite
**Files changed in `~/Desktop/project-claw/` (uncommitted — see below):**

- `src/tools/revenue/pinterest.ts` — **Full rewrite**
  - Old: Pinterest API v5 (`createPinterestTool(accessToken)`) — broken, API access denied
  - New: Make.com webhook (`createPinterestTool(webhookUrl, githubPat?, supabaseUrl?, supabaseKey?)`)
  - 5 operations: `postPin`, `listBoards`, `getPostHistory`, `triggerPipeline`, `getPipelineStatus`
  - All 17 boards hardcoded from `social-media-empire/video_automation/pinterest_boards.py`
  - `postPin` has 1-retry-after-60s logic + optional Supabase `content_history` logging
  - `triggerPipeline` dispatches `content-engine.yml` via GitHub API
  - `getPipelineStatus` returns last 3 GitHub Actions runs for `content-engine.yml`

- `src/security/vault.ts` — Swapped `"pinterest-access-token"` → `"make-webhook-url"` in both CredentialKey union type and KNOWN_KEYS array

- `src/cli/commands/start.ts` — Updated Pinterest registration block (lines ~171-181):
  ```typescript
  const makeWebhookUrl = await vaultGet("make-webhook-url");
  if (makeWebhookUrl) {
    const ghPat = await vaultGet("github-pat");
    const sbUrl = await vaultGet("supabase-url");
    const sbKey = await vaultGet("supabase-key");
    toolRegistry.register(createPinterestTool(makeWebhookUrl, ghPat ?? undefined, sbUrl ?? undefined, sbKey ?? undefined));
  }
  ```

**Verification:** `pnpm build` ✅ | `pnpm test` 26/26 ✅

### 2. Vault + CLAW Running
- `make-webhook-url` stored in keytar vault: `https://hook.us2.make.com/8d51h67qpdt77jgz5brhvd5c9hgvaap8`
- CLAW restarted — running as PID 61739 with **14 tools** including `pinterest`
- `pinterest-health-check` cron job added to DB (runs 5:00 UTC daily, reports to Telegram)

### 3. End-to-End Test Result
Tested via `claw send`: CLAW successfully:
- Generated content: **"Creatine After 35: The #1 Supplement for Muscle & Recovery"**
- Selected board: **Supplement Honest Reviews** (`756745612325868912`)
- Sourced a Pexels image
- Called `postPin` → **HTTP 410 Gone** (Make.com scenario was inactive)

### 4. Make.com MCP Server Configured
- `.mcp.json` in `social-media-empire/` updated with Make.com SSE server:
  ```json
  {
    "mcpServers": {
      "supabase": { "type": "http", "url": "https://mcp.supabase.com/mcp?project_ref=epfoxpgrpsnhlsglxvsa" },
      "make": { "type": "sse", "url": "https://us2.make.com/mcp/api/v1/u/<TOKEN>/sse" }
    }
  }
  ```
- SSE endpoint confirmed live (curl test returned valid session)
- MCP tools pre-approved in `~/.claude/settings.local.json` (`mcp__make__scenarios_activate` etc.)
- **MCP not yet loaded** — Claude Code session was NOT restarted before handoff

---

## What To Do Next 🔜

### Step 1 — Restart Claude Code
Close this session and reopen in `~/Desktop/social-media-empire/`. The Make.com MCP tools (`mcp__make__*`) will load automatically.

### Step 2 — Activate Make.com Scenario
In the new chat, say: **"activate the Make.com scenario and retry the creatine pin"**

Claude will:
1. Call `mcp__make__scenarios_activate` with scenario ID `3977247`
2. Retry `claw send` for the creatine pin post
3. Confirm success via Telegram

### Step 3 — Commit project-claw Changes
The 3 modified files in `~/Desktop/project-claw/` are **not yet committed**. After verifying the pin posts successfully, commit them:
```bash
cd ~/Desktop/project-claw
git add src/tools/revenue/pinterest.ts src/security/vault.ts src/cli/commands/start.ts
git commit -m "feat: rewrite Pinterest tool to use Make.com webhook"
git push
```

---

## Key Facts for Next Session

| Item | Value |
|------|-------|
| Make.com scenario ID | `3977247` |
| Make.com scenario name | "Pinterest Pin Publisher - All Brands" |
| Webhook URL | `https://hook.us2.make.com/8d51h67qpdt77jgz5brhvd5c9hgvaap8` |
| Make.com MCP token | stored in `.mcp.json` (gitignored — local only) |
| CLAW PID | 61739 (may have changed — check with `claw status`) |
| project-claw changes | 3 files modified, not committed |
| Test pin content | "Creatine After 35: The #1 Supplement for Muscle & Recovery" / Supplement Honest Reviews board |

---

## Architecture Reminder

**Two posting paths in the new Pinterest tool:**
- `postPin` — CLAW generates content on the fly, POSTs raw image + content to Make.com webhook. Good for ad-hoc Telegram requests.
- `triggerPipeline` — Dispatches `content-engine.yml` GitHub Actions workflow. Full PIL text overlay rendering, all 3 brands, 15 pins. Good for scheduled/full runs.

**CLAW vault keys now in use for Pinterest:**
- `make-webhook-url` — the Make.com webhook endpoint
- `github-pat` — for `triggerPipeline` + `getPipelineStatus`
- `supabase-url` + `supabase-key` — for `getPostHistory` logging
