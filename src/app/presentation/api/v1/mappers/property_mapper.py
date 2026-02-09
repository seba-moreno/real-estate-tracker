from fastapi import HTTPException
from app.core.domain.entities.property import Property
from app.presentation.api.v1.schemas.property import PropertyBase, PropertyResponse


def domain_to_response_schema(entity: Property) -> PropertyResponse:
    if entity.id is None:
        raise HTTPException(status_code=500, detail="Cannot map a Property with no id")
    return PropertyResponse(
        id=entity.id,
        location=entity.location,
        area=entity.area,
        valuation=entity.valuation,
        details=entity.details,
    )


def domain_list_to_response_schemas(entities: list[Property]) -> list[PropertyResponse]:
    return [domain_to_response_schema(e) for e in entities]


def schema_to_domain(dto: PropertyBase) -> Property:
    return Property(id=None, **dto.model_dump())
