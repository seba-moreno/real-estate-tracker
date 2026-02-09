from fastapi import HTTPException
import pytest
from app.presentation.api.v1.mappers.properties_concepts_mapper import (
    domain_to_response_schema,
    domain_list_to_response_schemas,
    schema_to_domain,
)
from app.presentation.api.v1.schemas.properties_concepts import (
    PropertiesConceptsBase,
    PropertiesConceptsResponse,
)
from app.core.domain.entities.properties_concepts import PropertiesConcepts

# Nested mappers
from app.presentation.api.v1.schemas.concept import ConceptResponse
from app.presentation.api.v1.schemas.property import PropertyResponse


# -----------------------------------------
# domain_to_response_schema
# -----------------------------------------


def test_domain_to_response_schema_full_nested(monkeypatch):
    """Ensures nested concept and property are mapped correctly."""

    # Fake nested domain entities
    domain_concept = type(
        "Concept",
        (),
        {
            "id": 2,
            "name": "Utility",
            "is_ordinary": True,
            "periodicity": 1,
            "description": "Monthly",
        },
    )()

    domain_property = type(
        "Property",
        (),
        {
            "id": 3,
            "location": "Main St 123",
            "area": 50,
            "valuation": 100000,
            "details": None,
        },
    )()

    domain_pc = PropertiesConcepts(
        id=10,
        concept_id=2,
        property_id=3,
        enabled=True,
        concept=domain_concept,
        prop=domain_property,
    )

    # Spy replacements for nested mappers
    def fake_concept_mapper(c):
        assert c.id == 2
        return ConceptResponse(
            id=2,
            name=c.name,
            is_ordinary=c.is_ordinary,
            periodicity=c.periodicity,
            description=c.description,
        )

    def fake_prop_mapper(p):
        assert p.id == 3
        return PropertyResponse(
            id=3,
            location=p.location,
            area=p.area,
            valuation=p.valuation,
            details=p.details,
        )

    monkeypatch.setattr(
        "app.presentation.api.v1.mappers.properties_concepts_mapper.concept_domain_to_response_schema",
        fake_concept_mapper,
    )
    monkeypatch.setattr(
        "app.presentation.api.v1.mappers.properties_concepts_mapper.prop_domain_to_response_schema",
        fake_prop_mapper,
    )

    schema = domain_to_response_schema(domain_pc)

    assert isinstance(schema, PropertiesConceptsResponse)
    assert schema.id == 10
    assert schema.concept_id == 2
    assert schema.property_id == 3
    assert schema.enabled is True

    # Nested objects present
    assert isinstance(schema.concept, ConceptResponse)
    assert isinstance(schema.property, PropertyResponse)


def test_domain_to_response_schema_no_nested(monkeypatch):
    """Ensures nested fields are None when entity.concept / entity.prop are None."""

    domain_pc = PropertiesConcepts(
        id=5,
        concept_id=1,
        property_id=1,
        enabled=False,
        concept=None,
        prop=None,
    )

    schema = domain_to_response_schema(domain_pc)

    assert schema.id == 5
    assert schema.concept is None
    assert schema.property is None


def test_domain_to_response_schema_raises_if_id_none():
    """The mapping asserts entity.id is not None."""

    domain_pc = PropertiesConcepts(
        id=None,
        concept_id=1,
        property_id=2,
        enabled=True,
        concept=None,
        prop=None,
    )

    with pytest.raises(HTTPException) as exc:
        domain_to_response_schema(domain_pc)
    assert exc.value.status_code == 500


# -----------------------------------------
# domain_list_to_response_schemas
# -----------------------------------------


def test_domain_list_to_response_schemas(monkeypatch):
    """Checks that the mapper delegates to domain_to_response_schema for each element."""

    d1 = PropertiesConcepts(
        id=1, concept_id=2, property_id=3, enabled=True, concept=None, prop=None
    )
    d2 = PropertiesConcepts(
        id=2, concept_id=4, property_id=5, enabled=False, concept=None, prop=None
    )

    called_ids = []

    def fake_mapper(e):
        called_ids.append(e.id)
        return PropertiesConceptsResponse(
            id=e.id,
            concept_id=e.concept_id,
            property_id=e.property_id,
            enabled=e.enabled,
            concept=None,
            property=None,
        )

    monkeypatch.setattr(
        "app.presentation.api.v1.mappers.properties_concepts_mapper.domain_to_response_schema",
        fake_mapper,
    )

    result = domain_list_to_response_schemas([d1, d2])

    assert len(result) == 2
    assert [r.id for r in result] == [1, 2]
    assert called_ids == [1, 2]


# -----------------------------------------
# schema_to_domain
# -----------------------------------------


def test_schema_to_domain_happy_path():
    dto = PropertiesConceptsBase(
        concept_id=1,
        property_id=2,
        enabled=True,
    )

    domain = schema_to_domain(dto)

    assert isinstance(domain, PropertiesConcepts)
    assert domain.id is None  # mapper always sets id=None
    assert domain.concept_id == 1
    assert domain.property_id == 2
    assert domain.enabled is True


def test_schema_to_domain_values_passed_correctly():
    dto = PropertiesConceptsBase(
        concept_id=3,
        property_id=4,
        enabled=False,
    )

    domain = schema_to_domain(dto)

    assert domain.id is None
    assert domain.concept_id == 3
    assert domain.property_id == 4
    assert domain.enabled is False


# -----------------------------------------
# Round Trip
# -----------------------------------------


def test_properties_concepts_round_trip():
    """schema → domain → response (after adding id & removing nested)"""

    base = PropertiesConceptsBase(concept_id=5, property_id=6, enabled=True)

    domain = schema_to_domain(base)
    domain.id = 99  # simulate DB assignment
    domain.concept = None
    domain.prop = None

    schema = domain_to_response_schema(domain)

    assert schema.id == 99
    assert schema.concept_id == 5
    assert schema.property_id == 6
    assert schema.enabled is True
    assert schema.concept is None
    assert schema.property is None
