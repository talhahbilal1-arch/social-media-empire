# MCP Setup for the Social Media Empire

Operational guide for the MCP servers installed by `scripts/install_mcps.sh`.
Each server is chosen against a concrete pain point in this repo (see
`CLAUDE.md` for the system architecture). Tokens live in
`~/.claude/mcp-secrets.env` (chmod 600) — never in the repo.

## One-shot install

```bash
bash scripts/install_mcps.sh
```

The script prompts `y/n` per server, reuses any token already saved in
`~/.claude/mcp-secrets.env`, and skips servers that are already registered.

---

## The servers, mapped to real pain points

### 1. Supabase — `@supabase/mcp-server-supabase`
**Pain point:** Every pipeline phase writes to Supabase (`content_history`,
`errors`, `agent_runs`, `pinterest_pins`, `generated_articles`,
`daily_trending`, etc.) across **two projects** (`epfoxpgrpsnhlsglxvsa` prod,
`bjacmhjtpkdcxngkasux` TikTok). Today you have to hand-write SQL in the web
editor or Python clients to answer "which pin performed best this week".

**Wins:**
- "Show me the last 10 rows in `errors` where `severity = 'high'`."
- "Which pins from last week had the lowest CTR?"
- "List tables that are missing the `severity` column."

**Try after install:** `Show me pins from last week with lowest CTR.`

### 2. Stripe — `@stripe/mcp`
**Pain point:** Revenue tracking is currently manual. Gumroad + upcoming
Stripe products for the Fitness / Menopause / Deals brands. You want MRR,
refund rate, and top products without opening the dashboard.

**Wins:**
- "What's my MRR right now?"
- "List the last 20 Stripe charges and group by product."
- "Which customers have failed payments in the last 7 days?"

**Try after install:** `What's my MRR right now?`

### 3. Playwright — `@playwright/mcp@latest`
**Pain point:** Gumroad, Pinterest, Make.com, Late, and Etsy onboarding
require clicking through dashboards. You've flagged in `CLAUDE.md` that
Etsy banking/billing setup is manual and Late API keys are expired.

**Wins:**
- Upload Gumroad PDFs without manual drag-and-drop.
- Scrape Pinterest pin analytics the API doesn't expose.
- Screenshot deployed brand sites to verify affiliate tag hygiene.

**Try after install:** `Open gumroad.com/products and tell me which products have no file attached.`

### 4. GitHub — `@modelcontextprotocol/server-github`
**Pain point:** 35 active workflows + 24 archived. Watchdog, weekly-health,
pin-watchdog — diagnosing a red run means tab-hopping.

**Wins:**
- "Which workflows failed in the last 24 hours?"
- "Show logs for the most recent `content-engine.yml` run."
- "Open a PR from this branch."

**Try after install:** `List the last 5 failed workflow runs on main.`

### 5. Vercel (HTTP / OAuth) — `https://mcp.vercel.com/`
**Pain point:** Three Vercel projects (fitover35, deals, menopause) + the
PilotTools deploy + Anti-Gravity site queued. Log tailing and deployment
status is a browser round-trip.

**Wins:**
- "Tail the logs for the fitover35 production deployment."
- "Which projects failed their last build?"
- "Roll back `dailydealdarling` to the previous deployment."

**Try after install:** `Tail the logs for the fitover35 production deployment.`

> Uses HTTP transport + Vercel OAuth on first use — no static token.

### 6. Sentry — `@sentry/mcp-server`
**Pain point:** Errors are logged into a Supabase `errors` table, but only
after the script survives to catch them. A proper error aggregator for
the Python workers + Vercel functions closes that gap.

**Wins:**
- "What's the most frequent error in `content-engine` this week?"
- "Show me the stack trace for issue XYZ-123."

**Try after install:** `Summarise unresolved errors grouped by release.`

### 7. Slack — `@modelcontextprotocol/server-slack`
**Pain point:** `emergency-alert.yml` and `weekly-health-report.yml` already
push notifications. Being able to *reply* from Claude closes the loop.

**Wins:**
- "Post a summary of today's content engine run to #ops."
- "Search Slack for the Make.com webhook ID we set last week."

**Try after install:** `Send "#ops content engine green" to the ops channel.`

### 8. Notion — `@notionhq/notion-mcp-server`
**Pain point:** Roadmap + handoff docs (PHONE-ACTION-CHECKLIST,
HANDOFF-affiliate-signups, etc.) are scattered. Notion is a natural home
for affiliate program tracking and phone-action queues.

**Wins:**
- "Add a row to the Affiliate Programs database for Semrush."
- "Fetch the current week's roadmap page as markdown."

**Try after install:** `Create a Notion page called "This week" with today's pipeline status.`

### 9. Figma — `figma-developer-mcp`
**Pain point:** Pin overlay styles (gradient / box_dark / numbered_list /
big_stat / split_layout) are PIL-only. Design iteration is slow. Figma
MCP turns Figma frames into layout specs that `pin_image_generator.py`
can mimic.

**Wins:**
- "Read the `Pin Templates` Figma file and list each frame's dimensions and colours."
- "Export this frame as JSON so I can replicate it with PIL."

**Try after install:** `List the frames in Figma file <file-id>.`

### 10. Context7 — `@upstash/context7-mcp`
**Pain point:** You're working with Supabase Python, Claude SDK, Playwright,
Stripe Python, Make.com, Pinterest API — library version drift bites
(`gemini-2.5-flash` migration was a recent example).

**Wins:**
- "Show me the current Supabase Python upsert syntax."
- "What's the latest Anthropic SDK streaming API?"

**Try after install:** `Using context7, show Stripe Python 2025 subscription creation.`

---

## How to obtain each token

Exact URLs that take you straight to the token generation page.

| Service | Where to generate |
|---|---|
| Supabase | https://supabase.com/dashboard/account/tokens — click **Generate new token**. Store as `SUPABASE_ACCESS_TOKEN`. |
| Stripe | https://dashboard.stripe.com/apikeys — copy the **Secret key** (`sk_live_...` or `sk_test_...`). Store as `STRIPE_SECRET_KEY`. |
| Playwright | No token. Chromium/Firefox download on first run. |
| GitHub | https://github.com/settings/tokens (classic) — scopes: `repo`, `workflow`, `read:org`, `read:user`. Store as `GITHUB_PERSONAL_ACCESS_TOKEN`. |
| Vercel | No token — the HTTP transport opens an OAuth flow on first use. Accept the workspace scope in the browser. |
| Sentry | https://sentry.io/settings/account/api/auth-tokens/ — scopes: `org:read`, `project:read`, `event:read`, `issue:read`. Store as `SENTRY_AUTH_TOKEN`. |
| Slack | https://api.slack.com/apps → create app → **OAuth & Permissions** → bot scopes: `chat:write`, `channels:read`, `channels:history`, `users:read`, `search:read` → **Install to workspace** → copy **Bot User OAuth Token** (`xoxb-...`). Store as `SLACK_BOT_TOKEN`. |
| Notion | https://www.notion.so/profile/integrations → **New integration** (internal) → copy the secret → in Notion, share each target page/database with the integration. Store as `NOTION_API_KEY`. |
| Figma | https://www.figma.com/settings → **Personal access tokens** → **Generate new token**. Store as `FIGMA_API_KEY`. |
| Context7 | No token. |

See `docs/MCP_TOKEN_CHECKLIST.md` for the one-line checklist version.

---

## Verifying the install

```bash
claude mcp list
```

Every row should show green / connected. If a row says `failed`, see below.

---

## Troubleshooting

**`claude mcp list` shows `failed`**
- Restart Claude Code — new servers are only picked up on a fresh session.
- Re-run `claude mcp list` after 10 seconds; first-run `npx -y` downloads can race the handshake.

**Token rejected / 401 / 403**
- Verify the scope on the token generation page (GitHub and Sentry tokens especially need explicit scopes).
- Supabase: the token must be a **personal access token** (account settings), not a project anon/service key.
- Stripe: secret key only — publishable keys (`pk_...`) will be rejected.
- Slack: you must click **Install to workspace** after adding scopes or the token won't have them.

**"command not found: npx"**
- Install Node.js 18+ from https://nodejs.org. Every stdio MCP server uses `npx`.

**Notion returns "page not found"**
- Integrations are invisible by default. Open the page or database in Notion → `...` → **Add connections** → pick your integration.

**Vercel prompts for OAuth every run**
- Tokens refresh on expiry. If it reprompts daily, check that your browser allows cookies for `vercel.com`.

**Figma MCP returns empty**
- Personal tokens can only read files you have access to. Confirm you can open the file in the browser with the same account.

---

## Uninstall

```bash
claude mcp remove <name>
# e.g.
claude mcp remove stripe
```

To wipe a saved token, edit `~/.claude/mcp-secrets.env` and delete the
`export FOO=...` line. The file is `chmod 600` and must stay in your home
directory — **never** commit it.
