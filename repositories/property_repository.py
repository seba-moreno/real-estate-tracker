from typing import List, Optional
from sqlalchemy.orm import Session
from models.property import Property

class PropertyRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, property_id: int) -> Optional[Property]:
        return self.db.query(Property).filter(Property.id == property_id).first()
        
    def get_all(self) -> List[Property]:
        return self.db.query(Property).all()
    
    def create(self, property: Property) -> Property:
        new_property = Property(**property)
        self.db.add(new_property)
        self.db.commit()
        self.db.refresh(new_property)
        
        return new_property
    
    def update(self, property_id: int, property: Property) -> Optional[Property]:
        db_property = self.get_by_id(property_id)
        
        if db_property:
            for key, value in property.model_dump().items():
                setattr(db_property, key, value)
            self.db.commit()
            self.db.refresh(db_property)
        return db_property
    
    def delete(self, property_id: int) -> bool:
        db_property = self.get_by_id(property_id)
        
        if db_property:
            self.db.delete(db_property)
            self.db.commit()
            return True
        return False
    