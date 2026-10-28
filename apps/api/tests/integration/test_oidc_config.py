"""Tests for Google OIDC configuration resolution.

Verifies that `google_oidc_config()` raises a clear error when the required
env vars are missing and returns a fully populated config when they are
present. These tests run without network or database access.
"""

from __future__ import annotations

import pytest

from admin_template.auth.oidc import GoogleOIDCConfig, google_oidc_config


def _set_google_env(
    monkeypatch: pytest.MonkeyPatch,
    client_id: str | None = "test-client-id",
    client_secret: str | None = "test-client-secret",
    redirect_uri: str | None = "http://localhost:8000/auth/callback",
    issuer: str = "https://accounts.google.com",
) -> None:
    monkeypatch.setattr("admin_template.auth.oidc.settings.google_client_id", client_id)
    monkeypatch.setattr(
        "admin_template.auth.oidc.settings.google_client_secret", client_secret
    )
    monkeypatch.setattr(
        "admin_template.auth.oidc.settings.google_redirect_uri", redirect_uri
    )
    monkeypatch.setattr("admin_template.auth.oidc.settings.google_issuer", issuer)


def test_google_oidc_config_missing_client_id_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_google_env(monkeypatch, client_id=None)
    with pytest.raises(RuntimeError, match="Google OIDC is not fully configured"):
        google_oidc_config()


def test_google_oidc_config_missing_client_secret_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_google_env(monkeypatch, client_secret=None)
    with pytest.raises(RuntimeError, match="Google OIDC is not fully configured"):
        google_oidc_config()


def test_google_oidc_config_missing_redirect_uri_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_google_env(monkeypatch, redirect_uri=None)
    with pytest.raises(RuntimeError, match="Google OIDC is not fully configured"):
        google_oidc_config()


def test_google_oidc_config_all_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_google_env(monkeypatch, client_id=None, client_secret=None, redirect_uri=None)
    with pytest.raises(RuntimeError, match="Google OIDC is not fully configured"):
        google_oidc_config()


def test_google_oidc_config_returns_config(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_google_env(monkeypatch)
    config = google_oidc_config()
    assert isinstance(config, GoogleOIDCConfig)
    assert config.client_id == "test-client-id"
    assert config.client_secret == "test-client-secret"
    assert config.redirect_uri == "http://localhost:8000/auth/callback"
    assert config.issuer == "https://accounts.google.com"
