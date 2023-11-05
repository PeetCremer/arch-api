from typing import Any

import fastapi
import pytest

from tests.integration.conftest import TestClient


async def delete_all_splits(test_client: TestClient) -> int:
    response = await test_client.delete_all_splits()
    assert response.status_code == fastapi.status.HTTP_200_OK
    num_deleted: int = response.json().get("num_deleted")
    return num_deleted


async def create_sample_split(
    test_client: TestClient, building_limits: dict[str, Any], height_plateaus: dict[str, Any]
) -> dict[str, Any]:
    input = {
        "building_limits": building_limits,
        "height_plateaus": height_plateaus,
    }
    response = await test_client.create_split(input)
    assert response.status_code == fastapi.status.HTTP_201_CREATED
    output = response.json()
    assert isinstance(output, dict)
    return output


@pytest.fixture
async def created_split(
    test_client: TestClient, building_limits: dict[str, Any], height_plateaus: dict[str, Any]
) -> dict[str, Any]:
    split = await create_sample_split(test_client, building_limits, height_plateaus)
    yield split
    # Teardown
    await test_client.delete_split(split["id"])


class TestCreateSplit:
    @pytest.mark.anyio
    async def test_valid(
        self, test_client: TestClient, building_limits: dict[str, Any], height_plateaus: dict[str, Any]
    ) -> None:
        _split = await create_sample_split(test_client, building_limits, height_plateaus)
        pass

    @pytest.mark.anyio
    @pytest.mark.parametrize("missing", ["building_limits", "height_plateaus"])
    async def test_invalid_missing_input(
        self, missing: str, test_client: TestClient, building_limits: dict[str, Any], height_plateaus: dict[str, Any]
    ) -> None:
        input = {
            "building_limits": building_limits,
            "height_plateaus": height_plateaus,
        }
        del input[missing]
        response = await test_client.create_split(input)
        assert response.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
        type = response.json().get("detail")[0].get("type")
        assert type == "missing"
        msg = response.json().get("detail")[0].get("msg")
        assert msg == "Field required"
        loc = response.json().get("detail")[0].get("loc")
        assert missing in loc

    @pytest.mark.anyio
    async def test_invalid_missing_elevation(
        self, test_client: TestClient, building_limits: dict[str, Any], height_plateaus: dict[str, Any]
    ) -> None:
        del height_plateaus["features"][0]["properties"]["elevation"]
        input = {
            "building_limits": building_limits,
            "height_plateaus": height_plateaus,
        }
        response = await test_client.create_split(input)
        assert response.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Missing 'elevation' property" in response.json().get("detail")[0].get("msg")

    @pytest.mark.anyio
    async def test_invalid_elevation_type(
        self, test_client: TestClient, building_limits: dict[str, Any], height_plateaus: dict[str, Any]
    ) -> None:
        height_plateaus["features"][0]["properties"]["elevation"] = "wrong type"
        input = {
            "building_limits": building_limits,
            "height_plateaus": height_plateaus,
        }
        response = await test_client.create_split(input)
        assert response.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "'elevation' property must be a float" in response.json().get("detail")[0].get("msg")
