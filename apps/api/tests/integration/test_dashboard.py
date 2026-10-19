"""Dashboard correctness tests (US6)."""

from fastapi.testclient import TestClient


def test_dashboard_requires_auth(client: TestClient) -> None:
    response = client.get(
        "/api/v1/dashboard?tenant_id=00000000-0000-0000-0000-000000000001"
    )
    assert response.status_code in (401, 403)


def test_dashboard_structure(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert any("dashboard" in p for p in paths)
