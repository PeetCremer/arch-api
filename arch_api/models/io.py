from arch_api.models.geometry import BuildingLimits, HeightPlateaus, Split
from pydantic import BaseModel, Field


class ProjectMixin(BaseModel):
    project: str = Field(..., min_length=1, max_length=50)


class SplitInput(BaseModel):
    building_limits: BuildingLimits
    height_plateaus: HeightPlateaus


class SplitOutput(ProjectMixin):
    _id: str
    building_limits: BuildingLimits
    height_plateaus: HeightPlateaus
    # The splits need to have elevation populated
    split: Split
