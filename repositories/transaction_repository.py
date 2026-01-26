from typing import List, Optional
from sqlalchemy.orm import Session
from models.transaction import Transaction

class TransactionRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        
    def get_all(self) -> List[Transaction]:
        return self.db.query(Transaction).all()
    
    def create(self, transaction: Transaction) -> Transaction:
        new_transaction = Transaction(**transaction)
        self.db.add(new_transaction)
        self.db.commit()
        self.db.refresh(new_transaction)
        
        return new_transaction
    
    def update(self, transaction_id: int, transaction: Transaction) -> Optional[Transaction]:
        db_transaction = self.get_by_id(transaction_id)
        
        if db_transaction:
            for key, value in transaction.model_dump().items():
                setattr(db_transaction, key, value)
            self.db.commit()
            self.db.refresh(db_transaction)
        return db_transaction
    
    def delete(self, transaction_id: int) -> bool:
        db_transaction = self.get_by_id(transaction_id)
        
        if db_transaction:
            self.db.delete(db_transaction)
            self.db.commit()
            return True
        return False
    