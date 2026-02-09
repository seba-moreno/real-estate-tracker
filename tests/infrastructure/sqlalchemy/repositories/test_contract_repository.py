from __future__ import annotations

import calendar
from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.persistence.sql_alchemy.database import Base
from app.infrastructure.persistence.sql_alchemy.models.contract_model import (
    ContractModel,
)
from app.infrastructure.persistence.sql_alchemy.repositories.contract_repository import (
    ContractRepository,
)


def _add_months(d: date, months: int) -> date:
    """Calendar-aware months addition (no dateutil), clamping the day when needed."""
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    last_day = calendar.monthrange(y, m)[1]
    day = min(d.day, last_day)
    return date(y, m, day)


@pytest.fixture
def in_memory_db(monkeypatch):
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )

    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository.SessionLocal",
        TestSessionLocal,
        raising=False,
    )

    yield TestSessionLocal

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repo(in_memory_db):
    """Fresh ContractRepository bound to the in-memory DB for each test."""
    return ContractRepository()


def _seed_contract(
    session_maker,
    *,
    property_id: int,
    start_date: date,
    end_date: date,
    details: str | None = None,
) -> int:
    with session_maker() as db:
        obj = ContractModel(
            property_id=property_id,
            start_date=start_date,
            end_date=end_date,
            details=details,
        )
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj.id  # type: ignore[return-value]


def test_get_ending_within_months_raises_when_invalid(repo: ContractRepository):
    with pytest.raises(ValueError):
        repo.get_ending_within_months(0)
    with pytest.raises(ValueError):
        repo.get_ending_within_months(-3)


def test_get_ending_within_months_filters_and_orders(
    repo: ContractRepository, in_memory_db
):
    session_factory = in_memory_db

    # We use a fixed 'reference' today to calculate relative offsets.
    # To ensure SQLite's date('now') includes our 'today' record,
    # we seed the 'today' record with Today + 1 day.
    today = date.today()

    # --- SEED ---

    # 1. Excluded: Ends yesterday (Too early for date('now'))
    _seed_contract(
        session_factory,
        property_id=101,
        start_date=today,
        end_date=today - timedelta(days=1),
    )

    # 2. Included: Ends tomorrow (Guaranteed >= date('now'))
    _seed_contract(
        session_factory,
        property_id=202,
        start_date=today,
        end_date=today + timedelta(days=1),
    )

    # 3. Included: Ends in 1 month
    _seed_contract(
        session_factory,
        property_id=303,
        start_date=today,
        end_date=_add_months(today, 1),
    )

    # 4. Included: Ends in 2 months (Safely inside the 3-month window)
    _seed_contract(
        session_factory,
        property_id=404,
        start_date=today,
        end_date=_add_months(today, 2),
    )

    # 5. Excluded: Ends in 4 months (Too late for date('now', '+3 months'))
    _seed_contract(
        session_factory,
        property_id=505,
        start_date=today,
        end_date=_add_months(today, 4),
    )

    # --- EXECUTE ---
    # We ask for contracts ending in the next 3 months
    results = repo.get_ending_within_months(3)

    # --- ASSERT ---
    property_ids_found = {r.property_id for r in results}
    expected_property_ids = {202, 303, 404}

    assert (
        len(results) == 3
    ), f"Expected 3 results, got {len(results)}: {property_ids_found}"
    assert expected_property_ids == property_ids_found


def test_get_ending_within_months_returns_empty_when_none_in_range(
    repo: ContractRepository, in_memory_db
):
    session_factory = in_memory_db
    today = date.today()
    _seed_contract(
        session_factory,
        property_id=10,
        start_date=today,
        end_date=today - timedelta(days=10),
    )

    results = repo.get_ending_within_months(2)
    assert results == []
