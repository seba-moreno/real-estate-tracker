from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from core.dependencies.logger import get_request_logger
from core.logging.logger_with_correlation_id import CorrelationLoggerAdapter
from repositories.concept_repository import ConceptRepository
from schemas.concept import ConceptResponse, CreateConcept, UpdateConcept


class ConceptService:
    def __init__(
        self,
        db: Session,
        logger: CorrelationLoggerAdapter = Depends(get_request_logger),
    ) -> None:
        self.concept_repository = ConceptRepository(db)
        self.logger = logger

    def get_concept_by_id(self, concept_id: int) -> Optional[ConceptResponse]:
        existing_concept = self.concept_repository.get_by_id(concept_id)

        if not existing_concept:
            self.logger.warning(
                "Get by id failed: Concept not found", extra={"concept_id": concept_id}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found"
            )

        return existing_concept

    def get_all_concepts(self) -> list[ConceptResponse]:
        return self.concept_repository.get_all()

    def create_concept(self, concept: CreateConcept) -> ConceptResponse:
        payload = concept.model_dump()
        self.logger.info("Creating concept", extra={"data": payload})

        try:
            created_concept = self.concept_repository.create(concept)
            self.logger.info(
                "Concept created successfully",
                extra={"data": created_concept.model_dump()},
            )
            return created_concept
        except Exception:
            self.logger.exception("Failed to create Concept", extra={"data": payload})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the concept",
            )

    def update_concept(
        self, concept_id: int, concept: UpdateConcept
    ) -> ConceptResponse:
        existing_concept = self.concept_repository.get_by_id(concept_id)

        if not existing_concept:
            self.logger.warning(
                "Update failed: Concept not found", extra={"concept_id": concept_id}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found"
            )

        payload = concept.model_dump()
        self.logger.info(
            "Updating concept", extra={"concept_id": concept_id, "data": payload}
        )

        try:
            updated_concept = self.concept_repository.update(concept_id, concept)
            self.logger.info(
                "Concept updated successfully",
                extra={"data": updated_concept.model_dump()},
            )
            return updated_concept
        except Exception:
            self.logger.exception(
                "Failed to update Concept",
                extra={"concept_id": concept_id, "data": payload},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the concept",
            )

    def delete_concept(self, concept_id: int) -> None:
        self.logger.info("Removing concept", extra={"concept_id": concept_id})
        existing_concept = self.concept_repository.get_by_id(concept_id)

        if not existing_concept:
            self.logger.warning(
                "Delete failed: Concept not found", extra={"concept_id": concept_id}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found"
            )

        try:
            if not self.concept_repository.delete(concept_id):
                self.logger.error(
                    "Failed to delete Concept", extra={"concept_id": concept_id}
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred while deleting the concept",
                )

            self.logger.info(
                "Concept deleted successfully", extra={"concept_id": concept_id}
            )
        except Exception:
            self.logger.exception(
                "Failed to delete Concept", extra={"concept_id": concept_id}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting the concept",
            )
