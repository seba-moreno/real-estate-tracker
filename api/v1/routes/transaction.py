from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.dependencies.logger import get_request_logger
from core.logging.logger_with_correlation_id import CorrelationLoggerAdapter
from database import get_db
from schemas.transaction import (
    CreateTransaction,
    TransactionResponse,
    TransactionsBalanceResponse,
    UpdateTransaction,
)
from services.transaction_service import TransactionService

router = APIRouter(prefix="/transaction", tags=["Transaction"])


def get_transaction_service(
    db: Annotated[Session, Depends(get_db)],
    logger: Annotated[CorrelationLoggerAdapter, Depends(get_request_logger)],
) -> TransactionService:
    return TransactionService(db, logger)


@router.get(
    "/balance",
    summary="Get transactions balance",
    response_model=TransactionsBalanceResponse,
    status_code=status.HTTP_200_OK,
)
def get_transactions_balance(
    service: Annotated[TransactionService, Depends(get_transaction_service)],
):
    balance = service.get_balance()
    return {"balance": balance}


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
)
def get_transaction(
    transaction_id: int,
    service: Annotated[TransactionService, Depends(get_transaction_service)],
) -> None | TransactionResponse:
    return service.get_transaction_by_id(transaction_id)


@router.get(
    "/", response_model=list[TransactionResponse], status_code=status.HTTP_200_OK
)
def list_transactions(
    service: Annotated[TransactionService, Depends(get_transaction_service)],
) -> list[TransactionResponse]:
    return service.get_all_transactions()


@router.post(
    "/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
def create_transaction(
    transaction: CreateTransaction,
    service: Annotated[TransactionService, Depends(get_transaction_service)],
) -> TransactionResponse:
    return service.create_transaction(transaction)


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
)
def update_transaction(
    transaction_id: int,
    transaction: UpdateTransaction,
    service: Annotated[TransactionService, Depends(get_transaction_service)],
) -> TransactionResponse:
    return service.update_transaction(transaction_id, transaction)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    service: Annotated[TransactionService, Depends(get_transaction_service)],
) -> None:
    service.delete_transaction(transaction_id)
