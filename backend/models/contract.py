from sqlalchemy import Boolean, Column, Date, Integer, String
from backend.database import Base

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True)
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    isActive = Column(Boolean, nullable=False)
    details = Column(String, nullable=True)