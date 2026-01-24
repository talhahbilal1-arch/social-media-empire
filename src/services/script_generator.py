"""Script generation service with brand-specific prompts and caching.

This module provides the ScriptGenerator class that uses Gemini to generate
brand-appropriate video scripts with voiceovers and Pexels search terms.
"""

import logging
from datetime import date
from typing import Any, Dict, Optional

from src.clients.gemini import GeminiClient
from src.models.brand import BrandConfig
from src.models.content import Script
from src.utils.cache import FileCache


class ScriptGenerator:
    """Generate video scripts with brand-specific tone and CTAs.

    Uses Gemini for text generation with file-based caching to prevent
    quota exhaustion on the 5 RPM free tier limit.

    Cache key: hash(brand_slug + topic_seed + date)
    Including date ensures fresh content daily while allowing same-day reruns.

    Attributes:
        BRAND_VOICES: Mapping of brand slugs to voice configuration dicts.
        DEFAULT_VOICE: Fallback voice config for unknown brands.
    """

    BRAND_VOICES: Dict[str, Dict[str, str]] = {
        "menopause": {
            "tone": "warm, supportive, and understanding",
            "audience": "women navigating menopause",
            "style": "empathetic, informative, reassuring",
        },
        "daily_deal": {
            "tone": "excited, enthusiastic, and deal-savvy",
            "audience": "bargain hunters and smart shoppers",
            "style": "energetic, urgent but not pushy, value-focused",
        },
        "fitness": {
            "tone": "motivational, energetic, and encouraging",
            "audience": "people starting or maintaining fitness journeys",
            "style": "upbeat, can-do attitude, practical",
        },
    }

    DEFAULT_VOICE: Dict[str, str] = {
        "tone": "friendly and informative",
        "audience": "general audience",
        "style": "clear, engaging, helpful",
    }

    def __init__(self, gemini_client: Optional[GeminiClient] = None) -> None:
        """Initialize ScriptGenerator.

        Args:
            gemini_client: Optional GeminiClient instance. If not provided,
                a new client will be created using settings.
        """
        self.client = gemini_client or GeminiClient()
        self.cache = FileCache("scripts")
        self.logger = logging.getLogger(self.__class__.__name__)

    def _cache_key(self, brand_slug: str, topic_seed: Optional[str] = None) -> str:
        """Generate cache key for a brand/seed/date combination.

        Args:
            brand_slug: Brand identifier.
            topic_seed: Optional seed for reproducible generation.

        Returns:
            Cache key string combining brand, seed, and current date.
        """
        seed = topic_seed or "random"
        return f"{brand_slug}_{seed}_{date.today().isoformat()}"

    def _build_topic_prompt(
        self, brand_config: BrandConfig, voice: Dict[str, str]
    ) -> str:
        """Build prompt for topic generation.

        Args:
            brand_config: Brand configuration with name and description.
            voice: Voice configuration dict with tone/audience/style.

        Returns:
            Formatted prompt string for Gemini.
        """
        brand_description = brand_config.description or f"A brand called {brand_config.name}"

        return f"""You are generating a video topic for {brand_config.name}.
Brand voice: {voice['tone']}
Target audience: {voice['audience']}
Brand description: {brand_description}

Generate ONE unique, engaging topic for a 30-45 second video.
The topic should:
- Be relevant to {voice['audience']}
- Have visual potential (can be illustrated with stock footage)
- Be specific enough to be interesting, not generic

Return ONLY the topic as a single sentence, no quotes or extra text."""

    def _build_script_prompt(
        self,
        brand_config: BrandConfig,
        voice: Dict[str, str],
        topic: str,
        target_duration: int,
        word_count: int,
    ) -> str:
        """Build prompt for script generation.

        Args:
            brand_config: Brand configuration with CTA info.
            voice: Voice configuration dict with tone/style.
            topic: The generated topic to write about.
            target_duration: Target video duration in seconds.
            word_count: Maximum word count for script.

        Returns:
            Formatted prompt string for Gemini.
        """
        return f"""You are a video scriptwriter for {brand_config.name}.
Brand voice: {voice['tone']}
Style: {voice['style']}
CTA: "{brand_config.cta_text}" leading to {brand_config.cta_url}

Write a voiceover script for a {target_duration}-second video about:
{topic}

Requirements:
1. Start with a hook that grabs attention in the first 3 seconds
2. Provide valuable, specific information in 3-4 sentences
3. End by naturally mentioning the CTA - don't say "click the link", weave it in conversationally
4. Use conversational, spoken language - this will be read aloud
5. Keep it to {word_count} words maximum (about {target_duration} seconds of speech)

After the script, list 3-5 Pexels search terms that would find good background video footage.

Format your response EXACTLY like this:
VOICEOVER:
[Your script here - just the spoken words, no stage directions]

SEARCH_TERMS:
[comma-separated search terms]"""

    def _parse_response(
        self, response: str, brand_config: BrandConfig, topic: str
    ) -> Script:
        """Parse Gemini response into Script dataclass.

        Args:
            response: Raw response from Gemini API.
            brand_config: Brand configuration for metadata.
            topic: The topic that was used for generation.

        Returns:
            Script dataclass with parsed content.
        """
        voiceover = ""
        search_terms: list[str] = []

        if "VOICEOVER:" in response and "SEARCH_TERMS:" in response:
            parts = response.split("SEARCH_TERMS:")
            voiceover = parts[0].replace("VOICEOVER:", "").strip()
            search_terms = [t.strip() for t in parts[1].strip().split(",")]
        else:
            # Fallback: treat entire response as voiceover
            voiceover = response.strip()
            search_terms = ["lifestyle", "nature", "wellness"]
            self.logger.warning(
                "Could not parse structured response, using fallback search terms"
            )

        # Estimate duration: ~150 words per minute = 2.5 words per second
        word_count = len(voiceover.split())
        estimated_duration = word_count / 2.5

        return Script(
            topic=topic,
            voiceover=voiceover,
            search_terms=search_terms[:5],  # Max 5 terms
            brand_slug=brand_config.slug,
            cta_text=brand_config.cta_text,
            estimated_duration=estimated_duration,
        )

    def generate(
        self,
        brand_config: BrandConfig,
        topic_seed: Optional[str] = None,
        target_duration: int = 35,
    ) -> Script:
        """Generate a video script for the given brand.

        Args:
            brand_config: Brand configuration with name, colors, CTA, etc.
            topic_seed: Optional seed for reproducible topic generation.
            target_duration: Target video duration in seconds (default 35).

        Returns:
            Script dataclass with topic, voiceover, search_terms, etc.

        Flow:
            1. Check cache for existing script
            2. If cache miss: generate topic with Gemini
            3. Generate full script with Gemini
            4. Parse response into Script dataclass
            5. Cache and return
        """
        # Check cache first
        cache_key = self._cache_key(brand_config.slug, topic_seed)
        cached = self.cache.get(cache_key)
        if cached:
            self.logger.info(
                f"Cache HIT for {brand_config.slug}",
                extra={"cache_key": cache_key},
            )
            return Script.from_dict(cached)

        self.logger.info(
            f"Cache MISS for {brand_config.slug}",
            extra={"cache_key": cache_key},
        )

        # Get brand voice configuration
        # Normalize slug: "menopause-planner" -> "menopause" to match BRAND_VOICES keys
        normalized_slug = brand_config.slug.split("-")[0].replace("_", "")
        voice = self.BRAND_VOICES.get(normalized_slug, self.DEFAULT_VOICE)

        # Generate topic
        topic_prompt = self._build_topic_prompt(brand_config, voice)
        topic = self.client.generate_text(
            topic_prompt, max_tokens=100, temperature=0.9
        ).strip()

        # Generate script
        # ~150 words per minute, so target_duration seconds = target_duration * 2.5 words
        word_count = int(target_duration * 2.5)
        script_prompt = self._build_script_prompt(
            brand_config, voice, topic, target_duration, word_count
        )
        response = self.client.generate_text(
            script_prompt, max_tokens=500, temperature=0.7
        )

        # Parse response into Script dataclass
        script = self._parse_response(response, brand_config, topic)

        # Cache and return
        self.cache.set(cache_key, script.to_dict())
        self.logger.info(
            f"Generated script for {brand_config.slug}",
            extra={
                "topic": topic[:50],
                "duration_est": script.estimated_duration,
                "search_terms": script.search_terms,
            },
        )

        return script
