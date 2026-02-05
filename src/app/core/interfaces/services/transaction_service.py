from abc import ABC, abstractmethod
from app.core.domain.entities.transaction import Transaction
from app.core.interfaces.services.base_service import IBaseService


class ITransactionService(IBaseService[Transaction], ABC):
    @abstractmethod
    def get_balance(self) -> float: ...
