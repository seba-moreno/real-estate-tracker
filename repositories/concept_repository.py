from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.concept import Concept
from repositories.base_repository import BaseRepository
from schemas.concept import ConceptResponse, CreateConcept, UpdateConcept


class ConceptRepository(BaseRepository[ConceptResponse]):
    dto_model = ConceptResponse

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, concept_id: int) -> Optional[ConceptResponse]:
        result = self.db.get(Concept, concept_id)

        if not result:
            return None

        return self.to_dto(result)

    def get_all(self) -> list[ConceptResponse]:
        results = self.db.query(Concept).all()
        return self.to_dto_list(results)

    def create(self, concept: CreateConcept) -> ConceptResponse:
        new_concept = Concept(**concept.model_dump())

        try:
            self.db.add(new_concept)
            self.db.commit()
            self.db.refresh(new_concept)

        except SQLAlchemyError:
            self.db.rollback()

        return self.to_dto(new_concept)

    def update(self, concept_id: int, concept: UpdateConcept) -> ConceptResponse:
        db_concept = self.db.get(Concept, concept_id)

        if db_concept:
            for key, value in concept.model_dump().items():
                setattr(db_concept, key, value)

            try:
                self.db.commit()
                self.db.refresh(db_concept)
            except SQLAlchemyError:
                self.db.rollback()
        return self.to_dto(db_concept)

    def delete(self, concept_id: int) -> bool:
        db_concept = self.db.get(Concept, concept_id)

        if db_concept:
            try:
                self.db.delete(db_concept)
                self.db.commit()
                return True
            except SQLAlchemyError:
                self.db.rollback()
                return False
        return False
