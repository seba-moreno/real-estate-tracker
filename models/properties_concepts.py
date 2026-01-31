from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, ForeignKey, Integer
from database import Base


class PropertiesConcepts(Base):
    __tablename__ = "properties_concepts"

    id = Column(Integer, primary_key=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    enabled = Column(Boolean, nullable=False)

    concept = relationship("Concept", backref="properties_concepts")
    property = relationship("Property", backref="properties_concepts")
