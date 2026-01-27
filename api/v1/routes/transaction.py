from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.transaction import CreateTransaction, TransactionResponse, UpdateTransaction
from services.transaction_service import TransactionService

router = APIRouter(prefix="/transaction", tags=["Transaction"])

@router.get("/{transaction_id}", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.get_transaction_by_id(transaction_id)

@router.get("/", response_model=List[TransactionResponse], status_code=status.HTTP_200_OK)
def list_transactions(db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.get_all_transactions()

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: CreateTransaction, db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.create_transaction(transaction)

@router.put("/{transaction_id}", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
def update_transaction(transaction_id: int, transaction: UpdateTransaction, db: Session = Depends(get_db)):
    service = TransactionService(db)
    return service.update_transaction(transaction_id, transaction)

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    service = TransactionService(db)
    service.delete_transaction(transaction_id)