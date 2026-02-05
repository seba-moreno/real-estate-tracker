from app.core.domain.entities.properties_concepts import PropertiesConcepts
from app.core.interfaces.repositories.properties_concepts_repository import (
    IPropertiesConceptsRepository,
)
from app.core.interfaces.services.properties_concepts_service import (
    IPropertiesConceptsService,
)
from app.infrastructure.logging.logger_with_correlation_id import get_logger
from app.infrastructure.services.base_service import BaseService


class PropertiesConceptsService(
    BaseService[PropertiesConcepts], IPropertiesConceptsService
):
    repo: IPropertiesConceptsRepository

    def __init__(
        self, repository: IPropertiesConceptsRepository, entity_name: str
    ) -> None:
        super().__init__(repository=repository, entity_name=entity_name)
        self.repo = repository
        self.logger = get_logger(type(self).__name__)

    def get_combos(self) -> list[PropertiesConcepts]:
        self.logger.info("Fetching PropertiesConcepts combos")
        results = self.repo.get_with_navigations()
        self.logger.info(
            "Fetched all PropertiesConcepts combos", extra={"count": len(results)}
        )

        return results
