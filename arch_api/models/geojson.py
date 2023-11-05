# We base the pydantic models on the geojson_pydantic models,
# as they follow the GeoJSON standard quite well
# https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.1
from typing import Any

from geojson_pydantic.features import Feature, FeatureCollection
from geojson_pydantic.geometries import Polygon
from pydantic import field_validator, model_validator


class Polygon2d(Polygon):
    """
    Polygon with no elevation
    """

    @model_validator(mode="after")
    def check_2d(self) -> "Polygon2d":
        if self.has_z:
            raise ValueError("Only 2D Polygons are supported")
        return self


class Polygon2dFeature(Feature[Polygon2d, dict[str, Any]]):
    """
    Feature restricted to the 2d Polygon geometry
    """

    geometry: Polygon2d


class NonEmptyPolygon2dFeatureCollection(FeatureCollection[Polygon2dFeature]):
    """
    FeatureCollection restricted to features with the 2d Polygon geometry
    that contains at least 1 polygon
    """

    @field_validator("features", mode="after")
    @classmethod
    def check_features_nonempty(cls, features: list[Polygon2dFeature]) -> list[Polygon2dFeature]:
        if len(features) == 0:
            raise ValueError("FeatureCollection must contain at least 1 feature")
        return features
