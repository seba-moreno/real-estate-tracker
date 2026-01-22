from datetime import date
from sqlalchemy.orm import Session
from database import Base
from models.concept import Concept
from models.contract import Contract
from models.properties_concepts import PropertiesConcepts
from models.property import Property
from models.transaction import Transaction

def add_mockup_data(session: Session):
    add_initial_properties(session)
    add_initial_concepts(session)
    add_initial_contracts(session)
    add_initial_properties_concepts(session)
    add_initial_transactions(session)

def add_initial_properties(session: Session):
    prop1 = Property(id=1, location="Avellaneda 500 1°A", valuation="100000")
    prop2 = Property(id=2, location="Avellaneda 500 1°B", valuation="100000")
    prop3 = Property(id=3, location="Campo en algun lugar", area=250, valuation="2000000", details="Lote de 250 has en algun lugar")
    session.add_all([prop1, prop2, prop3])
    session.commit()

def add_initial_concepts(session: Session):
    concept1 = Concept(id=1, category="Alquiler mensual", isOrdinary=True, periodicity= 1)
    concept2 = Concept(id=2, category="API Santa Fe", isOrdinary=True, periodicity= 2, description="Pago de impuesto inmobiliario urbano o rural. Vencimiento bimestral")
    concept3 = Concept(id=3, category="TGI Rosario", isOrdinary=True, periodicity= 1)
    concept3 = Concept(id=4, category="Alquiler semestral", isOrdinary=True, periodicity= 6)
    session.add_all([concept1, concept2, concept3])
    session.commit()

def add_initial_contracts(session: Session):
    contract1 = Contract(id=1, propertyId=1, startDate=date(2023,1,20), endDate=date(2026,1,19))
    contract2 = Contract(id=2, propertyId=3, startDate=date(2025,12,20), endDate=date(2026,6,19))
    session.add_all([contract1, contract2])
    session.commit()

def add_initial_properties_concepts(session: Session):
    pc1 = PropertiesConcepts(id=1, propertyId=1, conceptId=1, enabled=True)
    pc2 = PropertiesConcepts(id=2, propertyId=1, conceptId=2, enabled=True)
    pc3 = PropertiesConcepts(id=3, propertyId=1, conceptId=3, enabled=True)
    pc4 = PropertiesConcepts(id=4, propertyId=2, conceptId=1, enabled=False)
    pc5 = PropertiesConcepts(id=5, propertyId=2, conceptId=2, enabled=True)
    pc6 = PropertiesConcepts(id=6, propertyId=2, conceptId=3, enabled=True)
    pc7 = PropertiesConcepts(id=7, propertyId=3, conceptId=4, enabled=True)
    pc8 = PropertiesConcepts(id=8, propertyId=3, conceptId=2, enabled=True)
    
    session.add_all([pc1, pc2, pc3, pc4, pc5, pc6, pc7, pc8])
    session.commit()

def add_initial_transactions(session: Session):
    t1 = Transaction(id=1, date=date(2026,1,4), propertiesConceptsId=1, transactionType="Income", period="2026.01", amount=400)
    t2 = Transaction(id=2, date=date(2026,1,4), propertiesConceptsId=2, transactionType="Expense", period="2026.01", amount=20)
    t3 = Transaction(id=3, date=date(2026,1,4), propertiesConceptsId=1, transactionType="Income", period="2025.12", amount=400)
    t4 = Transaction(id=4, date=date(2026,6,19), propertiesConceptsId=7, transactionType="Income", period="2025.12 2026.06", amount=20000)
    t5 = Transaction(id=5, date=date(2026,1,4), propertiesConceptsId=5, transactionType="Expense", period="2026.01", amount=20)
    t6 = Transaction(id=6, date=date(2026,1,4), propertiesConceptsId=6, transactionType="Expense", period="2026.01", amount=40)
    session.add_all([t1, t2, t3, t4, t5, t6])
    session.commit()