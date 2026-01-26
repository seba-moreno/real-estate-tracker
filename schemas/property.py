from __future__ import annotations
from decimal import Decimal
from typing import Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator

class PropertyBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "location": "Example St. 123",
                    "area": 50,
                    "valuation": 100000,
                    "details": "Additional details of the property",
                }
            ]
        },
    )

    location: Annotated[str, Field(min_length=1, max_length=100, description="Property's adress")]
    area: Annotated[Optional[int], Field(default=None, ge=1, description="Property's size in m2")]
    valuation: Annotated[Decimal, Field(max_digits=19, decimal_places=2, ge=0, description="Property's market value")]
    details: Annotated[Optional[str], Field(default=None, max_length=500, description="Optional additional details")]

    @field_validator("location", "details", mode="before")
    @classmethod
    def _trim_strings(cls, v):
        if isinstance(v, str):
            v = v.strip()
        return v

class CreateProperty(PropertyBase):
    pass

class UpdateProperty(PropertyBase):
    pass

class PropertyResponse(PropertyBase):
    id: Annotated[int, Field(ge=1, description="Unique identifier assigned by the system")] 
