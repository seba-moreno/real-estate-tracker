from __future__ import annotations

from datetime import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.persistence.sql_alchemy.database import Base
from app.infrastructure.persistence.sql_alchemy.models.user_model import UserModel
from app.infrastructure.persistence.sql_alchemy.repositories.user_repository import (
    UserRepository,
)


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture
def in_memory_db(monkeypatch):
    """
    Creates an isolated in-memory SQLite DB and patches the SessionLocal used
    by SqlAlchemyRepository so UserRepository uses this DB exclusively.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )

    # Patch the SessionLocal used inside SqlAlchemyRepository
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository.SessionLocal",
        TestSessionLocal,
        raising=False,
    )

    yield TestSessionLocal

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repo(in_memory_db):
    return UserRepository()


# ---------------------------------------------------------------------
# Helper: Insert a user directly
# ---------------------------------------------------------------------


def _seed_user(
    SessionLocal, *, username: str, password: str, email: str | None, created_at=None
):
    if created_at is None:
        created_at = datetime.now()

    with SessionLocal() as db:
        row = UserModel(
            username=username,
            password_hash=password,
            email=email,
            is_active=True,
            created_at=created_at,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id, row


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------


def test_get_by_username_returns_user(repo: UserRepository, in_memory_db):
    SessionLocal = in_memory_db

    # Seed user
    uid, row = _seed_user(
        SessionLocal,
        username="alice",
        password="hashedpw",
        email="alice@example.com",
    )

    # Execute
    result = repo.get_by_username("alice")

    assert result is not None
    assert result.id == uid
    assert result.username == "alice"
    assert result.password_hash == "hashedpw"
    assert result.email == "alice@example.com"
    assert result.is_active is True


def test_get_by_username_returns_none_when_missing(repo: UserRepository):
    result = repo.get_by_username("who-does-not-exist")
    assert result is None


def test_get_by_username_is_case_sensitive(repo: UserRepository, in_memory_db):
    """
    SQLAlchemy's `==` is case-sensitive on SQLite.
    It's worth documenting this behavior.
    """
    SessionLocal = in_memory_db

    _seed_user(SessionLocal, username="alice", password="x", email=None)

    assert repo.get_by_username("alice") is not None
    assert repo.get_by_username("ALICE") is None  # case-sensitive match
