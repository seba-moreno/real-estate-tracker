import datetime

from app.core.domain.entities.user import User
from app.infrastructure.persistence.sql_alchemy.models.user_model import UserModel
from app.infrastructure.persistence.sql_alchemy.mappers.user_mapper import (
    to_domain,
    to_model,
)


def test_to_domain():
    # Arrange
    model = UserModel(
        id=1,
        username="sebastian",
        email="sebastian@example.com",
        password_hash="hashedpassword",
        is_active=True,
        created_at=datetime.datetime(2023, 1, 1, 12, 0, 0),
        updated_at=datetime.datetime(2023, 1, 2, 12, 0, 0),
    )

    # Act
    entity = to_domain(model)

    # Assert
    assert isinstance(entity, User)
    assert entity.id == model.id
    assert entity.username == model.username
    assert entity.email == model.email
    assert entity.password_hash == model.password_hash
    assert entity.is_active == model.is_active
    assert entity.created_at == model.created_at
    assert entity.updated_at == model.updated_at


def test_to_model():
    # Arrange
    entity = User(
        id=1,
        username="sebastian",
        email="sebastian@example.com",
        password_hash="hashedpassword",
        is_active=True,
        created_at=datetime.datetime(2023, 1, 1, 12, 0, 0),
        updated_at=datetime.datetime(2023, 1, 2, 12, 0, 0),
    )

    # Act
    model = to_model(entity)

    # Assert
    assert isinstance(model, UserModel)
    assert model.id == entity.id
    assert model.username == entity.username
    assert model.email == entity.email
    assert model.password_hash == entity.password_hash
    assert model.is_active == entity.is_active
    assert model.created_at == entity.created_at
    assert model.updated_at == entity.updated_at
