"""Video pin generator for Pinterest — 9:16 short-form video pins.

Generates 8-second branded video pins using PIL frame-by-frame rendering
piped to ffmpeg for H.264 encoding. Supports two background modes:
  1. Pexels stock video (preferred — real footage looks professional)
  2. Pexels stock photo with Ken Burns zoom effect (fallback)

Output: 1080x1920 MP4, 8 seconds, H.264, ~5-15MB, silent.

Frame structure:
  0.0-3.0s: Hook text (fade in + slide up)
  3.0-6.0s: Solution text (cross-fade in)
  6.0-8.0s: CTA text + brand watermark

Dependencies: PIL (installed), ffmpeg (pre-installed on GitHub Actions runners).
"""

import hashlib
import io
import logging
import math
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import requests
from PIL import Image, ImageDraw, ImageFont

# Reuse existing brand styles and font infrastructure
from video_automation.video_templates import BRAND_VIDEO_STYLES
from video_automation.pin_image_generator import (
    load_font, hex_to_rgb, _wrap_text, resize_and_crop,
)

logger = logging.getLogger(__name__)

# Feature flag — set to True to enable video pin generation
VIDEO_PIN_ENABLED = True

# Video dimensions (Pinterest 9:16)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 25
VIDEO_DURATION_SECONDS = 8
TOTAL_FRAMES = VIDEO_FPS * VIDEO_DURATION_SECONDS  # 200 frames


# ═══════════════════════════════════════════════════════════════
# EASING FUNCTIONS (for smooth, professional animations)
# ═══════════════════════════════════════════════════════════════

def _ease_out_cubic(t):
    """Ease-out cubic — starts fast, decelerates. Professional feel."""
    return 1 - (1 - t) ** 3


def _ease_in_out_cubic(t):
    """Ease-in-out cubic — smooth start and end."""
    if t < 0.5:
        return 4 * t * t * t
    return 1 - (-2 * t + 2) ** 3 / 2


# ═══════════════════════════════════════════════════════════════
# BACKGROUND: Pexels video or photo with Ken Burns
# ═══════════════════════════════════════════════════════════════

def _fetch_pexels_video(query, api_key):
    """Fetch a portrait stock video from Pexels. Returns video file URL or None."""
    try:
        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": api_key},
            params={"query": query, "orientation": "portrait", "per_page": 5, "size": "medium"},
            timeout=15,
        )
        resp.raise_for_status()
        videos = resp.json().get("videos", [])
        if not videos:
            return None

        # Pick the first video, get best portrait file
        video = videos[0]
        files = video.get("video_files", [])
        best = None
        for f in files:
            h = f.get("height", 0)
            w = f.get("width", 0)
            # Prefer portrait (h > w) files with decent resolution
            if h >= 720 and h > w:
                if best is None or h > best.get("height", 0):
                    best = f
        # Fallback: just get highest resolution file
        if best is None and files:
            best = max(files, key=lambda x: x.get("height", 0))
        return best.get("link") if best else None
    except Exception as e:
        logger.warning(f"Pexels video search failed for '{query}': {e}")
        return None


def _fetch_pexels_photo(query, api_key):
    """Fetch a portrait stock photo from Pexels. Returns image URL or None."""
    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": api_key},
            params={"query": query, "orientation": "portrait", "per_page": 3},
            timeout=15,
        )
        resp.raise_for_status()
        photos = resp.json().get("photos", [])
        if not photos:
            return None
        return photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
    except Exception as e:
        logger.warning(f"Pexels photo search failed for '{query}': {e}")
        return None


def _download_video_frames(video_url, width, height, fps, duration):
    """Download a video and extract frames using ffmpeg. Returns list of PIL Images."""
    frames = []
    try:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_url,
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
            "-r", str(fps),
            "-t", str(duration),
            "-f", "rawvideo",
            "-pix_fmt", "rgb24",
            "-loglevel", "error",
            "pipe:1",
        ]
        proc = subprocess.run(cmd, capture_output=True, timeout=60)
        if proc.returncode != 0:
            logger.warning(f"ffmpeg frame extraction failed: {proc.stderr.decode()[:200]}")
            return []

        raw = proc.stdout
        frame_size = width * height * 3
        num_frames = len(raw) // frame_size
        for i in range(num_frames):
            chunk = raw[i * frame_size : (i + 1) * frame_size]
            img = Image.frombytes("RGB", (width, height), chunk)
            frames.append(img)
    except Exception as e:
        logger.warning(f"Video frame extraction failed: {e}")
    return frames


def _generate_ken_burns_frames(photo_url, width, height, total_frames):
    """Generate Ken Burns (slow zoom-in) frames from a static photo."""
    frames = []
    try:
        resp = requests.get(photo_url, timeout=30)
        resp.raise_for_status()
        # Load at high resolution for smooth zoom
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        # Upscale to ~2x target for zoom headroom
        up_w = width * 2
        up_h = height * 2
        img = resize_and_crop(img, up_w, up_h)

        for i in range(total_frames):
            progress = i / max(total_frames - 1, 1)
            # Zoom from 1.0x to 1.3x (slow, cinematic)
            zoom = 1.0 + 0.3 * progress
            crop_w = int(up_w / zoom)
            crop_h = int(up_h / zoom)
            # Center crop
            x = (up_w - crop_w) // 2
            y = (up_h - crop_h) // 2
            cropped = img.crop((x, y, x + crop_w, y + crop_h))
            resized = cropped.resize((width, height), Image.LANCZOS)
            frames.append(resized)
    except Exception as e:
        logger.warning(f"Ken Burns frame generation failed: {e}")
    return frames


def _generate_solid_background_frames(brand_style, total_frames):
    """Generate solid branded gradient background frames as last resort."""
    bg_hex = brand_style["colors"].get("background", "#1A1A2E")
    primary_hex = brand_style["colors"].get("primary", "#333333")
    bg_rgb = hex_to_rgb(bg_hex)
    primary_rgb = hex_to_rgb(primary_hex)

    frames = []
    base = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), bg_rgb)
    draw = ImageDraw.Draw(base)
    # Subtle gradient from primary at top to background at bottom
    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        r = int(primary_rgb[0] * (1 - ratio) + bg_rgb[0] * ratio)
        g = int(primary_rgb[1] * (1 - ratio) + bg_rgb[1] * ratio)
        b = int(primary_rgb[2] * (1 - ratio) + bg_rgb[2] * ratio)
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(r, g, b))

    for _ in range(total_frames):
        frames.append(base.copy())
    return frames


# ═══════════════════════════════════════════════════════════════
# TEXT OVERLAY RENDERING
# ═══════════════════════════════════════════════════════════════

def _draw_text_shadow(draw, xy, text, font, fill, shadow_color=(0, 0, 0), offset=3):
    """Draw text with shadow for readability."""
    x, y = xy
    for dx in (-offset, 0, offset):
        for dy in (-offset, 0, offset):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, fill=shadow_color, font=font)
    draw.text(xy, text, fill=fill, font=font)


def _apply_dark_gradient(frame):
    """Apply dark gradient overlay on bottom 65% for text readability."""
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    gradient_start = int(VIDEO_HEIGHT * 0.35)
    for y in range(gradient_start, VIDEO_HEIGHT):
        progress = (y - gradient_start) / (VIDEO_HEIGHT - gradient_start)
        alpha = int(200 * progress)
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(0, 0, 0, alpha))
    frame_rgba = frame.convert("RGBA")
    composited = Image.alpha_composite(frame_rgba, overlay)
    return composited.convert("RGB")


def _render_text_on_frame(frame, frame_num, brand_style, hook, solution, cta, watermark):
    """Render animated text overlays on a single frame.

    Timeline:
      0.0-0.4s: Brand accent bar fades in
      0.4-1.4s: Hook text fades in + slides up (ease-out-cubic)
      1.4-3.0s: Hook text holds
      3.0-3.5s: Hook fades out, solution fades in
      3.5-6.0s: Solution text holds
      6.0-6.5s: Solution fades out, CTA fades in
      6.5-8.0s: CTA text + watermark hold
    """
    t = frame_num / VIDEO_FPS  # current time in seconds
    colors = brand_style["colors"]
    fonts = brand_style["fonts"]

    # Create RGBA overlay for text (supports alpha)
    txt_layer = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_layer)

    text_color = hex_to_rgb(colors["text_primary"])
    accent_color = hex_to_rgb(colors.get("accent", "#FFD700"))
    margin = 80
    max_w = VIDEO_WIDTH - margin * 2

    # Load fonts
    hook_font = load_font(fonts["heading"], 78, bold=True)
    solution_font = load_font(fonts["heading"], 68, bold=True)
    cta_font = load_font(fonts.get("cta", fonts["heading"]), 56, bold=True)
    wm_font = load_font(fonts["body"], 30)
    sub_font = load_font(fonts["body"], 36)

    # ── Brand accent bar (top) — fades in 0-0.4s ──
    if t >= 0:
        bar_alpha = min(1.0, t / 0.4)
        bar_color = (*accent_color, int(255 * bar_alpha))
        txt_draw.rectangle([(0, 0), (VIDEO_WIDTH, 8)], fill=bar_color)

    # ── HOOK TEXT (0.4s - 3.0s) ──
    if 0.4 <= t < 3.5:
        if t < 1.4:
            # Fade in + slide up (0.4-1.4s)
            progress = (t - 0.4) / 1.0
            eased = _ease_out_cubic(progress)
            alpha = eased
            y_offset = int(60 * (1 - eased))
        elif t < 3.0:
            # Hold
            alpha = 1.0
            y_offset = 0
        else:
            # Fade out (3.0-3.5s)
            progress = (t - 3.0) / 0.5
            alpha = 1.0 - progress
            y_offset = 0

        alpha_int = int(255 * max(0, min(1, alpha)))
        hook_lines = _wrap_text(hook, hook_font, max_w)
        base_y = int(VIDEO_HEIGHT * 0.50) + y_offset
        line_h = 95

        for line in hook_lines:
            bbox = hook_font.getbbox(line)
            lw = bbox[2] - bbox[0]
            x = (VIDEO_WIDTH - lw) // 2
            # Shadow
            shadow_color = (0, 0, 0, alpha_int)
            for dx in (-3, 0, 3):
                for dy in (-3, 0, 3):
                    if dx == 0 and dy == 0:
                        continue
                    txt_draw.text((x + dx, base_y + dy), line, fill=shadow_color, font=hook_font)
            txt_draw.text((x, base_y), line, fill=(*text_color, alpha_int), font=hook_font)
            base_y += line_h

    # ── SOLUTION TEXT (3.0s - 6.5s) ──
    if 3.0 <= t < 6.5:
        if t < 3.5:
            # Fade in (3.0-3.5s)
            progress = (t - 3.0) / 0.5
            alpha = _ease_out_cubic(progress)
            y_offset = int(40 * (1 - alpha))
        elif t < 6.0:
            # Hold
            alpha = 1.0
            y_offset = 0
        else:
            # Fade out (6.0-6.5s)
            progress = (t - 6.0) / 0.5
            alpha = 1.0 - progress
            y_offset = 0

        alpha_int = int(255 * max(0, min(1, alpha)))
        sol_lines = _wrap_text(solution, solution_font, max_w)
        base_y = int(VIDEO_HEIGHT * 0.52) + y_offset
        line_h = 82

        for line in sol_lines:
            bbox = solution_font.getbbox(line)
            lw = bbox[2] - bbox[0]
            x = (VIDEO_WIDTH - lw) // 2
            shadow_color = (0, 0, 0, alpha_int)
            for dx in (-3, 0, 3):
                for dy in (-3, 0, 3):
                    if dx == 0 and dy == 0:
                        continue
                    txt_draw.text((x + dx, base_y + dy), line, fill=shadow_color, font=solution_font)
            txt_draw.text((x, base_y), line, fill=(*text_color, alpha_int), font=solution_font)
            base_y += line_h

    # ── CTA TEXT (6.0s - 8.0s) ──
    if t >= 6.0:
        if t < 6.5:
            progress = (t - 6.0) / 0.5
            alpha = _ease_out_cubic(progress)
        else:
            alpha = 1.0

        alpha_int = int(255 * max(0, min(1, alpha)))

        # CTA pill button
        cta_text = cta
        bbox = cta_font.getbbox(cta_text)
        cta_w = bbox[2] - bbox[0]
        cta_h = bbox[3] - bbox[1]
        pill_x = (VIDEO_WIDTH - cta_w) // 2 - 32
        pill_y = int(VIDEO_HEIGHT * 0.60)
        pill_color = (*accent_color, int(220 * alpha))
        txt_draw.rounded_rectangle(
            [(pill_x, pill_y), (pill_x + cta_w + 64, pill_y + cta_h + 28)],
            radius=24,
            fill=pill_color,
        )
        txt_draw.text(
            ((VIDEO_WIDTH - cta_w) // 2, pill_y + 14),
            cta_text,
            fill=(0, 0, 0, alpha_int),
            font=cta_font,
        )

        # Watermark below CTA
        wm_bbox = wm_font.getbbox(watermark)
        wm_w = wm_bbox[2] - wm_bbox[0]
        txt_draw.text(
            ((VIDEO_WIDTH - wm_w) // 2, pill_y + cta_h + 56),
            watermark,
            fill=(*accent_color, int(180 * alpha)),
            font=wm_font,
        )

    # Composite text layer onto frame
    frame_rgba = frame.convert("RGBA")
    composited = Image.alpha_composite(frame_rgba, txt_layer)
    return composited.convert("RGB")


# ═══════════════════════════════════════════════════════════════
# FFMPEG ENCODING
# ═══════════════════════════════════════════════════════════════

def _encode_frames_to_mp4(frames):
    """Pipe PIL frames to ffmpeg, return MP4 bytes."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{VIDEO_WIDTH}x{VIDEO_HEIGHT}",
        "-r", str(VIDEO_FPS),
        "-i", "pipe:0",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-loglevel", "error",
        "-f", "mp4",
        "pipe:1",
    ]

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Write all frames to stdin
    for frame in frames:
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()

    mp4_bytes = proc.stdout.read()
    stderr = proc.stderr.read()
    proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg encoding failed: {stderr.decode()[:300]}")

    logger.info(f"Encoded video: {len(mp4_bytes) / 1024:.0f}KB, {len(frames)} frames")
    return mp4_bytes


# ═══════════════════════════════════════════════════════════════
# COVER IMAGE
# ═══════════════════════════════════════════════════════════════

def _generate_cover_image(bg_frame, brand_style, hook, watermark):
    """Generate a cover image (JPEG) showing the hook text — used as Pinterest thumbnail."""
    frame = _apply_dark_gradient(bg_frame.copy())

    colors = brand_style["colors"]
    fonts = brand_style["fonts"]
    text_color = hex_to_rgb(colors["text_primary"])
    accent_color = hex_to_rgb(colors.get("accent", "#FFD700"))

    draw = ImageDraw.Draw(frame)
    # Accent bar
    draw.rectangle([(0, 0), (VIDEO_WIDTH, 8)], fill=accent_color)

    # Hook text (fully visible, centered)
    hook_font = load_font(fonts["heading"], 78, bold=True)
    max_w = VIDEO_WIDTH - 160
    lines = _wrap_text(hook, hook_font, max_w)
    y = int(VIDEO_HEIGHT * 0.50)
    for line in lines:
        bbox = hook_font.getbbox(line)
        lw = bbox[2] - bbox[0]
        x = (VIDEO_WIDTH - lw) // 2
        _draw_text_shadow(draw, (x, y), line, hook_font, text_color)
        y += 95

    # Watermark
    wm_font = load_font(fonts["body"], 30)
    wm_bbox = wm_font.getbbox(watermark)
    wm_w = wm_bbox[2] - wm_bbox[0]
    draw.text(((VIDEO_WIDTH - wm_w) // 2, VIDEO_HEIGHT - 80), watermark, fill=accent_color, font=wm_font)

    buf = io.BytesIO()
    frame.save(buf, "JPEG", quality=85)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════
# MAIN PUBLIC API
# ═══════════════════════════════════════════════════════════════

def generate_video_pin(brand, pin_data):
    """Generate a 9:16 video pin for Pinterest.

    Args:
        brand: Brand key ('fitness', 'deals', 'menopause')
        pin_data: Dict with keys:
            - hook: Frame 1 text (5-8 words, the problem/attention grab)
            - solution: Frame 2 text (6-10 words, the payoff)
            - cta: Frame 3 text (4-6 words, call to action)
            - search_query: Pexels search term for background
            (Optional: title, description for metadata)

    Returns:
        dict with:
            - video_bytes: MP4 bytes
            - cover_bytes: JPEG cover image bytes
            - duration: video duration in seconds
        Or None if VIDEO_PIN_ENABLED is False or generation fails.
    """
    if not VIDEO_PIN_ENABLED:
        return None

    brand_style = BRAND_VIDEO_STYLES.get(brand)
    if not brand_style:
        logger.error(f"Unknown brand '{brand}' for video pin")
        return None

    hook = pin_data.get("hook", "")
    solution = pin_data.get("solution", "")
    cta = pin_data.get("cta", "Save This For Later")
    search_query = pin_data.get("search_query", "lifestyle")
    watermark = brand_style.get("watermark_text", brand.title())

    api_key = os.environ.get("PEXELS_API_KEY", "")
    if not api_key:
        logger.error("PEXELS_API_KEY not set — cannot generate video pin")
        return None

    logger.info(f"[{brand}] Generating video pin: hook='{hook[:40]}...'")

    # ── Step 1: Get background frames ──
    bg_frames = []

    # Try stock video first (looks most professional)
    if api_key:
        video_url = _fetch_pexels_video(search_query, api_key)
        if video_url:
            logger.info(f"[{brand}] Using Pexels video background")
            bg_frames = _download_video_frames(
                video_url, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, VIDEO_DURATION_SECONDS
            )

    # Fallback: stock photo with Ken Burns
    if len(bg_frames) < TOTAL_FRAMES:
        photo_url = _fetch_pexels_photo(search_query, api_key)
        if photo_url:
            logger.info(f"[{brand}] Using Ken Burns photo background")
            bg_frames = _generate_ken_burns_frames(
                photo_url, VIDEO_WIDTH, VIDEO_HEIGHT, TOTAL_FRAMES
            )

    # Last resort: solid branded gradient
    if len(bg_frames) < TOTAL_FRAMES:
        logger.info(f"[{brand}] Using solid gradient background")
        bg_frames = _generate_solid_background_frames(brand_style, TOTAL_FRAMES)

    # Ensure we have exactly TOTAL_FRAMES
    if len(bg_frames) > TOTAL_FRAMES:
        bg_frames = bg_frames[:TOTAL_FRAMES]
    while len(bg_frames) < TOTAL_FRAMES:
        bg_frames.append(bg_frames[-1].copy() if bg_frames else
                         Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), (30, 30, 40)))

    # ── Step 2: Apply dark gradient + text overlays to each frame ──
    composited_frames = []
    for i, bg in enumerate(bg_frames):
        frame = _apply_dark_gradient(bg)
        frame = _render_text_on_frame(frame, i, brand_style, hook, solution, cta, watermark)
        composited_frames.append(frame)

    # ── Step 3: Encode to MP4 ──
    try:
        mp4_bytes = _encode_frames_to_mp4(composited_frames)
    except Exception as e:
        logger.error(f"[{brand}] Video encoding failed: {e}")
        return None

    # ── Step 4: Generate cover image ──
    cover_bytes = _generate_cover_image(bg_frames[0], brand_style, hook, watermark)

    logger.info(f"[{brand}] Video pin generated: {len(mp4_bytes) / 1024:.0f}KB")

    return {
        "video_bytes": mp4_bytes,
        "cover_bytes": cover_bytes,
        "duration": VIDEO_DURATION_SECONDS,
    }


def compute_video_hash(video_bytes):
    """Compute SHA256 hash of video bytes for deduplication."""
    return hashlib.sha256(video_bytes).hexdigest()


def is_video_pin_enabled():
    """Check if video pin generation is enabled."""
    return VIDEO_PIN_ENABLED
