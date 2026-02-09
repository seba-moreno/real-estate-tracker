import pytest
from pydantic import ValidationError
from decimal import Decimal

from app.presentation.api.v1.schemas.properties_concepts import (
    PropertiesConceptsBase,
    PropertiesConceptsResponse,
)
from app.presentation.api.v1.schemas.concept import ConceptResponse
from app.presentation.api.v1.schemas.property import PropertyResponse


# ---------------------------
# Base Model (PropertiesConceptsBase)
# ---------------------------


def test_properties_concepts_base_happy_path():
    obj = PropertiesConceptsBase(
        concept_id=1,
        property_id=2,
        enabled=True,
    )

    assert obj.concept_id == 1
    assert obj.property_id == 2
    assert obj.enabled is True


def test_properties_concepts_base_trim_strings_even_if_not_present():
    # No string fields, but str_strip_whitespace=True shouldn't break anything
    obj = PropertiesConceptsBase(
        concept_id=5,
        property_id=10,
        enabled=False,
    )
    assert obj.enabled is False


def test_properties_concepts_base_forbid_extra_fields():
    with pytest.raises(ValidationError) as exc:
        PropertiesConceptsBase(
            concept_id=1,
            property_id=1,
            enabled=True,
            unexpected="nope",
        )
    assert "unexpected" in str(exc.value)


@pytest.mark.parametrize("field", ["concept_id", "property_id"])
def test_properties_concepts_base_rejects_id_less_than_one(field):
    payload = {
        "concept_id": 1,
        "property_id": 1,
        "enabled": True,
    }
    payload[field] = 0  # violates ge=1

    with pytest.raises(ValidationError) as exc:
        PropertiesConceptsBase(**payload)

    assert field in str(exc.value)


# ---------------------------
# Response Model (PropertiesConceptsResponse)
# ---------------------------


def test_properties_concepts_response_happy_path_with_nested_models():
    concept = ConceptResponse(
        id=2,
        name="Water",
        is_ordinary=True,
        periodicity=1,
        description=None,
    )

    # FIXED: PropertyResponse requires location, valuation, area, details
    prop = PropertyResponse(
        id=3,
        location="Apartment 3B",
        valuation=Decimal("150000.00"),
        area=75,
        details="Nice view",
    )

    obj = PropertiesConceptsResponse(
        id=10,
        concept_id=2,
        property_id=3,
        enabled=True,
        concept=concept,
        property=prop,
    )

    assert obj.id == 10
    assert obj.concept_id == 2
    assert obj.property_id == 3
    assert obj.enabled is True

    # Nested
    assert isinstance(obj.concept, ConceptResponse)
    assert isinstance(obj.property, PropertyResponse)
    assert obj.concept.name == "Water"
    assert obj.property.location == "Apartment 3B"
    assert obj.property.details == "Nice view"


def test_properties_concepts_response_nested_can_be_none():
    obj = PropertiesConceptsResponse(
        id=5,
        concept_id=1,
        property_id=1,
        enabled=False,
        concept=None,
        property=None,
    )

    assert obj.id == 5
    assert obj.concept is None
    assert obj.property is None


def test_properties_concepts_response_requires_id_ge_1():
    with pytest.raises(ValidationError):
        PropertiesConceptsResponse(
            id=0,  # invalid
            concept_id=1,
            property_id=1,
            enabled=True,
            concept=None,
            property=None,
        )
