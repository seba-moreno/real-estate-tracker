from __future__ import annotations
from datetime import date
from decimal import Decimal
import re
from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator


class TransactionBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "date": "2026-01-15",
                    "properties_concepts_id": 1,
                    "transaction_type": "income",
                    "period": "2027-01",
                    "amount": "100000.00",
                }
            ]
        },
    )

    date: Annotated[date, Field(description="Transaction's date (YYYY-MM-DD)")]
    properties_concepts_id: Annotated[
        int,
        Field(
            ge=1,
            description="Id of the properties_concepts that the Transaction belongs to",
        ),
    ]
    transaction_type: Annotated[
        str,
        Field(description="Type of transaction in lowercase ('income' or 'expense')"),
    ]
    period: Annotated[
        str,
        Field(
            description="Year and month that the Transaction due date belongs to (2026-01)"
        ),
    ]
    amount: Annotated[
        Decimal,
        Field(
            max_digits=19,
            decimal_places=2,
            ge=0,
            description="Amount of the Transaction (max 19 digits, 2 decimal places))",
        ),
    ]

    @field_validator("transaction_type", mode="before")
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("transaction_type must be a string")

        v = v.strip().lower()
        if v not in {"income", "expense"}:
            raise ValueError("transaction_type must be either 'income' or 'expense'")
        return v

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}$", v):
            raise ValueError("period must be in format YYYY-MM")

        month = int(v[5:7])

        if month < 1 or month > 12:
            raise ValueError("period month must be between 01 and 12")

        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError(
                "amount cannot be negative because transaction_type determines the sign."
            )

        str_val = format(v, "f")  # force normal decimal string (no exponent)
        if "." in str_val:
            decimals = str_val.split(".")[1]
            if len(decimals) > 2:
                raise ValueError("amount must have at most 2 decimal places")

        digits = str_val.replace(".", "")
        if len(digits) > 19:
            raise ValueError("amount must not exceed 19 total digits")

        return v


class CreateTransaction(TransactionBase):
    pass


class UpdateTransaction(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: Annotated[
        int, Field(ge=1, description="Unique identifier assigned by the system")
    ]
