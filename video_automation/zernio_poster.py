"""Post video pins to Pinterest via Zernio (formerly Late.dev) API.

Zernio handles Pinterest's 3-step video upload flow in a single API call.
Supports video pins, image pins, and cross-platform posting.

Docs: https://docs.zernio.com
"""

import os
import json
import logging
import time
from typing import Optional, Dict, Any, List

import requests

logger = logging.getLogger(__name__)

ZERNIO_API_KEY = os.environ.get('ZERNIO_API_KEY', '')
ZERNIO_BASE_URL = 'https://api.zernio.com/api'

# Timeout for video posts (Zernio handles the 3-step Pinterest upload, can take ~60s)
POST_TIMEOUT = 120


def is_zernio_configured() -> bool:
    """Check if Zernio API key is set."""
    return bool(ZERNIO_API_KEY)


def _headers() -> Dict[str, str]:
    return {
        'Authorization': f'Bearer {ZERNIO_API_KEY}',
        'Content-Type': 'application/json',
    }


def get_connected_platforms() -> List[str]:
    """Get list of social platforms connected to this Zernio account."""
    if not ZERNIO_API_KEY:
        return []
    try:
        resp = requests.get(f'{ZERNIO_BASE_URL}/user', headers=_headers(), timeout=15)
        data = resp.json()
        return data.get('activeSocialAccounts', [])
    except Exception as e:
        logger.warning(f'Zernio get_connected_platforms failed: {e}')
        return []


def post_video_pin(
    video_url: str,
    title: str,
    description: str,
    board_id: str,
    link: str,
    profile_key: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Post a video pin to Pinterest via Zernio.

    Args:
        video_url: Public URL of the video file (Supabase Storage URL)
        title: Pin title
        description: Pin description
        board_id: Pinterest board ID to post to
        link: Destination URL (article link)
        profile_key: Zernio profile key (optional, uses default if not set)

    Returns:
        Dict with post result including Pinterest pin URL, or None on failure.
    """
    if not ZERNIO_API_KEY:
        logger.warning('ZERNIO_API_KEY not set — skipping video pin post')
        return None

    payload = {
        'post': description[:500],
        'platforms': ['pinterest'],
        'mediaUrls': [video_url],
        'pinterest': {
            'boardId': board_id,
            'title': title[:100],
            'link': link,
        },
    }

    if profile_key:
        payload['profileKey'] = profile_key

    try:
        logger.info(f'Zernio: posting video pin "{title[:50]}" to board {board_id}')
        resp = requests.post(
            f'{ZERNIO_BASE_URL}/post',
            headers=_headers(),
            json=payload,
            timeout=POST_TIMEOUT,
        )
        data = resp.json()

        if data.get('status') == 'success':
            post_ids = data.get('postIds', [])
            pin_result = next((p for p in post_ids if p.get('platform') == 'pinterest'), None)
            if pin_result:
                pin_url = pin_result.get('postUrl', '')
                pin_id = pin_result.get('id', '')
                logger.info(f'Zernio: VIDEO PIN POSTED ✅ {pin_url}')
                return {
                    'status': 'success',
                    'pin_id': pin_id,
                    'pin_url': pin_url,
                    'zernio_id': data.get('id', ''),
                }
            else:
                logger.warning(f'Zernio: post succeeded but no Pinterest result in response')
                return {'status': 'success', 'zernio_id': data.get('id', '')}
        else:
            error_msg = json.dumps(data)[:200]
            logger.error(f'Zernio: post failed: {error_msg}')
            return None

    except requests.Timeout:
        logger.error(f'Zernio: post timed out after {POST_TIMEOUT}s')
        return None
    except Exception as e:
        logger.error(f'Zernio: post error: {e}')
        return None


def post_image_pin(
    image_url: str,
    title: str,
    description: str,
    board_id: str,
    link: str,
    profile_key: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Post an image pin to Pinterest via Zernio. Same API, just image URL instead of video."""
    if not ZERNIO_API_KEY:
        logger.warning('ZERNIO_API_KEY not set — skipping image pin post')
        return None

    payload = {
        'post': description[:500],
        'platforms': ['pinterest'],
        'mediaUrls': [image_url],
        'pinterest': {
            'boardId': board_id,
            'title': title[:100],
            'link': link,
        },
    }

    if profile_key:
        payload['profileKey'] = profile_key

    try:
        logger.info(f'Zernio: posting image pin "{title[:50]}" to board {board_id}')
        resp = requests.post(
            f'{ZERNIO_BASE_URL}/post',
            headers=_headers(),
            json=payload,
            timeout=60,
        )
        data = resp.json()

        if data.get('status') == 'success':
            post_ids = data.get('postIds', [])
            pin_result = next((p for p in post_ids if p.get('platform') == 'pinterest'), None)
            if pin_result:
                logger.info(f'Zernio: IMAGE PIN POSTED ✅ {pin_result.get("postUrl", "")}')
                return {
                    'status': 'success',
                    'pin_id': pin_result.get('id', ''),
                    'pin_url': pin_result.get('postUrl', ''),
                    'zernio_id': data.get('id', ''),
                }
            return {'status': 'success', 'zernio_id': data.get('id', '')}
        else:
            logger.error(f'Zernio: image post failed: {json.dumps(data)[:200]}')
            return None

    except Exception as e:
        logger.error(f'Zernio: image post error: {e}')
        return None


def post_multi_platform(
    video_url: str,
    title: str,
    description: str,
    board_id: str,
    link: str,
    platforms: Optional[List[str]] = None,
    profile_key: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Post a video to Pinterest + other platforms in a single API call.

    Only posts to platforms that are connected in Zernio.
    """
    if not ZERNIO_API_KEY:
        return None

    if platforms is None:
        platforms = ['pinterest']

    # Filter to only connected platforms
    connected = get_connected_platforms()
    active_platforms = [p for p in platforms if p in connected]

    if not active_platforms:
        logger.warning(f'Zernio: none of {platforms} are connected')
        return None

    payload = {
        'post': description[:500],
        'platforms': active_platforms,
        'mediaUrls': [video_url],
    }

    # Add Pinterest-specific data if posting to Pinterest
    if 'pinterest' in active_platforms:
        payload['pinterest'] = {
            'boardId': board_id,
            'title': title[:100],
            'link': link,
        }

    if profile_key:
        payload['profileKey'] = profile_key

    try:
        logger.info(f'Zernio: posting to {active_platforms}')
        resp = requests.post(
            f'{ZERNIO_BASE_URL}/post',
            headers=_headers(),
            json=payload,
            timeout=POST_TIMEOUT,
        )
        data = resp.json()

        if data.get('status') == 'success':
            logger.info(f'Zernio: multi-platform post succeeded: {data.get("postIds", [])}')
            return data
        else:
            logger.error(f'Zernio: multi-platform post failed: {json.dumps(data)[:200]}')
            return None

    except Exception as e:
        logger.error(f'Zernio: multi-platform error: {e}')
        return None
