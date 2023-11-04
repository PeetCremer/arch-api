import logging
import os
from typing import Any

import bson
import fastapi
import uvicorn
from arch_api.db import delete_split_triple, get_db, get_split_triple, save_split_triple
from arch_api.models.io import SplitInput, SplitOutput
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

load_dotenv()
logging.basicConfig(level=os.environ.get("LOG_LEVEL", logging.DEBUG))

app = fastapi.FastAPI(
    title="Architecture API (arch-api)",
    description=(
        "Consumes building limits and height plateaus, splits up the building limits"
        "according to the height plateaus, and stores these three entities persistently"
    ),
)

database = get_db(os.environ["MONGODB_URL"])


# TODO fix this
async def pydantic_validation_error_handler(_request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        content={"message": f"Oops! {str(exc)} did something. There goes a rainbow..."},
    )


app.add_exception_handler(ValidationError, pydantic_validation_error_handler)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"health": "OK"}


# TODO create a project string length middleware


@app.get("/projects/{project}/splits/{id}")
async def get_split_byid(project: str, id: str) -> dict[str, Any]:
    try:
        object_id = bson.ObjectId(id)
    except bson.errors.InvalidId as e:
        raise HTTPException(status_code=400, detail=str(e))

    doc = await get_split_triple(database, project, object_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Split not found")
    doc = dict(doc)
    # unwrap ObjectId before returning
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@app.post("/projects/{project}/splits", status_code=fastapi.status.HTTP_201_CREATED)
async def create_split(project: str, input: SplitInput) -> SplitOutput:
    # TODO make bad input (pydantic validation error) return 400
    # TODO create a proper split. For now, we just copy the height_plateaus
    logging.debug("Processing split")
    split = input.height_plateaus

    # Persist the split
    logging.debug("Before save_split")
    split_triple = {
        "building_limits": input.building_limits.model_dump(),
        "height_plateaus": input.height_plateaus.model_dump(),
        "split": split.model_dump(),
    }
    doc = await save_split_triple(database, project, split_triple)
    logging.debug("After save_split")

    # Build output object
    doc = dict(doc)

    return SplitOutput(
        project=project,
        id=str(doc["_id"]),
        building_limits=doc["building_limits"],
        height_plateaus=doc["height_plateaus"],
        split=doc["split"],
    )


@app.delete("/projects/{project}/splits/{id}", status_code=fastapi.status.HTTP_204_NO_CONTENT)
async def delete_split_byid(project: str, id: str) -> None:
    try:
        object_id = bson.ObjectId(id)
    except bson.errors.InvalidId as e:
        raise HTTPException(status_code=400, detail=str(e))

    deleted = await delete_split_triple(database, project, object_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Split not found")


if __name__ == "__main__":
    uvicorn.run("app:app", host=os.environ["UVICORN_HOST"], port=8000, reload=True)
