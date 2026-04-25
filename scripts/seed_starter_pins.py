#!/usr/bin/env python3
"""Seed 9 pins (3 per brand × fitness/deals/menopause) in `content_ready` state.

Part of the 2026-04-24 Pinterest H1-empty-queue fix (see DIAGNOSTIC_REPORT.md
and FIX_PLAN.md). Uses live-schema columns — `brand`/`title`/`description`,
NOT the runbook-literal `account`/`pin_title`/`pin_description`, because the
live schema never populates the latter on posted rows.

Exits 0 on full success, 2 on hard stop (per runbook: two failed insert
attempts means stop).
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

SUPABASE_URL = os.environ['SUPABASE_URL'].rstrip('/')
SUPABASE_KEY = os.environ['SUPABASE_KEY']
PEXELS_KEY = os.environ['PEXELS_API_KEY']

SB_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}


def http(method: str, url: str, *, headers: dict[str, str], body: bytes | None = None, timeout: int = 20) -> tuple[int, bytes]:
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


PEXELS_UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'


def pexels_image(query: str) -> str | None:
    """Return large2x (or large) portrait URL for a query. Retry with simpler query on empty.

    NOTE: Pexels sits behind Cloudflare, which 403s the default Python UA (error 1010).
    Must send a browser-like User-Agent.
    """
    for q in (query, ' '.join(query.split()[:3]), ' '.join(query.split()[:2])):
        url = f'https://api.pexels.com/v1/search?{urllib.parse.urlencode({"query": q, "per_page": 1, "orientation": "portrait", "size": "large"})}'
        status, body = http('GET', url, headers={'Authorization': PEXELS_KEY, 'User-Agent': PEXELS_UA})
        if status != 200:
            print(f'  [pexels] query="{q}" → HTTP {status}', file=sys.stderr)
            continue
        data = json.loads(body)
        photos = data.get('photos') or []
        if not photos:
            print(f'  [pexels] query="{q}" → no photos', file=sys.stderr)
            continue
        src = photos[0].get('src') or {}
        return src.get('large2x') or src.get('large')
    return None


PLAN = {
    'fitness': {
        'board_id': '418834902785124651',
        'destination_url': 'https://fitover35.com',
        'topics': [
            ('man lifting weights gym', 'workouts'),
            ('healthy meal prep protein bowl', 'nutrition'),
            ('morning stretching workout mat', 'lifestyle'),
        ],
    },
    'deals': {
        'board_id': '874683627569113370',
        'destination_url': 'https://dailydealdarling.com',
        'topics': [
            ('home organization storage baskets', 'organization'),
            ('cozy neutral bedroom decor', 'home_decor'),
            ('modern kitchen utensils wooden', 'kitchen'),
        ],
    },
    'menopause': {
        'board_id': '1076993767079898628',
        'destination_url': 'https://menopause-planner-website.vercel.app',
        'topics': [
            ('woman meditation peaceful calm', 'mental_health'),
            ('herbal tea cup cozy', 'wellness'),
            ('woman walking outdoors nature', 'symptoms'),
        ],
    },
}

# Runbook §3B-H1 step 4: hardcoded fallback copy (no ANTHROPIC_API_KEY available).
FALLBACK_HASHTAGS = '#pinterest #inspiration #dailyinspo #lifestyle'


def build_row(brand: str, topic: str, niche: str, image_url: str) -> dict[str, Any]:
    title = f"{topic.title()}: Simple Tips"
    desc = f"Ideas and inspiration for {topic}. Save this pin for later."
    return {
        'brand': brand,
        'status': 'content_ready',
        'pin_type': 'image',
        'title': title,
        'description': desc,
        'overlay_headline': title,
        'overlay_subtext': desc[:80],
        'topic': topic,
        'niche': niche,
        'visual_style': 'bold_text_overlay',
        'pexels_search_term': topic,
        'image_url': image_url,
        'board_id': PLAN[brand]['board_id'],
        'destination_url': PLAN[brand]['destination_url'],
        'retry_count': 0,
        'article_generated': False,
        'tips': [
            'Quick change, big impact — start today.',
            'Small habits compound over weeks.',
            'Track one metric, keep it honest.',
            'Consistency over intensity.',
            'Save for when motivation dips.',
        ],
    }


def main() -> int:
    rows: list[dict[str, Any]] = []
    for brand, cfg in PLAN.items():
        for topic, niche in cfg['topics']:
            print(f'[pexels] fetching image for "{topic}"')
            image_url = pexels_image(topic)
            if not image_url:
                print(f'  [pexels] HARD SKIP — no image available for "{topic}"', file=sys.stderr)
                continue
            rows.append(build_row(brand, topic, niche, image_url))

    if not rows:
        print('ABORT: no seed rows built (Pexels produced nothing).', file=sys.stderr)
        return 2

    url = f'{SUPABASE_URL}/rest/v1/pinterest_pins'
    body = json.dumps(rows).encode('utf-8')

    print(f'[supabase] inserting {len(rows)} rows (attempt 1)')
    status, resp_body = http('POST', url, headers=SB_HEADERS, body=body)
    if 200 <= status < 300:
        inserted = json.loads(resp_body)
        save_result(inserted)
        return 0

    # Retry ONCE with minimal columns, per runbook.
    print(f'[supabase] attempt 1 failed: HTTP {status} {resp_body[:400]!r}', file=sys.stderr)
    print('[supabase] retry with minimal-column variant (attempt 2)')
    minimal = [{
        'brand': r['brand'],
        'status': r['status'],
        'pin_type': r['pin_type'],
        'title': r['title'],
        'description': r['description'],
        'image_url': r['image_url'],
        'board_id': r['board_id'],
        'destination_url': r['destination_url'],
        'topic': r['topic'],
        'niche': r['niche'],
        'retry_count': 0,
    } for r in rows]
    status2, resp2 = http('POST', url, headers=SB_HEADERS, body=json.dumps(minimal).encode('utf-8'))
    if 200 <= status2 < 300:
        inserted = json.loads(resp2)
        save_result(inserted, minimal=True)
        return 0

    print(f'[supabase] attempt 2 failed: HTTP {status2} {resp2[:400]!r}', file=sys.stderr)
    # Write SEED_FAILED.md so the orchestrator can see why we stopped.
    with open(os.path.join(REPO, 'SEED_FAILED.md'), 'w') as f:
        f.write(f'# Seed failed twice\n\n'
                f'Attempt 1: HTTP {status}\n```\n{resp_body.decode("utf-8", errors="replace")}\n```\n\n'
                f'Attempt 2 (minimal columns): HTTP {status2}\n```\n{resp2.decode("utf-8", errors="replace")}\n```\n')
    return 2


def save_result(inserted: list[dict[str, Any]], minimal: bool = False) -> None:
    summary = {
        'attempt': 'minimal-columns-retry' if minimal else 'full',
        'inserted_count': len(inserted),
        'ids': [r.get('id') for r in inserted],
        'per_brand': {
            b: sum(1 for r in inserted if r.get('brand') == b)
            for b in ['fitness', 'deals', 'menopause']
        },
        'created_at_iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    with open(os.path.join(REPO, 'seed_result.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f'[ok] inserted {len(inserted)} rows — see seed_result.json')
    print(json.dumps(summary['per_brand'], indent=2))


if __name__ == '__main__':
    sys.exit(main())
