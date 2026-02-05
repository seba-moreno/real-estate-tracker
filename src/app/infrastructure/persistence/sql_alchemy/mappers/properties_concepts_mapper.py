from sqlalchemy.orm import attributes
from app.core.domain.entities.properties_concepts import PropertiesConcepts
from app.infrastructure.persistence.sql_alchemy.models.properties_concepts_model import (
    PropertiesConceptsModel,
)
from app.infrastructure.persistence.sql_alchemy.mappers.concept_mapper import (
    to_domain as concept_to_domain,
)
from app.infrastructure.persistence.sql_alchemy.mappers.property_mapper import (
    to_domain as prop_to_domain,
)


def to_domain(model: PropertiesConceptsModel) -> PropertiesConcepts:
    state = attributes.instance_state(model)

    concept = None
    if "concept" not in state.unloaded and model.concept is not None:
        concept = concept_to_domain(model.concept)

    prop = None
    if "prop" not in state.unloaded and model.prop is not None:
        prop = prop_to_domain(model.prop)

    return PropertiesConcepts(
        id=model.id,
        concept_id=model.concept_id,
        property_id=model.property_id,
        enabled=model.enabled,
        concept=concept,
        prop=prop,
    )


def to_model(entity: PropertiesConcepts) -> PropertiesConceptsModel:
    return PropertiesConceptsModel(
        id=entity.id,
        concept_id=entity.concept_id,
        property_id=entity.property_id,
        enabled=entity.enabled,
    )
