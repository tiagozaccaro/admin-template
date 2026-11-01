"""Approval registry for the agent daemon.

Destructive tool calls (FR-006 / SC-003) must not execute until a human
approves them. This module provides the coordination primitive:

- `request_approval(...)` is called *from inside* a tool. It creates a
  pending approval, pushes an event onto a shared asyncio queue so the SSE
  endpoint can emit an `approval_request` to the client, then awaits the
  human decision.
- `resolve(approval_id, approved)` is called from `POST /approve/{id}`. It
  records the decision and wakes both the blocked tool and the SSE endpoint
  so streaming can resume.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class _Pending:
    tool_name: str
    args: dict[str, Any]
    summary: str
    event: asyncio.Event = field(default_factory=asyncio.Event)
    endpoint_event: asyncio.Event = field(default_factory=asyncio.Event)
    approved: bool | None = None


class ApprovalRegistry:
    """Thread-safe (asyncio) registry of pending destructive-action approvals."""

    def __init__(self) -> None:
        self._pending: dict[str, _Pending] = {}
        self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    @property
    def queue(self) -> asyncio.Queue[dict[str, Any]]:
        return self._queue

    async def request_approval(
        self,
        tool_name: str,
        args: dict[str, Any],
        summary: str,
    ) -> str:
        """Register a pending approval and block until resolved.

        Returns the approval id (also pushed onto `queue` for the SSE
        endpoint to emit). The caller (the tool) receives the *decision*
        via the return value of the awaited call — wait, no: the tool needs
        the decision, so this returns the approved bool once resolved.
        """
        approval_id = uuid.uuid4().hex
        pending = _Pending(
            tool_name=tool_name,
            args=dict(args),
            summary=summary,
        )
        self._pending[approval_id] = pending
        await self._queue.put(
            {
                "type": "approval_request",
                "id": approval_id,
                "tool_name": tool_name,
                "args": dict(args),
                "summary": summary,
            }
        )
        await pending.event.wait()
        return bool(pending.approved)

    async def wait_for_resolve(self, approval_id: str) -> bool:
        """Block the SSE endpoint until the human resolves the approval."""
        pending = self._pending.get(approval_id)
        if pending is None:
            return False
        await pending.endpoint_event.wait()
        return bool(pending.approved)

    def resolve(self, approval_id: str, approved: bool) -> bool:
        """Record a decision and wake the tool + endpoint."""
        pending = self._pending.get(approval_id)
        if pending is None:
            return False
        pending.approved = approved
        pending.event.set()
        pending.endpoint_event.set()
        return True

    def status(self, approval_id: str) -> dict[str, Any] | None:
        pending = self._pending.get(approval_id)
        if pending is None:
            return None
        return {
            "id": approval_id,
            "tool_name": pending.tool_name,
            "args": pending.args,
            "summary": pending.summary,
            "approved": pending.approved,
            "resolved": pending.event.is_set(),
        }


def new_registry() -> ApprovalRegistry:
    """Construct a fresh registry for a single chat turn."""
    return ApprovalRegistry()


__all__ = ["ApprovalRegistry", "new_registry"]