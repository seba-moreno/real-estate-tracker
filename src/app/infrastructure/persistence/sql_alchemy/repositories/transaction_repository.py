from sqlalchemy import case, func
from app.core.domain.entities.transaction import Transaction

from app.core.interfaces.repositories.transaction_repository import (
    ITransactionRepository,
)
from app.infrastructure.persistence.sql_alchemy.models.transaction_model import (
    TransactionModel,
)
from app.infrastructure.persistence.sql_alchemy.repositories.sql_alchemy_repository import (
    SqlAlchemyRepository,
)
from app.infrastructure.persistence.sql_alchemy.mappers.transaction_mapper import (
    to_domain,
    to_model,
)


class TransactionRepository(
    SqlAlchemyRepository[Transaction, TransactionModel], ITransactionRepository
):
    def __init__(self) -> None:
        super().__init__(
            model=TransactionModel,
            to_model=to_model,
            to_domain=to_domain,
        )

    def get_balance(self) -> float:
        with self._session() as db:
            balance = db.query(
                func.coalesce(
                    func.sum(
                        case(
                            (
                                TransactionModel.transaction_type == "income",
                                TransactionModel.amount,
                            ),
                            (
                                TransactionModel.transaction_type == "expense",
                                -TransactionModel.amount,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                )
            ).scalar()
            return float(balance or 0.0)
