from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Property:
    id: int | None
    location: str
    area: int | None
    valuation: Decimal
    details: str | None
