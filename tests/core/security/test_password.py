import re
from app.core.security.password import hash_password, verify_password


def test_hash_password_produces_valid_bcrypt_hash():
    raw = "my-secret-password"
    hashed = hash_password(raw)

    # Should not match the raw password
    assert hashed != raw

    # Bcrypt hashes always start with $2... (2b, 2y depending on backend)
    assert re.match(r"^\$2[aby]?\$.{56}$", hashed)


def test_verify_password_succeeds_for_correct_password():
    raw = "correct-horse-battery-staple"
    hashed = hash_password(raw)

    assert verify_password(raw, hashed) is True


def test_verify_password_fails_for_incorrect_password():
    raw = "super-password"
    hashed = hash_password(raw)

    assert verify_password("wrong-password", hashed) is False


def test_hashing_same_password_creates_different_hashes():
    raw = "repeatable-password"

    h1 = hash_password(raw)
    h2 = hash_password(raw)

    # Salting should make them different
    assert h1 != h2

    # Both should verify correctly
    assert verify_password(raw, h1)
    assert verify_password(raw, h2)
