from __future__ import annotations
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict


class ConceptBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "Lease collection",
                    "is_ordinary": True,
                    "periodicity": 1,
                    "description": "Monthly lease collection",
                }
            ]
        },
    )

    name: Annotated[
        str,
        Field(min_length=1, max_length=100, description="Human-friendly concept name"),
    ]
    is_ordinary: Annotated[
        bool, Field(description="Whether the concept is ordinary/recurring")
    ]
    periodicity: Annotated[
        None | int,
        Field(default=None, ge=0, description="Recurrence interval in months (≥ 0)"),
    ]
    description: Annotated[
        None | str,
        Field(default=None, max_length=500, description="Optional additional details"),
    ]


class CreateConcept(ConceptBase):
    pass


class UpdateConcept(ConceptBase):
    pass


class ConceptResponse(ConceptBase):
    id: Annotated[
        int, Field(ge=1, description="Unique identifier assigned by the system")
    ]
