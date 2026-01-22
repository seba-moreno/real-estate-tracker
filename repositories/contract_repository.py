from typing import List, Optional
from sqlalchemy.orm import Session
from models.contract import Contract

class ContractRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, contractId: int) -> Optional[Contract]:
        return self.db.query(Contract).filter(Contract.id == contractId).first()
        
    def get_all(self) -> List[Contract]:
        return self.db.query(Contract).all()
    
    def create(self, contract: Contract) -> Contract:
        newcontract = Contract(**contract)
        self.db.add(newcontract)
        self.db.commit()
        self.db.refresh(newcontract)
        
        return newcontract
    
    def update(self, contractId: int, contract: Contract) -> Optional[Contract]:
        db_contract = self.get_by_id(contractId)
        
        if db_contract:
            for key, value in contract.model_dump().items():
                setattr(db_contract, key, value)
            self.db.commit()
            self.db.refresh(db_contract)
        return db_contract
    
    def delete(self, contractId: int) -> bool:
        db_contract = self.get_by_id(contractId)
        
        if db_contract:
            self.db.delete(db_contract)
            self.db.commit()
            return True
        return False
    