"""Unit tests for password hashing utilities."""

import pytest

from admin_template.core.security import hash_password, verify_password


def test_hash_and_verify_roundtrip():
    h = hash_password("correct-horse-battery-staple")
    assert verify_password("correct-horse-battery-staple", h)


def test_wrong_password_fails():
    h = hash_password("secret")
    assert not verify_password("wrong", h)


def test_empty_password_raises():
    with pytest.raises(ValueError):
        hash_password("")


def test_malformed_hash_returns_false():
    assert not verify_password("secret", "not-a-hash")
    assert not verify_password("secret", "scrypt$bad")


def test_hashes_are_unique():
    h1 = hash_password("secret")
    h2 = hash_password("secret")
    assert h1 != h2
    assert verify_password("secret", h1)
    assert verify_password("secret", h2)
