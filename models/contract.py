from sqlalchemy import Column, Date, ForeignKey, Integer, String
from database import Base

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.id"), unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    details = Column(String, nullable=True)