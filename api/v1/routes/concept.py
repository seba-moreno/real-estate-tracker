from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.dependencies.logger import get_request_logger
from core.logging.logger_with_correlation_id import CorrelationLoggerAdapter
from database import get_db
from schemas.concept import CreateConcept, ConceptResponse, UpdateConcept
from services.concept_service import ConceptService

router = APIRouter(prefix="/concept", tags=["Concept"])


def get_concept_service(
    db: Annotated[Session, Depends(get_db)],
    logger: Annotated[CorrelationLoggerAdapter, Depends(get_request_logger)],
) -> ConceptService:
    return ConceptService(db, logger)


@router.get(
    "/{concept_id}", response_model=ConceptResponse, status_code=status.HTTP_200_OK
)
def get_concept(
    concept_id: int,
    service: Annotated[ConceptService, Depends(get_concept_service)],
) -> None | ConceptResponse:
    return service.get_concept_by_id(concept_id)


@router.get("/", response_model=list[ConceptResponse], status_code=status.HTTP_200_OK)
def list_concepts(
    service: Annotated[ConceptService, Depends(get_concept_service)],
) -> list[ConceptResponse]:
    return service.get_all_concepts()


@router.post("/", response_model=ConceptResponse, status_code=status.HTTP_201_CREATED)
def create_concept(
    concept: CreateConcept,
    service: Annotated[ConceptService, Depends(get_concept_service)],
) -> ConceptResponse:
    return service.create_concept(concept)


@router.put(
    "/{concept_id}", response_model=ConceptResponse, status_code=status.HTTP_200_OK
)
def update_concept(
    concept_id: int,
    concept: UpdateConcept,
    service: Annotated[ConceptService, Depends(get_concept_service)],
) -> ConceptResponse:
    return service.update_concept(concept_id, concept)


@router.delete("/{concept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_concept(
    concept_id: int,
    service: Annotated[ConceptService, Depends(get_concept_service)],
) -> None:
    service.delete_concept(concept_id)
