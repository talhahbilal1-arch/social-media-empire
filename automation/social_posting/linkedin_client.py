"""Direct REST client for LinkedIn's UGC Posts API.

We deliberately avoid the (unmaintained) python-linkedin package and use
``requests`` directly. The image-post flow is a 3-step dance:

    1. POST /assets?action=registerUpload  -> get uploadUrl + asset URN
    2. PUT image bytes to uploadUrl
    3. POST /ugcPosts referencing the asset URN
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

import requests

from . import config

logger = logging.getLogger(__name__)

API_BASE = "https://api.linkedin.com"
UGC_ENDPOINT = f"{API_BASE}/v2/ugcPosts"
ASSETS_REGISTER_ENDPOINT = f"{API_BASE}/v2/assets?action=registerUpload"


class LinkedInClient:
    """Minimal LinkedIn UGC posting client."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        person_id: Optional[str] = None,
        max_retries: int = 3,
        timeout: float = 30.0,
    ) -> None:
        self.access_token = config.require(
            access_token or config.LINKEDIN_ACCESS_TOKEN, "LINKEDIN_ACCESS_TOKEN"
        )
        self.person_id = config.require(
            person_id or config.LINKEDIN_PERSON_ID, "LINKEDIN_PERSON_ID"
        )
        self.max_retries = max_retries
        self.timeout = timeout

    # ------------------------------------------------------------------
    @property
    def author_urn(self) -> str:
        """LinkedIn requires ``urn:li:person:<id>`` (or ``organization:<id>``)."""
        if self.person_id.startswith("urn:li:"):
            return self.person_id
        return f"urn:li:person:{self.person_id}"

    def _headers(self, extra: Optional[dict] = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def post(self, text: str) -> tuple[str, str]:
        """Post a text-only update. Returns ``(post_urn, post_url)``."""
        body = {
            "author": self.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        resp = self._with_retry(
            lambda: requests.post(
                UGC_ENDPOINT, headers=self._headers(), json=body, timeout=self.timeout
            )
        )
        post_urn = resp.headers.get("x-restli-id") or resp.json().get("id", "")
        return post_urn, self._post_url(post_urn)

    def post_with_image(self, text: str, image_path: str) -> tuple[str, str]:
        """Upload an image then publish a post that references it."""
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"image not found: {image_path}")

        asset_urn, upload_url = self._register_image_upload()
        self._upload_image_bytes(upload_url, path)

        body = {
            "author": self.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {"text": text[:200]},
                            "media": asset_urn,
                            "title": {"text": path.stem[:200]},
                        }
                    ],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        resp = self._with_retry(
            lambda: requests.post(
                UGC_ENDPOINT, headers=self._headers(), json=body, timeout=self.timeout
            )
        )
        post_urn = resp.headers.get("x-restli-id") or resp.json().get("id", "")
        return post_urn, self._post_url(post_urn)

    # ------------------------------------------------------------------
    # Internal: image upload dance
    # ------------------------------------------------------------------
    def _register_image_upload(self) -> tuple[str, str]:
        """Step 1: ask LinkedIn for an uploadUrl + asset URN."""
        body = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": self.author_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        }
        resp = self._with_retry(
            lambda: requests.post(
                ASSETS_REGISTER_ENDPOINT,
                headers=self._headers(),
                json=body,
                timeout=self.timeout,
            )
        )
        data = resp.json()
        value = data["value"]
        asset_urn = value["asset"]
        upload_url = value["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        return asset_urn, upload_url

    def _upload_image_bytes(self, upload_url: str, path: Path) -> None:
        """Step 2: PUT the raw image bytes to LinkedIn's CDN."""
        with path.open("rb") as fh:
            data = fh.read()
        headers = {"Authorization": f"Bearer {self.access_token}"}
        self._with_retry(
            lambda: requests.put(
                upload_url, headers=headers, data=data, timeout=self.timeout
            )
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _post_url(post_urn: str) -> str:
        # urn:li:share:1234 -> https://www.linkedin.com/feed/update/urn:li:share:1234
        if not post_urn:
            return ""
        return f"https://www.linkedin.com/feed/update/{post_urn}"

    def _with_retry(self, func):  # type: ignore[no-untyped-def]
        """Sleep-and-retry on 429/5xx with exponential backoff."""
        delay = 5.0
        last_exc: Optional[Exception] = None
        last_resp: Optional[requests.Response] = None
        for attempt in range(self.max_retries):
            try:
                resp = func()
            except requests.RequestException as exc:
                last_exc = exc
                logger.warning(
                    "LinkedIn network error %s; retry %d/%d after %.0fs",
                    exc,
                    attempt + 1,
                    self.max_retries,
                    delay,
                )
                time.sleep(delay)
                delay *= 2
                continue

            if resp.status_code == 429 or resp.status_code >= 500:
                last_resp = resp
                retry_after = float(resp.headers.get("Retry-After", delay))
                logger.warning(
                    "LinkedIn %d; sleeping %.0fs (attempt %d/%d)",
                    resp.status_code,
                    retry_after,
                    attempt + 1,
                    self.max_retries,
                )
                time.sleep(retry_after)
                delay *= 2
                continue

            if not resp.ok:
                raise RuntimeError(
                    f"LinkedIn API error {resp.status_code}: {resp.text[:500]}"
                )
            return resp

        if last_resp is not None:
            raise RuntimeError(
                f"LinkedIn API exhausted retries: {last_resp.status_code} {last_resp.text[:500]}"
            )
        assert last_exc is not None
        raise last_exc
