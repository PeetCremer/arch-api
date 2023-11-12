import json
from pathlib import Path
from typing import Any

import pytest

Testcase = dict[str, dict[str, Any]]
TESTCASES_PATH = Path(__file__).parent / "testcases"
TESTCASE_NAMES = [path.name for path in TESTCASES_PATH.iterdir()]


def load_testcase(testcase: str) -> Testcase:
    testcase_path = TESTCASES_PATH / testcase
    with open(testcase_path / "building_limits.geojson") as f:
        building_limits: dict[str, Any] = json.load(f)
    with open(testcase_path / "height_plateaus.geojson") as f:
        height_plateaus: dict[str, Any] = json.load(f)
    return {
        "building_limits": building_limits,
        "height_plateaus": height_plateaus,
    }


@pytest.fixture(scope="session", params=[name for name in TESTCASE_NAMES if name.startswith("valid_")])
def valid_testcase(request: pytest.FixtureRequest) -> Testcase:
    return load_testcase(request.param)


@pytest.fixture(scope="session", params=[name for name in TESTCASE_NAMES if name.startswith("invalid_")])
def invalid_testcase(request: pytest.FixtureRequest) -> dict[str, Testcase]:
    return load_testcase(request.param)


@pytest.fixture
def vaterlandsparken_testcase() -> dict[str, dict[str, Any]]:
    return load_testcase("vaterlandsparken")
