"""Render a video using Remotion's SlideshowVideo component.

Subprocess wrapper around `npx remotion render`. Writes scene images to
remotion-videos/public/assets/images/generated/<brand>/ so Remotion's
staticFile() resolver picks them up, then invokes the CLI with a --props
JSON payload matching the SlideshowVideoProps interface.

Returns a dict with {'video_bytes', 'cover_bytes', 'duration'} on success,
or None on any failure so the caller can fall back to the legacy pipeline.
"""

import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Repo layout: this file lives at <repo>/video_automation/remotion_renderer.py,
# so the Remotion project is at <repo>/remotion-videos/.
REPO_ROOT = Path(__file__).resolve().parent.parent
REMOTION_DIR = REPO_ROOT / "remotion-videos"
PUBLIC_DIR = REMOTION_DIR / "public"

# Content-engine brand key → (Remotion brand key, composition ID).
# These Remotion brand keys are the ones registered in remotion-videos/src/config/brands.ts.
BRAND_MAP = {
    "fitness":   ("fitnessmadeasy",     "Slideshow-FitOver35"),
    "deals":     ("daily_deal_darling", "Slideshow-DailyDealDarling"),
    "menopause": ("menopause_planner",  "Slideshow-MenopausePlanner"),
    "pilottools": ("pilottools_ai",     "Slideshow-PilotTools"),
    "homedecor":  ("home_decor_edit",   "Slideshow-HomeDecor"),
    "beauty":     ("beauty_shelf",      "Slideshow-Beauty"),
}

RENDER_TIMEOUT_SEC = 240  # 15s video + Remotion boot overhead
DEFAULT_CTA = "Save This For Later"


def _find_npx() -> Optional[str]:
    """Locate the npx executable, preferring the one on PATH."""
    return shutil.which("npx")


def _find_system_chrome() -> Optional[str]:
    """Find an installed Chrome/Chromium binary — used when Remotion's bundled
    headless-shell download fails (happens in sandboxed CI and some networks).
    """
    candidates = [
        shutil.which("chromium-browser"),  # Ubuntu runners after apt install
        shutil.which("chromium"),
        shutil.which("google-chrome"),
        shutil.which("chrome"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS dev
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


def _write_scene_images(brand: str, scene_images: list) -> tuple:
    """Write scene JPEGs to public/assets/images/generated/<brand>/.

    Returns (relative_paths, output_dir) — paths are relative to the Remotion
    public/ directory so staticFile() can resolve them.
    """
    out_dir = PUBLIC_DIR / "assets" / "images" / "generated" / brand
    out_dir.mkdir(parents=True, exist_ok=True)

    relative_paths = []
    for i, image_bytes in enumerate(scene_images, start=1):
        path = out_dir / f"scene_{i}.jpg"
        path.write_bytes(image_bytes)
        relative_paths.append(f"assets/images/generated/{brand}/scene_{i}.jpg")

    return relative_paths, out_dir


def _extract_cover_frame(video_path: Path) -> bytes:
    """Extract first-frame JPEG via ffmpeg. Returns empty bytes on failure."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        logger.warning("ffmpeg not on PATH — cover extraction skipped")
        return b""

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
        cover_path = Path(tf.name)
    try:
        subprocess.run(
            [
                ffmpeg, "-y", "-loglevel", "error",
                "-ss", "3",  # Skip intro — grab frame at 3 seconds (first scene visible)
                "-i", str(video_path),
                "-vframes", "1", "-q:v", "2",
                str(cover_path),
            ],
            check=True, timeout=30,
        )
        return cover_path.read_bytes() if cover_path.exists() else b""
    except Exception as e:
        logger.warning(f"cover extraction failed: {e}")
        return b""
    finally:
        cover_path.unlink(missing_ok=True)


def _cleanup(scene_dir: Path, video_path: Optional[Path]) -> None:
    """Remove generated scene images and temp video after render."""
    try:
        if scene_dir.exists():
            shutil.rmtree(scene_dir)
    except Exception as e:
        logger.warning(f"scene dir cleanup failed: {e}")
    try:
        if video_path and video_path.exists():
            video_path.unlink()
    except Exception as e:
        logger.warning(f"video cleanup failed: {e}")


def render_remotion_video(brand: str, video_content: dict, scene_images: list) -> Optional[dict]:
    """Render a 15-second slideshow video via Remotion.

    Args:
        brand: Content-engine brand key ('fitness', 'deals', 'menopause')
        video_content: Dict from generate_video_pin_content() — hook/title/tips/cta
        scene_images: List of 4 JPEG byte arrays (1080x1920) from generate_scene_images

    Returns:
        {'video_bytes': bytes, 'cover_bytes': bytes, 'duration': 15} on success,
        None on any failure so the caller can fall back.
    """
    if brand not in BRAND_MAP:
        logger.error(f"Unknown brand '{brand}' — valid: {list(BRAND_MAP)}")
        return None

    if not REMOTION_DIR.exists():
        logger.error(f"Remotion dir not found: {REMOTION_DIR}")
        return None

    npx = _find_npx()
    if not npx:
        logger.error("npx not on PATH — Remotion render unavailable")
        return None

    remotion_brand, composition_id = BRAND_MAP[brand]
    scene_dir = None
    video_path = None

    try:
        # 1. Write scene JPEGs to the Remotion public/ tree
        relative_paths, scene_dir = _write_scene_images(brand, scene_images)

        # 2. Build props payload — passes through SlideshowVideoProps
        props = {
            "brand": remotion_brand,
            "hook": (video_content.get("hook") or "")[:180],
            "title": (video_content.get("title") or "")[:120],
            "points": [p for p in (video_content.get("tips") or [])[:4] if p],
            "cta": (video_content.get("cta") or DEFAULT_CTA)[:40],
            "images": relative_paths,
            # voiceover omitted — component falls back to brand default or silence
        }
        props_json = json.dumps(props, ensure_ascii=False)

        # 3. Run `npx remotion render` from within remotion-videos/
        with tempfile.NamedTemporaryFile(
            suffix=".mp4", delete=False, dir=str(REMOTION_DIR / "out")
            if (REMOTION_DIR / "out").exists() else None,
        ) as tf:
            video_path = Path(tf.name)

        logger.info(f"[{brand}] Remotion render starting ({composition_id})…")
        start = time.time()
        cmd = [
            npx, "remotion", "render",
            composition_id,
            str(video_path),
            f"--props={props_json}",
            "--concurrency=1",  # GitHub Actions runners have limited RAM
        ]
        # Point Remotion at an existing Chrome binary when available — avoids the
        # runtime download that fails behind some networks and in fresh CI runners.
        chrome = os.environ.get("REMOTION_CHROME_EXECUTABLE") or _find_system_chrome()
        if chrome:
            cmd.append(f"--browser-executable={chrome}")

        result = subprocess.run(
            cmd,
            cwd=str(REMOTION_DIR),
            timeout=RENDER_TIMEOUT_SEC,
            capture_output=True,
            text=True,
        )
        elapsed = time.time() - start

        if result.returncode != 0:
            logger.error(
                f"[{brand}] Remotion render failed (rc={result.returncode}, "
                f"{elapsed:.1f}s): {result.stderr[-600:]}"
            )
            return None

        if not video_path.exists() or video_path.stat().st_size == 0:
            logger.error(f"[{brand}] Remotion produced empty/missing output")
            return None

        video_bytes = video_path.read_bytes()
        cover_bytes = _extract_cover_frame(video_path)

        logger.info(
            f"[{brand}] Remotion rendered {len(video_bytes)/1024:.0f}KB "
            f"video + {len(cover_bytes)/1024:.0f}KB cover in {elapsed:.1f}s"
        )
        return {
            "video_bytes": video_bytes,
            "cover_bytes": cover_bytes,
            "duration": 15,
        }

    except subprocess.TimeoutExpired:
        logger.error(f"[{brand}] Remotion render timed out after {RENDER_TIMEOUT_SEC}s")
        return None
    except Exception as e:
        logger.error(f"[{brand}] Remotion render error: {e}")
        return None
    finally:
        _cleanup(scene_dir, video_path)
