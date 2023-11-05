from collections.abc import Mapping
from typing import Any

from arch_api.models.geojson import Polygon2dFeature, Polygon2dFeatureCollection
from pydantic import BaseModel, Field, field_validator


class ProjectMixin(BaseModel):
    project: str = Field(..., min_length=1, max_length=50)


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


class CreateSplitInput(BaseModel):
    building_limits: BuildingLimits
    height_plateaus: HeightPlateaus


class CreateSplitOutput(ProjectMixin):
    id: str
    building_limits: BuildingLimits
    height_plateaus: HeightPlateaus
    # The splits need to have elevation populated
    split: Split

    def from_doc(doc: Mapping[str, Any]) -> "CreateSplitOutput":
        return CreateSplitOutput(
            id=str(doc["_id"]),
            project=doc["project"],
            building_limits=doc["building_limits"],
            height_plateaus=doc["height_plateaus"],
            split=doc["split"],
        )
