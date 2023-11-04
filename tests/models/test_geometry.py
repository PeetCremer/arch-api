import json
from pathlib import Path
from typing import Any

import pytest
from arch_api.models.geometry import (
    BuildingLimits,
    HeightPlateaus,
    Polygon2d,
    Polygon2dFeature,
    Polygon2dFeatureCollection,
)
from geojson_pydantic import Feature, Point
from pydantic import ValidationError

_TEST_CASES_PATH = Path(__file__).parent.parent / "cases"


@pytest.fixture
def building_limits() -> dict[str, Any]:
    with open(_TEST_CASES_PATH / "1" / "building_limits.geojson") as f:
        building_limits: dict[str, Any] = json.load(f)
    return building_limits


@pytest.fixture
def height_plateaus() -> dict[str, Any]:
    with open(_TEST_CASES_PATH / "1" / "height_plateaus.geojson") as f:
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


class TestPolygon2d:
    def test_valid(self, polygon: dict[str, Any]) -> None:
        _polygon = Polygon2d(**polygon)

    def test_invalid(self, polygon: dict[str, Any]) -> None:
        # append additional coordinates to first and last position of the ring
        polygon["coordinates"][0][0].append(0.0)
        polygon["coordinates"][0][-1].append(0.0)
        with pytest.raises(ValidationError, match="Only 2D Polygons are supported"):
            _polygon = Polygon2d(**polygon)


class TestPolygon2dFeature:
    def test_valid(self, feature: dict[str, Any]) -> None:
        _feature = Polygon2dFeature(**feature)

    def test_invalid_polygon(self, feature: dict[str, Any]) -> None:
        for i in range(len(feature["geometry"]["coordinates"][0])):
            feature["geometry"]["coordinates"][0][i].append(0.0)
        with pytest.raises(ValidationError, match="Only 2D Polygons are supported"):
            _feature = Polygon2dFeature(**feature)

    def test_invalid_geometry(self) -> None:
        point = Point(type="Point", coordinates=[0.0, 0.0])
        # Should complain about 'Polygon' in error message
        with pytest.raises(ValidationError, match="Polygon"):
            _feature = Polygon2dFeature(type="Feature", geometry=point, properties=None)


class TestPolygon2dFeatureCollection:
    """
    This also tests BuildingLimits and HeightPlateaus, as they are
    derived from Polygon2dFeatureCollection
    """

    def test_valid(self, building_limits: dict[str, Any]) -> None:
        _feature_collection = BuildingLimits(**building_limits)

    def test_invalid_feature(self) -> None:
        point = Point(type="Point", coordinates=[0.0, 0.0])
        feature: Feature[Point, dict[str, Any]] = Feature(type="Feature", geometry=point, properties=None)
        # Should complain about Polygon2dFeature in error message
        with pytest.raises(ValidationError, match="Polygon2dFeature"):
            _feature_collection = Polygon2dFeatureCollection(type="FeatureCollection", features=[feature])

    def test_model_dump(self, building_limits: dict[str, Any]) -> None:
        feature_collection = Polygon2dFeatureCollection(**building_limits)
        dump = feature_collection.model_dump()
        assert isinstance(dump, dict)


class TestHeightPlateaus:
    def test_valid(self, height_plateaus: dict[str, Any]) -> None:
        _height_plateaus = HeightPlateaus(**height_plateaus)

    def test_invalid_missing_elevation(self, height_plateaus: dict[str, Any]) -> None:
        del height_plateaus["features"][0]["properties"]["elevation"]
        with pytest.raises(ValidationError, match="Missing 'elevation' property"):
            _height_plateaus = HeightPlateaus(**height_plateaus)

    def test_invalid_elevation_not_float(self, height_plateaus: dict[str, Any]) -> None:
        height_plateaus["features"][0]["properties"]["elevation"] = "a"
        with pytest.raises(ValidationError, match="'elevation' property must be a float"):
            _height_plateaus = HeightPlateaus(**height_plateaus)
