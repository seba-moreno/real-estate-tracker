from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.domain.entities.concept import Concept
from app.infrastructure.persistence.sql_alchemy.database import Base
from app.infrastructure.persistence.sql_alchemy.repositories.concept_repository import (
    ConceptRepository,
)


@pytest.fixture
def in_memory_db(monkeypatch):
    """
    Create an in-memory SQLite engine and patch the SessionLocal used by
    SqlAlchemyRepository so ConceptRepository uses this isolated DB.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
    )
    # Create tables for all models registered on Base
    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )

    # Patch the SessionLocal that SqlAlchemyRepository imports/uses internally
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository.SessionLocal",
        TestSessionLocal,
        raising=False,
    )

    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repo(in_memory_db):
    """A fresh ConceptRepository bound to the in-memory DB for each test."""
    return ConceptRepository()


def make_concept(
    name: str = "Concept A",
    is_ordinary: bool = True,
    periodicity: int | None = 1,
    description: str | None = "desc",
) -> Concept:
    return Concept(
        id=None,
        name=name,
        is_ordinary=is_ordinary,
        periodicity=periodicity,
        description=description,
    )


# -----------------------------
# Create + Get by id
# -----------------------------


def test_create_and_get_by_id(repo: ConceptRepository):
    created = repo.create(make_concept("Lease", True, 1, "Monthly lease"))
    assert created.id is not None
    assert created.name == "Lease"
    assert created.is_ordinary is True
    assert created.periodicity == 1
    assert created.description == "Monthly lease"

    fetched = repo.get_by_id(created.id)  # type: ignore[arg-type]
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Lease"


# -----------------------------
# Get all
# -----------------------------


def test_get_all_returns_all_rows(repo: ConceptRepository):
    # empty
    assert repo.get_all() == []

    c1 = repo.create(make_concept("A", True, None, None))
    c2 = repo.create(make_concept("B", False, 3, "x"))

    all_rows = repo.get_all()
    ids = sorted(c.id for c in all_rows if c.id is not None)
    assert len(all_rows) == 2
    assert ids == sorted([c1.id, c2.id])  # type: ignore[list-item]


# -----------------------------
# Update
# -----------------------------


def test_update_success(repo: ConceptRepository):
    created = repo.create(make_concept("Old", True, 1, "old"))
    updated_input = make_concept("New", False, 0, None)

    updated = repo.update(created.id, updated_input)  # type: ignore[arg-type]
    assert updated.id == created.id
    assert updated.name == "New"
    assert updated.is_ordinary is False
    assert updated.periodicity == 0
    assert updated.description is None

    # verify persisted
    again = repo.get_by_id(created.id)  # type: ignore[arg-type]
    assert again is not None
    assert again.name == "New"


def test_update_raises_when_missing(repo: ConceptRepository):
    with pytest.raises(ValueError) as exc:
        repo.update(9999, make_concept("X", True, None, None))
    assert "ConceptModel with id=9999 not found" in str(exc.value)


# -----------------------------
# Delete
# -----------------------------


def test_delete_success_then_missing(repo: ConceptRepository):
    created = repo.create(make_concept("Del", True, 1, None))
    assert repo.delete(created.id) is True  # type: ignore[arg-type]
    # second time should return False
    assert repo.delete(created.id) is False  # type: ignore[arg-type]
