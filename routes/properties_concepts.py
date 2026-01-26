from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.properties_concepts import CreatePropertiesConcepts, PropertiesConceptsResponse, UpdatePropertiesConcepts
from services.properties_concepts_service import PropertiesConceptsService

router = APIRouter()

@router.get("/{properties_concepts_id}", response_model=PropertiesConceptsResponse, status_code=status.HTTP_200_OK)
def get_properties_concepts(properties_concepts_id: int, db: Session = Depends(get_db)):
    service = PropertiesConceptsService(db)
    return service.get_properties_concepts_by_id(properties_concepts_id)

@router.get("/", response_model=List[PropertiesConceptsResponse], status_code=status.HTTP_200_OK)
def list_properties_conceptss(db: Session = Depends(get_db)):
    service = PropertiesConceptsService(db)
    return service.get_all_properties_conceptss()

@router.post("/", response_model=PropertiesConceptsResponse, status_code=status.HTTP_201_CREATED)
def create_properties_concepts(properties_concepts: CreatePropertiesConcepts, db: Session = Depends(get_db)):
    service = PropertiesConceptsService(db)
    return service.create_properties_concepts(properties_concepts)

@router.put("/{properties_concepts_id}", response_model=PropertiesConceptsResponse, status_code=status.HTTP_200_OK)
def update_properties_concepts(properties_concepts_id: int, properties_concepts: UpdatePropertiesConcepts, db: Session = Depends(get_db)):
    service = PropertiesConceptsService(db)
    return service.update_properties_concepts(properties_concepts_id, properties_concepts)

@router.delete("/{properties_concepts_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_properties_concepts(properties_concepts_id: int, db: Session = Depends(get_db)):
    service = PropertiesConceptsService(db)
    service.delete_properties_concepts(properties_concepts_id)