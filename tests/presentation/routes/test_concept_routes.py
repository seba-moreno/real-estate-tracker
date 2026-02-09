from unittest.mock import MagicMock
from dependency_injector import providers
from fastapi.testclient import TestClient
from app.main import app
from app.presentation.api.v1.schemas.concept import ConceptBase


def _override_concept_service(mock_service):
    """Override DI provider for the concept service. Always reset after use."""
    app.container.services.concept_service.override(providers.Object(mock_service))


def _reset_concept_service_override():
    try:
        app.container.services.concept_service.reset_last_overriding()
    except Exception:
        pass


def test_get_concept_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain = MagicMock()
    mock_service.get_by_id.return_value = mock_domain

    # Make the mapper return a fully-valid ConceptResponse dict
    mock_response = {
        "id": 1,
        "name": "Concept A",
        "is_ordinary": True,
        "periodicity": 1,
        "description": "desc",
    }

    _override_concept_service(mock_service)
    try:
        # Patch mapper in the router's namespace
        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.concept.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.get("/api/v1/concept/1")

        assert resp.status_code == 200
        assert resp.json() == mock_response
        mock_service.get_by_id.assert_called_once_with(1)
    finally:
        _reset_concept_service_override()


def test_list_concepts_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_list = [MagicMock(), MagicMock()]
    mock_service.get_all.return_value = mock_domain_list

    mock_response_list = [
        {
            "id": 1,
            "name": "A",
            "is_ordinary": True,
            "periodicity": 1,
            "description": None,
        },
        {
            "id": 2,
            "name": "B",
            "is_ordinary": False,
            "periodicity": None,
            "description": "x",
        },
    ]

    _override_concept_service(mock_service)
    try:

        def fake_domain_list_to_response_schemas(_):
            return mock_response_list

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.concept.domain_list_to_response_schemas",
            fake_domain_list_to_response_schemas,
        )

        resp = client.get("/api/v1/concept/")

        assert resp.status_code == 200
        assert resp.json() == mock_response_list
        mock_service.get_all.assert_called_once_with()
    finally:
        _reset_concept_service_override()


def test_create_concept_created(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_in = MagicMock(name="domain_in")
    mock_domain_created = MagicMock(name="domain_created")
    mock_service.create.return_value = mock_domain_created

    payload = {
        "name": "Lease collection",
        "is_ordinary": True,
        "periodicity": 1,
        "description": "Monthly lease collection",
    }

    mock_response = {
        "id": 10,
        "name": "Lease collection",
        "is_ordinary": True,
        "periodicity": 1,
        "description": "Monthly lease collection",
    }

    _override_concept_service(mock_service)
    try:
        # Patch mappers in the router's namespace
        def fake_schema_to_domain(model: ConceptBase):
            # Ensure route passed a proper ConceptBase instance
            assert isinstance(model, ConceptBase)
            return mock_domain_in

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.concept.schema_to_domain",
            fake_schema_to_domain,
        )
        monkeypatch.setattr(
            "app.presentation.api.v1.routes.concept.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.post("/api/v1/concept/", json=payload)

        assert resp.status_code == 201
        assert resp.json() == mock_response
        mock_service.create.assert_called_once_with(mock_domain_in)
    finally:
        _reset_concept_service_override()


def test_create_concept_validation_error(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    _override_concept_service(mock_service)
    try:
        # Missing required 'name' and 'is_ordinary'
        bad_payload = {"periodicity": 1, "description": "x"}
        resp = client.post("/api/v1/concept/", json=bad_payload)
        assert resp.status_code == 422
        mock_service.create.assert_not_called()
    finally:
        _reset_concept_service_override()


def test_update_concept_ok(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    mock_domain_in = MagicMock(name="domain_in")
    mock_domain_updated = MagicMock(name="domain_updated")
    mock_service.update.return_value = mock_domain_updated

    payload = {
        "name": "Updated name",
        "is_ordinary": False,
        "periodicity": 0,
        "description": None,
    }

    mock_response = {
        "id": 42,
        "name": "Updated name",
        "is_ordinary": False,
        "periodicity": 0,
        "description": None,
    }

    _override_concept_service(mock_service)
    try:

        def fake_schema_to_domain(model: ConceptBase):
            assert isinstance(model, ConceptBase)
            return mock_domain_in

        def fake_domain_to_response_schema(_):
            return mock_response

        monkeypatch.setattr(
            "app.presentation.api.v1.routes.concept.schema_to_domain",
            fake_schema_to_domain,
        )
        monkeypatch.setattr(
            "app.presentation.api.v1.routes.concept.domain_to_response_schema",
            fake_domain_to_response_schema,
        )

        resp = client.put("/api/v1/concept/42", json=payload)

        assert resp.status_code == 200
        assert resp.json() == mock_response
        mock_service.update.assert_called_once_with(42, mock_domain_in)
    finally:
        _reset_concept_service_override()


def test_update_concept_validation_error(client: TestClient, monkeypatch):
    mock_service = MagicMock()
    _override_concept_service(mock_service)
    try:
        # invalid: name empty, periodicity negative
        bad_payload = {
            "name": "",
            "is_ordinary": True,
            "periodicity": -1,
            "description": "d",
        }
        resp = client.put("/api/v1/concept/1", json=bad_payload)
        assert resp.status_code == 422
        mock_service.update.assert_not_called()
    finally:
        _reset_concept_service_override()


def test_delete_concept_no_content(client: TestClient):
    mock_service = MagicMock()
    mock_service.delete.return_value = True

    _override_concept_service(mock_service)
    try:
        resp = client.delete("/api/v1/concept/99")
        assert resp.status_code == 204
        assert resp.text == ""
        mock_service.delete.assert_called_once_with(99)
    finally:
        _reset_concept_service_override()


def test_get_concept_not_found_assertion_triggers_404(client: TestClient):
    """
    Your route asserts that the domain entity is not None.
    If the service returns None, it raises AssertionError -> 404.
    """
    mock_service = MagicMock()
    mock_service.get_by_id.return_value = None

    _override_concept_service(mock_service)
    try:
        resp = client.get("/api/v1/concept/999")
        assert resp.status_code == 404
    finally:
        _reset_concept_service_override()
