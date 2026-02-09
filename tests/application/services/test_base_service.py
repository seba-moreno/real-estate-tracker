import pytest
import app.application.services.base_service as svc_mod

from app.core.exceptions.domain_exceptions import NotFoundError


# --- Test Doubles ------------------------------------------------------------------


class DummyLogger:
    """Captures logger calls for assertions."""

    def __init__(self):
        self.infos = []
        self.warnings = []
        self.exceptions = []

    def info(self, msg, *args, **kw):
        self.infos.append((msg, args, kw))

    def warning(self, msg, *args, **kw):
        self.warnings.append((msg, args, kw))

    def exception(self, msg, *args, **kw):
        self.exceptions.append((msg, args, kw))


class FakeRepo:
    """
    Generic in-memory repository stub.
    """

    def __init__(
        self,
        initial=None,
        fail_on_create=False,
        fail_on_update=False,
        fail_on_delete=False,
    ):
        self.storage = initial or {}
        self.fail_on_create = fail_on_create
        self.fail_on_update = fail_on_update
        self.fail_on_delete = fail_on_delete

        # For assertions
        self.created = []
        self.updated = []
        self.deleted = []

    def get_all(self):
        return list(self.storage.values())

    def get_by_id(self, entity_id: int):
        return self.storage.get(entity_id)

    def create(self, entity):
        if self.fail_on_create:
            raise RuntimeError("Create failed")
        new_id = max(self.storage.keys(), default=0) + 1
        entity.id = new_id
        self.storage[new_id] = entity
        self.created.append(entity)
        return entity

    def update(self, entity_id, entity):
        if self.fail_on_update:
            raise RuntimeError("Update failed")
        if entity_id not in self.storage:
            return None
        self.storage[entity_id] = entity
        entity.id = entity_id
        self.updated.append(entity)
        return entity

    def delete(self, entity_id):
        if self.fail_on_delete:
            raise RuntimeError("Delete failed")
        self.deleted.append(entity_id)
        self.storage.pop(entity_id, None)


# Dummy entity
class E:
    def __init__(self, id=None, value="x"):
        self.id = id
        self.value = value

    def __repr__(self):
        return f"E(id={self.id}, value={self.value})"


# --- Logger fixture ----------------------------------------------------------------


@pytest.fixture
def logger(monkeypatch):
    dummy = DummyLogger()
    monkeypatch.setattr(svc_mod, "get_logger", lambda name: dummy)
    return dummy


# --- Tests -------------------------------------------------------------------------


def test_get_all(logger):
    repo = FakeRepo(initial={1: E(1), 2: E(2)})
    service = svc_mod.BaseService(repo, "Entity")

    results = service.get_all()

    assert len(results) == 2
    assert any("Fetching all Entity" in msg for msg, *_ in logger.infos)
    assert any("Fetched all Entity" in msg for msg, *_ in logger.infos)


def test_get_by_id_success(logger):
    repo = FakeRepo(initial={1: E(1)})
    service = svc_mod.BaseService(repo, "Entity")

    result = service.get_by_id(1)

    assert result.id == 1
    assert any("Fetching Entity" in msg for msg, *_ in logger.infos)
    assert any("Fetched Entity" in msg for msg, *_ in logger.infos)


def test_get_by_id_not_found(logger):
    repo = FakeRepo(initial={})
    service = svc_mod.BaseService(repo, "Entity")

    with pytest.raises(NotFoundError):
        service.get_by_id(7)

    assert any("not found" in msg.lower() for msg, *_ in logger.warnings)


def test_create_success(logger):
    repo = FakeRepo()
    service = svc_mod.BaseService(repo, "Entity")

    new = E(value="created")
    created = service.create(new)

    assert created.id == 1
    assert repo.created == [created]
    assert any("Creating Entity" in msg for msg, *_ in logger.infos)
