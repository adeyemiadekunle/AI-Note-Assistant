from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument

from app.database.mongodb import get_database
from app.models.note_model import NoteCreate, NoteRead, NoteUpdate

_COLLECTION_NAME = "notes"


def _collection() -> AsyncIOMotorCollection:
    return get_database()[_COLLECTION_NAME]


def _normalize(document: Dict[str, Any]) -> NoteRead:
    payload = document.copy()
    payload["id"] = str(payload.pop("_id"))
    return NoteRead.model_validate(payload)


def _object_id(note_id: str) -> ObjectId:
    try:
        return ObjectId(note_id)
    except (InvalidId, TypeError) as exc:
        raise ValueError("Invalid note id") from exc


async def list_notes(user_id: str) -> List[NoteRead]:
    notes: List[NoteRead] = []
    cursor = _collection().find({"user_id": user_id}).sort("created_at", -1)
    async for document in cursor:
        notes.append(_normalize(document))
    return notes


async def create_note(note: NoteCreate, user_id: str) -> NoteRead:
    now = datetime.utcnow()
    payload = note.model_dump()
    payload["user_id"] = user_id
    payload["created_at"] = now
    payload["updated_at"] = now
    result = await _collection().insert_one(payload)
    payload["_id"] = result.inserted_id
    return _normalize(payload)


async def get_note(note_id: str, user_id: Optional[str] = None) -> Optional[NoteRead]:
    query: Dict[str, Any] = {"_id": _object_id(note_id)}
    if user_id:
        query["user_id"] = user_id

    document = await _collection().find_one(query)
    if not document:
        return None
    return _normalize(document)


async def update_note(note_id: str, update: NoteUpdate, user_id: str) -> Optional[NoteRead]:
    update_data = update.model_dump(exclude_unset=True)
    if not update_data:
        return await get_note(note_id, user_id)

    update_data["updated_at"] = datetime.utcnow()
    result = await _collection().find_one_and_update(
        {"_id": _object_id(note_id), "user_id": user_id},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )
    return _normalize(result) if result else None


async def delete_note(note_id: str, user_id: str) -> bool:
    result = await _collection().delete_one({"_id": _object_id(note_id), "user_id": user_id})
    return result.deleted_count == 1
