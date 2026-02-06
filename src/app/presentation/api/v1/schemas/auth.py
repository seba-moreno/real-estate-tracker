from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
    )
    username: Annotated[
        str,
        Field(min_length=1, max_length=100),
    ]
    password: Annotated[
        str,
        Field(min_length=1, max_length=100),
    ]


class TokenResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
    )

    access_token: Annotated[
        str,
        Field(min_length=1, max_length=100),
    ]
    token_type: Annotated[
        str,
        Field(min_length=1, max_length=100, default="Bearer"),
    ]
    expires_in: Annotated[
        int,
        Field(ge=1),
    ]


class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
    )

    username: Annotated[
        str,
        Field(min_length=1, max_length=100),
    ]
    password: Annotated[
        str,
        Field(min_length=1, max_length=100),
    ]
    email: Annotated[
        str | None,
        Field(min_length=1, max_length=100, default=None),
    ]
    is_active: Annotated[
        bool,
        Field(),
    ]
