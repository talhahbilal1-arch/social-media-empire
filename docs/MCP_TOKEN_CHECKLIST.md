# MCP Token Checklist

Exactly which tokens to obtain before running `scripts/install_mcps.sh`, where to
generate each one, and the minimum scopes required. Tokens are saved to
`~/.claude/mcp-secrets.env` (chmod 600) by the installer — never commit that
file.

| # | Service | Env var | Generate at (exact URL) | Required scopes / permissions | Why we need it |
|---|---------|---------|-------------------------|-------------------------------|----------------|
| 1 | Supabase | `SUPABASE_ACCESS_TOKEN` | https://supabase.com/dashboard/account/tokens | Full account access (personal access token) | Query `content_history`, `errors`, `pinterest_pins` across both Supabase projects without hand-writing SQL. |
| 2 | Stripe | `STRIPE_SECRET_KEY` | https://dashboard.stripe.com/apikeys | Secret key (`sk_live_...` for prod, `sk_test_...` for test). Optionally create a **restricted key** with read access to `charges`, `customers`, `subscriptions`, `products`, `prices`, `invoices`. | MRR, refund rate, top products by revenue. |
| 3 | Playwright | — (none) | — | — | Headless browser for Gumroad uploads, Pinterest scraping, Late key refresh. Chromium downloads on first run. |
| 4 | GitHub | `GITHUB_PERSONAL_ACCESS_TOKEN` | https://github.com/settings/tokens (classic) — or https://github.com/settings/personal-access-tokens/new (fine-grained) | Classic: `repo`, `workflow`, `read:org`, `read:user`. Fine-grained: `Actions: read/write`, `Contents: read/write`, `Pull requests: read/write`, `Metadata: read`. | Inspect failed workflow runs across 35 active workflows, open PRs, read logs. |
| 5 | Vercel | — (OAuth) | — (HTTP transport triggers OAuth in the browser) | Browser grants the Claude client access to the workspace. Revoke any time at https://vercel.com/account/tokens. | Tail production logs for fitover35 / deals / menopause deploys. |
| 6 | Sentry | `SENTRY_AUTH_TOKEN` | https://sentry.io/settings/account/api/auth-tokens/ | `org:read`, `project:read`, `event:read`, `issue:read`. Add `project:write` + `event:write` only if you want Claude to resolve issues. | Aggregate Python worker + Vercel function errors beyond the Supabase `errors` table. |
| 7 | Slack | `SLACK_BOT_TOKEN` | https://api.slack.com/apps → create app → **OAuth & Permissions** → **Install to workspace** | Bot scopes: `chat:write`, `channels:read`, `channels:history`, `groups:read`, `users:read`, `search:read`, `files:read`. Copy the **Bot User OAuth Token** (`xoxb-...`). | Post pipeline summaries to #ops, search past alerts without leaving Claude. |
| 8 | Notion | `NOTION_API_KEY` | https://www.notion.so/profile/integrations → **New integration** (type: internal) | No scope selector — Notion uses per-page sharing. After creating the integration, open each target page/database → `...` → **Add connections** → pick the integration. | Centralise affiliate-program tracking, phone-action queue, weekly roadmap. |
| 9 | Figma | `FIGMA_API_KEY` | https://www.figma.com/settings (scroll to **Personal access tokens** → **Generate new token**) | At minimum `file_content:read`, `file_metadata:read`. Add `file_dev_resources:read` if you use Dev Mode frames. | Extract frame specs from pin template files so PIL renders match design. |
| 10 | Context7 | — (none) | — | — | Public docs MCP; fetches up-to-date library docs (Supabase Python, Stripe, PIL, Anthropic SDK). |

## Pre-flight check

Before running the installer, confirm:

- [ ] `claude` CLI is on PATH (`claude --version`)
- [ ] Node.js 18+ is installed (`node --version`) — every stdio MCP uses `npx`
- [ ] For each row above that has an env var: the token is copied to clipboard
- [ ] `~/.claude/` is writable (the installer creates `mcp-secrets.env` with `chmod 600`)

Then:

```bash
bash scripts/install_mcps.sh
```

The installer prompts y/n per server, skips anything already registered, and
exits with a summary. After it finishes, **restart Claude Code** so the new
servers are picked up, then verify with `claude mcp list`.

## Rotating a token

1. Revoke the old token at the provider's dashboard (URLs above).
2. Generate a new one.
3. Edit `~/.claude/mcp-secrets.env` and replace the `export FOO=...` line, or
   delete the line and re-run the installer — it will re-prompt only for the
   missing var.
4. `claude mcp remove <name>` then re-run the installer for that single server.

## Never commit

`~/.claude/mcp-secrets.env` lives in your home directory, outside this repo.
Do not move it into the repo, do not paste tokens into `CLAUDE.md`, do not
echo tokens in commit messages.
