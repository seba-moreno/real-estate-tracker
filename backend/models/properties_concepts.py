from sqlalchemy import Boolean, Column, Integer
from backend.database import Base

class PropertiesConcepts(Base):
    __tablename__ = "properties_concepts"

    id = Column(Integer, primary_key=True)
    conceptId = Column(Integer, nullable=False)
    propertyId = Column(Integer, nullable=False)
    enabled = Column(Boolean, nullable=False)