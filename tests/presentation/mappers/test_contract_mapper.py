from datetime import date
from fastapi import HTTPException
import pytest

from app.presentation.api.v1.mappers.contract_mapper import (
    domain_to_response_schema,
    domain_list_to_response_schemas,
    schema_to_domain,
)
from app.presentation.api.v1.schemas.contract import ContractBase, ContractResponse
from app.core.domain.entities.contract import Contract


# ---------------------------
# domain_to_response_schema
# ---------------------------


def test_domain_to_response_schema_happy_path():
    domain = Contract(
        id=10,
        property_id=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        details="details",
    )

    schema = domain_to_response_schema(domain)

    assert isinstance(schema, ContractResponse)
    assert schema.id == 10
    assert schema.property_id == 1
    assert schema.start_date == date(2026, 1, 1)
    assert schema.end_date == date(2026, 12, 31)
    assert schema.details == "details"


def test_domain_to_response_schema_raises_when_id_none():
    domain = Contract(
        id=None,
        property_id=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 2),
        details=None,
    )

    with pytest.raises(HTTPException) as exc:
        domain_to_response_schema(domain)
    assert exc.value.status_code == 500


# ---------------------------
# domain_list_to_response_schemas
# ---------------------------


def test_domain_list_to_response_schemas(monkeypatch):
    d1 = Contract(
        id=1,
        property_id=10,
        start_date=date.today(),
        end_date=date.today(),
        details=None,
    )
    d2 = Contract(
        id=2,
        property_id=20,
        start_date=date.today(),
        end_date=date.today(),
        details="x",
    )

    called_ids = []

    def fake_mapper(entity):
        called_ids.append(entity.id)
        return ContractResponse(
            id=entity.id,
            property_id=entity.property_id,
            start_date=entity.start_date,
            end_date=entity.end_date,
            details=entity.details,
        )

    monkeypatch.setattr(
        "app.presentation.api.v1.mappers.contract_mapper.domain_to_response_schema",
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
    base = ContractBase(
        property_id=1,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 1),
        details="contract details",
    )

    domain = schema_to_domain(base)

    assert isinstance(domain, Contract)
    assert domain.id is None  # mapper sets it explicitly
    assert domain.property_id == 1
    assert domain.start_date == date(2026, 1, 1)
    assert domain.end_date == date(2026, 12, 1)
    assert domain.details == "contract details"


def test_schema_to_domain_optional_fields():
    base = ContractBase(
        property_id=22,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 15),
        details=None,
    )

    domain = schema_to_domain(base)

    assert domain.id is None
    assert domain.details is None


# ---------------------------
# Round Trip
# ---------------------------


def test_contract_round_trip_schema_to_domain_to_schema():
    """Ensure that converting schema → domain → response keeps all fields except id logic."""
    base = ContractBase(
        property_id=8,
        start_date=date(2026, 5, 1),
        end_date=date(2026, 6, 1),
        details="hello",
    )

    domain = schema_to_domain(base)
    domain.id = 99  # assign ID to simulate DB assignment

    schema = domain_to_response_schema(domain)

    assert schema.id == 99
    assert schema.property_id == base.property_id
    assert schema.start_date == base.start_date
    assert schema.end_date == base.end_date
    assert schema.details == base.details
