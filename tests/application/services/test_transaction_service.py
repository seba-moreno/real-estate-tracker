import pytest
from app.application.services.transaction_service import TransactionService
from app.core.exceptions.domain_exceptions import PersistenceError


# --- Test Doubles ------------------------------------------------------


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
    def __init__(self, balance=0.0, fail=False):
        self.balance = balance
        self.fail = fail
        self.calls = 0

    def get_balance(self):
        self.calls += 1
        if self.fail:
            raise RuntimeError("DB error")
        return self.balance


# --- Fixtures ----------------------------------------------------------


@pytest.fixture
def logger(monkeypatch):
    dummy = DummyLogger()
    monkeypatch.setattr(
        "app.application.services.transaction_service.get_logger", lambda name: dummy
    )
    return dummy


# --- Tests -------------------------------------------------------------


def test_get_balance_success(logger):
    repo = FakeRepo(balance=123.45)
    svc = TransactionService(repository=repo, entity_name="Transaction")

    result = svc.get_balance()

    assert result == 123.45
    assert repo.calls == 1

    # Logging
    assert any("Balance calculated" in msg for msg, *_ in logger.infos)
    assert any(
        kw.get("extra", {}).get("balance") == 123.45
        for (msg, _args, kw) in logger.infos
    )
    assert not logger.exceptions


def test_get_balance_raises_persistence_error(logger):
    repo = FakeRepo(fail=True)
    svc = TransactionService(repository=repo, entity_name="Transaction")

    with pytest.raises(PersistenceError) as err:
        svc.get_balance()

    assert "Error calculating balance" in str(err.value)
    assert repo.calls == 1

    # Exception logged
    assert any("Failed to calculate balance" in msg for msg, *_ in logger.exceptions)
