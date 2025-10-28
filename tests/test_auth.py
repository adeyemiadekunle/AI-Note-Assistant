from __future__ import annotations

from typing import Any, Dict

from bson import ObjectId
from fastapi.testclient import TestClient
import pytest

from app.main import app
import app.routes.auth as auth_route
from app.services import auth_service

client = TestClient(app)


class InMemoryCollection:
    def __init__(self) -> None:
        self._documents: Dict[str, Dict[str, Any]] = {}

    async def find_one(self, query: Dict[str, Any]) -> Dict[str, Any] | None:
        if "email" in query:
            document = self._documents.get(query["email"])
            return dict(document) if document else None

        if "_id" in query:
            for document in self._documents.values():
                if document.get("_id") == query["_id"]:
                    return dict(document)
        return None

    async def insert_one(self, document: Dict[str, Any]):
        doc_copy = dict(document)
        if "_id" not in doc_copy:
            doc_copy["_id"] = ObjectId()
        self._documents[doc_copy["email"]] = doc_copy

        class Result:
            def __init__(self, inserted_id: Any) -> None:
                self.inserted_id = inserted_id

        return Result(doc_copy["_id"])


class _TestSettings:
    jwt_secret = "secret"
    jwt_algorithm = "HS256"
    jwt_expire_minutes = 60


@pytest.fixture
def patched_auth_dependencies(monkeypatch):
    store = InMemoryCollection()
    monkeypatch.setattr(auth_service, "get_user_collection", lambda: store)
    monkeypatch.setattr(auth_service, "get_settings", lambda: _TestSettings())
    return store


def test_signup_creates_user(patched_auth_dependencies):
    response = client.post(
        "/api/auth/signup",
        json={"email": "user@example.com", "password": "Password123", "full_name": "User"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "user@example.com"
    assert "access_token" in body


def test_signup_rejects_duplicate_email(patched_auth_dependencies):
    client.post(
        "/api/auth/signup",
        json={"email": "user@example.com", "password": "Password123", "full_name": "User"},
    )

    response = client.post(
        "/api/auth/signup",
        json={"email": "user@example.com", "password": "Password456", "full_name": "Other"},
    )

    assert response.status_code == 409


def test_login_returns_token(monkeypatch, patched_auth_dependencies):
    # Seed user directly to simulate prior signup
    store = patched_auth_dependencies
    password_hash = auth_service.hash_password("Password123")
    store._documents["user@example.com"] = {
        "_id": ObjectId(),
        "email": "user@example.com",
        "hashed_password": password_hash,
        "full_name": "User",
    }

    response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "Password123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["user"]["email"] == "user@example.com"


def test_login_rejects_invalid_credentials(patched_auth_dependencies):
    response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "wrong"},
    )

    assert response.status_code == 401


def test_me_endpoint_requires_valid_token(monkeypatch, patched_auth_dependencies):
    store = patched_auth_dependencies
    password_hash = auth_service.hash_password("Password123")
    user_id = ObjectId()
    store._documents["user@example.com"] = {
        "_id": user_id,
        "email": "user@example.com",
        "hashed_password": password_hash,
        "full_name": "User",
    }

    token = auth_service.create_access_token(user_id)

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "user@example.com"
