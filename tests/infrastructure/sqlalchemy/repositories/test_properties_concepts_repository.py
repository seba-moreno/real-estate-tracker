from __future__ import annotations

from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.persistence.sql_alchemy.database import Base
from app.infrastructure.persistence.sql_alchemy.repositories.properties_concepts_repository import (
    PropertiesConceptsRepository,
)
from app.infrastructure.persistence.sql_alchemy.models.concept_model import ConceptModel
from app.infrastructure.persistence.sql_alchemy.models.property_model import (
    PropertyModel,
)
from app.infrastructure.persistence.sql_alchemy.models.properties_concepts_model import (
    PropertiesConceptsModel,
)


@pytest.fixture
def in_memory_db(monkeypatch):
    """
    Create an in-memory SQLite engine and patch the SessionLocal used by
    SqlAlchemyRepository so this repository uses the isolated DB.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
    )

    # Ensure all involved models are imported so they are registered on Base
    # (ConceptModel, PropertyModel, PropertiesConceptsModel)
    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )

    # Patch the SessionLocal that the generic SqlAlchemyRepository uses internally
    monkeypatch.setattr(
        "app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository.SessionLocal",
        TestSessionLocal,
        raising=False,
    )

    try:
        yield TestSessionLocal
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repo(in_memory_db) -> PropertiesConceptsRepository:
    return PropertiesConceptsRepository()


def _seed_concept(
    SessionLocal,
    *,
    name: str,
    is_ordinary: bool,
    periodicity: int | None,
    description: str | None,
) -> int:
    with SessionLocal() as db:
        row = ConceptModel(
            name=name,
            is_ordinary=is_ordinary,
            periodicity=periodicity,
            description=description,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id  # type: ignore[return-value]


def _seed_property(
    SessionLocal, *, location: str, area: int | None, valuation, details: str | None
) -> int:
    with SessionLocal() as db:
        row = PropertyModel(
            location=location,
            area=area,
            valuation=valuation,  # Numeric/Decimal-compatible
            details=details,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id  # type: ignore[return-value]


def _seed_pc(SessionLocal, *, concept_id: int, property_id: int, enabled: bool) -> int:
    with SessionLocal() as db:
        row = PropertiesConceptsModel(
            concept_id=concept_id,
            property_id=property_id,
            enabled=enabled,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id  # type: ignore[return-value]


def test_get_with_navigations_returns_nested_entities(
    repo: PropertiesConceptsRepository, in_memory_db
):
    """
    Ensures get_with_navigations() returns PropertiesConcepts domain objects
    with nested concept and property mapped (not None) and values consistent
    with the seed data.
    """
    SessionLocal = in_memory_db  # the patched sessionmaker

    # Seed one concept, one property, and their relation
    concept_id = _seed_concept(
        SessionLocal,
        name="Lease",
        is_ordinary=True,
        periodicity=1,
        description="Monthly lease",
    )
    property_id = _seed_property(
        SessionLocal,
        location="Main St 123",
        area=50,
        valuation=Decimal("100000.00"),
        details=None,
    )
    pc_id = _seed_pc(
        SessionLocal, concept_id=concept_id, property_id=property_id, enabled=True
    )

    # Execute
    results = repo.get_with_navigations()

    # Validate
    assert isinstance(results, list)
    assert len(results) == 1

    item = results[0]
    assert item.id == pc_id
    assert item.concept_id == concept_id
    assert item.property_id == property_id
    assert item.enabled is True

    # Nested domain entities should be present and consistent with seed values
    assert item.concept is not None
    assert item.concept.id == concept_id
    assert item.concept.name == "Lease"
    assert item.concept.is_ordinary is True
    assert item.concept.periodicity == 1
    assert item.concept.description == "Monthly lease"

    assert item.prop is not None
    assert item.prop.id == property_id
    assert item.prop.location == "Main St 123"
    assert item.prop.area == 50
    assert item.prop.valuation == Decimal("100000.00")
    assert item.prop.details is None


def test_get_with_navigations_empty_returns_empty_list(
    repo: PropertiesConceptsRepository,
):
    results = repo.get_with_navigations()
    assert results == []
