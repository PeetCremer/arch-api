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


class Polygon2dFeatureCollection(FeatureCollection[Polygon2dFeature]):
    """
    FeatureCollection restricted to features with the 2d Polygon geometry
    """

    ...


class BuildingLimits(Polygon2dFeatureCollection):
    """
    BuildingLimits are effectively a FeatureCollection of 2d Polygons
    """

    ...


class HeightPlateaus(Polygon2dFeatureCollection):
    """
    HeightPlateaus are a FeatureCollection of 2d Polygons
    with the additional constraint that the features need
    to have the "elevation" property set with a valid float
    """

    features: list[Polygon2dFeature]

    @field_validator("features", mode="after")
    @classmethod
    def check_elevation_property(cls, features: list[Polygon2dFeature]) -> list[Polygon2dFeature]:
        for feature in features:
            if "elevation" not in feature.properties:
                raise ValueError("Missing 'elevation' property")
            if not isinstance(feature.properties["elevation"], float):
                raise ValueError("'elevation' property must be a float")
        return features


class Split(HeightPlateaus):
    """
    Splits are from a dataclass perspective the same as HeightPlateaus,
    as they need to have elevation populated
    """

    ...
