from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock


from app.infrastructure.persistence.sql_alchemy.mappers.contract_mapper import (
    to_domain,
    to_model,
)
from app.infrastructure.persistence.sql_alchemy.models.contract_model import (
    ContractModel,
)
from app.infrastructure.persistence.sql_alchemy.models.property_model import (
    PropertyModel,
)
from app.core.domain.entities.contract import Contract


def _make_contract_model(
    *,
    id: int | None = 1,
    property_id: int = 10,
    start_date: date = date(2026, 1, 1),
    end_date: date = date(2026, 12, 31),
    details: str | None = "details",
    prop: PropertyModel | None = None,
) -> ContractModel:
    m = ContractModel(
        id=id,
        property_id=property_id,
        start_date=start_date,
        end_date=end_date,
        details=details,
    )
    # relationship attribute on the model
    setattr(m, "prop", prop)
    return m


def _make_property_model(
    *,
    id: int = 3,
    location: str = "Main St 123",
    area: int | None = 50,
    valuation=Decimal("100000.00"),
    details: str | None = None,
) -> PropertyModel:
    return PropertyModel(
        id=id,
        location=location,
        area=area,
        valuation=valuation,
        details=details,
    )


def test_to_domain_maps_all_scalars_and_nested_when_loaded(monkeypatch):
    model = _make_contract_model(prop=_make_property_model())

    # Simulate state with 'prop' LOADED -> 'prop' NOT in state.unloaded
    fake_state = MagicMock()
    fake_state.unloaded = set()  # nothing unloaded
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.contract_mapper.attributes.instance_state",
        lambda obj: fake_state,
    )

    # Also spy that property mapper is invoked
    captured = {"called": False}

    def prop_mapper_spy(pm):
        captured["called"] = True
        # Return a plain object with the same attributes the domain expects
        # but we can also import the real mapper for Property if preferred.
        from app.infrastructure.persistence.sql_alchemy.mappers.property_mapper import (
            to_domain as real_prop_to_domain,
        )

        return real_prop_to_domain(pm)

    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.contract_mapper.prop_to_domain",
        prop_mapper_spy,
    )

    domain = to_domain(model)

    assert isinstance(domain, Contract)
    assert domain.id == model.id
    assert domain.property_id == model.property_id
    assert domain.start_date == model.start_date
    assert domain.end_date == model.end_date
    assert domain.details == model.details
    # nested mapped
    assert domain.prop is not None
    assert domain.prop.id == model.prop.id  # type: ignore[union-attr]
    assert captured["called"] is True


def test_to_domain_sets_prop_none_when_relationship_unloaded(monkeypatch):
    model = _make_contract_model(prop=_make_property_model())

    # Simulate state with 'prop' UNLOADED -> 'prop' in state.unloaded
    fake_state = MagicMock()
    fake_state.unloaded = {"prop"}
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.contract_mapper.attributes.instance_state",
        lambda obj: fake_state,
    )

    # Even if model.prop has a value, the mapper should NOT traverse it when unloaded.
    domain = to_domain(model)

    assert isinstance(domain, Contract)
    assert domain.prop is None  # important behavior


def test_to_domain_prop_none_when_loaded_but_value_is_none(monkeypatch):
    model = _make_contract_model(prop=None)

    # 'prop' is loaded (not in unloaded), but value is None
    fake_state = MagicMock()
    fake_state.unloaded = set()
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.contract_mapper.attributes.instance_state",
        lambda obj: fake_state,
    )

    domain = to_domain(model)

    assert domain.prop is None


def test_to_model_maps_all_scalars():
    entity = Contract(
        id=77,
        property_id=999,
        start_date=date(2026, 5, 1),
        end_date=date(2026, 6, 1),
        details="hello",
        prop=None,  # nested is not included on to_model
    )

    model = to_model(entity)

    assert isinstance(model, ContractModel)
    assert model.id == 77
    assert model.property_id == 999
    assert model.start_date == date(2026, 5, 1)
    assert model.end_date == date(2026, 6, 1)
    assert model.details == "hello"


def test_round_trip_scalars_ignore_nested_on_to_model(monkeypatch):
    """
    Contract.prop is intentionally not persisted by to_model.
    Ensure round-trip preserves scalar fields and prop remains None after to_domain.
    """
    entity = Contract(
        id=5,
        property_id=10,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 2, 1),
        details=None,
        prop=None,
    )

    model = to_model(entity)
    model.prop = None

    # Simulate state with 'prop' loaded but value still None
    fake_state = MagicMock()
    fake_state.unloaded = set()
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.contract_mapper.attributes.instance_state",
        lambda obj: fake_state,
    )

    back = to_domain(model)

    assert back.id == entity.id
    assert back.property_id == entity.property_id
    assert back.start_date == entity.start_date
    assert back.end_date == entity.end_date
    assert back.details == entity.details
    assert back.prop is None
