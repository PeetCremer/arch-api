from collections.abc import Mapping
from typing import Any

import bson
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase


def get_db(db_url: str) -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(db_url)
    db = client["arch-api"]  # setup mongodb database
    _collection = db["splits"]  # setup mongodb collection
    return db


async def save_split(db: AsyncIOMotorDatabase, project: str, split: dict[str, Any]) -> Mapping[str, Any]:
    # insert
    collection: AsyncIOMotorCollection = db["splits"]
    res = await collection.insert_one({"project": project, "split": split})
    # fetch inserted document
    doc = await get_split(db, project, res.inserted_id)
    assert doc is not None
    return doc


async def get_split(db: AsyncIOMotorDatabase, project: str, id: bson.ObjectId) -> Mapping[str, Any] | None:
    collection: AsyncIOMotorCollection = db["splits"]
    doc = await collection.find_one({"project": project, "_id": id})
    return doc


async def delete_split(db: AsyncIOMotorDatabase, project: str, id: bson.ObjectId) -> bool:
    collection: AsyncIOMotorCollection = db["splits"]
    res = await collection.delete_one({"project": project, "_id": id})
    return res.deleted_count > 0
