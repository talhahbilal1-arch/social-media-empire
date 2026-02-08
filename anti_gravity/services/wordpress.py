"""
WordPress REST API client for publishing and managing posts.

Handles:
- Authentication via Application Passwords
- Post creation with Gutenberg HTML blocks
- Featured image uploads
- SEO metadata injection (RankMath / Yoast compatible)
- Duplicate slug detection
- Post liveness verification
- Exponential backoff on failures
"""

import base64
import logging
import re
import time
from typing import Optional, Literal
from dataclasses import dataclass

import requests
import backoff

from anti_gravity.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PostResult:
    """Result of a WordPress post operation."""
    success: bool
    post_id: Optional[int] = None
    post_url: Optional[str] = None
    slug: Optional[str] = None
    error: Optional[str] = None


class WordPressClient:
    """Full-featured WordPress REST API client."""

    def __init__(
        self,
        site_url: Optional[str] = None,
        username: Optional[str] = None,
        app_password: Optional[str] = None,
        default_status: Optional[str] = None,
    ):
        self.site_url = (site_url or settings.WP_SITE_URL).rstrip("/")
        self.username = username or settings.WP_USERNAME
        self.app_password = app_password or settings.WP_APP_PASSWORD
        self.default_status = default_status or settings.WP_DEFAULT_STATUS
        self.api_base = f"{self.site_url}/wp-json/wp/v2"

        if not all([self.site_url, self.username, self.app_password]):
            raise ValueError("WP_SITE_URL, WP_USERNAME, and WP_APP_PASSWORD are required")

        # Build auth header
        creds = f"{self.username}:{self.app_password}"
        token = base64.b64encode(creds.encode()).decode()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        })

    # ------------------------------------------------------------------
    # Duplicate detection
    # ------------------------------------------------------------------

    def slug_exists(self, slug: str) -> bool:
        """Check if a post with this slug already exists on WordPress."""
        try:
            resp = self.session.get(
                f"{self.api_base}/posts",
                params={"slug": slug, "status": "any"},
                timeout=15,
            )
            if resp.status_code == 200:
                posts = resp.json()
                return len(posts) > 0
        except requests.RequestException as e:
            logger.warning(f"Slug check failed: {e}")
        return False

    # ------------------------------------------------------------------
    # Post creation
    # ------------------------------------------------------------------

    @backoff.on_exception(
        backoff.expo,
        requests.RequestException,
        max_tries=3,
        max_time=90,
    )
    def create_post(
        self,
        title: str,
        content: str,
        slug: Optional[str] = None,
        status: Optional[Literal["draft", "publish"]] = None,
        excerpt: Optional[str] = None,
        categories: Optional[list[int]] = None,
        tags: Optional[list[int]] = None,
        featured_media: Optional[int] = None,
        meta: Optional[dict] = None,
    ) -> PostResult:
        """
        Create a new WordPress post.

        Args:
            title: Post title
            content: Gutenberg HTML content
            slug: URL slug (auto-generated from title if omitted)
            status: 'draft' or 'publish'
            excerpt: SEO excerpt / meta description
            categories: WP category IDs
            tags: WP tag IDs
            featured_media: Media library ID for featured image
            meta: SEO meta fields (RankMath / Yoast compatible)
        """
        # Check for duplicate slug
        effective_slug = slug or self._slugify(title)
        if self.slug_exists(effective_slug):
            msg = f"Post with slug '{effective_slug}' already exists — skipping"
            logger.warning(msg)
            return PostResult(success=False, error=msg, slug=effective_slug)

        payload = {
            "title": title,
            "content": content,
            "status": status or self.default_status,
            "slug": effective_slug,
            "format": "standard",
        }

        if excerpt:
            payload["excerpt"] = excerpt
        if categories:
            payload["categories"] = categories
        if tags:
            payload["tags"] = tags
        if featured_media:
            payload["featured_media"] = featured_media

        # Inject SEO meta (RankMath + Yoast compatible)
        if meta:
            payload["meta"] = meta

        logger.info(f"Creating post: '{title}' (status={payload['status']}, slug={effective_slug})")

        try:
            resp = self.session.post(
                f"{self.api_base}/posts",
                json=payload,
                timeout=30,
            )

            if resp.status_code == 201:
                data = resp.json()
                result = PostResult(
                    success=True,
                    post_id=data.get("id"),
                    post_url=data.get("link"),
                    slug=data.get("slug"),
                )
                logger.info(f"Post created: ID={result.post_id}, URL={result.post_url}")
                return result
            else:
                error = f"WP API {resp.status_code}: {resp.text[:500]}"
                logger.error(error)
                return PostResult(success=False, error=error)

        except requests.RequestException as e:
            error = f"Request failed: {e}"
            logger.error(error)
            return PostResult(success=False, error=error)

    # ------------------------------------------------------------------
    # Featured image upload
    # ------------------------------------------------------------------

    @backoff.on_exception(
        backoff.expo,
        requests.RequestException,
        max_tries=3,
        max_time=60,
    )
    def upload_featured_image(
        self,
        image_path: str,
        filename: Optional[str] = None,
        alt_text: Optional[str] = None,
    ) -> Optional[int]:
        """
        Upload an image to the WP media library.

        Returns the media ID, or None on failure.
        """
        import mimetypes

        fname = filename or image_path.split("/")[-1]
        mime = mimetypes.guess_type(fname)[0] or "image/jpeg"

        headers = {
            "Authorization": self.session.headers["Authorization"],
            "Content-Disposition": f'attachment; filename="{fname}"',
            "Content-Type": mime,
        }

        logger.info(f"Uploading image: {fname}")

        try:
            with open(image_path, "rb") as f:
                resp = requests.post(
                    f"{self.api_base}/media",
                    headers=headers,
                    data=f,
                    timeout=60,
                )

            if resp.status_code == 201:
                data = resp.json()
                media_id = data.get("id")
                logger.info(f"Image uploaded: media ID={media_id}")

                # Set alt text if provided
                if alt_text and media_id:
                    self.session.post(
                        f"{self.api_base}/media/{media_id}",
                        json={"alt_text": alt_text},
                        timeout=15,
                    )

                return media_id
            else:
                logger.error(f"Image upload failed: {resp.status_code} — {resp.text[:300]}")
                return None

        except Exception as e:
            logger.error(f"Image upload error: {e}")
            return None

    # ------------------------------------------------------------------
    # SEO metadata helpers
    # ------------------------------------------------------------------

    def build_seo_meta(
        self,
        meta_description: str,
        focus_keyword: str,
        og_title: Optional[str] = None,
        og_description: Optional[str] = None,
    ) -> dict:
        """
        Build SEO meta dict compatible with RankMath AND Yoast.

        WordPress stores these as post meta fields.
        """
        meta = {}

        # RankMath fields
        meta["rank_math_description"] = meta_description
        meta["rank_math_focus_keyword"] = focus_keyword
        meta["rank_math_robots"] = ["index", "follow"]

        # Yoast fields (if Yoast is installed instead)
        meta["_yoast_wpseo_metadesc"] = meta_description
        meta["_yoast_wpseo_focuskw"] = focus_keyword

        # Open Graph
        if og_title:
            meta["rank_math_og_title"] = og_title
            meta["_yoast_wpseo_opengraph-title"] = og_title
        if og_description:
            meta["rank_math_og_description"] = og_description
            meta["_yoast_wpseo_opengraph-description"] = og_description

        return meta

    # ------------------------------------------------------------------
    # Post verification
    # ------------------------------------------------------------------

    def verify_post_live(self, post_url: str, retries: int = 3) -> bool:
        """
        Verify a published post is actually accessible (HTTP 200).

        Uses exponential backoff since WP caches may take a moment.
        """
        for attempt in range(retries):
            try:
                resp = requests.get(post_url, timeout=15, allow_redirects=True)
                if resp.status_code == 200:
                    logger.info(f"Post verified live: {post_url}")
                    return True
                logger.warning(f"Post check attempt {attempt + 1}: HTTP {resp.status_code}")
            except requests.RequestException as e:
                logger.warning(f"Post check attempt {attempt + 1} failed: {e}")

            if attempt < retries - 1:
                time.sleep(2 ** attempt)

        logger.error(f"Post NOT live after {retries} attempts: {post_url}")
        return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _slugify(self, title: str) -> str:
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")[:200]
