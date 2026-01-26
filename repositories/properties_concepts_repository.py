from typing import List, Optional
from sqlalchemy.orm import Session
from models.properties_concepts import PropertiesConcepts

class PropertiesConceptsRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, properties_concepts_id: int) -> Optional[PropertiesConcepts]:
        return self.db.query(PropertiesConcepts).filter(PropertiesConcepts.id == properties_concepts_id).first()
        
    def get_all(self) -> List[PropertiesConcepts]:
        return self.db.query(PropertiesConcepts).all()
    
    def create(self, properties_concepts: PropertiesConcepts) -> PropertiesConcepts:
        new_properties_concepts = PropertiesConcepts(**properties_concepts)
        self.db.add(new_properties_concepts)
        self.db.commit()
        self.db.refresh(new_properties_concepts)
        
        return new_properties_concepts
    
    def update(self, properties_concepts_id: int, propertiesConcepts: PropertiesConcepts) -> Optional[PropertiesConcepts]:
        db_properties_concepts = self.get_by_id(properties_concepts_id)
        
        if db_properties_concepts:
            for key, value in propertiesConcepts.model_dump().items():
                setattr(db_properties_concepts, key, value)
            self.db.commit()
            self.db.refresh(db_properties_concepts)
        return db_properties_concepts
    
    def delete(self, properties_concepts_id: int) -> bool:
        db_properties_concepts = self.get_by_id(properties_concepts_id)
        
        if db_properties_concepts:
            self.db.delete(db_properties_concepts)
            self.db.commit()
            return True
        return False
    