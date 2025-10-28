from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    transcript: str
    summary: str
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    mindmap: Dict[str, Any] = Field(default_factory=dict)


class NoteCreate(NoteBase):
    """Payload for creating a new note."""


class NoteUpdate(BaseModel):
    transcript: Optional[str] = None
    summary: Optional[str] = None
    actions: Optional[List[Dict[str, Any]]] = None
    topics: Optional[List[str]] = None
    mindmap: Optional[Dict[str, Any]] = None


class NoteRead(NoteBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
