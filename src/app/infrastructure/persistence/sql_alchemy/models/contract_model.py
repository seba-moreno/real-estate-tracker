from datetime import date
from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.sql_alchemy.database import Base


class ContractModel(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    property_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    details: Mapped[str] = mapped_column(String, nullable=True)

    prop = relationship("PropertyModel", back_populates="contracts")
