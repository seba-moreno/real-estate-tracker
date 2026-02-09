# tests/test_contract_schemas.py
import pytest
from datetime import date
from pydantic import ValidationError

from app.presentation.api.v1.schemas.contract import (
    ContractBase,
    ContractResponse,
)


# ---------------------------
# ContractBase - Happy Path
# ---------------------------


def test_contract_base_happy_path_strips_whitespace_and_validates():
    obj = ContractBase(
        property_id=1,
        start_date=date(2026, 1, 15),
        end_date=date(2026, 2, 15),
        details="  Some details here  ",
    )

    assert obj.property_id == 1
    assert obj.start_date == date(2026, 1, 15)
    assert obj.end_date == date(2026, 2, 15)
    assert obj.details == "Some details here"


# ---------------------------
# Extra Fields
# ---------------------------


def test_contract_base_forbid_extra_fields():
    with pytest.raises(ValidationError) as exc:
        ContractBase(
            property_id=1,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 2),
            details=None,
            unexpected="nope",
        )
    assert "unexpected" in str(exc.value)


# ---------------------------
# Field Validations
# ---------------------------


def test_contract_base_property_id_minimum():
    with pytest.raises(ValidationError):
        ContractBase(
            property_id=0,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 2),
            details=None,
        )


def test_contract_base_details_length_limit():
    too_long = "x" * 501
    with pytest.raises(ValidationError):
        ContractBase(
            property_id=1,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 2),
            details=too_long,
        )


def test_contract_base_details_can_be_none():
    obj = ContractBase(
        property_id=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 2),
        details=None,
    )
    assert obj.details is None


# ---------------------------
# Date Ordering Validator
# ---------------------------


def test_contract_base_rejects_end_before_start():
    with pytest.raises(ValidationError) as exc:
        ContractBase(
            property_id=1,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 1, 1),
            details=None,
        )

    assert "endDate must be on or after startDate" in str(exc.value)


def test_contract_base_allows_end_equal_start():
    obj = ContractBase(
        property_id=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 1),
        details=None,
    )
    assert obj.end_date == obj.start_date


# ---------------------------
# ContractResponse
# ---------------------------


def test_contract_response_happy_path():
    obj = ContractResponse(
        id=10,
        property_id=5,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 15),
        details="Valid",
    )

    assert obj.id == 10
    assert obj.property_id == 5
    assert obj.start_date == date(2026, 1, 1)
    assert obj.end_date == date(2026, 1, 15)
    assert obj.details == "Valid"


def test_contract_response_requires_id_ge_1():
    with pytest.raises(ValidationError):
        ContractResponse(
            id=0,
            property_id=1,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 2),
            details=None,
        )
