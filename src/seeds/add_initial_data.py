from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.infrastructure.persistence.sql_alchemy.models.concept_model import ConceptModel
from app.infrastructure.persistence.sql_alchemy.models.contract_model import (
    ContractModel,
)
from app.infrastructure.persistence.sql_alchemy.models.properties_concepts_model import (
    PropertiesConceptsModel,
)
from app.infrastructure.persistence.sql_alchemy.models.property_model import (
    PropertyModel,
)
from app.infrastructure.persistence.sql_alchemy.models.transaction_model import (
    TransactionModel,
)


def add_mockup_data(session: Session) -> None:
    add_initial_properties(session)
    add_initial_concepts(session)
    add_initial_contracts(session)
    add_initial_properties_concepts(session)
    add_initial_transactions(session)


def add_initial_properties(session: Session) -> None:
    properties = [
        PropertyModel(
            id=1,
            location="Avellaneda 500 1°A",
            area=None,
            valuation=Decimal(95000),
            details=None,
        ),
        PropertyModel(
            id=2,
            location="Avellaneda 500 1°B",
            area=None,
            valuation=Decimal(98000),
            details="Balcón al frente",
        ),
        PropertyModel(
            id=3,
            location="Campo El Encuentro",
            area=250,
            valuation=Decimal(2000000),
            details="Lote agrícola 250ha",
        ),
        PropertyModel(
            id=4,
            location="Italia 1320 PB",
            area=None,
            valuation=Decimal(75000),
            details=None,
        ),
        PropertyModel(
            id=5,
            location="Cordoba 2200 2°C",
            area=None,
            valuation=Decimal(120000),
            details=None,
        ),
        PropertyModel(
            id=6,
            location="San Martín 980 5°B",
            area=None,
            valuation=Decimal(89000),
            details=None,
        ),
        PropertyModel(
            id=7,
            location="Entre Ríos 310 3°A",
            area=None,
            valuation=Decimal(110000),
            details=None,
        ),
        PropertyModel(
            id=8,
            location="Urquiza 1800 1°D",
            area=None,
            valuation=Decimal(83000),
            details=None,
        ),
        PropertyModel(
            id=9,
            location="Mendoza 2300 7°C",
            area=None,
            valuation=Decimal(150000),
            details="Cochera incluída",
        ),
        PropertyModel(
            id=10,
            location="Pellegrini 900 10°B",
            area=None,
            valuation=Decimal(175000),
            details="Vista al parque",
        ),
    ]
    session.add_all(properties)
    session.commit()


def add_initial_concepts(session: Session) -> None:
    concepts = [
        ConceptModel(
            id=1,
            name="Alquiler mensual",
            is_ordinary=True,
            periodicity=1,
            description=None,
        ),
        ConceptModel(
            id=2,
            name="Impuesto API",
            is_ordinary=True,
            periodicity=2,
            description="Impuesto provincial",
        ),
        ConceptModel(
            id=3, name="TGI Rosario", is_ordinary=True, periodicity=1, description=None
        ),
        ConceptModel(
            id=4,
            name="ABL Buenos Aires",
            is_ordinary=True,
            periodicity=1,
            description=None,
        ),
        ConceptModel(
            id=5,
            name="Expensas",
            is_ordinary=True,
            periodicity=1,
            description="Pago mensual",
        ),
        ConceptModel(
            id=6,
            name="Alquiler semestral",
            is_ordinary=True,
            periodicity=6,
            description=None,
        ),
        ConceptModel(
            id=7,
            name="Reparaciones",
            is_ordinary=False,
            periodicity=0,
            description="Gastos puntuales",
        ),
        ConceptModel(
            id=8,
            name="Seguro hogar",
            is_ordinary=True,
            periodicity=12,
            description=None,
        ),
        ConceptModel(
            id=9,
            name="Patente rural",
            is_ordinary=True,
            periodicity=6,
            description=None,
        ),
        ConceptModel(
            id=10,
            name="Honorarios administración",
            is_ordinary=True,
            periodicity=1,
            description="5%",
        ),
    ]
    session.add_all(concepts)
    session.commit()


def add_initial_contracts(session: Session) -> None:
    contracts = [
        ContractModel(
            id=1,
            property_id=1,
            start_date=date(2024, 1, 1),
            end_date=date(2027, 1, 1),
            details=None,
        ),
        ContractModel(
            id=2,
            property_id=2,
            start_date=date(2023, 6, 1),
            end_date=date(2026, 6, 1),
            details=None,
        ),
        ContractModel(
            id=3,
            property_id=3,
            start_date=date(2025, 12, 1),
            end_date=date(2026, 12, 1),
            details="Rural",
        ),
        ContractModel(
            id=4,
            property_id=5,
            start_date=date(2022, 9, 1),
            end_date=date(2025, 9, 1),
            details=None,
        ),
        ContractModel(
            id=5,
            property_id=6,
            start_date=date(2024, 3, 1),
            end_date=date(2027, 3, 1),
            details=None,
        ),
        ContractModel(
            id=6,
            property_id=7,
            start_date=date(2024, 4, 15),
            end_date=date(2027, 4, 15),
            details="Indexado",
        ),
        ContractModel(
            id=7,
            property_id=8,
            start_date=date(2023, 11, 1),
            end_date=date(2026, 11, 1),
            details=None,
        ),
        ContractModel(
            id=8,
            property_id=9,
            start_date=date(2025, 5, 10),
            end_date=date(2028, 5, 10),
            details=None,
        ),
    ]
    session.add_all(contracts)
    session.commit()


def add_initial_properties_concepts(session: Session) -> None:
    pcs = [
        PropertiesConceptsModel(id=1, property_id=1, concept_id=1, enabled=True),
        PropertiesConceptsModel(id=2, property_id=1, concept_id=2, enabled=True),
        PropertiesConceptsModel(id=3, property_id=1, concept_id=5, enabled=False),
        PropertiesConceptsModel(id=4, property_id=2, concept_id=1, enabled=True),
        PropertiesConceptsModel(id=5, property_id=2, concept_id=3, enabled=True),
        PropertiesConceptsModel(id=6, property_id=2, concept_id=10, enabled=True),
        PropertiesConceptsModel(id=7, property_id=3, concept_id=6, enabled=True),
        PropertiesConceptsModel(id=8, property_id=3, concept_id=9, enabled=True),
        PropertiesConceptsModel(id=9, property_id=4, concept_id=1, enabled=True),
        PropertiesConceptsModel(id=10, property_id=4, concept_id=4, enabled=False),
        PropertiesConceptsModel(id=11, property_id=5, concept_id=1, enabled=True),
        PropertiesConceptsModel(id=12, property_id=5, concept_id=5, enabled=True),
        PropertiesConceptsModel(id=13, property_id=6, concept_id=1, enabled=True),
        PropertiesConceptsModel(id=14, property_id=6, concept_id=7, enabled=False),
        PropertiesConceptsModel(id=15, property_id=7, concept_id=1, enabled=True),
        PropertiesConceptsModel(id=16, property_id=8, concept_id=5, enabled=True),
        PropertiesConceptsModel(id=17, property_id=9, concept_id=1, enabled=True),
        PropertiesConceptsModel(id=18, property_id=9, concept_id=8, enabled=True),
        PropertiesConceptsModel(id=19, property_id=10, concept_id=1, enabled=True),
        PropertiesConceptsModel(id=20, property_id=10, concept_id=3, enabled=True),
    ]
    session.add_all(pcs)
    session.commit()


def add_initial_transactions(session: Session) -> None:
    txs: list[TransactionModel] = []
    tid = 1

    for pc_id in range(1, 21):
        txs.append(
            TransactionModel(
                id=tid,
                date=date(2026, 1, (pc_id % 28) + 1),
                properties_concepts_id=pc_id,
                transaction_type="income",
                period="2026-01",
                amount=Decimal(str(300 + pc_id * 10)),
            )
        )
        tid += 1

        # Expense transaction
        txs.append(
            TransactionModel(
                id=tid,
                date=date(2026, 2, (pc_id % 28) + 1),
                properties_concepts_id=pc_id,
                transaction_type="expense",
                period="2026-02",
                amount=Decimal(str(20 + pc_id * 5)),
            )
        )
        tid += 1

    session.add_all(txs)
    session.commit()
