"""Smoke tests for local auth lifecycle endpoints (US1)."""

from fastapi.testclient import TestClient

from admin_template.api.main import app


def test_auth_lifecycle_routes_registered() -> None:
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    paths = set(schema["paths"].keys())
    for p in ("/auth/register", "/auth/verify-email", "/auth/request-reset", "/auth/reset-password", "/auth/account"):
        assert p in paths, p
