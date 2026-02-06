from app.infrastructure.logging.logger_with_correlation_id import get_logger
from app.core.domain.entities.contract import Contract
from app.core.interfaces.repositories.contract_repository import IContractRepository
from app.core.interfaces.services.contract_service import IContractService
from app.core.exceptions.domain_exceptions import PersistenceError, ValidationError
from app.application.services.base_service import BaseService


class ContractService(BaseService[Contract], IContractService):
    repo: IContractRepository

    def __init__(self, repository: IContractRepository, entity_name: str) -> None:
        super().__init__(repository=repository, entity_name=entity_name)
        self.repo = repository
        self.logger = get_logger(type(self).__name__)

    def get_contracts_ending_within(self, months: int) -> list[Contract]:
        if months <= 0:
            self.logger.warning(
                "Invalid months parameter in get_contracts_ending_within()",
                extra={"months": months},
            )
            raise ValidationError("Months must be a greater than 0 integer")

        self.logger.info(
            "Fetching contracts ending within months",
            extra={"months": months},
        )

        try:
            contracts = self.repo.get_ending_within_months(months)
            self.logger.info(
                "Fetched contracts ending within period",
                extra={"months": months, "count": len(contracts)},
            )
            return contracts
        except Exception as ex:
            self.logger.exception(
                "Failed to fetch contracts ending within months",
                extra={"months": months},
            )
            raise PersistenceError(
                "An unexpected error occurred while fetching expiring contracts"
            ) from ex
