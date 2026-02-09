# tests/test_properties_concepts_routes.py
from unittest.mock import MagicMock
from dependency_injector import providers
from fastapi.testclient import TestClient

from app.main import app


def _override_pc_service(mock_service):
    """Override DI provider for the properties_concepts service. Reset after use."""
    app.container.services.properties_concepts_service.override(
        providers.Object(mock_service)
    )


def _reset_pc_service_override():
    try:
        app.container.services.properties_concepts_service.reset_last_overriding()
    except Exception:
        pass


# ---------------------------
# GET /api/v1/properties-concepts/get-combos
# ---------------------------


def test_list_properties_concepts_combos_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_list = [MagicMock()]
    mock_service.get_combos.return_value = mock_domain_list

    mock_response_list = [
        {
            "id": 10,
            "concept_id": 1,
            "property_id": 2,
            "enabled": True,
            "concept": None,
            "property": None,
        }
    ]

    _override_pc_service(mock_service)
    try:

        def fake_domain_list_to_response_schemas(_):
            return mock_response_list

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.properties_concepts.domain_list_to_response_schemas",
            fake_domain_list_to_response_schemas,
        )

        resp = client.get("/api/v1/properties-concepts/get-combos")
        assert resp.status_code == 200
        assert resp.json() == mock_response_list
        mock_service.get_combos.assert_called_once_with()
    finally:
        _reset_pc_service_override()


# ---------------------------
# GET /api/v1/properties-concepts/{id}
# ---------------------------


def test_get_properties_concepts_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain = MagicMock()
    mock_service.get_by_id.return_value = mock_domain

    mock_response = {
        "id": 5,
        "concept_id": 1,
        "property_id": 1,
        "enabled": True,
        "concept": None,
        "property": None,
    }

    _override_pc_service(mock_service)
    try:

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.properties_concepts.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.get("/api/v1/properties-concepts/5")
        assert resp.status_code == 200
        assert resp.json() == mock_response
        mock_service.get_by_id.assert_called_once_with(5)
    finally:
        _reset_pc_service_override()


def test_get_properties_concepts_not_found_assertion_triggers_404(client: TestClient):
    """
    Route asserts domain entity is not None.
    If service returns None -> AssertionError -> 404.
    """
    mock_service = MagicMock()
    mock_service.get_by_id.return_value = None

    _override_pc_service(mock_service)
    try:
        resp = client.get("/api/v1/properties-concepts/999")
        assert resp.status_code == 404
    finally:
        _reset_pc_service_override()


# ---------------------------
# GET /api/v1/properties-concepts/
# ---------------------------


def test_list_properties_concepts_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_list = [MagicMock(), MagicMock()]
    mock_service.get_all.return_value = mock_domain_list

    mock_response_list = [
        {
            "id": 1,
            "concept_id": 2,
            "property_id": 3,
            "enabled": True,
            "concept": None,
            "property": None,
        },
        {
            "id": 2,
            "concept_id": 4,
            "property_id": 5,
            "enabled": False,
            "concept": None,
            "property": None,
        },
    ]

    _override_pc_service(mock_service)
    try:

        def fake_domain_list_to_response_schemas(_):
            return mock_response_list

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.properties_concepts.domain_list_to_response_schemas",
            fake_domain_list_to_response_schemas,
        )

        resp = client.get("/api/v1/properties-concepts/")
        assert resp.status_code == 200
        assert resp.json() == mock_response_list
        mock_service.get_all.assert_called_once_with()
    finally:
        _reset_pc_service_override()


# ---------------------------
# POST /api/v1/properties-concepts/
# ---------------------------


def test_create_properties_concepts_created(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_in = MagicMock(name="domain_in")
    mock_domain_created = MagicMock(name="domain_created")
    mock_service.create.return_value = mock_domain_created

    payload = {"concept_id": 1, "property_id": 2, "enabled": True}
    mock_response = {
        "id": 10,
        "concept_id": 1,
        "property_id": 2,
        "enabled": True,
        "concept": None,
        "property": None,
    }

    _override_pc_service(mock_service)
    try:

        def fake_schema_to_domain(schema):
            # Should receive a valid PropertiesConceptsBase instance
            assert hasattr(schema, "concept_id")
            assert hasattr(schema, "property_id")
            assert hasattr(schema, "enabled")
            return mock_domain_in

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.properties_concepts.schema_to_domain",
            fake_schema_to_domain,
        )
        monkeypatch.setattr(
            "app.presentation.api.v1.routes.properties_concepts.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.post("/api/v1/properties-concepts/", json=payload)
        assert resp.status_code == 201
        assert resp.json() == mock_response
        mock_service.create.assert_called_once_with(mock_domain_in)
    finally:
        _reset_pc_service_override()


def test_create_properties_concepts_validation_error(client: TestClient):
    mock_service = MagicMock()
    _override_pc_service(mock_service)
    try:
        # Missing required fields
        bad_payload = {"enabled": True}
        resp = client.post("/api/v1/properties-concepts/", json=bad_payload)
        assert resp.status_code == 422
        mock_service.create.assert_not_called()
    finally:
        _reset_pc_service_override()


def test_create_properties_concepts_validation_error_ids(client: TestClient):
    mock_service = MagicMock()
    _override_pc_service(mock_service)
    try:
        # concept_id and property_id must be >= 1
        bad_payload = {"concept_id": 0, "property_id": 0, "enabled": True}
        resp = client.post("/api/v1/properties-concepts/", json=bad_payload)
        assert resp.status_code == 422
        mock_service.create.assert_not_called()
    finally:
        _reset_pc_service_override()


# ---------------------------
# PUT /api/v1/properties-concepts/{id}
# ---------------------------


def test_update_properties_concepts_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_in = MagicMock(name="domain_in")
    mock_domain_updated = MagicMock(name="domain_updated")
    mock_service.update.return_value = mock_domain_updated

    payload = {"concept_id": 3, "property_id": 4, "enabled": False}
    mock_response = {
        "id": 77,
        "concept_id": 3,
        "property_id": 4,
        "enabled": False,
        "concept": None,
        "property": None,
    }

    _override_pc_service(mock_service)
    try:

        def fake_schema_to_domain(schema):
            assert hasattr(schema, "concept_id")
            return mock_domain_in

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.properties_concepts.schema_to_domain",
            fake_schema_to_domain,
        )
        monkeypatch.setattr(
            "app.presentation.api.v1.routes.properties_concepts.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.put("/api/v1/properties-concepts/77", json=payload)
        assert resp.status_code == 200
        assert resp.json() == mock_response
        mock_service.update.assert_called_once_with(77, mock_domain_in)
    finally:
        _reset_pc_service_override()


def test_update_properties_concepts_validation_error(client: TestClient):
    mock_service = MagicMock()
    _override_pc_service(mock_service)
    try:
        # invalid ids
        bad_payload = {"concept_id": 0, "property_id": 1, "enabled": True}
        resp = client.put("/api/v1/properties-concepts/1", json=bad_payload)
        assert resp.status_code == 422
        mock_service.update.assert_not_called()
    finally:
        _reset_pc_service_override()


# ---------------------------
# DELETE /api/v1/properties-concepts/{id}
# ---------------------------


def test_delete_properties_concepts_no_content(client: TestClient):
    mock_service = MagicMock()
    mock_service.delete.return_value = True

    _override_pc_service(mock_service)
    try:
        resp = client.delete("/api/v1/properties-concepts/123")
        assert resp.status_code == 204
        assert resp.text == ""
        mock_service.delete.assert_called_once_with(123)
    finally:
        _reset_pc_service_override()
