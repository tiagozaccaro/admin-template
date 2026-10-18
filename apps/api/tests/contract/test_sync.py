"""Contract tests for sync changes GET /api/v1/sync/changes (T078).

Written before the sync router exists (T087), so these tests fail
(TDD red state). They define the expected request/response contract per
contracts/sync-api.md:

Request:
  GET /api/v1/sync/changes?cursor=<opaque base64>&limit=50

Response (200):
  { "items": [
      { "entity_type": str, "entity_id": str, "revision": int,
        "payload": dict, "author": str, "created_at": str }, ...],
    "next_cursor": str | null }
"""

from fastapi.testclient import TestClient

SYNC_CHANGES_URL = "/api/v1/sync/changes"
USER_ID = "00000000-0000-0000-000000000000"


def test_sync_changes_returns_200(client: TestClient) -> None:
    response = client.get(
        SYNC_CHANGES_URL,
        params={"user_id": USER_ID, "cursor": "", "limit": 50},
    )
    assert response.status_code == 200
    body = response.json()
    assert "items" in body and isinstance(body["items"], list)
    assert "next_cursor" in body


def test_sync_changes_invalid_cursor_returns_422(client: TestClient) -> None:
    response = client.get(
        SYNC_CHANGES_URL,
        params={"user_id": USER_ID, "cursor": "not-base64", "limit": 50},
    )
    assert response.status_code == 422
