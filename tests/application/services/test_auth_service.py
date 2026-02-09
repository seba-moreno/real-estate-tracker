import pytest
from datetime import timezone, datetime, timedelta
from fastapi import HTTPException

import app.application.services.auth_service as svc_mod
from app.core.domain.entities.user import User


class DummyLogger:
    def __init__(self):
        self.infos = []
        self.warnings = []
        self.exceptions = []

    def info(self, msg, *args, **kwargs):
        self.infos.append((msg, args, kwargs))

    def warning(self, msg, *args, **kwargs):
        self.warnings.append((msg, args, kwargs))

    def exception(self, msg, *args, **kwargs):
        self.exceptions.append((msg, args, kwargs))


class FakeRepo:
    """In-memory repo stub controlled by tests."""

    def __init__(self, users_by_username=None, fail_on_create=False):
        self.users_by_username = users_by_username or {}
        self.fail_on_create = fail_on_create
        self.created = []
        self.get_calls = []

    def get_by_username(self, username: str):
        self.get_calls.append(username)
        return self.users_by_username.get(username)

    def create(self, user: User):
        if self.fail_on_create:
            raise RuntimeError("DB failure")
        self.created.append(user)


@pytest.fixture
def logger(monkeypatch):
    dummy = DummyLogger()
    monkeypatch.setattr(svc_mod, "get_logger", lambda name: dummy)
    return dummy


@pytest.fixture
def fixed_time(monkeypatch):
    """
    Freeze time for deterministic 'expires_in' and timestamps in register().
    We patch the module's 'datetime' symbol which the service imports directly.
    """
    fixed_dt = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    class _DTShim:
        @staticmethod
        def now(tz=None):
            return fixed_dt

    monkeypatch.setattr(svc_mod, "datetime", _DTShim)
    return fixed_dt


def make_user(
    username="sebastian",
    is_active=True,
    password_hash="HASH",
    email="sebastian@example.com",
):
    return User(
        id=1,
        username=username,
        email=email,
        password_hash=password_hash,
        is_active=is_active,
        created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )


# ---------------------------
# login() tests
# ---------------------------


def test_login_success(monkeypatch, logger, fixed_time):
    repo = FakeRepo(users_by_username={"sebastian": make_user()})

    # Capture sub passed into create_access_token
    captured = {}

    def fake_create_access_token(sub: str) -> str:
        captured["sub"] = sub
        return "TOKEN123"

    monkeypatch.setattr(svc_mod, "verify_password", lambda raw, hashed: True)
    monkeypatch.setattr(svc_mod, "create_access_token", fake_create_access_token)
    monkeypatch.setattr(svc_mod, "JWT_EXPIRE_MIN", 60)

    service = svc_mod.AuthService(repo, "User")

    token = service.login(svc_mod.LoginCredentials(username="sebastian", password="pw"))

    assert token.access_token == "TOKEN123"
    assert token.token_type == "Bearer"
    expected_exp = int((fixed_time + timedelta(minutes=60)).timestamp())
    assert token.expires_in == expected_exp

    assert captured["sub"] == "sebastian"
    # No warnings on success
    assert not logger.warnings
    # Repo was called exactly once with the username
    assert repo.get_calls == ["sebastian"]


def test_login_user_not_found(monkeypatch, logger):
    repo = FakeRepo(users_by_username={})
    service = svc_mod.AuthService(repo, "User")

    with pytest.raises(HTTPException) as ei:
        service.login(svc_mod.LoginCredentials(username="ghost", password="pw"))

    assert ei.value.status_code == 401
    assert ei.value.detail == "Invalid credentials"

    # Warning logged with username (stored inside kwargs["extra"])
    assert any(
        ("Login attempt failed" in msg)
        and kw.get("extra", {}).get("username") == "ghost"
        for (msg, _args, kw) in logger.warnings
    )
    assert repo.get_calls == ["ghost"]


def test_login_wrong_password(monkeypatch, logger):
    repo = FakeRepo(users_by_username={"sebastian": make_user()})
    monkeypatch.setattr(svc_mod, "verify_password", lambda raw, hashed: False)

    service = svc_mod.AuthService(repo, "User")

    with pytest.raises(HTTPException) as ei:
        service.login(svc_mod.LoginCredentials(username="sebastian", password="bad"))

    assert ei.value.status_code == 401
    assert ei.value.detail == "Invalid credentials"

    assert any(
        ("Login attempt failed" in msg)
        and kw.get("extra", {}).get("username") == "sebastian"
        for (msg, _args, kw) in logger.warnings
    )
    assert repo.get_calls == ["sebastian"]


def test_login_inactive_user(monkeypatch, logger):
    repo = FakeRepo(users_by_username={"sebastian": make_user(is_active=False)})
    monkeypatch.setattr(svc_mod, "verify_password", lambda raw, hashed: True)

    service = svc_mod.AuthService(repo, "User")

    with pytest.raises(HTTPException) as ei:
        service.login(svc_mod.LoginCredentials(username="sebastian", password="pw"))

    assert ei.value.status_code == 401
    assert ei.value.detail == "User is inactive"

    assert any(
        ("user is inactive" in msg.lower())
        and kw.get("extra", {}).get("username") == "sebastian"
        for (msg, _args, kw) in logger.warnings
    )
    assert repo.get_calls == ["sebastian"]


# ---------------------------
# register() tests
# ---------------------------


def test_register_success(monkeypatch, logger, fixed_time):
    repo = FakeRepo(users_by_username={}, fail_on_create=False)

    # Ensure we hash and store the hash
    monkeypatch.setattr(svc_mod, "hash_password", lambda raw: "HASHED!")
    service = svc_mod.AuthService(repo, "User")

    user_in = svc_mod.UserCreate(
        username="victoria",
        email="victoria@example.com",
        password="super-secret",
        is_active=True,
    )

    service.register(user_in)

    # Created exactly one user with hashed password and fixed timestamps
    assert len(repo.created) == 1
    created = repo.created[0]
    assert isinstance(created, User)
    assert created.username == "victoria"
    assert created.email == "victoria@example.com"
    assert created.password_hash == "HASHED!"
    assert created.is_active is True
    assert created.created_at == fixed_time
    assert created.updated_at == fixed_time

    # Logs around registration
    assert any(
        "Registering user" in msg and kw.get("extra", {}).get("username") == "victoria"
        for (msg, _a, kw) in logger.infos
    )
    assert any(
        "User registered successfully" in msg
        and kw.get("extra", {}).get("username") == "victoria"
        for (msg, _a, kw) in logger.infos
    )


def test_register_existing_username_raises_validationerror(monkeypatch, logger):
    existing = make_user(username="victoria")
    repo = FakeRepo(users_by_username={"victoria": existing})

    service = svc_mod.AuthService(repo, "User")

    user_in = svc_mod.UserCreate(
        username="victoria",
        email="whatever@example.com",
        password="pw",
        is_active=True,
    )

    with pytest.raises(svc_mod.ValidationError) as ei:
        service.register(user_in)

    assert "Username is already on use" in str(ei.value) or "already exists" in str(
        ei.value
    )

    # Warning logged for duplicate
    assert any(
        "username already exists" in msg.lower()
        and kw.get("extra", {}).get("username") == "victoria"
        for (msg, _a, kw) in logger.warnings
    )
    # No exception log for a controlled validation error
    assert not logger.exceptions


def test_register_db_failure_is_wrapped(monkeypatch, logger):
    repo = FakeRepo(users_by_username={}, fail_on_create=True)
    monkeypatch.setattr(svc_mod, "hash_password", lambda raw: "HASHED!")
    service = svc_mod.AuthService(repo, "User")

    user_in = svc_mod.UserCreate(
        username="juan",
        email="juan@example.com",
        password="pw",
        is_active=True,
    )

    with pytest.raises(svc_mod.PersistenceError) as ei:
        service.register(user_in)

    assert "Error registering user" in str(ei.value)
    assert logger.exceptions
