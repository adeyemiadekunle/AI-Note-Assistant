from fastapi.testclient import TestClient

from app.main import app
import app.routes.audio as audio_route
from app.services.whisper_service import TranscriptionResult

client = TestClient(app)


def test_upload_audio_returns_transcript(monkeypatch) -> None:
    async def fake_transcribe(data: bytes, language: str | None = None) -> TranscriptionResult:
        assert data == b"data"
        assert language == "en"
        return TranscriptionResult(text="hello", language="en", raw={})

    monkeypatch.setattr(audio_route, "transcribe_audio", fake_transcribe)

    response = client.post(
        "/api/upload-audio",
        files={"file": ("sample.wav", b"data", "audio/wav")},
        params={"language": "en"},
    )

    assert response.status_code == 200
    assert response.json() == {"transcript": "hello", "language": "en"}


def test_upload_audio_handles_client_error(monkeypatch) -> None:
    async def fake_transcribe(data: bytes, language: str | None = None):
        raise ValueError("bad audio")

    monkeypatch.setattr(audio_route, "transcribe_audio", fake_transcribe)

    response = client.post(
        "/api/upload-audio",
        files={"file": ("sample.wav", b"", "audio/wav")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "bad audio"


def test_upload_audio_handles_server_error(monkeypatch) -> None:
    async def fake_transcribe(data: bytes, language: str | None = None):
        raise RuntimeError("failure")

    monkeypatch.setattr(audio_route, "transcribe_audio", fake_transcribe)

    response = client.post(
        "/api/upload-audio",
        files={"file": ("sample.wav", b"data", "audio/wav")},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "failure"
