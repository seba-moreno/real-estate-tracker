from app.core.domain.entities.transaction import Transaction
from app.presentation.api.v1.schemas.transaction import (
    TransactionBase,
    TransactionResponse,
)


def domain_to_response_schema(entity: Transaction) -> TransactionResponse:
    assert entity.id is not None
    return TransactionResponse(
        id=entity.id,
        date=entity.date,
        properties_concepts_id=entity.properties_concepts_id,
        transaction_type=entity.transaction_type,
        period=entity.period,
        amount=entity.amount,
    )


def domain_list_to_response_schemas(
    entities: list[Transaction],
) -> list[TransactionResponse]:
    return [domain_to_response_schema(e) for e in entities]


def schema_to_domain(dto: TransactionBase) -> Transaction:
    return Transaction(id=None, **dto.model_dump())
