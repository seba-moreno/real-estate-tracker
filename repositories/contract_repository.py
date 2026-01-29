from sqlalchemy.orm import Session
from models.contract import Contract
from repositories.base_repository import BaseRepository
from schemas.contract import ContractResponse, CreateContract, UpdateContract
from sqlalchemy.exc import SQLAlchemyError


class ContractRepository(BaseRepository[ContractResponse]):
    dto_model = ContractResponse

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, contract_id: int) -> None | ContractResponse:
        result = self.db.get(Contract, contract_id)

        if not result:
            return None

        return self.to_dto(result)

    def get_all(self) -> list[ContractResponse]:
        results = self.db.query(Contract).all()
        return self.to_dto_list(results)

    def create(self, contract: CreateContract) -> ContractResponse:
        new_contract = Contract(**contract.model_dump())

        try:
            self.db.add(new_contract)
            self.db.commit()
            self.db.refresh(new_contract)

        except SQLAlchemyError:
            self.db.rollback()

        return self.to_dto(new_contract)

    def update(self, contract_id: int, contract: UpdateContract) -> ContractResponse:
        db_contract = self.db.get(Contract, contract_id)

        if db_contract:
            for key, value in contract.model_dump().items():
                setattr(db_contract, key, value)

            try:
                self.db.commit()
                self.db.refresh(db_contract)
            except SQLAlchemyError:
                self.db.rollback()
        return self.to_dto(db_contract)

    def delete(self, contract_id: int) -> bool:
        db_contract = self.db.get(Contract, contract_id)

        if db_contract:
            try:
                self.db.delete(db_contract)
                self.db.commit()
                return True
            except SQLAlchemyError:
                self.db.rollback()
                return False
        return False
