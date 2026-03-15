"""Video pin generator for Pinterest — 9:16 short-form video pins.

CURRENTLY DISABLED — placeholder module for future video pin integration.
Set VIDEO_PIN_ENABLED = True when video rendering infrastructure is ready.

Spec (when enabled):
  - Aspect ratio: 9:16 (1080x1920)
  - Duration: 6-12 seconds
  - Frame structure:
      Frame 1 (0-2s):  PROBLEM — text overlay with the audience's pain point
      Frame 2 (2-4s):  SOLUTION — text overlay with the fix/product/insight
      Frame 3 (4-6s):  CTA — "Save for later" / "Click the link" / brand CTA
  - Text-on-screen captions using brand fonts and colors
  - Background: Pexels stock video or static image with Ken Burns effect
  - Audio: Optional ambient music (no voiceover for MVP)

Integration:
  - Called from content-engine.yml after static pin rendering
  - Uses the same pin_data dict from content_brain.generate_pin_content()
  - Uploads to Supabase storage alongside static images
  - Posts via same Make.com webhook (Pinterest accepts video URLs)

Dependencies (when enabled):
  - moviepy or Pillow + ffmpeg for video composition
  - Brand fonts from assets/fonts/
  - Problem-Solution Matrix from content_brain.BRAND_CONFIGS
"""

import logging

logger = logging.getLogger(__name__)

# Feature flag — set to True when video infrastructure is ready
VIDEO_PIN_ENABLED = False

# Video dimensions (Pinterest 9:16)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
VIDEO_DURATION_SECONDS = 6


def generate_video_pin(brand, pin_data):
    """Generate a 9:16 video pin for Pinterest.

    Args:
        brand: Brand key (e.g. 'fitness', 'deals', 'menopause')
        pin_data: Dict from content_brain.generate_pin_content() containing
                  title, graphic_title, description, tips, visual_style, etc.

    Returns:
        bytes: MP4 video data if VIDEO_PIN_ENABLED, else None.
    """
    if not VIDEO_PIN_ENABLED:
        return None

    # TODO: Implement when video infrastructure is ready
    # 1. Fetch background video/image from Pexels
    # 2. Build 3-frame sequence: Problem → Solution → CTA
    # 3. Overlay brand-styled text on each frame
    # 4. Composite with transitions (fade/slide)
    # 5. Export as MP4 bytes
    logger.info(f"[{brand}] Video pin generation not yet implemented")
    return None


def is_video_pin_enabled():
    """Check if video pin generation is enabled."""
    return VIDEO_PIN_ENABLED
