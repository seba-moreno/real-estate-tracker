from __future__ import annotations
from datetime import date
from typing import Optional, Annotated, Self
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


class ContractBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "propertyId": 1,
                    "start_date": "2026-01-15",
                    "end_date": "2027-01-15",
                    "details": "Additional details of the contract",
                }
            ]
        },
    )

    property_id: Annotated[
        int, Field(ge=1, description="Id of the Property that the contract belongs to")
    ]
    start_date: Annotated[date, Field(description="Contract's start date (YYYY-MM-DD)")]
    end_date: Annotated[date, Field(description="Contract's end date (YYYY-MM-DD)")]
    details: Annotated[
        Optional[str],
        Field(default=None, max_length=500, description="Optional additional details"),
    ]

    @field_validator("details", mode="before")
    @classmethod
    def _normalize_details(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = v.strip()
        return s if s else None

    @model_validator(mode="after")
    def _validate_date_order(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("endDate must be on or after startDate.")
        return self


class CreateContract(ContractBase):
    pass


class UpdateContract(ContractBase):
    pass


class ContractResponse(ContractBase):
    id: Annotated[
        int, Field(ge=1, description="Unique identifier assigned by the system")
    ]
