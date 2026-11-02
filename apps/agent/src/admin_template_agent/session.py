"""Session store for the agent daemon.

By default this is an in-memory store (sufficient for local development).
When `persistence` is provided (a callable that receives
`(session_id, role, content)` and returns nothing), every append is also
forwarded to it so the daemon can persist history to the core API's
`AgentSession` table (FR-001).
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

PersistFn = Callable[[str, str, str], Awaitable[None]]


class SessionStore:
    """In-memory chat history with optional persistence callback."""

    def __init__(self, persistence: PersistFn | None = None) -> None:
        self.sessions: dict[str, list[dict]] = {}
        self._persistence = persistence

    def load(self, session_id: str) -> list[dict]:
        return self.sessions.get(session_id, [])

    def save(self, session_id: str, history: list[dict]) -> None:
        self.sessions[session_id] = history

    def append(self, session_id: str, role: str, content: str) -> None:
        self.sessions.setdefault(session_id, []).append({"role": role, "content": content})
        if self._persistence is not None:
            try:
                import asyncio

                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(self._persistence(session_id, role, content))
                else:
                    loop.run_until_complete(self._persistence(session_id, role, content))
            except RuntimeError:
                # No running loop: fire-and-forget is not possible; log.
                logger.debug(
                    "Session persistence deferred (no running loop) for %s",
                    session_id,
                )


def make_persistence(
    api_url: str,
    api_token: str,
    agent_id: str,
    user_id: str,
    tenant_id: str,
) -> PersistFn:
    """Build a persistence callback that POSTs to the core API."""

    async def _persist(session_id: str, role: str, content: str) -> None:
        import httpx

        url = api_url.rstrip("/") + "/api/v1/agents/sessions"
        headers = {"Authorization": f"Bearer {api_token}"}
        payload = {
            "agent_id": agent_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "session_id": session_id,
            "history": [{"role": role, "content": content}],
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(url, json=payload, headers=headers)
        except Exception:
            logger.debug("Session persistence to %s failed", url, exc_info=True)

    return _persist


__all__ = ["PersistFn", "SessionStore", "make_persistence"]
