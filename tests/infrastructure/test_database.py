import importlib
import pytest
from sqlalchemy.orm import Session


# -------------------------------------------------------------
# Helper: reload module with patched environment
# -------------------------------------------------------------
def _reload_with_db_url(monkeypatch, url="sqlite:///:memory:"):
    monkeypatch.setenv("DATABASE_URL", url)

    # reload module to re-run environment loading logic
    import app.infrastructure.persistence.sql_alchemy.database as module

    importlib.reload(module)
    return module


# -------------------------------------------------------------
# DATABASE_URL presence
# -------------------------------------------------------------


def test_database_module_exits_without_database_url(monkeypatch):
    """If DATABASE_URL is missing, the module should call sys.exit(1)."""
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(SystemExit) as exc:
        _reload_with_db_url(monkeypatch, url="")  # empty string forces exit

    assert exc.value.code == 1


def test_database_module_loads_with_valid_url(monkeypatch):
    """If DATABASE_URL is set, module loads successfully."""
    module = _reload_with_db_url(monkeypatch)
    assert hasattr(module, "engine")
    assert hasattr(module, "SessionLocal")


# -------------------------------------------------------------
# get_db() generator behavior
# -------------------------------------------------------------


def test_get_db_yields_session_and_commits(monkeypatch):
    """Ensures get_db yields a session, commits on success, and closes at end."""
    module = _reload_with_db_url(monkeypatch)

    # Spy on Session.commit and Session.close
    commit_called = False
    close_called = False

    def fake_commit(self):
        nonlocal commit_called
        commit_called = True

    def fake_close(self):
        nonlocal close_called
        close_called = True

    monkeypatch.setattr(module.Session, "commit", fake_commit, raising=False)
    monkeypatch.setattr(module.Session, "close", fake_close, raising=False)

    gen = module.get_db()
    session = next(gen)

    assert isinstance(session, Session)

    # Trigger commit + close
    try:
        next(gen)
    except StopIteration:
        pass

    assert commit_called is True
    assert close_called is True


def test_get_db_rolls_back_on_exception(monkeypatch):
    """Ensures rollback happens when an exception is thrown inside the context."""
    module = _reload_with_db_url(monkeypatch)

    rollback_called = False
    close_called = False

    def fake_rollback(self):
        nonlocal rollback_called
        rollback_called = True

    def fake_close(self):
        nonlocal close_called
        close_called = True

    monkeypatch.setattr(module.Session, "rollback", fake_rollback, raising=False)
    monkeypatch.setattr(module.Session, "close", fake_close, raising=False)

    gen = module.get_db()
    session = next(gen)

    assert isinstance(session, Session)

    # Throw exception inside generator
    with pytest.raises(RuntimeError):
        gen.throw(RuntimeError("test error"))

    assert rollback_called is True
    assert close_called is True
