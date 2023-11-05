from typing import Any

import pytest
from arch_api.models.geojson import (
    Polygon2d,
    Polygon2dFeature,
    Polygon2dFeatureCollection,
)
from geojson_pydantic import Feature, Point
from pydantic import ValidationError


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
        _feature_collection = Polygon2dFeatureCollection(**building_limits)

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
