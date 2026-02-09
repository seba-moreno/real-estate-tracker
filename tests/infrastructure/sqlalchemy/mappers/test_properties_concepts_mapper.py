from decimal import Decimal
from unittest.mock import MagicMock


from app.infrastructure.persistence.sql_alchemy.mappers.properties_concepts_mapper import (
    to_domain,
    to_model,
)
from app.infrastructure.persistence.sql_alchemy.models.properties_concepts_model import (
    PropertiesConceptsModel,
)
from app.infrastructure.persistence.sql_alchemy.models.concept_model import ConceptModel
from app.infrastructure.persistence.sql_alchemy.models.property_model import (
    PropertyModel,
)
from app.core.domain.entities.properties_concepts import PropertiesConcepts


def _make_concept_model(
    *,
    id: int = 2,
    name: str = "Water",
    is_ordinary: bool = True,
    periodicity: int | None = 1,
    description: str | None = "Monthly",
) -> ConceptModel:
    return ConceptModel(
        id=id,
        name=name,
        is_ordinary=is_ordinary,
        periodicity=periodicity,
        description=description,
    )


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


def _make_pc_model(
    *,
    id: int | None = 10,
    concept_id: int = 2,
    property_id: int = 3,
    enabled: bool = True,
    concept: ConceptModel | None = None,
    prop: PropertyModel | None = None,
) -> PropertiesConceptsModel:
    m = PropertiesConceptsModel(
        id=id,
        concept_id=concept_id,
        property_id=property_id,
        enabled=enabled,
    )
    # Relationship attributes on the model instance
    setattr(m, "concept", concept)
    setattr(m, "prop", prop)
    return m


# -----------------------------
# to_domain
# -----------------------------


def test_to_domain_maps_scalars_and_nested_when_loaded(monkeypatch):
    model = _make_pc_model(
        concept=_make_concept_model(),
        prop=_make_property_model(),
    )

    # Simulate BOTH relationships LOADED: neither "concept" nor "prop" in unloaded
    fake_state = MagicMock()
    fake_state.unloaded = set()  # nothing unloaded
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.properties_concepts_mapper.attributes.instance_state",
        lambda obj: fake_state,
    )

    # Spy that nested mappers are called
    called = {"concept": False, "prop": False}

    def concept_mapper_spy(cm):
        called["concept"] = True
        # Use real concept mapper for correctness
        from app.infrastructure.persistence.sql_alchemy.mappers.concept_mapper import (
            to_domain as real,
        )

        return real(cm)

    def prop_mapper_spy(pm):
        called["prop"] = True
        # Use real property mapper for correctness
        from app.infrastructure.persistence.sql_alchemy.mappers.property_mapper import (
            to_domain as real,
        )

        return real(pm)

    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.properties_concepts_mapper.concept_to_domain",
        concept_mapper_spy,
    )
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.properties_concepts_mapper.prop_to_domain",
        prop_mapper_spy,
    )

    domain = to_domain(model)

    assert isinstance(domain, PropertiesConcepts)
    # Scalars
    assert domain.id == model.id
    assert domain.concept_id == model.concept_id
    assert domain.property_id == model.property_id
    assert domain.enabled is True
    # Nested mapped
    assert domain.concept is not None
    assert domain.prop is not None
    assert called == {"concept": True, "prop": True}


def test_to_domain_concept_unloaded_keeps_concept_none(monkeypatch):
    model = _make_pc_model(
        concept=_make_concept_model(),
        prop=_make_property_model(),
    )

    # "concept" is UNLOADED, "prop" is LOADED
    fake_state = MagicMock()
    fake_state.unloaded = {"concept"}
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.properties_concepts_mapper.attributes.instance_state",
        lambda obj: fake_state,
    )

    # Ensure we don't call concept mapper
    called = {"concept": False}

    def concept_mapper_spy(cm):
        called["concept"] = True
        from app.infrastructure.persistence.sql_alchemy.mappers.concept_mapper import (
            to_domain as real,
        )

        return real(cm)

    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.properties_concepts_mapper.concept_to_domain",
        concept_mapper_spy,
    )

    domain = to_domain(model)

    assert domain.concept is None
    # prop should get mapped since it's loaded and present
    assert domain.prop is not None
    assert called["concept"] is False


def test_to_domain_prop_unloaded_keeps_prop_none(monkeypatch):
    model = _make_pc_model(
        concept=_make_concept_model(),
        prop=_make_property_model(),
    )

    # "prop" is UNLOADED, "concept" is LOADED
    fake_state = MagicMock()
    fake_state.unloaded = {"prop"}
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.properties_concepts_mapper.attributes.instance_state",
        lambda obj: fake_state,
    )

    # Ensure we don't call prop mapper
    called = {"prop": False}

    def prop_mapper_spy(pm):
        called["prop"] = True
        from app.infrastructure.persistence.sql_alchemy.mappers.property_mapper import (
            to_domain as real,
        )

        return real(pm)

    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.properties_concepts_mapper.prop_to_domain",
        prop_mapper_spy,
    )

    domain = to_domain(model)

    assert domain.prop is None
    # concept should be mapped
    assert domain.concept is not None
    assert called["prop"] is False


def test_to_domain_loaded_but_values_none(monkeypatch):
    model = _make_pc_model(concept=None, prop=None)

    # Both relationships LOADED, but values are None
    fake_state = MagicMock()
    fake_state.unloaded = set()
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.properties_concepts_mapper.attributes.instance_state",
        lambda obj: fake_state,
    )

    domain = to_domain(model)

    assert domain.concept is None
    assert domain.prop is None
    # Scalars still mapped
    assert domain.id == model.id
    assert domain.enabled is True


# -----------------------------
# to_model
# -----------------------------


def test_to_model_maps_all_scalars():
    entity = PropertiesConcepts(
        id=77,
        concept_id=5,
        property_id=9,
        enabled=False,
        concept=None,
        prop=None,
    )

    model = to_model(entity)

    assert isinstance(model, PropertiesConceptsModel)
    assert model.id == 77
    assert model.concept_id == 5
    assert model.property_id == 9
    assert model.enabled is False


# -----------------------------
# Round-trip scalars
# -----------------------------


def test_round_trip_scalars_ignores_nested_on_to_model(monkeypatch):
    """
    Nested entities are intentionally not persisted by to_model.
    Ensure round-trip preserves scalar fields while nested stay None after to_domain.
    """
    entity = PropertiesConcepts(
        id=10,
        concept_id=1,
        property_id=2,
        enabled=True,
        concept=None,
        prop=None,
    )

    model = to_model(entity)
    model.prop = None
    model.concept = None

    # Simulate loader with both relationships loaded, but model has None values.
    fake_state = MagicMock()
    fake_state.unloaded = set()
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.mappers.properties_concepts_mapper.attributes.instance_state",
        lambda obj: fake_state,
    )

    back = to_domain(model)

    assert back.id == entity.id
    assert back.concept_id == entity.concept_id
    assert back.property_id == entity.property_id
    assert back.enabled is True
    assert back.concept is None
    assert back.prop is None
