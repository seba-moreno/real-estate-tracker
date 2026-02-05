from abc import ABC, abstractmethod
from app.core.interfaces.repositories.base_repository import BaseRepository
from app.core.domain.entities.contract import Contract


class IContractRepository(BaseRepository[Contract], ABC):
    @abstractmethod
    def get_ending_within_months(self, months: int) -> list[Contract]: ...
