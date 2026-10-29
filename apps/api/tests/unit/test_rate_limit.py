"""Unit tests for rate limiting middleware."""

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from admin_template.core.rate_limit import RateLimitMiddleware


async def homepage(request):
    return PlainTextResponse("ok")


def _make_client(max_requests=3, window_seconds=60):
    app = Starlette(routes=[Route("/", homepage)])
    app.add_middleware(
        RateLimitMiddleware, max_requests=max_requests, window_seconds=window_seconds
    )
    return TestClient(app)


def test_allows_under_limit():
    client = _make_client(max_requests=3)
    for _ in range(3):
        r = client.get("/")
        assert r.status_code == 200


def test_blocks_over_limit():
    client = _make_client(max_requests=2)
    client.get("/")
    client.get("/")
    r = client.get("/")
    assert r.status_code == 429
    assert r.json()["detail"] == "Too many requests"
