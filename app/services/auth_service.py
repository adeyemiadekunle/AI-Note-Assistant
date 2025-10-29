from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Dict, Tuple

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorCollection
from passlib.context import CryptContext

from app.config import get_settings
from app.database.mongodb import get_database
from app.models.user_model import TokenResponse, UserCreate, UserLogin, UserPublic


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""


class InvalidCredentialsError(Exception):
    """Raised when authentication fails."""


class AuthConfigurationError(Exception):
    """Raised when JWT configuration is missing."""


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_user_collection() -> AsyncIOMotorCollection:
    return get_database()["users"]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def _to_object_id(user_id: str) -> ObjectId | str:
    try:
        return ObjectId(user_id)
    except (InvalidId, TypeError):
        return user_id


def _build_public_user(document: Dict[str, Any]) -> UserPublic:
    return UserPublic(
        id=str(document.get("_id")),
        email=document["email"],
        full_name=document.get("full_name"),
    )


def create_access_token(user_id: Any, *, expires_minutes: int | None = None) -> str:
    settings = get_settings()
    secret = settings.jwt_secret
    if not secret:
        raise AuthConfigurationError("JWT secret is not configured.")

    expires_delta = timedelta(minutes=expires_minutes or settings.jwt_expire_minutes)
    expire = datetime.now(UTC) + expires_delta
    payload = {"sub": str(user_id), "exp": int(expire.timestamp())}
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


async def register_user(data: UserCreate) -> Tuple[str, UserPublic]:
    collection = get_user_collection()
    email = data.email.lower()

    existing = await collection.find_one({"email": email})
    if existing:
        raise UserAlreadyExistsError("Email is already registered.")

    now = datetime.now(UTC)
    hashed_password = hash_password(data.password)
    document: Dict[str, Any] = {
        "email": email,
        "hashed_password": hashed_password,
        "full_name": data.full_name,
        "created_at": now,
        "updated_at": now,
    }

    result = await collection.insert_one(document)
    document["_id"] = result.inserted_id

    token = create_access_token(document["_id"])
    return token, _build_public_user(document)


async def authenticate_user(data: UserLogin) -> Tuple[str, UserPublic]:
    collection = get_user_collection()
    email = data.email.lower()

    user = await collection.find_one({"email": email})
    if not user or not verify_password(data.password, user.get("hashed_password", "")):
        raise InvalidCredentialsError("Invalid email or password.")

    token = create_access_token(user["_id"])
    return token, _build_public_user(user)


async def get_user_by_id(user_id: str) -> Dict[str, Any] | None:
    collection = get_user_collection()
    return await collection.find_one({"_id": _to_object_id(user_id)})


async def get_user_from_token(token: str) -> UserPublic:
    settings = get_settings()
    secret = settings.jwt_secret
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT secret is not configured.",
        )

    try:
        payload = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
    except JWTError as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        ) from exc

    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    return _build_public_user(user)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    return await get_user_from_token(token)


def token_response(token: str, user: UserPublic) -> TokenResponse:
    return TokenResponse(access_token=token, user=user)
