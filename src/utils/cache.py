"""File-based caching utilities.

This module provides a FileCache class for storing and retrieving
JSON-serializable data with deterministic hash keys.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# Cache version prefix for invalidation
CACHE_VERSION = "v1"


class FileCache:
    """File-based JSON cache with hash keys.

    Stores cached data as JSON files in subdirectories under cache/.
    Keys are hashed to prevent filesystem issues with special characters
    and to maintain consistent filename lengths.

    Usage:
        cache = FileCache("scripts")  # -> cache/scripts/
        cache.set("key", {"data": "value"})
        data = cache.get("key")  # Returns dict or None

    The cache version prefix (CACHE_VERSION) is included in the hash
    computation, allowing cache invalidation by changing the version.
    """

    def __init__(
        self,
        subdirectory: str,
        cache_root: Optional[Path] = None,
    ) -> None:
        """Initialize file cache.

        Args:
            subdirectory: Subdirectory name under cache root (e.g., "scripts").
            cache_root: Root cache directory. Defaults to Path("cache").
        """
        self.cache_root = cache_root or Path("cache")
        self.cache_dir = self.cache_root / subdirectory
        self.logger = logging.getLogger(f"cache.{subdirectory}")

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _hash_key(self, content: str) -> str:
        """Generate deterministic hash for cache key.

        Includes cache version prefix to enable cache invalidation
        when version changes.

        Args:
            content: The key content to hash.

        Returns:
            16-character hex hash string.
        """
        versioned = f"{CACHE_VERSION}_{content}"
        return hashlib.sha256(versioned.encode()).hexdigest()[:16]

    def _cache_path(self, key: str) -> Path:
        """Get file path for a cache key.

        Args:
            key: The cache key.

        Returns:
            Path to the JSON cache file.
        """
        hashed = self._hash_key(key)
        return self.cache_dir / f"{hashed}.json"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached data by key.

        Args:
            key: The cache key.

        Returns:
            Cached dictionary data, or None if not found or on error.
        """
        path = self._cache_path(key)

        if not path.exists():
            self.logger.info("Cache MISS: %s", key)
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.logger.debug("Cache HIT: %s", key)
            return data
        except json.JSONDecodeError as e:
            self.logger.warning("Cache parse error for %s: %s", key, e)
            return None
        except OSError as e:
            self.logger.warning("Cache read error for %s: %s", key, e)
            return None

    def set(self, key: str, data: Dict[str, Any]) -> None:
        """Store data in cache.

        Args:
            key: The cache key.
            data: JSON-serializable dictionary to cache.
        """
        path = self._cache_path(key)

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            size = path.stat().st_size
            self.logger.debug("Cache WRITE: %s (%d bytes)", key, size)
        except (TypeError, ValueError) as e:
            self.logger.error("Cache serialization error for %s: %s", key, e)
            raise
        except OSError as e:
            self.logger.error("Cache write error for %s: %s", key, e)
            raise

    def has(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: The cache key.

        Returns:
            True if cache file exists.
        """
        return self._cache_path(key).exists()

    def delete(self, key: str) -> bool:
        """Delete a cached item.

        Args:
            key: The cache key to delete.

        Returns:
            True if file was deleted, False if it didn't exist.
        """
        path = self._cache_path(key)

        if not path.exists():
            return False

        try:
            path.unlink()
            self.logger.debug("Cache DELETE: %s", key)
            return True
        except OSError as e:
            self.logger.warning("Cache delete error for %s: %s", key, e)
            return False

    def clear(self) -> int:
        """Delete all cached items in subdirectory.

        Returns:
            Number of files deleted.
        """
        count = 0

        for path in self.cache_dir.glob("*.json"):
            try:
                path.unlink()
                count += 1
            except OSError as e:
                self.logger.warning("Cache clear error for %s: %s", path.name, e)

        self.logger.info("Cache CLEAR: deleted %d files from %s", count, self.cache_dir)
        return count
