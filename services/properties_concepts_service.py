from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.logging.logger_with_correlation_id import CorrelationLoggerAdapter
from repositories.properties_concepts_repository import PropertiesConceptsRepository
from schemas.properties_concepts import (
    CreatePropertiesConcepts,
    PropertiesConceptsResponse,
    UpdatePropertiesConcepts,
)


class PropertiesConceptsService:
    def __init__(
        self,
        db: Session,
        logger: CorrelationLoggerAdapter,
    ) -> None:
        self.properties_concepts_repository = PropertiesConceptsRepository(db)
        self.logger = logger

    def get_properties_concepts_by_id(
        self, properties_concepts_id: int
    ) -> None | PropertiesConceptsResponse:
        existing_properties_concepts = self.properties_concepts_repository.get_by_id(
            properties_concepts_id
        )

        if not existing_properties_concepts:
            self.logger.warning(
                "Get by id failed: PropertiesConcepts not found",
                extra={"properties_concepts_id": properties_concepts_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PropertiesConcepts not found",
            )

        return existing_properties_concepts

    def get_all_properties_conceptss(self) -> list[PropertiesConceptsResponse]:
        return self.properties_concepts_repository.get_all()

    def create_properties_concepts(
        self, properties_concepts: CreatePropertiesConcepts
    ) -> PropertiesConceptsResponse:
        payload = properties_concepts.model_dump()
        self.logger.info("Creating PropertiesConcepts", extra={"data": payload})

        try:
            created_properties_concepts = self.properties_concepts_repository.create(
                properties_concepts
            )
            self.logger.info(
                "PropertiesConcepts created successfully",
                extra={"data": created_properties_concepts.model_dump()},
            )
            return created_properties_concepts
        except Exception:
            self.logger.exception(
                "Failed to create PropertiesConcepts", extra={"data": payload}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the properties_concepts",
            )

    def update_properties_concepts(
        self, properties_concepts_id: int, properties_concepts: UpdatePropertiesConcepts
    ) -> PropertiesConceptsResponse:
        existing_properties_concepts = self.properties_concepts_repository.get_by_id(
            properties_concepts_id
        )

        if not existing_properties_concepts:
            self.logger.warning(
                "Update failed: PropertiesConcepts not found",
                extra={"properties_concepts_id": properties_concepts_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PropertiesConcepts not found",
            )

        payload = properties_concepts.model_dump()
        self.logger.info(
            "Updating properties_concepts",
            extra={"properties_concepts_id": properties_concepts_id, "data": payload},
        )

        try:
            updated_properties_concepts = self.properties_concepts_repository.update(
                properties_concepts_id, properties_concepts
            )
            self.logger.info(
                "PropertiesConcepts updated successfully",
                extra={"data": updated_properties_concepts.model_dump()},
            )
            return updated_properties_concepts
        except Exception:
            self.logger.exception(
                "Failed to update PropertiesConcepts",
                extra={
                    "properties_concepts_id": properties_concepts_id,
                    "data": payload,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the properties_concepts",
            )

    def delete_properties_concepts(self, properties_concepts_id: int) -> None:
        self.logger.info(
            "Removing properties_concepts",
            extra={"properties_concepts_id": properties_concepts_id},
        )
        existing_properties_concepts = self.properties_concepts_repository.get_by_id(
            properties_concepts_id
        )

        if not existing_properties_concepts:
            self.logger.warning(
                "Delete failed: PropertiesConcepts not found",
                extra={"properties_concepts_id": properties_concepts_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PropertiesConcepts not found",
            )

        try:
            if not self.properties_concepts_repository.delete(properties_concepts_id):
                self.logger.error(
                    "Failed to delete PropertiesConcepts",
                    extra={"properties_concepts_id": properties_concepts_id},
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred while deleting the properties_concepts",
                )

            self.logger.info(
                "PropertiesConcepts deleted successfully",
                extra={"properties_concepts_id": properties_concepts_id},
            )
        except Exception:
            self.logger.exception(
                "Failed to delete PropertiesConcepts",
                extra={"properties_concepts_id": properties_concepts_id},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting the properties_concepts",
            )
