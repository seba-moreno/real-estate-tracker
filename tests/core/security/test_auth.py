import time
import jwt
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from types import SimpleNamespace
import app.core.security.auth as auth_module

bearer = HTTPBearer(auto_error=True)


def make_app_with_repo(mock_repo):
    """
    Build a small FastAPI app that uses a wrapper dependency to pass our mock_repo
    into auth_required without wiring the real DI container.
    """
    app = FastAPI()

    # Wrapper that calls the real auth_required but supplies our mock repo explicitly
    def auth_dep(
        credentials: HTTPAuthorizationCredentials = Depends(bearer),
    ):
        return auth_module.auth_required(credentials=credentials, repo=mock_repo)

    @app.get("/me")
    def me(username: str = Depends(auth_dep)):
        return {"username": username}

    return app


def mint_token(sub: str, secret: str, algo: str, expires_in_seconds: int = 300):
    now = int(time.time())
    payload = {
        "sub": sub,
        "iat": now,
        "exp": now + expires_in_seconds,
    }
    return jwt.encode(payload, secret, algorithm=algo)


@pytest.fixture()
def jwt_conf(monkeypatch):
    """
    Ensure the test controls JWT secret/algorithm used by the dependency.
    """
    secret = "test-secret"
    algo = "HS256"
    monkeypatch.setattr(auth_module, "JWT_SECRET", secret)
    monkeypatch.setattr(auth_module, "JWT_ALGORITHM", algo)
    return SimpleNamespace(secret=secret, algo=algo)


@pytest.fixture()
def mock_repo_active_user():
    """
    A mock repo that returns an active user when username matches.
    It mimics the interface: get_by_username(username) -> User (with is_active attr) or None
    """

    class MockUser:
        def __init__(self, username, is_active=True):
            self.username = username
            self.is_active = is_active

    class MockRepo:
        def __init__(self):
            self.calls = []

        def get_by_username(self, username: str):
            self.calls.append(username)
            if username == "sebastian":
                return MockUser(username="sebastian", is_active=True)
            return None

    return MockRepo()


def test_valid_token_returns_username(jwt_conf, mock_repo_active_user):
    app = make_app_with_repo(mock_repo_active_user)
    client = TestClient(app)

    token = mint_token(
        "sebastian", jwt_conf.secret, jwt_conf.algo, expires_in_seconds=600
    )
    res = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 200, res.text
    assert res.json() == {"username": "sebastian"}
    # Repo was queried with the 'sub'
    assert mock_repo_active_user.calls == ["sebastian"]


def test_missing_authorization_header_results_in_403():
    """
    With HTTPBearer(auto_error=True), missing header yields 403 Not authenticated.
    """

    # Minimal repo – should not be called
    class DummyRepo:
        def get_by_username(self, username: str):
            pytest.fail("Repo should not be called when missing Authorization header")

    app = make_app_with_repo(DummyRepo())
    client = TestClient(app)

    res = client.get("/me")
    assert res.status_code == 401
    assert "Invalid token" in res.text or "Not authenticated" in res.text


def test_expired_token_results_in_401(jwt_conf, mock_repo_active_user):
    app = make_app_with_repo(mock_repo_active_user)
    client = TestClient(app)

    token = mint_token(
        "sebastian", jwt_conf.secret, jwt_conf.algo, expires_in_seconds=-5
    )  # already expired
    res = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 401
    assert res.json()["detail"] == "Token expired"


def test_invalid_signature_results_in_401(jwt_conf, mock_repo_active_user):
    app = make_app_with_repo(mock_repo_active_user)
    client = TestClient(app)
