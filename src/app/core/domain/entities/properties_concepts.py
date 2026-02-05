from dataclasses import dataclass

from app.core.domain.entities.concept import Concept
from app.core.domain.entities.property import Property


@dataclass
class PropertiesConcepts:
    id: int | None
    concept_id: int
    property_id: int
    enabled: bool

    concept: Concept | None = None
    prop: Property | None = None
