"""Tests for nano_banana_generator.py — Gemini image generation for Pinterest pins."""

import pytest
from unittest.mock import MagicMock, patch

from video_automation.nano_banana_generator import (
    BRAND_CONFIGS,
    IMAGE_MODEL,
    _build_prompt,
    _pexels_fallback,
    generate_pin_batch,
    generate_pin_image,
)


# ── Config sanity ─────────────────────────────────────────────────────────────

def test_all_brands_have_configs():
    for brand in ("fitness", "deals", "menopause"):
        assert brand in BRAND_CONFIGS
        for key in ("name", "colors", "style", "audience", "aesthetic"):
            assert key in BRAND_CONFIGS[brand], f"{brand} missing '{key}'"


def test_brand_prompts_are_unique():
    """Each brand must produce a distinct image prompt (different visual identity)."""
    prompts = {brand: _build_prompt(brand, "test topic") for brand in BRAND_CONFIGS}
    assert len(set(prompts.values())) == 3, "All brands must have unique prompts"


def test_fitness_brand_targets_men():
    """FitOver35 is men-only — prompt must not mention women."""
    prompt = _build_prompt("fitness", "strength training")
    prompt_lower = prompt.lower()
    assert "men" in prompt_lower or "masculine" in prompt_lower
    assert "women over 35" not in prompt_lower  # regression: was wrong in old version


def test_model_name_is_image_model():
    """Ensure we're using the image-capable model, not the text model."""
    assert "image" in IMAGE_MODEL.lower() or "flash" in IMAGE_MODEL.lower()


# ── generate_pin_image — success path ─────────────────────────────────────────

def _make_mock_response(image_bytes: bytes):
    """Build a fake Gemini generate_content response containing an image part."""
    part = MagicMock()
    part.inline_data = MagicMock()
    part.inline_data.data = image_bytes

    content = MagicMock()
    content.parts = [part]

    candidate = MagicMock()
    candidate.content = content

    response = MagicMock()
    response.candidates = [candidate]
    return response


def test_generate_pin_image_returns_bytes():
    """Happy path: Gemini returns image bytes → function returns them unchanged."""
    fake_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _make_mock_response(fake_bytes)

    with patch("video_automation.nano_banana_generator._get_client", return_value=mock_client):
        result = generate_pin_image("fitness", "5 strength exercises for men over 35")

    assert result == fake_bytes
    mock_client.models.generate_content.assert_called_once()


def test_generate_pin_image_uses_correct_model():
    """The call must use IMAGE_MODEL, not a text-only model."""
    fake_bytes = b"\x89PNG" + b"\x00" * 50

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _make_mock_response(fake_bytes)

    with patch("video_automation.nano_banana_generator._get_client", return_value=mock_client):
        generate_pin_image("deals", "Amazon home finds under $20")

    call_kwargs = mock_client.models.generate_content.call_args
    assert call_kwargs[1].get("model") == IMAGE_MODEL or call_kwargs[0][0] == IMAGE_MODEL or \
           mock_client.models.generate_content.call_args.kwargs.get("model") == IMAGE_MODEL or \
           IMAGE_MODEL in str(call_kwargs)


# ── generate_pin_image — failure / fallback ───────────────────────────────────

def test_generate_pin_image_retries_then_falls_back_to_pexels():
    """When Gemini fails 3 times, we must call the Pexels fallback."""
    fake_pexels_bytes = b"PEXELS_IMAGE_DATA"

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = RuntimeError("API quota exceeded")

    with patch("video_automation.nano_banana_generator._get_client", return_value=mock_client), \
         patch("video_automation.nano_banana_generator._pexels_fallback", return_value=fake_pexels_bytes) as mock_pexels, \
         patch("time.sleep"):  # Skip actual sleeps in tests
        result = generate_pin_image("menopause", "hot flash relief tips")

    assert result == fake_pexels_bytes
    mock_pexels.assert_called_once_with("menopause", "hot flash relief tips")
    assert mock_client.models.generate_content.call_count == 3  # exhausted all retries


def test_generate_pin_image_raises_when_both_fail():
    """If both Gemini and Pexels fail, RuntimeError should propagate."""
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = RuntimeError("Gemini down")

    with patch("video_automation.nano_banana_generator._get_client", return_value=mock_client), \
         patch("video_automation.nano_banana_generator._pexels_fallback", side_effect=RuntimeError("Pexels down")), \
         patch("time.sleep"):
        with pytest.raises(RuntimeError):
            generate_pin_image("fitness", "workout tips")


# ── generate_pin_batch ─────────────────────────────────────────────────────────

def test_generate_pin_batch_returns_correct_count():
    """Batch should return one result per topic when generation succeeds."""
    fake_bytes = b"\x89PNG" + b"\x00" * 30
    topics = ["topic A", "topic B", "topic C"]

    with patch("video_automation.nano_banana_generator.generate_pin_image", return_value=fake_bytes), \
         patch("video_automation.nano_banana_generator._generate_metadata",
               return_value={"title": "Test Title", "description": "Test desc"}):
        results = generate_pin_batch("fitness", topics, count=3)

    assert len(results) == 3
    for r in results:
        assert "image_bytes" in r
        assert "topic" in r
        assert "title" in r
        assert "description" in r
        assert "filename" in r
        assert r["image_bytes"] == fake_bytes


def test_generate_pin_batch_skips_failed_pins():
    """A single pin failure should not abort the whole batch."""
    good_bytes = b"\x89PNG" + b"\x00" * 20
    call_count = {"n": 0}

    def sometimes_fail(brand, topic, style="default"):
        call_count["n"] += 1
        if call_count["n"] == 2:
            raise RuntimeError("Simulated failure on pin 2")
        return good_bytes

    with patch("video_automation.nano_banana_generator.generate_pin_image", side_effect=sometimes_fail), \
         patch("video_automation.nano_banana_generator._generate_metadata",
               return_value={"title": "T", "description": "D"}):
        results = generate_pin_batch("deals", ["t1", "t2", "t3"], count=3)

    # Pin 2 failed — only 2 results
    assert len(results) == 2


def test_generate_pin_batch_cycles_topics():
    """When count > len(topics), topics should cycle rather than crash."""
    fake_bytes = b"\x89PNG" + b"\x00" * 10

    with patch("video_automation.nano_banana_generator.generate_pin_image", return_value=fake_bytes), \
         patch("video_automation.nano_banana_generator._generate_metadata",
               return_value={"title": "T", "description": "D"}):
        results = generate_pin_batch("menopause", ["only topic"], count=5)

    assert len(results) == 5
    assert all(r["topic"] == "only topic" for r in results)
