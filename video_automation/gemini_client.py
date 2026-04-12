"""Bulletproof Gemini API client with auto-discovery, fallback, and self-healing.

This module is the SINGLE source of truth for all Gemini API calls across the
entire pipeline. Every file that needs Gemini should import from here instead
of calling the API directly.

Features:
- Auto-discovers available models at startup (no hardcoded model names to break)
- Prefers flash models, falls back through a priority chain
- Disables thinking for JSON calls (prevents response corruption)
- Retries with exponential backoff on rate limits (429)
- Logs every failure with full context for debugging
- Caches working model name so subsequent calls are fast
"""

import json
import logging
import os
import re
import time

from google import genai

logger = logging.getLogger(__name__)

_client = None
_working_model = None  # Cache of last model that worked

# Priority order: prefer newest flash, fall back to older stable models
MODEL_PRIORITY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.5-pro",
    "gemini-1.5-pro",
]


def get_client():
    """Lazy-initialize the Gemini client."""
    global _client
    if _client is None:
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        _client = genai.Client(api_key=api_key)
    return _client


def discover_models():
    """Query the Gemini API for available models and return them in priority order.

    Returns a list of model name strings that are actually available for
    generation, ordered by MODEL_PRIORITY preference.
    """
    try:
        client = get_client()
        available = []
        for model in client.models.list():
            name = model.name if hasattr(model, 'name') else str(model)
            # Strip "models/" prefix if present
            short_name = name.replace("models/", "")
            available.append(short_name)

        # Filter to our priority list + any other flash models
        ordered = []
        for preferred in MODEL_PRIORITY:
            if preferred in available:
                ordered.append(preferred)

        # Also add any other flash models we didn't list (future-proofing)
        for name in sorted(available):
            if "flash" in name and name not in ordered:
                ordered.append(name)

        if ordered:
            logger.info(f"Gemini models discovered: {ordered[:5]}")
        else:
            logger.warning(f"No priority models found. Available: {available[:10]}")
            # Last resort: return priority list and hope for the best
            ordered = MODEL_PRIORITY.copy()

        return ordered
    except Exception as e:
        logger.error(f"Model discovery failed: {e}")
        return MODEL_PRIORITY.copy()


def _get_thinking_config():
    """Build ThinkingConfig to disable thinking (prevents JSON corruption).

    Returns None if the SDK version doesn't support thinking config.
    """
    try:
        from google.genai import types
        return types.ThinkingConfig(thinking_budget=0)
    except Exception:
        # Catches pydantic_core.ValidationError on newer SDK versions that
        # reject thinking_budget=0 as an extra/invalid field.
        return None


def generate_json(prompt, max_tokens=1000):
    """Generate a JSON response from Gemini. Most reliable method for structured output.

    - Forces response_mime_type: application/json
    - Disables thinking (prevents reasoning tokens in output)
    - Auto-discovers and falls back through available models
    - Returns the raw JSON string

    Raises RuntimeError if all models fail.
    """
    return _generate(prompt, max_tokens=max_tokens, json_mode=True)


def generate_text(prompt, max_tokens=4000):
    """Generate a text response from Gemini.

    - Disables thinking for consistency
    - Auto-discovers and falls back through available models
    - Returns the raw text string

    Raises RuntimeError if all models fail.
    """
    return _generate(prompt, max_tokens=max_tokens, json_mode=False)


def _generate(prompt, max_tokens=1000, json_mode=True):
    """Core generation function with model fallback and retry logic."""
    global _working_model

    # Build model list: try cached working model first, then discovery
    if _working_model:
        models_to_try = [_working_model] + [m for m in discover_models() if m != _working_model]
    else:
        models_to_try = discover_models()

    if not models_to_try:
        raise RuntimeError("No Gemini models available")

    last_error = None
    thinking_config = _get_thinking_config()

    for model_name in models_to_try:
        config = {"max_output_tokens": max_tokens}
        if json_mode:
            config["response_mime_type"] = "application/json"
        if thinking_config is not None:
            config["thinking_config"] = thinking_config

        for attempt in range(3):
            try:
                response = get_client().models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                text = response.text.strip() if response.text else ""
                if not text:
                    raise ValueError(f"Empty response from {model_name}")

                # For JSON mode, validate it's actually parseable
                if json_mode:
                    try:
                        json.loads(text)
                    except json.JSONDecodeError:
                        # Try to extract JSON from response
                        json_match = re.search(r'\{.*\}', text, re.DOTALL)
                        if json_match:
                            json.loads(json_match.group())  # Validate
                            text = json_match.group()
                        else:
                            raise ValueError(f"Response from {model_name} is not valid JSON: {text[:100]}")

                # Success — cache this model
                if _working_model != model_name:
                    logger.info(f"Gemini model {model_name} working — caching for future calls")
                    _working_model = model_name
                return text

            except Exception as e:
                last_error = e
                err_str = str(e)

                if "429" in err_str and attempt < 2:
                    wait = 15 * (attempt + 1)
                    logger.warning(f"Rate limit on {model_name} — waiting {wait}s (attempt {attempt + 1}/3)")
                    time.sleep(wait)
                    continue
                else:
                    logger.warning(f"Model {model_name} failed: {err_str[:200]}")
                    break  # Try next model

    error_msg = f"All Gemini models failed. Last error: {last_error}"
    logger.error(error_msg)
    raise RuntimeError(error_msg)


def health_check():
    """Quick health check — tries to generate a minimal response.

    Returns (True, model_name) on success, (False, error_message) on failure.
    """
    try:
        text = generate_json('Return this exact JSON: {"status": "ok"}', max_tokens=50)
        parsed = json.loads(text)
        return True, _working_model or "unknown"
    except Exception as e:
        return False, str(e)[:200]
