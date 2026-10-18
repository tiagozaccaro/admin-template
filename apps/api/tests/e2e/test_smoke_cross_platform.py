"""Cross-platform smoke tests validating API parity invariants (US3)."""

from fastapi.testclient import TestClient


def test_health_endpoints_available(client: TestClient) -> None:
    """SMK-001/002 baseline: Health endpoints are available to both clients."""
    for endpoint in ("/health", "/healthz", "/readyz"):
        response = client.get(endpoint)
        assert response.status_code in (200, 503)
        body = response.json()
        assert isinstance(body, dict)
        assert "status" in body or "ready" in body


def test_auth_endpoints_structure(client: TestClient) -> None:
    """SMK-001: Auth endpoints expose consistent contract shape."""
    response = client.get("/auth/google/start")
    assert response.status_code == 200
    body = response.json()
    assert "authorization_url" in body
    assert "state" in body
    assert "nonce" in body


def test_me_requires_auth(client: TestClient) -> None:
    """SMK-002/003: Protected endpoints reject unauthenticated requests."""
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_callback_validates_input(client: TestClient) -> None:
    """SMK-006: Callback validates parameters consistently."""
    assert client.get("/auth/callback").status_code == 400
    assert client.get("/auth/callback?code=abc").status_code == 400
    assert client.get("/auth/callback?state=xyz").status_code == 400
    assert client.get("/auth/callback?error=access_denied").status_code == 400


def test_logout_accepts_session_revocation(client: TestClient) -> None:
    """SMK-001: Logout endpoint exists and handles session revocation."""
    response = client.post("/auth/logout?session_id=invalid")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "revoked"


def test_openapi_contract_exists(client: TestClient) -> None:
    """Parity requires reproducible contracts; OpenAPI is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"].startswith("3.1")
    assert "/auth/google/start" in schema["paths"]
    assert "/auth/callback" in schema["paths"]
    # /me may be under auth prefix; check for presence
    paths = schema["paths"]
    assert "/auth/google/start" in paths
    assert "/auth/callback" in paths
    assert any("/me" in p for p in paths.keys())
