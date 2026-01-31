from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.dependencies.logger import get_request_logger
from core.logging.logger_with_correlation_id import CorrelationLoggerAdapter
from database import get_db
from schemas.property import CreateProperty, PropertyResponse, UpdateProperty
from services.property_service import PropertyService

router = APIRouter(prefix="/property", tags=["Property"])


def get_property_service(
    db: Annotated[Session, Depends(get_db)],
    logger: Annotated[CorrelationLoggerAdapter, Depends(get_request_logger)],
) -> PropertyService:
    return PropertyService(db, logger)


@router.get(
    "/{property_id}", response_model=PropertyResponse, status_code=status.HTTP_200_OK
)
def get_property(
    property_id: int,
    service: Annotated[PropertyService, Depends(get_property_service)],
) -> None | PropertyResponse:
    return service.get_property_by_id(property_id)


@router.get("/", response_model=list[PropertyResponse], status_code=status.HTTP_200_OK)
def list_propertys(
    service: Annotated[PropertyService, Depends(get_property_service)],
) -> list[PropertyResponse]:
    return service.get_all_properties()


@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(
    property: CreateProperty,
    service: Annotated[PropertyService, Depends(get_property_service)],
) -> PropertyResponse:
    return service.create_property(property)


@router.put(
    "/{property_id}", response_model=PropertyResponse, status_code=status.HTTP_200_OK
)
def update_property(
    property_id: int,
    property: UpdateProperty,
    service: Annotated[PropertyService, Depends(get_property_service)],
) -> PropertyResponse:
    return service.update_property(property_id, property)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    service: Annotated[PropertyService, Depends(get_property_service)],
) -> None:
    service.delete_property(property_id)
