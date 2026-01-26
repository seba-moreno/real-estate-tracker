from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from core.dependencies.logger import get_request_logger
from repositories.property_repository import PropertyRepository
from schemas.property import PropertyResponse, CreateProperty, UpdateProperty

class PropertyService:
    def __init__(self, db: Session, logger = Depends(get_request_logger)):
        self.property_repository = PropertyRepository(db)
        self.logger = logger

    def get_property_by_id(self, property_id: int) -> Optional[PropertyResponse]:
        existing_property = self.property_repository.get_by_id(property_id)

        if not existing_property:
            self.logger.warning("Get by id failed: Property not found", extra={"property_id": property_id})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        return existing_property
    
    def get_all_propertys(self) -> List[PropertyResponse]:
        return self.property_repository.get_all()

    def create_property(self, property: CreateProperty) -> PropertyResponse:
        payload = property.model_dump()
        self.logger.info("Creating Property", extra={"data": payload})
        
        try:
            created_property = self.property_repository.create(property)
            self.logger.info("Property created successfully", extra={"data": created_property.model_dump()})
            return created_property
        except Exception:
            self.logger.exception("Failed to create Property", extra={"data": payload})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the property"
            )

    def update_property(self, property_id: int, property: UpdateProperty) -> PropertyResponse:
        existing_property = self.property_repository.get_by_id(property_id)
        
        if not existing_property:
            self.logger.warning("Update failed: Property not found", extra={"property_id": property_id})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        payload = property.model_dump()
        self.logger.info("Updating property", extra={"property_id": property_id, "data": payload})

        try:
            updated_property = self.property_repository.update(property_id, property)
            self.logger.info("Property updated successfully", extra={"data": updated_property.model_dump()})
            return updated_property
        except Exception:
            self.logger.exception("Failed to update Property", extra={"property_id": property_id, "data": payload})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the property"
            )

        
    def delete_property(self, property_id: int) -> None:
        self.logger.info("Removing property", extra={"property_id": property_id})
        existing_property = self.property_repository.get_by_id(property_id)

        if not existing_property:
            self.logger.warning("Delete failed: Property not found", extra={"property_id": property_id})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        try:
            if not self.property_repository.delete(property_id):
                self.logger.error("Failed to delete Property", extra={"property_id": property_id})
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred while deleting the property"
                )
            
            self.logger.info("Property deleted successfully", extra={"property_id": property_id})
        except Exception:
            self.logger.exception("Failed to delete Property", extra={"property_id": property_id})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting the property"
            )
