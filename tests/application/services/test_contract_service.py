import pytest
from unittest.mock import MagicMock
from datetime import date

from app.application.services.contract_service import ContractService
from app.core.domain.entities.contract import Contract
from app.core.exceptions.domain_exceptions import PersistenceError, ValidationError

# --- Test Doubles ------------------------------------------------------


class DummyLogger:
    def __init__(self):
        self.infos = []
        self.warnings = []
        self.exceptions = []

    def info(self, msg, *args, **kwargs):
        self.infos.append((msg, kwargs))

    def warning(self, msg, *args, **kwargs):
        self.warnings.append((msg, kwargs))

    def exception(self, msg, *args, **kwargs):
        self.exceptions.append((msg, kwargs))


# --- Fixtures -----------------------------------------------------------


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def dummy_logger(monkeypatch):
    dummy = DummyLogger()
    # Patch the logger factory used in the service
    monkeypatch.setattr(
        "app.application.services.contract_service.get_logger", lambda name: dummy
    )
    return dummy


@pytest.fixture
def service(mock_repo, dummy_logger):
    # Note: Using 'repository' as the keyword based on your service's __init__
    return ContractService(repository=mock_repo, entity_name="Contract")


# --- Tests --------------------------------------------------------------


def test_get_contracts_ending_within_success(service, mock_repo, dummy_logger):
    # Given
    months = 3
    mock_contracts = [
        Contract(
            id=1,
            property_id=10,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 4, 1),
            details=None,
        ),
        Contract(
            id=2,
            property_id=11,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 5, 1),
            details="Active",
        ),
    ]
    mock_repo.get_ending_within_months.return_value = mock_contracts

    # When
    results = service.get_contracts_ending_within(months)

    # Then
    assert results == mock_contracts
    mock_repo.get_ending_within_months.assert_called_once_with(months)

    # Verify Logging
    assert any("Fetching contracts" in msg for msg, _ in dummy_logger.infos)
    assert any("Fetched contracts" in msg for msg, _ in dummy_logger.infos)
    # Check if extra context was passed to logger
    assert dummy_logger.infos[-1][1]["extra"]["count"] == 2


def test_get_contracts_ending_within_invalid_months_raises_validation_error(
    service, dummy_logger
):
    # Given
    invalid_months = 0

    # When / Then
    with pytest.raises(ValidationError) as exc:
        service.get_contracts_ending_within(invalid_months)

    assert "greater than 0" in str(exc.value)

    # Verify Warning Log
    assert any("Invalid months parameter" in msg for msg, _ in dummy_logger.warnings)
    assert dummy_logger.warnings[0][1]["extra"]["months"] == 0


def test_get_contracts_ending_within_repo_failure_raises_persistence_error(
    service, mock_repo, dummy_logger
):
    # Given
    mock_repo.get_ending_within_months.side_effect = Exception("Database is down")

    # When / Then
    with pytest.raises(PersistenceError) as exc:
        service.get_contracts_ending_within(3)

    assert "unexpected error" in str(exc.value)

    # Verify Exception Log
    assert any("Failed to fetch contracts" in msg for msg, _ in dummy_logger.exceptions)
    assert dummy_logger.exceptions[0][1]["extra"]["months"] == 3


def test_service_initialization_sets_logger_and_repo(mock_repo):
    # Verification of inheritance and internal state
    service = ContractService(repository=mock_repo, entity_name="Contract")

    assert service.repo == mock_repo
    assert service.entity_name == "Contract"
    assert service.logger is not None
