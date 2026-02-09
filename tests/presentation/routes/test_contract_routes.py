# tests/test_contract_routes.py
from unittest.mock import MagicMock
from dependency_injector import providers
from fastapi.testclient import TestClient

from app.main import app


def _override_contract_service(mock_service):
    """Override DI provider for the contract service. Always reset after use."""
    app.container.services.contract_service.override(providers.Object(mock_service))


def _reset_contract_service_override():
    try:
        app.container.services.contract_service.reset_last_overriding()
    except Exception:
        pass


# ---------------------------
# GET /api/v1/contract/{id}
# ---------------------------


def test_get_contract_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain = MagicMock()
    mock_service.get_by_id.return_value = mock_domain

    mock_response = {
        "id": 7,
        "property_id": 3,
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "details": "details",
    }

    _override_contract_service(mock_service)
    try:

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.contract.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.get("/api/v1/contract/7")
        assert resp.status_code == 200
        assert resp.json() == mock_response
        mock_service.get_by_id.assert_called_once_with(7)
    finally:
        _reset_contract_service_override()


def test_get_contract_not_found_assertion_triggers_404(client: TestClient):
    """
    Route asserts the domain entity is not None.
    If service returns None -> AssertionError -> 404.
    """
    mock_service = MagicMock()
    mock_service.get_by_id.return_value = None

    _override_contract_service(mock_service)
    try:
        resp = client.get("/api/v1/contract/999")
        assert resp.status_code == 404
    finally:
        _reset_contract_service_override()


# ---------------------------
# GET /api/v1/contract/
# ---------------------------


def test_list_contracts_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_list = [MagicMock(), MagicMock()]
    mock_service.get_all.return_value = mock_domain_list

    mock_response_list = [
        {
            "id": 1,
            "property_id": 10,
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "details": None,
        },
        {
            "id": 2,
            "property_id": 11,
            "start_date": "2026-02-01",
            "end_date": "2027-01-31",
            "details": "x",
        },
    ]

    _override_contract_service(mock_service)
    try:

        def fake_domain_list_to_response_schemas(_):
            return mock_response_list

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.contract.domain_list_to_response_schemas",
            fake_domain_list_to_response_schemas,
        )

        resp = client.get("/api/v1/contract/")
        assert resp.status_code == 200
        assert resp.json() == mock_response_list
        mock_service.get_all.assert_called_once_with()
    finally:
        _reset_contract_service_override()


# ---------------------------
# GET /api/v1/contract/ending-in/{months}
# ---------------------------


def test_get_contracts_ending_in_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_list = [MagicMock()]
    mock_service.get_contracts_ending_within.return_value = mock_domain_list

    mock_response_list = [
        {
            "id": 5,
            "property_id": 20,
            "start_date": "2026-03-01",
            "end_date": "2026-06-01",
            "details": "ending soon",
        }
    ]

    _override_contract_service(mock_service)
    try:

        def fake_domain_list_to_response_schemas(_):
            return mock_response_list

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.contract.domain_list_to_response_schemas",
            fake_domain_list_to_response_schemas,
        )

        resp = client.get("/api/v1/contract/ending-in/3")
        assert resp.status_code == 200
        assert resp.json() == mock_response_list
        mock_service.get_contracts_ending_within.assert_called_once_with(3)
    finally:
        _reset_contract_service_override()


# ---------------------------
# POST /api/v1/contract/
# ---------------------------


def test_create_contract_created(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_in = MagicMock(name="domain_in")
    mock_domain_created = MagicMock(name="domain_created")
    mock_service.create.return_value = mock_domain_created

    payload = {
        "property_id": 10,
        "start_date": "2026-01-15",
        "end_date": "2026-12-15",
        "details": "Additional details of the contract",
    }

    mock_response = {
        "id": 10,
        "property_id": 10,
        "start_date": "2026-01-15",
        "end_date": "2026-12-15",
        "details": "Additional details of the contract",
    }

    _override_contract_service(mock_service)
    try:

        def fake_schema_to_domain(_schema):
            # We don't depend on specific schema type here; just confirm route passed something
            assert hasattr(_schema, "property_id")
            return mock_domain_in

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.contract.schema_to_domain",
            fake_schema_to_domain,
        )
        monkeypatch.setattr(
            "app.presentation.api.v1.routes.contract.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.post("/api/v1/contract/", json=payload)
        assert resp.status_code == 201
        assert resp.json() == mock_response
        mock_service.create.assert_called_once_with(mock_domain_in)
    finally:
        _reset_contract_service_override()


def test_create_contract_validation_error_missing_or_wrong_fields(client: TestClient):
    mock_service = MagicMock()
    _override_contract_service(mock_service)
    try:
        # Missing required property_id and dates
        bad_payload = {"details": "x"}
        resp = client.post("/api/v1/contract/", json=bad_payload)
        assert resp.status_code == 422
        mock_service.create.assert_not_called()
    finally:
        _reset_contract_service_override()


def test_create_contract_validation_error_end_before_start(client: TestClient):
    mock_service = MagicMock()
    _override_contract_service(mock_service)
    try:
        # Violates model_validator (end_date < start_date)
        bad_payload = {
            "property_id": 1,
            "start_date": "2026-02-01",
            "end_date": "2026-01-01",
            "details": None,
        }
        resp = client.post("/api/v1/contract/", json=bad_payload)
        # Pydantic validation -> 422
        assert resp.status_code == 422
        mock_service.create.assert_not_called()
    finally:
        _reset_contract_service_override()


# ---------------------------
# PUT /api/v1/contract/{id}
# ---------------------------


def test_update_contract_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_in = MagicMock(name="domain_in")
    mock_domain_updated = MagicMock(name="domain_updated")
    mock_service.update.return_value = mock_domain_updated

    payload = {
        "property_id": 99,
        "start_date": "2026-05-01",
        "end_date": "2026-12-01",
        "details": None,
    }

    mock_response = {
        "id": 42,
        "property_id": 99,
        "start_date": "2026-05-01",
        "end_date": "2026-12-01",
        "details": None,
    }

    _override_contract_service(mock_service)
    try:

        def fake_schema_to_domain(_schema):
            assert hasattr(_schema, "property_id")
            return mock_domain_in

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.contract.schema_to_domain",
            fake_schema_to_domain,
        )
        monkeypatch.setattr(
            "app.presentation.api.v1.routes.contract.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.put("/api/v1/contract/42", json=payload)
        assert resp.status_code == 200
        assert resp.json() == mock_response
        mock_service.update.assert_called_once_with(42, mock_domain_in)
    finally:
        _reset_contract_service_override()


def test_update_contract_validation_error(client: TestClient):
    mock_service = MagicMock()
    _override_contract_service(mock_service)
    try:
        # property_id < 1 not allowed; also end < start
        bad_payload = {
            "property_id": 0,
            "start_date": "2026-06-01",
            "end_date": "2026-05-01",
            "details": "invalid",
        }
        resp = client.put("/api/v1/contract/1", json=bad_payload)
        assert resp.status_code == 422
        mock_service.update.assert_not_called()
    finally:
        _reset_contract_service_override()


# ---------------------------
# DELETE /api/v1/contract/{id}
# ---------------------------


def test_delete_contract_no_content(client: TestClient):
    mock_service = MagicMock()
    mock_service.delete.return_value = True

    _override_contract_service(mock_service)
    try:
        resp = client.delete("/api/v1/contract/123")
        assert resp.status_code == 204
        assert resp.text == ""
        mock_service.delete.assert_called_once_with(123)
    finally:
        _reset_contract_service_override()
