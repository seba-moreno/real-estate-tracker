from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from app.core.interfaces.services.transaction_service import ITransactionService
from app.presentation.api.v1.schemas.transaction import (
    TransactionBase,
    TransactionResponse,
    TransactionsBalanceResponse,
)
from app.infrastructure.containers.root_container import RootContainer
from app.presentation.api.v1.mappers.transaction_mapper import (
    domain_to_response_schema,
    domain_list_to_response_schemas,
    schema_to_domain,
)

router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.get(
    "/balance",
    summary="Get transactions balance",
    response_model=TransactionsBalanceResponse,
    status_code=status.HTTP_200_OK,
)
@inject
def get_transactions_balance(
    service: ITransactionService = Depends(
        Provide[RootContainer.services.transaction_service]
    ),
) -> TransactionsBalanceResponse:
    result = service.get_balance()
    return TransactionsBalanceResponse(balance=result)


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
)
@inject
def get_transaction(
    transaction_id: int,
    service: ITransactionService = Depends(
        Provide[RootContainer.services.transaction_service]
    ),
) -> TransactionResponse | None:
    domain_entity = service.get_by_id(transaction_id)
    if domain_entity is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return domain_to_response_schema(domain_entity)


@router.get(
    "/", response_model=list[TransactionResponse], status_code=status.HTTP_200_OK
)
@inject
def list_transactions(
    service: ITransactionService = Depends(
        Provide[RootContainer.services.transaction_service]
    ),
) -> list[TransactionResponse]:
    result = service.get_all()
    return domain_list_to_response_schemas(result)


@router.post(
    "/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
@inject
def create_transaction(
    transaction: TransactionBase,
    service: ITransactionService = Depends(
        Provide[RootContainer.services.transaction_service]
    ),
) -> TransactionResponse:
    domain_entity = schema_to_domain(transaction)
    result = service.create(domain_entity)
    return domain_to_response_schema(result)


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
)
@inject
def update_transaction(
    transaction_id: int,
    transaction: TransactionBase,
    service: ITransactionService = Depends(
        Provide[RootContainer.services.transaction_service]
    ),
) -> TransactionResponse:
    domain_entity = schema_to_domain(transaction)
    result = service.update(transaction_id, domain_entity)
    return domain_to_response_schema(result)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_transaction(
    transaction_id: int,
    service: ITransactionService = Depends(
        Provide[RootContainer.services.transaction_service]
    ),
) -> None:
    service.delete(transaction_id)
