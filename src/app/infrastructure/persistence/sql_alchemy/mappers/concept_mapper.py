from app.core.domain.entities.concept import Concept
from app.infrastructure.persistence.sql_alchemy.models.concept_model import ConceptModel


def to_domain(model: ConceptModel) -> Concept:
    return Concept(
        id=model.id,
        name=model.name,
        is_ordinary=model.is_ordinary,
        periodicity=model.periodicity,
        description=model.description,
    )


def to_model(entity: Concept) -> ConceptModel:
    return ConceptModel(
        id=entity.id,
        name=entity.name,
        is_ordinary=entity.is_ordinary,
        periodicity=entity.periodicity,
        description=entity.description,
    )
