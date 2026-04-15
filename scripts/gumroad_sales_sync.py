#!/usr/bin/env python3
"""Gumroad Sales Sync.

Pulls recent sales from the Gumroad /v2/sales API and inserts any rows not
already present in the Supabase `gumroad_sales` table.

Secrets (via env):
    GUMROAD_ACCESS_TOKEN   Gumroad personal access token.
    SUPABASE_URL           Supabase project URL.
    SUPABASE_KEY           Supabase service-role / anon key.
    BACKFILL_DAYS          Optional override for lookback window (default 1).

Idempotent: each sale is upserted by its Gumroad `id`; existing rows are kept.
Missing secrets cause a graceful skip — the script exits 0 with a log line.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta


GUMROAD_SALES_ENDPOINT = 'https://api.gumroad.com/v2/sales'


def _log(msg: str) -> None:
    print(f'[gumroad-sync] {msg}', flush=True)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def fetch_gumroad_sales(token: str, since_date: str) -> list[dict]:
    """Return sales list from Gumroad, paginating until empty."""
    collected: list[dict] = []
    params = {
        'access_token': token,
        'after': since_date,  # YYYY-MM-DD
    }
    url = f'{GUMROAD_SALES_ENDPOINT}?{urllib.parse.urlencode(params)}'
    page = 1
    while url and page < 20:  # safety cap
        req = urllib.request.Request(url, method='GET')
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            _log(f'Gumroad HTTP {e.code}: {e.read().decode("utf-8", errors="replace")[:200]}')
            break
        except Exception as e:
            _log(f'Gumroad request failed: {e}')
            break
        sales = payload.get('sales', []) or []
        collected.extend(sales)
        next_page_url = payload.get('next_page_url')
        if next_page_url:
            # Gumroad next_page_url may be relative — prefix host if so
            if next_page_url.startswith('/'):
                next_page_url = 'https://api.gumroad.com' + next_page_url
            # Ensure access_token is included on follow-up pages
            if 'access_token=' not in next_page_url:
                sep = '&' if '?' in next_page_url else '?'
                next_page_url = f'{next_page_url}{sep}access_token={token}'
            url = next_page_url
            page += 1
        else:
            url = ''
    _log(f'Fetched {len(collected)} sales across {page} page(s)')
    return collected


def existing_ids(sb_url: str, sb_key: str, ids: list[str]) -> set[str]:
    if not ids:
        return set()
    # Chunk to avoid URL length issues
    found: set[str] = set()
    headers = {
        'apikey': sb_key,
        'Authorization': f'Bearer {sb_key}',
    }
    CHUNK = 50
    for i in range(0, len(ids), CHUNK):
        chunk = ids[i:i + CHUNK]
        filter_val = ','.join(f'"{x}"' for x in chunk)
        query = f'{sb_url}/rest/v1/gumroad_sales?select=id&id=in.({filter_val})'
        req = urllib.request.Request(query, headers=headers, method='GET')
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                rows = json.loads(resp.read().decode('utf-8'))
                for r in rows:
                    if r.get('id'):
                        found.add(str(r['id']))
        except Exception as e:
            _log(f'existing_ids query failed (chunk {i}): {e}')
    return found


def insert_sale(sb_url: str, sb_key: str, sale: dict) -> bool:
    row = {
        'id': str(sale.get('id', '')),
        'product_name': str(sale.get('product_name', ''))[:500],
        'amount_cents': int(sale.get('price', 0) or 0),
        'buyer_email': str(sale.get('email', ''))[:320],
        'purchased_at': sale.get('created_at') or sale.get('sale_timestamp') or _iso(datetime.now(timezone.utc)),
        'raw_json': sale,
    }
    body = json.dumps(row).encode('utf-8')
    headers = {
        'apikey': sb_key,
        'Authorization': f'Bearer {sb_key}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=minimal',
    }
    req = urllib.request.Request(
        f'{sb_url}/rest/v1/gumroad_sales',
        data=body,
        headers=headers,
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as e:
        body_text = e.read().decode('utf-8', errors='replace')[:200]
        _log(f'insert failed for {row["id"]}: HTTP {e.code} {body_text}')
        return False
    except Exception as e:
        _log(f'insert failed for {row["id"]}: {e}')
        return False


def main() -> int:
    token = os.environ.get('GUMROAD_ACCESS_TOKEN', '').strip()
    sb_url = os.environ.get('SUPABASE_URL', '').strip()
    sb_key = os.environ.get('SUPABASE_KEY', '').strip()
    backfill_days_raw = os.environ.get('BACKFILL_DAYS', '1').strip() or '1'
    try:
        backfill_days = max(1, int(backfill_days_raw))
    except ValueError:
        backfill_days = 1

    missing = [n for n, v in (
        ('GUMROAD_ACCESS_TOKEN', token),
        ('SUPABASE_URL', sb_url),
        ('SUPABASE_KEY', sb_key),
    ) if not v]
    if missing:
        _log(f'Missing secret(s): {", ".join(missing)} — skipping sync (exit 0)')
        return 0

    since = (datetime.now(timezone.utc) - timedelta(days=backfill_days)).strftime('%Y-%m-%d')
    _log(f'Syncing sales since {since} (backfill={backfill_days}d)')

    sales = fetch_gumroad_sales(token, since)
    if not sales:
        _log('No sales returned — nothing to sync')
        return 0

    ids = [str(s.get('id', '')) for s in sales if s.get('id')]
    already = existing_ids(sb_url, sb_key, ids)
    _log(f'{len(already)}/{len(ids)} already in DB — inserting {len(ids) - len(already)} new')

    inserted = 0
    failed = 0
    for sale in sales:
        sid = str(sale.get('id', ''))
        if not sid or sid in already:
            continue
        if insert_sale(sb_url, sb_key, sale):
            inserted += 1
        else:
            failed += 1

    _log(f'Done — inserted={inserted} failed={failed} skipped={len(already)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
