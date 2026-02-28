#!/usr/bin/env python3
"""Video pin renderer: generates one video pin per brand per day.

Flow per brand:
  1. generate_pin_content() → hook/title/points/cta/search_term
  2. Fetch 4 portrait images from Pexels API
  3. (Optional) Generate ElevenLabs voiceover → upload to Supabase Storage
  4. npx remotion render <Composition> out/{brand}.mp4 --props '...'
  5. Upload MP4 to Supabase Storage → get public URL
  6. POST to Make.com webhook with video pin payload
  7. Insert row into pinterest_pins table (status='posted' or 'failed')
"""

import os
import sys
import json
import time
import subprocess
import urllib.parse
import urllib.request
import urllib.error
import logging
import requests
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from video_automation.content_brain import generate_pin_content
from video_automation.pinterest_boards import get_board_id, DEFAULT_BOARDS
from database.supabase_client import get_supabase_client

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

BRANDS = ['fitness', 'deals', 'menopause']

BRAND_MAP = {
    'fitness':   {'composition': 'Slideshow-FitOver35',        'remotion_brand': 'fitnessmadeasy'},
    'deals':     {'composition': 'Slideshow-DailyDealDarling', 'remotion_brand': 'daily_deal_darling'},
    'menopause': {'composition': 'Slideshow-MenopausePlanner', 'remotion_brand': 'menopause_planner'},
}

WEBHOOK_VARS = {
    'fitness': 'MAKE_WEBHOOK_VIDEO_FITNESS',
    'deals': 'MAKE_WEBHOOK_VIDEO_DEALS',
    'menopause': 'MAKE_WEBHOOK_VIDEO_MENOPAUSE',
}

BRAND_NAMES_HYPHEN = {
    'fitness': 'fitness-made-easy',
    'deals': 'daily-deal-darling',
    'menopause': 'menopause-planner',
}

BRAND_SITE_URLS = {
    'fitness': 'https://fitover35.com',
    'deals': 'https://dailydealdarling.com',
    'menopause': 'https://menopause-planner-website.vercel.app',
}

VIDEO_BUCKET = 'pin-videos'
AUDIO_BUCKET = 'pin-audio'

ELEVENLABS_VOICE_ID = '21m00Tcm4TlvDq8ikWAM'
ELEVENLABS_MODEL = 'eleven_monolingual_v1'


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def truncate_to_8_words(text):
    # type: (str) -> str
    """Truncate text to 8 words max for video point display."""
    words = text.split()
    return ' '.join(words[:8]) + ('...' if len(words) > 8 else '')


def fetch_pexels_portraits(query, count=4):
    # type: (str, int) -> List[str]
    """Fetch portrait-oriented images from Pexels API."""
    api_key = os.environ.get('PEXELS_API_KEY', '')
    if not api_key:
        logger.warning('PEXELS_API_KEY not set — returning empty image list')
        return []

    url = 'https://api.pexels.com/v1/search?query={}&per_page={}&orientation=portrait'.format(
        urllib.parse.quote(query), count
    )
    try:
        resp = requests.get(url, headers={'Authorization': api_key}, timeout=15)
        resp.raise_for_status()
        photos = resp.json().get('photos', [])
        return [p['src']['large'] for p in photos]
    except Exception as e:
        logger.error('Pexels fetch failed for "{}": {}'.format(query, e))
        return []


def generate_voiceover(script_text, brand):
    # type: (str, str) -> Optional[str]
    """Generate TTS voiceover via ElevenLabs, upload to Supabase, return public URL.

    Returns None if ELEVENLABS_API_KEY not set (graceful skip).
    """
    elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY', '')
    if not elevenlabs_key:
        logger.info('ELEVENLABS_API_KEY not set — skipping voiceover')
        return None

    url = 'https://api.elevenlabs.io/v1/text-to-speech/{}'.format(ELEVENLABS_VOICE_ID)
    headers = {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': elevenlabs_key,
    }
    data = {
        'text': script_text,
        'model_id': ELEVENLABS_MODEL,
        'voice_settings': {
            'stability': 0.5,
            'similarity_boost': 0.75,
        },
    }

    try:
        resp = requests.post(url, json=data, headers=headers, timeout=60)
        resp.raise_for_status()
        audio_bytes = resp.content
        logger.info('Generated voiceover ({} bytes)'.format(len(audio_bytes)))
    except Exception as e:
        logger.error('ElevenLabs TTS failed: {}'.format(e))
        return None

    # Upload audio to Supabase Storage
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    filename = 'voiceover_{}_{}.mp3'.format(brand, timestamp)
    try:
        audio_url = upload_to_supabase(audio_bytes, filename, AUDIO_BUCKET, 'audio/mpeg')
        logger.info('Voiceover uploaded: {}'.format(audio_url))
        return audio_url
    except Exception as e:
        logger.error('Voiceover upload failed: {}'.format(e))
        return None


def upload_to_supabase(file_bytes, filename, bucket, content_type):
    # type: (bytes, str, str, str) -> str
    """Upload file to Supabase Storage and return public URL."""
    supabase_url = os.environ.get('SUPABASE_URL', '')
    supabase_key = os.environ.get('SUPABASE_KEY', '')
    if not supabase_url or not supabase_key:
        raise ValueError('SUPABASE_URL and SUPABASE_KEY must be set')

    headers = {
        'apikey': supabase_key,
        'Authorization': 'Bearer {}'.format(supabase_key),
    }

    # Ensure bucket exists
    check_headers = dict(headers)
    check_headers['Content-Type'] = 'application/json'
    resp = requests.get(
        '{}/storage/v1/bucket/{}'.format(supabase_url, bucket),
        headers=check_headers, timeout=15,
    )
    if resp.status_code != 200:
        requests.post(
            '{}/storage/v1/bucket'.format(supabase_url),
            headers=check_headers,
            json={'id': bucket, 'name': bucket, 'public': True},
            timeout=15,
        )

    # Upload with upsert
    upload_headers = dict(headers)
    upload_headers['Content-Type'] = content_type
    upload_headers['x-upsert'] = 'true'

    upload_url = '{}/storage/v1/object/{}/{}'.format(supabase_url, bucket, filename)
    resp = requests.post(upload_url, headers=upload_headers, data=file_bytes, timeout=120)

    if resp.status_code in (200, 201):
        public_url = '{}/storage/v1/object/public/{}/{}'.format(supabase_url, bucket, filename)
        return public_url

    raise RuntimeError('Supabase upload failed: {} {}'.format(resp.status_code, resp.text[:300]))


def render_video(composition, brand, props_dict, output_path):
    # type: (str, str, Dict[str, Any], str) -> bool
    """Render video using Remotion CLI."""
    props_json = json.dumps(props_dict)
    cmd = [
        'npx', 'remotion', 'render',
        composition,
        output_path,
        '--props', props_json,
    ]
    logger.info('Rendering {} → {}'.format(composition, output_path))
    logger.info('Props: {}'.format(props_json[:200]))

    try:
        result = subprocess.run(
            cmd,
            cwd=os.path.join(os.path.dirname(__file__), '..', 'remotion-videos'),
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode == 0:
            logger.info('Render complete: {}'.format(output_path))
            return True
        else:
            logger.error('Render failed (exit {}):'.format(result.returncode))
            logger.error('STDOUT: {}'.format(result.stdout[-500:] if result.stdout else ''))
            logger.error('STDERR: {}'.format(result.stderr[-500:] if result.stderr else ''))
            return False
    except subprocess.TimeoutExpired:
        logger.error('Render timed out after 600s')
        return False
    except Exception as e:
        logger.error('Render error: {}'.format(e))
        return False


def post_to_webhook(brand, payload):
    # type: (str, Dict[str, Any]) -> bool
    """POST video pin payload to Make.com webhook."""
    webhook_var = WEBHOOK_VARS.get(brand, '')
    webhook_url = os.environ.get(webhook_var, '')
    if not webhook_url:
        logger.warning('[{}] No webhook URL ({} not set) — skipping post'.format(brand, webhook_var))
        return False

    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        webhook_url,
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_body = resp.read().decode('utf-8', errors='replace')
                logger.info('[{}] Webhook → HTTP {} "{}"'.format(brand, resp.status, resp_body[:60]))
            return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='replace')[:200]
            logger.error('[{}] Attempt {}/3 — HTTP {}: {}'.format(brand, attempt + 1, e.code, err_body))
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
        except Exception as e:
            logger.error('[{}] Attempt {}/3 — {}'.format(brand, attempt + 1, e))
            if attempt < 2:
                time.sleep(5 * (attempt + 1))

    return False


def log_error(db_client, phase, brand, error, severity='medium'):
    # type: (Any, str, str, Any, str) -> None
    """Log error to Supabase errors table."""
    try:
        db_client.table('errors').insert({
            'error_type': 'video_pins',
            'error_message': str(error)[:500],
            'context': json.dumps({'phase': phase, 'brand': brand}),
            'severity': severity,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════

def process_brand(brand, db_client):
    # type: (str, Any) -> bool
    """Generate and post one video pin for a brand. Returns True on success."""
    brand_info = BRAND_MAP[brand]
    composition = brand_info['composition']
    remotion_brand = brand_info['remotion_brand']

    print('\n' + '=' * 60)
    print('  VIDEO PIN: {}'.format(brand.upper()))
    print('=' * 60)

    # ── Step 1: Generate content ──
    print('\n  [1/7] Generating content...')
    try:
        pin_data = generate_pin_content(brand, db_client)
    except Exception as e:
        logger.error('[{}] Content generation failed: {}'.format(brand, e))
        log_error(db_client, 'content', brand, e, 'high')
        return False

    hook = pin_data.get('graphic_title', pin_data.get('title', ''))[:60]
    title_text = pin_data.get('title', '')
    tips = pin_data.get('tips', [])
    points = [truncate_to_8_words(t) for t in tips[:3]]
    cta = 'Read the full guide'
    search_term = pin_data.get('image_search_query', pin_data.get('title', 'lifestyle'))
    description = pin_data.get('description', '')
    board_name = pin_data.get('board', '')
    board_id = get_board_id(brand, board_name)
    destination_url = BRAND_SITE_URLS.get(brand, '')

    print('    Hook: {}'.format(hook))
    print('    Title: {}'.format(title_text[:50]))
    print('    Points: {}'.format(points))
    print('    Board: {} → {}'.format(board_name[:30], board_id))

    # ── Step 2: Fetch portrait images ──
    print('\n  [2/7] Fetching Pexels portraits...')
    image_urls = fetch_pexels_portraits(search_term, count=4)
    if not image_urls:
        logger.warning('[{}] No Pexels images — video will use static fallbacks'.format(brand))
    print('    Got {} images'.format(len(image_urls)))

    # ── Step 3: Generate voiceover (optional) ──
    print('\n  [3/7] Generating voiceover...')
    script = '{}. {}. '.format(hook, title_text)
    script += '. '.join(points[:3])
    script += '. Read the full guide.'
    voiceover_url = generate_voiceover(script, brand)
    if voiceover_url:
        print('    Voiceover: {}'.format(voiceover_url[:70]))
    else:
        print('    Voiceover: skipped')

    # ── Step 4: Render video ──
    print('\n  [4/7] Rendering video...')
    # Ensure output directory exists
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'remotion-videos', 'out')
    os.makedirs(out_dir, exist_ok=True)

    output_filename = '{}.mp4'.format(brand)
    output_path = 'out/{}'.format(output_filename)

    props = {
        'brand': remotion_brand,
        'hook': hook,
        'title': title_text,
        'points': points,
        'cta': cta,
        'images': image_urls,
        'voiceover': voiceover_url or '',
    }

    if not render_video(composition, brand, props, output_path):
        logger.error('[{}] Render failed'.format(brand))
        log_error(db_client, 'render', brand, 'Remotion render failed', 'high')
        return False

    # ── Step 5: Upload MP4 to Supabase ──
    print('\n  [5/7] Uploading video...')
    abs_output = os.path.join(os.path.dirname(__file__), '..', 'remotion-videos', output_path)
    try:
        with open(abs_output, 'rb') as f:
            video_bytes = f.read()
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        video_filename = 'video_{}_{}.mp4'.format(brand, timestamp)
        video_url = upload_to_supabase(video_bytes, video_filename, VIDEO_BUCKET, 'video/mp4')
        logger.info('[{}] Video uploaded: {}'.format(brand, video_url))
    except Exception as e:
        logger.error('[{}] Video upload failed: {}'.format(brand, e))
        log_error(db_client, 'upload', brand, e, 'high')
        return False

    # ── Step 6: POST to Make.com webhook ──
    # Uses first Pexels portrait as the pin image (Pinterest image pin).
    # The rendered video is stored in Supabase for article embedding / future
    # native video pin support (which requires Pinterest media upload flow).
    print('\n  [6/7] Posting to Make.com...')
    cover_image = image_urls[0] if image_urls else ''
    webhook_payload = {
        'brand': BRAND_NAMES_HYPHEN.get(brand, brand),
        'image_url': cover_image,
        'video_url': video_url,
        'title': title_text[:100],
        'description': description[:500],
        'link': destination_url,
        'board_id': board_id,
        'pin_type': 'video',
    }

    posted = post_to_webhook(brand, webhook_payload)

    # ── Step 7: Log to pinterest_pins table ──
    print('\n  [7/7] Logging to database...')
    try:
        db_client.table('pinterest_pins').insert({
            'brand': brand,
            'title': title_text[:200],
            'description': description[:500],
            'image_url': video_url,
            'generated_image_url': video_url,
            'destination_url': destination_url,
            'board_id': board_id,
            'topic': pin_data.get('topic', ''),
            'niche': pin_data.get('category', ''),
            'status': 'posted' if posted else 'failed',
            'pin_type': 'video',
            'posted_at': datetime.now(timezone.utc).isoformat() if posted else None,
        }).execute()
    except Exception as e:
        logger.error('[{}] DB insert failed: {}'.format(brand, e))

    status = 'POSTED' if posted else 'RENDERED (webhook skipped)'
    print('\n  [{}] {} — {}'.format(brand, status, title_text[:50]))
    return posted


def main():
    print('=' * 60)
    print('  VIDEO PIN GENERATOR')
    print('  {}'.format(datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')))
    print('=' * 60)

    db = get_supabase_client()

    # Determine which brands to process
    brands_input = os.environ.get('BRANDS_INPUT', 'all').strip()
    if brands_input and brands_input != 'all':
        brands = [b.strip() for b in brands_input.split(',') if b.strip() in BRANDS]
    else:
        brands = BRANDS

    print('\n  Brands: {}'.format(', '.join(brands)))

    results = {}
    for brand in brands:
        try:
            results[brand] = process_brand(brand, db.client)
        except Exception as e:
            logger.error('[{}] Unexpected error: {}'.format(brand, e))
            import traceback
            traceback.print_exc()
            log_error(db.client, 'pipeline', brand, e, 'high')
            results[brand] = False

    # Summary
    print('\n' + '=' * 60)
    print('  SUMMARY')
    print('=' * 60)
    for brand, success in results.items():
        status = 'OK' if success else 'FAILED'
        print('    {}: {}'.format(brand, status))

    # Update agent_runs
    try:
        all_ok = all(results.values())
        db.client.table('agent_runs').upsert({
            'agent_name': 'video_pin_generator',
            'last_run_at': datetime.now(timezone.utc).isoformat(),
            'status': 'success' if all_ok else 'partial_failure',
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }, on_conflict='agent_name').execute()
    except Exception:
        pass

    failed_count = sum(1 for v in results.values() if not v)
    if failed_count > 0:
        print('\n  {} brand(s) failed'.format(failed_count))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
