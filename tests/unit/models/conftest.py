from typing import Any

import pytest


@pytest.fixture
def building_limits(vaterlandsparken_testcase: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return vaterlandsparken_testcase["building_limits"]


@pytest.fixture
def height_plateaus(vaterlandsparken_testcase: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return vaterlandsparken_testcase["height_plateaus"]


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
