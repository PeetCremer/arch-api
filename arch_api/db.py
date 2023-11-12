from collections.abc import Mapping
from typing import Any

import bson
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

MAX_PAGE_SIZE = 10


def get_db(db_url: str) -> AsyncIOMotorDatabase:
    """
    Connects to MongoDB using motor and creates a "splits" collection in the "arch-api" database.

    Args:
        db_url (str): A MongoDB connection string, e.g. mongodb://localhost:27017

    Returns:
        AsyncIOMotorDatabase: A motor database handle to interact with the DB
    """
    client = AsyncIOMotorClient(db_url)
    db = client["arch-api"]  # setup mongodb database
    _collection = db["splits"]  # setup mongodb collection
    return db


async def save_split_triple(db: AsyncIOMotorDatabase, project: str, split_triple: dict[str, Any]) -> Mapping[str, Any]:
    """
    Saves a split triple consisting of building_limits, height_plateaus, and splits to the database.
    Args:
        db (AsyncIOMotorDatabase): Database handle
        project (str): Project name
        split_triple (dict): Dict containing the split triple. Keys are "building_limits", "height_plateaus", and "split"
    Returns:
        Mapping[str, Any]: Document representing the saved split triple, containing also id and project
    """
    # insert
    collection: AsyncIOMotorCollection = db["splits"]
    res = await collection.insert_one({"project": project, **split_triple})
    # fetch inserted document
    doc = await get_split_triple(db, project, res.inserted_id)
    assert doc is not None
    return doc


async def get_split_triple(db: AsyncIOMotorDatabase, project: str, id: bson.ObjectId) -> Mapping[str, Any] | None:
    """
    Retrieves a saved split triple consisting of building_limits, height_plateaus, and splits from the database
    Args:
        db (AsyncIOMotorDatabase): Database handle
        project (str): Project name
        id (bson.ObjectId): bson ObjectId corresponding to the split triple
    Returns:
        Mapping[str, Any] | None: Document representing the saved split triple, containing also id and project, or None if there is no object with the given id
    """
    collection: AsyncIOMotorCollection = db["splits"]
    doc = await collection.find_one({"project": project, "_id": id})
    return doc


async def delete_split_triple(db: AsyncIOMotorDatabase, project: str, id: bson.ObjectId) -> bool:
    """
    Deletes a saved split triple by id from the database
    Args:
        db (AsyncIOMotorDatabase): Database handle
        project (str): Project name
        id (bson.ObjectId): bson ObjectId corresponding to the split triple
    Returns:
        bool: True if the split triple was deleted, False if there was no object with the given id
    """
    collection: AsyncIOMotorCollection = db["splits"]
    res = await collection.delete_one({"project": project, "_id": id})
    return res.deleted_count > 0


async def delete_all_split_triples(db: AsyncIOMotorDatabase, project: str) -> int:
    """
    Deletes all saved split triples for a given project from the database
    Args:
        db (AsyncIOMotorDatabase): Database handle
        project (str): Project name
    Returns:
        int: The number of deleted objects
    """
    collection: AsyncIOMotorCollection = db["splits"]
    res = await collection.delete_many({"project": project})
    return res.deleted_count


async def list_split_triples(db: AsyncIOMotorDatabase, project: str, skip: int, limit: int) -> list[Mapping[str, Any]]:
    """
    Lists saved split triples for a given project. Pagination can be achieved by using skip and limit.
    Args:
        db (AsyncIOMotorDatabase): Database handle
        project (str): Project name
        skip (int): Number of documents to skip in the cursor
        limit (int): Number of documents to return at the cursor position
    Returns:
        list[Mapping[str, Any]]: List of the split triples at the given cursor position
    """
    collection: AsyncIOMotorCollection = db["splits"]
    docs = await collection.find({"project": project}, skip=skip, limit=limit).to_list(length=MAX_PAGE_SIZE)
    return docs
