#!/usr/bin/env python3
"""Error Alerts.

Queries the Supabase `errors` table for rows created in the last 2 hours where
`severity` is `high` or `critical`, then posts a formatted summary to a Discord
webhook.

Secrets (via env):
    SUPABASE_URL            Supabase project URL.
    SUPABASE_KEY            Supabase service-role / anon key.
    DISCORD_ALERTS_WEBHOOK  Discord incoming webhook URL (optional — if missing,
                            the script logs locally and exits 0).
    ALERT_WINDOW_HOURS      Optional override for the lookback window (default 2).

The script never fails the workflow — missing secrets, HTTP errors, and empty
result sets all exit 0 with a log line. Loud failures would just wake the
operator for no reason.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta


def _log(msg: str) -> None:
    print(f'[error-alerts] {msg}', flush=True)


def fetch_errors(sb_url: str, sb_key: str, since_iso: str) -> list[dict]:
    """Return rows from the `errors` table that match the alert criteria."""
    # severity=in.(high,critical) — matches high/critical severities
    # created_at=gte.<cutoff> — last 2h window
    # order by created_at desc, cap at 50 to keep Discord message under 2k chars
    params = {
        'select': 'id,error_type,error_message,context,severity,created_at',
        'severity': 'in.(high,critical)',
        'created_at': f'gte.{since_iso}',
        'order': 'created_at.desc',
        'limit': '50',
    }
    query = urllib.parse.urlencode(params, safe=',.()')
    url = f'{sb_url}/rest/v1/errors?{query}'
    headers = {
        'apikey': sb_key,
        'Authorization': f'Bearer {sb_key}',
        'Accept': 'application/json',
    }
    req = urllib.request.Request(url, headers=headers, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        _log(f'Supabase HTTP {e.code}: {e.read().decode("utf-8", errors="replace")[:200]}')
        return []
    except Exception as e:
        _log(f'Supabase query failed: {e}')
        return []


def format_discord_payload(rows: list[dict], window_hours: int) -> dict:
    """Render the errors list as a Discord embed payload."""
    critical = [r for r in rows if (r.get('severity') or '').lower() == 'critical']
    high = [r for r in rows if (r.get('severity') or '').lower() == 'high']

    header = f'**{len(rows)} error(s) in the last {window_hours}h** '
    header += f'(critical: {len(critical)}, high: {len(high)})'

    # Build compact lines, grouped by type.
    by_type: dict[str, int] = {}
    for r in rows:
        etype = r.get('error_type') or 'unknown'
        by_type[etype] = by_type.get(etype, 0) + 1
    grouped = sorted(by_type.items(), key=lambda x: -x[1])
    group_lines = [f'- `{etype}` x {count}' for etype, count in grouped[:10]]

    # Sample latest 5 messages.
    sample_lines = []
    for r in rows[:5]:
        ts = (r.get('created_at') or '')[:19]
        sev = (r.get('severity') or '').upper()
        etype = r.get('error_type') or 'unknown'
        msg = str(r.get('error_message') or '').replace('\n', ' ')[:140]
        sample_lines.append(f'- `{ts}` **[{sev}]** `{etype}` — {msg}')

    description = header + '\n\n'
    if group_lines:
        description += '**By type:**\n' + '\n'.join(group_lines) + '\n\n'
    if sample_lines:
        description += '**Recent:**\n' + '\n'.join(sample_lines)

    # Discord embed description max 4096 chars — truncate for safety.
    description = description[:3800]

    color = 0xE74C3C if critical else 0xF1C40F  # red / yellow
    return {
        'username': 'Error Monitor',
        'embeds': [
            {
                'title': 'Social Media Empire — Error Alert',
                'description': description,
                'color': color,
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }
        ],
    }


def post_discord(webhook_url: str, payload: dict) -> bool:
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        webhook_url,
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as e:
        _log(f'Discord HTTP {e.code}: {e.read().decode("utf-8", errors="replace")[:200]}')
        return False
    except Exception as e:
        _log(f'Discord POST failed: {e}')
        return False


def main() -> int:
    sb_url = os.environ.get('SUPABASE_URL', '').strip()
    sb_key = os.environ.get('SUPABASE_KEY', '').strip()
    webhook = os.environ.get('DISCORD_ALERTS_WEBHOOK', '').strip()
    window_raw = os.environ.get('ALERT_WINDOW_HOURS', '2').strip() or '2'
    try:
        window_hours = max(1, int(window_raw))
    except ValueError:
        window_hours = 2

    if not sb_url or not sb_key:
        _log('Missing SUPABASE_URL / SUPABASE_KEY — skipping (exit 0)')
        return 0

    since = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    since_iso = since.strftime('%Y-%m-%dT%H:%M:%SZ')

    rows = fetch_errors(sb_url, sb_key, since_iso)
    _log(f'Found {len(rows)} high/critical errors since {since_iso}')

    if not rows:
        _log('No alertable errors — nothing to send')
        return 0

    # Always log a summary so operators can inspect Actions logs without Discord.
    for r in rows[:10]:
        _log(
            f'  [{(r.get("severity") or "").upper()}] '
            f'{(r.get("created_at") or "")[:19]} '
            f'{r.get("error_type", "unknown")}: '
            f'{str(r.get("error_message") or "")[:120]}'
        )

    if not webhook:
        _log('DISCORD_ALERTS_WEBHOOK not set — logged only, no Discord post')
        return 0

    payload = format_discord_payload(rows, window_hours)
    ok = post_discord(webhook, payload)
    _log(f'Discord alert {"sent" if ok else "FAILED"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
