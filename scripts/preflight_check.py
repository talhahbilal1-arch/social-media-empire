"""Pre-flight validation script for the content engine.

Checks all required secrets and API connectivity before the expensive
pin generation phase begins. Exits 0 on pass, 1 on failure.

Used as the first step in content-engine.yml with continue-on-error: true
so the pipeline surfaces failures fast rather than after 10+ minutes.
"""

import os
import sys
import requests


def check(label, passed, detail=""):
    icon = "✅" if passed else "❌"
    msg = f"  {icon} {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return passed


def main():
    print("=== Pre-flight check ===")
    failures = []

    # ── Required env vars ────────────────────────────────────────
    print("\n[1] Environment variables")
    required = [
        ("ANTHROPIC_API_KEY", "Claude content generation"),
        ("PEXELS_API_KEY", "Pexels image fetching"),
        ("SUPABASE_URL", "Supabase database"),
        ("SUPABASE_KEY", "Supabase database"),
    ]
    for var, purpose in required:
        val = os.environ.get(var, "")
        ok = bool(val and len(val) > 10)
        if not check(f"{var} ({purpose})", ok, "set" if ok else "MISSING"):
            failures.append(f"Missing {var}")

    # At least one Make.com webhook must be configured
    webhook_vars = ["MAKE_WEBHOOK_FITNESS", "MAKE_WEBHOOK_DEALS", "MAKE_WEBHOOK_MENOPAUSE", "MAKE_WEBHOOK_PINTEREST"]
    any_webhook = any(os.environ.get(v, "") for v in webhook_vars)
    if not check("At least one Make.com webhook", any_webhook,
                 "found" if any_webhook else "ALL MISSING — no pins will be posted"):
        failures.append("No Make.com webhooks configured")

    # ── Supabase table accessibility ─────────────────────────────
    print("\n[2] Supabase connectivity")
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_KEY", "")
    tables_to_check = ["content_history", "errors", "agent_runs", "daily_trending"]

    if supabase_url and supabase_key:
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
        }
        for table in tables_to_check:
            try:
                resp = requests.get(
                    f"{supabase_url}/rest/v1/{table}?select=id&limit=1",
                    headers=headers,
                    timeout=10,
                )
                ok = resp.status_code == 200
                if not ok and resp.status_code == 404:
                    detail = f"HTTP {resp.status_code} — table may not exist (run 001_master_schema.sql)"
                elif not ok:
                    detail = f"HTTP {resp.status_code}"
                else:
                    detail = "accessible"
                if not check(f"supabase:{table}", ok, detail):
                    failures.append(f"Supabase table {table} not accessible")
            except requests.exceptions.RequestException as e:
                check(f"supabase:{table}", False, str(e)[:80])
                failures.append(f"Supabase {table} request error")
    else:
        check("Supabase tables", False, "skipped (credentials missing)")

    # ── Pexels API ───────────────────────────────────────────────
    print("\n[3] Pexels API")
    pexels_key = os.environ.get("PEXELS_API_KEY", "")
    if pexels_key:
        try:
            resp = requests.get(
                "https://api.pexels.com/v1/search?query=fitness&per_page=1",
                headers={"Authorization": pexels_key},
                timeout=10,
            )
            ok = resp.status_code == 200
            if not check("Pexels API", ok, f"HTTP {resp.status_code}"):
                failures.append("Pexels API unreachable or invalid key")
        except requests.exceptions.RequestException as e:
            check("Pexels API", False, str(e)[:80])
            failures.append("Pexels API request error")
    else:
        check("Pexels API", False, "skipped (key missing)")

    # ── Anthropic API (lightweight header check) ─────────────────
    print("\n[4] Anthropic API")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if anthropic_key:
        try:
            resp = requests.get(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": anthropic_key,
                    "anthropic-version": "2023-06-01",
                },
                timeout=10,
            )
            ok = resp.status_code in (200, 404)  # 404 = endpoint may not exist but key is valid
            if not check("Anthropic API", ok, f"HTTP {resp.status_code}"):
                failures.append("Anthropic API unreachable or invalid key")
        except requests.exceptions.RequestException as e:
            check("Anthropic API", False, str(e)[:80])
            failures.append("Anthropic API request error")
    else:
        check("Anthropic API", False, "skipped (key missing)")

    # ── Make.com webhook reachability ────────────────────────────
    print("\n[5] Make.com webhooks")
    webhook_map = {
        "MAKE_WEBHOOK_FITNESS": "fitness",
        "MAKE_WEBHOOK_DEALS": "deals",
        "MAKE_WEBHOOK_MENOPAUSE": "menopause",
        "MAKE_WEBHOOK_PINTEREST": "global-fallback",
    }
    # IMPORTANT: Do NOT make HTTP requests to webhook URLs.
    # Make.com fires the scenario on ANY HTTP method (HEAD, GET, POST, etc.).
    # Calling the URL with an empty body causes Pinterest 400 errors, deactivating
    # the scenario before the actual pin posting step runs.
    any_configured = False
    for env_var, label in webhook_map.items():
        url = os.environ.get(env_var, "")
        ok = bool(url and url.startswith("https://hook.us2.make.com/"))
        if check(f"webhook:{label}", ok, "configured" if ok else "not configured"):
            any_configured = True

    if not any_configured:
        failures.append("No Make.com webhooks configured")

    # ── Summary ──────────────────────────────────────────────────
    print(f"\n=== Pre-flight result: {len(failures)} issue(s) ===")
    if failures:
        for f in failures:
            print(f"  ⚠ {f}")
        print("\nPipeline will continue but may fail. Fix issues for reliable operation.")
        sys.exit(1)
    else:
        print("  All checks passed — pipeline is ready.")
        sys.exit(0)


if __name__ == "__main__":
    main()
