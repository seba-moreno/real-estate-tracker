# tests/test_property_routes.py
from unittest.mock import MagicMock
from dependency_injector import providers
from fastapi.testclient import TestClient

from app.main import app


def _override_property_service(mock_service):
    """Override DI provider for the property service. Always reset after use."""
    app.container.services.property_service.override(providers.Object(mock_service))


def _reset_property_service_override():
    try:
        app.container.services.property_service.reset_last_overriding()
    except Exception:
        pass


# ---------------------------
# GET /api/v1/property/{id}
# ---------------------------


def test_get_property_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain = MagicMock()
    mock_service.get_by_id.return_value = mock_domain

    mock_response = {
        "id": 7,
        "location": "Example St. 123",
        "area": 50,
        "valuation": "100000",
        "details": "details",
    }

    _override_property_service(mock_service)
    try:

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.property.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.get("/api/v1/property/7")
        assert resp.status_code == 200
        assert resp.json() == mock_response
        mock_service.get_by_id.assert_called_once_with(7)
    finally:
        _reset_property_service_override()


def test_get_property_not_found_assertion_triggers_404(client: TestClient):
    """
    Route asserts the domain entity is not None.
    If service returns None -> AssertionError -> 404.
    """
    mock_service = MagicMock()
    mock_service.get_by_id.return_value = None

    _override_property_service(mock_service)
    try:
        resp = client.get("/api/v1/property/999")
        assert resp.status_code == 404
    finally:
        _reset_property_service_override()


# ---------------------------
# GET /api/v1/property/
# ---------------------------


def test_list_properties_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_list = [MagicMock(), MagicMock()]
    mock_service.get_all.return_value = mock_domain_list

    mock_response_list = [
        {
            "id": 1,
            "location": "A",
            "area": None,
            "valuation": "1000",
            "details": None,
        },
        {
            "id": 2,
            "location": "B",
            "area": 70,
            "valuation": "2000",
            "details": "x",
        },
    ]

    _override_property_service(mock_service)
    try:

        def fake_domain_list_to_response_schemas(_):
            return mock_response_list

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.property.domain_list_to_response_schemas",
            fake_domain_list_to_response_schemas,
        )

        resp = client.get("/api/v1/property/")
        assert resp.status_code == 200
        assert resp.json() == mock_response_list
        mock_service.get_all.assert_called_once_with()
    finally:
        _reset_property_service_override()


# ---------------------------
# POST /api/v1/property/
# ---------------------------


def test_create_property_created(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_in = MagicMock(name="domain_in")
    mock_domain_created = MagicMock(name="domain_created")
    mock_service.create.return_value = mock_domain_created

    payload = {
        "location": "Example St. 123",
        "area": 50,
        "valuation": "100000",  # decimal-compatible integer
        "details": "Additional details of the property",
    }

    mock_response = {
        "id": 10,
        "location": "Example St. 123",
        "area": 50,
        "valuation": "100000",
        "details": "Additional details of the property",
    }

    _override_property_service(mock_service)
    try:

        def fake_schema_to_domain(schema):
            # Basic shape checks for PropertyBase instance
            assert hasattr(schema, "location")
            assert hasattr(schema, "valuation")
            return mock_domain_in

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.property.schema_to_domain",
            fake_schema_to_domain,
        )
        monkeypatch.setattr(
            "app.presentation.api.v1.routes.property.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.post("/api/v1/property/", json=payload)
        assert resp.status_code == 201
        assert resp.json() == mock_response
        mock_service.create.assert_called_once_with(mock_domain_in)
    finally:
        _reset_property_service_override()


def test_create_property_validation_error_missing_required(client: TestClient):
    mock_service = MagicMock()
    _override_property_service(mock_service)
    try:
        # Missing required fields: 'location' and 'valuation'
        bad_payload = {"area": 10, "details": "x"}
        resp = client.post("/api/v1/property/", json=bad_payload)
        assert resp.status_code == 422
        mock_service.create.assert_not_called()
    finally:
        _reset_property_service_override()


def test_create_property_validation_error_bad_numbers(client: TestClient):
    mock_service = MagicMock()
    _override_property_service(mock_service)
    try:
        # area must be >= 1 if provided, valuation must be >= 0 and with 2 decimal places
        bad_payload = {
            "location": "A",
            "area": 0,  # invalid
            "valuation": "-1",  # invalid
            "details": None,
        }
        resp = client.post("/api/v1/property/", json=bad_payload)
        assert resp.status_code == 422
        mock_service.create.assert_not_called()
    finally:
        _reset_property_service_override()


# ---------------------------
# PUT /api/v1/property/{id}
# ---------------------------


def test_update_property_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_in = MagicMock(name="domain_in")
    mock_domain_updated = MagicMock(name="domain_updated")
    mock_service.update.return_value = mock_domain_updated

    payload = {
        "location": "Updated Location",
        "area": None,
        "valuation": "5000",
        "details": None,
    }

    mock_response = {
        "id": 42,
        "location": "Updated Location",
        "area": None,
        "valuation": "5000",
        "details": None,
    }

    _override_property_service(mock_service)
    try:

        def fake_schema_to_domain(schema):
            assert hasattr(schema, "location")
            return mock_domain_in

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.property.schema_to_domain",
            fake_schema_to_domain,
        )
        monkeypatch.setattr(
            "app.presentation.api.v1.routes.property.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.put("/api/v1/property/42", json=payload)
        assert resp.status_code == 200
        assert resp.json() == mock_response
        mock_service.update.assert_called_once_with(42, mock_domain_in)
    finally:
        _reset_property_service_override()


def test_update_property_validation_error(client: TestClient):
    mock_service = MagicMock()
    _override_property_service(mock_service)
    try:
        # invalid: empty location & negative valuation
        bad_payload = {
            "location": "",
            "area": 10,
            "valuation": "-5",
            "details": "invalid",
        }
        resp = client.put("/api/v1/property/1", json=bad_payload)
        assert resp.status_code == 422
        mock_service.update.assert_not_called()
    finally:
        _reset_property_service_override()


# ---------------------------
# DELETE /api/v1/property/{id}
# ---------------------------


def test_delete_property_no_content(client: TestClient):
    mock_service = MagicMock()
    mock_service.delete.return_value = True

    _override_property_service(mock_service)
    try:
        resp = client.delete("/api/v1/property/123")
        assert resp.status_code == 204
        assert resp.text == ""
        mock_service.delete.assert_called_once_with(123)
    finally:
        _reset_property_service_override()
