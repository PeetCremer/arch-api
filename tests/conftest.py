import json
from pathlib import Path
from typing import Any

import pytest

TESTCASES_PATH = Path(__file__).parent / "testcases"


def load_testcase(testcase: str) -> dict[str, dict[str, Any]]:
    testcase_path = TESTCASES_PATH / testcase
    with open(testcase_path / "building_limits.geojson") as f:
        building_limits: dict[str, Any] = json.load(f)
    with open(testcase_path / "height_plateaus.geojson") as f:
        height_plateaus: dict[str, Any] = json.load(f)
    return {
        "building_limits": building_limits,
        "height_plateaus": height_plateaus,
    }


@pytest.fixture
def valid_testcases() -> list[dict[str, dict[str, Any]]]:
    testcases = []
    for path in TESTCASES_PATH.iterdir():
        testcase = path.name
        if testcase.startswith("valid_"):
            testcases.append(load_testcase(testcase))
    return testcases


@pytest.fixture
def invalid_testcases() -> list[dict[str, dict[str, Any]]]:
    testcases = []
    for path in TESTCASES_PATH.iterdir():
        testcase = path.name
        if testcase.startswith("invalid_"):
            testcases.append(load_testcase(testcase))
    return testcases


@pytest.fixture
def vaterlandsparken_testcase() -> dict[str, dict[str, Any]]:
    return load_testcase("vaterlandsparken")


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
