import pytest
from unittest.mock import patch, MagicMock
from video_automation.nano_banana_generator import (
    BRAND_CONFIGS, generate_pin_image, generate_pin_batch
)


def test_all_brands_have_configs():
    for brand in ['fitness', 'deals', 'menopause']:
        assert brand in BRAND_CONFIGS
        assert 'name' in BRAND_CONFIGS[brand]
        assert 'colors' in BRAND_CONFIGS[brand]


def test_brand_configs_are_different():
    configs = [BRAND_CONFIGS[b]['colors'] for b in BRAND_CONFIGS]
    assert len(set(configs)) == len(configs), "Each brand must have unique colors"


def test_generate_pin_image_returns_none_without_api_key():
    with patch.dict('os.environ', {}, clear=True):
        result = generate_pin_image('fitness', 'test topic')
        assert result is None  # Should fail gracefully without API key
