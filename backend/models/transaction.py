from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from backend.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    propertiesConceptsId = Column(Integer, ForeignKey("properties_concepts.id"), nullable=False)
    transactionType = Column(String, nullable=False)
    period = Column(String, nullable=False)
    amount = Column(Numeric(19, 2), nullable=False) 
