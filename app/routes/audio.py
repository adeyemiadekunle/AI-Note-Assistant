from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.whisper_service import TranscriptionResult, transcribe_audio

router = APIRouter(prefix="/api", tags=["audio"])


class TranscriptionResponse(BaseModel):
    transcript: str
    language: str | None


@router.post("/upload-audio", response_model=TranscriptionResponse)
async def upload_audio(
    file: UploadFile = File(...),
    language: str | None = None,
) -> TranscriptionResponse:
    contents = await file.read()
    try:
        result: TranscriptionResult = await transcribe_audio(contents, language=language)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return TranscriptionResponse(transcript=result.text, language=result.language)
