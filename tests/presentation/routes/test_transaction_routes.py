# tests/test_transaction_routes.py
from unittest.mock import MagicMock
from dependency_injector import providers
from fastapi.testclient import TestClient

from app.main import app


def _override_transaction_service(mock_service):
    """Override DI provider for the transaction service. Always reset after use."""
    app.container.services.transaction_service.override(providers.Object(mock_service))


def _reset_transaction_service_override():
    try:
        app.container.services.transaction_service.reset_last_overriding()
    except Exception:
        pass


# ---------------------------
# GET /api/v1/transaction/balance
# ---------------------------


def test_get_transactions_balance_ok(client: TestClient):
    mock_service = MagicMock()
    mock_service.get_balance.return_value = 1234.56

    _override_transaction_service(mock_service)
    try:
        resp = client.get("/api/v1/transaction/balance")
        assert resp.status_code == 200
        assert resp.json() == {"balance": 1234.56}
        mock_service.get_balance.assert_called_once_with()
    finally:
        _reset_transaction_service_override()


# ---------------------------
# GET /api/v1/transaction/{id}
# ---------------------------


def test_get_transaction_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain = MagicMock()
    mock_service.get_by_id.return_value = mock_domain

    mock_response = {
        "id": 7,
        "date": "2026-01-15",
        "properties_concepts_id": 1,
        "transaction_type": "income",
        "period": "2026-05",
        "amount": "1000",
    }

    _override_transaction_service(mock_service)
    try:

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.transaction.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.get("/api/v1/transaction/7")
        assert resp.status_code == 200
        assert resp.json() == mock_response
        mock_service.get_by_id.assert_called_once_with(7)
    finally:
        _reset_transaction_service_override()


def test_get_transaction_not_found_assertion_triggers_404(client: TestClient):
    """
    The route catches AssertionError internally and returns 404.
    Therefore this test should assert the HTTP 404 response,
    not expect an AssertionError to bubble up.
    """
    mock_service = MagicMock()
    mock_service.get_by_id.return_value = None

    _override_transaction_service(mock_service)
    try:
        resp = client.get("/api/v1/transaction/999")
        assert resp.status_code == 404
    finally:
        _reset_transaction_service_override()


# ---------------------------
# GET /api/v1/transaction/
# ---------------------------


def test_list_transactions_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_list = [MagicMock(), MagicMock()]
    mock_service.get_all.return_value = mock_domain_list

    mock_response_list = [
        {
            "id": 1,
            "date": "2026-01-01",
            "properties_concepts_id": 2,
            "transaction_type": "income",
            "period": "2026-01",
            "amount": "500",
        },
        {
            "id": 2,
            "date": "2026-02-01",
            "properties_concepts_id": 3,
            "transaction_type": "expense",
            "period": "2026-02",
            "amount": "250",
        },
    ]

    _override_transaction_service(mock_service)
    try:

        def fake_domain_list_to_response_schemas(_):
            return mock_response_list

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.transaction.domain_list_to_response_schemas",
            fake_domain_list_to_response_schemas,
        )

        resp = client.get("/api/v1/transaction/")
        assert resp.status_code == 200
        assert resp.json() == mock_response_list
        mock_service.get_all.assert_called_once_with()
    finally:
        _reset_transaction_service_override()


# ---------------------------
# POST /api/v1/transaction/
# ---------------------------


def test_create_transaction_created(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_in = MagicMock(name="domain_in")
    mock_domain_created = MagicMock(name="domain_created")
    mock_service.create.return_value = mock_domain_created

    payload = {
        "date": "2026-01-15",
        "properties_concepts_id": 1,
        "transaction_type": "income",
        "period": "2026-05",
        "amount": "1000.00",
    }

    mock_response = {
        "id": 10,
        "date": "2026-01-15",
        "properties_concepts_id": 1,
        "transaction_type": "income",
        "period": "2026-05",
        "amount": "1000",
    }

    _override_transaction_service(mock_service)
    try:

        def fake_schema_to_domain(schema):
            assert hasattr(schema, "date")
            assert hasattr(schema, "properties_concepts_id")
            assert hasattr(schema, "transaction_type")
            assert hasattr(schema, "period")
            assert hasattr(schema, "amount")
            return mock_domain_in

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.transaction.schema_to_domain",
            fake_schema_to_domain,
        )
        monkeypatch.setattr(
            "app.presentation.api.v1.routes.transaction.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.post("/api/v1/transaction/", json=payload)
        assert resp.status_code == 201
        assert resp.json() == mock_response
        mock_service.create.assert_called_once_with(mock_domain_in)
    finally:
        _reset_transaction_service_override()


def test_create_transaction_validation_error_missing_fields(client: TestClient):
    mock_service = MagicMock()
    _override_transaction_service(mock_service)
    try:
        bad_payload = {
            "properties_concepts_id": 1,
            "transaction_type": "income",
            "period": "2026-01",
            "amount": "10.00",
        }
        resp = client.post("/api/v1/transaction/", json=bad_payload)
        assert resp.status_code == 422
        mock_service.create.assert_not_called()
    finally:
        _reset_transaction_service_override()


def test_create_transaction_validation_error_business_rules(client: TestClient):
    mock_service = MagicMock()
    _override_transaction_service(mock_service)
    try:
        bad_payload = {
            "date": "2026-01-15",
            "properties_concepts_id": 1,
            "transaction_type": "income",
            "period": "2026-13",
            "amount": "10.999",
        }
        resp = client.post("/api/v1/transaction/", json=bad_payload)
        assert resp.status_code == 422
        mock_service.create.assert_not_called()
    finally:
        _reset_transaction_service_override()


# ---------------------------
# PUT /api/v1/transaction/{id}
# ---------------------------


def test_update_transaction_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_in = MagicMock(name="domain_in")
    mock_domain_updated = MagicMock(name="domain_updated")
    mock_service.update.return_value = mock_domain_updated

    payload = {
        "date": "2026-02-01",
        "properties_concepts_id": 2,
        "transaction_type": "expense",
        "period": "2026-02",
        "amount": "50.00",
    }

    mock_response = {
        "id": 42,
        "date": "2026-02-01",
        "properties_concepts_id": 2,
        "transaction_type": "expense",
        "period": "2026-02",
        "amount": "50",
    }

    _override_transaction_service(mock_service)
    try:

        def fake_schema_to_domain(schema):
            assert hasattr(schema, "transaction_type")
            return mock_domain_in

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.transaction.schema_to_domain",
            fake_schema_to_domain,
        )
        monkeypatch.setattr(
            "app.presentation.api.v1.routes.transaction.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.put("/api/v1/transaction/42", json=payload)
        assert resp.status_code == 200
        assert resp.json() == mock_response
        mock_service.update.assert_called_once_with(42, mock_domain_in)
    finally:
        _reset_transaction_service_override()


def test_update_transaction_validation_error(client: TestClient):
    mock_service = MagicMock()
    _override_transaction_service(mock_service)
    try:
        bad_payload = {
            "date": "2026-01-15",
            "properties_concepts_id": 1,
            "transaction_type": "invalid",
            "period": "2026-01",
            "amount": "-5.00",
        }
        resp = client.put("/api/v1/transaction/1", json=bad_payload)
        assert resp.status_code == 422
        mock_service.update.assert_not_called()
    finally:
        _reset_transaction_service_override()


# ---------------------------
# DELETE /api/v1/transaction/{id}
# ---------------------------


def test_delete_transaction_no_content(client: TestClient):
    mock_service = MagicMock()
    mock_service.delete.return_value = True

    _override_transaction_service(mock_service)
    try:
        resp = client.delete("/api/v1/transaction/123")
        assert resp.status_code == 204
        assert resp.text == ""
        mock_service.delete.assert_called_once_with(123)
    finally:
        _reset_transaction_service_override()
