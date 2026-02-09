from fastapi import HTTPException
from app.presentation.api.v1.mappers.concept_mapper import (
    domain_to_response_schema,
    domain_list_to_response_schemas,
    schema_to_domain,
)
from app.presentation.api.v1.schemas.concept import ConceptBase, ConceptResponse
from app.core.domain.entities.concept import Concept
import pytest


# ---------------------------
# domain_to_response_schema
# ---------------------------


def test_domain_to_response_schema_happy_path():
    domain = Concept(
        id=10,
        name="Lease",
        is_ordinary=True,
        periodicity=1,
        description="Monthly lease",
    )

    schema = domain_to_response_schema(domain)

    assert isinstance(schema, ConceptResponse)
    assert schema.id == 10
    assert schema.name == "Lease"
    assert schema.is_ordinary is True
    assert schema.periodicity == 1
    assert schema.description == "Monthly lease"


def test_domain_to_response_schema_raises_if_id_none():
    domain = Concept(
        id=None,
        name="Water",
        is_ordinary=False,
        periodicity=None,
        description=None,
    )

    with pytest.raises(HTTPException) as exc:
        domain_to_response_schema(domain)
    assert exc.value.status_code == 500


# ---------------------------
# domain_list_to_response_schemas
# ---------------------------


def test_domain_list_to_response_schemas_happy_path(monkeypatch):
    d1 = Concept(id=1, name="A", is_ordinary=True, periodicity=None, description=None)
    d2 = Concept(id=2, name="B", is_ordinary=False, periodicity=3, description="x")

    # Spy on domain_to_response_schema
    called = []

    def fake_mapper(entity):
        called.append(entity.id)
        return ConceptResponse(
            id=entity.id,
            name=entity.name,
            is_ordinary=entity.is_ordinary,
            periodicity=entity.periodicity,
            description=entity.description,
        )

    monkeypatch.setattr(
        "app.presentation.api.v1.mappers.concept_mapper.domain_to_response_schema",
        fake_mapper,
    )

    result = domain_list_to_response_schemas([d1, d2])

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2
    assert called == [1, 2]


# ---------------------------
# schema_to_domain
# ---------------------------


def test_schema_to_domain_happy_path():
    base = ConceptBase(
        name="Electricity",
        is_ordinary=True,
        periodicity=1,
        description="Monthly electricity",
    )

    domain = schema_to_domain(base)

    assert isinstance(domain, Concept)
    assert domain.id is None  # always None per mapper design
    assert domain.name == "Electricity"
    assert domain.is_ordinary is True
    assert domain.periodicity == 1
    assert domain.description == "Monthly electricity"


def test_schema_to_domain_allows_optional_fields():
    base = ConceptBase(
        name="Tax",
        is_ordinary=False,
        periodicity=None,
        description=None,
    )

    domain = schema_to_domain(base)

    assert domain.id is None
    assert domain.periodicity is None
    assert domain.description is None


# ---------------------------
# Round-trip consistency
# ---------------------------


def test_concept_round_trip_schema_to_domain_to_schema():
    """Ensures conversion keeps all fields intact except id=None."""
    base = ConceptBase(
        name="Water",
        is_ordinary=True,
        periodicity=2,
        description="Utility",
    )

    domain = schema_to_domain(base)
    # inject an id to test round-trip
    domain.id = 99

    schema = domain_to_response_schema(domain)

    assert schema.id == 99
    assert schema.name == base.name
    assert schema.is_ordinary == base.is_ordinary
    assert schema.periodicity == base.periodicity
    assert schema.description == base.description
