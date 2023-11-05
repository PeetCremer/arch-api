import json
from pathlib import Path
from typing import Any

import pytest

_TEST_CASES_PATH = Path(__file__).parent / "testcases"


@pytest.fixture
def building_limits() -> dict[str, Any]:
    with open(_TEST_CASES_PATH / "vaterlandsparken" / "building_limits.geojson") as f:
        building_limits: dict[str, Any] = json.load(f)
    return building_limits


@pytest.fixture
def height_plateaus() -> dict[str, Any]:
    with open(_TEST_CASES_PATH / "vaterlandsparken" / "height_plateaus.geojson") as f:
        height_plateaus: dict[str, Any] = json.load(f)
    return height_plateaus


@pytest.fixture
def feature(building_limits: dict[str, Any]) -> dict[str, Any]:
    feature = building_limits["features"][0]
    assert isinstance(feature, dict)
    return feature


@pytest.fixture
def feature_with_elevation(height_plateaus: dict[str, Any]) -> dict[str, Any]:
    feature = height_plateaus["features"][0]
    assert isinstance(feature, dict)
    return feature


@pytest.fixture
def polygon(feature: dict[str, Any]) -> dict[str, Any]:
    polygon = feature["geometry"]
    assert isinstance(polygon, dict)
    return polygon
