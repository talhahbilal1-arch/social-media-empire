"""Brand configuration models for multi-brand video generation.

This module defines the Pydantic models for brand configurations, including
color palettes with type-safe validation using pydantic-extra-types.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic_extra_types.color import Color


class ColorPalette(BaseModel):
    """Brand color palette with validated color types.

    Supports hex codes (#RRGGBB), RGB strings (rgb(r,g,b)), and named colors.
    Colors are normalized to lowercase hex format.
    """

    primary: Color = Field(
        ...,
        description="Primary brand color (used for backgrounds, main elements)"
    )
    secondary: Color = Field(
        ...,
        description="Secondary brand color (used for text, accents)"
    )
    accent: Optional[Color] = Field(
        default=None,
        description="Optional accent color for highlights or CTAs"
    )

    model_config = ConfigDict(extra="ignore")


class BrandConfig(BaseModel):
    """Complete brand configuration for video generation.

    Defines all brand-specific settings including visual identity,
    text-to-speech voice, and call-to-action elements.
    """

    name: str = Field(
        ...,
        description="Brand display name (e.g., 'Menopause Planner')"
    )
    slug: str = Field(
        ...,
        description="URL-safe brand identifier (e.g., 'menopause-planner')"
    )
    colors: ColorPalette = Field(
        ...,
        description="Brand color palette with validated color types"
    )
    tts_voice: str = Field(
        ...,
        description="Edge-TTS voice ID (e.g., 'en-US-JennyNeural')"
    )
    cta_text: str = Field(
        ...,
        description="Call-to-action button text (e.g., 'Get Your Free Planner')"
    )
    cta_url: str = Field(
        ...,
        description="Call-to-action destination URL"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional brand description for context"
    )
    target_audience: Optional[str] = Field(
        default=None,
        description="Optional target audience description"
    )

    model_config = ConfigDict(extra="ignore")
