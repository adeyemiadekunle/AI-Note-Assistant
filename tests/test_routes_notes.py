from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.models.note_model import NoteRead
from app.routes import notes as notes_route
from app.services import auth_service

client = TestClient(app)
AUTH_HEADER = {"Authorization": "Bearer testtoken"}


async def _stub_get_user_from_token(token: str):
    assert token == "testtoken"
    return SimpleNamespace(id="user", email="user@example.com")


def test_list_notes_requires_auth() -> None:
    response = client.get("/api/notes")
    assert response.status_code == 401


def test_list_notes_returns_payload(monkeypatch) -> None:
    async def fake_list_notes(user_id: str):
        assert user_id == "user"
        return []

    monkeypatch.setattr(notes_route.note_service, "list_notes", fake_list_notes)
    monkeypatch.setattr(auth_service, "get_user_from_token", _stub_get_user_from_token)

    response = client.get("/api/notes", headers=AUTH_HEADER)

    assert response.status_code == 200
    assert response.json() == []


def test_create_note_injects_user(monkeypatch) -> None:
    now = datetime.now(UTC)
    note = NoteRead(
        id="1",
        user_id="user",
        transcript="t",
        summary="s",
        actions=[],
        topics=[],
        mindmap={},
        created_at=now,
        updated_at=now,
    )

    async def fake_create_note(payload, user_id: str):
        assert user_id == "user"
        assert payload.transcript == "t"
        return note

    monkeypatch.setattr(notes_route.note_service, "create_note", fake_create_note)
    monkeypatch.setattr(auth_service, "get_user_from_token", _stub_get_user_from_token)

    response = client.post(
        "/api/notes",
        headers=AUTH_HEADER,
        json={"transcript": "t", "summary": "s", "actions": [], "topics": [], "mindmap": {}},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == "user"
    assert body["id"] == "1"
