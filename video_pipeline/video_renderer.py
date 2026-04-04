"""
Render a 1080x1920 vertical MP4 video using FFmpeg.
Pipeline: Pexels images → Pillow text overlays → Ken Burns effect → voiceover mix → fade transitions.
Text is burned onto images via Pillow before FFmpeg (avoids drawtext/freetype dependency).
"""

import json
import logging
import os
import subprocess
import tempfile
import textwrap
import urllib.request
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from .config import BrandConfig, BrandColors, get_api_key

logger = logging.getLogger(__name__)

VIDEO_W = 1080
VIDEO_H = 1920
IMAGE_DURATION = 7  # seconds per image before transition
FADE_DURATION = 0.5


def _fetch_pexels_images(
    queries: list[str],
    count: int,
    orientation: str,
    output_dir: Path,
) -> list[Path]:
    """Download up to `count` images from Pexels matching the search queries."""
    api_key = get_api_key("PEXELS_API_KEY")
    downloaded: list[Path] = []

    for i, query in enumerate(queries):
        if len(downloaded) >= count:
            break
        try:
            url = (
                f"https://api.pexels.com/v1/search"
                f"?query={urllib.request.quote(query)}"
                f"&orientation={orientation}&per_page=1&page=1"
            )
            req = urllib.request.Request(url, headers={"Authorization": api_key})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())

            photos = data.get("photos", [])
            if not photos:
                logger.warning(f"No Pexels results for query: '{query}'")
                continue

            photo = photos[0]
            img_url = photo["src"].get("large2x") or photo["src"]["original"]
            img_path = output_dir / f"img_{i:02d}.jpg"

            urllib.request.urlretrieve(img_url, img_path)
            downloaded.append(img_path)
            logger.debug(f"Downloaded: {img_path.name} ({query})")

        except Exception as e:
            logger.warning(f"Pexels fetch failed for '{query}': {e}")
            continue

    return downloaded


def _find_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Return best available TrueType font at the given size.

    Tries common system paths (macOS + Ubuntu/Debian for GitHub Actions),
    then falls back to PIL's built-in bitmap font.
    """
    if bold:
        candidates = [
            # macOS
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf",
            # Ubuntu / Debian
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            # Fallback to regular dejavu
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]

    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue

    logger.warning("No TrueType font found — using PIL built-in default (text will be small)")
    return ImageFont.load_default()


def _color_luminance(hex_color: str) -> float:
    """Return relative luminance of a hex color (0 = black, 1 = white)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def _burn_text_onto_images(
    images: list[Path],
    title: str,
    body_points: list[str],
    colors: BrandColors,
    output_dir: Path,
) -> list[Path]:
    """Burn text overlays onto images using Pillow.

    Each image gets a dark semi-transparent bar at the bottom, then text:
      - Image 0        : large centered title
      - Images 1..n-2  : one body point per image (left-aligned)
      - Image n-1      : CTA "Follow for more! ↓"

    Returns a list of new JPEG paths (text_XX.jpg) in output_dir.
    """
    n = len(images)
    if n == 0:
        return images

    # Body-point text color: use brand primary if bright enough, else white
    point_color: tuple[int, int, int, int] = (255, 255, 255, 255)
    if _color_luminance(colors.primary) > 0.25:
        point_color = _hex_to_rgba(colors.primary)

    # Assign text role to each frame
    assignments: list[tuple[str, str]] = []
    for i in range(n):
        if n == 1:
            assignments.append(("title", title))
        elif i == 0:
            assignments.append(("title", title))
        elif i == n - 1:
            assignments.append(("cta", "Follow for more! \u2193"))
        else:
            point_idx = i - 1
            if point_idx < len(body_points) and body_points[point_idx]:
                assignments.append(("point", f"\u2022 {body_points[point_idx]}"))
            else:
                assignments.append(("skip", ""))

    result_paths: list[Path] = []

    for i, (img_path, (kind, text)) in enumerate(zip(images, assignments)):
        if kind == "skip" or not text:
            result_paths.append(img_path)
            continue

        # Open + resize to exact frame dimensions
        img = Image.open(img_path).convert("RGB")
        img = img.resize((VIDEO_W, VIDEO_H), Image.LANCZOS)

        # --- Dark gradient bar at bottom (semi-transparent black box) ---
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(overlay).rectangle(
            [(0, VIDEO_H - 520), (VIDEO_W, VIDEO_H)],
            fill=(0, 0, 0, 165),
        )
        img_rgba = Image.alpha_composite(img.convert("RGBA"), overlay)
        draw = ImageDraw.Draw(img_rgba)

        # --- Text on top of the dark bar ---
        if kind == "title":
            font = _find_font(58, bold=True)
            wrapped = textwrap.fill(title, width=26)
            bbox = draw.textbbox((0, 0), wrapped, font=font)
            text_w = bbox[2] - bbox[0]
            x = max(40, (VIDEO_W - text_w) // 2)
            y = VIDEO_H - 490
            draw.text((x, y), wrapped, font=font, fill=(255, 255, 255, 255))

        elif kind == "point":
            font = _find_font(40)
            wrapped = textwrap.fill(text, width=34)
            draw.text((60, VIDEO_H - 440), wrapped, font=font, fill=point_color)

        elif kind == "cta":
            font = _find_font(50, bold=True)
            wrapped = textwrap.fill(text, width=28)
            bbox = draw.textbbox((0, 0), wrapped, font=font)
            text_w = bbox[2] - bbox[0]
            x = max(40, (VIDEO_W - text_w) // 2)
            y = VIDEO_H - 460
            draw.text((x, y), wrapped, font=font, fill=(255, 255, 255, 255))

        out_path = output_dir / f"text_{i:02d}.jpg"
        img_rgba.convert("RGB").save(out_path, "JPEG", quality=92)
        result_paths.append(out_path)
        logger.debug(f"Text burned onto frame {i} ({kind})")

    return result_paths


def _build_filter_complex(
    images: list[Path],
    voiceover_path: Optional[Path],
    total_duration: float,
) -> tuple[str, list[str]]:
    """Build FFmpeg filter_complex for Ken Burns zoom/pan + fades + concat.

    Text overlays are handled by Pillow before this step, so no drawtext here.
    """
    n = len(images)
    seg_duration = total_duration / n

    filters = []
    scaled_labels = []

    # Per-image: upscale → Ken Burns zoompan → fade in/out
    for i in range(n):
        filters.append(
            f"[{i}:v]scale={VIDEO_W * 2}:{VIDEO_H * 2}:force_original_aspect_ratio=increase,"
            f"crop={VIDEO_W * 2}:{VIDEO_H * 2},"
            f"zoompan="
            f"z='if(lte(zoom,1.0),1.0,zoom-0.002)':"
            f"x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':"
            f"d={int(seg_duration * 25)}:s={VIDEO_W}x{VIDEO_H}:fps=25,"
            f"setpts=PTS-STARTPTS,"
            f"fade=t=in:st=0:d={FADE_DURATION},"
            f"fade=t=out:st={seg_duration - FADE_DURATION}:d={FADE_DURATION}"
            f"[v{i}]"
        )
        scaled_labels.append(f"[v{i}]")

    # Concatenate all segments
    concat_in = "".join(scaled_labels)
    filters.append(f"{concat_in}concat=n={n}:v=1:a=0[vfinal]")

    return ";".join(filters), []


def render_video(
    images: list[Path],
    voiceover_path: Optional[Path],
    output_path: Path,
    title: str,
    body_points: list[str],
    colors: BrandColors,
    total_duration: float,
) -> Path:
    """
    Render a vertical MP4 from images + voiceover using FFmpeg.

    Args:
        images: List of image file paths (5 expected)
        voiceover_path: Path to MP3 audio (or None for silent)
        output_path: Where to write the final MP4
        title: Video title for overlay
        body_points: Bullet points for overlay
        colors: Brand color palette
        total_duration: Target video length in seconds

    Returns:
        Path to the rendered MP4 file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Burn text overlays onto images with Pillow before handing off to FFmpeg
    img_dir = images[0].parent if images else output_path.parent
    text_images = _burn_text_onto_images(
        images=images,
        title=title,
        body_points=body_points,
        colors=colors,
        output_dir=img_dir,
    )

    filter_complex, _ = _build_filter_complex(
        images=text_images,
        voiceover_path=voiceover_path,
        total_duration=total_duration,
    )

    # Build FFmpeg command
    cmd = ["ffmpeg", "-y"]

    # Input: one entry per image, looped for its segment duration
    seg_duration = total_duration / len(text_images)
    for img_path in text_images:
        cmd += ["-loop", "1", "-t", str(seg_duration), "-i", str(img_path)]

    # Input: audio (if provided)
    has_audio = voiceover_path and voiceover_path.exists()
    if has_audio:
        cmd += ["-i", str(voiceover_path)]

    cmd += ["-filter_complex", filter_complex]

    # Map video output
    cmd += ["-map", "[vfinal]"]

    # Map audio
    if has_audio:
        audio_idx = len(text_images)
        cmd += ["-map", f"{audio_idx}:a"]

    cmd += [
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        str(output_path),
    ]

    logger.info(f"Running FFmpeg render → {output_path.name}")
    logger.debug(f"FFmpeg command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            logger.error(f"FFmpeg stderr:\n{result.stderr[-3000:]}")
            raise RuntimeError(f"FFmpeg failed with return code {result.returncode}")

        logger.info(f"Video rendered: {output_path} ({output_path.stat().st_size / 1_000_000:.1f} MB)")
        return output_path

    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg render timed out after 300 seconds")


def create_video(
    brand: BrandConfig,
    script_data: dict,
    voiceover_path: Optional[Path],
    output_path: Path,
) -> Path:
    """
    Full pipeline: download Pexels images → render video.

    Args:
        brand: BrandConfig for this video
        script_data: Output from script_generator.generate_script()
        voiceover_path: Path to generated MP3 (or None)
        output_path: Destination for the final MP4

    Returns:
        Path to rendered MP4
    """
    with tempfile.TemporaryDirectory(prefix="vidpipeline_") as tmpdir:
        tmp_path = Path(tmpdir)

        # Download images
        logger.info("Downloading Pexels images...")
        images = _fetch_pexels_images(
            queries=script_data.get("pexels_search_queries", [brand.name]),
            count=5,
            orientation=brand.pexels_orientation,
            output_dir=tmp_path,
        )

        if not images:
            raise RuntimeError("No images downloaded from Pexels — check PEXELS_API_KEY and queries")

        total_duration = float(script_data.get("estimated_duration_seconds", 45))
        # Pad a couple seconds so video doesn't cut before audio ends
        total_duration = max(total_duration, len(images) * IMAGE_DURATION * 0.6)

        return render_video(
            images=images,
            voiceover_path=voiceover_path,
            output_path=output_path,
            title=script_data["title"],
            body_points=script_data.get("body_points", []),
            colors=brand.colors,
            total_duration=total_duration,
        )
