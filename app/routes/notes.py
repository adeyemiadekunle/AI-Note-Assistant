from typing import List

from fastapi import APIRouter, HTTPException, Request, status

from app.models.note_model import NoteCreate, NoteRead, NoteUpdate
from app.services import note_service

router = APIRouter(prefix="/api/notes", tags=["notes"])


def _require_user(request: Request):
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    return user


@router.get("/", response_model=List[NoteRead])
async def list_notes(request: Request) -> List[NoteRead]:
    user = _require_user(request)
    return await note_service.list_notes(user.id)


@router.post("/", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def create_note(request: Request, note: NoteCreate) -> NoteRead:
    user = _require_user(request)
    return await note_service.create_note(note, user.id)


@router.get("/{note_id}", response_model=NoteRead)
async def get_note(request: Request, note_id: str) -> NoteRead:
    user = _require_user(request)
    try:
        note = await note_service.get_note(note_id, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=NoteRead)
async def update_note(request: Request, note_id: str, update: NoteUpdate) -> NoteRead:
    user = _require_user(request)
    try:
        note = await note_service.update_note(note_id, update, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(request: Request, note_id: str) -> None:
    user = _require_user(request)
    try:
        deleted = await note_service.delete_note(note_id, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
