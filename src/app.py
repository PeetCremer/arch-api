import os
from typing import Any

import bson
import fastapi
import uvicorn
from dotenv import load_dotenv
from fastapi import HTTPException

from db import delete_split, get_db, get_split, save_split

load_dotenv()

app = fastapi.FastAPI(
    title="Architecture API (arch-api)",
    description=(
        "Consumes building limits and height plateaus, splits up the building limits"
        "according to the height plateaus, and stores these three entities persistently"
    ),
)

database = get_db(os.environ["MONGODB_URL"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"health": "OK"}


@app.get("/projects/{project}/splits/{split_id}")
async def get_split_byid(project: str, split_id: str) -> dict[str, Any]:
    try:
        split_object_id = bson.ObjectId(split_id)
    except bson.errors.InvalidId as e:
        raise HTTPException(status_code=400, detail=str(e))

    doc = await get_split(database, project, split_object_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Split not found")
    doc = dict(doc)
    # unwrap ObjectId before returning
    doc["_id"] = str(doc["_id"])
    return doc


@app.post("/projects/{project}/splits", status_code=fastapi.status.HTTP_201_CREATED)
async def create_split(project: str, split: dict[str, Any]) -> dict[str, Any]:
    # TODO: split should be a pydantic model
    doc = await save_split(database, project, split)
    doc = dict(doc)
    # unwrap ObjectId before returning
    doc["_id"] = str(doc["_id"])
    return doc


@app.delete("/projects/{project}/splits/{split_id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_split_byid(project: str, split_id: str) -> None:
    try:
        split_object_id = bson.ObjectId(split_id)
    except bson.errors.InvalidId as e:
        raise HTTPException(status_code=400, detail=str(e))

    deleted = await delete_split(database, project, split_object_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Split not found")


if __name__ == "__main__":
    uvicorn.run("app:app", port=8000, reload=True)
