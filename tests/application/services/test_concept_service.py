import pytest
from app.application.services.concept_service import ConceptService
from app.core.domain.entities.concept import Concept
from app.core.exceptions.domain_exceptions import NotFoundError, PersistenceError


class FakeRepo:
    def __init__(self, initial=None):
        self.storage = initial or {}

    def get_all(self):
        return list(self.storage.values())

    def get_by_id(self, id):
        return self.storage.get(id)

    def create(self, entity):
        entity.id = 1
        self.storage[1] = entity
        return entity

    def update(self, id, entity):
        if id not in self.storage:
            raise PersistenceError("Missing")
        entity.id = id
        self.storage[id] = entity
        return entity

    def delete(self, id):
        if id not in self.storage:
            raise PersistenceError("Missing")
        del self.storage[id]


def test_conceptservice_crud():
    repo = FakeRepo()
    service = ConceptService(repository=repo, entity_name="Concept")

    # Create
    create_conc = Concept(
        id=None, name="A", is_ordinary=False, periodicity=None, description=None
    )
    created = service.create(create_conc)
    assert created.id == 1

    # Read
    result = service.get_by_id(1)
    assert result.name == "A"

    # Update
    update_conc = Concept(
        id=1, name="B", is_ordinary=False, periodicity=None, description=None
    )
    updated = service.update(1, update_conc)
    assert updated.name == "B"

    # Delete
    service.delete(1)
    with pytest.raises(NotFoundError):
        service.get_by_id(1)
