from typing import Optional
from sqlalchemy.orm import Session
from models.properties_concepts import PropertiesConcepts
from repositories.base_repository import BaseRepository
from schemas.properties_concepts import (
    CreatePropertiesConcepts,
    PropertiesConceptsResponse,
    UpdatePropertiesConcepts,
)
from sqlalchemy.exc import SQLAlchemyError


class PropertiesConceptsRepository(BaseRepository[PropertiesConceptsResponse]):
    dto_model = PropertiesConceptsResponse

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(
        self, properties_concepts_id: int
    ) -> Optional[PropertiesConceptsResponse]:
        result = self.db.get(PropertiesConcepts, properties_concepts_id)

        if not result:
            return None

        return self.to_dto(result)

    def get_all(self) -> list[PropertiesConceptsResponse]:
        results = self.db.query(PropertiesConcepts).all()
        return self.to_dto_list(results)

    def create(
        self, properties_concepts: CreatePropertiesConcepts
    ) -> PropertiesConceptsResponse:
        new_properties_concepts = PropertiesConcepts(**properties_concepts.model_dump())

        try:
            self.db.add(new_properties_concepts)
            self.db.commit()
            self.db.refresh(new_properties_concepts)

        except SQLAlchemyError:
            self.db.rollback()

        return self.to_dto(new_properties_concepts)

    def update(
        self, properties_concepts_id: int, propertiesConcepts: UpdatePropertiesConcepts
    ) -> PropertiesConceptsResponse:
        db_properties_concepts = self.db.get(PropertiesConcepts, properties_concepts_id)

        if db_properties_concepts:
            for key, value in propertiesConcepts.model_dump().items():
                setattr(db_properties_concepts, key, value)

            try:
                self.db.commit()
                self.db.refresh(db_properties_concepts)
            except SQLAlchemyError:
                self.db.rollback()
        return self.to_dto(db_properties_concepts)

    def delete(self, properties_concepts_id: int) -> bool:
        db_properties_concepts = self.db.get(PropertiesConcepts, properties_concepts_id)

        if db_properties_concepts:
            try:
                self.db.delete(db_properties_concepts)
                self.db.commit()
                return True
            except SQLAlchemyError:
                self.db.rollback()
                return False
        return False
