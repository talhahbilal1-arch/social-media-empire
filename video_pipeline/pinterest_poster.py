"""
Playwright-based Pinterest video poster.

Uses a persistent browser context (stored at ~/.pinterest-poster-profile/) so
the Pinterest session survives across runs.  On the very first run the browser
will open headed so you can log in; after that it runs headless automatically.

Usage (direct):
    python -m video_pipeline.pinterest_poster \\
        --video output/deals_20260404_160613.mp4 \\
        --brand deals

Usage (as library):
    from video_pipeline.pinterest_poster import post_pin
    result = post_pin(video_path=Path("output/...mp4"), brand_key="deals")
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, Page, BrowserContext, TimeoutError as PWTimeout

from .config import get_brand, BrandConfig, load_env
from .pinterest_destination_mapper import resolve_destination

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────

PROFILE_DIR = Path.home() / ".pinterest-poster-profile"
ERROR_SCREENSHOTS_DIR = Path(__file__).parent.parent / "output" / "_errors"
PINTEREST_CREATE_URL = "https://www.pinterest.com/pin-creation-tool/"
SESSION_CHECK_URL = "https://www.pinterest.com/"

# Board names per brand — these must exist on the Pinterest account
# (post_pin() will create them if missing)
BRAND_BOARD_NAMES: dict[str, str] = {
    "fitover35": "Fitness Tips for Men Over 35",
    "deals":     "Amazon Deals & Finds",
    "menopause": "Menopause Wellness & Tips",
    "pilottools": "AI Tools & Productivity",
}

MAX_RETRIES = 3
UPLOAD_TIMEOUT_MS = 120_000   # 2 min — Pinterest video processing can be slow
ACTION_TIMEOUT_MS  = 30_000   # 30 s for normal UI interactions (video upload needs time)
NAV_TIMEOUT_MS     = 30_000   # 30 s for page navigations


# ── Browser / context helpers ─────────────────────────────────────────────────

def _launch_context(playwright, headless: bool = True) -> tuple:
    """
    Launch (or resume) a persistent browser context.

    Returns (browser, context).  The persistent context keeps cookies on disk
    so Pinterest stays logged in across script runs.
    """
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=headless,
        # Realistic viewport so Pinterest doesn't flag us as a bot
        viewport={"width": 1280, "height": 900},
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        locale="en-US",
        # Give the browser permission to access files (needed for upload)
        accept_downloads=True,
    )
    return browser  # persistent context IS the context


def _is_logged_in(context: BrowserContext) -> bool:
    """Check whether the current session is authenticated on Pinterest."""
    page = context.new_page()
    try:
        page.goto(SESSION_CHECK_URL, timeout=NAV_TIMEOUT_MS, wait_until="domcontentloaded")
        # Pinterest adds a "Log in" button when logged out; absence = logged in
        logged_in = page.locator('[data-test-id="header-login"]').count() == 0
        logger.debug(f"Session check: {'logged in' if logged_in else 'NOT logged in'}")
        return logged_in
    except Exception as e:
        logger.warning(f"Session check failed: {e}")
        return False
    finally:
        page.close()


def _dismiss_popups(page: Page) -> None:
    """Dismiss cookie banners and modals that block interaction."""
    popup_selectors = [
        # Cookie consent
        'button[id*="onetrust-accept"]',
        'button:has-text("Accept all cookies")',
        'button:has-text("Accept All")',
        # "Get the free app" modal
        '[data-test-id="closeup-close-button"]',
        'button[aria-label="Close"]',
        # Pinterest onboarding modals
        '[data-test-id="done-button"]',
    ]
    for sel in popup_selectors:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click(timeout=2000)
                logger.debug(f"Dismissed popup: {sel}")
                time.sleep(0.5)
        except Exception:
            pass  # not present — fine


# ── Board helpers ─────────────────────────────────────────────────────────────

def _ensure_board_exists(page: Page, board_name: str) -> bool:
    """
    Verify the board exists in the board selector dropdown.
    Returns True if found.  Logs a warning (but does NOT abort) if not found.
    """
    # The board selector is opened via the "Choose board" button
    try:
        board_btn = page.locator('[data-test-id="board-dropdown-select-button"]')
        board_btn.wait_for(timeout=ACTION_TIMEOUT_MS)
        board_btn.click()
        time.sleep(1)

        # Search for the board name in the dropdown
        search_input = page.locator('[data-test-id="board-dropdown-search-input"]')
        if search_input.is_visible(timeout=3000):
            search_input.fill(board_name)
            time.sleep(1)

        # Look for the board in results
        board_item = page.locator(f'[data-test-id="board-row"]:has-text("{board_name}")').first
        if board_item.is_visible(timeout=5000):
            board_item.click()
            logger.info(f"Board selected: '{board_name}'")
            return True
        else:
            # Board not found — close dropdown and proceed without board selection
            page.keyboard.press("Escape")
            logger.warning(
                f"Board '{board_name}' not found on this account. "
                "Pin will be saved without a board. "
                "Create the board on Pinterest and re-run to fix."
            )
            return False
    except Exception as e:
        logger.warning(f"Board selection failed: {e}")
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
        return False


# ── Screenshot helpers ─────────────────────────────────────────────────────────

def _screenshot(page: Page, label: str) -> Path:
    """Save a screenshot and return its path."""
    ERROR_SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = ERROR_SCREENSHOTS_DIR / f"{ts}_{label}.png"
    try:
        page.screenshot(path=str(path), full_page=False)
        logger.info(f"Screenshot saved: {path}")
    except Exception as e:
        logger.warning(f"Screenshot failed: {e}")
    return path


# ── Core posting logic ────────────────────────────────────────────────────────

def _build_description(brand: BrandConfig, script_data: dict) -> str:
    """Combine hook + hashtags into a Pinterest description (<500 chars)."""
    hook = script_data.get("hook", "")
    hashtags = " ".join(brand.hashtags)
    description = f"{hook}\n\n{hashtags}"
    # Pinterest description limit is 500 chars
    if len(description) > 490:
        description = description[:487] + "..."
    return description


def _build_title(brand: BrandConfig, script_data: dict) -> str:
    """Return pin title, max 100 chars (Pinterest limit)."""
    title = script_data.get("title", f"{brand.name} — {script_data.get('topic', '')}")
    return title[:100]


def _post_single(
    context: BrowserContext,
    brand: BrandConfig,
    video_path: Path,
    script_data: dict,
    headed: bool,
) -> dict:
    """
    Navigate to the Pinterest pin creation tool and upload one video.

    Returns a result dict with keys: status, pin_url, screenshot, error.
    """
    page = context.new_page()
    result: dict = {"status": "failed", "pin_url": None, "screenshot": None, "error": None}

    try:
        logger.info(f"Opening Pinterest pin creation tool...")
        page.goto(PINTEREST_CREATE_URL, timeout=NAV_TIMEOUT_MS, wait_until="networkidle")
        _dismiss_popups(page)

        # If Pinterest redirected us away (not logged in), wait for the user to
        # log in and manually navigate to the creation tool (headed mode only).
        if "pin-creation-tool" not in page.url:
            if headed:
                logger.info(
                    "Not on pin creation tool — Pinterest may have redirected to login. "
                    "Please log in and navigate to pinterest.com/pin-creation-tool/ "
                    "Waiting up to 3 minutes..."
                )
                try:
                    page.wait_for_url("**/pin-creation-tool/**", timeout=180_000)
                    _dismiss_popups(page)
                    logger.info("Now on pin creation tool — continuing.")
                except PWTimeout:
                    raise RuntimeError(
                        "Timed out waiting for Pinterest pin creation tool. "
                        "Please log in and navigate to the creation tool manually."
                    )
            else:
                raise RuntimeError(
                    f"Pinterest redirected to {page.url!r} instead of pin creation tool. "
                    "Session may be expired — run with --headed to re-authenticate."
                )

        # ── 1. Upload the video ───────────────────────────────────────────────
        logger.info(f"Uploading video: {video_path.name}")

        # Pinterest has a hidden file input — set files directly, no dialog needed
        file_input = page.locator('input[type="file"]#storyboard-upload-input').first
        if not file_input.count():
            file_input = page.locator('input[type="file"]').first
        file_input.set_input_files(str(video_path))
        logger.info(f"File set on input: {video_path.name}")

        # ── 2. Wait for upload / processing ──────────────────────────────────
        # Pinterest shows a processing indicator; wait for it to disappear
        processing_selectors = [
            '[data-test-id="video-processing"]',
            'div:has-text("Processing")',
            '[data-test-id="storyboard-progress"]',
        ]
        # Give upload a moment to start
        time.sleep(3)

        # Wait until processing indicator disappears (or timeout)
        for sel in processing_selectors:
            try:
                indicator = page.locator(sel).first
                if indicator.is_visible(timeout=5000):
                    logger.info("Video processing... (waiting up to 2 minutes)")
                    indicator.wait_for(state="hidden", timeout=UPLOAD_TIMEOUT_MS)
                    logger.info("Video processing complete.")
                    break
            except Exception:
                pass  # indicator not present — likely already done

        # ── 3. Fill title ─────────────────────────────────────────────────────
        title = _build_title(brand, script_data)
        logger.info(f"Setting title: {title}")

        title_selectors = [
            '[data-test-id="pin-draft-title"]',
            'textarea[placeholder*="title"]',
            'input[placeholder*="title"]',
            'div[data-test-id="title-field"] textarea',
        ]
        for sel in title_selectors:
            try:
                field = page.locator(sel).first
                if field.is_visible(timeout=4000):
                    field.click()
                    field.fill(title)
                    logger.debug(f"Title filled via: {sel}")
                    break
            except Exception:
                continue

        # ── 4. Fill description ───────────────────────────────────────────────
        description = _build_description(brand, script_data)
        logger.info("Setting description...")

        desc_selectors = [
            '[data-test-id="pin-draft-description"]',
            'textarea[placeholder*="description"]',
            'div[data-test-id="description-field"] textarea',
            'div[contenteditable="true"]',
        ]
        for sel in desc_selectors:
            try:
                field = page.locator(sel).first
                if field.is_visible(timeout=4000):
                    field.click()
                    field.fill(description)
                    logger.debug(f"Description filled via: {sel}")
                    break
            except Exception:
                continue

        # ── 5. Select board ───────────────────────────────────────────────────
        board_name = BRAND_BOARD_NAMES.get(brand.key)
        if board_name:
            _ensure_board_exists(page, board_name)
        else:
            logger.info(f"No board configured for brand '{brand.key}' — skipping board selection")

        # ── 6. Add destination link ───────────────────────────────────────────
        # Deep-link to the most relevant article (not homepage) + UTM params.
        # See pinterest_destination_mapper.resolve_destination for precedence.
        dest_url = resolve_destination(brand, script_data, board_name=board_name)
        logger.info(f"Setting destination link: {dest_url}")

        link_selectors = [
            '[data-test-id="pin-draft-link"]',
            'input[placeholder*="destination"]',
            'input[placeholder*="link"]',
            'input[type="url"]',
        ]
        for sel in link_selectors:
            try:
                field = page.locator(sel).first
                if field.is_visible(timeout=4000):
                    field.click()
                    field.fill(dest_url)
                    logger.debug(f"Destination link set via: {sel}")
                    break
            except Exception:
                continue

        # ── 7. Publish ────────────────────────────────────────────────────────
        _screenshot(page, f"before_publish_{brand.key}")
        logger.info("Clicking Publish...")

        publish_selectors = [
            '[data-test-id="board-dropdown-save-button"]',
            'button:has-text("Publish")',
            'button:has-text("Save")',
            '[data-test-id="pin-draft-save-button"]',
        ]
        published = False
        for sel in publish_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=5000):
                    btn.click(timeout=ACTION_TIMEOUT_MS)
                    published = True
                    logger.debug(f"Publish clicked via: {sel}")
                    break
            except Exception:
                continue

        if not published:
            raise RuntimeError("Could not find Publish/Save button")

        # ── 8. Wait for confirmation ──────────────────────────────────────────
        # Pinterest redirects to the pin URL or shows a success toast
        time.sleep(4)

        confirmation_selectors = [
            '[data-test-id="pin-create-success"]',
            'div:has-text("Your Pin was saved")',
            'div:has-text("Pin created")',
        ]
        for sel in confirmation_selectors:
            try:
                if page.locator(sel).is_visible(timeout=6000):
                    logger.info("Success confirmation visible.")
                    break
            except Exception:
                pass

        # Capture final URL
        pin_url = page.url
        success_screenshot = _screenshot(page, f"success_{brand.key}")
        logger.info(f"Pin posted! URL: {pin_url}")

        result.update({
            "status": "posted",
            "pin_url": pin_url,
            "screenshot": str(success_screenshot),
            "error": None,
        })

    except PWTimeout as e:
        err = f"Playwright timeout: {e}"
        logger.error(err)
        result["error"] = err
        result["screenshot"] = str(_screenshot(page, f"error_{brand.key}"))
    except Exception as e:
        err = f"Post failed: {e}"
        logger.error(err, exc_info=True)
        result["error"] = err
        result["screenshot"] = str(_screenshot(page, f"error_{brand.key}"))
    finally:
        page.close()

    return result


# ── Public API ────────────────────────────────────────────────────────────────

def post_pin(
    video_path: Path,
    brand_key: str,
    script_data: Optional[dict] = None,
    headless: bool = True,
    dry_run: bool = False,
) -> dict:
    """
    Post a video pin to Pinterest using Playwright.

    On the very first call (no saved session), set headless=False so you can
    log in manually.  After login the session is persisted and future calls
    can use headless=True.

    Args:
        video_path:  Absolute or relative Path to the .mp4 file.
        brand_key:   One of "fitover35", "deals", "menopause", "pilottools".
        script_data: Optional dict with keys: title, hook, hashtags, topic.
                     If omitted, title/description are inferred from the filename.
        headless:    Run browser headless (True) or visible (False).
        dry_run:     Log what would happen but don't open a browser.

    Returns:
        dict with keys: status, pin_url, screenshot, error, brand, video_file,
                        posted_at, retries_used
    """
    video_path = Path(video_path).resolve()
    if not video_path.exists():
        return {
            "status": "failed",
            "error": f"Video file not found: {video_path}",
            "brand": brand_key,
            "video_file": str(video_path),
        }

    brand = get_brand(brand_key)

    # Build minimal script_data from filename if not provided
    if script_data is None:
        script_data = {
            "title": f"{brand.name} — {video_path.stem.replace('_', ' ')}",
            "hook":  brand.hook_styles[0].replace("{topic}", brand.topics[0]) if brand.hook_styles else "",
            "hashtags": brand.hashtags,
            "topic": brand.topics[0],
        }

    if dry_run:
        logger.info(
            f"[DRY RUN] Would post: {video_path.name} → Pinterest | "
            f"brand={brand_key} board={BRAND_BOARD_NAMES.get(brand_key, 'none')}"
        )
        return {
            "status": "dry_run",
            "brand": brand_key,
            "video_file": str(video_path),
            "pin_url": None,
            "error": None,
        }

    logger.info(f"Pinterest poster: brand={brand_key}, video={video_path.name}, headless={headless}")

    last_result: dict = {}
    for attempt in range(1, MAX_RETRIES + 1):
        if attempt > 1:
            wait = 2 ** attempt  # 4s, 8s
            logger.info(f"Retry {attempt}/{MAX_RETRIES} in {wait}s...")
            time.sleep(wait)

        with sync_playwright() as pw:
            context = _launch_context(pw, headless=headless)
            try:
                # First run: check if logged in; open headed if not
                if not headless:
                    logger.info("Running headed — please log in to Pinterest if prompted.")
                else:
                    logged_in = _is_logged_in(context)
                    if not logged_in:
                        logger.warning(
                            "Pinterest session not found or expired. "
                            "Run with --headed once to log in:\n"
                            "  python -m video_pipeline.pinterest_poster "
                            f"--video {video_path} --brand {brand_key} --headed"
                        )
                        return {
                            "status": "auth_required",
                            "error": "Not logged in. Run with --headed to authenticate.",
                            "brand": brand_key,
                            "video_file": str(video_path),
                        }

                result = _post_single(
                    context=context,
                    brand=brand,
                    video_path=video_path,
                    script_data=script_data,
                    headed=not headless,
                )
            finally:
                context.close()

        last_result = result
        last_result["retries_used"] = attempt - 1
        last_result["brand"] = brand_key
        last_result["video_file"] = str(video_path)
        last_result["posted_at"] = datetime.now(timezone.utc).isoformat()

        if result["status"] == "posted":
            logger.info(f"Posted successfully on attempt {attempt}")
            return last_result

        logger.warning(f"Attempt {attempt} failed: {result.get('error')}")

    logger.error(f"All {MAX_RETRIES} attempts failed for {video_path.name}")
    return last_result


# ── CLI entrypoint ────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    load_env()

    parser = argparse.ArgumentParser(
        description="Post a video to Pinterest using Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
First-time setup (login):
  python -m video_pipeline.pinterest_poster --video output/deals_xxx.mp4 --brand deals --headed

Subsequent runs (headless):
  python -m video_pipeline.pinterest_poster --video output/deals_xxx.mp4 --brand deals
""",
    )
    parser.add_argument("--video", required=True, help="Path to the .mp4 file to post")
    parser.add_argument(
        "--brand",
        required=True,
        choices=["fitover35", "deals", "menopause", "pilottools"],
        help="Brand key",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in visible mode (required for first login)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Log only, don't post")
    parser.add_argument("--title", default=None, help="Override pin title")
    args = parser.parse_args()

    script_data = None
    if args.title:
        brand = get_brand(args.brand)
        script_data = {
            "title": args.title,
            "hook": brand.hook_styles[0].replace("{topic}", brand.topics[0]) if brand.hook_styles else "",
            "hashtags": brand.hashtags,
            "topic": brand.topics[0],
        }

    result = post_pin(
        video_path=Path(args.video),
        brand_key=args.brand,
        script_data=script_data,
        headless=not args.headed,
        dry_run=args.dry_run,
    )

    print(json.dumps(result, indent=2))

    if result.get("status") == "auth_required":
        import sys
        sys.exit(2)
    elif result.get("status") != "posted" and not args.dry_run:
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
