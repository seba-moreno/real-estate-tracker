from datetime import date
from decimal import Decimal
from fastapi import HTTPException
import pytest

from app.presentation.api.v1.mappers.transaction_mapper import (
    domain_to_response_schema,
    domain_list_to_response_schemas,
    schema_to_domain,
)
from app.presentation.api.v1.schemas.transaction import (
    TransactionBase,
    TransactionResponse,
)
from app.core.domain.entities.transaction import Transaction


# ---------------------------
# domain_to_response_schema
# ---------------------------


def test_domain_to_response_schema_happy_path():
    domain = Transaction(
        id=10,
        date=date(2026, 1, 15),
        properties_concepts_id=1,
        transaction_type="income",
        period="2026-01",
        amount=Decimal("1000.00"),
    )

    schema = domain_to_response_schema(domain)

    assert isinstance(schema, TransactionResponse)
    assert schema.id == 10
    assert schema.date == date(2026, 1, 15)
    assert schema.properties_concepts_id == 1
    assert schema.transaction_type == "income"
    assert schema.period == "2026-01"
    assert schema.amount == Decimal("1000.00")


def test_domain_to_response_schema_raises_when_id_none():
    domain = Transaction(
        id=None,
        date=date(2026, 1, 15),
        properties_concepts_id=1,
        transaction_type="expense",
        period="2026-02",
        amount=Decimal("50.00"),
    )

    with pytest.raises(HTTPException) as exc:
        domain_to_response_schema(domain)
    assert exc.value.status_code == 500


# ---------------------------
# domain_list_to_response_schemas
# ---------------------------


def test_domain_list_to_response_schemas(monkeypatch):
    d1 = Transaction(
        id=1,
        date=date(2026, 1, 1),
        properties_concepts_id=2,
        transaction_type="income",
        period="2026-01",
        amount=Decimal("10.00"),
    )
    d2 = Transaction(
        id=2,
        date=date(2026, 2, 1),
        properties_concepts_id=3,
        transaction_type="expense",
        period="2026-02",
        amount=Decimal("5.00"),
    )

    called_ids = []

    def fake_mapper(entity):
        called_ids.append(entity.id)
        return TransactionResponse(
            id=entity.id,
            date=entity.date,
            properties_concepts_id=entity.properties_concepts_id,
            transaction_type=entity.transaction_type,
            period=entity.period,
            amount=entity.amount,
        )

    monkeypatch.setattr(
        "app.presentation.api.v1.mappers.transaction_mapper.domain_to_response_schema",
        fake_mapper,
    )

    result = domain_list_to_response_schemas([d1, d2])

    assert len(result) == 2
    assert [r.id for r in result] == [1, 2]
    assert called_ids == [1, 2]


# ---------------------------
# schema_to_domain
# ---------------------------


def test_schema_to_domain_happy_path():
    base = TransactionBase(
        date=date(2026, 3, 10),
        properties_concepts_id=9,
        transaction_type="income",
        period="2026-03",
        amount=Decimal("123.45"),
    )

    domain = schema_to_domain(base)

    assert isinstance(domain, Transaction)
    assert domain.id is None  # mapper enforces id=None on creation
    assert domain.date == date(2026, 3, 10)
    assert domain.properties_concepts_id == 9
    assert domain.transaction_type == "income"
    assert domain.period == "2026-03"
    assert domain.amount == Decimal("123.45")


def test_schema_to_domain_accepts_validators_output():
    """Ensures values processed by schema validators flow through correctly."""
    base = TransactionBase(
        date="2026-04-01",  # str accepted by schema; parsed to date
        properties_concepts_id=1,
        transaction_type="  EXPENSE  ",  # normalized to 'expense'
        period="2026-04",  # valid YYYY-MM
        amount="1000.00",  # str -> Decimal
    )

    domain = schema_to_domain(base)

    assert domain.id is None
    assert domain.date == date(2026, 4, 1)
    assert domain.transaction_type == "expense"
    assert domain.period == "2026-04"
    assert domain.amount == Decimal("1000.00")


# ---------------------------
# Round Trip
# ---------------------------


def test_transaction_round_trip_schema_to_domain_to_schema():
    """schema → domain (id=None) → assign id → response schema, preserving values."""
    base = TransactionBase(
        date=date(2026, 5, 1),
        properties_concepts_id=12,
        transaction_type="income",
        period="2026-05",
        amount=Decimal("999.99"),
    )

    domain = schema_to_domain(base)
    domain.id = 77  # simulate DB assignment

    schema = domain_to_response_schema(domain)

    assert schema.id == 77
    assert schema.date == base.date
    assert schema.properties_concepts_id == base.properties_concepts_id
    assert schema.transaction_type == base.transaction_type
    assert schema.period == base.period
    assert schema.amount == base.amount
