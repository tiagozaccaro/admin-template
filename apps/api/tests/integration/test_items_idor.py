"""Regression tests for item tenant isolation / IDOR protection (US2)."""

from fastapi.testclient import TestClient


def test_items_list_requires_auth(client: TestClient) -> None:
    response = client.get(
        "/api/v1/items", params={"tenant_id": "00000000-0000-0000-0000-000000000000"}
    )
    assert response.status_code in (401, 403)


def test_items_get_requires_auth(client: TestClient) -> None:
    response = client.get(
        "/api/v1/items/00000000-0000-0000-0000-000000000000",
        params={"tenant_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code in (401, 403)
