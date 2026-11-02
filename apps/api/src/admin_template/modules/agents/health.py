"""Periodic health check background task.

Polls every registered agent's /health endpoint on an interval and updates
the Agent.status + last_seen_at columns so the web UI reflects live state.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

import httpx

from admin_template.core.settings import settings
from admin_template.modules.agents import service as agent_service
from admin_template.modules.agents.models.agent import Agent

logger = logging.getLogger(__name__)

_health_task: asyncio.Task[None] | None = None
_stop_event: asyncio.Event | None = None


async def _probe_agent(agent: Agent) -> str:
    """Probe a single agent and return its new status string.

    Sends the agent's stored bearer token (FR-003) so token-protected
    daemons authenticate the probe instead of returning 401. Falls back
    to an unauthenticated probe when no token is registered.
    """
    url = agent.url.rstrip("/") + "/health"
    headers: dict[str, str] = {}
    token = getattr(agent, "health_token", None) or getattr(agent, "token_hash", None)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, headers=headers)
        if resp.status_code == 200:
            return "healthy"
        if resp.status_code in (401, 403) and token:
            # The stored token was rejected; try without auth as a last
            # resort so daemons that don't require a token still report.
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp2 = await client.get(url)
                if resp2.status_code == 200:
                    return "healthy"
            except Exception:  # noqa: S110 — best-effort fallback
                pass
        return "unhealthy"
    except Exception:
        return "offline"


async def _run_health_checks() -> None:
    """Run a single health-check sweep across all agents."""
    from admin_template.core.db import db

    if db.session_factory is None:
        db.init()
    assert db.session_factory is not None
    async with db.session_factory() as session:
        from sqlalchemy import select

        result = await session.execute(select(Agent))
        agents = list(result.scalars().all())
    for agent in agents:
        try:
            status_value = await _probe_agent(agent)
            await agent_service.update_agent_status(
                agent.id,
                status_value,
                last_seen_at=datetime.now(UTC),
            )
        except Exception:
            logger.exception("Health check failed for agent %s", agent.id)


async def health_check_loop(interval_seconds: float = 30) -> None:
    """Background loop that runs health checks on a fixed interval."""
    global _stop_event
    _stop_event = asyncio.Event()
    logger.info("Health check loop started (interval=%ss)", interval_seconds)
    while not _stop_event.is_set():
        try:
            await _run_health_checks()
        except Exception:
            logger.exception("Health check sweep failed")
        try:
            await asyncio.wait_for(_stop_event.wait(), timeout=interval_seconds)
        except TimeoutError:
            continue
    logger.info("Health check loop stopped")


def start_health_check_loop(interval_seconds: float | None = None) -> None:
    """Start the health check loop as a background asyncio task."""
    global _health_task
    if _health_task is not None and not _health_task.done():
        return
    interval = interval_seconds or getattr(settings, "agent_health_interval_seconds", 30)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logger.warning("No running loop; health check loop not started")
        return
    _health_task = loop.create_task(health_check_loop(interval))


async def stop_health_check_loop() -> None:
    """Signal the health check loop to stop and wait for it."""
    global _health_task, _stop_event
    if _stop_event is not None:
        _stop_event.set()
    if _health_task is not None:
        try:
            await _health_task
        except asyncio.CancelledError:
            pass
        _health_task = None
    _stop_event = None


__all__ = [
    "health_check_loop",
    "start_health_check_loop",
    "stop_health_check_loop",
]
