from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

_client: Optional[AsyncIOMotorClient] = None


def get_client() -> AsyncIOMotorClient:
    settings = get_settings()
    if not settings.mongo_uri:
        raise RuntimeError("MONGO_URI is not configured.")

    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_uri)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    settings = get_settings()
    client = get_client()
    return client[settings.database_name]
