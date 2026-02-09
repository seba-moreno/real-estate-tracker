from decimal import Decimal

from app.infrastructure.persistence.sql_alchemy.mappers.property_mapper import (
    to_domain,
    to_model,
)
from app.infrastructure.persistence.sql_alchemy.models.property_model import (
    PropertyModel,
)
from app.core.domain.entities.property import Property


def _make_property_model(
    *,
    id: int | None = 1,
    location: str = "Main St 123",
    area: int | None = 50,
    valuation=Decimal("100000.00"),
    details: str | None = "some details",
) -> PropertyModel:
    return PropertyModel(
        id=id,
        location=location,
        area=area,
        valuation=valuation,
        details=details,
    )


def test_to_domain_maps_all_fields():
    model = _make_property_model(
        id=10,
        location="Ave 1",
        area=80,
        valuation=Decimal("5000.50"),
        details="Nice unit",
    )

    domain = to_domain(model)

    assert isinstance(domain, Property)
    assert domain.id == 10
    assert domain.location == "Ave 1"
    assert domain.area == 80
    assert domain.valuation == Decimal("5000.50")
    assert domain.details == "Nice unit"


def test_to_domain_allows_optional_fields_none():
    model = _make_property_model(
        id=2,
        location="X",
        area=None,
        valuation=Decimal("1.00"),
        details=None,
    )

    domain = to_domain(model)

    assert domain.id == 2
    assert domain.location == "X"
    assert domain.area is None
    assert domain.valuation == Decimal("1.00")
    assert domain.details is None


def test_to_model_maps_all_fields():
    entity = Property(
        id=33,
        location="Street ABC",
        area=120,
        valuation=Decimal("999.99"),
        details="Hello",
    )

    model = to_model(entity)

    assert isinstance(model, PropertyModel)
    assert model.id == 33
    assert model.location == "Street ABC"
    assert model.area == 120
    assert model.valuation == Decimal("999.99")
    assert model.details == "Hello"


def test_round_trip_domain_model_domain():
    original = Property(
        id=5,
        location="Loc",
        area=10,
        valuation=Decimal("50.00"),
        details="A",
    )

    mid = to_model(original)
    back = to_domain(mid)

    assert back.id == original.id
    assert back.location == original.location
    assert back.area == original.area
    assert back.valuation == original.valuation
    assert back.details == original.details
