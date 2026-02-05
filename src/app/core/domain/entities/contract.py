from dataclasses import dataclass
from datetime import date

from app.core.domain.entities.property import Property


@dataclass
class Contract:
    id: int | None
    property_id: int
    start_date: date
    end_date: date
    details: str | None

    prop: Property | None = None
