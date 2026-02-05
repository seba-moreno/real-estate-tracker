from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.persistence.sql_alchemy.database import Base

if TYPE_CHECKING:
    from app.infrastructure.persistence.sql_alchemy.models.properties_concepts_model import (
        PropertiesConceptsModel,
    )


class ConceptModel(Base):
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    is_ordinary: Mapped[bool] = mapped_column(Boolean, nullable=False)
    periodicity: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)

    properties_concepts: Mapped[list["PropertiesConceptsModel"]] = relationship(
        "PropertiesConceptsModel",
        back_populates="concept",
        cascade="all, delete-orphan",
    )
