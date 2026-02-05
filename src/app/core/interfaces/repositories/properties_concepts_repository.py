from abc import ABC, abstractmethod
from app.core.interfaces.repositories.base_repository import BaseRepository
from app.core.domain.entities.properties_concepts import PropertiesConcepts


class IPropertiesConceptsRepository(BaseRepository[PropertiesConcepts], ABC):
    @abstractmethod
    def get_with_navigations(self) -> list[PropertiesConcepts]: ...
