from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.dependencies.logger import get_request_logger
from core.logging.logger_with_correlation_id import CorrelationLoggerAdapter
from database import get_db
from schemas.contract import CreateContract, ContractResponse, UpdateContract
from services.contract_service import ContractService

router = APIRouter(prefix="/contract", tags=["Contract"])


def get_contract_service(
    db: Annotated[Session, Depends(get_db)],
    logger: Annotated[CorrelationLoggerAdapter, Depends(get_request_logger)],
) -> ContractService:
    return ContractService(db, logger)


@router.get("/ending-in/{months}", response_model=list[ContractResponse])
def get_contracts_ending_in(
    months: int, service: ContractService = Depends(get_contract_service)
) -> list[ContractResponse]:
    return service.get_contracts_ending_within(months)


@router.get(
    "/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK
)
def get_contract(
    contract_id: int,
    service: Annotated[ContractService, Depends(get_contract_service)],
) -> None | ContractResponse:
    return service.get_contract_by_id(contract_id)


@router.get("/", response_model=list[ContractResponse], status_code=status.HTTP_200_OK)
def list_contracts(
    service: Annotated[ContractService, Depends(get_contract_service)],
) -> list[ContractResponse]:
    return service.get_all_contracts()


@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(
    contract: CreateContract,
    service: Annotated[ContractService, Depends(get_contract_service)],
) -> ContractResponse:
    return service.create_contract(contract)


@router.put(
    "/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK
)
def update_contract(
    contract_id: int,
    contract: UpdateContract,
    service: Annotated[ContractService, Depends(get_contract_service)],
) -> ContractResponse:
    return service.update_contract(contract_id, contract)


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(
    contract_id: int,
    service: Annotated[ContractService, Depends(get_contract_service)],
) -> None:
    service.delete_contract(contract_id)
