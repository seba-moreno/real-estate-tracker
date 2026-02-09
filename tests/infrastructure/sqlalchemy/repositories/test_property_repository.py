from __future__ import annotations

import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.domain.entities.property import Property
from app.infrastructure.persistence.sql_alchemy.database import Base
from app.infrastructure.persistence.sql_alchemy.repositories.property_repository import (
    PropertyRepository,
)
from sqlalchemy.exc import SQLAlchemyError


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------


def make_domain(
    location="Main St 1",
    area=50,
    valuation=Decimal("100000.00"),
    details="test details",
) -> Property:
    return Property(
        id=None,
        location=location,
        area=area,
        valuation=valuation,
        details=details,
    )


# --------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------


@pytest.fixture
def in_memory_db(monkeypatch):
    """
    Creates an in-memory SQLite DB and patches SessionLocal used by
    SqlAlchemyRepository so PropertyRepository uses this DB.
    """
    engine = create_engine(
        "sqlite:///:memory:", future=True, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )

    # Patch SessionLocal symbol used by SqlAlchemyRepository
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository.SessionLocal",
        TestSessionLocal,
        raising=False,
    )

    yield TestSessionLocal

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repo(in_memory_db):
    return PropertyRepository()


# --------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------


def test_create_and_get_by_id(repo: PropertyRepository):
    created = repo.create(make_domain("A", 10, Decimal("111.11"), "Nice"))
    assert created.id is not None
    assert created.location == "A"
    assert created.area == 10
    assert created.valuation == Decimal("111.11")
    assert created.details == "Nice"

    fetched = repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.location == "A"


def test_get_by_id_missing_returns_none(repo: PropertyRepository):
    assert repo.get_by_id(999999) is None


def test_get_all_empty(repo: PropertyRepository):
    assert repo.get_all() == []


def test_get_all_after_creates(repo: PropertyRepository):
    a = repo.create(make_domain("A", 10, Decimal("1.00"), None))
    b = repo.create(make_domain("B", None, Decimal("2.00"), "x"))

    rows = repo.get_all()
    assert len(rows) == 2
    names = {r.location for r in rows}
    assert names == {"A", "B"}


def test_update_success(repo: PropertyRepository):
    created = repo.create(make_domain("Old", 20, Decimal("50.00"), "desc"))
    assert created.id is not None

    updated_input = make_domain("New", 99, Decimal("999.99"), None)

    updated = repo.update(created.id, updated_input)
    assert updated.id == created.id
    assert updated.location == "New"
    assert updated.area == 99
    assert updated.valuation == Decimal("999.99")
    assert updated.details is None

    fetched = repo.get_by_id(created.id)
    assert fetched.location == "New"


def test_update_missing_raises(repo: PropertyRepository):
    with pytest.raises(ValueError) as exc:
        repo.update(8888, make_domain("X", 1, Decimal("1.00"), None))

    assert "PropertyModel with id=8888 not found" in str(exc.value)


def test_delete_success_and_then_false(repo: PropertyRepository):
    created = repo.create(make_domain("DelMe", 10, Decimal("10.00"), None))
    assert created.id is not None

    assert repo.delete(created.id) is True
    assert repo.delete(created.id) is False  # already deleted


def test_create_rolls_back_on_sqlalchemy_error(repo: PropertyRepository, monkeypatch):
    """Force Session.commit() to throw SQLAlchemyError to verify rollback path."""

    class Boom(SQLAlchemyError):
        pass

    rolled_back = {"flag": False}

    def boom_commit(self: Session):
        raise Boom("commit failed")

    def rollback_spy(self: Session):
        rolled_back["flag"] = True

    monkeypatch.setattr(Session, "commit", boom_commit, raising=False)
    monkeypatch.setattr(Session, "rollback", rollback_spy, raising=False)

    with pytest.raises(Boom):
        repo.create(make_domain("Err", 1, Decimal("1.00"), None))

    assert rolled_back["flag"] is True


def test_update_rolls_back_on_sqlalchemy_error(repo: PropertyRepository, monkeypatch):
    class Boom(SQLAlchemyError):
        pass

    created = repo.create(make_domain("Old", 1, Decimal("1.00"), None))

    rolled_back = {"flag": False}

    def boom_commit(self: Session):
        raise Boom("commit failed")

    def rollback_spy(self: Session):
        rolled_back["flag"] = True

    monkeypatch.setattr(Session, "commit", boom_commit, raising=False)
    monkeypatch.setattr(Session, "rollback", rollback_spy, raising=False)

    with pytest.raises(Boom):
        repo.update(created.id, make_domain("New", 1, Decimal("1.00"), None))

    assert rolled_back["flag"] is True


def test_delete_rolls_back_on_sqlalchemy_error(repo: PropertyRepository, monkeypatch):
    class Boom(SQLAlchemyError):
        pass

    created = repo.create(make_domain("Old", 1, Decimal("1.00"), None))

    rolled_back = {"flag": False}

    def boom_commit(self: Session):
        raise Boom("commit failed")

    def rollback_spy(self: Session):
        rolled_back["flag"] = True

    monkeypatch.setattr(Session, "commit", boom_commit, raising=False)
    monkeypatch.setattr(Session, "rollback", rollback_spy, raising=False)

    with pytest.raises(Boom):
        repo.delete(created.id)

    assert rolled_back["flag"] is True
