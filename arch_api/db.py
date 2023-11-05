from collections.abc import Mapping
from typing import Any

import bson
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase


def get_db(db_url: str) -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(db_url)
    db = client["arch-api"]  # setup mongodb database
    _collection = db["splits"]  # setup mongodb collection
    return db


async def save_split_triple(db: AsyncIOMotorDatabase, project: str, split_triple: dict[str, Any]) -> Mapping[str, Any]:
    # insert
    collection: AsyncIOMotorCollection = db["splits"]
    res = await collection.insert_one({"project": project, **split_triple})
    # fetch inserted document
    doc = await get_split_triple(db, project, res.inserted_id)
    assert doc is not None
    return doc


async def get_split_triple(db: AsyncIOMotorDatabase, project: str, id: bson.ObjectId) -> Mapping[str, Any] | None:
    collection: AsyncIOMotorCollection = db["splits"]
    doc = await collection.find_one({"project": project, "_id": id})
    return doc


async def delete_split_triple(db: AsyncIOMotorDatabase, project: str, id: bson.ObjectId) -> bool:
    collection: AsyncIOMotorCollection = db["splits"]
    res = await collection.delete_one({"project": project, "_id": id})
    return res.deleted_count > 0


async def delete_all_split_triples(db: AsyncIOMotorDatabase, project: str) -> int:
    collection: AsyncIOMotorCollection = db["splits"]
    res = await collection.delete_many({"project": project})
    return res.deleted_count
