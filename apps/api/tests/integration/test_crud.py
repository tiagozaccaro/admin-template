"""CRUD validation/authorization tests (US7)."""

from fastapi.testclient import TestClient


def test_items_endpoints_require_auth(client: TestClient) -> None:
    response = client.get(
        "/api/v1/items?tenant_id=00000000-0000-0000-0000-000000000001"
    )
    assert response.status_code in (401, 403)


def test_items_in_openapi(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert any("items" in p for p in paths)
