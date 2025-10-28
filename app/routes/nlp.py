from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.models.note_model import NoteRead
from app.services import note_service
from app.services.mindmap_service import build_mindmap
from app.services.nlp_service import generate_summary

router = APIRouter(prefix="/api", tags=["nlp"])


def _require_user(request: Request):
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    return user


class SummariseRequest(BaseModel):
    transcript: str


class SummariseResponse(BaseModel):
    summary: str
    actions: List[Dict[str, Any]]
    topics: List[str]
    transcript_length: int


@router.post("/summarise", response_model=SummariseResponse)
async def summarise(request: SummariseRequest) -> SummariseResponse:
    try:
        result = await generate_summary(request.transcript)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return SummariseResponse.model_validate(result)


@router.get("/mindmap/{note_id}")
async def get_mindmap(request: Request, note_id: str) -> Dict[str, List[Dict[str, str]]]:
    user = _require_user(request)
    try:
        note: NoteRead | None = await note_service.get_note(note_id, user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    return build_mindmap(note.actions, note.topics)
