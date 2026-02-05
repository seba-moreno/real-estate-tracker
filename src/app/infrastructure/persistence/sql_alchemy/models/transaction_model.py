from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from app.infrastructure.persistence.sql_alchemy.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.sql_alchemy.models.properties_concepts_model import (
        PropertiesConceptsModel,
    )


class TransactionModel(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    properties_concepts_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("properties_concepts.id", ondelete="CASCADE"),
        nullable=False,
    )
    transaction_type: Mapped[str] = mapped_column(String, nullable=False)
    period: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(19, 2), nullable=False)

    properties_concepts: Mapped["PropertiesConceptsModel"] = relationship(
        "PropertiesConceptsModel", back_populates="transactions", passive_deletes=True
    )
