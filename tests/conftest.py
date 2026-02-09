import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security.auth import auth_required

# Optional: make tests deterministic
os.environ.setdefault("ENV", "test")


@pytest.fixture(autouse=True)
def override_auth_dependency():
    app.dependency_overrides[auth_required] = lambda: None
    yield
    app.dependency_overrides.pop(auth_required, None)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
