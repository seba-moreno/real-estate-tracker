from abc import ABC, abstractmethod
from app.core.domain.entities.contract import Contract
from app.core.interfaces.services.base_service import IBaseService


class IContractService(IBaseService[Contract], ABC):
    @abstractmethod
    def get_contracts_ending_within(self, months: int) -> list[Contract]: ...
