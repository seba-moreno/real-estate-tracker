from app.core.domain.entities.property import Property
from app.core.interfaces.repositories.base_repository import BaseRepository
from app.infrastructure.services.base_service import BaseService


class PropertyService(BaseService[Property]):
    def __init__(self, repository: BaseRepository[Property], entity_name: str) -> None:
        super().__init__(repository=repository, entity_name=entity_name)
