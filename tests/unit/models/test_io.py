from typing import Any

import pytest
from arch_api.models.io import HeightPlateaus, ProjectMixin
from pydantic import ValidationError


class TestProjectMixin:
    @pytest.mark.parametrize("project", ["a", "a" * 50])
    def test_valid(self, project: str) -> None:
        _project_mixin = ProjectMixin(project=project)

    @pytest.mark.parametrize("project", ["", "a" * 51])
    def test_invalid(self, project: str) -> None:
        with pytest.raises(ValidationError):
            _project_mixin = ProjectMixin(project=project)


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
