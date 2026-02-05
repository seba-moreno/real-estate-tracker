from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide
from app.core.domain.entities.concept import Concept
from app.core.interfaces.services.base_service import IBaseService
from app.infrastructure.containers.root_container import RootContainer
from app.presentation.api.v1.mappers.concept_mapper import (
    domain_list_to_response_schemas,
    domain_to_response_schema,
    schema_to_domain,
)
from app.presentation.api.v1.schemas.concept import ConceptBase, ConceptResponse

router = APIRouter(prefix="/concept", tags=["Concept"])


@router.get(
    "/{concept_id}", response_model=ConceptResponse, status_code=status.HTTP_200_OK
)
@inject
def get_concept(
    concept_id: int,
    service: IBaseService[Concept] = Depends(
        Provide[RootContainer.services.concept_service]
    ),
) -> ConceptResponse | None:
    domain_entity = service.get_by_id(concept_id)
    assert domain_entity is not None
    return domain_to_response_schema(domain_entity)


@router.get("/", response_model=list[ConceptResponse], status_code=status.HTTP_200_OK)
@inject
def list_concepts(
    service: IBaseService[Concept] = Depends(
        Provide[RootContainer.services.concept_service]
    ),
) -> list[ConceptResponse]:
    result = service.get_all()
    return domain_list_to_response_schemas(result)


@router.post("/", response_model=ConceptResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_concept(
    concept: ConceptBase,
    service: IBaseService[Concept] = Depends(
        Provide[RootContainer.services.concept_service]
    ),
) -> ConceptResponse:
    domain_entity = schema_to_domain(concept)
    result = service.create(domain_entity)
    return domain_to_response_schema(result)


@router.put(
    "/{concept_id}", response_model=ConceptResponse, status_code=status.HTTP_200_OK
)
@inject
def update_concept(
    concept_id: int,
    concept: ConceptBase,
    service: IBaseService[Concept] = Depends(
        Provide[RootContainer.services.concept_service]
    ),
) -> ConceptResponse:
    domain_entity = schema_to_domain(concept)
    result = service.update(concept_id, domain_entity)
    return domain_to_response_schema(result)


@router.delete("/{concept_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_concept(
    concept_id: int,
    service: IBaseService[Concept] = Depends(
        Provide[RootContainer.services.concept_service]
    ),
) -> None:
    service.delete(concept_id)
