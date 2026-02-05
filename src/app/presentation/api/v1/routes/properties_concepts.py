from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide
from app.core.interfaces.services.properties_concepts_service import (
    IPropertiesConceptsService,
)
from app.infrastructure.containers.root_container import RootContainer
from app.presentation.api.v1.mappers.properties_concepts_mapper import (
    domain_list_to_response_schemas,
    domain_to_response_schema,
    schema_to_domain,
)
from app.presentation.api.v1.schemas.properties_concepts import (
    PropertiesConceptsResponse,
    PropertiesConceptsBase,
)


router = APIRouter(prefix="/properties-concepts", tags=["Properties Concepts"])


@router.get(
    "/get-combos",
    response_model=list[PropertiesConceptsResponse],
    status_code=status.HTTP_200_OK,
)
@inject
def list_properties_concepts_combos(
    service: IPropertiesConceptsService = Depends(
        Provide[RootContainer.services.properties_concepts_service]
    ),
) -> list[PropertiesConceptsResponse]:
    result = service.get_combos()
    return domain_list_to_response_schemas(result)


@router.get(
    "/{properties_concepts_id}",
    response_model=PropertiesConceptsResponse,
    status_code=status.HTTP_200_OK,
)
@inject
def get_properties_concepts(
    properties_concepts_id: int,
    service: IPropertiesConceptsService = Depends(
        Provide[RootContainer.services.properties_concepts_service]
    ),
) -> PropertiesConceptsResponse | None:
    domain_entity = service.get_by_id(properties_concepts_id)
    assert domain_entity is not None
    return domain_to_response_schema(domain_entity)


@router.get(
    "/", response_model=list[PropertiesConceptsResponse], status_code=status.HTTP_200_OK
)
@inject
def list_properties_concepts(
    service: IPropertiesConceptsService = Depends(
        Provide[RootContainer.services.properties_concepts_service]
    ),
) -> list[PropertiesConceptsResponse]:
    result = service.get_all()
    return domain_list_to_response_schemas(result)


@router.post(
    "/", response_model=PropertiesConceptsResponse, status_code=status.HTTP_201_CREATED
)
@inject
def create_properties_concepts(
    properties_concepts: PropertiesConceptsBase,
    service: IPropertiesConceptsService = Depends(
        Provide[RootContainer.services.properties_concepts_service]
    ),
) -> PropertiesConceptsResponse:
    domain_entity = schema_to_domain(properties_concepts)
    result = service.create(domain_entity)
    return domain_to_response_schema(result)


@router.put(
    "/{properties_concepts_id}",
    response_model=PropertiesConceptsResponse,
    status_code=status.HTTP_200_OK,
)
@inject
def update_properties_concepts(
    properties_concepts_id: int,
    properties_concepts: PropertiesConceptsBase,
    service: IPropertiesConceptsService = Depends(
        Provide[RootContainer.services.properties_concepts_service]
    ),
) -> PropertiesConceptsResponse:
    domain_entity = schema_to_domain(properties_concepts)
    result = service.update(properties_concepts_id, domain_entity)
    return domain_to_response_schema(result)


@router.delete("/{properties_concepts_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_properties_concepts(
    properties_concepts_id: int,
    service: IPropertiesConceptsService = Depends(
        Provide[RootContainer.services.properties_concepts_service]
    ),
) -> None:
    service.delete(properties_concepts_id)
