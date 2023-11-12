import pytest

from tests.conftest import Testcase, load_testcase


@pytest.fixture
def overlapping_height_plateaus_testcase() -> Testcase:
    return load_testcase("invalid_overlapping_height_plateaus")


@pytest.fixture
def overlapping_building_limits_testcase() -> Testcase:
    return load_testcase("invalid_overlapping_building_limits")


@pytest.fixture
def height_plateaus_not_covering_testcase() -> Testcase:
    return load_testcase("invalid_not_covering")
