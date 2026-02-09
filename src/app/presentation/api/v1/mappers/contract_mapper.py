from fastapi import HTTPException
from app.core.domain.entities.contract import Contract
from app.presentation.api.v1.schemas.contract import ContractBase, ContractResponse


def domain_to_response_schema(entity: Contract) -> ContractResponse:
    if entity.id is None:
        raise HTTPException(status_code=500, detail="Cannot map a Contract with no id")
    return ContractResponse(
        id=entity.id,
        property_id=entity.property_id,
        start_date=entity.start_date,
        end_date=entity.end_date,
        details=entity.details,
    )


def domain_list_to_response_schemas(entities: list[Contract]) -> list[ContractResponse]:
    return [domain_to_response_schema(e) for e in entities]


def schema_to_domain(dto: ContractBase) -> Contract:
    return Contract(id=None, **dto.model_dump())
