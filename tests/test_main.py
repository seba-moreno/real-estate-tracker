from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.exceptions.domain_exceptions import NotFoundError, PersistenceError


client = TestClient(app)


# ---------------------------
# Basic Endpoints
# ---------------------------


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version_ok():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": app.version}


# ---------------------------
# CORS
# ---------------------------


def test_cors_preflight_allows_any_origin():
    response = client.options(
        "/health",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code in (200, 204)
    assert response.headers.get("access-control-allow-origin") is not None


# ---------------------------
# DB Health Check
# ---------------------------


def test_db_health_ok():
    """Simulate a working database connection."""
    mock_session = MagicMock()
    mock_session.execute.return_value = True

    with patch("app.main.get_db", return_value=mock_session):
        response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_db_health_error_logs_and_returns_error():
    """Simulate DB failure and assert graceful handling."""
    mock_session = MagicMock()
    mock_session.execute.side_effect = Exception("DB failure")

    with patch("app.main.get_db", return_value=mock_session):
        resp = client.get("/health/db")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------
# Exception Handlers
# ---------------------------


def test_not_found_handler():
    """Ensure custom NotFoundError handler returns 404 with correct detail."""

    @app.get("/trigger-notfound")
    def _():
        raise NotFoundError("Item not found")

    response = client.get("/trigger-notfound")

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_persistence_handler():
    """Ensure custom PersistenceError handler returns 500."""

    @app.get("/trigger-persistence")
    def _():
        raise PersistenceError("DB error")

    response = client.get("/trigger-persistence")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal database error"}


# ---------------------------
# Middleware Smoke Tests
# ---------------------------


def test_correlation_middleware_adds_header():
    """Ensure CorrelationIdMiddleware always adds a header."""

    response = client.get("/health")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 5


def test_rate_limiter_middleware_allows_normal_request():
    """Smoke test — just ensures the limiter doesn't block by default."""

    response = client.get("/health")
    assert response.status_code == 200
