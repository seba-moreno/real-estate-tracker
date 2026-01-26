from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.concept import CreateConcept, ConceptResponse, UpdateConcept
from services.concept_service import ConceptService

router = APIRouter(prefix="/concept", tags=["concept"])

@router.get("/{concept_id}", response_model=ConceptResponse, status_code=status.HTTP_200_OK)
def get_concept(concept_id: int, db: Session = Depends(get_db)):
    service = ConceptService(db)
    return service.get_concept_by_id(concept_id)

@router.get("/", response_model=List[ConceptResponse], status_code=status.HTTP_200_OK)
def list_concepts(db: Session = Depends(get_db)):
    service = ConceptService(db)
    return service.get_all_concepts()

@router.post("/", response_model=ConceptResponse, status_code=status.HTTP_201_CREATED)
def create_concept(concept: CreateConcept, db: Session = Depends(get_db)):
    service = ConceptService(db)
    return service.create_concept(concept)

@router.put("/{concept_id}", response_model=ConceptResponse, status_code=status.HTTP_200_OK)
def update_concept(concept_id: int, concept: UpdateConcept, db: Session = Depends(get_db)):
    service = ConceptService(db)
    return service.update_concept(concept_id, concept)

@router.delete("/{concept_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_concept(concept_id: int, db: Session = Depends(get_db)):
    service = ConceptService(db)
    service.delete_concept(concept_id)