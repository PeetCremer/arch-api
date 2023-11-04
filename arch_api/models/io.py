from arch_api.models.geometry import BuildingLimits, HeightPlateaus, Splits
from pydantic import BaseModel, Field


class ProjectMixin(BaseModel):
    project: str = Field(..., min_length=1, max_length=50)


class CreateSplitInput(BaseModel):
    building_limits: BuildingLimits
    height_plateaus: HeightPlateaus


class CreateSplitsOutput(ProjectMixin):
    _id: str
    building_limits: BuildingLimits
    height_plateaus: HeightPlateaus
    # The splits need to have elevation populated
    splits: Splits
