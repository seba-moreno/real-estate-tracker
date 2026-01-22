from sqlalchemy import Column, Integer, Numeric, String
from database import Base

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True)
    location = Column(String, nullable=False)
    area = Column(Integer, nullable=True)
    valuation = Column(Numeric(19, 2), nullable=False) 
    details = Column(String, nullable=True)