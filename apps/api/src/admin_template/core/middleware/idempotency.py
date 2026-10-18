"""Idempotency key middleware.

Intercepts mutating requests (POST/PUT/PATCH/DELETE) carrying an
`Idempotency-Key` header and returns a cached response when the key has
already been processed. New responses are cached by individual route
handlers via SyncService.record_idempotency(). Per contracts/sync-api.md
(T097).
"""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from admin_template.core.db import get_session
from admin_template.modules.sync.services.sync_service import SyncService

MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces idempotency via the Idempotency-Key header."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        if request.method not in MUTATING_METHODS:
            return await call_next(request)

        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)

        user_id = request.query_params.get("user_id", "anonymous")

        async for session in get_session():
            service = SyncService(session)
            cached = await service.check_idempotency(
                user_id, request.url.path, idempotency_key
            )
            if cached is not None:
                return JSONResponse(
                    content=cached["response_body"],
                    status_code=cached["response_status"],
                )
            # No cached response: let the request proceed. The route
            # handler is responsible for recording the response via
            # SyncService.record_idempotency().
            return await call_next(request)

        return await call_next(request)


__all__ = ["IdempotencyMiddleware"]
