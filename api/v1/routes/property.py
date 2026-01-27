from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.property import CreateProperty, PropertyResponse, UpdateProperty
from services.property_service import PropertyService

router = APIRouter(prefix="/property", tags=["Property"])

@router.get("/{property_id}", response_model=PropertyResponse, status_code=status.HTTP_200_OK)
def get_property(property_id: int, db: Session = Depends(get_db)):
    service = PropertyService(db)
    return service.get_property_by_id(property_id)

@router.get("/", response_model=List[PropertyResponse], status_code=status.HTTP_200_OK)
def list_propertys(db: Session = Depends(get_db)):
    service = PropertyService(db)
    return service.get_all_properties()

@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(property: CreateProperty, db: Session = Depends(get_db)):
    service = PropertyService(db)
    return service.create_property(property)

@router.put("/{property_id}", response_model=PropertyResponse, status_code=status.HTTP_200_OK)
def update_property(property_id: int, property: UpdateProperty, db: Session = Depends(get_db)):
    service = PropertyService(db)
    return service.update_property(property_id, property)

@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(property_id: int, db: Session = Depends(get_db)):
    service = PropertyService(db)
    service.delete_property(property_id)