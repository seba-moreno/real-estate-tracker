from __future__ import annotations

from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.persistence.sql_alchemy.database import Base
from app.infrastructure.persistence.sql_alchemy.repositories.transaction_repository import (
    TransactionRepository,
)
from app.infrastructure.persistence.sql_alchemy.models.transaction_model import (
    TransactionModel,
)


# ---------------------------------------------------------------------------
# Test setup helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def in_memory_db(monkeypatch):
    """
    Creates an isolated in‑memory SQLite DB and patches the SessionLocal used by
    SqlAlchemyRepository so TransactionRepository uses this DB.
    """
    engine = create_engine(
        "sqlite:///:memory:", future=True, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )

    # Patch the internal SessionLocal symbol used by SqlAlchemyRepository
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository.SessionLocal",
        TestSessionLocal,
        raising=False,
    )

    yield TestSessionLocal

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repo(in_memory_db):
    return TransactionRepository()


def seed_tx(
    SessionLocal,
    *,
    transaction_type: str,
    amount: Decimal | float | str,
    properties_concepts_id: int = 1,
    date_value: date = date(2026, 1, 15),
    period: str = "2026-01",
):
    """
    Seed a transaction row directly using the SQLite session.
    """
    with SessionLocal() as db:
        tx = TransactionModel(
            date=date_value,
            properties_concepts_id=properties_concepts_id,
            transaction_type=transaction_type,
            period=period,
            amount=amount,
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return tx.id  # type: ignore


# ---------------------------------------------------------------------------
# Tests for get_balance()
# ---------------------------------------------------------------------------


def test_get_balance_empty_returns_zero(repo: TransactionRepository):
    assert repo.get_balance() == 0.0


def test_get_balance_only_incomes(repo: TransactionRepository, in_memory_db):
    SessionLocal = in_memory_db

    seed_tx(SessionLocal, transaction_type="income", amount="100.00")
    seed_tx(SessionLocal, transaction_type="income", amount="50.00")

    balance = repo.get_balance()
    assert balance == pytest.approx(150.0)


def test_get_balance_only_expenses(repo: TransactionRepository, in_memory_db):
    SessionLocal = in_memory_db

    seed_tx(SessionLocal, transaction_type="expense", amount="30.00")
    seed_tx(SessionLocal, transaction_type="expense", amount="70.00")

    balance = repo.get_balance()
    # expenses subtract
    assert balance == pytest.approx(-100.0)


def test_get_balance_mixed_incomes_and_expenses(
    repo: TransactionRepository, in_memory_db
):
    SessionLocal = in_memory_db

    # incomes
    seed_tx(SessionLocal, transaction_type="income", amount="100.00")
    seed_tx(SessionLocal, transaction_type="income", amount="50.00")

    # expenses
    seed_tx(SessionLocal, transaction_type="expense", amount="20.00")
    seed_tx(SessionLocal, transaction_type="expense", amount="30.00")

    balance = repo.get_balance()
    # 150 income - 50 expense = 100
    assert balance == pytest.approx(100.0)


def test_get_balance_expense_larger_than_income(
    repo: TransactionRepository, in_memory_db
):
    SessionLocal = in_memory_db

    seed_tx(SessionLocal, transaction_type="income", amount="10.00")
    seed_tx(SessionLocal, transaction_type="expense", amount="25.00")

    balance = repo.get_balance()
    assert balance == pytest.approx(-15.0)


def test_get_balance_ignores_unknown_type(repo: TransactionRepository, in_memory_db):
    """
    Your CASE expression includes an ELSE 0.
    Any non-income / non-expense row contributes 0.
    """
    SessionLocal = in_memory_db

    seed_tx(SessionLocal, transaction_type="income", amount="50.00")
    seed_tx(SessionLocal, transaction_type="weird", amount="999.00")  # contributes 0
    seed_tx(SessionLocal, transaction_type="expense", amount="20.00")

    balance = repo.get_balance()
    # 50 - 20 + 0 = 30
    assert balance == pytest.approx(30.0)


def test_get_balance_returns_float(repo: TransactionRepository, in_memory_db):
    SessionLocal = in_memory_db

    seed_tx(SessionLocal, transaction_type="income", amount="123.45")

    balance = repo.get_balance()
    assert isinstance(balance, float)
    assert balance == pytest.approx(123.45)
