from typing import List, Optional
from sqlalchemy.orm import Session
from models.concept import Concept

class ContractRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, conceptId: int) -> Optional[Concept]:
        return self.db.query(Concept).filter(Concept.id == conceptId).first()
        
    def get_all(self) -> List[Concept]:
        return self.db.query(Concept).all()
    
    def create(self, concept: Concept) -> Concept:
        newconcept = Concept(**concept)
        self.db.add(newconcept)
        self.db.commit()
        self.db.refresh(newconcept)
        
        return newconcept
    
    def update(self, conceptId: int, concept: Concept) -> Optional[Concept]:
        db_concept = self.get_by_id(conceptId)
        
        if db_concept:
            for key, value in concept.model_dump().items():
                setattr(db_concept, key, value)
            self.db.commit()
            self.db.refresh(db_concept)
        return db_concept
    
    def delete(self, conceptId: int) -> bool:
        db_concept = self.get_by_id(conceptId)
        
        if db_concept:
            self.db.delete(db_concept)
            self.db.commit()
            return True
        return False
    