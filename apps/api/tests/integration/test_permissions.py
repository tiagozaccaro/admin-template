"""Role enforcement negative tests (US5)."""

from fastapi.testclient import TestClient


def test_protected_endpoints_require_auth(client: TestClient) -> None:
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)

    response = client.get("/api/v1/tenants/")
    assert response.status_code in (401, 403)
