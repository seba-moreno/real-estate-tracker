from typing import List, Optional
from sqlalchemy.orm import Session
from models.concept import Concept

class ContractRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, concept_id: int) -> Optional[Concept]:
        return self.db.query(Concept).filter(Concept.id == concept_id).first()
        
    def get_all(self) -> List[Concept]:
        return self.db.query(Concept).all()
    
    def create(self, concept: Concept) -> Concept:
        new_concept = Concept(**concept)
        self.db.add(new_concept)
        self.db.commit()
        self.db.refresh(new_concept)
        
        return new_concept
    
    def update(self, concept_id: int, concept: Concept) -> Optional[Concept]:
        db_concept = self.get_by_id(concept_id)
        
        if db_concept:
            for key, value in concept.model_dump().items():
                setattr(db_concept, key, value)
            self.db.commit()
            self.db.refresh(db_concept)
        return db_concept
    
    def delete(self, concept_id: int) -> bool:
        db_concept = self.get_by_id(concept_id)
        
        if db_concept:
            self.db.delete(db_concept)
            self.db.commit()
            return True
        return False
    