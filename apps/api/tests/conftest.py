"""Pytest fixtures for the Admin Template API."""

import pytest
from fastapi.testclient import TestClient

from admin_template.api.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client bound to the application instance."""
    return TestClient(app)
