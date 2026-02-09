from fastapi import HTTPException
import pytest
from decimal import Decimal

from app.presentation.api.v1.mappers.property_mapper import (
    domain_to_response_schema,
    domain_list_to_response_schemas,
    schema_to_domain,
)
from app.presentation.api.v1.schemas.property import PropertyBase, PropertyResponse
from app.core.domain.entities.property import Property


# ---------------------------
# domain_to_response_schema
# ---------------------------


def test_domain_to_response_schema_happy_path():
    domain = Property(
        id=10,
        location="Main St 123",
        area=50,
        valuation=Decimal("100000.00"),
        details="Nice place",
    )

    schema = domain_to_response_schema(domain)

    assert isinstance(schema, PropertyResponse)
    assert schema.id == 10
    assert schema.location == "Main St 123"
    assert schema.area == 50
    assert schema.valuation == Decimal("100000.00")
    assert schema.details == "Nice place"


def test_domain_to_response_schema_raises_when_id_none():
    domain = Property(
        id=None,
        location="Test",
        area=20,
        valuation=Decimal("10.00"),
        details=None,
    )

    with pytest.raises(HTTPException) as exc:
        domain_to_response_schema(domain)
    assert exc.value.status_code == 500


# ---------------------------
# domain_list_to_response_schemas
# ---------------------------


def test_domain_list_to_response_schemas(monkeypatch):
    d1 = Property(
        id=1, location="A", area=None, valuation=Decimal("10.00"), details=None
    )
    d2 = Property(id=2, location="B", area=30, valuation=Decimal("20.00"), details="x")

    called_ids = []

    def fake_mapper(entity):
        called_ids.append(entity.id)
        return PropertyResponse(
            id=entity.id,
            location=entity.location,
            area=entity.area,
            valuation=entity.valuation,
            details=entity.details,
        )

    monkeypatch.setattr(
        "app.presentation.api.v1.mappers.property_mapper.domain_to_response_schema",
        fake_mapper,
    )

    result = domain_list_to_response_schemas([d1, d2])

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2
    assert called_ids == [1, 2]


# ---------------------------
# schema_to_domain
# ---------------------------


def test_schema_to_domain_happy_path():
    base = PropertyBase(
        location="Main St 99",
        area=40,
        valuation=Decimal("50000.00"),
        details="Clean",
    )

    domain = schema_to_domain(base)

    assert isinstance(domain, Property)
    assert domain.id is None  # mapper always sets id=None
    assert domain.location == "Main St 99"
    assert domain.area == 40
    assert domain.valuation == Decimal("50000.00")
    assert domain.details == "Clean"


def test_schema_to_domain_optional_fields():
    base = PropertyBase(
        location="X",
        area=None,
        valuation=Decimal("10.00"),
        details=None,
    )

    domain = schema_to_domain(base)

    assert domain.id is None
    assert domain.area is None
    assert domain.details is None


# ---------------------------
# Round Trip
# ---------------------------


def test_property_round_trip_schema_to_domain_to_schema():
    """Ensure mapping preserves all fields except id logic."""
    base = PropertyBase(
        location="Somewhere",
        area=60,
        valuation=Decimal("99.99"),
        details="Unit 1A",
    )

    domain = schema_to_domain(base)
    domain.id = 77  # simulate DB assignment

    schema = domain_to_response_schema(domain)

    assert schema.id == 77
    assert schema.location == base.location
    assert schema.area == base.area
    assert schema.valuation == base.valuation
    assert schema.details == base.details
