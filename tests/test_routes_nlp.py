from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.models.note_model import NoteRead
from app.routes import nlp as nlp_route
from app.services import auth_service

client = TestClient(app)
AUTH_HEADER = {"Authorization": "Bearer testtoken"}


def test_summarise_endpoint_returns_payload(monkeypatch) -> None:
    async def fake_generate_summary(transcript: str):
        return {
            "summary": "done",
            "actions": [{"task": "Test"}],
            "topics": ["Topic"],
            "transcript_length": len(transcript),
        }

    monkeypatch.setattr(nlp_route, "generate_summary", fake_generate_summary)
    monkeypatch.setattr(auth_service, "get_user_from_token", _stub_get_user_from_token)

    response = client.post("/api/summarise", json={"transcript": "hello"}, headers=AUTH_HEADER)

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "done"
    assert body["actions"] == [{"task": "Test"}]
    assert body["topics"] == ["Topic"]


def test_summarise_endpoint_handles_errors(monkeypatch) -> None:
    async def fake_generate_summary(_: str):
        raise ValueError("bad data")

    monkeypatch.setattr(nlp_route, "generate_summary", fake_generate_summary)
    monkeypatch.setattr(auth_service, "get_user_from_token", _stub_get_user_from_token)

    response = client.post("/api/summarise", json={"transcript": ""}, headers=AUTH_HEADER)

    assert response.status_code == 400
    assert response.json()["detail"] == "bad data"


async def _stub_get_user_from_token(token: str):
    assert token == "testtoken"
    return SimpleNamespace(id="user", email="user@example.com")


def test_mindmap_endpoint_returns_graph(monkeypatch) -> None:
    now = datetime.now(UTC)
    note = NoteRead(
        id="123",
        user_id="user",
        transcript="",
        summary="",
        actions=[{"task": "Task"}],
        topics=["Topic"],
        mindmap={},
        created_at=now,
        updated_at=now,
    )

    async def fake_get_note(note_id: str, user_id: str):
        assert note_id == "123"
        assert user_id == "user"
        return note

    monkeypatch.setattr(nlp_route.note_service, "get_note", fake_get_note)
    monkeypatch.setattr(auth_service, "get_user_from_token", _stub_get_user_from_token)

    response = client.get("/api/mindmap/123", headers=AUTH_HEADER)

    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data and "links" in data
    assert any(node["label"] == "Task" for node in data["nodes"])


def test_mindmap_endpoint_handles_missing_note(monkeypatch) -> None:
    async def fake_get_note(_: str, __: str):
        return None

    monkeypatch.setattr(nlp_route.note_service, "get_note", fake_get_note)
    monkeypatch.setattr(auth_service, "get_user_from_token", _stub_get_user_from_token)

    response = client.get("/api/mindmap/unknown", headers=AUTH_HEADER)

    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"
