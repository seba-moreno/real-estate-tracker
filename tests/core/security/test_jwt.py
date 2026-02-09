import datetime
import os
import jwt
import pytest
import app.core.security.jwt as jwt_module


# ---------------------------
# TIME FREEZING UTIL
# ---------------------------


class _FixedDateTime:
    """
    Test-only replacement for the `datetime` symbol used by the module under test.
    It ensures that datetime.datetime.now(...) always returns a fixed moment.
    """

    def __init__(self, fixed_epoch_seconds: int):
        from datetime import timezone, timedelta, datetime

        self._timezone = timezone
        self._timedelta = timedelta
        self._orig_datetime = datetime
        self._fixed_dt = self._orig_datetime.fromtimestamp(
            fixed_epoch_seconds, tz=self._timezone.utc
        )

    @property
    def timezone(self):
        return self._timezone

    class _TDWrapper:
        def __call__(self, *args, **kwargs):
            from datetime import timedelta

            return timedelta(*args, **kwargs)

    class _TZWrapper:
        @property
        def utc(self):
            from datetime import timezone

            return timezone.utc

    def __getattr__(self, name):
        if name == "timezone":
            return self._TZWrapper()
        if name == "timedelta":
            return self._TDWrapper()
        if name == "datetime":
            fixed_dt = self._fixed_dt

            class _DTShim:
                @staticmethod
                def now(tz=None):
                    return fixed_dt

            return _DTShim

        return getattr(self._orig_datetime, name)


# ---------------------------
# FIXTURES
# ---------------------------


@pytest.fixture(autouse=True)
def restore_env(monkeypatch):
    """Ensure env changes do not leak across tests."""
    monkeypatch.delenv("SECRET_KEY", raising=False)


@pytest.fixture()
def fixed_time(monkeypatch):
    """
    Freeze time at 2026-01-01T00:00Z (epoch=1767225600) and patch the jwt_module datetime.
    """
    fixed_epoch = 1_767_225_600
    monkeypatch.setattr(jwt_module, "datetime", _FixedDateTime(fixed_epoch))
    return fixed_epoch


# ---------------------------
# TEST-ONLY JWT DECODER
# Disable expiration validation
# ---------------------------


def decode(token, secret):
    """
    Decode JWT *without* exp validation.
    This solves the real-time dependency that caused ExpiredSignatureError.
    """
    return jwt.decode(
        token,
        secret,
        algorithms=[jwt_module.JWT_ALGORITHM],
        options={"verify_exp": False},  #  << KEY FIX
    )


# ---------------------------
# TESTS
# ---------------------------


def test_creates_token_with_expected_claims_and_default_expiry(monkeypatch, fixed_time):
    """
    Validate iat and exp math (60 minutes).
    """

    monkeypatch.setenv("SECRET_KEY", "unit-secret")
    monkeypatch.setenv("JWT_EXPIRE_MIN", "60")

    monkeypatch.setattr(jwt_module, "JWT_SECRET", "unit-secret")
    monkeypatch.setattr(jwt_module, "JWT_EXPIRE_MIN", 60)

    class MockDatetime:
        @classmethod
        def now(cls, tz=None):
            return datetime.datetime.fromtimestamp(fixed_time, tz=datetime.timezone.utc)

        @classmethod
        def utcnow(cls):
            return datetime.datetime.fromtimestamp(fixed_time, tz=datetime.timezone.utc)

    monkeypatch.setattr("app.core.security.jwt.datetime", MockDatetime)

    token = jwt_module.create_access_token("sebastian")

    claims = decode(token, "unit-secret")
    assert claims["sub"] == "sebastian"
    assert claims["iat"] == fixed_time
    assert claims["exp"] == fixed_time + 60 * 60
    assert claims["exp"] > claims["iat"]


def test_honors_custom_expiry_minutes(monkeypatch, fixed_time):
    fixed_now = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)

    class MockDatetime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    monkeypatch.setattr("app.core.security.jwt.datetime", MockDatetime)

    monkeypatch.setenv("SECRET_KEY", "short-ttl")
    monkeypatch.setattr(jwt_module, "JWT_SECRET", os.getenv("SECRET_KEY"))
    monkeypatch.setattr(jwt_module, "JWT_EXPIRE_MIN", 5)

    token = jwt_module.create_access_token("victoria")
    claims = decode(token, "short-ttl")

    assert claims["sub"] == "victoria"
    assert claims["iat"] == fixed_time
    assert claims["exp"] == fixed_time + 5 * 60


def test_uses_configured_algorithm(monkeypatch, fixed_time):
    monkeypatch.setenv("SECRET_KEY", "algo-secret")
    monkeypatch.setattr(jwt_module, "JWT_SECRET", os.getenv("SECRET_KEY"))
    monkeypatch.setattr(jwt_module, "JWT_ALGORITHM", "HS256")

    token = jwt_module.create_access_token("gisele")

    claims = jwt.decode(token, "algo-secret", algorithms=["HS256"])
    assert claims["sub"] == "gisele"

    with pytest.raises(jwt.InvalidAlgorithmError):
        jwt.decode(token, "algo-secret", algorithms=["RS256"])


def test_returns_str_even_if_jwt_encode_returns_bytes(monkeypatch, fixed_time):
    monkeypatch.setenv("SECRET_KEY", "bytey")

    real_jwt_encode = jwt.encode

    def fake_encode(payload, secret, algorithm):
        real = real_jwt_encode(payload, secret, algorithm=algorithm)
        return real.encode("utf-8") if isinstance(real, str) else real

    monkeypatch.setattr(jwt_module.jwt, "encode", fake_encode)

    token = jwt_module.create_access_token("facundo")
    assert isinstance(token, str)


def test_env_secret_is_used_when_set(monkeypatch, fixed_time):
    monkeypatch.setenv("SECRET_KEY", "env-wins")
    monkeypatch.setattr(jwt_module, "JWT_SECRET", os.getenv("SECRET_KEY"))

    token = jwt_module.create_access_token("ezequiel")
    claims = decode(token, "env-wins")

    assert claims["sub"] == "ezequiel"
