import logging
import os

import bson
import fastapi
from arch_api.db import delete_all_split_triples, delete_split_triple, get_db, get_split_triple, save_split_triple
from arch_api.exceptions import HANDLERS
from arch_api.models.io import CreateSplitInput, CreateSplitOutput
from arch_api.splitting import split_building_limits_by_height_plateaus
from dotenv import load_dotenv
from fastapi import HTTPException

# Initialize DB
load_dotenv()
_DATABASE = get_db(os.environ["MONGODB_URL"])

# Intialize app
app = fastapi.FastAPI(
    title="Architecture API (arch-api)",
    description=(
        "Consumes building limits and height plateaus, splits up the building limits"
        "according to the height plateaus, and stores these three entities persistently"
    ),
)
# Attach exception handlers
for exc, handler in HANDLERS.items():
    app.add_exception_handler(exc, handler)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"health": "OK"}


@app.get("/projects/{project}/splits/{id}")
async def get_split(project: str, id: str) -> CreateSplitOutput:
    # TODO move into exception handler
    try:
        object_id = bson.ObjectId(id)
    except bson.errors.InvalidId as e:
        raise HTTPException(status_code=400, detail=str(e))

    doc = await get_split_triple(_DATABASE, project, object_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Split not found")

    # Build output object
    return CreateSplitOutput.from_doc(doc)


@app.post("/projects/{project}/splits", status_code=fastapi.status.HTTP_201_CREATED)
async def create_split(project: str, input: CreateSplitInput) -> CreateSplitOutput:
    # TODO create a proper split. For now, we just copy the height_plateaus
    logging.debug("Processing split")
    split = split_building_limits_by_height_plateaus(input.building_limits, input.height_plateaus)
    logging.debug("Processing split done")

    # Persist the split
    logging.debug("Before save_split_triple")
    split_triple = {
        "building_limits": input.building_limits.model_dump(),
        "height_plateaus": input.height_plateaus.model_dump(),
        "split": split.model_dump(),
    }
    doc = await save_split_triple(_DATABASE, project, split_triple)
    logging.debug("After save_split_triple")

    # Build output object
    return CreateSplitOutput.from_doc(doc)


@app.delete("/projects/{project}/splits/{id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_split(project: str, id: str) -> None:
    try:
        object_id = bson.ObjectId(id)
    except bson.errors.InvalidId as e:
        raise HTTPException(status_code=400, detail=str(e))

    deleted = await delete_split_triple(_DATABASE, project, object_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Split not found")


@app.delete("/projects/{project}/splits", status_code=fastapi.status.HTTP_200_OK)
async def delete_all_splits(project: str) -> dict[str, int]:
    num_deleted = await delete_all_split_triples(_DATABASE, project)
    return {"num_deleted": num_deleted}
