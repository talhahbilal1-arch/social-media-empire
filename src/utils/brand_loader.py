"""Brand configuration loader with validation and caching.

This module provides utilities to load brand configurations from YAML files,
validate them against the BrandConfig Pydantic model, and cache results for
performance.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml

from src.models.brand import BrandConfig


# Default config directory (project root / config / brands)
DEFAULT_CONFIG_DIR = Path(__file__).parent.parent.parent / "config" / "brands"


def load_brand(brand_slug: str, config_dir: Optional[Path] = None) -> BrandConfig:
    """Load and validate a brand configuration by slug.

    Args:
        brand_slug: URL-safe brand identifier (e.g., 'menopause-planner')
        config_dir: Optional custom config directory (defaults to config/brands)

    Returns:
        Validated BrandConfig instance

    Raises:
        FileNotFoundError: If brand YAML file doesn't exist
        yaml.YAMLError: If YAML file is malformed
        pydantic.ValidationError: If brand config doesn't match schema

    Example:
        >>> brand = load_brand('menopause-planner')
        >>> print(brand.name)
        Menopause Planner
    """
    if config_dir is None:
        config_dir = DEFAULT_CONFIG_DIR

    yaml_path = config_dir / f"{brand_slug}.yaml"

    if not yaml_path.exists():
        available_brands = list_brands(config_dir)
        raise FileNotFoundError(
            f"Brand '{brand_slug}' not found. "
            f"Available brands: {', '.join(available_brands) or 'none'}"
        )

    # CRITICAL: Use yaml.safe_load() to prevent arbitrary code execution
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Validate against Pydantic model
    return BrandConfig.model_validate(data)


def list_brands(config_dir: Optional[Path] = None) -> list[str]:
    """List all available brand slugs from config directory.

    Args:
        config_dir: Optional custom config directory (defaults to config/brands)

    Returns:
        Sorted list of brand slugs (without .yaml extension)

    Example:
        >>> brands = list_brands()
        >>> print(brands)
        ['daily-deal-darling', 'fitness-made-easy', 'menopause-planner']
    """
    if config_dir is None:
        config_dir = DEFAULT_CONFIG_DIR

    if not config_dir.exists():
        return []

    # Get all .yaml files and extract stems (filenames without extension)
    yaml_files = config_dir.glob("*.yaml")
    brand_slugs = [f.stem for f in yaml_files]

    return sorted(brand_slugs)


class BrandLoader:
    """Brand configuration loader with caching support.

    Provides an object-oriented interface to load brand configurations
    with LRU caching for improved performance when loading the same
    brand multiple times.

    Attributes:
        config_dir: Path to the brand configuration directory

    Example:
        >>> loader = BrandLoader()
        >>> brand = loader.load('menopause-planner')
        >>> all_brands = loader.list_brands()
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize BrandLoader.

        Args:
            config_dir: Optional custom config directory (defaults to config/brands)
        """
        self.config_dir = config_dir or DEFAULT_CONFIG_DIR

    @lru_cache(maxsize=128)
    def load(self, brand_slug: str) -> BrandConfig:
        """Load and cache a brand configuration.

        Cached for performance - subsequent loads of the same brand
        return cached instance.

        Args:
            brand_slug: URL-safe brand identifier

        Returns:
            Validated BrandConfig instance

        Raises:
            FileNotFoundError: If brand YAML file doesn't exist
            yaml.YAMLError: If YAML file is malformed
            pydantic.ValidationError: If brand config doesn't match schema
        """
        return load_brand(brand_slug, self.config_dir)

    def list_brands(self) -> list[str]:
        """List all available brand slugs.

        Returns:
            Sorted list of brand slugs
        """
        return list_brands(self.config_dir)
