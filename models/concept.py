from sqlalchemy import Boolean, Column, Integer, String
from database import Base

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True)
    category = Column(String, nullable=False)
    isOrdinary = Column(Boolean, nullable=False)
    periodicity = Column(Integer, nullable=True)
    description = Column(String, nullable=True)