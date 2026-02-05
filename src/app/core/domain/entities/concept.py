from dataclasses import dataclass


@dataclass
class Concept:
    id: int | None
    name: str
    is_ordinary: bool
    periodicity: int | None
    description: str | None
