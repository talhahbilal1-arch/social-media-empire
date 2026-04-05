"""
Render a 1080x1920 vertical MP4 video.
Two backends:
  - FFmpeg: Ken Burns + text overlays (create_video)
  - Remotion: SlideshowVideo React component (create_video_remotion)
"""

import json
import logging
import os
import shutil
import subprocess
import tempfile
import textwrap
import urllib.request
import uuid
from pathlib import Path
from typing import Optional

from .config import BrandConfig, BrandColors, get_api_key

logger = logging.getLogger(__name__)

VIDEO_W = 720
VIDEO_H = 1280
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
            req = urllib.request.Request(url, headers={"Authorization": api_key, "User-Agent": "VideoBot/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())

            photos = data.get("photos", [])
            if not photos:
                logger.warning(f"No Pexels results for query: '{query}'")
                continue

            photo = photos[0]
            img_url = photo["src"].get("large2x") or photo["src"]["original"]
            img_path = output_dir / f"img_{i:02d}.jpg"

            img_req = urllib.request.Request(img_url, headers={"User-Agent": "VideoBot/1.0"})
            with urllib.request.urlopen(img_req, timeout=30) as img_resp:
                with open(img_path, "wb") as f:
                    f.write(img_resp.read())
            downloaded.append(img_path)
            logger.debug(f"Downloaded: {img_path.name} ({query})")

        except Exception as e:
            logger.warning(f"Pexels fetch failed for '{query}': {e}")
            continue

    return downloaded


def _escape_ffmpeg_text(text: str) -> str:
    """Escape special characters for FFmpeg drawtext filter."""
    return (
        text
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace(":", "\\:")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )


def _hex_to_ffmpeg_color(hex_color: str, alpha: float = 1.0) -> str:
    """Convert #RRGGBB to FFmpeg 0xRRGGBBAA format."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    a = int(alpha * 255)
    return f"0x{r:02X}{g:02X}{b:02X}{a:02X}"


def _build_filter_complex(
    images: list[Path],
    voiceover_path: Optional[Path],
    title: str,
    body_points: list[str],
    colors: BrandColors,
    total_duration: float,
) -> tuple[str, list[str]]:
    """
    Build the FFmpeg -filter_complex string and input list.

    Returns:
        (filter_complex_string, extra_ffmpeg_args)
    """
    n = len(images)
    seg_duration = total_duration / n

    primary = _hex_to_ffmpeg_color(colors.primary, 0.85)
    text_color = _hex_to_ffmpeg_color(colors.text)
    accent = _hex_to_ffmpeg_color(colors.accent)

    filters = []
    scaled_labels = []

    # --- Per-image: scale, Ken Burns zoom/pan, fade in/out ---
    for i, img_path in enumerate(images):
        # Scale to slightly larger than frame so zoompan has room to move
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
            f"fade=t=out:st={seg_duration - FADE_DURATION}:d={FADE_DURATION},"
            f"setsar=1"
            f"[v{i}]"
        )
        scaled_labels.append(f"[v{i}]")

    # --- Concatenate all video segments ---
    concat_in = "".join(scaled_labels)
    filters.append(f"{concat_in}concat=n={n}:v=1:a=0[vconcat]")

    # --- Text overlays on the concatenated stream ---
    # Overlay 1: dark gradient bar at bottom for text legibility
    filters.append(
        f"[vconcat]drawbox="
        f"x=0:y={VIDEO_H - 500}:w={VIDEO_W}:h=500:"
        f"color={_hex_to_ffmpeg_color('#000000', 0.55)}:t=fill"
        f"[vbox]"
    )

    # Overlay 2: Title text
    safe_title = _escape_ffmpeg_text(textwrap.shorten(title, width=38, placeholder="..."))
    filters.append(
        f"[vbox]drawtext="
        f"text='{safe_title}':"
        f"fontsize=52:fontcolor={text_color}:"
        f"x=(w-text_w)/2:y={VIDEO_H - 460}:"
        f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        f"[vtitle]"
    )

    # Overlay 3: Body points (up to 3, stacked)
    current_label = "[vtitle]"
    for j, point in enumerate(body_points[:3]):
        safe_point = _escape_ffmpeg_text(
            textwrap.shorten(f"• {point}", width=48, placeholder="...")
        )
        next_label = f"[vpoint{j}]" if j < 2 else "[vfinal]"
        y_pos = VIDEO_H - 350 + (j * 80)
        filters.append(
            f"{current_label}drawtext="
            f"text='{safe_point}':"
            f"fontsize=34:fontcolor={accent}:"
            f"x=60:y={y_pos}:"
            f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            f"{next_label}"
        )
        current_label = next_label

    if current_label != "[vfinal]":
        filters.append(f"{current_label}copy[vfinal]")

    filter_str = ";".join(filters)
    return filter_str, []


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

    filter_complex, _ = _build_filter_complex(
        images=images,
        voiceover_path=voiceover_path,
        title=title,
        body_points=body_points,
        colors=colors,
        total_duration=total_duration,
    )

    # Build FFmpeg command
    cmd = ["ffmpeg", "-y"]

    # Input: one entry per image, looped for its segment duration
    seg_duration = total_duration / len(images)
    for img_path in images:
        cmd += ["-loop", "1", "-t", str(seg_duration), "-i", str(img_path)]

    # Input: audio (if provided)
    has_audio = voiceover_path and voiceover_path.exists()
    if has_audio:
        cmd += ["-i", str(voiceover_path)]

    cmd += ["-filter_complex", filter_complex]

    # Map video output
    cmd += ["-map", "[vfinal]"]

    # Map audio (mix voiceover to final track)
    if has_audio:
        audio_idx = len(images)
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
            timeout=900,
        )
        if result.returncode != 0:
            logger.error(f"FFmpeg stderr:\n{result.stderr[-3000:]}")
            raise RuntimeError(f"FFmpeg failed with return code {result.returncode}")

        logger.info(f"Video rendered: {output_path} ({output_path.stat().st_size / 1_000_000:.1f} MB)")
        return output_path

    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg render timed out after 300 seconds")


# Mapping from Python brand key → (Remotion composition ID, brands.ts config key)
_BRAND_TO_REMOTION: dict[str, tuple[str, str]] = {
    "deals":      ("Slideshow-DailyDealDarling", "daily_deal_darling"),
    "fitover35":  ("Slideshow-FitOver35",         "fitnessmadeasy"),
    "menopause":  ("Slideshow-MenopausePlanner",  "menopause_planner"),
    "pilottools": ("Slideshow-FitOver35",         "fitnessmadeasy"),
}

# Remotion project directory
_REMOTION_DIR = Path(__file__).parent.parent / "remotion-videos"


def create_video_remotion(
    brand: BrandConfig,
    script_data: dict,
    voiceover_path: Optional[Path],
    output_path: Path,
) -> Path:
    """
    Render a 1080x1920 vertical MP4 using Remotion's SlideshowVideo component.

    Steps:
      1. Download Pexels portrait images
      2. Copy images + voiceover into remotion-videos/public/temp_{session}/
      3. Write props JSON to /tmp/remotion_props_{session}.json
      4. Run `npx remotion render {composition} {output} --props=...`
      5. Clean up temp assets

    Args:
        brand: BrandConfig for this video
        script_data: Output from script_generator.generate_script()
        voiceover_path: Path to ElevenLabs MP3 (or None for silent)
        output_path: Destination for the final MP4

    Returns:
        Path to rendered MP4
    """
    from .pexels_fetcher import fetch_portrait_images

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    composition_id, brand_ts_key = _BRAND_TO_REMOTION.get(
        brand.key, ("Slideshow-FitOver35", "fitnessmadeasy")
    )

    session_id = uuid.uuid4().hex[:10]
    public_temp_dir = _REMOTION_DIR / "public" / f"temp_{session_id}"
    props_path = Path(f"/tmp/remotion_props_{session_id}.json")

    try:
        public_temp_dir.mkdir(parents=True, exist_ok=True)

        # 1. Download Pexels images
        logger.info("Downloading Pexels portrait images...")
        with tempfile.TemporaryDirectory(prefix="pexels_") as tmpdir:
            images = fetch_portrait_images(
                queries=script_data.get("pexels_search_queries", [brand.name]),
                count=4,
                output_dir=Path(tmpdir),
            )
            # 2a. Copy images to remotion public/
            public_image_refs = []
            for i, img_path in enumerate(images):
                dest = public_temp_dir / f"img_{i:02d}.jpg"
                shutil.copy2(img_path, dest)
                public_image_refs.append(f"temp_{session_id}/img_{i:02d}.jpg")

        # 2b. Copy voiceover to remotion public/
        public_voiceover_ref = ""
        if voiceover_path and Path(voiceover_path).exists():
            dest_audio = public_temp_dir / "voiceover.mp3"
            shutil.copy2(voiceover_path, dest_audio)
            public_voiceover_ref = f"temp_{session_id}/voiceover.mp3"

        # 3. Build props JSON
        props = {
            "brand": brand_ts_key,
            "hook": script_data.get("hook", ""),
            "title": script_data.get("title", ""),
            "points": script_data.get("body_points", [])[:1],  # Pinterest: max 1 point
            "cta": script_data.get("cta", "Link in bio"),
            "images": public_image_refs,
            "voiceover": public_voiceover_ref,
        }
        props_path.write_text(json.dumps(props, indent=2))
        logger.debug(f"Remotion props: {json.dumps(props, indent=2)}")

        # 4. Run Remotion render
        env = os.environ.copy()
        env["PATH"] = f"/opt/homebrew/bin:/usr/local/bin:{env.get('PATH', '')}"

        cmd = [
            "npx", "remotion", "render",
            composition_id,
            str(output_path.resolve()),
            f"--props={props_path}",
            "--browser-executable=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]

        logger.info(f"Remotion render: {composition_id} → {output_path.name}")
        logger.debug(f"Command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            cwd=str(_REMOTION_DIR),
            capture_output=True,
            text=True,
            timeout=600,
            env=env,
        )

        if result.returncode != 0:
            logger.error(f"Remotion stdout:\n{result.stdout[-2000:]}")
            logger.error(f"Remotion stderr:\n{result.stderr[-2000:]}")
            raise RuntimeError(
                f"Remotion render failed (exit {result.returncode}):\n{result.stderr[-500:]}"
            )

        size_mb = output_path.stat().st_size / 1_000_000
        logger.info(f"Video rendered: {output_path} ({size_mb:.1f} MB)")
        return output_path

    finally:
        # Clean up temp assets regardless of success/failure
        if public_temp_dir.exists():
            shutil.rmtree(public_temp_dir, ignore_errors=True)
        if props_path.exists():
            props_path.unlink(missing_ok=True)


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
