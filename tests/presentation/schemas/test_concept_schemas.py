# tests/test_concept_schemas.py
import pytest
from pydantic import ValidationError
from app.presentation.api.v1.schemas.concept import ConceptBase, ConceptResponse


def test_concept_base_happy_path_strips_and_validates():
    obj = ConceptBase(
        name="  Lease collection  ",
        is_ordinary=True,
        periodicity=1,
        description="  Monthly lease collection  ",
    )
    assert obj.name == "Lease collection"
    assert obj.is_ordinary is True
    assert obj.periodicity == 1
    assert obj.description == "Monthly lease collection"


def test_concept_base_forbid_extra_fields():
    with pytest.raises(ValidationError) as exc:
        ConceptBase(
            name="X",
            is_ordinary=False,
            periodicity=None,
            description=None,
            unexpected="nope",  # extra="forbid"
        )
    assert "unexpected" in str(exc.value)


def test_concept_base_name_length_and_description_length():
    with pytest.raises(ValidationError):
        ConceptBase(name="", is_ordinary=True, periodicity=0, description=None)

    too_long_name = "x" * 101
    with pytest.raises(ValidationError):
        ConceptBase(
            name=too_long_name, is_ordinary=True, periodicity=0, description=None
        )

    too_long_desc = "y" * 501
    with pytest.raises(ValidationError):
        ConceptBase(
            name="ok", is_ordinary=True, periodicity=0, description=too_long_desc
        )


def test_concept_base_periodicity_allows_none_and_ge_zero():
    obj = ConceptBase(name="ok", is_ordinary=False, periodicity=None, description=None)
    assert obj.periodicity is None

    obj2 = ConceptBase(name="ok", is_ordinary=False, periodicity=0, description=None)
    assert obj2.periodicity == 0

    with pytest.raises(ValidationError):
        ConceptBase(name="ok", is_ordinary=False, periodicity=-1, description=None)


def test_concept_response_requires_id_ge_1_and_inherits_fields():
    # valid
    obj = ConceptResponse(
        id=1,
        name="Name",
        is_ordinary=True,
        periodicity=2,
        description="desc",
    )
    assert obj.id == 1
    assert obj.name == "Name"

    # invalid id
    with pytest.raises(ValidationError):
        ConceptResponse(
            id=0, name="N", is_ordinary=False, periodicity=None, description=None
        )
