from sqlalchemy.orm import Session
from models.property import Property
from repositories.base_repository import BaseRepository
from schemas.property import CreateProperty, PropertyResponse, UpdateProperty
from sqlalchemy.exc import SQLAlchemyError


class PropertyRepository(BaseRepository[PropertyResponse]):
    dto_model = PropertyResponse

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, property_id: int) -> None | PropertyResponse:
        result = self.db.get(Property, property_id)

        if not result:
            return None

        return self.to_dto(result)

    def get_all(self) -> list[PropertyResponse]:
        results = self.db.query(Property).all()
        return self.to_dto_list(results)

    def create(self, property: CreateProperty) -> PropertyResponse:
        new_property = Property(**property.model_dump())

        try:
            self.db.add(new_property)
            self.db.commit()
            self.db.refresh(new_property)

        except SQLAlchemyError:
            self.db.rollback()

        return self.to_dto(new_property)

    def update(self, property_id: int, property: UpdateProperty) -> PropertyResponse:
        db_property = self.db.get(Property, property_id)

        if db_property:
            for key, value in property.model_dump().items():
                setattr(db_property, key, value)

            try:
                self.db.commit()
                self.db.refresh(db_property)
            except SQLAlchemyError:
                self.db.rollback()
        return self.to_dto(db_property)

    def delete(self, property_id: int) -> bool:
        db_property = self.db.get(Property, property_id)

        if db_property:
            try:
                self.db.delete(db_property)
                self.db.commit()
                return True
            except SQLAlchemyError:
                self.db.rollback()
                return False
        return False
