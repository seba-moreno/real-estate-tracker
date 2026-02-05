from app.core.domain.entities.property import Property
from app.infrastructure.persistence.sql_alchemy.models.property_model import (
    PropertyModel,
)


def to_domain(model: PropertyModel) -> Property:
    return Property(
        id=model.id,
        location=model.location,
        area=model.area,
        valuation=model.valuation,
        details=model.details,
    )


def to_model(entity: Property) -> PropertyModel:
    return PropertyModel(
        id=entity.id,
        location=entity.location,
        area=entity.area,
        valuation=entity.valuation,
        details=entity.details,
    )
