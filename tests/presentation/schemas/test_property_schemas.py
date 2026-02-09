# tests/test_property_schemas.py
import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.presentation.api.v1.schemas.property import (
    PropertyBase,
    PropertyResponse,
)


# ----------------------------
# PropertyBase - Happy Path
# ----------------------------


def test_property_base_happy_path_strips_whitespace_and_validates():
    obj = PropertyBase(
        location="  Example St. 123  ",
        area=50,
        valuation=Decimal("100000.50"),
        details="  Something here  ",
    )

    assert obj.location == "Example St. 123"
    assert obj.area == 50
    assert obj.valuation == Decimal("100000.50")
    assert obj.details == "Something here"


# ----------------------------
# location field
# ----------------------------


def test_property_base_location_min_length():
    with pytest.raises(ValidationError):
        PropertyBase(location="", area=10, valuation=Decimal("1.00"), details=None)


def test_property_base_location_max_length():
    too_long = "x" * 101
    with pytest.raises(ValidationError):
        PropertyBase(
            location=too_long, area=10, valuation=Decimal("1.00"), details=None
        )


# ----------------------------
# area field (optional)
# ----------------------------


def test_property_base_area_can_be_none():
    obj = PropertyBase(
        location="A", area=None, valuation=Decimal("10.00"), details=None
    )
    assert obj.area is None


def test_property_base_area_must_be_ge_1_if_provided():
    with pytest.raises(ValidationError):
        PropertyBase(location="A", area=0, valuation=Decimal("10.00"), details=None)


# ----------------------------
# valuation field (Decimal constraints)
# ----------------------------


def test_property_base_valuation_ge_0():
    with pytest.raises(ValidationError):
        PropertyBase(location="A", area=10, valuation=Decimal("-1.00"), details=None)


def test_property_base_valuation_decimal_places():
    # more than 2 decimal places -> error
    with pytest.raises(ValidationError):
        PropertyBase(location="A", area=10, valuation=Decimal("1.234"), details=None)


def test_property_base_valuation_max_digits_enforced():
    # 20 digits before decimal ( > max_digits=19 ) should fail
    too_big = Decimal("9" * 20)  # 20 digits
    with pytest.raises(ValidationError):
        PropertyBase(location="A", area=10, valuation=too_big, details=None)


# ----------------------------
# details field
# ----------------------------


def test_property_base_details_max_length():
    too_long = "x" * 501
    with pytest.raises(ValidationError):
        PropertyBase(location="A", area=10, valuation=Decimal("1.00"), details=too_long)


def test_property_base_details_trimmed():
    obj = PropertyBase(
        location="A",
        area=10,
        valuation=Decimal("1.00"),
        details="  hello  ",
    )
    assert obj.details == "hello"


# ----------------------------
# extra="forbid"
# ----------------------------


def test_property_base_forbid_extra_fields():
    with pytest.raises(ValidationError) as exc:
        PropertyBase(
            location="A",
            area=10,
            valuation=Decimal("1.00"),
            details=None,
            unexpected="nope",
        )
    assert "unexpected" in str(exc.value)


# ----------------------------
# PropertyResponse
# ----------------------------


def test_property_response_happy_path():
    obj = PropertyResponse(
        id=5,
        location="Street",
        area=70,
        valuation=Decimal("1000.00"),
        details="Nice",
    )

    assert obj.id == 5
    assert obj.location == "Street"
    assert obj.area == 70
    assert obj.valuation == Decimal("1000.00")
    assert obj.details == "Nice"


def test_property_response_requires_id_ge_1():
    with pytest.raises(ValidationError):
        PropertyResponse(
            id=0,
            location="A",
            area=10,
            valuation=Decimal("10.00"),
            details=None,
        )
