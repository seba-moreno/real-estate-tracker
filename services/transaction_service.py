from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from core.dependencies.logger import get_request_logger
from core.logging.logger_with_correlation_id import CorrelationLoggerAdapter
from repositories.transaction_repository import TransactionRepository
from schemas.transaction import (
    TransactionResponse,
    CreateTransaction,
    UpdateTransaction,
)


class TransactionService:
    def __init__(
        self,
        db: Session,
        logger: CorrelationLoggerAdapter = Depends(get_request_logger),
    ) -> None:
        self.transaction_repository = TransactionRepository(db)
        self.logger = logger

    def get_transaction_by_id(
        self, transaction_id: int
    ) -> Optional[TransactionResponse]:
        existing_transaction = self.transaction_repository.get_by_id(transaction_id)

        if not existing_transaction:
            self.logger.warning(
                "Get by id failed: Transaction not found",
                extra={"transaction_id": transaction_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )

        return existing_transaction

    def get_all_transactions(self) -> list[TransactionResponse]:
        return self.transaction_repository.get_all()

    def create_transaction(self, transaction: CreateTransaction) -> TransactionResponse:
        payload = transaction.model_dump()
        self.logger.info("Creating Transaction", extra={"data": payload})

        try:
            created_transaction = self.transaction_repository.create(transaction)
            self.logger.info(
                "Transaction created successfully",
                extra={"data": created_transaction.model_dump()},
            )
            return created_transaction
        except Exception:
            self.logger.exception(
                "Failed to create Transaction", extra={"data": payload}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the transaction",
            )

    def update_transaction(
        self, transaction_id: int, transaction: UpdateTransaction
    ) -> TransactionResponse:
        existing_transaction = self.transaction_repository.get_by_id(transaction_id)

        if not existing_transaction:
            self.logger.warning(
                "Update failed: Transaction not found",
                extra={"transaction_id": transaction_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )

        payload = transaction.model_dump()
        self.logger.info(
            "Updating transaction",
            extra={"transaction_id": transaction_id, "data": payload},
        )

        try:
            updated_transaction = self.transaction_repository.update(
                transaction_id, transaction
            )
            self.logger.info(
                "Transaction updated successfully",
                extra={"data": updated_transaction.model_dump()},
            )
            return updated_transaction
        except Exception:
            self.logger.exception(
                "Failed to update Transaction",
                extra={"transaction_id": transaction_id, "data": payload},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the transaction",
            )

    def delete_transaction(self, transaction_id: int) -> None:
        self.logger.info(
            "Removing transaction", extra={"transaction_id": transaction_id}
        )
        existing_transaction = self.transaction_repository.get_by_id(transaction_id)

        if not existing_transaction:
            self.logger.warning(
                "Delete failed: Transaction not found",
                extra={"transaction_id": transaction_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )

        try:
            if not self.transaction_repository.delete(transaction_id):
                self.logger.error(
                    "Failed to delete Transaction",
                    extra={"transaction_id": transaction_id},
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred while deleting the transaction",
                )

            self.logger.info(
                "Transaction deleted successfully",
                extra={"transaction_id": transaction_id},
            )
        except Exception:
            self.logger.exception(
                "Failed to delete Transaction", extra={"transaction_id": transaction_id}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting the transaction",
            )
