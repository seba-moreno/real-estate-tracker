from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.persistence.sql_alchemy.database import Base
from app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository import (
    SqlAlchemyRepository,
)

# Ensure database module doesn't exit if imported elsewhere without env
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")


# -----------------------------
# Test Model & Domain
# -----------------------------


class MockModel(Base):
    __tablename__ = "test_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Keep non-null to allow integrity error tests for rollback paths
    name = Column(String(100), nullable=False)
    value = Column(Integer, nullable=False)


@dataclass
class MockDomain:
    id: Optional[int]
    name: str
    value: int


def default_to_model(d: MockDomain) -> MockModel:
    return MockModel(id=d.id, name=d.name, value=d.value)


def default_to_domain(m: MockModel) -> MockDomain:
    return MockDomain(id=m.id, name=m.name, value=m.value)


# -----------------------------
# Fixtures
# -----------------------------


@pytest.fixture
def in_memory_sessionlocal(monkeypatch):
    """
    Patch the SessionLocal used by SqlAlchemyRepository to point to an in-memory DB,
    reusing the same connection across sessions (StaticPool).
    """
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )

    # Patch the specific symbol used inside the repository module
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository.SessionLocal",
        TestSessionLocal,
        raising=False,
    )

    yield

    # Cleanup metadata for isolation (not strictly necessary for :memory: + StaticPool per test)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repo(in_memory_sessionlocal) -> SqlAlchemyRepository[MockDomain, MockModel]:
    """Repository instance bound to the in-memory DB via patched SessionLocal."""
    return SqlAlchemyRepository[MockDomain, MockModel](
        model=MockModel,
        to_model=default_to_model,
        to_domain=default_to_domain,
    )


def make_domain(
    name: str = "item", value: int = 1, id: int | None = None
) -> MockDomain:
    return MockDomain(id=id, name=name, value=value)


# -----------------------------
# Tests: CREATE
# -----------------------------


def test_create_persists_and_returns_domain(
    repo: SqlAlchemyRepository[MockDomain, MockModel],
):
    created = repo.create(make_domain("alpha", 10))
    assert isinstance(created, MockDomain)
    assert created.id is not None
    assert created.name == "alpha"
    assert created.value == 10

    # Verify persisted via repository read APIs
    fetched = repo.get_by_id(created.id)
    assert fetched == created

    all_items = repo.get_all()
    assert len(all_items) == 1
    assert all_items[0] == created


def test_create_rollback_on_integrity_error(
    repo: SqlAlchemyRepository[MockDomain, MockModel],
):
    # name is NOT NULL; setting to None should raise and rollback
    with pytest.raises(SQLAlchemyError):
        repo.create(MockDomain(id=None, name=None, value=5))  # type: ignore[arg-type]

    # Should not have persisted anything
    assert repo.get_all() == []


# -----------------------------
# Tests: GET
# -----------------------------


def test_get_all_empty_initially(repo: SqlAlchemyRepository[MockDomain, MockModel]):
    assert repo.get_all() == []


def test_get_all_returns_all_in_domain_shape(
    repo: SqlAlchemyRepository[MockDomain, MockModel],
):
    a = repo.create(make_domain("a", 1))
    b = repo.create(make_domain("b", 2))

    items = repo.get_all()
    # Order not guaranteed; compare as sets on tuples
    assert {(x.id, x.name, x.value) for x in items} == {
        (a.id, "a", 1),
        (b.id, "b", 2),
    }
    assert all(isinstance(x, MockDomain) for x in items)


def test_get_by_id_found_and_missing(repo: SqlAlchemyRepository[MockDomain, MockModel]):
    created = repo.create(make_domain("x", 99))
    assert repo.get_by_id(created.id) == created

    assert repo.get_by_id(999999) is None


# -----------------------------
# Tests: UPDATE
# -----------------------------


def test_update_existing_overwrites_fields_and_keeps_id(
    repo: SqlAlchemyRepository[MockDomain, MockModel],
):
    created = repo.create(make_domain("start", 1))

    updated_payload = make_domain(name="changed", value=42)  # id ignored by repo
    updated = repo.update(created.id, updated_payload)

    assert updated.id == created.id
    assert updated.name == "changed"
    assert updated.value == 42

    # Read back
    fetched = repo.get_by_id(created.id)
    assert fetched == updated


def test_update_nonexistent_raises_value_error(
    repo: SqlAlchemyRepository[MockDomain, MockModel],
):
    with pytest.raises(ValueError) as exc:
        repo.update(12345, make_domain("nope", 0))
    assert "not found" in str(exc.value)


def test_update_rollback_on_integrity_error_preserves_previous_state(
    repo: SqlAlchemyRepository[MockDomain, MockModel],
):
    created = repo.create(make_domain("ok", 7))

    # Attempt to update to an invalid state (name=None violates NOT NULL)
    with pytest.raises(SQLAlchemyError):
        repo.update(created.id, MockDomain(id=None, name=None, value=8))  # type: ignore[arg-type]

    # Entity should remain unchanged after failed transaction
    fetched = repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "ok"
    assert fetched.value == 7


# -----------------------------
# Tests: DELETE
# -----------------------------


def test_delete_existing_returns_true_and_removes_entity(
    repo: SqlAlchemyRepository[MockDomain, MockModel],
):
    created = repo.create(make_domain("victim", 13))

    result = repo.delete(created.id)
    assert result is True
    assert repo.get_by_id(created.id) is None
    assert repo.get_all() == []

    # idempotent-ish: deleting again returns False
    assert repo.delete(created.id) is False


def test_delete_missing_returns_false(
    repo: SqlAlchemyRepository[MockDomain, MockModel],
):
    assert repo.delete(9999) is False


# -----------------------------
# Tests: Mapping functions
# -----------------------------


def test_default_mappers_round_trip(repo: SqlAlchemyRepository[MockDomain, MockModel]):
    original = make_domain("roundtrip", 21)
    stored = repo.create(original)
    fetched = repo.get_by_id(stored.id)
    assert fetched == stored
