from fastapi import FastAPI

from app.middleware.auth_middleware import AuthMiddleware
from app.routes import audio, auth, nlp, notes

app = FastAPI(title="AI Note-Taking Assistant API")

app.add_middleware(AuthMiddleware, protected_paths=("/api/notes", "/api/mindmap", "/api/summarise"))

app.include_router(audio.router)
app.include_router(notes.router)
app.include_router(auth.router)
app.include_router(nlp.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
