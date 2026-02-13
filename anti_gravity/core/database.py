"""
SQLite database via SQLAlchemy for tracking published content.

Prevents duplicate posts and links Pinterest pins back to their source articles.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from .config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class Post(Base):
    """Published blog post record."""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wp_post_id = Column(Integer, unique=True, nullable=True)
    slug = Column(String(512), unique=True, nullable=False)
    keyword = Column(String(512), nullable=False)
    title = Column(String(1024), nullable=False)
    url = Column(String(2048), nullable=True)
    commission_link = Column(String(2048), nullable=True)
    word_count = Column(Integer, default=0)
    status = Column(String(32), default="draft")
    is_live = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    published_at = Column(DateTime, nullable=True)


class Pin(Base):
    """Pinterest pin record linked to a post."""

    __tablename__ = "pins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pinterest_pin_id = Column(String(128), unique=True, nullable=True)
    post_id = Column(Integer, nullable=False)  # FK to posts.id
    variation = Column(Integer, default=1)  # 1, 2, or 3
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    posted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("post_id", "variation", name="uq_post_variation"),
    )


class Keyword(Base):
    """Discovered keyword record for deduplication."""

    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(512), unique=True, nullable=False)
    niche = Column(String(256), nullable=True)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Database:
    """Database operations for the Anti-Gravity engine."""

    def __init__(self, db_path: Optional[str] = None):
        path = db_path or settings.DATABASE_PATH
        self.engine = create_engine(f"sqlite:///{path}", echo=False)
        Base.metadata.create_all(self.engine)
        self._Session = sessionmaker(bind=self.engine)
        logger.info(f"Database initialized at {path}")

    def _session(self) -> Session:
        return self._Session()

    # --- Posts ---

    def slug_exists(self, slug: str) -> bool:
        """Check if a post with this slug already exists."""
        with self._session() as s:
            return s.query(Post).filter_by(slug=slug).first() is not None

    def keyword_used(self, keyword: str) -> bool:
        """Check if a keyword has already been used for a post."""
        with self._session() as s:
            return s.query(Post).filter_by(keyword=keyword).first() is not None

    def save_post(
        self,
        slug: str,
        keyword: str,
        title: str,
        wp_post_id: Optional[int] = None,
        url: Optional[str] = None,
        commission_link: Optional[str] = None,
        word_count: int = 0,
        status: str = "draft",
        is_live: bool = False,
    ) -> int:
        """Save a post record. Returns the local post ID."""
        with self._session() as s:
            post = Post(
                wp_post_id=wp_post_id,
                slug=slug,
                keyword=keyword,
                title=title,
                url=url,
                commission_link=commission_link,
                word_count=word_count,
                status=status,
                is_live=is_live,
                published_at=datetime.now(timezone.utc) if is_live else None,
            )
            s.add(post)
            s.commit()
            post_id = post.id
            logger.info(f"Saved post #{post_id}: {title}")
            return post_id

    def mark_post_live(self, post_id: int, url: str) -> None:
        """Mark a post as verified live."""
        with self._session() as s:
            post = s.query(Post).get(post_id)
            if post:
                post.is_live = True
                post.url = url
                post.status = "publish"
                post.published_at = datetime.now(timezone.utc)
                s.commit()

    def get_post(self, post_id: int) -> Optional[Post]:
        """Get a post by local ID."""
        with self._session() as s:
            return s.query(Post).get(post_id)

    def get_unpinned_posts(self) -> list:
        """Get live posts that haven't been fully pinned (< 3 pins)."""
        with self._session() as s:
            posts = s.query(Post).filter_by(is_live=True).all()
            result = []
            for p in posts:
                pin_count = s.query(Pin).filter_by(post_id=p.id, posted=True).count()
                if pin_count < 3:
                    result.append({"post": p, "pins_done": pin_count})
            return result

    # --- Pins ---

    def save_pin(
        self,
        post_id: int,
        variation: int,
        title: str,
        description: Optional[str] = None,
        scheduled_at: Optional[datetime] = None,
        pinterest_pin_id: Optional[str] = None,
        posted: bool = False,
    ) -> int:
        """Save a pin record. Returns the local pin ID."""
        with self._session() as s:
            pin = Pin(
                post_id=post_id,
                variation=variation,
                title=title,
                description=description,
                scheduled_at=scheduled_at,
                pinterest_pin_id=pinterest_pin_id,
                posted=posted,
            )
            s.add(pin)
            s.commit()
            return pin.id

    def mark_pin_posted(self, pin_id: int, pinterest_pin_id: str) -> None:
        """Mark a pin as successfully posted."""
        with self._session() as s:
            pin = s.query(Pin).get(pin_id)
            if pin:
                pin.posted = True
                pin.pinterest_pin_id = pinterest_pin_id
                s.commit()

    # --- Keywords ---

    def save_keywords(self, keywords: list[str], niche: str) -> int:
        """Save discovered keywords, skipping duplicates. Returns count saved."""
        saved = 0
        with self._session() as s:
            for kw in keywords:
                exists = s.query(Keyword).filter_by(keyword=kw).first()
                if not exists:
                    s.add(Keyword(keyword=kw, niche=niche))
                    saved += 1
            s.commit()
        logger.info(f"Saved {saved}/{len(keywords)} new keywords")
        return saved

    def get_unused_keywords(self, limit: int = 10) -> list[str]:
        """Get keywords that haven't been used for posts yet."""
        with self._session() as s:
            rows = (
                s.query(Keyword)
                .filter_by(used=False)
                .order_by(Keyword.created_at)
                .limit(limit)
                .all()
            )
            return [r.keyword for r in rows]

    def mark_keyword_used(self, keyword: str) -> None:
        """Mark a keyword as used."""
        with self._session() as s:
            row = s.query(Keyword).filter_by(keyword=keyword).first()
            if row:
                row.used = True
                s.commit()

    # --- Stats ---

    def get_stats(self) -> dict:
        """Get summary statistics."""
        with self._session() as s:
            return {
                "total_posts": s.query(Post).count(),
                "live_posts": s.query(Post).filter_by(is_live=True).count(),
                "total_pins": s.query(Pin).filter_by(posted=True).count(),
                "keywords_discovered": s.query(Keyword).count(),
                "keywords_unused": s.query(Keyword).filter_by(used=False).count(),
            }
