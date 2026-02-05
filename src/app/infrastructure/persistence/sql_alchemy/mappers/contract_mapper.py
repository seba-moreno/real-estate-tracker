from sqlalchemy.orm import attributes
from app.core.domain.entities.contract import Contract
from app.infrastructure.persistence.sql_alchemy.models.contract_model import (
    ContractModel,
)
from app.infrastructure.persistence.sql_alchemy.mappers.property_mapper import (
    to_domain as prop_to_domain,
)


def to_domain(model: ContractModel) -> Contract:
    state = attributes.instance_state(model)

    prop = None
    if "prop" not in state.unloaded and model.prop is not None:
        prop = prop_to_domain(model.prop)

    return Contract(
        id=model.id,
        property_id=model.property_id,
        start_date=model.start_date,
        end_date=model.end_date,
        details=model.details,
        prop=prop,
    )


def to_model(entity: Contract) -> ContractModel:
    return ContractModel(
        id=entity.id,
        property_id=entity.property_id,
        start_date=entity.start_date,
        end_date=entity.end_date,
        details=entity.details,
    )
