#!/usr/bin/env bash
# Deploy the Anti-Gravity Next.js site to Vercel.
#
# Usage:
#   VERCEL_TOKEN=xxx bash scripts/deploy_anti_gravity.sh
#
# Optional env vars:
#   VERCEL_ORG_ID         — org/team scope (only needed if the token is scoped)
#   VERCEL_PROJECT_ID     — existing Vercel project to redeploy into
#   SKIP_INSTALL_PROMPT=1 — auto-install Vercel CLI if missing (no prompt)
#
# Safe on Linux and macOS. POSIX-ish bash.

set -euo pipefail

# Resolve repo root relative to this script, so it works from any cwd.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SITE_DIR="${REPO_ROOT}/anti_gravity/site"
URL_FILE="${REPO_ROOT}/anti_gravity/DEPLOYED_URL.txt"

red()   { printf '\033[31m%s\033[0m\n' "$*" >&2; }
green() { printf '\033[32m%s\033[0m\n' "$*"; }
bold()  { printf '\033[1m%s\033[0m\n' "$*"; }

# ---- Preconditions ---------------------------------------------------------

if [ -z "${VERCEL_TOKEN:-}" ]; then
  red "ERROR: VERCEL_TOKEN is not set."
  red "Export the Vercel token before running:"
  red "  export VERCEL_TOKEN=xxxxxxxxxxxx"
  red "In CI, use secret VERCEL_BRAND_TOKEN mapped to VERCEL_TOKEN."
  exit 1
fi

if [ ! -d "${SITE_DIR}" ]; then
  red "ERROR: site directory not found: ${SITE_DIR}"
  exit 1
fi

if [ ! -f "${SITE_DIR}/package.json" ]; then
  red "ERROR: ${SITE_DIR}/package.json missing — Next.js site not initialized."
  exit 1
fi

# ---- Vercel CLI ------------------------------------------------------------

if ! command -v vercel >/dev/null 2>&1; then
  if [ "${SKIP_INSTALL_PROMPT:-0}" = "1" ] || [ ! -t 0 ]; then
    bold "Vercel CLI not found. Installing globally (npm i -g vercel)..."
    npm install -g vercel@latest
  else
    bold "Vercel CLI not found."
    printf "Install it globally now via 'npm i -g vercel'? [y/N] "
    read -r reply
    case "${reply}" in
      y|Y|yes|YES)
        npm install -g vercel@latest
        ;;
      *)
        red "Aborted: install Vercel CLI manually then re-run."
        exit 1
        ;;
    esac
  fi
fi

# ---- Deploy ----------------------------------------------------------------

bold "Deploying anti_gravity/site to Vercel (production)..."

DEPLOY_LOG="$(mktemp -t antigravity-deploy.XXXXXX.log)"
trap 'rm -f "${DEPLOY_LOG}"' EXIT

cd "${SITE_DIR}"

# shellcheck disable=SC2086
if ! vercel deploy --prod --yes --token "${VERCEL_TOKEN}" . 2>&1 | tee "${DEPLOY_LOG}"; then
  red "Deploy command failed. See log above."
  exit 1
fi

# Extract the last https://*.vercel.app URL from the log.
DEPLOY_URL="$(grep -Eo 'https://[A-Za-z0-9._-]+\.vercel\.app' "${DEPLOY_LOG}" | tail -n 1 || true)"

if [ -z "${DEPLOY_URL}" ]; then
  red "WARNING: could not parse deploy URL from Vercel output."
  red "Check the Vercel dashboard manually."
  exit 2
fi

printf '%s\n' "${DEPLOY_URL}" > "${URL_FILE}"
green "Deployed: ${DEPLOY_URL}"
green "URL saved to: ${URL_FILE}"

# ---- Post-deploy notes -----------------------------------------------------

cat <<NOTE

=== Next steps (manual) ===
1. Custom domain:  Vercel dashboard -> Project -> Settings -> Domains
                   (point a brand domain at this project)
2. GA4 property:   Update G-XXXXXXXXXX in anti_gravity/site/app/layout.tsx
                   with the Anti-Gravity GA4 measurement ID.
3. Sitemap:        anti_gravity/site/public/sitemap.xml currently points at
                   https://anti-gravity.vercel.app/ — update the <loc> values
                   when the custom domain is live.
4. Submit to Search Console:
                   https://search.google.com/search-console -> add property -> submit sitemap.
NOTE
