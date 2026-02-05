from app.infrastructure.logging.logger_with_correlation_id import get_logger
from app.core.domain.entities.transaction import Transaction
from app.core.exceptions.domain_exceptions import PersistenceError
from app.core.interfaces.repositories.transaction_repository import (
    ITransactionRepository,
)
from app.core.interfaces.services.transaction_service import ITransactionService
from app.infrastructure.services.base_service import BaseService


class TransactionService(BaseService[Transaction], ITransactionService):
    repo: ITransactionRepository

    def __init__(self, repository: ITransactionRepository, entity_name: str) -> None:
        super().__init__(repository=repository, entity_name=entity_name)
        self.repo = repository
        self.logger = get_logger(type(self).__name__)

    def get_balance(self) -> float:
        try:
            balance = self.repo.get_balance()
            self.logger.info("Balance calculated", extra={"balance": balance})
            return balance

        except Exception as ex:
            self.logger.exception("Failed to calculate balance")
            raise PersistenceError("Error calculating balance") from ex
