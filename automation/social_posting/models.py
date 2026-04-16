"""Pydantic v2 models for the queue schema.

The queue is a directory of JSON files (one per article) — these models are
the contract between :mod:`article_repurposer` (writer) and :mod:`poster`
(reader).
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


Platform = Literal["twitter", "linkedin", "bluesky", "threads"]


class TweetItem(BaseModel):
    """A single tweet inside a thread or a standalone tweet."""

    text: str = Field(..., max_length=280)
    image_path: Optional[str] = None

    @field_validator("text")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("tweet text cannot be empty")
        return v


class TwitterPayload(BaseModel):
    """Twitter content for one queued article."""

    hook_tweet: TweetItem
    thread: list[TweetItem] = Field(default_factory=list)

    @field_validator("thread")
    @classmethod
    def _thread_size(cls, v: list[TweetItem]) -> list[TweetItem]:
        if v and not (5 <= len(v) <= 8):
            raise ValueError("thread must contain 5-8 tweets when present")
        return v


class LinkedInPayload(BaseModel):
    """LinkedIn content for one queued article."""

    text: str
    image_path: Optional[str] = None

    @field_validator("text")
    @classmethod
    def _length(cls, v: str) -> str:
        v = v.strip()
        # LinkedIn ugcPost hard-limit is ~3000 chars; we target 300-600 words.
        if len(v) > 3000:
            raise ValueError("LinkedIn post exceeds 3000 char hard limit")
        if not v:
            raise ValueError("LinkedIn post cannot be empty")
        return v


class QueueItem(BaseModel):
    """One queued article ready to post across platforms."""

    brand: str
    article_slug: str
    article_url: str
    article_title: str
    created_at: datetime
    platforms: list[Platform] = Field(default_factory=lambda: ["twitter", "linkedin"])
    twitter: Optional[TwitterPayload] = None
    linkedin: Optional[LinkedInPayload] = None
    # Future platforms — stubbed out for now.
    bluesky: Optional[dict] = None
    threads: Optional[dict] = None


class PostResult(BaseModel):
    """Result of a single platform post attempt."""

    platform: Platform
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
