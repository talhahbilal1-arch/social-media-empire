"""Thin Tweepy wrapper for OAuth1.0a posting.

Tweepy's ``Client`` (v2 API) is used for tweet creation; ``API`` (v1.1) is
used only for media upload because v2 still routes media through v1.1.

All public methods return ``(tweet_id, tweet_url)`` tuples.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from . import config

logger = logging.getLogger(__name__)


class TwitterClient:
    """Authenticated wrapper around tweepy.Client + tweepy.API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_secret: Optional[str] = None,
        max_retries: int = 3,
    ) -> None:
        self.api_key = config.require(api_key or config.TWITTER_API_KEY, "TWITTER_API_KEY")
        self.api_secret = config.require(
            api_secret or config.TWITTER_API_SECRET, "TWITTER_API_SECRET"
        )
        self.access_token = config.require(
            access_token or config.TWITTER_ACCESS_TOKEN, "TWITTER_ACCESS_TOKEN"
        )
        self.access_secret = config.require(
            access_secret or config.TWITTER_ACCESS_SECRET, "TWITTER_ACCESS_SECRET"
        )
        self.max_retries = max_retries
        self._client = None
        self._api = None

    # ------------------------------------------------------------------
    # Lazy clients (so importing the module works even without tweepy)
    # ------------------------------------------------------------------
    def _get_client(self):  # type: ignore[no-untyped-def]
        if self._client is None:
            import tweepy  # local import — tweepy is an optional runtime dep

            self._client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret,
            )
        return self._client

    def _get_api(self):  # type: ignore[no-untyped-def]
        if self._api is None:
            import tweepy

            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_secret,
            )
            self._api = tweepy.API(auth)
        return self._api

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def post_tweet(
        self, text: str, in_reply_to: Optional[str] = None
    ) -> tuple[str, str]:
        """Post a single tweet. Returns ``(tweet_id, tweet_url)``."""
        text = text.strip()
        if not text:
            raise ValueError("tweet text is empty")
        if len(text) > 280:
            raise ValueError(f"tweet exceeds 280 chars ({len(text)})")

        response = self._with_retry(
            lambda: self._get_client().create_tweet(
                text=text, in_reply_to_tweet_id=in_reply_to
            )
        )
        tweet_id = str(response.data["id"])
        return tweet_id, self._tweet_url(tweet_id)

    def post_thread(self, tweets: list[str]) -> list[tuple[str, str]]:
        """Post a thread; each tweet replies to the previous. Returns list of (id, url)."""
        if not tweets:
            raise ValueError("thread is empty")
        results: list[tuple[str, str]] = []
        reply_to: Optional[str] = None
        for idx, text in enumerate(tweets):
            tid, url = self.post_tweet(text, in_reply_to=reply_to)
            results.append((tid, url))
            reply_to = tid
            # Twitter v2 has tighter rate limits on thread bursts; small pause.
            if idx < len(tweets) - 1:
                time.sleep(1.0)
        return results

    def post_with_media(self, text: str, image_path: str) -> tuple[str, str]:
        """Upload an image then post a tweet referencing it."""
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"image not found: {image_path}")

        media = self._with_retry(lambda: self._get_api().media_upload(filename=str(path)))
        media_id = media.media_id_string

        response = self._with_retry(
            lambda: self._get_client().create_tweet(text=text, media_ids=[media_id])
        )
        tweet_id = str(response.data["id"])
        return tweet_id, self._tweet_url(tweet_id)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _tweet_url(tweet_id: str) -> str:
        return f"https://twitter.com/i/web/status/{tweet_id}"

    def _with_retry(self, func):  # type: ignore[no-untyped-def]
        """Sleep-and-retry on 429 with exponential backoff (max ``max_retries``)."""
        import tweepy

        delay = 5.0
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                return func()
            except tweepy.TooManyRequests as exc:
                last_exc = exc
                logger.warning(
                    "Twitter 429 rate-limited; sleeping %.0fs (attempt %d/%d)",
                    delay,
                    attempt + 1,
                    self.max_retries,
                )
                time.sleep(delay)
                delay *= 2
            except tweepy.TweepyException as exc:
                # Non-rate-limit errors are not retried — surface immediately.
                raise
        assert last_exc is not None
        raise last_exc
