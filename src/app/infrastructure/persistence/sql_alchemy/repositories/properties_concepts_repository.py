from sqlalchemy.orm import joinedload
from app.core.domain.entities.properties_concepts import PropertiesConcepts

from app.core.interfaces.repositories.properties_concepts_repository import (
    IPropertiesConceptsRepository,
)
from app.infrastructure.persistence.sql_alchemy.mappers.properties_concepts_mapper import (
    to_model,
    to_domain,
)
from app.infrastructure.persistence.sql_alchemy.models.properties_concepts_model import (
    PropertiesConceptsModel,
)
from app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository import (
    SqlAlchemyRepository,
)


class PropertiesConceptsRepository(
    SqlAlchemyRepository[PropertiesConcepts, PropertiesConceptsModel],
    IPropertiesConceptsRepository,
):
    def __init__(self) -> None:
        super().__init__(
            model=PropertiesConceptsModel,
            to_model=to_model,
            to_domain=to_domain,
        )

    def get_with_navigations(self) -> list[PropertiesConcepts]:
        with self._session() as db:
            results = db.query(PropertiesConceptsModel).options(
                joinedload(PropertiesConceptsModel.concept),
                joinedload(PropertiesConceptsModel.prop),
            )

            return [to_domain(row) for row in results]
