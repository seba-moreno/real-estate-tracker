from typing import List, Optional
from sqlalchemy.orm import Session
from models.properties_concepts import PropertiesConcepts

class PropertiesConceptsRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, propertiesConceptsId: int) -> Optional[PropertiesConcepts]:
        return self.db.query(PropertiesConcepts).filter(PropertiesConcepts.id == propertiesConceptsId).first()
        
    def get_all(self) -> List[PropertiesConcepts]:
        return self.db.query(PropertiesConcepts).all()
    
    def create(self, propertiesConcepts: PropertiesConcepts) -> PropertiesConcepts:
        newpropertiesConcepts = PropertiesConcepts(**propertiesConcepts)
        self.db.add(newpropertiesConcepts)
        self.db.commit()
        self.db.refresh(newpropertiesConcepts)
        
        return newpropertiesConcepts
    
    def update(self, propertiesConceptsId: int, propertiesConcepts: PropertiesConcepts) -> Optional[PropertiesConcepts]:
        db_propertiesConcepts = self.get_by_id(propertiesConceptsId)
        
        if db_propertiesConcepts:
            for key, value in propertiesConcepts.model_dump().items():
                setattr(db_propertiesConcepts, key, value)
            self.db.commit()
            self.db.refresh(db_propertiesConcepts)
        return db_propertiesConcepts
    
    def delete(self, propertiesConceptsId: int) -> bool:
        db_propertiesConcepts = self.get_by_id(propertiesConceptsId)
        
        if db_propertiesConcepts:
            self.db.delete(db_propertiesConcepts)
            self.db.commit()
            return True
        return False
    