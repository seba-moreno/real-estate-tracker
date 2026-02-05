from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.core.domain.entities.properties_concepts import PropertiesConcepts


@dataclass
class Transaction:
    id: int | None
    date: date
    properties_concepts_id: int
    transaction_type: str
    period: str
    amount: Decimal

    properties_concepts: PropertiesConcepts | None = None
