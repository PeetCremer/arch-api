from collections import OrderedDict
from typing import Any

import fastapi
import pytest

from tests.conftest import Testcase
from tests.integration.conftest import TestClient


def dict_to_deep_ordered_dict(d: dict[str, Any]) -> OrderedDict[str, Any]:
    return OrderedDict({k: dict_to_deep_ordered_dict(v) if isinstance(v, dict) else v for k, v in d.items()})


async def delete_all_splits(test_client: TestClient) -> int:
    response = await test_client.delete_all_splits()
    assert response.status_code == fastapi.status.HTTP_200_OK
    num_deleted: int = response.json().get("num_deleted")
    return num_deleted


async def create_sample_split(test_client: TestClient, testcase: Testcase) -> dict[str, Any]:
    response = await test_client.create_split(testcase)
    assert response.status_code == fastapi.status.HTTP_201_CREATED
    split = response.json()
    assert isinstance(split, dict)
    return split


@pytest.fixture
async def created_split(test_client: TestClient, vaterlandsparken_testcase: Testcase) -> dict[str, Any]:
    split = await create_sample_split(test_client, vaterlandsparken_testcase)
    yield split
    # Teardown
    response = await test_client.delete_split(split["id"])
    assert response.status_code in [fastapi.status.HTTP_204_NO_CONTENT, fastapi.status.HTTP_404_NOT_FOUND]


@pytest.fixture
async def created_multiple_splits(test_client: TestClient, vaterlandsparken_testcase: Testcase) -> list[dict[str, Any]]:
    num = 42
    splits = [await create_sample_split(test_client, vaterlandsparken_testcase) for _ in range(num)]
    yield splits
    # Teardown
    for split in splits:
        response = await test_client.delete_split(split["id"])
        assert response.status_code in [fastapi.status.HTTP_204_NO_CONTENT, fastapi.status.HTTP_404_NOT_FOUND]


class TestCreateSplit:
    @pytest.fixture(autouse=True, scope="class")
    async def cleanup_after_tests(self, test_client: TestClient) -> None:
        """
        Cleanup all created splits after all tests in the class are concluded
        """
        # Code that runs before tests goes here
        yield
        # Code that runs after tests goes here
        await delete_all_splits(test_client)

    @pytest.mark.asyncio
    async def test_vaterlandsparken(self, created_split: dict[str, Any]) -> None:
        features = created_split["split"]["features"]
        assert len(features) == 3
        # elevations should be all different
        assert features[0]["properties"]["elevation"] != features[1]["properties"]["elevation"]
        assert features[0]["properties"]["elevation"] != features[2]["properties"]["elevation"]
        assert features[1]["properties"]["elevation"] != features[2]["properties"]["elevation"]

    @pytest.mark.asyncio
    async def test_height_plateaus_do_not_cover(
        self, test_client: TestClient, vaterlandsparken_testcase: Testcase
    ) -> None:
        # remove one point from height plateaus so that they no longer cover
        height_plateaus = vaterlandsparken_testcase["height_plateaus"]
        height_plateaus["features"][0]["geometry"]["coordinates"][0].pop()
        height_plateaus["features"][0]["geometry"]["coordinates"][0][-1] = height_plateaus["features"][0]["geometry"][
            "coordinates"
        ][0][0]
        response = await test_client.create_split(vaterlandsparken_testcase)
        assert response.status_code == fastapi.status.HTTP_400_BAD_REQUEST
        assert "The height plateaus do not completely cover the building limits" in response.json().get("detail")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("missing", ["building_limits", "height_plateaus"])
    async def test_missing_input(
        self, missing: str, test_client: TestClient, vaterlandsparken_testcase: Testcase
    ) -> None:
        # Delete one of the inputs
        del vaterlandsparken_testcase[missing]
        response = await test_client.create_split(vaterlandsparken_testcase)
        assert response.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
        type = response.json().get("detail")[0].get("type")
        assert type == "missing"
        msg = response.json().get("detail")[0].get("msg")
        assert msg == "Field required"
        loc = response.json().get("detail")[0].get("loc")
        assert missing in loc

    @pytest.mark.asyncio
    async def test_invalid_missing_elevation(
        self, test_client: TestClient, vaterlandsparken_testcase: Testcase
    ) -> None:
        height_plateaus = vaterlandsparken_testcase["height_plateaus"]
        del height_plateaus["features"][0]["properties"]["elevation"]
        response = await test_client.create_split(vaterlandsparken_testcase)
        assert response.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Missing 'elevation' property" in response.json().get("detail")[0].get("msg")

    @pytest.mark.asyncio
    async def test_wrong_type_for_elevation(self, test_client: TestClient, vaterlandsparken_testcase: Testcase) -> None:
        height_plateaus = vaterlandsparken_testcase["height_plateaus"]
        height_plateaus["features"][0]["properties"]["elevation"] = "wrong type"
        response = await test_client.create_split(vaterlandsparken_testcase)
        assert response.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "'elevation' property must be a float" in response.json().get("detail")[0].get("msg")

    @pytest.mark.asyncio
    async def test_invalid_testcases(self, test_client: TestClient, invalid_testcase: Testcase) -> None:
        response = await test_client.create_split(invalid_testcase)
        assert response.status_code in [
            fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            fastapi.status.HTTP_400_BAD_REQUEST,
        ]

    @pytest.mark.asyncio
    async def test_valid_testcases(self, test_client: TestClient, valid_testcase: Testcase) -> None:
        response = await test_client.create_split(valid_testcase)
        assert response.status_code == fastapi.status.HTTP_201_CREATED


class TestDeleteSplit:
    @pytest.mark.asyncio
    async def test_valid(self, test_client: TestClient, created_split: dict[str, Any]) -> None:
        response = await test_client.delete_split(created_split["id"])
        assert response.status_code == fastapi.status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_missing(self, test_client: TestClient, created_split: dict[str, Any]) -> None:
        response = await test_client.delete_split(created_split["id"])
        assert response.status_code == fastapi.status.HTTP_204_NO_CONTENT
        response = await test_client.delete_split(created_split["id"])
        assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND
        assert response.json().get("detail") == "Split not found"

    @pytest.mark.asyncio
    async def test_invalid_id(self, test_client: TestClient) -> None:
        response = await test_client.delete_split("invalid")
        assert response.status_code == fastapi.status.HTTP_400_BAD_REQUEST
        assert "'invalid' is not a valid ObjectId" in response.json().get("detail")


class TestGetSplit:
    @pytest.mark.asyncio
    async def test_valid(self, test_client: TestClient, created_split: dict[str, Any]) -> None:
        response = await test_client.get_split(created_split["id"])
        assert response.status_code == fastapi.status.HTTP_200_OK
        split: dict[str, Any] = response.json()
        # should be equal to created split except for ordering of elements
        assert dict_to_deep_ordered_dict(split) == dict_to_deep_ordered_dict(created_split)

    @pytest.mark.asyncio
    async def test_split_not_found(self, test_client: TestClient, created_split: dict[str, Any]) -> None:
        response = await test_client.delete_split(created_split["id"])
        assert response.status_code == fastapi.status.HTTP_204_NO_CONTENT
        response = await test_client.get_split(created_split["id"])
        assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND
        assert response.json().get("detail") == "Split not found"

    @pytest.mark.asyncio
    async def test_bad_object_id(self, test_client: TestClient) -> None:
        response = await test_client.get_split("bad_id")
        assert response.status_code == fastapi.status.HTTP_400_BAD_REQUEST
        assert "'bad_id' is not a valid ObjectId" in response.json().get("detail")


class TestDeleteAllSplits:
    @pytest.fixture(autouse=True, scope="function")
    async def cleanup_before_each_test(self, test_client: TestClient) -> None:
        """
        Cleanup any previously created splits before each test in the class
        """
        # Code that runs before tests goes here
        await delete_all_splits(test_client)
        yield
        # Code that runs after tests goes here
        pass

    @pytest.mark.asyncio
    async def test_delete_zero(self, test_client: TestClient) -> None:
        num_deleted = await delete_all_splits(test_client)
        assert num_deleted == 0

    @pytest.mark.asyncio
    async def test_delete_multiple(
        self, test_client: TestClient, created_multiple_splits: list[dict[str, Any]]
    ) -> None:
        num_deleted = await delete_all_splits(test_client)
        assert num_deleted == len(created_multiple_splits)


class TestListSplits:
    @pytest.fixture(autouse=True, scope="class")
    async def cleanup_before(self, test_client: TestClient) -> None:
        """
        Cleanup any previously created splits before running any tests in the class
        """
        # Code that runs before tests goes here
        await delete_all_splits(test_client)
        yield
        # Code that runs after tests goes here
        pass

    @pytest.mark.asyncio
    async def test_bad_skip(self, test_client: TestClient) -> None:
        response = await test_client.list_splits(skip=-1)
        assert response.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
        type = response.json().get("detail")[0].get("type")
        assert type == "greater_than_equal"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("limit", [-1, 11])
    async def test_bad_limit(self, test_client: TestClient, limit: int) -> None:
        response = await test_client.list_splits(limit=limit)
        assert response.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
        type = response.json().get("detail")[0].get("type")
        assert type in ["greater_than_equal", "less_than_equal"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ["skip", "limit", "expected_len"], [(0, 0, 10), (0, 10, 10), (40, 10, 2), (42, 10, 0), (0, 5, 5), (38, 5, 4)]
    )
    async def test_skip_and_limit(
        self,
        test_client: TestClient,
        created_multiple_splits: list[dict[str, Any]],
        skip: int,
        limit: int,
        expected_len: int,
    ) -> None:
        response = await test_client.list_splits(skip=skip, limit=limit)
        assert response.status_code == fastapi.status.HTTP_200_OK
        items = response.json()
        assert isinstance(items, list)
        assert len(items) == expected_len

    # def test_skip_non_negative()
