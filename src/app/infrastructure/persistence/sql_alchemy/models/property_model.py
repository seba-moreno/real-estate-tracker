from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.persistence.sql_alchemy.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.sql_alchemy.models.properties_concepts_model import (
        PropertiesConceptsModel,
    )


class PropertyModel(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location: Mapped[str] = mapped_column(String, nullable=False)
    area: Mapped[int] = mapped_column(Integer, nullable=True)
    valuation: Mapped[Decimal] = mapped_column(Numeric(19, 2), nullable=False)
    details: Mapped[str] = mapped_column(String, nullable=True)

    properties_concepts: Mapped[list["PropertiesConceptsModel"]] = relationship(
        "PropertiesConceptsModel",
        back_populates="prop",
        cascade="all, delete-orphan",
    )

    contracts = relationship(
        "ContractModel",
        back_populates="prop",
        passive_deletes=True,
        cascade="all, delete-orphan",
    )
