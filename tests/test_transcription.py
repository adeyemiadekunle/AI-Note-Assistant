import pytest

from app.config import get_settings
from app.services import whisper_service


@pytest.mark.asyncio
async def test_transcribe_audio_requires_non_empty_bytes() -> None:
    with pytest.raises(ValueError):
        await whisper_service.transcribe_audio(b"")


@pytest.mark.asyncio
async def test_transcribe_audio_uses_sync_transcriber(monkeypatch) -> None:
    captured = {}

    def fake_transcribe(file_bytes: bytes, language: str | None, model_name: str):
        captured["args"] = (file_bytes, language, model_name)
        return whisper_service.TranscriptionResult(
            text="Fake transcript",
            language=language or "en",
            raw={"text": "Fake transcript"},
        )

    monkeypatch.setattr(whisper_service, "_transcribe_sync", fake_transcribe)

    result = await whisper_service.transcribe_audio(b"audio-bytes", language="en")

    assert result.text == "Fake transcript"
    assert captured["args"] == (b"audio-bytes", "en", get_settings().whisper_model_size)
