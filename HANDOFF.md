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

## ✅ COMPLETED — 2026-02-19

All steps done in follow-up session.

### What Was Resolved

**Root cause:** Two stale values from when the Make.com scenario was rebuilt:
1. **Webhook URL changed** — old `8d51h67qpdt77jgz5brhvd5c9hgvaap8` was dead; new hook (`pinterest-pin-publisher`) is `6i5khyaxd3jf5ask3oyvj98iqnv996sk`
2. **Brand name format** — filters expect hyphenated names (`fitness-made-easy`), not underscored (`fitness_made_easy`)

**Make.com MCP note:** SSE endpoint returns HTTP 524 (Cloudflare timeout) — MCP tools will not load. Used browser automation + direct webhook calls instead.

### Step 1 ✅ — Scenario confirmed active
Verified via Make.com UI (`aria-checked: true`). User had already toggled it on.

### Step 2 ✅ — Creatine pin posted
- Discovered correct webhook URL via Make.com Webhooks page
- Sent pin with `"brand": "fitness-made-easy"` (hyphenated)
- **Result:** Success — 2 ops, 1.7 KB at 10:32 PM (Feb 18)

### Step 3 ✅ — project-claw changes committed
Already committed as `23d8e03 feat: rewrite Pinterest tool to use Make.com webhook` before handoff was written.

---

## Current Webhook URLs

| Hook name | URL |
|-----------|-----|
| `pinterest-pin-publisher` | `https://hook.us2.make.com/6i5khyaxd3jf5ask3oyvj98iqnv996sk` |

Updated in: GitHub secret `MAKE_WEBHOOK_DEALS`, CLAW vault `make-webhook-url`, MEMORY.md

---

## Architecture Reminder

**Two posting paths in the new Pinterest tool:**
- `postPin` — CLAW generates content on the fly, POSTs raw image + content to Make.com webhook. Good for ad-hoc Telegram requests.
- `triggerPipeline` — Dispatches `content-engine.yml` GitHub Actions workflow. Full PIL text overlay rendering, all 3 brands, 15 pins. Good for scheduled/full runs.

**CLAW vault keys now in use for Pinterest:**
- `make-webhook-url` — the Make.com webhook endpoint
- `github-pat` — for `triggerPipeline` + `getPipelineStatus`
- `supabase-url` + `supabase-key` — for `getPostHistory` logging
