import pytest
from decimal import Decimal
from app.application.services.property_service import PropertyService
from app.core.domain.entities.property import Property
from app.core.exceptions.domain_exceptions import NotFoundError, PersistenceError


# --- Test doubles ------------------------------------------------------


class DummyLogger:
    def __init__(self):
        self.infos = []
        self.warnings = []
        self.exceptions = []

    def info(self, msg, *args, **kwargs):
        self.infos.append((msg, args, kwargs))

    def warning(self, msg, *args, **kwargs):
        self.warnings.append((msg, args, kwargs))

    def error(self, msg, *args, **kwargs):
        self.exceptions.append((msg, args, kwargs))

    def exception(self, msg, *args, **kwargs):
        self.exceptions.append((msg, args, kwargs))


class FakeRepo:
    def __init__(
        self, initial=None, fail_create=False, fail_update=False, fail_delete=False
    ):
        self.storage = initial or {}
        self.fail_create = fail_create
        self.fail_update = fail_update
        self.fail_delete = fail_delete

    # BaseRepository methods
    def get_all(self):
        return list(self.storage.values())

    def get_by_id(self, id):
        return self.storage.get(id)

    def create(self, entity):
        if self.fail_create:
            raise RuntimeError("Create failed")
        new_id = max(self.storage.keys(), default=0) + 1
        entity.id = new_id
        self.storage[new_id] = entity
        return entity

    def update(self, id, entity):
        if self.fail_update:
            raise RuntimeError("Update failed")
        if id not in self.storage:
            return None
        entity.id = id
        self.storage[id] = entity
        return entity

    def delete(self, id):
        if self.fail_delete:
            raise RuntimeError("Delete failed")
        self.storage.pop(id, None)


# --- Fixtures -----------------------------------------------------------


@pytest.fixture
def logger(monkeypatch):
    dummy = DummyLogger()

    monkeypatch.setattr(
        "app.application.services.base_service.logger",
        dummy,
        raising=False,
    )

    monkeypatch.setattr(
        "app.application.services.base_service.get_logger",
        lambda name: dummy,
        raising=False,
    )

    monkeypatch.setattr(
        "app.infrastructure.logging.logger_with_correlation_id.get_logger",
        lambda name: dummy,
        raising=False,
    )

    monkeypatch.setattr(
        "app.application.services.property_service.logger",
        dummy,
        raising=False,
    )

    return dummy


# --- Tests --------------------------------------------------------------


def test_get_all_properties(logger):
    initial_prop = Property(
        id=1,
        location="Street A",
        area=100,
        valuation=Decimal("1000.00"),
        details="Detail",
    )
    repo = FakeRepo(initial={1: initial_prop})
    svc = PropertyService(repository=repo, entity_name="Property")

    props = svc.get_all()

    assert len(props) == 1
    assert props[0].id == 1
    assert any("Fetching all Property" in msg for msg, *_ in logger.infos)


def test_get_property_by_id_success(logger):
    initial_prop = Property(
        id=1,
        location="Test Location",
        area=50,
        valuation=Decimal("500.00"),
        details=None,
    )
    repo = FakeRepo(initial={1: initial_prop})
    svc = PropertyService(repository=repo, entity_name="Property")

    prop = svc.get_by_id(1)

    assert prop.id == 1
    assert any("Fetched Property" in msg for msg, *_ in logger.infos)


def test_get_property_by_id_not_found(logger):
    repo = FakeRepo(initial={})
    svc = PropertyService(repository=repo, entity_name="Property")

    with pytest.raises(NotFoundError):
        svc.get_by_id(123)

    assert any("not found" in msg.lower() for msg, *_ in logger.warnings)


def test_create_property_success(logger):
    repo = FakeRepo()
    svc = PropertyService(repository=repo, entity_name="Property")

    new_prop = Property(
        id=None, location="New St", area=60, valuation=Decimal("600.00"), details="New"
    )
    created = svc.create(new_prop)

    assert created.id == 1
    assert any("Property created successfully" in msg for msg, *_ in logger.infos)


def test_create_property_failure_raises_persistence(logger):
    repo = FakeRepo(fail_create=True)
    svc = PropertyService(repository=repo, entity_name="Property")

    fail_prop = Property(
        id=None, location="Fail", area=0, valuation=Decimal("0"), details=None
    )
    with pytest.raises(PersistenceError):
        svc.create(fail_prop)

    assert logger.exceptions


def test_update_property_success(logger):
    old_prop = Property(
        id=1, location="Old St", area=40, valuation=Decimal("400"), details="Old"
    )
    repo = FakeRepo(initial={1: old_prop})
    svc = PropertyService(repository=repo, entity_name="Property")

    update_payload = Property(
        id=None,
        location="Updated St",
        area=45,
        valuation=Decimal("450"),
        details="Updated",
    )
    updated = svc.update(1, update_payload)

    assert updated.location == "Updated St"
    assert any("updated successfully" in msg.lower() for msg, *_ in logger.infos)


def test_update_property_notfound(logger):
    repo = FakeRepo(initial={})
    svc = PropertyService(repository=repo, entity_name="Property")

    not_found_prop = Property(
        id=None, location="X", area=0, valuation=Decimal("0"), details=None
    )
    with pytest.raises(NotFoundError):
        svc.update(999, not_found_prop)


def test_update_property_failure(logger):
    initial_prop = Property(
        id=1, location="Loc", area=10, valuation=Decimal("100"), details=None
    )
    repo = FakeRepo(initial={1: initial_prop}, fail_update=True)
    svc = PropertyService(repository=repo, entity_name="Property")

    bad_update = Property(
        id=None, location="Bad", area=10, valuation=Decimal("100"), details=None
    )
    with pytest.raises(PersistenceError):
        svc.update(1, bad_update)

    assert logger.exceptions


def test_delete_property_success(logger):
    initial_prop = Property(
        id=1, location="Loc", area=10, valuation=Decimal("100"), details=None
    )
    repo = FakeRepo(initial={1: initial_prop})
    svc = PropertyService(repository=repo, entity_name="Property")

    svc.delete(1)

    assert 1 not in repo.storage
    assert any("deleted successfully" in msg.lower() for msg, *_ in logger.infos)


def test_delete_property_notfound(logger):
    repo = FakeRepo(initial={})
    svc = PropertyService(repository=repo, entity_name="Property")

    with pytest.raises(NotFoundError):
        svc.delete(8000)


def test_delete_property_failure(logger):
    initial_prop = Property(
        id=1, location="Loc", area=10, valuation=Decimal("100"), details=None
    )
    repo = FakeRepo(initial={1: initial_prop}, fail_delete=True)
    svc = PropertyService(repository=repo, entity_name="Property")

    with pytest.raises(PersistenceError):
        svc.delete(1)

    assert logger.exceptions
