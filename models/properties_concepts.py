from sqlalchemy import Boolean, Column, ForeignKey, Integer
from database import Base

class PropertiesConcepts(Base):
    __tablename__ = "properties_concepts"

    id = Column(Integer, primary_key=True)
    conceptId = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    propertyId = Column(Integer, ForeignKey("properties.id"), nullable=False)
    enabled = Column(Boolean, nullable=False)