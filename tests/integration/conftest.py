import asyncio
from collections.abc import AsyncIterator, Iterator
from typing import Any

import pytest
from arch_api.app import app
from httpx import AsyncClient, Response


class TestClient(AsyncClient):
    def __init__(self, project: str = "test"):
        super().__init__(app=app, base_url="http://test")
        self.project = project

    async def health(self) -> Response:
        response = await self.get("/health")
        assert isinstance(response, Response)
        return response

    async def create_split(self, input: dict[str, Any]) -> Response:
        response = await self.post(f"/projects/{self.project}/splits", json=input)
        assert isinstance(response, Response)
        return response

    async def get_split(self, id: str) -> Response:
        response = await self.get(f"/projects/{self.project}/splits/{id}")
        assert isinstance(response, Response)
        return response

    async def delete_split(self, id: str) -> Response:
        response = await self.delete(f"/projects/{self.project}/splits/{id}")
        assert isinstance(response, Response)
        return response

    async def delete_all_splits(self) -> Response:
        response = await self.delete(f"/projects/{self.project}/splits")
        assert isinstance(response, Response)
        return response


# override pytests event loop to be module scoped
# to avoid "RuntimeError: Event loop is closed" errors
# when running multiple tests in parallel
@pytest.fixture(scope="module")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# test_client must be module scoped, same as event_loop
@pytest.fixture(scope="module")
async def test_client() -> AsyncIterator[TestClient]:
    async with TestClient() as client:
        yield client
