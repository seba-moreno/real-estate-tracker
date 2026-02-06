from app.core.domain.entities.auth import JwtToken, LoginCredentials, UserCreate
from app.presentation.api.v1.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)


def login_domain_to_schema(credentials: LoginCredentials) -> LoginRequest:
    return LoginRequest(username=credentials.username, password=credentials.password)


def login_schema_to_domain(credentials: LoginRequest) -> LoginCredentials:
    return LoginCredentials(
        username=credentials.username, password=credentials.password
    )


def token_domain_to_schema(token: JwtToken) -> TokenResponse:
    return TokenResponse(
        access_token=token.access_token,
        token_type=token.token_type,
        expires_in=token.expires_in,
    )


def token_schema_to_domain(token: TokenResponse) -> JwtToken:
    return JwtToken(
        access_token=token.access_token,
        token_type=token.token_type,
        expires_in=token.expires_in,
    )


def register_domain_to_schema(user: UserCreate) -> RegisterRequest:
    return RegisterRequest(
        username=user.username,
        password=user.password,
        email=user.email,
        is_active=user.is_active,
    )


def register_schema_to_domain(user: RegisterRequest) -> UserCreate:
    return UserCreate(
        username=user.username,
        password=user.password,
        email=user.email,
        is_active=user.is_active,
    )
