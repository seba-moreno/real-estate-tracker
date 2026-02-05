from sqlalchemy import func
from app.core.domain.entities.contract import Contract
from app.core.interfaces.repositories.contract_repository import IContractRepository
from app.infrastructure.persistence.sql_alchemy.mappers.contract_mapper import (
    to_domain,
    to_model,
)
from app.infrastructure.persistence.sql_alchemy.models.contract_model import (
    ContractModel,
)
from app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository import (
    SqlAlchemyRepository,
)


class ContractRepository(
    SqlAlchemyRepository[Contract, ContractModel], IContractRepository
):
    def __init__(self) -> None:
        super().__init__(
            model=ContractModel,
            to_model=to_model,
            to_domain=to_domain,
        )

    def get_ending_within_months(self, months: int) -> list[Contract]:
        if months <= 0:
            raise ValueError("Months must be > 0")

        with self._session() as db:
            results = (
                db.query(ContractModel)
                .filter(
                    ContractModel.end_date >= func.date("now"),
                    ContractModel.end_date <= func.date("now", f"+{months} months"),
                )
                .order_by(ContractModel.end_date.asc())
                .all()
            )
            return [to_domain(row) for row in results]
