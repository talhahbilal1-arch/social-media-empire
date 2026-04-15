#!/usr/bin/env bash
#
# install_mcps.sh — interactive installer for Claude Code MCP servers.
#
# Prompts y/n per server, reads/writes tokens to ~/.claude/mcp-secrets.env
# (chmod 600), and runs `claude mcp add ...` for each chosen server.
# Idempotent: already-added servers are skipped.
#
set -euo pipefail

# ---------- styling ----------
BOLD=$(printf '\033[1m')
DIM=$(printf '\033[2m')
RED=$(printf '\033[31m')
GREEN=$(printf '\033[32m')
YELLOW=$(printf '\033[33m')
BLUE=$(printf '\033[34m')
RESET=$(printf '\033[0m')

info()  { printf "%s[info]%s %s\n"  "$BLUE"   "$RESET" "$*"; }
ok()    { printf "%s[ ok ]%s %s\n"  "$GREEN"  "$RESET" "$*"; }
warn()  { printf "%s[warn]%s %s\n"  "$YELLOW" "$RESET" "$*"; }
err()   { printf "%s[err ]%s %s\n"  "$RED"    "$RESET" "$*" 1>&2; }

# ---------- pre-flight ----------
if ! command -v claude >/dev/null 2>&1; then
  err "The 'claude' CLI was not found in PATH."
  err "Install it first: https://docs.claude.com/en/docs/claude-code/setup"
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  warn "'npx' not found — most stdio MCP servers launch via npx."
  warn "Install Node.js 18+ (https://nodejs.org) before continuing."
fi

SECRETS_DIR="${HOME}/.claude"
SECRETS_FILE="${SECRETS_DIR}/mcp-secrets.env"
mkdir -p "$SECRETS_DIR"
if [ ! -f "$SECRETS_FILE" ]; then
  touch "$SECRETS_FILE"
fi
chmod 600 "$SECRETS_FILE"

# ---------- helpers ----------

# Load existing secrets from the file without echoing them.
# shellcheck disable=SC1090
load_secrets() {
  set +u
  # shellcheck disable=SC1091
  . "$SECRETS_FILE" 2>/dev/null || true
  set -u
}

# Prompt y/n — returns 0 for yes, 1 for no.
prompt_yn() {
  local prompt="$1"
  local reply
  while :; do
    printf "%s [y/n]: " "$prompt"
    read -r reply </dev/tty || reply="n"
    case "$reply" in
      y|Y|yes|YES) return 0 ;;
      n|N|no|NO|"") return 1 ;;
      *) echo "Please answer y or n." ;;
    esac
  done
}

# Prompt silently for a secret and write it to ~/.claude/mcp-secrets.env.
# Never echoes the value. Args: VAR_NAME  "Friendly description"
capture_secret() {
  local var="$1"
  local desc="$2"
  local value=""
  printf "  Enter %s (input hidden): " "$desc"
  # -s suppresses echo on bash
  read -rs value </dev/tty || value=""
  printf "\n"
  if [ -z "$value" ]; then
    warn "Empty value — skipping this server."
    return 1
  fi
  # Strip any existing assignment of this var from the file, then append.
  local tmp
  tmp=$(mktemp)
  grep -v "^export ${var}=" "$SECRETS_FILE" > "$tmp" 2>/dev/null || true
  printf 'export %s=%q\n' "$var" "$value" >> "$tmp"
  mv "$tmp" "$SECRETS_FILE"
  chmod 600 "$SECRETS_FILE"
  # Export into current shell for the add command below
  export "$var=$value"
  ok "  Saved ${var} to ${SECRETS_FILE} (chmod 600)."
  return 0
}

# Ensure the given env var has a value — from the secrets file or by prompting.
ensure_secret() {
  local var="$1"
  local desc="$2"
  load_secrets
  if [ -n "${!var-}" ]; then
    ok "  Using cached ${var} from ${SECRETS_FILE}."
    return 0
  fi
  capture_secret "$var" "$desc"
}

# Check whether a given MCP server name is already registered.
already_installed() {
  local name="$1"
  claude mcp list 2>/dev/null | awk '{print $1}' | grep -Fxq "$name"
}

# ---------- state ----------
INSTALLED=()
SKIPPED=()
FAILED=()

# Install one MCP server.
# Args: name, needs_secret ("yes"/"no"), secret_var, secret_desc, cmd_template
# cmd_template uses $SECRET_VAL as placeholder for the secret.
install_mcp() {
  local name="$1"
  local needs_secret="$2"
  local secret_var="$3"
  local secret_desc="$4"
  shift 4
  # Remaining args are the literal command to run
  printf "\n%s=== %s ===%s\n" "$BOLD" "$name" "$RESET"

  if already_installed "$name"; then
    ok "'$name' is already registered with claude — skipping."
    SKIPPED+=("$name (already installed)")
    return 0
  fi

  if ! prompt_yn "Install MCP server '$name'?"; then
    SKIPPED+=("$name (declined)")
    return 0
  fi

  if [ "$needs_secret" = "yes" ]; then
    if ! ensure_secret "$secret_var" "$secret_desc"; then
      FAILED+=("$name (no secret provided)")
      return 0
    fi
  fi

  info "Running: claude mcp add $name ..."
  if "$@"; then
    ok "Installed '$name'."
    INSTALLED+=("$name")
  else
    err "Failed to install '$name'."
    FAILED+=("$name (claude mcp add failed)")
  fi
}

# ---------- intro ----------
cat <<EOF
${BOLD}Claude Code MCP Installer${RESET}
${DIM}Secrets are stored in ${SECRETS_FILE} (chmod 600). This file is in your
home directory and must NEVER be committed to the repo.${RESET}

You will be prompted y/n for each server. Required API tokens are read from
${SECRETS_FILE} if already present, otherwise prompted for (input hidden).

EOF

load_secrets

# ---------- 1. Supabase ----------
# shellcheck disable=SC2016
install_mcp "supabase" "yes" "SUPABASE_ACCESS_TOKEN" "Supabase personal access token" \
  bash -c 'claude mcp add supabase -- npx -y @supabase/mcp-server-supabase --access-token "$SUPABASE_ACCESS_TOKEN"'

# ---------- 2. Stripe ----------
install_mcp "stripe" "yes" "STRIPE_SECRET_KEY" "Stripe secret key (sk_live_... or sk_test_...)" \
  bash -c 'claude mcp add stripe -- npx -y @stripe/mcp --tools=all --api-key="$STRIPE_SECRET_KEY"'

# ---------- 3. Playwright ----------
install_mcp "playwright" "no" "" "" \
  claude mcp add playwright -- npx -y @playwright/mcp@latest

# ---------- 4. GitHub ----------
install_mcp "github" "yes" "GITHUB_PERSONAL_ACCESS_TOKEN" "GitHub personal access token (classic, with repo+workflow scope)" \
  bash -c 'claude mcp add github --env GITHUB_PERSONAL_ACCESS_TOKEN="$GITHUB_PERSONAL_ACCESS_TOKEN" -- npx -y @modelcontextprotocol/server-github'

# ---------- 5. Vercel (HTTP transport, OAuth) ----------
install_mcp "vercel" "no" "" "" \
  claude mcp add vercel --transport http https://mcp.vercel.com/

# ---------- 6. Sentry ----------
install_mcp "sentry" "yes" "SENTRY_AUTH_TOKEN" "Sentry user auth token (org:read + project:read scopes)" \
  bash -c 'claude mcp add sentry --env SENTRY_AUTH_TOKEN="$SENTRY_AUTH_TOKEN" -- npx -y @sentry/mcp-server'

# ---------- 7. Slack ----------
install_mcp "slack" "yes" "SLACK_BOT_TOKEN" "Slack bot token (xoxb-...)" \
  bash -c 'claude mcp add slack --env SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN" -- npx -y @modelcontextprotocol/server-slack'

# ---------- 8. Notion ----------
install_mcp "notion" "yes" "NOTION_API_KEY" "Notion internal integration token (secret_...)" \
  bash -c 'claude mcp add notion --env NOTION_API_KEY="$NOTION_API_KEY" -- npx -y @notionhq/notion-mcp-server'

# ---------- 9. Figma ----------
install_mcp "figma" "yes" "FIGMA_API_KEY" "Figma personal access token" \
  bash -c 'claude mcp add figma --env FIGMA_API_KEY="$FIGMA_API_KEY" -- npx -y figma-developer-mcp'

# ---------- 10. Context7 ----------
install_mcp "context7" "no" "" "" \
  claude mcp add context7 -- npx -y @upstash/context7-mcp

# ---------- summary ----------
printf "\n%s=== Final MCP server list ===%s\n" "$BOLD" "$RESET"
claude mcp list || true

printf "\n%s=== Summary ===%s\n" "$BOLD" "$RESET"
if [ ${#INSTALLED[@]} -gt 0 ]; then
  printf "%sInstalled:%s\n" "$GREEN" "$RESET"
  for s in "${INSTALLED[@]}"; do printf "  + %s\n" "$s"; done
fi
if [ ${#SKIPPED[@]} -gt 0 ]; then
  printf "%sSkipped:%s\n" "$YELLOW" "$RESET"
  for s in "${SKIPPED[@]}"; do printf "  - %s\n" "$s"; done
fi
if [ ${#FAILED[@]} -gt 0 ]; then
  printf "%sFailed:%s\n" "$RED" "$RESET"
  for s in "${FAILED[@]}"; do printf "  ! %s\n" "$s"; done
fi

printf "\n%sNext:%s restart Claude Code so new servers are picked up.\n" "$BOLD" "$RESET"
printf "     Run %sclaude mcp list%s anytime to verify status.\n" "$DIM" "$RESET"
printf "     Secrets live in %s%s%s — do not commit.\n" "$DIM" "$SECRETS_FILE" "$RESET"

if [ ${#FAILED[@]} -gt 0 ]; then
  exit 1
fi
exit 0
