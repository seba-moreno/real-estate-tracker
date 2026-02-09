from fastapi import HTTPException
from app.core.domain.entities.properties_concepts import PropertiesConcepts
from app.presentation.api.v1.schemas.properties_concepts import (
    PropertiesConceptsBase,
    PropertiesConceptsResponse,
)
from app.presentation.api.v1.mappers.property_mapper import (
    domain_to_response_schema as prop_domain_to_response_schema,
)
from app.presentation.api.v1.mappers.concept_mapper import (
    domain_to_response_schema as concept_domain_to_response_schema,
)


def domain_to_response_schema(entity: PropertiesConcepts) -> PropertiesConceptsResponse:
    if entity.id is None:
        raise HTTPException(
            status_code=500, detail="Cannot map a Property Concept with no id"
        )
    return PropertiesConceptsResponse(
        id=entity.id,
        concept_id=entity.concept_id,
        property_id=entity.property_id,
        enabled=entity.enabled,
        concept=concept_domain_to_response_schema(entity.concept)
        if entity.concept
        else None,
        property=prop_domain_to_response_schema(entity.prop) if entity.prop else None,
    )


def domain_list_to_response_schemas(
    entities: list[PropertiesConcepts],
) -> list[PropertiesConceptsResponse]:
    return [domain_to_response_schema(e) for e in entities]


def schema_to_domain(dto: PropertiesConceptsBase) -> PropertiesConcepts:
    return PropertiesConcepts(id=None, **dto.model_dump())
