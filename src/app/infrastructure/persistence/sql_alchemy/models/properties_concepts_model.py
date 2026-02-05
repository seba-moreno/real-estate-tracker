from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.infrastructure.persistence.sql_alchemy.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.sql_alchemy.models.concept_model import (
        ConceptModel,
    )
    from app.infrastructure.persistence.sql_alchemy.models.property_model import (
        PropertyModel,
    )
    from app.infrastructure.persistence.sql_alchemy.models.transaction_model import (
        TransactionModel,
    )


class PropertiesConceptsModel(Base):
    __tablename__ = "properties_concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    concept_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False
    )
    property_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    concept: Mapped["ConceptModel"] = relationship(
        "ConceptModel", back_populates="properties_concepts"
    )
    prop: Mapped["PropertyModel"] = relationship(
        "PropertyModel", back_populates="properties_concepts"
    )

    transactions: Mapped[list["TransactionModel"]] = relationship(
        "TransactionModel",
        back_populates="properties_concepts",
        passive_deletes=True,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("property_id", "concept_id", name="uq_property_concept"),
    )
