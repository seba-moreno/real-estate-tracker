from app.core.exceptions.domain_exceptions import (
    DomainError,
    NotFoundError,
    PersistenceError,
    ValidationError,
)


def test_error_hierarchy():
    assert issubclass(NotFoundError, DomainError)
    assert issubclass(PersistenceError, DomainError)
    assert issubclass(ValidationError, DomainError)


def test_not_found_error_message():
    try:
        raise NotFoundError("User not found")
    except NotFoundError as e:
        assert str(e) == "User not found"


def test_validation_error_message():
    try:
        raise ValidationError("Invalid value")
    except ValidationError as e:
        assert str(e) == "Invalid value"


def test_catching_domain_error_parent():
    try:
        raise PersistenceError("DB down")
    except DomainError as e:
        assert isinstance(e, PersistenceError)
