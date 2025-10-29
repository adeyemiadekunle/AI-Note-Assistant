from __future__ import annotations

from typing import Iterable

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.services import auth_service


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_paths: Iterable[str] | None = None) -> None:
        super().__init__(app)
        self.protected_paths = tuple(protected_paths or ())

    async def dispatch(self, request: Request, call_next) -> Response:
        if self._requires_auth(request.url.path):
            try:
                token = self._extract_token(request)
            except HTTPException as exc:
                return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

            try:
                user = await auth_service.get_user_from_token(token)
            except HTTPException as exc:
                return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

            request.state.user = user

        return await call_next(request)

    def _requires_auth(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self.protected_paths)

    @staticmethod
    def _extract_token(request: Request) -> str:
        header = request.headers.get("Authorization")
        if not header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated."
            )

        parts = header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header."
            )

        return parts[1]
