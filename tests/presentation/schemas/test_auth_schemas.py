import pytest
from pydantic import ValidationError

from app.presentation.api.v1.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RegisterRequest,
)


# ---------------------------
# LoginRequest
# ---------------------------


def test_login_request_happy_path_strips_whitespace_and_validates():
    data = {
        "username": "  john_doe  ",
        "password": "  s3cr3t  ",
    }
    obj = LoginRequest(**data)
    # str_strip_whitespace=True -> leading/trailing spaces removed
    assert obj.username == "john_doe"
    assert obj.password == "s3cr3t"


@pytest.mark.parametrize("field", ["username", "password"])
def test_login_request_rejects_empty_strings(field):
    data = {
        "username": "john",
        "password": "pass",
    }
    data[field] = ""  # violate min_length=1
    with pytest.raises(ValidationError) as exc:
        LoginRequest(**data)
    # Ensure the correct field is mentioned
    assert field in str(exc.value)


def test_login_request_rejects_extra_fields():
    with pytest.raises(ValidationError) as exc:
        LoginRequest(username="john", password="pass", unexpected="nope")
    # extra="forbid" should flag "unexpected"
    assert "unexpected" in str(exc.value)


def test_login_request_max_length_enforced():
    long_val = "x" * 101  # max_length=100
    with pytest.raises(ValidationError):
        LoginRequest(username=long_val, password="ok")
    with pytest.raises(ValidationError):
        LoginRequest(username="ok", password=long_val)


# ---------------------------
# TokenResponse
# ---------------------------


def test_token_response_happy_path_with_default_token_type_and_numeric_expires():
    obj = TokenResponse(access_token="abc123", token_type="Bearer", expires_in=3600)
    assert obj.access_token == "abc123"
    assert obj.token_type == "Bearer"
    assert obj.expires_in == 3600


def test_token_response_default_token_type_is_bearer_if_omitted():
    obj = TokenResponse(access_token="abc123", expires_in=600)
    assert obj.access_token == "abc123"
    assert obj.token_type == "Bearer"  # default applied
    assert obj.expires_in == 600


def test_token_response_rejects_zero_or_negative_expires_in():
    with pytest.raises(ValidationError):
        TokenResponse(access_token="abc", expires_in=0)
    with pytest.raises(ValidationError):
        TokenResponse(access_token="abc", expires_in=-1)


def test_token_response_rejects_extra_fields():
    with pytest.raises(ValidationError) as exc:
        TokenResponse(access_token="abc", expires_in=1, unexpected="nope")
    assert "unexpected" in str(exc.value)


def test_token_response_strips_whitespace_and_enforces_lengths():
    obj = TokenResponse(access_token="  tok  ", token_type="  Bearer  ", expires_in=1)
    assert obj.access_token == "tok"
    assert obj.token_type == "Bearer"

    too_long = "x" * 101
    with pytest.raises(ValidationError):
        TokenResponse(access_token=too_long, expires_in=1)
    with pytest.raises(ValidationError):
        TokenResponse(access_token="ok", token_type=too_long, expires_in=1)


# ---------------------------
# RegisterRequest
# ---------------------------


def test_register_request_happy_path_with_optional_email_and_bool():
    data = {
        "username": "  alice  ",
        "password": "  P@ssw0rd  ",
        "email": "  alice@example.com  ",
        "is_active": True,
    }
    obj = RegisterRequest(**data)
    # whitespace trimmed on strings
    assert obj.username == "alice"
    assert obj.password == "P@ssw0rd"
    assert obj.email == "alice@example.com"
    assert obj.is_active is True


def test_register_request_email_can_be_none_and_trims_if_present():
    # Explicit None
    obj = RegisterRequest(username="bob", password="pass", email=None, is_active=False)
    assert obj.email is None
    assert obj.is_active is False

    # Present but with whitespace
    obj2 = RegisterRequest(
        username="bob", password="pass", email="  x@y.z  ", is_active=True
    )
    assert obj2.email == "x@y.z"
    assert obj2.is_active is True


@pytest.mark.parametrize("field", ["username", "password"])
def test_register_request_rejects_empty_username_or_password(field):
    payload = {
        "username": "ok",
        "password": "ok",
        "email": None,
        "is_active": True,
    }
    payload[field] = ""  # violates min_length=1
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(**payload)
    assert field in str(exc.value)


def test_register_request_rejects_missing_is_active():
    # is_active is required (no default)
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(username="u", password="p")
    assert "is_active" in str(exc.value)


def test_register_request_rejects_extra_fields():
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(username="u", password="p", is_active=True, unexpected="nope")
    assert "unexpected" in str(exc.value)


def test_register_request_max_length_enforced_for_all_strings():
    too_long = "x" * 101
    with pytest.raises(ValidationError):
        RegisterRequest(username=too_long, password="p", is_active=True)
    with pytest.raises(ValidationError):
        RegisterRequest(username="u", password=too_long, is_active=True)
    with pytest.raises(ValidationError):
        RegisterRequest(username="u", password="p", email=too_long, is_active=True)
