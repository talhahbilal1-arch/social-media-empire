"""Assert BRAND_SLUG maps each short key to the exact hyphenated slug that
Make.com route filters expect. A wrong slug causes silent pin drops — this
test catches the drift before it reaches production.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from video_automation.brand_slugs import BRAND_SLUG

EXPECTED = {
    'fitness': 'fitness-made-easy',
    'deals': 'daily-deal-darling',
    'menopause': 'menopause-planner',
}


@pytest.mark.parametrize("short_key,expected_slug", EXPECTED.items())
def test_brand_slug_mapping(short_key, expected_slug):
    assert short_key in BRAND_SLUG, \
        f"Short key '{short_key}' missing from BRAND_SLUG in brand_slugs.py"
    assert BRAND_SLUG[short_key] == expected_slug, (
        f"BRAND_SLUG['{short_key}'] = '{BRAND_SLUG[short_key]}', "
        f"expected '{expected_slug}'. Make.com route filters will silently reject posts."
    )


def test_no_unknown_brands():
    """Catch additions that haven't been registered in Make.com scenarios yet."""
    assert set(BRAND_SLUG.keys()) == set(EXPECTED.keys()), (
        f"Unexpected brands in BRAND_SLUG: {set(BRAND_SLUG.keys()) - set(EXPECTED.keys())}. "
        "Add a Make.com route filter for each new brand before adding it here."
    )
