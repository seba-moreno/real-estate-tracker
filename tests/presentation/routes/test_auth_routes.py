from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.domain.entities.auth import JwtToken


def _override_auth_service(mock):
    """
    Override the dependency_injector provider for the auth service.
    We must undo the override after the test to avoid cross-test leakage.
    """
    app.container.services.auth_service.override(mock)


def _reset_auth_service_override():
    try:
        app.container.services.auth_service.reset_last_overriding()
    except Exception:
        # If nothing was overridden, ignore
        pass


def test_login_ok(client: TestClient):
    mock_service = MagicMock()
    token = JwtToken(access_token="abc123", token_type="bearer", expires_in=3600)
    mock_service.login.return_value = token

    _override_auth_service(mock_service)
    try:
        payload = {"username": "john", "password": "s3cr3t"}
        resp = client.post("/api/v1/auth/login", json=payload)

        assert resp.status_code == 200
        body = resp.json()
        assert body == {
            "access_token": "abc123",
            "token_type": "bearer",
            "expires_in": 3600,
        }

        # mapper should have turned schema into a domain-like object;
        # we can at least assert we got called once with an object
        assert mock_service.login.call_count == 1
        # The first positional argument of the first call is the mapped domain object
        call_args, _ = mock_service.login.call_args
        assert len(call_args) == 1
        domain_obj = call_args[0]
        # Basic structural assertions (attributes present)
        assert hasattr(domain_obj, "username")
        assert hasattr(domain_obj, "password")
        assert domain_obj.username == "john"
        assert domain_obj.password == "s3cr3t"
    finally:
        _reset_auth_service_override()


def test_login_validation_error(client: TestClient):
    mock_service = MagicMock()
    _override_auth_service(mock_service)
    try:
        # Missing required fields should trigger 422 (Pydantic validation)
        resp = client.post("/api/v1/auth/login", json={"username": "only-username"})
        assert resp.status_code == 422
        # Service must NOT be called on validation error
        mock_service.login.assert_not_called()
    finally:
        _reset_auth_service_override()


def test_register_created(client: TestClient):
    mock_service = MagicMock()
    mock_service.register.return_value = None

    _override_auth_service(mock_service)
    try:
        payload = {
            "username": "alice",
            "password": "P@ssw0rd!",
            "email": "alice@example.com",
            "is_active": True,
        }

        resp = client.post("/api/v1/auth/register", json=payload)

        assert resp.status_code == 201
        # By default, FastAPI returns `null` in JSON for `None` body; depending on your response model
        # and handler, it may be an empty response. We assert both possibilities for robustness:
        assert resp.text in ("null", "")

        assert mock_service.register.call_count == 1
        call_args, _ = mock_service.register.call_args
        assert len(call_args) == 1
        domain_obj = call_args[0]
        # Structural assertions
        assert hasattr(domain_obj, "username")
        assert hasattr(domain_obj, "password")
        assert hasattr(domain_obj, "email")
        assert domain_obj.username == "alice"
        assert domain_obj.password == "P@ssw0rd!"
        assert domain_obj.email == "alice@example.com"
    finally:
        _reset_auth_service_override()


def test_register_validation_error(client: TestClient):
    mock_service = MagicMock()
    _override_auth_service(mock_service)
    try:
        # Missing required fields (e.g., no password / email)
        resp = client.post("/api/v1/auth/register", json={"username": "bob"})
        assert resp.status_code == 422
        mock_service.register.assert_not_called()
    finally:
        _reset_auth_service_override()
