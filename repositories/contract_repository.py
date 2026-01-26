from typing import List, Optional
from sqlalchemy.orm import Session
from models.contract import Contract

class ContractRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, contract_id: int) -> Optional[Contract]:
        return self.db.query(Contract).filter(Contract.id == contract_id).first()
        
    def get_all(self) -> List[Contract]:
        return self.db.query(Contract).all()
    
    def create(self, contract: Contract) -> Contract:
        new_contract = Contract(**contract)
        self.db.add(new_contract)
        self.db.commit()
        self.db.refresh(new_contract)
        
        return new_contract
    
    def update(self, contract_id: int, contract: Contract) -> Optional[Contract]:
        db_contract = self.get_by_id(contract_id)
        
        if db_contract:
            for key, value in contract.model_dump().items():
                setattr(db_contract, key, value)
            self.db.commit()
            self.db.refresh(db_contract)
        return db_contract
    
    def delete(self, contract_id: int) -> bool:
        db_contract = self.get_by_id(contract_id)
        
        if db_contract:
            self.db.delete(db_contract)
            self.db.commit()
            return True
        return False
    