from typing import Optional
from sqlalchemy.orm import Session
from models.transaction import Transaction
from repositories.base_repository import BaseRepository
from schemas.transaction import (
    CreateTransaction,
    TransactionResponse,
    UpdateTransaction,
)
from sqlalchemy.exc import SQLAlchemyError


class TransactionRepository(BaseRepository[TransactionResponse]):
    dto_model = TransactionResponse

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, transaction_id: int) -> Optional[TransactionResponse]:
        result = self.db.get(Transaction, transaction_id)

        if not result:
            return None

        return self.to_dto(result)

    def get_all(self) -> list[TransactionResponse]:
        results = self.db.query(Transaction).all()
        return self.to_dto_list(results)

    def create(self, transaction: CreateTransaction) -> TransactionResponse:
        new_transaction = Transaction(**transaction.model_dump())

        try:
            self.db.add(new_transaction)
            self.db.commit()
            self.db.refresh(new_transaction)

        except SQLAlchemyError:
            self.db.rollback()

        return self.to_dto(new_transaction)

    def update(
        self, transaction_id: int, transaction: UpdateTransaction
    ) -> TransactionResponse:
        db_transaction = self.db.get(Transaction, transaction_id)

        if db_transaction:
            for key, value in transaction.model_dump().items():
                setattr(db_transaction, key, value)

            try:
                self.db.commit()
                self.db.refresh(db_transaction)
            except SQLAlchemyError:
                self.db.rollback()
        return self.to_dto(db_transaction)

    def delete(self, transaction_id: int) -> bool:
        db_transaction = self.db.get(Transaction, transaction_id)

        if db_transaction:
            try:
                self.db.delete(db_transaction)
                self.db.commit()
                return True
            except SQLAlchemyError:
                self.db.rollback()
                return False
        return False
