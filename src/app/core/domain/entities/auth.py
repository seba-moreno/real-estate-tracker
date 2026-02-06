from dataclasses import dataclass


@dataclass
class LoginCredentials:
    username: str
    password: str


@dataclass
class JwtToken:
    access_token: str
    token_type: str
    expires_in: int


@dataclass
class UserCreate:
    username: str
    email: str | None
    password: str
    is_active: bool
