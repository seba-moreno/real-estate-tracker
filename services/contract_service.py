from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from core.dependencies.logger import get_request_logger
from core.logging.logger_with_correlation_id import CorrelationLoggerAdapter
from repositories.contract_repository import ContractRepository
from schemas.contract import ContractResponse, CreateContract, UpdateContract


class ContractService:
    def __init__(
        self,
        db: Session,
        logger: CorrelationLoggerAdapter = Depends(get_request_logger),
    ) -> None:
        self.contract_repository = ContractRepository(db)
        self.logger = logger

    def get_contract_by_id(self, contract_id: int) -> Optional[ContractResponse]:
        existing_contract = self.contract_repository.get_by_id(contract_id)

        if not existing_contract:
            self.logger.warning(
                "Get by id failed: Contract not found",
                extra={"contract_id": contract_id},
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found"
            )

        return existing_contract

    def get_all_contracts(self) -> list[ContractResponse]:
        return self.contract_repository.get_all()

    def create_contract(self, contract: CreateContract) -> ContractResponse:
        payload = contract.model_dump()
        self.logger.info("Creating Contract", extra={"data": payload})

        try:
            created_contract = self.contract_repository.create(contract)
            self.logger.info(
                "Contract created successfully",
                extra={"data": created_contract.model_dump()},
            )
            return created_contract
        except Exception:
            self.logger.exception("Failed to create Contract", extra={"data": payload})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the contract",
            )

    def update_contract(
        self, contract_id: int, contract: UpdateContract
    ) -> ContractResponse:
        existing_contract = self.contract_repository.get_by_id(contract_id)

        if not existing_contract:
            self.logger.warning(
                "Update failed: Contract not found", extra={"contract_id": contract_id}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found"
            )

        payload = contract.model_dump()
        self.logger.info(
            "Updating contract", extra={"contract_id": contract_id, "data": payload}
        )

        try:
            updated_contract = self.contract_repository.update(contract_id, contract)
            self.logger.info(
                "Contract updated successfully",
                extra={"data": updated_contract.model_dump()},
            )
            return updated_contract
        except Exception:
            self.logger.exception(
                "Failed to update Contract",
                extra={"contract_id": contract_id, "data": payload},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the contract",
            )

    def delete_contract(self, contract_id: int) -> None:
        self.logger.info("Removing contract", extra={"contract_id": contract_id})
        existing_contract = self.contract_repository.get_by_id(contract_id)

        if not existing_contract:
            self.logger.warning(
                "Delete failed: Contract not found", extra={"contract_id": contract_id}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found"
            )

        try:
            if not self.contract_repository.delete(contract_id):
                self.logger.error(
                    "Failed to delete Contract", extra={"contract_id": contract_id}
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An unexpected error occurred while deleting the contract",
                )

            self.logger.info(
                "Contract deleted successfully", extra={"contract_id": contract_id}
            )
        except Exception:
            self.logger.exception(
                "Failed to delete Contract", extra={"contract_id": contract_id}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while deleting the contract",
            )
