from app.infrastructure.persistence.sql_alchemy.mappers.concept_mapper import (
    to_domain,
    to_model,
)
from app.infrastructure.persistence.sql_alchemy.models.concept_model import ConceptModel
from app.core.domain.entities.concept import Concept


def test_to_domain_happy_path():
    model = ConceptModel(
        id=10,
        name="Lease",
        is_ordinary=True,
        periodicity=1,
        description="Monthly lease",
    )

    domain = to_domain(model)

    assert isinstance(domain, Concept)
    assert domain.id == 10
    assert domain.name == "Lease"
    assert domain.is_ordinary is True
    assert domain.periodicity == 1
    assert domain.description == "Monthly lease"


def test_to_domain_allows_none_optionals():
    model = ConceptModel(
        id=2,
        name="Water",
        is_ordinary=False,
        periodicity=None,
        description=None,
    )

    domain = to_domain(model)

    assert domain.id == 2
    assert domain.name == "Water"
    assert domain.is_ordinary is False
    assert domain.periodicity is None
    assert domain.description is None


def test_to_model_happy_path():
    domain = Concept(
        id=77,
        name="Tax",
        is_ordinary=False,
        periodicity=3,
        description="Quarterly tax",
    )

    model = to_model(domain)

    assert isinstance(model, ConceptModel)
    assert model.id == 77
    assert model.name == "Tax"
    assert model.is_ordinary is False
    assert model.periodicity == 3
    assert model.description == "Quarterly tax"


def test_to_model_with_none_optionals():
    domain = Concept(
        id=None,
        name="Maintenance",
        is_ordinary=True,
        periodicity=None,
        description=None,
    )

    model = to_model(domain)

    assert model.id is None
    assert model.name == "Maintenance"
    assert model.is_ordinary is True
    assert model.periodicity is None
    assert model.description is None


def test_round_trip_domain_model_domain():
    original = Concept(
        id=5,
        name="Electricity",
        is_ordinary=True,
        periodicity=1,
        description="Monthly",
    )

    # domain -> model -> domain
    mid = to_model(original)
    back = to_domain(mid)

    assert back.id == original.id
    assert back.name == original.name
    assert back.is_ordinary == original.is_ordinary
    assert back.periodicity == original.periodicity
    assert back.description == original.description
