from app.presentation.api.v1.mappers.auth_mapper import (
    login_domain_to_schema,
    login_schema_to_domain,
    token_domain_to_schema,
    token_schema_to_domain,
    register_domain_to_schema,
    register_schema_to_domain,
)
from app.core.domain.entities.auth import JwtToken, LoginCredentials, UserCreate
from app.presentation.api.v1.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)


# ---------------------------
# Login mappers
# ---------------------------


def test_login_schema_to_domain():
    schema = LoginRequest(username="john", password="secret")
    domain = login_schema_to_domain(schema)

    assert isinstance(domain, LoginCredentials)
    assert domain.username == "john"
    assert domain.password == "secret"


def test_login_domain_to_schema():
    domain = LoginCredentials(username="john", password="secret")
    schema = login_domain_to_schema(domain)

    assert isinstance(schema, LoginRequest)
    assert schema.username == "john"
    assert schema.password == "secret"


def test_login_schema_domain_round_trip():
    schema = LoginRequest(username="user", password="pass")
    domain = login_schema_to_domain(schema)
    schema2 = login_domain_to_schema(domain)

    assert schema2 == schema


# ---------------------------
# Token mappers
# ---------------------------


def test_token_schema_to_domain():
    schema = TokenResponse(
        access_token="abc123",
        token_type="Bearer",
        expires_in=3600,
    )
    domain = token_schema_to_domain(schema)

    assert isinstance(domain, JwtToken)
    assert domain.access_token == "abc123"
    assert domain.token_type == "Bearer"
    assert domain.expires_in == 3600


def test_token_domain_to_schema():
    domain = JwtToken(access_token="abc123", token_type="Bearer", expires_in=3600)
    schema = token_domain_to_schema(domain)

    assert isinstance(schema, TokenResponse)
    assert schema.access_token == "abc123"
    assert schema.token_type == "Bearer"
    assert schema.expires_in == 3600


def test_token_schema_domain_round_trip():
    schema = TokenResponse(access_token="aaa", token_type="Bearer", expires_in=300)
    domain = token_schema_to_domain(schema)
    schema2 = token_domain_to_schema(domain)

    assert schema2 == schema


# ---------------------------
# Register mappers
# ---------------------------


def test_register_schema_to_domain():
    schema = RegisterRequest(
        username="alice",
        password="pw",
        email="alice@example.com",
        is_active=True,
    )

    domain = register_schema_to_domain(schema)

    assert isinstance(domain, UserCreate)
    assert domain.username == "alice"
    assert domain.password == "pw"
    assert domain.email == "alice@example.com"
    assert domain.is_active is True


def test_register_domain_to_schema():
    domain = UserCreate(
        username="bob",
        password="pw",
        email="bob@example.com",
        is_active=False,
    )

    schema = register_domain_to_schema(domain)

    assert isinstance(schema, RegisterRequest)
    assert schema.username == "bob"
    assert schema.password == "pw"
    assert schema.email == "bob@example.com"
    assert schema.is_active is False


def test_register_schema_domain_round_trip():
    schema = RegisterRequest(
        username="test",
        password="pw",
        email=None,
        is_active=True,
    )

    domain = register_schema_to_domain(schema)
    schema2 = register_domain_to_schema(domain)

    assert schema2 == schema
