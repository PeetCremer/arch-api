# We base the pydantic models on the geojson_pydantic models,
# as they follow the GeoJSON standard quite well
# https://datatracker.ietf.org/doc/html/rfc7946#section-3.1.1
from typing import Any

from geojson_pydantic.features import Feature, FeatureCollection
from geojson_pydantic.geometries import Polygon
from pydantic import model_validator


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
