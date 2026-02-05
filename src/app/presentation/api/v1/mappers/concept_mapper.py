from app.core.domain.entities.concept import Concept
from app.presentation.api.v1.schemas.concept import ConceptBase, ConceptResponse


def domain_to_response_schema(entity: Concept) -> ConceptResponse:
    assert entity.id is not None
    return ConceptResponse(
        id=entity.id,
        name=entity.name,
        is_ordinary=entity.is_ordinary,
        periodicity=entity.periodicity,
        description=entity.description,
    )


def domain_list_to_response_schemas(entities: list[Concept]) -> list[ConceptResponse]:
    return [domain_to_response_schema(e) for e in entities]


def schema_to_domain(dto: ConceptBase) -> Concept:
    return Concept(id=None, **dto.model_dump())
