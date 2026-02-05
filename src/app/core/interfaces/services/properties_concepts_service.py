from abc import ABC, abstractmethod
from app.core.domain.entities.properties_concepts import PropertiesConcepts
from app.core.interfaces.services.base_service import IBaseService


class IPropertiesConceptsService(IBaseService[PropertiesConcepts], ABC):
    @abstractmethod
    def get_combos(self) -> list[PropertiesConcepts]: ...
