import re
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.infrastructure.logging.correlation_context import correlation_id_var
from app.infrastructure.middlewares.correlation import CorrelationIdMiddleware

UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[1-5][0-9a-fA-F]{3}-"
    r"[89abAB][0-9a-fA-F]{3}-"
    r"[0-9a-fA-F]{12}$"
)


@pytest.fixture()
def app():
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/echo")
    async def echo(request: Request):
        # Assert middleware set state before handler execution
        assert getattr(request.state, "correlation_id", None) is not None
        # Assert context var visible inside request scope
        assert correlation_id_var.get(None) == request.state.correlation_id
        return {"correlation_id": request.state.correlation_id}

    # A sync endpoint too
    @app.get("/sync-echo")
    def sync_echo(request: Request):
        assert getattr(request.state, "correlation_id", None) is not None
        assert correlation_id_var.get(None) == request.state.correlation_id
        return {"correlation_id": request.state.correlation_id}

    return app


def test_propagates_incoming_header(app):
    client = TestClient(app)
    incoming_id = "test-fixed-id-123"

    resp = client.get("/echo", headers={"X-Request-ID": incoming_id})

    assert resp.status_code == 200
    body = resp.json()
    assert body["correlation_id"] == incoming_id
    assert resp.headers["X-Request-ID"] == incoming_id


def test_generates_uuid_when_header_missing(app):
    client = TestClient(app)

    resp = client.get("/echo")

    assert resp.status_code == 200
    body = resp.json()

    # Validate it looks like a UUID
    generated_id = body["correlation_id"]
    assert isinstance(generated_id, str)
    assert UUID_RE.match(generated_id), f"Not a UUID: {generated_id}"
    # Response header must match the state value
    assert resp.headers["X-Request-ID"] == generated_id


def test_contextvar_reset_between_requests(app, monkeypatch):
    client = TestClient(app)

    # 1. First request — should generate a fresh UUID
    resp1 = client.get("/echo")
    assert resp1.status_code == 200
    cid1 = resp1.json()["correlation_id"]
    assert isinstance(cid1, str)
    assert resp1.headers["X-Request-ID"] == cid1

    # 2. Intentionally pollute the contextvar outside of any request scope
    # This sets the "baseline" state for the next request in this thread
    token = correlation_id_var.set("manually-injected-id")

    try:
        # 3. Second request — middleware must override the pollution
        # during the request and set a NEW unique UUID
        resp2 = client.get("/echo")
        assert resp2.status_code == 200
        cid2 = resp2.json()["correlation_id"]

        # Ensure the middleware didn't use the polluted value
        assert cid2 != "manually-injected-id"
        assert cid2 != cid1  # Each request should be isolated
        assert UUID_RE.match(cid2), f"Expected UUID-like value, got: {cid2}"
        assert resp2.headers["X-Request-ID"] == cid2

        # 4. Verify Middleware Reset logic
        # The middleware should have reset the contextvar to the value
        # it had BEFORE the request started (the pollution).
        assert correlation_id_var.get() == "manually-injected-id"

    finally:
        # 5. Cleanup: Manually reset the contextvar so other tests aren't affected
        correlation_id_var.reset(token)

    # Final check: Now that we reset our manual token, it should be back to default
    assert correlation_id_var.get(None) in [None, "N/A"]


def test_works_for_sync_endpoint_and_sets_header(app):
    client = TestClient(app)
    resp = client.get("/sync-echo")
    assert resp.status_code == 200
    cid = resp.json()["correlation_id"]
    assert isinstance(cid, str)
    assert resp.headers["X-Request-ID"] == cid
