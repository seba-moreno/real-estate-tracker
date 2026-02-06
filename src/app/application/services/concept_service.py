from app.core.domain.entities.concept import Concept
from app.core.interfaces.repositories.base_repository import BaseRepository
from app.application.services.base_service import BaseService


class ConceptService(BaseService[Concept]):
    def __init__(self, repository: BaseRepository[Concept], entity_name: str) -> None:
        super().__init__(repository=repository, entity_name=entity_name)
