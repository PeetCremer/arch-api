import pytest
from arch_api.models.io import ProjectMixin
from pydantic import ValidationError


class TestProjectMixin:
    @pytest.mark.parametrize("project", ["a", "a" * 50])
    def test_valid(self, project: str) -> None:
        _project_mixin = ProjectMixin(project=project)

    @pytest.mark.parametrize("project", ["", "a" * 51])
    def test_invalid(self, project: str) -> None:
        with pytest.raises(ValidationError):
            _project_mixin = ProjectMixin(project=project)
