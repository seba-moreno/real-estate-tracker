from sqlalchemy.orm import attributes
from app.core.domain.entities.transaction import Transaction
from app.infrastructure.persistence.sql_alchemy.models.transaction_model import (
    TransactionModel,
)
from app.infrastructure.persistence.sql_alchemy.mappers.properties_concepts_mapper import (
    to_domain as prop_concepts_to_domain,
)


def to_domain(model: TransactionModel) -> Transaction:
    state = attributes.instance_state(model)

    properties_concepts = None
    if (
        "properties_concepts" not in state.unloaded
        and model.properties_concepts is not None
    ):
        properties_concepts = prop_concepts_to_domain(model.properties_concepts)

    return Transaction(
        id=model.id,
        date=model.date,
        properties_concepts_id=model.properties_concepts_id,
        transaction_type=model.transaction_type,
        period=model.period,
        amount=model.amount,
        properties_concepts=properties_concepts,
    )


def to_model(entity: Transaction) -> TransactionModel:
    return TransactionModel(
        id=entity.id,
        date=entity.date,
        properties_concepts_id=entity.properties_concepts_id,
        transaction_type=entity.transaction_type,
        period=entity.period,
        amount=entity.amount,
    )
