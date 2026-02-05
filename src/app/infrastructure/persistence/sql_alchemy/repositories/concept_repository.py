from app.core.domain.entities.concept import Concept
from app.core.interfaces.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.sql_alchemy.mappers.concept_mapper import (
    to_domain,
    to_model,
)
from app.infrastructure.persistence.sql_alchemy.models.concept_model import ConceptModel
from app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository import (
    SqlAlchemyRepository,
)


class ConceptRepository(
    SqlAlchemyRepository[Concept, ConceptModel], BaseRepository[Concept]
):
    def __init__(self) -> None:
        super().__init__(
            model=ConceptModel,
            to_model=to_model,
            to_domain=to_domain,
        )
