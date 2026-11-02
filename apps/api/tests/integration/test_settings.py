"""Settings API correctness tests."""

import pytest
from fastapi.testclient import TestClient

from admin_template.api.main import app
from admin_template.auth.sessions import get_current_user_from_session
from admin_template.modules.identity.models.user import User


@pytest.fixture
def authed_client():
    async def fake_user() -> User:
        return User(keycloak_sub="sub", email="test@test.com", display_name="Test")

    app.dependency_overrides[get_current_user_from_session] = fake_user
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_current_user_from_session, None)


def test_settings_requires_auth(client: TestClient) -> None:
    response = client.get("/api/v1/settings")
    assert response.status_code in (401, 403)


def test_settings_read_and_update(authed_client: TestClient) -> None:
    read_response = authed_client.get("/api/v1/settings")
    assert read_response.status_code == 200
    data = read_response.json()
    assert "app_name" in data
    assert "app_description" in data
    assert "maintenance_mode" in data
    assert "session_ttl_minutes" in data
    assert "chat_models" in data

    update_payload = {
        "app_name": "Test App",
        "app_description": "A test description.",
        "maintenance_mode": True,
        "session_ttl_minutes": 120,
        "chat_models": '["openai", "anthropic"]',
        "provider_settings": '{"openai": {"api_key": "sk-test", "base_url": "https://api.openai.com/v1"}}',
    }
    update_response = authed_client.post("/api/v1/settings", json=update_payload)
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["app_name"] == "Test App"
    assert updated["maintenance_mode"] is True
    assert updated["session_ttl_minutes"] == 120
    assert "provider_settings" in updated


def test_settings_rejects_invalid_chat_models(authed_client: TestClient) -> None:
    update_payload = {
        "app_name": "Test App",
        "app_description": "desc",
        "maintenance_mode": False,
        "session_ttl_minutes": 60,
        "chat_models": "not-json",
    }
    response = authed_client.post("/api/v1/settings", json=update_payload)
    assert response.status_code == 422
