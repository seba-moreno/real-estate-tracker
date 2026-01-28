from __future__ import annotations
from typing import Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ConceptBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "Lease collection",
                    "isOrdinary": True,
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
        Optional[int],
        Field(default=None, ge=0, description="Recurrence interval in months (≥ 0)"),
    ]
    description: Annotated[
        Optional[str],
        Field(default=None, max_length=500, description="Optional additional details"),
    ]

    @field_validator("name", "description", mode="before")
    @classmethod
    def _trim_strings(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
        return v


class CreateConcept(ConceptBase):
    pass


class UpdateConcept(ConceptBase):
    pass


class ConceptResponse(ConceptBase):
    id: Annotated[
        int, Field(ge=1, description="Unique identifier assigned by the system")
    ]
