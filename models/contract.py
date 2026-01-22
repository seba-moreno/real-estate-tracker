from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from database import Base

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True)
    propertyId = Column(Integer, ForeignKey("properties.id"), unique=True, nullable=False)
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    details = Column(String, nullable=True)