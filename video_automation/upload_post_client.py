"""Post video pins to multiple platforms via Upload-Post.com API.

Placeholder — real implementation ships when UPLOAD_POST_API_KEY is provisioned.
Structured so the caller (content-engine Phase 1v) can invoke it today without
breaking: the function returns None when the key is missing and logs a no-op.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

UPLOAD_POST_API_KEY = os.environ.get("UPLOAD_POST_API_KEY", "")
UPLOAD_POST_BASE_URL = "https://api.upload-post.com/api"


def post_to_all_platforms(
    video_url: str,
    cover_url: str,
    title: str,
    description: str,
    link: str,
    platforms: Optional[list] = None,
) -> Optional[dict]:
    """Post a video to Pinterest + TikTok + Instagram Reels + YouTube Shorts.

    Args:
        video_url: Public URL of the MP4 to post (Supabase storage URL)
        cover_url: Public URL of the cover thumbnail JPEG
        title: Pin/post title
        description: Pin/post description (platforms truncate as needed)
        link: Destination URL (where viewers land when they tap the video)
        platforms: Subset to post to; defaults to all four

    Returns:
        Dict of {platform: result_dict} on success, or None when the API key
        is not configured (no-op fallback so callers can invoke unconditionally).
    """
    if not UPLOAD_POST_API_KEY:
        logger.info("UPLOAD_POST_API_KEY not set — skipping multi-platform posting")
        return None

    if platforms is None:
        platforms = ["pinterest", "tiktok", "instagram", "youtube"]

    # TODO: Implement when API key is available.
    # Docs: https://docs.upload-post.com/api/reference/
    logger.info(f"Would post to {platforms}: {title[:50]}")
    return None
