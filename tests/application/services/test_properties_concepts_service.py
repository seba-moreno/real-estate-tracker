import pytest

from app.application.services.properties_concepts_service import (
    PropertiesConceptsService,
)
from app.core.domain.entities.properties_concepts import PropertiesConcepts


# --- test doubles ---------------------------------------------------


class DummyLogger:
    def __init__(self):
        self.infos = []
        self.warnings = []
        self.exceptions = []

    def info(self, msg, *args, **kwargs):
        self.infos.append((msg, args, kwargs))

    def warning(self, msg, *args, **kwargs):
        self.warnings.append((msg, args, kwargs))

    def exception(self, msg, *args, **kwargs):
        self.exceptions.append((msg, args, kwargs))


class FakeRepo:
    def __init__(self, values=None, fail=False):
        self.values = values or []
        self.fail = fail
        self.calls = 0

    def get_with_navigations(self):
        self.calls += 1
        if self.fail:
            raise RuntimeError("Repo failure")
        return self.values


# --- fixtures -------------------------------------------------------


@pytest.fixture
def logger(monkeypatch):
    dummy = DummyLogger()
    # Patch the logger factory used by the service module under test
    monkeypatch.setattr(
        "app.application.services.properties_concepts_service.get_logger",
        lambda name: dummy,
    )
    return dummy


# --- tests ----------------------------------------------------------


def test_get_combos_success(logger):
    pc1 = PropertiesConcepts(id=1, concept_id=10, property_id=20, enabled=True)
    pc2 = PropertiesConcepts(id=2, concept_id=11, property_id=20, enabled=True)
    repo = FakeRepo(values=[pc1, pc2])
    svc = PropertiesConceptsService(repository=repo, entity_name="PropertiesConcepts")

    result = svc.get_combos()

    assert result == repo.values
    assert repo.calls == 1

    # Start log present
    assert any("Fetching PropertiesConcepts combos" in msg for msg, *_ in logger.infos)
    # Success log with count
    assert any(
        "Fetched all PropertiesConcepts combos" in msg and d.get("count") == 2
        for (msg, _args, kw) in logger.infos
        for d in [kw.get("extra", {})]
    )
    assert not logger.warnings
    assert not logger.exceptions


def test_get_combos_repo_exception_bubbles(logger):
    repo = FakeRepo(fail=True)
    svc = PropertiesConceptsService(repository=repo, entity_name="PropertiesConcepts")

    with pytest.raises(RuntimeError) as ei:
        svc.get_combos()

    assert "Repo failure" in str(ei.value)
    # Still should have the initial info log
    assert any("Fetching PropertiesConcepts combos" in msg for msg, *_ in logger.infos)
    # No success log when it fails
    assert not any(
        "Fetched all PropertiesConcepts combos" in msg for msg, *_ in logger.infos
    )
