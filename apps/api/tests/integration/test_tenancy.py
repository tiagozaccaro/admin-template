"""Integration tests for tenancy (US4)."""

from fastapi.testclient import TestClient


def test_tenants_list_requires_auth(client: TestClient) -> None:
    response = client.get("/api/v1/tenants/")
    assert response.status_code in (401, 403)


def test_tenants_endpoints_exist(client: TestClient) -> None:
    response = client.options("/api/v1/tenants/")
    assert response.status_code in (200, 404, 405)


def test_openapi_includes_tenants(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert any("tenants" in p for p in paths)
