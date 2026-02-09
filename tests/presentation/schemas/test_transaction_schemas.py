import pytest
from datetime import date
from decimal import Decimal
from pydantic import ValidationError

from app.presentation.api.v1.schemas.transaction import (
    TransactionBase,
    TransactionResponse,
    TransactionsBalanceResponse,
)


# ---------------------------
# Happy Path
# ---------------------------


def test_transaction_base_happy_path_strips_and_validates():
    obj = TransactionBase(
        date="2026-01-15",
        properties_concepts_id=1,
        transaction_type="  INCOME  ",
        period="2026-05",
        amount="1000.00",
    )

    # date parsing
    assert obj.date == date(2026, 1, 15)

    # id
    assert obj.properties_concepts_id == 1

    # lowercase and stripping validator
    assert obj.transaction_type == "income"

    # regex + month validation
    assert obj.period == "2026-05"

    # decimal conversion
    assert obj.amount == Decimal("1000.00")


# ---------------------------
# transaction_type validator
# ---------------------------


def test_transaction_base_invalid_transaction_type():
    with pytest.raises(ValidationError) as exc:
        TransactionBase(
            date="2026-01-15",
            properties_concepts_id=1,
            transaction_type="invalid",
            period="2026-01",
            amount="10.00",
        )

    assert "transaction_type must be either 'income' or 'expense'" in str(exc.value)


def test_transaction_base_transaction_type_must_be_string():
    with pytest.raises(ValidationError) as exc:
        TransactionBase(
            date="2026-01-15",
            properties_concepts_id=1,
            transaction_type=123,  # invalid
            period="2026-01",
            amount="10.00",
        )

    assert "must be a string" in str(exc.value)


# ---------------------------
# period validator
# ---------------------------


def test_transaction_base_period_invalid_format():
    with pytest.raises(ValidationError) as exc:
        TransactionBase(
            date="2026-01-15",
            properties_concepts_id=1,
            transaction_type="income",
            period="2026-1",
            amount="10.00",
        )

    assert "period must be in format" in str(exc.value)


def test_transaction_base_period_invalid_month():
    with pytest.raises(ValidationError) as exc:
        TransactionBase(
            date="2026-01-15",
            properties_concepts_id=1,
            transaction_type="income",
            period="2026-13",
            amount="10.00",
        )
    assert "period month must be between 01 and 12" in str(exc.value)


# ---------------------------
# amount validator
# ---------------------------


def test_transaction_base_amount_negative_not_allowed():
    with pytest.raises(ValidationError) as exc:
        TransactionBase(
            date="2026-01-15",
            properties_concepts_id=1,
            transaction_type="income",
            period="2026-01",
            amount="-1.00",
        )
    assert "greater than or equal to 0" in str(exc.value)


def test_transaction_base_amount_too_many_decimal_places():
    with pytest.raises(ValidationError) as exc:
        TransactionBase(
            date="2026-01-15",
            properties_concepts_id=1,
            transaction_type="income",
            period="2026-01",
            amount="10.999",
        )
    assert "no more than 2 decimal places" in str(exc.value)


def test_transaction_base_amount_too_many_digits():
    # 20 digits -> violate max 19
    with pytest.raises(ValidationError) as exc:
        TransactionBase(
            date="2026-01-15",
            properties_concepts_id=1,
            transaction_type="income",
            period="2026-01",
            amount="9" * 20,
        )

    assert "no more than 19 digits in total" in str(exc.value)


# ---------------------------
# Missing / extra fields
# ---------------------------


def test_transaction_base_missing_required_fields():
    with pytest.raises(ValidationError):
        TransactionBase(
            properties_concepts_id=1,
            transaction_type="income",
            period="2026-01",
            amount="10.00",
        )


def test_transaction_base_forbid_extra_fields():
    with pytest.raises(ValidationError) as exc:
        TransactionBase(
            date="2026-01-15",
            properties_concepts_id=1,
            transaction_type="income",
            period="2026-01",
            amount="10.00",
            unexpected="NOPE",
        )

    assert "unexpected" in str(exc.value)


# ---------------------------
# TransactionResponse
# ---------------------------


def test_transaction_response_happy_path():
    obj = TransactionResponse(
        id=1,
        date="2026-01-15",
        properties_concepts_id=2,
        transaction_type="expense",
        period="2026-01",
        amount="500.00",
    )

    assert obj.id == 1
    assert obj.transaction_type == "expense"
    assert obj.amount == Decimal("500.00")


def test_transaction_response_id_must_be_ge_1():
    with pytest.raises(ValidationError):
        TransactionResponse(
            id=0,
            date="2026-01-15",
            properties_concepts_id=1,
            transaction_type="income",
            period="2026-01",
            amount="10.00",
        )


# ---------------------------
# TransactionsBalanceResponse
# ---------------------------


def test_transactions_balance_response_happy_path():
    obj = TransactionsBalanceResponse(balance=1234.56)
    assert obj.balance == 1234.56


def test_transactions_balance_response_requires_float():
    with pytest.raises(ValidationError):
        TransactionsBalanceResponse(balance="invalid")
