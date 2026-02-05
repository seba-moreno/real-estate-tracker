from abc import ABC, abstractmethod
from app.core.domain.entities.transaction import Transaction
from app.core.interfaces.repositories.base_repository import BaseRepository


class ITransactionRepository(BaseRepository[Transaction], ABC):
    @abstractmethod
    def get_balance(self) -> float: ...
