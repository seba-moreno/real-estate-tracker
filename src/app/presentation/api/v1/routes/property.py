from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from app.core.domain.entities.property import Property
from app.core.interfaces.services.base_service import IBaseService
from app.infrastructure.containers.root_container import RootContainer
from app.presentation.api.v1.mappers.property_mapper import (
    domain_list_to_response_schemas,
    domain_to_response_schema,
    schema_to_domain,
)
from app.presentation.api.v1.schemas.property import PropertyBase, PropertyResponse

router = APIRouter(prefix="/property", tags=["Property"])


@router.get(
    "/{property_id}", response_model=PropertyResponse, status_code=status.HTTP_200_OK
)
@inject
def get_property(
    property_id: int,
    service: IBaseService[Property] = Depends(
        Provide[RootContainer.services.property_service]
    ),
) -> PropertyResponse | None:
    domain_entity = service.get_by_id(property_id)
    if domain_entity is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return domain_to_response_schema(domain_entity)


@router.get("/", response_model=list[PropertyResponse], status_code=status.HTTP_200_OK)
@inject
def list_properties(
    service: IBaseService[Property] = Depends(
        Provide[RootContainer.services.property_service]
    ),
) -> list[PropertyResponse]:
    result = service.get_all()
    return domain_list_to_response_schemas(result)


@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_property(
    property: PropertyBase,
    service: IBaseService[Property] = Depends(
        Provide[RootContainer.services.property_service]
    ),
) -> PropertyResponse:
    domain_entity = schema_to_domain(property)
    result = service.create(domain_entity)
    return domain_to_response_schema(result)


@router.put(
    "/{property_id}", response_model=PropertyResponse, status_code=status.HTTP_200_OK
)
@inject
def update_property(
    property_id: int,
    property: PropertyBase,
    service: IBaseService[Property] = Depends(
        Provide[RootContainer.services.property_service]
    ),
) -> PropertyResponse:
    domain_entity = schema_to_domain(property)
    result = service.update(property_id, domain_entity)
    return domain_to_response_schema(result)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_property(
    property_id: int,
    service: IBaseService[Property] = Depends(
        Provide[RootContainer.services.property_service]
    ),
) -> None:
    service.delete(property_id)
