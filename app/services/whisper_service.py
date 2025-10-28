from __future__ import annotations

import asyncio
import tempfile
from dataclasses import dataclass
from threading import Lock
from typing import Any, Dict, Optional

import whisper

from app.config import get_settings


@dataclass(frozen=True)
class TranscriptionResult:
    """Structured transcription payload returned by Whisper."""

    text: str
    language: Optional[str]
    raw: Dict[str, Any]


_model_cache: Dict[str, Any] = {}
_model_lock = Lock()


def _get_or_load_model(model_name: str):
    with _model_lock:
        if model_name not in _model_cache:
            _model_cache[model_name] = whisper.load_model(model_name)
    return _model_cache[model_name]


def _transcribe_sync(file_bytes: bytes, language: Optional[str], model_name: str) -> TranscriptionResult:
    model = _get_or_load_model(model_name)
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        result = model.transcribe(tmp.name, language=language)

    text = result.get("text", "").strip()
    language_detected = result.get("language") or language
    return TranscriptionResult(text=text, language=language_detected, raw=result)


async def transcribe_audio(
    file_bytes: bytes,
    *,
    language: Optional[str] = None,
) -> TranscriptionResult:
    """Run Whisper transcription asynchronously using the configured model size."""

    if not file_bytes:
        raise ValueError("Uploaded audio file is empty.")

    settings = get_settings()
    model_name = settings.whisper_model_size

    try:
        return await asyncio.to_thread(_transcribe_sync, file_bytes, language, model_name)
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Failed to transcribe audio.") from exc
