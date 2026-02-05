from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide
from app.core.interfaces.services.contract_service import IContractService
from app.infrastructure.containers.root_container import RootContainer
from app.presentation.api.v1.mappers.contract_mapper import (
    domain_list_to_response_schemas,
    domain_to_response_schema,
    schema_to_domain,
)
from app.presentation.api.v1.schemas.contract import ContractBase, ContractResponse

router = APIRouter(prefix="/contract", tags=["Contract"])


@router.get("/ending-in/{months}", response_model=list[ContractResponse])
@inject
def get_contracts_ending_in(
    months: int,
    service: IContractService = Depends(
        Provide[RootContainer.services.contract_service]
    ),
) -> list[ContractResponse]:
    result = service.get_contracts_ending_within(months)
    return domain_list_to_response_schemas(result)


@router.get(
    "/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK
)
@inject
def get_contract(
    contract_id: int,
    service: IContractService = Depends(
        Provide[RootContainer.services.contract_service]
    ),
) -> ContractResponse | None:
    domain_entity = service.get_by_id(contract_id)
    assert domain_entity is not None
    return domain_to_response_schema(domain_entity)


@router.get("/", response_model=list[ContractResponse], status_code=status.HTTP_200_OK)
@inject
def list_contracts(
    service: IContractService = Depends(
        Provide[RootContainer.services.contract_service]
    ),
) -> list[ContractResponse]:
    result = service.get_all()
    return domain_list_to_response_schemas(result)


@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
@inject
def create_contract(
    contract: ContractBase,
    service: IContractService = Depends(
        Provide[RootContainer.services.contract_service]
    ),
) -> ContractResponse:
    domain_entity = schema_to_domain(contract)
    result = service.create(domain_entity)
    return domain_to_response_schema(result)


@router.put(
    "/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK
)
@inject
def update_contract(
    contract_id: int,
    contract: ContractBase,
    service: IContractService = Depends(
        Provide[RootContainer.services.contract_service]
    ),
) -> ContractResponse:
    domain_entity = schema_to_domain(contract)
    result = service.update(contract_id, domain_entity)
    return domain_to_response_schema(result)


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_contract(
    contract_id: int,
    service: IContractService = Depends(
        Provide[RootContainer.services.contract_service]
    ),
) -> None:
    service.delete(contract_id)
